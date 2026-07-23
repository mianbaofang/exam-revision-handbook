from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import tempfile

from intl_exam_guide.auditing.quality_inspector import (
    QUALITY_INSPECTION_FILE,
)
from intl_exam_guide.auditing.pdf_delivery import (
    ControlledDeliveryError,
    PdfTechnicalValidationError,
    copy_current_pdf_to_delivery,
    inspect_current_pdf,
    inspect_pdf_candidate,
    invalidate_current_pdf,
    promote_pdf_candidate,
    write_pdf_export_record,
)
from intl_exam_guide.core import DeliveryState, course_contract_payload
from intl_exam_guide.models import GuidePlan, Qualification
from intl_exam_guide.rendering.output_names import (
    default_handbook_paths,
    find_handbook_html,
)
from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf
from intl_exam_guide.rendering.text import strip_internal_review_panel
from intl_exam_guide.rendering.visual_assets import load_visual_manifest
from intl_exam_guide.validation.checks import (
    delivery_status_from_issues,
    issues_to_dict,
    review_summary,
    summary_int,
    validate_plan,
)

PENDING_INFOGRAPHIC_STATUSES = {
    "external-generation-required",
    "infographic-provider-required",
    "provider-selected-pending-generation",
    "llm-svg-required",
    "svg-fallback-needs-review",
}
PRODUCT_REVIEW_FILE = "agent-product-review.json"
LEGACY_PRODUCT_REVIEW_SCHEMA_VERSION = "v0.6-llm-html-review"
PRODUCT_REVIEW_SCHEMA_VERSION = "v0.7-llm-html-review-ledger"
FINAL_CONTENT_BLOCKER_PATTERNS = [
    "formulaic AI-style wording",
    "Topic map mastery summary is duplicated",
    "Topic map knowledge-unit title is duplicated",
    "student-facing topic titles are too repetitive",
    "SVG visual titles are too repetitive",
    "SVG visual structures are too repetitive",
    "Raster infographic assets are reused exactly",
    "LLM Analyst syllabus outline is missing",
    "Python evidence extraction cannot be treated as final topic/exam-point analysis",
    "topics and exam points must come from the LLM syllabus_outline_analyst",
]


class HtmlReviewRequiredError(RuntimeError):
    """Raised when PDF export is attempted before current-HTML LLM approval."""


