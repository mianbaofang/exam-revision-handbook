from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from intl_exam_guide.auditing.review_ledger import review_ledger_evidence
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.render_snapshot import (
    canonical_json_sha256,
    inspect_current_render,
)
from intl_exam_guide.validation.checks import (
    issues_to_dict,
    pdf_quality_summary,
    validate_pdf_output,
)


PDF_EXPORT_RECORD_SCHEMA_VERSION = "v1-pdf-export-record"
CURRENT_PDF_SCHEMA_VERSION = "v1-current-pdf-pointer"
DELIVERY_COPY_RECORD_SCHEMA_VERSION = "v1-delivery-copy-record"
CURRENT_DELIVERY_SCHEMA_VERSION = "v1-current-delivery-pointer"
CURRENT_PDF_FILE = "current-pdf.json"
CURRENT_DELIVERY_FILE = "current-delivery.json"
PDF_EXPORT_DIR = "pdf-exports"
DELIVERY_COPY_DIR = "delivery-copies"


class PdfTechnicalValidationError(RuntimeError):
    """Raised when a generated PDF candidate fails technical delivery checks."""


class ControlledDeliveryError(RuntimeError):
    """Raised when a controlled delivery copy cannot be completed safely."""


def inspect_pdf_candidate(plan: GuidePlan, pdf_path: Path) -> dict[str, object]:
    issues = issues_to_dict(validate_pdf_output(plan, pdf_path))
    blockers = [issue for issue in issues if issue.get("severity") == "error"]
    warnings = [issue for issue in issues if issue.get("severity") == "warning"]
    return {
        "status": "passed" if not blockers else "failed",
        "blockers": blockers,
        "warnings": warnings,
        "summary": pdf_quality_summary(plan, pdf_path),
    }


def promote_pdf_candidate(candidate_path: Path, desired_path: Path) -> Path:
    """Promote a checked candidate without overwriting a differing historical PDF."""

    candidate_hash = _file_sha256(candidate_path)
    target = desired_path
    if target.exists():
        if _file_sha256(target) == candidate_hash:
            candidate_path.unlink()
            return target
        target = desired_path.with_name(
            f"{desired_path.stem}-approved-{candidate_hash[:12]}{desired_path.suffix}"
        )
        if target.exists():
            if _file_sha256(target) == candidate_hash:
                candidate_path.unlink()
                return target
            target = desired_path.with_name(
                f"{desired_path.stem}-approved-{candidate_hash}{desired_path.suffix}"
            )
            if target.exists() and _file_sha256(target) != candidate_hash:
                raise PdfTechnicalValidationError(
                    f"Cannot promote PDF candidate without overwriting an unrelated file: {target}"
                )
    candidate_path.replace(target)
    return target


