from __future__ import annotations

import json
import re
from pathlib import Path

from intl_exam_guide.agents import (
    agent_orchestration_payload,
    final_reviewer_is_independent,
    write_agent_orchestration,
)
from intl_exam_guide.auditing.quality_inspector import (
    QUALITY_INSPECTION_FILE,
    write_quality_inspection,
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
    orchestration = agent_orchestration_payload(
        final_review_complete=True,
        quality_inspection_complete=quality_inspection_was_run(output_dir),
    )
    quality_inspection = quality_inspection_evidence(output_dir)
    product_review = product_review_evidence(output_dir)
    return {
        "agent_review_required": True,
        "agent_orchestration": orchestration,
        "quality_inspection": quality_inspection,
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
    orchestration: dict[str, object] | None = None,
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
    if not orchestration_has_independent_final_reviewer(orchestration):
        status = "blocked"
        reasons.append(
            "Final review must be performed by a role independent from outline analysis and handbook writing."
        )
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
            issues.append(
                "final_review_rerun_after_repairs must be true when repairs_made is non-empty."
            )
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
    write_agent_orchestration(
        output_dir,
        final_review_complete=True,
        quality_inspection_complete=quality_inspection_is_passed(
            packet.get("quality_inspection")
            if isinstance(packet.get("quality_inspection"), dict)
            else None
        ),
    )
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
    product_review = packet.get("product_review_evidence")
    quality_inspection = packet.get("quality_inspection")
    agent_review_ready = (
        isinstance(agent_review, dict)
        and agent_review.get("status") == "ready"
        and product_review_is_complete(product_review if isinstance(product_review, dict) else None)
        and quality_inspection_is_passed(
            quality_inspection if isinstance(quality_inspection, dict) else None
        )
    )
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
    product_review = packet.get("product_review_evidence")
    quality_inspection = packet.get("quality_inspection")
    agent_review_ready = (
        isinstance(agent_review, dict)
        and agent_review.get("status") == "ready"
        and product_review_is_complete(product_review if isinstance(product_review, dict) else None)
        and quality_inspection_is_passed(
            quality_inspection if isinstance(quality_inspection, dict) else None
        )
    )
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
    Build detailed prompt for independent LLM Reviewer to audit the handbook.

    This is Phase 4 of the five-role workflow. The LLM must:
    1. Read the rendered handbook (guide.html)
    2. Compare with original syllabus evidence
    3. Consider the Quality Inspector's fast structure/completeness report
    4. Check teaching quality, visual appropriateness, PDF rendering
    5. Output final-review-packet.json with approval or repair instructions

    CRITICAL: The reviewer is an independent subagent with NO access to Analyst/Writer/Inspector conversation context.
    """

    guide_html = (
        read_text(guide_html_path) if guide_html_path.exists() else "[guide.html not found]"
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
            "=" * 80,
            "PHASE 4: FINAL REVIEWER (INDEPENDENT AUDIT)",
            "=" * 80,
            "",
            "You are the final_reviewer, an independent subagent auditing the revision handbook.",
            "",
            "CRITICAL: You are NOT the analyst, writer, or inspector. You did NOT create this content.",
            "You are reviewing it FRESH with NO access to the Analyst/Writer/Inspector conversation context.",
            "",
            "Your role: Independent quality gate before final delivery.",
            "",
            "INPUT FILES:",
            "1. guide.html - The rendered handbook (see below)",
            "2. syllabus-evidence.json - Original specification PDF evidence (see below)",
            "3. validation.json - Automated checks (see below)",
            "4. quality-inspection.json - Fast structure/completeness check from Quality Inspector (see below, if exists)",
            "5. images/visual_manifest.json - Visual asset list (see below, if exists)",
            "",
            "YOUR AUDIT CHECKLIST:",
            "",
            "=" * 80,
            "CHECKPOINT 1: SYLLABUS OUTLINE ACCURACY",
            "=" * 80,
            "",
            "Task:",
            "- Read Module 3 (Study Roadmap / Topic Map) in guide.html",
            "- Read syllabus-evidence.json pages",
            "- Question: Does the outline match the official specification?",
            "",
            "Look for:",
            "- Are the topic titles accurate? (not 'Content 1.1' placeholders)",
            "- Are the exam points covered?",
            "- Are there topics in the handbook that aren't in the syllabus?",
            "- Are there major syllabus topics missing from the handbook?",
            "",
            "Output:",
            "{",
            '  "syllabus_outline_compared": {',
            '    "status": "approved" | "repair_needed",',
            '    "notes": "Topic boundaries match official spec pages 12-35. All exam points covered." | "Issue description"',
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 2: TEACHING QUALITY (VISIBLE HANDBOOK)",
            "=" * 80,
            "",
            "Task:",
            "- Read Module 5 (Topic Guides) in guide.html",
            "- Question: Are concept explanations clear, analogies helpful, examples appropriate?",
            "",
            "Look for:",
            "- Vague explanations ('students should understand the topic')",
            "- Confusing analogies (culturally inappropriate, misleading comparisons)",
            "- Worked examples with errors or incomplete solutions",
            "- Inconsistent style (mixes formal and friendly voice)",
            "- Formulaic AI wording ('delve into', 'it's important to note', 'in conclusion')",
            "- Copy-pasted syllabus text instead of original teaching language",
            "",
            "Output:",
            "{",
            '  "visible_handbook_inspected": {',
            '    "status": "approved" | "repair_needed",',
            '    "issues": [',
            '      "Topic 3.2 analogy compares journal entries to filing taxes which may confuse international students",',
            '      "Worked example 4.1 solution step 2 has calculation error: should be 125 not 120"',
            "    ]",
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 3: VISUAL APPROPRIATENESS",
            "=" * 80,
            "",
            "Task:",
            "- Read images/visual_manifest.json (if exists)",
            "- Read visual placements in guide.html",
            "- Question: Are visuals appropriate and non-repetitive?",
            "",
            "Look for:",
            "- Missing visuals where diagrams would genuinely help",
            "  (e.g., 'Chemical bonding structure' with no diagram)",
            "- Unnecessary visuals for text-only topics",
            "  (e.g., 'Essay writing steps' doesn't need an infographic)",
            "- Repetitive visual specs",
            "  (e.g., 5 topics all have 'process flowchart' with identical structure)",
            "- Vague visual specs",
            "  (e.g., 'diagram' without specifics)",
            "",
            "Output:",
            "{",
            '  "visuals_inspected": {',
            '    "status": "approved" | "repair_needed",',
            '    "issues": [',
            '      "Topic 2.3 Ionic bonding has no visual spec, but spatial structure needs a labeled diagram",',
            '      "Topics 4.1, 4.2, 4.3 all spec identical process flowcharts - appears repetitive"',
            "    ]",
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 4: PDF RENDERING (IF AVAILABLE)",
            "=" * 80,
            "",
            "Task:",
            "- If guide.pdf exists, sample a few pages",
            "- Question: Are there rendering issues?",
            "",
            "Look for:",
            "- Blank pages",
            "- Broken image links (shows 'image not found' icon)",
            "- Page count unreasonable (e.g., 200 pages for 6-topic IGCSE subject)",
            "- Text overflow or cut-off content",
            "",
            "Output:",
            "{",
            '  "pdf_pages_sampled": {',
            '    "status": "approved" | "not_checked" | "repair_needed",',
            '    "notes": "PDF is 42 pages, no blank pages, all images render correctly" | "Issue description"',
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 5: VALIDATION ISSUES",
            "=" * 80,
            "",
            "Task:",
            "- Read validation.json",
            "- Question: Are there severity='error' items?",
            "",
            "Look for:",
            "- Errors that block final delivery",
            "- Warnings that are expected (e.g., 'pending concept imports' for prompt-queue workflow)",
            "",
            "Output:",
            "{",
            '  "validation_issues_reviewed": {',
            '    "status": "clean" | "has_errors",',
            '    "summary": "No errors. 2 warnings about pending infographic imports (expected)." | "Error summary"',
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 6: QUALITY INSPECTION HANDOFF",
            "=" * 80,
            "",
            "Task:",
            "- Read quality-inspection.json if present",
            "- Question: Did the fast Inspector pass the package to final review?",
            "",
            "Look for:",
            "- inspection_status must be pass for final-ready delivery",
            "- error-level file/module/concept/placeholder issues mean repair is needed before final approval",
            "- warnings can be acknowledged and sampled during your deeper review",
            "",
            "Output:",
            "{",
            '  "quality_inspection_reviewed": {',
            '    "status": "passed" | "missing" | "repair_needed",',
            '    "notes": "Quality Inspector passed the package." | "Issue description"',
            "  }",
            "}",
            "",
            "=" * 80,
            "CHECKPOINT 7: REPAIR LOOP DECISION",
            "=" * 80,
            "",
            "Task:",
            "- If you found issues in Checkpoints 1-5: output 'repair_needed' with detailed instructions",
            "- If all checkpoints approved: output 'approved'",
            "",
            "Output:",
            "{",
            '  "repair_loop_completed": {',
            '    "status": "repair_needed" | "approved",',
            '    "instructions": "Fix the 2 issues in visible_handbook_inspected, then rerender guide.html and resubmit for review." | null',
            "  }",
            "}",
            "",
            "=" * 80,
            "FULL OUTPUT JSON SCHEMA",
            "=" * 80,
            "",
            "{",
            '  "schema_version": "v0.5-final-review",',
            '  "syllabus_outline_compared": { ... },',
            '  "visible_handbook_inspected": { ... },',
            '  "visuals_inspected": { ... },',
            '  "pdf_pages_sampled": { ... },',
            '  "validation_issues_reviewed": { ... },',
            '  "quality_inspection_reviewed": { ... },',
            '  "repair_loop_completed": { ... }',
            "}",
            "",
            "CRITICAL RULES:",
            "",
            "1. You are INDEPENDENT. Do not assume Phase 1/2 decisions were correct.",
            "   Re-check everything against the original syllabus.",
            "",
            "2. Do NOT rubber-stamp approval.",
            "   If you find issues, report them clearly.",
            "",
            "3. 'repair_needed' is EXPECTED.",
            "   First review often finds issues. That's healthy.",
            "",
            "4. Be SPECIFIC in your issues[].",
            "   Not 'some examples are wrong'. Say 'Topic 3.2 worked example step 2: calculation error'.",
            "",
            "5. Check for FORMULAIC AI WORDING.",
            "   'delve into', 'it is important to note', 'in conclusion', 'leverage', 'utilize'.",
            "   These phrases suggest the writer copy-pasted instead of writing original teaching content.",
            "",
            "6. Visual judgment is CONTENT WORK.",
            "   A handbook doesn't need visuals for every topic.",
            "   But spatial/structural topics (chemistry bonding, circuit diagrams) DO need them.",
            "",
            "AFTER YOU OUTPUT THIS JSON:",
            "- If repair_needed: Python will notify the handler to fix issues, rerender, and call you again",
            "- If approved: Python marks delivery_status = 'final-ready' only after quality inspection and product-review evidence also pass",
            "",
            "EXCEPTION ESCALATION:",
            "",
            "1. Systemic problems (5+ topics with the same issue):",
            "   Mark status='repair_needed' and describe the repeated pattern so Coordinator can return it to Writer.",
            "",
            "2. Out-of-scope content:",
            "   Flag the exact topic and ask Coordinator to return to syllabus_outline_analyst for evidence re-check.",
            "",
            "3. Unresolvable ambiguity:",
            "   Use approved_with_notes only when the handbook is otherwise usable and the issue genuinely needs a subject specialist.",
            "",
            "4. Quality Inspector failed:",
            "   Do not perform a deep approval. Mark repair_needed and send the Inspector issues back to Coordinator.",
            "",
            "Do not spend more than 15 minutes stuck on one uncertain issue. Flag it concretely and move on.",
            "",
            "=" * 80,
            "FILE 1: guide.html (RENDERED HANDBOOK)",
            "=" * 80,
            "",
            guide_html[:50000]
            + (
                "\n\n[... truncated, full HTML available in guide.html ...]"
                if len(guide_html) > 50000
                else ""
            ),
            "",
            "=" * 80,
            "FILE 2: syllabus-evidence.json (ORIGINAL SPECIFICATION)",
            "=" * 80,
            "",
            syllabus_evidence[:20000]
            + (
                "\n\n[... truncated, full evidence available ...]"
                if len(syllabus_evidence) > 20000
                else ""
            ),
            "",
            "=" * 80,
            "FILE 3: validation.json (AUTOMATED CHECKS)",
            "=" * 80,
            "",
            validation_json,
            "",
            "=" * 80,
            "FILE 4: quality-inspection.json (FAST INSPECTION REPORT, IF EXISTS)",
            "=" * 80,
            "",
            quality_inspection
            if quality_inspection
            else "[No quality-inspection.json found - mark quality_inspection_reviewed.status as missing]",
            "",
            "=" * 80,
            "FILE 5: images/visual_manifest.json (IF EXISTS)",
            "=" * 80,
            "",
            visual_manifest
            if visual_manifest
            else "[No visual manifest found - no visuals generated yet]",
            "",
            "=" * 80,
            "BEGIN YOUR AUDIT",
            "=" * 80,
        ]
    )