def build_final_review_packet(output_dir: Path) -> dict[str, object]:
    validation = read_json(output_dir / "validation.json")
    qualification = read_json(output_dir / "qualification.json")
    guide_plan = read_json(output_dir / "guide-plan.json")
    manifest_entries = load_visual_manifest(output_dir / "images")
    infographic_jobs = read_json(output_dir / "images" / "infographic_jobs.json", default=[])
    html = read_text(find_handbook_html(output_dir))
    refreshed_validation = build_refreshed_validation(output_dir, validation, guide_plan)
    issues = refreshed_validation.get("issues", [])
    if not isinstance(issues, list):
        issues = []
    pending = [
        entry.get("id")
        for entry in manifest_entries
        if isinstance(entry, dict)
        and entry.get("complexity") == "infographic"
        and str(entry.get("asset_status", "")).lower() in PENDING_INFOGRAPHIC_STATUSES
    ]
    rendered_text = student_visible_text_from_html(html)
    machine_validation = {
        "error_count": count_issues(issues, "error"),
        "warning_count": count_issues(issues, "warning"),
        "delivery_status": refreshed_validation.get("delivery_status"),
        "delivery_state": refreshed_validation.get("delivery_state"),
        "validation_refreshed": refreshed_validation.get("validation_refreshed", False),
        "issues": issues,
    }
    summary = refreshed_validation.get("review_summary", {})
    if not isinstance(summary, dict):
        summary = {}
    workflow = {
        "mode": "lightweight-three-role",
        "roles": ["analyst", "writer", "reviewer"],
        "reviewer_instruction": (
            "Open and visually inspect the current rendered HTML yourself. Python validation "
            "and quality inspection are supporting diagnostics only and cannot approve it. "
            "Do not export PDF until the LLM HTML review passes."
        ),
    }
    quality_inspection = quality_inspection_evidence(output_dir)
    product_review = product_review_evidence(output_dir)
    return {
        "agent_review_required": True,
        "workflow": workflow,
        "quality_inspection": quality_inspection,
        "html_review_gate": {
            "html_path": product_review.get("html_path"),
            "html_sha256": product_review.get("current_html_sha256"),
            "llm_review_complete": product_review.get("complete", False),
            "pdf_export_allowed": product_review.get("complete", False),
            "rule": (
                "LLM must inspect this exact HTML. Repair and rerender until approved; "
                "only then may export-pdf run."
            ),
        },
        "required_full_review_coverage": {
            "topic_count": product_review.get("expected_topic_count", 0),
            "topic_titles": product_review.get("expected_topic_titles", []),
            "rendered_visual_count": product_review.get("expected_rendered_visual_count", 0),
            "rendered_visual_ids": product_review.get("expected_rendered_visual_ids", []),
            "sampling_allowed": False,
        },
        "review_questions": [
            "Does the rendered handbook match the requested board, level, subject, language, and style?",
            "Are topic titles teachable rather than parser fragments, broad container labels, or generic syllabus headings?",
            "Does coverage_granularity prove that every lowest official container was checked for one, several, or no independently assessable requirements?",
            "Can every official source_coverage item be traced from the handbook table of contents to visible teaching treatment, not just JSON coverage?",
            "Does every final topic trace to one or more independent source items, with a defensible merge reason and visible treatment for every mapped item?",
            "Were every topic's teaching claims, worked examples, solution steps, final answers, and source anchors checked for subject accuracy?",
            "Was every rendered visual inspected for factual meaning, including labels, arrows, positions, relationships, scales, units, and correspondence with its topic?",
            "Are complex infographics either reviewed/generated or clearly listed as pending with replacement instructions?",
            "Should this output be presented as final, draft, or blocked?",
        ],
        "machine_validation": machine_validation,
        "agent_self_review": build_agent_self_review(
            machine_validation,
            summary,
            rendered_text,
            [item for item in pending if item],
            product_review,
            quality_inspection,
        ),
        "product_review_evidence": product_review,
        "manual_review_contract": {
            "required": True,
            "required_artifact": PRODUCT_REVIEW_FILE,
            "instruction": (
                "Before PDF export or user handoff, the active LLM must open and visually inspect the "
                "current HTML. If it finds any content, layout, visual, notation, source, or language "
                "problem, it must return to the Writer, repair the source artifacts, rerender HTML, and "
                "personally inspect the new HTML again. Repeat until no fixable issue remains. Python "
                "diagnostics cannot supply the approval decision."
            ),
            "must_fix_before_final": [
                "blocking validation errors",
                "broad official containers passed through without a source-detail audit",
                "collapsed official bullets that are only covered in JSON and not visibly taught",
                "teaching topics with zero or multiple primary independent source items",
                "duplicated mastery requirements across independent topics",
                "worked examples that do not match the topic",
                "pending complex infographic assets",
                "language/style mismatch in student-facing sections",
            ],
            "required_product_review_fields": [
                "reviewer_type",
                "html_opened_and_visually_inspected",
                "reviewed_html_sha256",
                "render_snapshot_id",
                "review_ledger_index_sha256",
                "review_iteration",
                "html_review_passed",
                "complete_html_reviewed",
                "machine_validation_used_only_as_supporting_evidence",
                "repair_loop_completed",
                "decision",
            ],
        },
        "review_summary": summary,
        "qualification": qualification_summary(qualification),
        "guide_plan": {
            "available": isinstance(guide_plan, dict),
            "keys": sorted(guide_plan) if isinstance(guide_plan, dict) else [],
        },
        "visuals": {
            "pending_or_review_needed": [item for item in pending if item],
            "infographic_jobs": infographic_jobs if isinstance(infographic_jobs, list) else [],
        },
        "rendered_excerpt": rendered_text[:4000],
    }


def build_agent_self_review(
    machine_validation: dict[str, object],
    summary: dict[str, object],
    rendered_text: str,
    pending_visual_ids: list[str],
    product_review: dict[str, object] | None = None,
    quality_inspection: dict[str, object] | None = None,
) -> dict[str, object]:
    """Give the Agent a concrete final-delivery verdict to review, not just raw gates."""

    reasons: list[str] = []
    status = "ready"
    error_count = summary_int(machine_validation, "error_count")
    if error_count:
        status = "blocked"
        reasons.append(f"{error_count} validation error(s) must be fixed before delivery.")
    final_blockers = final_content_blockers(machine_validation)
    if final_blockers:
        status = "blocked"
        reasons.append(
            "Final-review content blockers must be repaired before delivery: "
            + "; ".join(final_blockers[:5])
            + ("..." if len(final_blockers) > 5 else "")
        )
    if not rendered_text.strip():
        status = "blocked"
        reasons.append("Rendered student-facing text is empty or unreadable.")
    if not product_review_is_complete(product_review):
        if status != "blocked":
            status = "draft"
        reasons.append(
            "Current-HTML LLM review evidence is missing, stale, or incomplete. "
            f"Write {PRODUCT_REVIEW_FILE} only after the active LLM has opened this exact HTML, "
            "repaired every fixable issue, rerendered, and reviewed again."
        )

    pending_concepts = summary_int(summary, "pending_concept_explanations")
    if pending_concepts:
        if status != "blocked":
            status = "draft"
        reasons.append(
            f"{pending_concepts} topic concept explanation(s) still need Agent/LLM review."
        )

    if pending_visual_ids:
        if status != "blocked":
            status = "draft"
        reasons.append(
            f"{len(pending_visual_ids)} complex infographic asset(s) are still pending: "
            + ", ".join(pending_visual_ids[:8])
            + ("..." if len(pending_visual_ids) > 8 else "")
        )

    if not reasons:
        reasons.append(
            "The active LLM approved the current HTML after visual inspection and no blocking "
            "content, concept, image, or rendered-text gaps remain. PDF export is now allowed."
        )
    return {
        "status": status,
        "reasons": reasons,
        "must_not_present_as_final": status != "ready",
        "agent_must_inspect_before_handoff": True,
    }


