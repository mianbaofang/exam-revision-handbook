from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from intl_exam_guide.auditing.final_review import product_review_evidence
from intl_exam_guide.auditing.pdf_delivery import (
    inspect_current_delivery,
    inspect_current_pdf,
)
from intl_exam_guide.auditing.review_ledger import review_ledger_evidence
from intl_exam_guide.auditing.visual_semantics import visual_semantic_issues
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.output_names import find_handbook_html
from intl_exam_guide.rendering.render_snapshot import inspect_current_render
from intl_exam_guide.rendering.visual_assets import (
    load_visual_manifest,
    visual_manifest_matches_plan,
)
from intl_exam_guide.validation.checks import issues_to_dict, validate_plan


DELIVERY_AUDIT_SCHEMA_VERSION = "v0.8-controlled-delivery-audit"
REVIEWED_STATES = {"approved", "reviewed"}
TEXT_ONLY_ROUTES = {"text-ok", "none"}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def audit_delivery(output_dir: Path) -> dict[str, object]:
    """Evaluate delivery readiness without changing any handbook artifact."""

    output_dir = output_dir.resolve()
    blockers: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    plan = _load_plan(output_dir, blockers)
    if plan is not None and plan.content_provenance != "llm-authored":
        _add_issue(
            blockers,
            "content.python_draft",
            "GuidePlan content_provenance must be llm-authored before formal delivery.",
            artifact=str(output_dir / "guide-plan.json"),
        )
    html_path = find_handbook_html(output_dir, plan.qualification if plan else None)
    html_sha256 = _file_sha256(html_path) if html_path.exists() else None
    if not html_path.exists():
        _add_issue(
            blockers,
            "html.missing",
            "The current handbook HTML is missing.",
            artifact=str(html_path),
        )

    render_snapshot = inspect_current_render(output_dir)
    raw_snapshot_issues = render_snapshot.get("issues")
    if isinstance(raw_snapshot_issues, list):
        for issue in raw_snapshot_issues:
            if not isinstance(issue, dict):
                continue
            _add_issue(
                blockers,
                str(issue.get("code") or "render.snapshot_invalid"),
                str(issue.get("message") or "Current render snapshot is invalid."),
                artifact=str(issue.get("artifact")) if issue.get("artifact") else None,
            )

    validation_issues: list[dict[str, str]] = []
    if plan is not None and html_path.exists():
        validation_issues = issues_to_dict(
            validate_plan(plan, html_path=html_path, pdf_path=None, output_dir=output_dir)
        )
        for issue in validation_issues:
            destination = blockers if issue.get("severity") == "error" else warnings
            _add_issue(
                destination,
                "validation.error" if destination is blockers else "validation.warning",
                str(issue.get("message") or "Machine validation reported an issue."),
                artifact=str(html_path),
            )

    review = product_review_evidence(output_dir)
    for message in _string_list(review.get("issues")):
        _add_issue(
            blockers,
            "review.current_html_unapproved",
            message,
            artifact=str(output_dir / "agent-product-review.json"),
        )

    _audit_concept_provenance(output_dir, blockers)

    review_ledger = review_ledger_evidence(output_dir)
    raw_ledger_issues = review_ledger.get("issues")
    if isinstance(raw_ledger_issues, list):
        for issue in raw_ledger_issues:
            if not isinstance(issue, dict):
                continue
            _add_issue(
                blockers,
                str(issue.get("code") or "review.ledger_invalid"),
                str(issue.get("message") or "Review ledger is incomplete."),
                artifact=str(review_ledger.get("index_path") or ""),
            )

    visual_report = _audit_visuals(output_dir, plan, blockers, warnings)
    current_pdf = inspect_current_pdf(output_dir)
    current_delivery = inspect_current_delivery(output_dir)
    next_actions = _next_actions(blockers, current_pdf, current_delivery)
    return {
        "schema_version": DELIVERY_AUDIT_SCHEMA_VERSION,
        "mode": "read-only-delivery-audit",
        "output_dir": str(output_dir),
        "delivery_eligible": not blockers,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "artifacts": {
            "guide_plan": str(output_dir / "guide-plan.json"),
            "html": str(html_path) if html_path.exists() else None,
            "html_sha256": html_sha256,
            "product_review": str(output_dir / "agent-product-review.json"),
            "visual_manifest": str(output_dir / "images" / "visual_manifest.json"),
        },
        "machine_validation": {
            "html_only": True,
            "error_count": sum(
                issue.get("severity") == "error" for issue in validation_issues
            ),
            "warning_count": sum(
                issue.get("severity") == "warning" for issue in validation_issues
            ),
            "issues": validation_issues,
        },
        "product_review": {
            "complete": review.get("complete") is True,
            "issues": _string_list(review.get("issues")),
            "reviewed_html_sha256": _reviewed_html_sha256(review),
            "current_html_sha256": review.get("current_html_sha256"),
            "expected_topic_count": review.get("expected_topic_count", 0),
            "expected_rendered_visual_count": review.get(
                "expected_rendered_visual_count", 0
            ),
        },
        "render_snapshot": {
            "complete": render_snapshot.get("complete") is True,
            "issues": render_snapshot.get("issues", []),
            "snapshot_path": render_snapshot.get("snapshot_path"),
        },
        "review_ledger": {
            "complete": review_ledger.get("complete") is True,
            "issues": review_ledger.get("issues", []),
            "index_path": review_ledger.get("index_path"),
            "index_sha256": review_ledger.get("index_sha256"),
        },
        "visuals": visual_report,
        "current_pdf": current_pdf,
        "current_delivery": current_delivery,
        "next_actions": next_actions,
    }