def write_pdf_export_record(
    output_dir: Path,
    pdf_path: Path,
    technical_report: dict[str, object],
) -> dict[str, object]:
    output_dir = output_dir.resolve()
    pdf_path = pdf_path.resolve()
    if technical_report.get("status") != "passed":
        raise PdfTechnicalValidationError("A failed PDF candidate cannot become current.")
    try:
        relative_pdf = pdf_path.relative_to(output_dir).as_posix()
    except ValueError as exc:
        raise PdfTechnicalValidationError(
            "The current PDF must stay inside the handbook output directory."
        ) from exc

    render = inspect_current_render(output_dir)
    pointer = render.get("pointer")
    if render.get("complete") is not True or not isinstance(pointer, dict):
        raise PdfTechnicalValidationError("Current render changed before PDF promotion.")
    ledger = review_ledger_evidence(output_dir)
    if ledger.get("complete") is not True:
        raise PdfTechnicalValidationError("Current review ledger changed before PDF promotion.")
    product_review_path = output_dir / "agent-product-review.json"
    ledger_path = Path(str(ledger.get("index_path") or ""))
    if not product_review_path.is_file() or not ledger_path.is_file():
        raise PdfTechnicalValidationError("Current LLM review evidence is missing.")

    html_path = _confined_path(output_dir, pointer.get("html_path"))
    if html_path is None:
        raise PdfTechnicalValidationError("Current render pointer has no valid HTML path.")
    pdf_payload: dict[str, object] = {
        "path": relative_pdf,
        "sha256": _file_sha256(pdf_path),
        "byte_size": pdf_path.stat().st_size,
        "page_count": _summary_int(technical_report, "pdf_pages"),
    }
    payload: dict[str, object] = {
        "schema_version": PDF_EXPORT_RECORD_SCHEMA_VERSION,
        "render_snapshot_id": pointer.get("snapshot_id"),
        "parent_html": {
            "path": pointer.get("html_path"),
            "sha256": pointer.get("html_sha256"),
        },
        "pdf": pdf_payload,
        "delivery_filename": f"{html_path.stem}.pdf",
        "review_ledger": {
            "path": ledger_path.resolve().relative_to(output_dir).as_posix(),
            "sha256": ledger.get("index_sha256"),
        },
        "product_review": {
            "path": product_review_path.relative_to(output_dir).as_posix(),
            "sha256": _file_sha256(product_review_path),
        },
        "technical_validation": technical_report,
    }
    export_id = canonical_json_sha256(payload)
    record = {"export_id": export_id, **payload}
    record_path = output_dir / PDF_EXPORT_DIR / f"{export_id}.json"
    serialized = _pretty_json(record)
    if record_path.exists():
        if record_path.read_text(encoding="utf-8") != serialized:
            raise PdfTechnicalValidationError(f"Immutable PDF export collision: {record_path}")
    else:
        _atomic_write_text(record_path, serialized)

    current = {
        "schema_version": CURRENT_PDF_SCHEMA_VERSION,
        "status": "current",
        "export_id": export_id,
        "record_file": record_path.relative_to(output_dir).as_posix(),
        "pdf_path": relative_pdf,
        "pdf_sha256": pdf_payload["sha256"],
        "render_snapshot_id": pointer.get("snapshot_id"),
        "parent_html_sha256": pointer.get("html_sha256"),
        "delivery_filename": payload["delivery_filename"],
    }
    _atomic_write_text(output_dir / CURRENT_PDF_FILE, _pretty_json(current))
    return current