def final_content_blockers(machine_validation: dict[str, object]) -> list[str]:
    issues = machine_validation.get("issues", [])
    if not isinstance(issues, list):
        return []
    blockers: list[str] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        message = str(issue.get("message") or "")
        if any(pattern in message for pattern in FINAL_CONTENT_BLOCKER_PATTERNS):
            blockers.append(message)
    return blockers


def quality_inspection_evidence(output_dir: Path) -> dict[str, object]:
    path = output_dir / QUALITY_INSPECTION_FILE
    if not path.exists():
        return {
            "required": False,
            "supporting_diagnostic_only": True,
            "file": QUALITY_INSPECTION_FILE,
            "present": False,
            "complete": False,
            "issues": [f"Missing {QUALITY_INSPECTION_FILE}."],
            "inspection": {},
        }
    inspection = read_json(path)
    issues = quality_inspection_issues(inspection)
    return {
        "required": False,
        "supporting_diagnostic_only": True,
        "file": QUALITY_INSPECTION_FILE,
        "present": True,
        "complete": not issues,
        "issues": issues,
        "inspection": inspection if isinstance(inspection, dict) else {},
    }


def quality_inspection_issues(inspection: object) -> list[str]:
    if not isinstance(inspection, dict) or not inspection:
        return [f"Missing {QUALITY_INSPECTION_FILE}."]
    issues: list[str] = []
    if inspection.get("schema_version") != "v0.5-quality-inspection":
        issues.append("schema_version must be v0.5-quality-inspection.")
    if inspection.get("inspection_status") != "pass":
        issues.append("inspection_status must be pass before final reviewer handoff.")
    if inspection.get("recommendation") != "pass_to_reviewer":
        issues.append("recommendation must be pass_to_reviewer before final reviewer handoff.")
    issue_items = inspection.get("issues")
    if isinstance(issue_items, list):
        for item in issue_items:
            if isinstance(item, dict) and item.get("severity") == "error":
                issues.append(
                    str(item.get("message") or "Quality inspection contains an error-level issue.")
                )
    return issues


def quality_inspection_is_passed(quality_inspection: dict[str, object] | None) -> bool:
    return bool(isinstance(quality_inspection, dict) and quality_inspection.get("complete") is True)


def quality_inspection_has_failed(quality_inspection: dict[str, object] | None) -> bool:
    if not isinstance(quality_inspection, dict):
        return False
    inspection = quality_inspection.get("inspection")
    return isinstance(inspection, dict) and inspection.get("inspection_status") == "fail"


def quality_inspection_was_run(output_dir: Path) -> bool:
    evidence = quality_inspection_evidence(output_dir)
    return bool(evidence.get("present") and evidence.get("complete"))


def product_review_evidence(output_dir: Path) -> dict[str, object]:
    review = read_json(output_dir / PRODUCT_REVIEW_FILE)
    html_path = find_handbook_html(output_dir)
    current_html_sha256 = file_sha256(html_path) if html_path.exists() else None
    expected_topic_titles, expected_visual_ids = expected_review_coverage(output_dir)
    issues = product_review_issues(
        review,
        current_html_sha256,
        expected_topic_titles=expected_topic_titles,
        expected_visual_ids=expected_visual_ids,
        output_dir=output_dir,
    )
    return {
        "required": True,
        "file": PRODUCT_REVIEW_FILE,
        "present": bool(review),
        "complete": not issues,
        "issues": issues,
        "review": review if isinstance(review, dict) else {},
        "html_path": str(html_path) if html_path.exists() else None,
        "current_html_sha256": current_html_sha256,
        "expected_topic_count": len(expected_topic_titles),
        "expected_topic_titles": expected_topic_titles,
        "expected_rendered_visual_count": len(expected_visual_ids),
        "expected_rendered_visual_ids": expected_visual_ids,
    }


def product_review_is_complete(product_review: dict[str, object] | None) -> bool:
    return bool(isinstance(product_review, dict) and product_review.get("complete") is True)