def _next_actions(
    blockers: list[dict[str, object]],
    current_pdf: dict[str, object],
    current_delivery: dict[str, object],
) -> list[dict[str, object]]:
    if not blockers:
        if current_pdf.get("complete") is not True:
            return [{"action": "export_pdf", "reason_codes": ["pdf.not_current"]}]
        delivery_pointer = current_delivery.get("pointer")
        if isinstance(delivery_pointer, dict) and delivery_pointer and current_delivery.get(
            "complete"
        ) is not True:
            return [
                {
                    "action": "refresh_controlled_delivery_copy",
                    "reason_codes": ["delivery.stale"],
                }
            ]
        return [{"action": "complete", "reason_codes": []}]

    groups: list[tuple[str, tuple[str, ...]]] = [
        ("repair_or_rerender_html", ("plan.", "html.", "render.", "validation.")),
        ("return_to_writer", ("content.",)),
        ("complete_or_repair_visuals", ("visual.",)),
        ("complete_llm_html_review", ("review.",)),
    ]
    codes = [str(item.get("code") or "") for item in blockers]
    actions: list[dict[str, object]] = []
    consumed: set[str] = set()
    for action, prefixes in groups:
        matching = sorted({code for code in codes if code.startswith(prefixes)})
        if matching:
            actions.append({"action": action, "reason_codes": matching})
            consumed.update(matching)
    remaining = sorted({code for code in codes if code not in consumed})
    if remaining:
        actions.append({"action": "resolve_delivery_blockers", "reason_codes": remaining})
    return actions


def _load_plan(
    output_dir: Path, blockers: list[dict[str, object]]
) -> GuidePlan | None:
    path = output_dir / "guide-plan.json"
    if not path.exists():
        _add_issue(blockers, "plan.missing", "guide-plan.json is missing.", artifact=str(path))
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("root value must be an object")
        return GuidePlan.from_dict(payload)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _add_issue(
            blockers,
            "plan.invalid",
            f"guide-plan.json is invalid: {exc}",
            artifact=str(path),
        )
        return None


def _audit_concept_provenance(
    output_dir: Path, blockers: list[dict[str, object]]
) -> None:
    path = output_dir / "concepts" / "concept_explanations.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    entries = payload.get("concept_explanations", payload) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        decision = entry.get("visual_decision")
        source = decision.get("source") if isinstance(decision, dict) else None
        if (
            entry.get("delivery_eligible") is False
            or entry.get("provenance") == "python-fallback"
            or source == "python-draft-fallback"
        ):
            title = str(entry.get("topic_title") or entry.get("topic_id") or f"entry-{index + 1}")
            _add_issue(
                blockers,
                "content.python_fallback",
                f"{title} contains Python fallback content or visual routing.",
                artifact=str(path),
            )
