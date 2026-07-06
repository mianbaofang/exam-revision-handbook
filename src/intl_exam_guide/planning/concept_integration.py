"""LLM concept integration helpers for guide planning."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from intl_exam_guide.llm.provider import ConceptExplanation, ConceptJob
from intl_exam_guide.models import GuidePlan, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.source_points import visible_source_points


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
                topic_id=f"topic_{hash(topic.title) % 10000:04d}",
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
        exp.concept_term: exp for exp in explanations if exp.status == "generated"
    }

    updated_guides: list[TopicGuide] = []

    for guide in topic_guides:
        matching_explanation = None
        if guide.topic_title in explanation_map:
            matching_explanation = explanation_map[guide.topic_title]
        else:
            for concept_term, explanation in explanation_map.items():
                if (
                    concept_term.lower() in guide.topic_title.lower()
                    or guide.topic_title.lower() in concept_term.lower()
                ):
                    matching_explanation = explanation
                    break
                if concept_term.lower() in guide.essence.lower():
                    matching_explanation = explanation
                    break
                for checklist_item in guide.checklist:
                    if concept_term.lower() in checklist_item.lower():
                        matching_explanation = explanation
                        break
                if matching_explanation:
                    break

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
) -> list[dict[str, object]]:
    """Convert provider results into the canonical concept_explanations.json shape."""

    entries: list[dict[str, object]] = []
    for job, explanation in zip(jobs, explanations, strict=False):
        entry = concept_entry_from_explanation(job, explanation)
        if entry:
            entries.append(entry)
    return entries


def concept_entry_from_explanation(
    job: ConceptJob,
    explanation: ConceptExplanation,
) -> dict[str, object] | None:
    if explanation.status != "generated" or not explanation.explanation.strip():
        return None

    bullets = explanation_bullets(explanation)
    if len(bullets) < 2:
        return None

    entry: dict[str, object] = {
        "topic_title": job.topic_title,
        "concept_term": job.concept_term,
        "explanations": bullets[:4],
        "essence": explanation.explanation.strip(),
    }
    if explanation.analogy:
        entry["analogy"] = explanation.analogy.strip()
    if explanation.example:
        entry["mini_worked_example"] = explanation.example.strip()
    if explanation.common_misconception:
        entry["pitfall"] = explanation.common_misconception.strip()
    if explanation.metadata:
        entry["writer_metadata"] = dict(explanation.metadata)
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
    imported = 0
    missing: list[str] = []
    for entry in entries:
        topic_title = str(entry.get("topic_title") or "")
        values = normalized_explanation_values(entry.get("explanations"))
        if not topic_title or len(values) < 2:
            continue
        guide = guides.get(topic_title)
        if not guide:
            missing.append(topic_title)
            continue
        mastery_summary = str(entry.get("mastery_summary") or "").strip()
        if mastery_summary:
            guide.mastery_summary = mastery_summary
        if force or values:
            guide.checklist = values[:4]
        apply_optional_text(entry, guide, "essence")
        apply_optional_text(entry, guide, "analogy")
        apply_optional_text(entry, guide, "mini_worked_example")
        apply_optional_text(entry, guide, "pitfall")
        guide.diagram_brief = build_clean_diagram_brief(topic_title, values)
        steps = entry.get("worked_solution_steps")
        if isinstance(steps, list):
            clean_steps = [str(value).strip() for value in steps if str(value).strip()]
            if clean_steps:
                guide.worked_solution_steps = clean_steps[:5]
        visual = visual_brief_from_entry(plan, topic_title, entry)
        if visual:
            upsert_visual_brief(plan, visual)
        imported += 1
    return imported, missing


def visual_brief_from_entry(
    plan: GuidePlan,
    topic_title: str,
    entry: dict[str, object],
) -> VisualBrief | None:
    visual_spec = entry.get("visual_spec")
    if not isinstance(visual_spec, dict):
        return None
    prompt = str(visual_spec.get("prompt") or "").strip()
    visual_type = str(visual_spec.get("visual_type") or visual_spec.get("type") or "").strip()
    complexity = str(visual_spec.get("complexity") or "infographic").strip()
    if not prompt or not visual_type:
        return None
    if complexity not in {"svg-basic", "infographic"}:
        complexity = "infographic"

    topic = next((item for item in plan.qualification.topics if item.title == topic_title), None)
    source_points = visual_source_points(topic, entry)
    provider = provider_for_visual_spec(plan, complexity)
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


def provider_for_visual_spec(plan: GuidePlan, complexity: str) -> str:
    if complexity == "svg-basic":
        return "llm-svg"
    if plan.run_options.image_provider == "custom":
        model = plan.run_options.image_model or "model-not-set"
        return f"custom:{model}"
    return "prompt-queue"


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
    return {str(key): value for key, value in data.items()}


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