def product_review_issues(
    review: object,
    current_html_sha256: str | None = None,
    *,
    expected_topic_titles: list[str] | None = None,
    expected_visual_ids: list[str] | None = None,
    output_dir: Path | None = None,
) -> list[str]:
    if not isinstance(review, dict) or not review:
        return [f"Missing {PRODUCT_REVIEW_FILE}."]
    if review.get("schema_version") == LEGACY_PRODUCT_REVIEW_SCHEMA_VERSION:
        return legacy_product_review_issues(
            review,
            current_html_sha256,
            expected_topic_titles=expected_topic_titles,
            expected_visual_ids=expected_visual_ids,
        )
    issues: list[str] = []
    if review.get("schema_version") != PRODUCT_REVIEW_SCHEMA_VERSION:
        issues.append(f"schema_version must be {PRODUCT_REVIEW_SCHEMA_VERSION}.")
    if review.get("reviewer_type") != "llm":
        issues.append("reviewer_type must be llm; Python inspection cannot approve HTML.")
    for field in [
        "html_opened_and_visually_inspected",
        "complete_html_reviewed",
        "html_review_passed",
        "machine_validation_used_only_as_supporting_evidence",
        "repair_loop_completed",
    ]:
        if review.get(field) is not True:
            issues.append(f"{field} must be true.")
    reviewed_html_sha256 = str(review.get("reviewed_html_sha256") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", reviewed_html_sha256):
        issues.append("reviewed_html_sha256 must be the inspected HTML SHA-256.")
    elif current_html_sha256 and reviewed_html_sha256 != current_html_sha256:
        issues.append(
            "reviewed_html_sha256 does not match the current HTML; rerendered or edited HTML "
            "must be opened and reviewed again by the LLM."
        )
    try:
        review_iteration = int(review.get("review_iteration", 0))
    except (TypeError, ValueError):
        review_iteration = 0
    if review_iteration < 1:
        issues.append("review_iteration must be a positive integer.")
    if not isinstance(review.get("issues_found"), list):
        issues.append("issues_found must be a list.")
    if review.get("unresolved_fixable_issues") not in (None, []):
        issues.append("unresolved_fixable_issues must be empty before final handoff.")
    if review.get("decision") != "approved":
        issues.append("decision must be approved before PDF export.")
    if output_dir is None:
        issues.append("output_dir is required to validate the v0.7 review ledger.")
        return issues
    from intl_exam_guide.auditing.review_ledger import review_ledger_evidence

    ledger = review_ledger_evidence(output_dir)
    raw_ledger_issues = ledger.get("issues")
    if isinstance(raw_ledger_issues, list):
        issues.extend(
            str(item.get("message") or item.get("code"))
            for item in raw_ledger_issues
            if isinstance(item, dict)
        )
    if review.get("review_ledger_index_sha256") != ledger.get("index_sha256"):
        issues.append("review_ledger_index_sha256 does not match the current review ledger index.")
    if review.get("render_snapshot_id") != ledger.get("render_snapshot_id"):
        issues.append("render_snapshot_id does not match the current render snapshot.")
    return issues


def legacy_product_review_issues(
    review: object,
    current_html_sha256: str | None = None,
    *,
    expected_topic_titles: list[str] | None = None,
    expected_visual_ids: list[str] | None = None,
) -> list[str]:
    if not isinstance(review, dict) or not review:
        return [f"Missing {PRODUCT_REVIEW_FILE}."]
    issues: list[str] = []
    if review.get("schema_version") != LEGACY_PRODUCT_REVIEW_SCHEMA_VERSION:
        issues.append(f"schema_version must be {LEGACY_PRODUCT_REVIEW_SCHEMA_VERSION}.")
    if review.get("reviewer_type") != "llm":
        issues.append("reviewer_type must be llm; Python inspection cannot approve HTML.")
    required_true_fields = [
        "html_opened_and_visually_inspected",
        "html_review_passed",
        "all_topics_reviewed",
        "subject_factual_accuracy_checked",
        "worked_examples_and_answers_checked",
        "all_rendered_visuals_reviewed",
        "visual_semantics_checked",
        "layout_checked",
        "machine_validation_used_only_as_supporting_evidence",
        "syllabus_outline_compared",
        "granularity_audit_checked",
        "merged_bullets_visible_in_handbook",
        "visuals_inspected",
        "cross_page_visual_repetition_checked",
        "notation_spot_check_completed",
        "glossary_policy_checked",
        "repair_loop_completed",
    ]
    for field in required_true_fields:
        if review.get(field) is not True:
            issues.append(f"{field} must be true.")
    reviewed_html_sha256 = str(review.get("reviewed_html_sha256") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", reviewed_html_sha256):
        issues.append("reviewed_html_sha256 must be the 64-character SHA-256 of the inspected HTML.")
    elif current_html_sha256 and reviewed_html_sha256 != current_html_sha256:
        issues.append(
            "reviewed_html_sha256 does not match the current HTML; rerendered or edited HTML "
            "must be opened and reviewed again by the LLM."
        )
    try:
        review_iteration = int(review.get("review_iteration", 0))
    except (TypeError, ValueError):
        review_iteration = 0
    if review_iteration < 1:
        issues.append("review_iteration must be a positive integer.")
    issues_found = review.get("issues_found")
    if not isinstance(issues_found, list):
        issues.append("issues_found must be a list.")
    issues.extend(
        review_coverage_issues(
            review,
            "topic",
            expected_topic_titles,
            count_field="topic_review_count",
            ids_field="reviewed_topic_titles",
        )
    )
    issues.extend(
        review_coverage_issues(
            review,
            "rendered visual",
            expected_visual_ids,
            count_field="rendered_visual_review_count",
            ids_field="reviewed_visual_ids",
        )
    )
    unresolved = review.get("unresolved_fixable_issues")
    if unresolved not in (None, []):
        issues.append("unresolved_fixable_issues must be empty before final handoff.")
    repairs = review.get("repairs_made")
    if isinstance(repairs, list) and repairs:
        if review.get("html_rerendered_after_repairs") is not True:
            issues.append(
                "html_rerendered_after_repairs must be true when repairs_made is non-empty."
            )
        if review.get("html_review_rerun_after_repairs") is not True:
            issues.append(
                "html_review_rerun_after_repairs must be true when repairs_made is non-empty."
            )
    elif repairs is not None and not isinstance(repairs, list):
        issues.append("repairs_made must be a list when provided.")
    decision = review.get("decision")
    if decision != "approved":
        issues.append("decision must be approved before PDF export.")
    return issues


def review_coverage_issues(
    review: dict[object, object],
    label: str,
    expected_ids: list[str] | None,
    *,
    count_field: str,
    ids_field: str,
) -> list[str]:
    issues: list[str] = []
    raw_reviewed_ids = review.get(ids_field)
    reviewed_ids = (
        [str(value).strip() for value in raw_reviewed_ids if str(value).strip()]
        if isinstance(raw_reviewed_ids, list)
        else []
    )
    if not isinstance(raw_reviewed_ids, list):
        issues.append(f"{ids_field} must be a list covering every {label}.")
    try:
        review_count = int(str(review.get(count_field, -1)))
    except (TypeError, ValueError):
        review_count = -1
    if review_count != len(reviewed_ids):
        issues.append(f"{count_field} must equal the number of entries in {ids_field}.")
    if len(set(reviewed_ids)) != len(reviewed_ids):
        issues.append(f"{ids_field} must not contain duplicates.")
    if expected_ids is not None:
        missing = sorted(set(expected_ids) - set(reviewed_ids))
        extra = sorted(set(reviewed_ids) - set(expected_ids))
        if missing:
            issues.append(
                f"{ids_field} is missing {len(missing)} required {label}(s): "
                + ", ".join(missing[:8])
            )
        if extra:
            issues.append(
                f"{ids_field} contains {len(extra)} unknown {label}(s): "
                + ", ".join(extra[:8])
            )
    return issues


def expected_review_coverage(output_dir: Path) -> tuple[list[str], list[str]]:
    topic_titles: list[str] = []
    plan_data = read_json(output_dir / "guide-plan.json")
    if isinstance(plan_data, dict):
        try:
            plan = GuidePlan.from_dict(plan_data)
        except (KeyError, TypeError, ValueError):
            plan = None
        if plan is not None:
            topic_titles = [
                str(guide.topic_title).strip()
                for guide in plan.topic_guides
                if str(guide.topic_title).strip()
            ]
    visual_ids: list[str] = []
    for entry in load_visual_manifest(output_dir / "images"):
        rendered_asset = entry.get("rendered_asset")
        nested_rendered = (
            isinstance(rendered_asset, dict)
            and rendered_asset.get("renders_in_html") is True
        )
        flat_status = str(entry.get("asset_status") or "").strip().lower()
        flat_rendered = bool(str(entry.get("file") or "").strip()) and flat_status in {
            "generated",
            "reviewed",
            "reviewed-generated",
            "provider-selected-generated",
            "sensenova-generated",
            "svg-fallback-needs-review",
        }
        if not nested_rendered and not flat_rendered:
            continue
        visual_id = str(entry.get("id") or entry.get("visual_id") or "").strip()
        if visual_id:
            visual_ids.append(visual_id)
    return topic_titles, visual_ids



def build_refreshed_validation(
    output_dir: Path,
    stored_validation: object,
    guide_plan: object,
) -> dict[str, object]:
    if not isinstance(guide_plan, dict):
        return stored_validation_with_flag(stored_validation, refreshed=False)
    try:
        plan = GuidePlan.from_dict(guide_plan)
    except (KeyError, TypeError, ValueError):
        return stored_validation_with_flag(stored_validation, refreshed=False)

    html_path = find_handbook_html(output_dir, plan.qualification)
    stored_pdf = stored_validation.get("pdf") if isinstance(stored_validation, dict) else None
    current_pdf = inspect_current_pdf(output_dir)
    pdf_path: Path | None = (
        Path(str(stored_pdf))
        if stored_pdf and current_pdf.get("complete") is True
        else (
            Path(str(current_pdf.get("pdf_path")))
            if current_pdf.get("complete") is True
            else None
        )
    )
    if pdf_path is not None and not pdf_path.exists():
        pdf_path = None
    issues = validate_plan(plan, html_path=html_path, pdf_path=pdf_path, output_dir=output_dir)
    summary = review_summary(plan, html_path=html_path, pdf_path=pdf_path, output_dir=output_dir)
    delivery_status = delivery_status_from_issues(issues, summary)
    return {
        "issues": issues_to_dict(issues),
        "review_summary": summary,
        "delivery_status": delivery_status,
        "delivery_state": DeliveryState.from_delivery_status(delivery_status).value,
        "validation_refreshed": True,
    }


def stored_validation_with_flag(stored_validation: object, refreshed: bool) -> dict[str, object]:
    if isinstance(stored_validation, dict):
        payload = dict(stored_validation)
    else:
        payload = {"issues": [], "review_summary": {}, "delivery_status": None}
    payload["validation_refreshed"] = refreshed
    return payload


def write_final_review_packet(output_dir: Path) -> Path:
    rerender_html(output_dir)
    packet = build_final_review_packet(output_dir)
    path = output_dir / "final-review-packet.json"
    write_review_artifacts(output_dir, packet, path)
    return path


def write_review_artifacts(output_dir: Path, packet: dict[str, object], path: Path) -> None:
    write_refreshed_validation(output_dir, packet)
    rewrite_delivery_contract(output_dir, packet)
    path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def rewrite_delivery_contract(output_dir: Path, packet: dict[str, object]) -> None:
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        return
    machine = packet.get("machine_validation")
    delivery_status = machine.get("delivery_status") if isinstance(machine, dict) else None
    quality_inspection = packet.get("quality_inspection")
    try:
        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return
    (output_dir / "delivery-contract.json").write_text(
        json.dumps(
            course_contract_payload(
                plan,
                str(delivery_status),
                quality_inspection_complete=quality_inspection_is_passed(
                    quality_inspection if isinstance(quality_inspection, dict) else None
                ),
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def rerender_html(output_dir: Path) -> None:
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        return
    try:
        from intl_exam_guide.rendering.html import render_html

        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
        html_path = find_handbook_html(output_dir, plan.qualification)
        if html_path.name == "guide.html" and not html_path.exists():
            html_path, _ = default_handbook_paths(output_dir, plan.qualification)
        render_html(plan, html_path, output_dir / "images" / "visual_manifest.json")
        strip_internal_review_panel_from_file(html_path)
        invalidate_pdf_export(output_dir, plan.qualification)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        # A legacy/draft directory may not have a valid plan yet. Once a current
        # render snapshot exists, however, silently reviewing the previous HTML
        # would create misleading evidence for a different input version.
        if not (output_dir / "current-render.json").exists():
            return
        raise RuntimeError(
            "Unable to rerender the current HTML for review; the existing HTML was not approved."
        ) from exc


def export_reviewed_pdf(
    output_dir: Path,
    delivery_dir: Path | None = None,
    *,
    supersede_existing: bool = False,
) -> Path:
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        raise HtmlReviewRequiredError("Missing guide-plan.json; cannot locate reviewed HTML.")
    try:
        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        raise HtmlReviewRequiredError(
            "guide-plan.json is invalid; PDF export remains blocked."
        ) from exc
    qualification = plan.qualification
    html_path = find_handbook_html(output_dir, qualification)
    if not html_path.exists():
        raise HtmlReviewRequiredError("Rendered HTML is missing; PDF export remains blocked.")
    from intl_exam_guide.auditing.delivery_gate import audit_delivery

    gate = audit_delivery(output_dir)
    if gate.get("delivery_eligible") is not True:
        raw_blockers = gate.get("blockers")
        blocker_messages = (
            [
                str(item.get("message") or item.get("code") or "Delivery blocker")
                for item in raw_blockers
                if isinstance(item, dict)
            ]
            if isinstance(raw_blockers, list)
            else ["Delivery audit is incomplete."]
        )
        raise HtmlReviewRequiredError(
            "PDF export requires LLM approval of the current HTML and a clean delivery gate: "
            + "; ".join(blocker_messages)
        )
    artifacts = gate.get("artifacts")
    reviewed_html_sha256 = (
        artifacts.get("html_sha256") if isinstance(artifacts, dict) else None
    )
    if reviewed_html_sha256 != file_sha256(html_path):
        raise HtmlReviewRequiredError(
            "Current HTML changed after delivery audit; it must be reviewed and audited again."
        )
    current_pdf = inspect_current_pdf(output_dir)
    if current_pdf.get("complete") is True:
        current_path = Path(str(current_pdf.get("pdf_path")))
        if delivery_dir is not None:
            copy_current_pdf_to_delivery(
                output_dir,
                delivery_dir,
                supersede_existing=supersede_existing,
            )
        return current_path
    validation_path = output_dir / "validation.json"
    stored = read_json(validation_path)
    payload = dict(stored) if isinstance(stored, dict) else {}
    desired_pdf_path = html_path.with_suffix(".pdf")
    handle = tempfile.NamedTemporaryFile(
        dir=output_dir,
        prefix=f".{desired_pdf_path.stem}.",
        suffix=".candidate.pdf",
        delete=False,
    )
    candidate_path = Path(handle.name)
    handle.close()
    try:
        export_pdf(html_path, candidate_path)
        technical_report = inspect_pdf_candidate(plan, candidate_path)
        if technical_report.get("status") != "passed":
            raw_blockers = technical_report.get("blockers")
            messages = [
                str(item.get("message") or "PDF technical validation failed.")
                for item in raw_blockers
                if isinstance(item, dict)
            ] if isinstance(raw_blockers, list) else []
            raise PdfTechnicalValidationError("; ".join(messages) or "PDF technical validation failed.")
        pdf_path = promote_pdf_candidate(candidate_path, desired_pdf_path)
        current_pointer = write_pdf_export_record(output_dir, pdf_path, technical_report)
    except (PdfExportError, PdfTechnicalValidationError) as exc:
        candidate_path.unlink(missing_ok=True)
        payload["pdf_error"] = str(exc)
        validation_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise
    payload["pdf"] = str(pdf_path)
    payload["pdf_error"] = None
    payload["pdf_export_gate"] = {
        "llm_html_review_required": True,
        "delivery_audit_schema_version": gate.get("schema_version"),
        "reviewed_html_sha256": reviewed_html_sha256,
        "review_artifact": PRODUCT_REVIEW_FILE,
        "render_snapshot_id": current_pointer.get("render_snapshot_id"),
        "pdf_sha256": current_pointer.get("pdf_sha256"),
        "pdf_export_id": current_pointer.get("export_id"),
        "status": "passed",
    }
    if delivery_dir is not None:
        try:
            delivered = copy_current_pdf_to_delivery(
                output_dir,
                delivery_dir,
                supersede_existing=supersede_existing,
            )
        except ControlledDeliveryError as exc:
            payload["delivery_error"] = str(exc)
            validation_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            raise
        payload["delivery_copy"] = str(delivered)
        payload["delivery_error"] = None
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return pdf_path


def invalidate_pdf_export(
    output_dir: Path,
    qualification: Qualification | None = None,
) -> None:
    invalidate_current_pdf(output_dir, "HTML or a render input changed")
    validation_path = output_dir / "validation.json"
    stored = read_json(validation_path)
    if not isinstance(stored, dict):
        return
    payload = dict(stored)
    payload["pdf"] = None
    payload["pdf_error"] = None
    payload["pdf_export_gate"] = {
        "llm_html_review_required": True,
        "status": "pending_current_html_review",
    }
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_internal_review_panel_from_file(html_path: Path) -> None:
    if not html_path.exists():
        return
    html = html_path.read_text(encoding="utf-8", errors="replace")
    cleaned = strip_internal_review_panel(html)
    if cleaned != html:
        html_path.write_text(cleaned, encoding="utf-8")


def write_refreshed_validation(output_dir: Path, packet: dict[str, object]) -> None:
    machine = packet.get("machine_validation")
    if not isinstance(machine, dict):
        return
    stored = read_json(output_dir / "validation.json")
    payload = dict(stored) if isinstance(stored, dict) else {}
    payload["issues"] = machine.get("issues", [])
    payload["review_summary"] = packet.get("review_summary", {})
    payload["delivery_status"] = machine.get("delivery_status")
    delivery_status = machine.get("delivery_status")
    payload["delivery_state"] = DeliveryState.from_delivery_status(
        str(delivery_status) if delivery_status is not None else None
    ).value
    payload["validation_refreshed"] = machine.get("validation_refreshed", False)
    (output_dir / "validation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path, default: object | None = None) -> object:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {} if default is None else default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def student_visible_text_from_html(html: str) -> str:
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def count_issues(issues: object, severity: str) -> int:
    if not isinstance(issues, list):
        return 0
    return sum(
        1 for issue in issues if isinstance(issue, dict) and issue.get("severity") == severity
    )


def qualification_summary(qualification: object) -> dict[str, object]:
    if not isinstance(qualification, dict):
        return {"title": None, "topic_count": 0}
    topics = qualification.get("topics", [])
    return {
        "title": qualification.get("title"),
        "topic_count": len(topics) if isinstance(topics, list) else 0,
    }


def build_final_review_prompt(
    guide_html_path: Path,
    syllabus_evidence_path: Path,
    validation_json_path: Path,
    visual_manifest_path: Path | None = None,
    quality_inspection_path: Path | None = None,
) -> str:
    """
    Build a Reviewer prompt for the lightweight three-role workflow.

    The host LLM must inspect the rendered handbook, compare it with evidence,
    check teaching quality and visuals, and report concrete repair items.
    """

    guide_html = (
        read_text(guide_html_path) if guide_html_path.exists() else "[named handbook HTML not found]"
    )
    guide_html_sha256 = file_sha256(guide_html_path) if guide_html_path.exists() else ""
    from intl_exam_guide.auditing.review_ledger import expected_review_items

    expected_topic_items, expected_visual_items = expected_review_items(guide_html_path.parent)
    syllabus_evidence = (
        read_text(syllabus_evidence_path) if syllabus_evidence_path.exists() else "{}"
    )
    validation_json = read_text(validation_json_path) if validation_json_path.exists() else "{}"
    visual_manifest = ""
    if visual_manifest_path and visual_manifest_path.exists():
        visual_manifest = read_text(visual_manifest_path)
    quality_inspection = ""
    if quality_inspection_path and quality_inspection_path.exists():
        quality_inspection = read_text(quality_inspection_path)

    return "\n".join(
        [
            "# Reviewer Visible-Handbook Audit",
            "",
            "You are the LLM Reviewer in a lightweight three-role workflow. The Analyst and Writer may have made mistakes; open and visually inspect the rendered HTML directly.",
            "Machine validation, quality-inspection.json, and final-review-packet.json are supporting diagnostics only. Python cannot approve the handbook and must not replace your visible HTML review.",
            "Do not generate or inspect a PDF during this stage. PDF export is blocked until you approve this exact HTML hash.",
            "",
            "Required checks:",
            "",
            "1. Open or inspect the named HTML output as the student-facing handbook.",
            "2. Compare the topic sequence and source anchors with syllabus-evidence.json, syllabus-outline.json, coverage_granularity, and granularity_audit when present.",
            "3. Confirm every lowest official container was audited for one, several, or no independently assessable requirements; reject broad headings passed through without source proof.",
            "4. Check that every final topic maps to one or more independent source items. When closely related items are combined, require a source-based merge reason and visible teaching treatment for every mapped item; do not force artificial one-item micro-topics.",
            "5. Review every topic listed below. For each one, verify the teaching claims, definitions, causal relationships, worked question, solution steps, final answer, units, and source anchor for subject accuracy. Sampling is not allowed.",
            "6. Review every rendered visual ID listed below. Verify the subject meaning, not only loading or formatting: labels, arrows, positions, structures, relationships, scales, units, captions, and correspondence with the topic must all be correct. Sampling is not allowed.",
            "7. Check mastery summaries, glossary policy, and cross-page visual repetition: repeated SVG layouts, reused raster infographics, same visual title/structure across different topics, and repeated decorative pages that make students feel every topic looks the same.",
            "8. Check notation throughout the HTML for code-style maths: b^2, t^3, x^(-1/2), sqrt(...), <=, >=, !=. Confirm superscripts, negative exponents, roots, fractions, statistics formulae, and physics/chemistry symbols are print-ready and readable.",
            "9. Inspect the full HTML at representative desktop and mobile widths for blank sections, broken images, overflow, cut-off content, visual repetition, and notation residue.",
            "10. If any issue is found, return to the Writer, repair the source artifact, rerender HTML, and personally repeat every check on the new hash. Do not approve a repaired handbook from code or diffs alone.",
            "11. Set decision to approved only when the current HTML has no unresolved fixable issue. Python diagnostics cannot make that decision.",
            "",
            "Required topic titles (review every entry):",
            json.dumps(expected_topic_items, ensure_ascii=False, indent=2),
            "",
            "Required rendered visual IDs (review every entry):",
            json.dumps(expected_visual_items, ensure_ascii=False, indent=2),
            "",
            "Write LLM-authored review-ledger/topics-NNN.json and visuals-NNN.json shards with at most 25 reviews each, plus review-ledger/holistic.json. Every review entry must record evidence_locations pointing to the screenshot or browser viewport position actually inspected. Bind every file to the current render_snapshot_id and HTML SHA-256. Then run index-review-ledger and return the compact agent-product-review.json only.",
            "Do not prefill approval booleans. Set each field only after that exact check was personally completed.",
            "",
            "Compact product-review JSON shape:",
            "",
            "{",
            f'  "schema_version": "{PRODUCT_REVIEW_SCHEMA_VERSION}",',
            '  "reviewer_type": "llm",',
            '  "html_opened_and_visually_inspected": "<true only after direct inspection>",',
            f'  "reviewed_html_sha256": "{guide_html_sha256}",',
            '  "render_snapshot_id": "<current snapshot ID>",',
            '  "review_ledger_index_sha256": "<current ledger index SHA-256>",',
            '  "review_iteration": "<positive integer>",',
            '  "html_review_passed": "<true only when all shards and holistic review pass>",',
            '  "complete_html_reviewed": "<true only after the complete assembled HTML was inspected>",',
            '  "machine_validation_used_only_as_supporting_evidence": "<true only when not used as approval>",',
            '  "repair_loop_completed": "<true only after all repairs were rerendered and re-reviewed>",',
            '  "issues_found": [],',
            '  "repairs_made": [],',
            '  "unresolved_fixable_issues": [],',
            '  "decision": "<approved or revisions_required>"',
            "}",
            "",
            "When repairs_made is non-empty, also set html_rerendered_after_repairs and html_review_rerun_after_repairs to true, and increment review_iteration for each visible review pass.",
            "The decision is the LLM Reviewer's current-HTML decision, not a Python-generated certification state.",
            "",
            "# Named handbook HTML",
            "",
            guide_html[:50000]
            + (
                "\n\n[... truncated, full HTML available in the named handbook file ...]"
                if len(guide_html) > 50000
                else ""
            ),
            "",
            "# syllabus-evidence.json",
            "",
            syllabus_evidence[:20000]
            + (
                "\n\n[... truncated, full evidence available ...]"
                if len(syllabus_evidence) > 20000
                else ""
            ),
            "",
            "# validation.json",
            "",
            validation_json,
            "",
            "# quality-inspection.json",
            "",
            quality_inspection if quality_inspection else "[No quality-inspection.json found]",
            "",
            "# images/visual_manifest.json",
            "",
            visual_manifest if visual_manifest else "[No visual manifest found]",
        ]
    )