def _audit_visuals(
    output_dir: Path,
    plan: GuidePlan | None,
    blockers: list[dict[str, object]],
    warnings: list[dict[str, object]],
) -> dict[str, object]:
    images_dir = output_dir / "images"
    manifest_path = images_dir / "visual_manifest.json"
    manifest_kind = "missing"
    entries: list[dict[str, Any]] = []
    if manifest_path.exists():
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _add_issue(
                blockers,
                "visual.manifest_invalid",
                f"visual_manifest.json is invalid: {exc}",
                artifact=str(manifest_path),
            )
        else:
            if isinstance(raw_manifest, list):
                manifest_kind = "legacy-list"
                _add_issue(
                    warnings,
                    "visual.manifest_legacy",
                    "Legacy visual manifest is readable but lacks the v2 review contract.",
                    artifact=str(manifest_path),
                )
                entries = load_visual_manifest(manifest_path)
            elif (
                isinstance(raw_manifest, dict)
                and raw_manifest.get("schema_version") == 2
                and isinstance(raw_manifest.get("visuals"), list)
            ):
                manifest_kind = "v2"
                entries = load_visual_manifest(manifest_path)
            else:
                manifest_kind = "unsupported"
                _add_issue(
                    blockers,
                    "visual.manifest_unsupported",
                    "visual_manifest.json must be a legacy list or a schema_version 2 object.",
                    artifact=str(manifest_path),
                )
    elif plan is not None and plan.visual_briefs:
        _add_issue(
            blockers,
            "visual.manifest_missing",
            "Visual briefs exist but images/visual_manifest.json is missing.",
            artifact=str(manifest_path),
                )

    if (
        plan is not None
        and manifest_kind in {"legacy-list", "v2"}
        and not visual_manifest_matches_plan(plan, entries)
    ):
        _add_issue(
            blockers,
            "visual.manifest_plan_mismatch",
            "visual_manifest.json is not the source-bound visual-spec set for the current guide-plan.json. Rebuild the manifest before importing or approving assets.",
            artifact=str(manifest_path),
        )

    if plan is not None and plan.visual_briefs and not entries and manifest_kind != "unsupported":
        _add_issue(
            blockers,
            "visual.manifest_empty",
            "Visual briefs exist but the visual manifest contains no entries.",
            artifact=str(manifest_path),
        )

    seen_ids: set[str] = set()
    rendered_count = 0
    reviewed_count = 0
    for index, entry in enumerate(entries):
        visual_id = str(entry.get("visual_id") or entry.get("id") or "").strip()
        label = visual_id or f"entry-{index + 1}"
        if not visual_id:
            _add_issue(
                blockers,
                "visual.id_missing",
                "Visual manifest entry has no visual_id.",
                artifact=str(manifest_path),
            )
        elif visual_id in seen_ids:
            _add_issue(
                blockers,
                "visual.id_duplicate",
                f"Duplicate visual_id: {visual_id}.",
                artifact=str(manifest_path),
                visual_id=visual_id,
            )
        seen_ids.add(visual_id)

        route = _visual_route(entry)
        decision = _reviewer_visual_decision(entry)
        if decision not in REVIEWED_STATES:
            _add_issue(
                blockers,
                "visual.decision_pending",
                f"{label} reviewer_visual_decision is {decision or 'missing'}.",
                artifact=str(manifest_path),
                visual_id=visual_id or None,
            )

        rendered = _renders_in_html(entry)
        if rendered:
            rendered_count += 1
            review_status = str(entry.get("review_status") or "").strip().lower()
            if review_status not in REVIEWED_STATES:
                _add_issue(
                    blockers,
                    "visual.asset_unreviewed",
                    f"{label} rendered asset review_status is {review_status or 'missing'}.",
                    artifact=str(manifest_path),
                    visual_id=visual_id or None,
                )
            else:
                reviewed_count += 1
            _audit_rendered_asset(
                images_dir,
                manifest_path,
                entry,
                label,
                visual_id or None,
                blockers,
            )
        elif route not in TEXT_ONLY_ROUTES:
            _add_issue(
                blockers,
                "visual.asset_not_rendered",
                f"{label} has route {route or 'missing'} but no rendered asset.",
                artifact=str(manifest_path),
                visual_id=visual_id or None,
            )
        for semantic_issue in visual_semantic_issues(entry, images_dir):
            _add_issue(
                blockers,
                semantic_issue["code"],
                semantic_issue["message"],
                artifact=str(manifest_path),
                visual_id=visual_id or None,
            )

    return {
        "manifest_kind": manifest_kind,
        "entry_count": len(entries),
        "rendered_count": rendered_count,
        "reviewed_rendered_count": reviewed_count,
    }


