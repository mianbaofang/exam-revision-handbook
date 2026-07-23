from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unicodedata
from typing import Any

from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.visual_assets import load_visual_manifest


RENDER_SNAPSHOT_SCHEMA_VERSION = "v1-render-input-snapshot"
CURRENT_RENDER_SCHEMA_VERSION = "v1-current-render-pointer"
CURRENT_RENDER_FILE = "current-render.json"
RENDER_SNAPSHOT_DIR = "render-snapshots"
INPUT_ARTIFACTS = (
    ("guide-plan.json", True),
    ("qualification.json", False),
    ("run-options.json", False),
    ("syllabus-evidence.json", False),
    ("syllabus-outline.json", False),
    ("concepts/concept_explanations.json", False),
    ("images/visual_manifest.json", False),
)


def canonical_json_bytes(value: object) -> bytes:
    normalized = _normalize_json(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_render_snapshot(
    output_dir: Path,
    html_path: Path,
    plan: GuidePlan,
    visual_manifest_path: Path | None = None,
) -> dict[str, object]:
    output_dir = output_dir.resolve()
    html_path = html_path.resolve()
    manifest_path = (
        visual_manifest_path.resolve()
        if visual_manifest_path is not None
        else output_dir / "images" / "visual_manifest.json"
    )
    rendered_plan_sha256 = canonical_json_sha256(plan.to_dict())
    inputs = [
        _artifact_record(output_dir, output_dir / relative_path, required=required)
        for relative_path, required in INPUT_ARTIFACTS
    ]
    guide_plan_record = next(
        record for record in inputs if record.get("path") == "guide-plan.json"
    )
    payload: dict[str, object] = {
        "schema_version": RENDER_SNAPSHOT_SCHEMA_VERSION,
        "html": _artifact_record(output_dir, html_path, required=True),
        "rendered_plan_sha256": rendered_plan_sha256,
        "guide_plan_matches_rendered_plan": (
            guide_plan_record.get("canonical_json_sha256") == rendered_plan_sha256
        ),
        "inputs": inputs,
        "assets": _rendered_asset_records(output_dir, manifest_path),
    }
    snapshot_id = canonical_json_sha256(payload)
    snapshot = {"snapshot_id": snapshot_id, **payload}
    snapshot_dir = output_dir / RENDER_SNAPSHOT_DIR
    snapshot_path = snapshot_dir / f"{snapshot_id}.json"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    serialized_snapshot = _pretty_json(snapshot)
    if snapshot_path.exists():
        if snapshot_path.read_text(encoding="utf-8") != serialized_snapshot:
            raise RuntimeError(f"Immutable render snapshot collision: {snapshot_path}")
    else:
        _atomic_write_text(snapshot_path, serialized_snapshot)

    html_record = payload["html"]
    pointer = {
        "schema_version": CURRENT_RENDER_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "snapshot_file": _relative_path(output_dir, snapshot_path),
        "html_path": html_record.get("path") if isinstance(html_record, dict) else None,
        "html_sha256": html_record.get("sha256") if isinstance(html_record, dict) else None,
    }
    _atomic_write_text(output_dir / CURRENT_RENDER_FILE, _pretty_json(pointer))
    _invalidate_stale_pdf_pointer(output_dir, snapshot_id)
    return pointer


def inspect_current_render(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    pointer_path = output_dir / CURRENT_RENDER_FILE
    issues: list[dict[str, object]] = []
    pointer = _read_json_object(pointer_path)
    if pointer is None:
        _snapshot_issue(
            issues,
            "render.current_pointer_missing",
            f"Missing or invalid {CURRENT_RENDER_FILE}.",
            pointer_path,
        )
        return {"complete": False, "issues": issues, "pointer": {}, "snapshot": {}}
    if pointer.get("schema_version") != CURRENT_RENDER_SCHEMA_VERSION:
        _snapshot_issue(
            issues,
            "render.current_pointer_schema",
            f"{CURRENT_RENDER_FILE} has an unsupported schema_version.",
            pointer_path,
        )

    snapshot_path = _confined_path(output_dir, pointer.get("snapshot_file"))
    if snapshot_path is None:
        _snapshot_issue(
            issues,
            "render.snapshot_path_invalid",
            "Current render snapshot path must stay inside the output directory.",
            pointer_path,
        )
        return {"complete": False, "issues": issues, "pointer": pointer, "snapshot": {}}
    snapshot = _read_json_object(snapshot_path)
    if snapshot is None:
        _snapshot_issue(
            issues,
            "render.snapshot_missing",
            "The current immutable render snapshot is missing or invalid.",
            snapshot_path,
        )
        return {"complete": False, "issues": issues, "pointer": pointer, "snapshot": {}}

    snapshot_id = str(snapshot.get("snapshot_id") or "")
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_id"}
    computed_snapshot_id = canonical_json_sha256(payload)
    if snapshot_id != computed_snapshot_id or pointer.get("snapshot_id") != snapshot_id:
        _snapshot_issue(
            issues,
            "render.snapshot_hash_mismatch",
            "The current render snapshot ID does not match its canonical payload.",
            snapshot_path,
        )
    if snapshot.get("guide_plan_matches_rendered_plan") is not True:
        _snapshot_issue(
            issues,
            "render.plan_not_bound",
            "The rendered plan does not match guide-plan.json.",
            snapshot_path,
        )

    html_record = snapshot.get("html")
    if isinstance(html_record, dict):
        html_path = _confined_path(output_dir, html_record.get("path"))
        expected_html_hash = str(html_record.get("sha256") or "")
        if html_path is None or not html_path.is_file():
            _snapshot_issue(
                issues,
                "render.html_missing",
                "The HTML bound to the current render snapshot is missing.",
                snapshot_path,
            )
        else:
            current_html_hash = _file_sha256(html_path)
            if current_html_hash != expected_html_hash:
                _snapshot_issue(
                    issues,
                    "render.html_hash_mismatch",
                    "Current HTML bytes do not match the render snapshot.",
                    html_path,
                )
            if pointer.get("html_path") != html_record.get("path") or pointer.get(
                "html_sha256"
            ) != expected_html_hash:
                _snapshot_issue(
                    issues,
                    "render.current_pointer_mismatch",
                    "Current render pointer does not match its snapshot HTML.",
                    pointer_path,
                )
    else:
        _snapshot_issue(
            issues,
            "render.html_record_missing",
            "Render snapshot has no HTML record.",
            snapshot_path,
        )

    _verify_artifact_records(output_dir, snapshot.get("inputs"), "input", issues)
    _verify_artifact_records(output_dir, snapshot.get("assets"), "asset", issues)
    return {
        "complete": not issues,
        "issues": issues,
        "pointer": pointer,
        "snapshot": snapshot,
        "snapshot_path": str(snapshot_path),
    }


def _verify_artifact_records(
    output_dir: Path,
    raw_records: object,
    label: str,
    issues: list[dict[str, object]],
) -> None:
    if not isinstance(raw_records, list):
        _snapshot_issue(
            issues,
            f"render.{label}_records_missing",
            f"Render snapshot {label} records are missing.",
            output_dir / CURRENT_RENDER_FILE,
        )
        return
    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            _snapshot_issue(
                issues,
                f"render.{label}_record_invalid",
                f"Render snapshot contains an invalid {label} record.",
                output_dir / CURRENT_RENDER_FILE,
            )
            continue
        path = _confined_path(output_dir, raw_record.get("path"))
        if path is None:
            _snapshot_issue(
                issues,
                f"render.{label}_path_invalid",
                f"Render snapshot {label} path must stay inside the output directory.",
                output_dir / CURRENT_RENDER_FILE,
            )
            continue
        current = _artifact_record(
            output_dir,
            path,
            required=raw_record.get("required") is True,
        )
        if current.get("present") != raw_record.get("present"):
            _snapshot_issue(
                issues,
                f"render.{label}_presence_changed",
                f"Render {label} presence changed after snapshot: {raw_record.get('path')}.",
                path,
            )
            continue
        if current.get("present") is not True:
            continue
        hash_key = (
            "canonical_json_sha256"
            if raw_record.get("canonical_json_sha256") is not None
            else "sha256"
        )
        if current.get(hash_key) != raw_record.get(hash_key):
            _snapshot_issue(
                issues,
                f"render.{label}_hash_mismatch",
                f"Render {label} changed after snapshot: {raw_record.get('path')}.",
                path,
            )


def _rendered_asset_records(output_dir: Path, manifest_path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen_paths: set[str] = set()
    for entry in load_visual_manifest(manifest_path):
        rendered_asset = entry.get("rendered_asset")
        rendered = (
            isinstance(rendered_asset, dict)
            and rendered_asset.get("renders_in_html") is True
        )
        filename = str(entry.get("file") or "").strip()
        if not rendered or not filename:
            continue
        asset_path = manifest_path.parent / filename
        path_value = _relative_path(output_dir, asset_path)
        if path_value in seen_paths:
            continue
        seen_paths.add(path_value)
        record = _artifact_record(output_dir, asset_path, required=True)
        record["visual_id"] = str(entry.get("visual_id") or entry.get("id") or "")
        records.append(record)
    return records


def _artifact_record(output_dir: Path, path: Path, *, required: bool) -> dict[str, object]:
    resolved_path = path.resolve()
    relative_path = _relative_path(output_dir, resolved_path)
    confined = _confined_path(output_dir, relative_path) == resolved_path
    present = resolved_path.is_file()
    record: dict[str, object] = {
        "path": relative_path,
        "required": required,
        "confined": confined,
        "present": present,
    }
    if not present:
        return record
    content = resolved_path.read_bytes()
    if resolved_path.suffix.lower() == ".json":
        try:
            parsed = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            record["json_valid"] = False
        else:
            record["json_valid"] = True
            record["canonical_json_sha256"] = canonical_json_sha256(parsed)
            return record
    record["sha256"] = hashlib.sha256(content).hexdigest()
    record["byte_size"] = len(content)
    return record


def _relative_path(output_dir: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(output_dir.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


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


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _invalidate_stale_pdf_pointer(output_dir: Path, snapshot_id: str) -> None:
    pointer_path = output_dir / "current-pdf.json"
    pointer = _read_json_object(pointer_path)
    if (
        pointer is None
        or pointer.get("status") != "current"
        or pointer.get("render_snapshot_id") == snapshot_id
    ):
        return
    stale = dict(pointer)
    stale["status"] = "stale"
    stale["invalidated_reason"] = "render snapshot changed"
    _atomic_write_text(pointer_path, _pretty_json(stale))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize_json(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _normalize_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_json(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_json(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    return value


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
        if temp_path.exists():
            temp_path.unlink()


def _snapshot_issue(
    issues: list[dict[str, object]], code: str, message: str, artifact: Path
) -> None:
    issues.append({"code": code, "message": message, "artifact": str(artifact)})