def inspect_current_pdf(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    pointer_path = output_dir / CURRENT_PDF_FILE
    pointer = _read_json_object(pointer_path)
    issues: list[dict[str, str]] = []
    if pointer is None:
        _issue(issues, "pdf.current_pointer_missing", "No current PDF export is recorded.")
        return {"complete": False, "issues": issues, "pointer": {}, "record": {}}
    if pointer.get("schema_version") != CURRENT_PDF_SCHEMA_VERSION:
        _issue(issues, "pdf.current_pointer_schema", "current-pdf.json schema is unsupported.")
    if pointer.get("status") != "current":
        _issue(issues, "pdf.current_pointer_stale", "The recorded PDF is historical, not current.")
        return {"complete": False, "issues": issues, "pointer": pointer, "record": {}}

    record_path = _confined_path(output_dir, pointer.get("record_file"))
    record = _read_json_object(record_path) if record_path is not None else None
    if record is None:
        _issue(issues, "pdf.export_record_missing", "Current PDF export record is missing.")
        return {"complete": False, "issues": issues, "pointer": pointer, "record": {}}
    payload = {key: value for key, value in record.items() if key != "export_id"}
    export_id = canonical_json_sha256(payload)
    if record.get("export_id") != export_id or pointer.get("export_id") != export_id:
        _issue(issues, "pdf.export_record_hash", "Current PDF export record hash is invalid.")

    raw_pdf = record.get("pdf")
    pdf_record: dict[str, Any] = dict(raw_pdf) if isinstance(raw_pdf, dict) else {}
    pdf_path = _confined_path(output_dir, pdf_record.get("path"))
    if pdf_path is None or not pdf_path.is_file():
        _issue(issues, "pdf.file_missing", "Current PDF file is missing.")
    else:
        current_hash = _file_sha256(pdf_path)
        if current_hash != pdf_record.get("sha256") or current_hash != pointer.get("pdf_sha256"):
            _issue(issues, "pdf.file_hash", "Current PDF bytes do not match the export record.")

    render = inspect_current_render(output_dir)
    render_pointer = render.get("pointer")
    if render.get("complete") is not True or not isinstance(render_pointer, dict):
        _issue(issues, "pdf.render_invalid", "Current render is no longer valid.")
    elif (
        record.get("render_snapshot_id") != render_pointer.get("snapshot_id")
        or pointer.get("render_snapshot_id") != render_pointer.get("snapshot_id")
        or _nested_value(record, "parent_html", "sha256") != render_pointer.get("html_sha256")
    ):
        _issue(issues, "pdf.render_binding", "Current PDF is not bound to the current HTML render.")

    ledger = review_ledger_evidence(output_dir)
    if ledger.get("complete") is not True or _nested_value(
        record, "review_ledger", "sha256"
    ) != ledger.get("index_sha256"):
        _issue(issues, "pdf.review_ledger_binding", "Current PDF review-ledger binding is stale.")
    product_path = output_dir / "agent-product-review.json"
    if not product_path.is_file() or _nested_value(
        record, "product_review", "sha256"
    ) != _file_sha256(product_path):
        _issue(issues, "pdf.product_review_binding", "Current PDF product-review binding is stale.")
    if _nested_value(record, "technical_validation", "status") != "passed":
        _issue(issues, "pdf.technical_validation", "Current PDF did not pass technical checks.")
    return {
        "complete": not issues,
        "issues": issues,
        "pointer": pointer,
        "record": record,
        "record_path": str(record_path) if record_path is not None else None,
        "pdf_path": str(pdf_path) if pdf_path is not None and pdf_path.is_file() else None,
    }


def invalidate_current_pdf(output_dir: Path, reason: str) -> None:
    output_dir = output_dir.resolve()
    pointer_path = output_dir / CURRENT_PDF_FILE
    pointer = _read_json_object(pointer_path)
    if pointer is None:
        return
    stale = dict(pointer)
    stale["schema_version"] = CURRENT_PDF_SCHEMA_VERSION
    stale["status"] = "stale"
    stale["invalidated_reason"] = reason
    _atomic_write_text(pointer_path, _pretty_json(stale))


def inspect_current_delivery(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    pointer = _read_json_object(output_dir / CURRENT_DELIVERY_FILE)
    issues: list[dict[str, str]] = []
    if pointer is None:
        _issue(issues, "delivery.current_pointer_missing", "No controlled delivery copy is recorded.")
        return {"complete": False, "issues": issues, "pointer": {}, "record": {}}
    if pointer.get("schema_version") != CURRENT_DELIVERY_SCHEMA_VERSION:
        _issue(issues, "delivery.current_pointer_schema", "Current delivery pointer is unsupported.")
    record_path = _confined_path(output_dir, pointer.get("record_file"))
    record = _read_json_object(record_path) if record_path is not None else None
    if record is None:
        _issue(issues, "delivery.record_missing", "Controlled delivery record is missing.")
        return {"complete": False, "issues": issues, "pointer": pointer, "record": {}}
    payload = {key: value for key, value in record.items() if key != "copy_id"}
    copy_id = canonical_json_sha256(payload)
    if record.get("copy_id") != copy_id or pointer.get("copy_id") != copy_id:
        _issue(issues, "delivery.record_hash", "Controlled delivery record hash is invalid.")
    current_pdf = inspect_current_pdf(output_dir)
    current_pointer = current_pdf.get("pointer")
    if current_pdf.get("complete") is not True or not isinstance(current_pointer, dict):
        _issue(issues, "delivery.source_stale", "Controlled delivery source is no longer current.")
    elif record.get("source_export_id") != current_pointer.get("export_id"):
        _issue(issues, "delivery.source_binding", "Controlled delivery is bound to an older PDF.")
    destination_value = record.get("destination_pdf")
    destination = Path(destination_value) if isinstance(destination_value, str) else None
    if destination is None or not destination.is_file():
        _issue(issues, "delivery.file_missing", "Controlled delivery destination is missing.")
    else:
        digest = _file_sha256(destination)
        if (
            digest != record.get("destination_pdf_sha256")
            or digest != pointer.get("destination_pdf_sha256")
        ):
            _issue(issues, "delivery.file_hash", "Controlled delivery copy hash is stale.")
    return {
        "complete": not issues,
        "issues": issues,
        "pointer": pointer,
        "record": record,
        "record_path": str(record_path) if record_path is not None else None,
        "destination_pdf": str(destination) if destination is not None else None,
    }


def copy_current_pdf_to_delivery(
    output_dir: Path,
    delivery_dir: Path,
    *,
    supersede_existing: bool = False,
) -> Path:
    output_dir = output_dir.resolve()
    evidence = inspect_current_pdf(output_dir)
    if evidence.get("complete") is not True:
        raise ControlledDeliveryError("Only the current gate-approved PDF can be copied for delivery.")
    source = Path(str(evidence.get("pdf_path"))).resolve()
    pointer = evidence.get("pointer")
    if not isinstance(pointer, dict):
        raise ControlledDeliveryError("Current PDF pointer is unavailable.")
    delivery_dir = delivery_dir.resolve()
    delivery_dir.mkdir(parents=True, exist_ok=True)
    filename = str(pointer.get("delivery_filename") or source.name)
    destination = delivery_dir / filename
    source_hash = _file_sha256(source)
    superseded: dict[str, object] | None = None
    if destination.exists() and _file_sha256(destination) != source_hash:
        if not supersede_existing:
            raise ControlledDeliveryError(
                f"Delivery destination already contains a different file: {destination}. "
                "Use --supersede-existing only after explicitly deciding to archive it."
            )
        old_hash = _file_sha256(destination)
        archive_dir = delivery_dir / "superseded"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive = archive_dir / f"{destination.stem}-{old_hash[:12]}{destination.suffix}"
        if archive.exists() and _file_sha256(archive) != old_hash:
            raise ControlledDeliveryError(f"Superseded archive path is occupied: {archive}")
        if archive.exists():
            destination.unlink()
        else:
            destination.replace(archive)
        superseded = {
            "original_path": str(destination),
            "archive_path": str(archive),
            "sha256": old_hash,
        }

    if not destination.exists():
        handle = tempfile.NamedTemporaryFile(
            dir=delivery_dir,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        )
        temp_path = Path(handle.name)
        handle.close()
        try:
            shutil.copy2(source, temp_path)
            if _file_sha256(temp_path) != source_hash:
                raise ControlledDeliveryError("Delivery copy hash verification failed.")
            temp_path.replace(destination)
        finally:
            temp_path.unlink(missing_ok=True)
    if _file_sha256(destination) != source_hash:
        raise ControlledDeliveryError("Delivered PDF hash does not match the approved source.")

    record_payload: dict[str, object] = {
        "schema_version": DELIVERY_COPY_RECORD_SCHEMA_VERSION,
        "source_export_id": pointer.get("export_id"),
        "source_pdf": str(source),
        "source_pdf_sha256": source_hash,
        "destination_pdf": str(destination),
        "destination_pdf_sha256": _file_sha256(destination),
        "superseded": superseded,
    }
    copy_id = canonical_json_sha256(record_payload)
    record = {"copy_id": copy_id, **record_payload}
    record_path = output_dir / DELIVERY_COPY_DIR / f"{copy_id}.json"
    _atomic_write_text(record_path, _pretty_json(record))
    current = {
        "schema_version": CURRENT_DELIVERY_SCHEMA_VERSION,
        "copy_id": copy_id,
        "record_file": record_path.relative_to(output_dir).as_posix(),
        "destination_pdf": str(destination),
        "destination_pdf_sha256": source_hash,
    }
    _atomic_write_text(output_dir / CURRENT_DELIVERY_FILE, _pretty_json(current))
    return destination


def _summary_int(report: dict[str, object], key: str) -> int:
    summary = report.get("summary")
    value = summary.get(key) if isinstance(summary, dict) else 0
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _nested_value(value: dict[str, Any], field: str, nested: str) -> object:
    raw = value.get(field)
    return raw.get(nested) if isinstance(raw, dict) else None


def _confined_path(output_dir: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    path = candidate if candidate.is_absolute() else output_dir / candidate
    try:
        resolved = path.resolve()
        resolved.relative_to(output_dir.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def _read_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pretty_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(path)
    finally:
        temp_path.unlink(missing_ok=True)


def _issue(issues: list[dict[str, str]], code: str, message: str) -> None:
    issues.append({"code": code, "message": message})