def _audit_rendered_asset(
    images_dir: Path,
    manifest_path: Path,
    entry: dict[str, Any],
    label: str,
    visual_id: str | None,
    blockers: list[dict[str, object]],
) -> None:
    rendered_asset = entry.get("rendered_asset")
    rendered_asset = rendered_asset if isinstance(rendered_asset, dict) else {}
    asset = entry.get("asset")
    asset = asset if isinstance(asset, dict) else {}
    filename = str(
        rendered_asset.get("file") or entry.get("file") or asset.get("file") or ""
    ).strip()
    if not filename:
        _add_issue(
            blockers,
            "visual.asset_file_missing",
            f"{label} is marked as rendered but has no asset filename.",
            artifact=str(manifest_path),
            visual_id=visual_id,
        )
        return
    relative_path = Path(filename)
    candidate = relative_path if relative_path.is_absolute() else images_dir / relative_path
    try:
        asset_path = candidate.resolve()
        asset_path.relative_to(images_dir.resolve())
    except (OSError, ValueError):
        _add_issue(
            blockers,
            "visual.asset_path_invalid",
            f"{label} asset path must stay inside the images directory: {filename}.",
            artifact=str(manifest_path),
            visual_id=visual_id,
        )
        return
    if not asset_path.is_file():
        _add_issue(
            blockers,
            "visual.asset_file_missing",
            f"{label} rendered asset file is missing: {filename}.",
            artifact=str(asset_path),
            visual_id=visual_id,
        )
        return
    expected_hash = str(rendered_asset.get("sha256") or asset.get("sha256") or "").lower()
    if not SHA256_PATTERN.fullmatch(expected_hash):
        _add_issue(
            blockers,
            "visual.asset_hash_missing",
            f"{label} rendered asset has no valid SHA-256 metadata.",
            artifact=str(asset_path),
            visual_id=visual_id,
        )
        return
    current_hash = _file_sha256(asset_path)
    if current_hash != expected_hash:
        _add_issue(
            blockers,
            "visual.asset_hash_mismatch",
            f"{label} rendered asset SHA-256 does not match the manifest.",
            artifact=str(asset_path),
            visual_id=visual_id,
            expected_sha256=expected_hash,
            current_sha256=current_hash,
        )


def _visual_route(entry: dict[str, Any]) -> str:
    route = entry.get("recommended_route")
    if isinstance(route, dict):
        return str(route.get("route") or "").strip().lower()
    return ""


def _reviewer_visual_decision(entry: dict[str, Any]) -> str:
    visual_need = entry.get("visual_need")
    if not isinstance(visual_need, dict):
        return ""
    return str(visual_need.get("reviewer_visual_decision") or "").strip().lower()


def _renders_in_html(entry: dict[str, Any]) -> bool:
    rendered_asset = entry.get("rendered_asset")
    if isinstance(rendered_asset, dict) and rendered_asset.get("renders_in_html") is True:
        return True
    status = str(entry.get("asset_status") or "").strip().lower()
    return bool(str(entry.get("file") or "").strip()) and status in {
        "generated",
        "reviewed",
        "reviewed-generated",
        "provider-selected-generated",
        "sensenova-generated",
        "svg-fallback-needs-review",
    }


def _reviewed_html_sha256(review_evidence: dict[str, object]) -> object:
    review = review_evidence.get("review")
    return review.get("reviewed_html_sha256") if isinstance(review, dict) else None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _string_list(value: object) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _add_issue(
    issues: list[dict[str, object]],
    code: str,
    message: str,
    *,
    artifact: str | None = None,
    visual_id: str | None = None,
    expected_sha256: str | None = None,
    current_sha256: str | None = None,
) -> None:
    issue: dict[str, object] = {"code": code, "message": message}
    for key, value in {
        "artifact": artifact,
        "visual_id": visual_id,
        "expected_sha256": expected_sha256,
        "current_sha256": current_sha256,
    }.items():
        if value is not None:
            issue[key] = value
    issues.append(issue)
