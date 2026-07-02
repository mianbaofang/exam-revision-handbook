from __future__ import annotations

import json
import re
from pathlib import Path

from intl_exam_guide.agents import (
    agent_orchestration_payload,
    final_reviewer_is_independent,
    write_agent_orchestration,
)
from intl_exam_guide.core import DeliveryState, course_contract_payload
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf
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
    "svg-fallback-needs-review",
}
PRODUCT_REVIEW_FILE = "agent-product-review.json"


def build_final_review_packet(output_dir: Path) -> dict[str, object]:
    validation = read_json(output_dir / "validation.json")
    qualification = read_json(output_dir / "qualification.json")
    guide_plan = read_json(output_dir / "guide-plan.json")
    manifest_entries = load_visual_manifest(output_dir / "images")
    infographic_jobs = read_json(output_dir / "images" / "infographic_jobs.json", default=[])
    html = read_text(output_dir / "guide.html")
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
    orchestration = agent_orchestration_payload(final_review_complete=True)
    product_review = product_review_evidence(output_dir)
    return {
        "agent_review_required": True,
        "agent_orchestration": orchestration,
        "review_questions": [
            "Does the rendered handbook match the requested board, level, subject, language, and style?",
            "Are topic titles teachable rather than parser fragments or generic labels?",
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
            orchestration,
            product_review,
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
                "duplicated mastery requirements across independent topics",
                "worked examples that do not match the topic",
                "pending complex infographic assets",
                "near-blank PDF pages",
                "language/style mismatch in student-facing sections",
            ],
            "required_product_review_fields": [
                "visible_handbook_inspected",
                "syllabus_outline_compared",
                "pdf_pages_sampled",
                "visuals_inspected",
                "glossary_policy_checked",
                "repair_loop_completed",
                "decision",
            ],
        },
        "review_summary": summary,
        "qualification": qualification_summary(qualification),
        "guide_plan": {"available": isinstance(guide_plan, dict), "keys": sorted(guide_plan) if isinstance(guide_plan, dict) else []},
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
    orchestration: dict[str, object] | None = None,
    product_review: dict[str, object] | None = None,
) -> dict[str, object]:
    """Give the Agent a concrete final-delivery verdict to review, not just raw gates."""

    reasons: list[str] = []
    status = "ready"
    error_count = summary_int(machine_validation, "error_count")
    if error_count:
        status = "blocked"
        reasons.append(f"{error_count} validation error(s) must be fixed before delivery.")
    if not rendered_text.strip():
        status = "blocked"
        reasons.append("Rendered student-facing text is empty or unreadable.")
    if not orchestration_has_independent_final_reviewer(orchestration):
        status = "blocked"
        reasons.append("Final review must be performed by a role independent from outline analysis and handbook writing.")
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
        reasons.append(f"{pending_concepts} topic concept explanation(s) still need Agent/LLM review.")

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
        reasons.append("No blocking validation, concept-review, image-review, or rendered-text gaps were detected.")
    return {
        "status": status,
        "reasons": reasons,
        "must_not_present_as_final": status != "ready",
        "agent_must_inspect_before_handoff": True,
    }


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
    if review.get("schema_version") != "v0.4-agent-product-review":
        issues.append("schema_version must be v0.4-agent-product-review.")
    required_true_fields = [
        "visible_handbook_inspected",
        "syllabus_outline_compared",
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
            issues.append("final_review_rerun_after_repairs must be true when repairs_made is non-empty.")
    elif repairs is not None and not isinstance(repairs, list):
        issues.append("repairs_made must be a list when provided.")
    if review.get("decision") != "final-ready":
        issues.append("decision must be final-ready.")
    return issues


def orchestration_has_independent_final_reviewer(orchestration: object) -> bool:
    if not isinstance(orchestration, dict):
        return False
    roles = orchestration.get("roles")
    if not isinstance(roles, list):
        return False
    return final_reviewer_is_independent([role for role in roles if isinstance(role, dict)])


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

    html_path = output_dir / "guide.html"
    stored_pdf = stored_validation.get("pdf") if isinstance(stored_validation, dict) else None
    pdf_path = Path(str(stored_pdf)) if stored_pdf else None
    if pdf_path is None and (output_dir / "guide.pdf").exists():
        pdf_path = output_dir / "guide.pdf"
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
    rerender_pdf(output_dir)
    packet = build_final_review_packet(output_dir)
    path = output_dir / "final-review-packet.json"
    write_review_artifacts(output_dir, packet, path)
    rerender_html(output_dir)
    rerender_pdf(output_dir)
    packet = build_final_review_packet(output_dir)
    write_review_artifacts(output_dir, packet, path)
    return path


def write_review_artifacts(output_dir: Path, packet: dict[str, object], path: Path) -> None:
    write_agent_orchestration(output_dir, final_review_complete=True)
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
    agent_review = packet.get("agent_self_review")
    agent_review_ready = isinstance(agent_review, dict) and agent_review.get("status") == "ready"
    try:
        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return
    (output_dir / "delivery-contract.json").write_text(
        json.dumps(
            course_contract_payload(
                plan,
                str(delivery_status),
                agent_review_ready=agent_review_ready,
                final_review_complete=True,
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
        render_html(plan, output_dir / "guide.html", output_dir / "images" / "visual_manifest.json")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return


def rerender_pdf(output_dir: Path) -> None:
    html_path = output_dir / "guide.html"
    if not html_path.exists():
        return
    validation_path = output_dir / "validation.json"
    stored = read_json(validation_path)
    payload = dict(stored) if isinstance(stored, dict) else {}
    pdf_path = output_dir / "guide.pdf"
    try:
        export_pdf(html_path, pdf_path)
    except PdfExportError as exc:
        payload["pdf_error"] = str(exc)
    else:
        payload["pdf"] = str(pdf_path)
        payload["pdf_error"] = None
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_refreshed_validation(output_dir: Path, packet: dict[str, object]) -> None:
    machine = packet.get("machine_validation")
    if not isinstance(machine, dict):
        return
    stored = read_json(output_dir / "validation.json")
    payload = dict(stored) if isinstance(stored, dict) else {}
    payload["issues"] = machine.get("issues", [])
    payload["review_summary"] = packet.get("review_summary", {})
    payload["delivery_status"] = machine.get("delivery_status")
    agent_review = packet.get("agent_self_review")
    agent_review_ready = isinstance(agent_review, dict) and agent_review.get("status") == "ready"
    delivery_status = machine.get("delivery_status")
    payload["delivery_state"] = DeliveryState.from_delivery_status(
        str(delivery_status) if delivery_status is not None else None,
        agent_review_ready=agent_review_ready,
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
        1
        for issue in issues
        if isinstance(issue, dict) and issue.get("severity") == severity
    )


def qualification_summary(qualification: object) -> dict[str, object]:
    if not isinstance(qualification, dict):
        return {"title": None, "topic_count": 0}
    topics = qualification.get("topics", [])
    return {
        "title": qualification.get("title"),
        "topic_count": len(topics) if isinstance(topics, list) else 0,
    }
