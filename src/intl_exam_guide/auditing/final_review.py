from __future__ import annotations

import json
import re
from pathlib import Path

from intl_exam_guide.auditing.quality_inspector import (
    QUALITY_INSPECTION_FILE,
    write_quality_inspection,
)
from intl_exam_guide.core import DeliveryState, course_contract_payload
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.output_names import (
    default_handbook_paths,
    find_handbook_html,
    find_handbook_pdf,
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
PRODUCT_REVIEW_SCHEMA_VERSION = "v0.5-visible-handbook-review"
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
        "reviewer_instruction": "Open the rendered handbook/PDF yourself. Machine validation and quality inspection are supporting evidence only; they are not approval.",
    }
    quality_inspection = quality_inspection_evidence(output_dir)
    product_review = product_review_evidence(output_dir)
    return {
        "agent_review_required": True,
        "workflow": workflow,
        "quality_inspection": quality_inspection,
        "review_questions": [
            "Does the rendered handbook match the requested board, level, subject, language, and style?",
            "Are topic titles teachable rather than parser fragments, broad container labels, or generic syllabus headings?",
            "Can every official source_coverage item be traced from the handbook table of contents to visible teaching treatment, not just JSON coverage?",
            "Do merged official bullets have a defensible teaching reason and visible explanation, worked-example, practice, or sub-skill coverage?",
            "Do sampled worked examples contain concrete questions, solution steps, final answers, and source anchors?",
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
                "Before user handoff, the Agent/LLM must read this packet, inspect the rendered handbook, "
                "classify any content, visual, PDF, or language problems, fix the generation logic or "
                "reviewed assets when possible, rerun review, and only then present the output according "
                "to agent_self_review.status."
            ),
            "must_fix_before_final": [
                "blocking validation errors",
                "collapsed official bullets that are only covered in JSON and not visibly taught",
                "duplicated mastery requirements across independent topics",
                "worked examples that do not match the topic",
                "pending complex infographic assets",
                "near-blank PDF pages",
                "language/style mismatch in student-facing sections",
            ],
            "required_product_review_fields": [
                "visible_handbook_inspected",
                "machine_validation_used_only_as_supporting_evidence",
                "syllabus_outline_compared",
                "granularity_audit_checked",
                "merged_bullets_visible_in_handbook",
                "pdf_pages_sampled",
                "visuals_inspected",
                "glossary_policy_checked",
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
    if not quality_inspection_is_passed(quality_inspection):
        if quality_inspection_has_failed(quality_inspection):
            status = "blocked"
            reasons.append(
                "Quality inspection failed and must be repaired before final review handoff."
            )
        elif status != "blocked":
            status = "draft"
            reasons.append(
                f"Quality inspection evidence is missing or incomplete. Write {QUALITY_INSPECTION_FILE} "
                "after the handbook writer renders the package and before final review."
            )
    if not product_review_is_complete(product_review):
        if status != "blocked":
            status = "draft"
        reasons.append(
            "Final product review evidence is missing or incomplete. "
            f"Write {PRODUCT_REVIEW_FILE} after the active Agent/LLM has compared the visible handbook "
            "with the syllabus outline and repaired fixable issues."
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

    blank_pages = summary_int(summary, "pdf_blank_text_pages")
    if blank_pages:
        if status != "blocked":
            status = "draft"
        reasons.append(f"PDF inspection found {blank_pages} near-blank text page(s).")

    if not reasons:
        reasons.append(
            "No blocking validation, concept-review, image-review, or rendered-text gaps were detected."
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
            "required": True,
            "file": QUALITY_INSPECTION_FILE,
            "present": False,
            "complete": False,
            "issues": [f"Missing {QUALITY_INSPECTION_FILE}."],
            "inspection": {},
        }
    inspection = read_json(path)
    issues = quality_inspection_issues(inspection)
    return {
        "required": True,
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
    issues = product_review_issues(review)
    return {
        "required": True,
        "file": PRODUCT_REVIEW_FILE,
        "present": bool(review),
        "complete": not issues,
        "issues": issues,
        "review": review if isinstance(review, dict) else {},
    }


def product_review_is_complete(product_review: dict[str, object] | None) -> bool:
    return bool(isinstance(product_review, dict) and product_review.get("complete") is True)


def product_review_issues(review: object) -> list[str]:
    if not isinstance(review, dict) or not review:
        return [f"Missing {PRODUCT_REVIEW_FILE}."]
    issues: list[str] = []
    if review.get("schema_version") != PRODUCT_REVIEW_SCHEMA_VERSION:
        issues.append(f"schema_version must be {PRODUCT_REVIEW_SCHEMA_VERSION}.")
    required_true_fields = [
        "visible_handbook_inspected",
        "machine_validation_used_only_as_supporting_evidence",
        "syllabus_outline_compared",
        "granularity_audit_checked",
        "merged_bullets_visible_in_handbook",
        "visuals_inspected",
        "glossary_policy_checked",
        "repair_loop_completed",
    ]
    for field in required_true_fields:
        if review.get(field) is not True:
            issues.append(f"{field} must be true.")
    sampled_pages = review.get("pdf_pages_sampled")
    if not isinstance(sampled_pages, list) or not sampled_pages:
        issues.append("pdf_pages_sampled must list at least one inspected PDF page.")
    unresolved = review.get("unresolved_fixable_issues")
    if unresolved not in (None, []):
        issues.append("unresolved_fixable_issues must be empty before final handoff.")
    repairs = review.get("repairs_made")
    if isinstance(repairs, list) and repairs:
        if review.get("rerendered_after_repairs") is not True:
            issues.append("rerendered_after_repairs must be true when repairs_made is non-empty.")
        if review.get("final_review_rerun_after_repairs") is not True:
            issues.append(
                "final_review_rerun_after_repairs must be true when repairs_made is non-empty."
            )
    elif repairs is not None and not isinstance(repairs, list):
        issues.append("repairs_made must be a list when provided.")
    decision = review.get("decision")
    if not isinstance(decision, str) or not decision.strip():
        issues.append("decision must describe the reviewer handoff decision.")
    return issues



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
    pdf_path = Path(str(stored_pdf)) if stored_pdf else find_handbook_pdf(output_dir, plan.qualification)
    if not pdf_path.exists():
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
    write_quality_inspection(output_dir)
    rerender_pdf(output_dir)
    packet = build_final_review_packet(output_dir)
    path = output_dir / "final-review-packet.json"
    write_review_artifacts(output_dir, packet, path)
    rerender_html(output_dir)
    write_quality_inspection(output_dir)
    rerender_pdf(output_dir)
    packet = build_final_review_packet(output_dir)
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
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return


def rerender_pdf(output_dir: Path) -> None:
    plan_path = output_dir / "guide-plan.json"
    qualification = None
    if plan_path.exists():
        try:
            qualification = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8"))).qualification
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
            qualification = None
    html_path = find_handbook_html(output_dir, qualification)
    if not html_path.exists():
        return
    strip_internal_review_panel_from_file(html_path)
    validation_path = output_dir / "validation.json"
    stored = read_json(validation_path)
    payload = dict(stored) if isinstance(stored, dict) else {}
    pdf_path = find_handbook_pdf(output_dir, qualification)
    try:
        export_pdf(html_path, pdf_path)
    except PdfExportError as exc:
        payload["pdf_error"] = str(exc)
    else:
        payload["pdf"] = str(pdf_path)
        payload["pdf_error"] = None
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
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {} if default is None else default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


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
            "You are the Reviewer in a lightweight three-role workflow. The Analyst and Writer may have made mistakes; inspect the rendered handbook directly.",
            "Machine validation, quality-inspection.json, and final-review-packet.json are supporting evidence only. They are not approval and must not replace visible HTML/PDF review.",
            "",
            "Required checks:",
            "",
            "1. Open or inspect the named HTML output as the student-facing handbook.",
            "2. Compare the topic sequence and source anchors with syllabus-evidence.json, syllabus-outline.json, and granularity_audit when present.",
            "3. Check that official source_coverage items are visibly taught in the handbook, especially bullets merged into larger topics.",
            "4. Check concept explanations, mastery summaries, worked examples, glossary policy, and visuals.",
            "5. If the named PDF exists, sample pages for blank pages, broken images, overflow, or cut-off content.",
            "6. Report repairable issues concretely; do not rubber-stamp the output because validation passed.",
            "",
            "Return JSON only:",
            "",
            "{",
            f'  "schema_version": "{PRODUCT_REVIEW_SCHEMA_VERSION}",',
            '  "visible_handbook_inspected": true,',
            '  "machine_validation_used_only_as_supporting_evidence": true,',
            '  "syllabus_outline_compared": true,',
            '  "granularity_audit_checked": true,',
            '  "merged_bullets_visible_in_handbook": true,',
            '  "concepts_checked": true,',
            '  "visuals_checked": true,',
            '  "glossary_policy_checked": true,',
            '  "pdf_pages_sampled": [],',
            '  "repairable_issues": [],',
            '  "repairs_made": [],',
            '  "unresolved_issues": [],',
            '  "decision": "complete" | "draft" | "blocked"',
            "}",
            "",
            "The decision is the Reviewer's handoff decision, not a Python-generated certification state.",
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
