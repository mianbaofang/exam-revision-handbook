"""LLM concept integration helpers for guide planning."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from intl_exam_guide.llm.provider import ConceptExplanation, ConceptJob
from intl_exam_guide.auditing.visual_semantics import visual_semantic_issues
from intl_exam_guide.models import GuidePlan, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.identifiers import normalized_identifier_text, stable_requirement_id
from intl_exam_guide.planning.source_points import visible_source_points

VISUAL_DECISION_ROUTES = {"text-ok", "exact-svg", "kroki-diagram", "external-infographic"}
FALLBACK_VISUAL_DECISION_STATE = "missing-writer-visual-decision-fallback"


class VisualDecisionContractError(ValueError):
    """Raised when a Writer concept entry violates the v0.5 visual contract."""


def collect_concept_jobs(
    topics: list[Topic],
    subject: str,
    level: str,
) -> list[ConceptJob]:
    """Collect concept generation jobs from topics."""

    concept_jobs: list[ConceptJob] = []
    level_name = "A-Level" if "a_level" in level.lower() or "as" in level.lower() else "IGCSE"

    for topic in topics:
        points = visible_source_points(topic, limit=4)
        concept_term = points[0] if points else topic.title
        context_parts = [topic.title] + points[:3]
        context_snippet = " | ".join(context_parts)[:200]
        concept_jobs.append(
            ConceptJob(
                topic_id=stable_requirement_id(topic),
                topic_title=topic.title,
                concept_term=concept_term,
                subject=subject,
                level=level_name,
                context_snippet=context_snippet,
            )
        )

    return concept_jobs


def apply_concept_explanations(
    topic_guides: list[TopicGuide],
    explanations: list[ConceptExplanation],
) -> list[TopicGuide]:
    """Apply provider-generated explanations to topic guides."""

    explanation_map: dict[str, ConceptExplanation] = {
        normalized_identifier_text(exp.concept_term): exp
        for exp in explanations
        if exp.status == "generated"
    }

    updated_guides: list[TopicGuide] = []

    for guide in topic_guides:
        exact_keys = {
            normalized_identifier_text(guide.topic_title),
            *{
                normalized_identifier_text(point)
                for point in guide.source_points
                if point.strip()
            },
            *{
                normalized_identifier_text(snippet.text)
                for snippet in guide.source_snippets
                if snippet.text.strip()
            },
        }
        matches = [explanation_map[key] for key in exact_keys if key in explanation_map]
        matching_explanation = matches[0] if len(matches) == 1 else None

        if matching_explanation:
            updated_guides.append(
                replace(
                    guide,
                    essence=matching_explanation.explanation or guide.essence,
                    analogy=matching_explanation.analogy or guide.analogy,
                    mini_worked_example=matching_explanation.example or guide.mini_worked_example,
                    pitfall=matching_explanation.common_misconception or guide.pitfall,
                )
            )
        else:
            updated_guides.append(guide)

    return updated_guides


def concept_entries_from_explanations(
    jobs: list[ConceptJob],
    explanations: list[ConceptExplanation],
    *,
    external_route_available: bool | None = None,
) -> list[dict[str, object]]:
    """Convert provider results into the canonical concept_explanations.json shape."""

    entries: list[dict[str, object]] = []
    for job, explanation in zip(jobs, explanations, strict=False):
        entry = concept_entry_from_explanation(
            job,
            explanation,
            external_route_available=external_route_available,
        )
        if entry:
            entries.append(entry)
    return entries


def concept_entry_from_explanation(
    job: ConceptJob,
    explanation: ConceptExplanation,
    *,
    external_route_available: bool | None = None,
) -> dict[str, object] | None:
    if explanation.status != "generated" or not explanation.explanation.strip():
        return None

    bullets = explanation_bullets(explanation)
    if len(bullets) < 2:
        return None

    entry: dict[str, object] = {
        "topic_id": job.topic_id,
        "topic_title": job.topic_title,
        "concept_term": job.concept_term,
        "explanations": bullets[:4],
        "essence": explanation.explanation.strip(),
        "content_provenance": "llm-authored",
        "delivery_eligible": True,
    }
    if explanation.analogy:
        entry["analogy"] = explanation.analogy.strip()
    if explanation.example:
        entry["mini_worked_example"] = explanation.example.strip()
    if explanation.common_misconception:
        entry["pitfall"] = explanation.common_misconception.strip()
    metadata = explanation.metadata or {}
    visual_decision = metadata.get("visual_decision")
    if isinstance(visual_decision, dict):
        entry["visual_decision"] = visual_decision
    else:
        entry["visual_decision"] = fallback_visual_decision(
            "The Writer did not request a separate visual for this topic."
        )
        entry["provenance"] = "python-fallback"
        entry["delivery_eligible"] = False
    visual_guidance = metadata.get("visual_guidance")
    if isinstance(visual_guidance, dict):
        entry["visual_guidance"] = visual_guidance
    visual_spec = metadata.get("visual_spec")
    if isinstance(visual_spec, dict):
        entry["visual_spec"] = visual_spec
    if metadata:
        entry["writer_metadata"] = dict(metadata)
    validate_visual_decision_entry(
        entry,
        allow_fallback=True,
        external_route_available=external_route_available,
    )
    return entry


def explanation_bullets(explanation: ConceptExplanation) -> list[str]:
    values = [explanation.explanation]
    if explanation.example:
        values.append(explanation.example)
    if explanation.common_misconception:
        values.append(explanation.common_misconception)
    if explanation.analogy:
        values.append(explanation.analogy)
    return [value.strip() for value in values if value and value.strip()]


def apply_concept_entries(
    plan: GuidePlan,
    entries: list[dict[str, object]],
    force: bool = False,
) -> tuple[int, list[str]]:
    """Apply canonical concept explanation entries to a GuidePlan in place."""

    guides = {guide.topic_title: guide for guide in plan.topic_guides}
    practice_items = {
        item.topic_title: item for item in getattr(plan, "practice_items", [])
    }
    qualification = getattr(plan, "qualification", None)
    qualification_topics = getattr(qualification, "topics", [])
    topic_ids = {
        stable_requirement_id(topic): topic.title for topic in qualification_topics
    }
    imported = 0
    missing: list[str] = []
    for entry in entries:
        topic_title = str(entry.get("topic_title") or "")
        topic_id = str(entry.get("topic_id") or "").strip()
        values = normalized_explanation_values(entry.get("explanations"))
        if not topic_title or len(values) < 2:
            continue
        if topic_id:
            expected_title = topic_ids.get(topic_id)
            if expected_title is None:
                missing.append(topic_title or topic_id)
                continue
            if topic_title and topic_title != expected_title:
                missing.append(topic_title)
                continue
            topic_title = expected_title
        guide = guides.get(topic_title)
        if not guide:
            missing.append(topic_title)
            continue
        mastery_summary = str(entry.get("mastery_summary") or "").strip()
        if mastery_summary:
            guide.mastery_summary = mastery_summary
        if force or values:
            guide.checklist = values[:4]
            guide.explanations = values[:4]
        apply_optional_text(entry, guide, "essence")
        apply_optional_text(entry, guide, "analogy")
        apply_optional_text(entry, guide, "mini_worked_example")
        apply_optional_text(entry, guide, "pitfall")
        guide.diagram_brief = build_clean_diagram_brief(topic_title, values)
        steps = entry.get("worked_solution_steps")
        clean_steps: list[str] = []
        if isinstance(steps, list):
            clean_steps = [str(value).strip() for value in steps if str(value).strip()]
            if clean_steps:
                guide.worked_solution_steps = clean_steps[:5]
        practice_item = practice_items.get(topic_title)
        worked_example = str(entry.get("mini_worked_example") or "").strip()
        if practice_item and worked_example:
            practice_item.question = worked_example
        if practice_item and clean_steps:
            practice_item.public_solution_steps = clean_steps[:5]
        validate_visual_decision_entry(
            entry,
            allow_fallback=True,
            external_route_available=_external_visual_route_available(plan),
        )
        visual = visual_brief_from_entry(plan, topic_title, entry)
        if visual:
            upsert_visual_brief(plan, visual)
        imported += 1
    return imported, missing


def fallback_visual_decision(no_visual_reason: str) -> dict[str, object]:
    reason = no_visual_reason.strip()
    return {
        "recommended_route": "text-ok",
        "learning_claim": "The written explanation and worked example carry the learning for this topic.",
        "no_visual_reason": reason,
        "visual_teaching_value": "not-needed",
        "workflow_state": FALLBACK_VISUAL_DECISION_STATE,
        "source": "python-draft-fallback",
        "visual_guidance": {
            "visual_kind": "none",
            "no_visual_rationale": reason,
        },
    }


def visual_decision_route(entry: dict[str, object]) -> str:
    visual_decision = entry.get("visual_decision")
    if not isinstance(visual_decision, dict):
        raise VisualDecisionContractError("visual_decision must be recorded for every topic.")
    route = str(visual_decision.get("recommended_route") or "").strip().lower()
    if route not in VISUAL_DECISION_ROUTES:
        allowed = ", ".join(sorted(VISUAL_DECISION_ROUTES))
        raise VisualDecisionContractError(
            f"visual_decision.recommended_route must be one of: {allowed}."
        )
    return route


def is_fallback_visual_decision(entry: dict[str, object]) -> bool:
    visual_decision = entry.get("visual_decision")
    if not isinstance(visual_decision, dict):
        return False
    workflow_state = str(visual_decision.get("workflow_state") or "").strip()
    source = str(visual_decision.get("source") or "").strip()
    return (
        workflow_state == FALLBACK_VISUAL_DECISION_STATE
        or source == "python-draft-fallback"
    )


def _external_visual_route_available(plan: GuidePlan) -> bool:
    """Return whether a verified callable external image route is recorded."""

    options = getattr(plan, "run_options", None)
    capability = str(getattr(options, "external_visual_capability", "") or "").strip().lower()
    method = str(getattr(options, "image_method", "") or "").strip()
    return (
        capability == "yes"
        and bool(getattr(options, "image_route_verified", False))
        and method.lower() not in {"", "none", "disabled", "prompt-queue"}
    )


def validate_visual_decision_entry(
    entry: dict[str, object],
    *,
    allow_fallback: bool = False,
    external_route_available: bool | None = None,
) -> None:
    title = str(entry.get("topic_title") or entry.get("concept_term") or "topic")
    route = visual_decision_route(entry)
    visual_decision = entry["visual_decision"]
    assert isinstance(visual_decision, dict)
    is_fallback = is_fallback_visual_decision(entry)
    if is_fallback and not allow_fallback:
        raise VisualDecisionContractError(
            f"{title}: visual_decision is a Python draft fallback, not a Writer decision."
        )
    has_visual_spec = isinstance(entry.get("visual_spec"), dict)
    if route == "text-ok":
        reason = str(visual_decision.get("no_visual_reason") or "").strip()
        if len(reason) < 12:
            raise VisualDecisionContractError(
                f"{title}: text-ok visual_decision requires no_visual_reason."
            )
        if has_visual_spec:
            raise VisualDecisionContractError(
                f"{title}: text-ok visual_decision must not include visual_spec."
            )
    elif not has_visual_spec:
        raise VisualDecisionContractError(
            f"{title}: {route} visual_decision requires visual_spec."
        )

    if route != "text-ok":
        visual_spec = entry.get("visual_spec")
        if isinstance(visual_spec, dict):
            semantic_issues = visual_semantic_issues(
                {
                    "id": title,
                    "recommended_route": {"route": route},
                    "semantic_contract": visual_spec.get("semantic_contract"),
                }
            )
            if semantic_issues:
                raise VisualDecisionContractError(
                    f"{title}: {semantic_issues[0]['message']}"
                )

    # Historical/Python draft fallbacks remain readable for migration and
    # incremental recovery. They are never delivery-eligible and are rejected
    # by the formal quality gate; do not require Writer-only guidance here.
    if is_fallback and allow_fallback:
        return

    guidance = entry.get("visual_guidance")
    if not isinstance(guidance, dict):
        # Keep the route/spec errors above stable for callers that rely on them;
        # missing guidance is still a hard contract error for every valid route.
        raise VisualDecisionContractError(
            f"{title}: visual_guidance is required for every topic."
        )

    def _text_value(key: str) -> str:
        value = guidance.get(key)
        return value.strip() if isinstance(value, str) else ""

    visual_kind = _text_value("visual_kind")
    if not visual_kind:
        raise VisualDecisionContractError(
            f"{title}: visual_guidance.visual_kind is required."
        )
    if route == "text-ok":
        if visual_kind.lower() != "none":
            raise VisualDecisionContractError(
                f"{title}: text-ok visual_guidance must use visual_kind='none'."
            )
        rationale = _text_value("no_visual_rationale")
        reason = str(visual_decision.get("no_visual_reason") or "").strip()
        if len(rationale) < 12:
            raise VisualDecisionContractError(
                f"{title}: text-ok visual_guidance requires no_visual_rationale."
            )
        if " ".join(rationale.split()) != " ".join(reason.split()):
            raise VisualDecisionContractError(
                f"{title}: no_visual_rationale must match visual_decision.no_visual_reason."
            )
        lowered_rationale = " ".join(rationale.lower().split())
        disallowed_shortcuts = (
            "no time",
            "lack of time",
            "not enough time",
            "provider unavailable",
            "no provider",
            "image provider",
            "convenience",
            "easier to write",
            "text is enough",
            "text alone is enough",
            "no need to draw",
        )
        if any(phrase in lowered_rationale for phrase in disallowed_shortcuts):
            raise VisualDecisionContractError(
                f"{title}: text-ok rationale cannot omit a useful visual for time, provider, convenience, or generic text-sufficiency reasons."
            )
        return

    required_guidance = {
        "composition": "composition",
        "reading_order": "reading_order",
        "required_elements": "required_elements",
        "student_inference": "student_inference",
    }
    for key, label in required_guidance.items():
        value = guidance.get(key)
        if isinstance(value, str):
            valid = bool(value.strip())
        elif isinstance(value, list):
            valid = any(str(item).strip() for item in value)
        else:
            valid = False
        if not valid:
            raise VisualDecisionContractError(
                f"{title}: non-text visual_guidance requires {label}."
            )

    if route in {"exact-svg", "kroki-diagram"}:
        visual_spec = entry.get("visual_spec")
        svg_fit = ""
        if isinstance(visual_spec, dict):
            svg_fit = str(visual_spec.get("svg_fit") or "").strip().lower()
        if svg_fit != "exact":
            raise VisualDecisionContractError(
                f"{title}: {route} visual_spec must declare svg_fit='exact'; otherwise use external-infographic."
            )
        exactness_exception = _text_value("exactness_exception")
        if len(exactness_exception) < 12:
            raise VisualDecisionContractError(
                f"{title}: {route} visual_guidance requires exactness_exception."
            )
        if external_route_available:
            external_exclusion = _text_value("external_route_exclusion_reason")
            if len(external_exclusion) < 12:
                raise VisualDecisionContractError(
                    f"{title}: verified external routes require external_route_exclusion_reason for {route}."
                )


def visual_brief_from_entry(
    plan: GuidePlan,
    topic_title: str,
    entry: dict[str, object],
) -> VisualBrief | None:
    route = visual_decision_route(entry)
    if route == "text-ok":
        return None
    visual_spec = entry.get("visual_spec")
    if not isinstance(visual_spec, dict):
        return None
    prompt = str(visual_spec.get("prompt") or "").strip()
    visual_type = str(visual_spec.get("visual_type") or visual_spec.get("type") or "").strip()
    complexity = complexity_for_visual_route(route, visual_spec)
    if not prompt or not visual_type:
        return None

    topic = next((item for item in plan.qualification.topics if item.title == topic_title), None)
    source_points = visual_source_points(topic, entry)
    provider = provider_for_visual_route(plan, route, complexity)
    return VisualBrief(
        topic_title=topic_title,
        focus_point=str(
            visual_spec.get("focus_point")
            or entry.get("concept_term")
            or entry.get("student_title")
            or topic_title
        ).strip(),
        trigger=str(visual_spec.get("trigger") or "LLM Writer selected this visual.").strip(),
        visual_type=visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=source_points,
        source_snippets=(topic.source_snippets[:2] if topic else []),
        llm_visual_spec=True,
        svg_fit=str(visual_spec.get("svg_fit") or "").strip(),
        semantic_contract=(
            dict(visual_spec.get("semantic_contract", {}))
            if isinstance(visual_spec.get("semantic_contract"), dict)
            else {}
        ),
    )


def visual_source_points(topic: Topic | None, entry: dict[str, object]) -> list[str]:
    visual_spec = entry.get("visual_spec")
    candidates = None
    if isinstance(visual_spec, dict):
        candidates = visual_spec.get("source_points")
    if not candidates:
        candidates = entry.get("source_points")
    if isinstance(candidates, list):
        points = [str(value).strip() for value in candidates if str(value).strip()]
        if points:
            return points[:4]
    return visible_source_points(topic, limit=4) if topic else []


def complexity_for_visual_route(route: str, visual_spec: dict[str, object]) -> str:
    complexity = str(visual_spec.get("complexity") or "").strip().lower()
    if route in {"exact-svg", "kroki-diagram"}:
        return "svg-basic"
    if route == "external-infographic":
        return "infographic"
    if complexity in {"svg-basic", "infographic"}:
        return complexity
    return "infographic"


def provider_for_visual_route(plan: GuidePlan, route: str, complexity: str) -> str:
    if route == "kroki-diagram":
        return "kroki"
    if route == "exact-svg" or complexity == "svg-basic":
        return "llm-svg"
    if route == "external-infographic" and _external_visual_route_available(plan):
        method = str(plan.run_options.image_method or "").strip()
        if method.lower() in {"custom", "prompt-queue"}:
            model = str(plan.run_options.image_model or "").strip()
            return f"custom:{model}" if model else method
        return method
    if plan.run_options.image_provider == "custom":
        model = plan.run_options.image_model or "model-not-set"
        return f"custom:{model}"
    return "prompt-queue"


def provider_for_visual_spec(plan: GuidePlan, complexity: str) -> str:
    return provider_for_visual_route(plan, "exact-svg" if complexity == "svg-basic" else "external-infographic", complexity)


def upsert_visual_brief(plan: GuidePlan, visual: VisualBrief) -> None:
    plan.visual_briefs = [
        brief for brief in plan.visual_briefs if brief.topic_title != visual.topic_title
    ]
    plan.visual_briefs.append(visual)


def normalized_explanation_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split("\n") if part.strip()]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def apply_optional_text(entry: dict[str, object], guide: TopicGuide, field_name: str) -> None:
    value = entry.get(field_name)
    if isinstance(value, str) and value.strip():
        setattr(guide, field_name, value.strip())


def build_clean_diagram_brief(topic_title: str, values: list[str]) -> str:
    branches = [value.rstrip(".") for value in values[:3]]
    branch_text = ", ".join(branches) if branches else "definition, relationship, common pitfall"
    return (
        f"Draw a clean concept map for '{topic_title}' with the central title in the middle, "
        f"branches for {branch_text}, and one short exam-action label on each branch."
    )


def concept_entry_from_callback_response(
    job: dict[str, Any],
    response: str,
    *,
    external_route_available: bool | None = None,
) -> dict[str, object] | None:
    """Parse a host-LLM response for one concept job into the canonical shape."""

    topic_title = str(job.get("topic_title") or "")
    if not topic_title or not response.strip():
        return None
    try:
        data = json.loads(strip_json_fence(response))
    except json.JSONDecodeError:
        data = {"explanations": split_plain_response(response)}
    if not isinstance(data, dict):
        return None
    data.setdefault("topic_title", topic_title)
    data.setdefault("concept_term", job.get("student_title") or job.get("topic_title") or "")
    explanations = normalized_explanation_values(data.get("explanations"))
    if not explanations and isinstance(data.get("explanation"), str):
        explanations = [str(data["explanation"]).strip()]
        for key in ["example", "mini_worked_example", "common_misconception", "pitfall", "analogy"]:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                explanations.append(value.strip())
    if not explanations:
        explanations = split_plain_response(response)
    if len(explanations) < 2:
        return None
    if "example" in data and "mini_worked_example" not in data:
        data["mini_worked_example"] = data["example"]
    if "common_misconception" in data and "pitfall" not in data:
        data["pitfall"] = data["common_misconception"]
    data["explanations"] = explanations[:4]
    if "visual_decision" not in data:
        data["visual_decision"] = fallback_visual_decision(
            "The Writer did not request a separate visual for this topic."
        )
    entry = {str(key): value for key, value in data.items()}
    validate_visual_decision_entry(
        entry,
        allow_fallback=True,
        external_route_available=external_route_available,
    )
    return entry


def strip_json_fence(value: str) -> str:
    text = value.strip()
    if text.startswith("```json"):
        return text.split("```json", 1)[1].split("```", 1)[0].strip()
    if text.startswith("```"):
        return text.split("```", 1)[1].split("```", 1)[0].strip()
    return text


def split_plain_response(value: str) -> list[str]:
    lines = [line.strip(" -\t") for line in value.splitlines() if line.strip(" -\t")]
    if len(lines) >= 2:
        return lines
    sentences = [part.strip() for part in value.replace(";", ".").split(".") if part.strip()]
    return [f"{sentence}." for sentence in sentences[:4]]
