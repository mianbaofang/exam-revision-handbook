from __future__ import annotations

import os
import re

from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.planning.localization import (
    is_generic_zh_label,
    zh_point_label,
    zh_point_labels,
    zh_visual_trigger,
    zh_visual_type,
)
from intl_exam_guide.planning.source_points import visible_source_points
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile


SUBJECT_PROMPT_LABELS = {
    "accounting": ("accounting", "会计"),
    "biology": ("biology", "生物"),
    "business": ("business", "商业"),
    "chemistry": ("chemistry", "化学"),
    "economics": ("economics and business", "经济与商业"),
    "generic": ("this subject", "本学科"),
    "history": ("history", "历史"),
    "mathematics": ("mathematics", "数学"),
    "physics": ("physics", "物理"),
}

COURSE_PACKAGING_PATTERNS = [
    r"\b(?:Oxford\s*)?AQA\b",
    r"\bOxfordAQA\b",
    r"\bPearson\b",
    r"\bEdexcel\b",
    r"\bCambridge\b",
    r"\bCAIE\b",
    r"\bInternational\s+(?:GCSE|AS(?:[-\s]A[-\s]level|[-\s]A-level|\s+Level)?|A[-\s]level)\b",
    r"\bIGCSE\b",
    r"\bGCSE\b",
    r"\bAS[-\s]A[-\s]level\b",
    r"\bAS[-\s]A-level\b",
    r"\bAS\s+Level\b",
    r"\bA[-\s]level\b",
    r"\bA\s+Level\b",
    r"\bAS\s+unit\s+[A-Z]?\d+\b",
    r"\bcourse\s+code\s*[·:,-]?\s*\d+\b",
    r"\bcode\s*[·:,-]?\s*\d+\b",
    r"课程代码\s*[·:：,-]?\s*\d+",
    r"国际课程",
    r"官方英文来源",
    r"AS\s*[A-Z]?\d+",
]


def build_visual_brief(
    topic: Topic,
    guide: TopicGuide,
    run_options: GuideRunOptions,
    subject_area: str | None = None,
) -> VisualBrief | None:
    llm_visual_required = bool(getattr(run_options, "llm_visual_spec_required", False))
    if llm_visual_required and not getattr(run_options, "llm_visual_spec_provided", False):
        return None
    if not llm_visual_required and os.environ.get("INTL_EXAM_GUIDE_REQUIRE_LLM_VISUAL_SPEC") == "1":
        return None
    points = visible_source_points(topic, limit=4)
    focus = points[0]
    visual_type, complexity, trigger = choose_visual_type(topic, points, subject_area)
    if complexity == "text-ok":
        return None
    provider = choose_provider_for_visual(complexity, run_options, visual_type)
    body_language = handbook_body_language(run_options.output_language)
    if body_language == "en":
        visible_focus = focus
        visible_points = points
        visible_visual_type = visual_type
        visible_trigger = trigger
    else:
        visible_focus = zh_point_label(focus)
        visible_points = [
            label for label in zh_point_labels(points) if not is_generic_zh_label(label)
        ]
        if not visible_points:
            visible_points = ["本节核心概念"]
        if is_generic_zh_label(visible_focus):
            visible_focus = visible_points[0]
        visible_visual_type = zh_visual_type(visual_type)
        visible_trigger = zh_visual_trigger(trigger)
    prompt = build_content_only_image_prompt(
        topic=topic,
        points=points,
        subject_area=subject_area,
        language=body_language,
        focus=visible_focus,
        visual_type=visible_visual_type,
        visible_points=visible_points,
    )
    return VisualBrief(
        topic_title=topic.title,
        focus_point=visible_focus,
        trigger=visible_trigger,
        visual_type=visible_visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def build_content_only_image_prompt(
    *,
    topic: Topic,
    points: list[str],
    subject_area: str | None,
    language: str,
    focus: str,
    visual_type: str,
    visible_points: list[str],
) -> str:
    """Build the prompt submitted to image models without board/source packaging."""

    language = handbook_body_language(language)
    subject = subject_prompt_label(subject_area, topic, points, language)
    clean_focus = clean_prompt_phrase(focus)
    clean_type = clean_prompt_phrase(visual_type)
    label_clause = prompt_label_clause(visible_points, language)
    return (
        "Create a polished educational worksheet infographic for a revision guide. "
        f"Topic: {subject}: {clean_focus}. "
        f"Visual task: {clean_type}. "
        "Use a clean landscape layout with a large topic banner, clear teaching panels, "
        "pastel subject colors, readable black labels, accurate diagrams or icons, "
        "and a small Quick Q&A or practice box. "
        "Show only the diagrams, formulas, and short labels needed for this topic. "
        "Do not add institutional logos, course-cover headers, badges, footers, "
        f"or watermarks.{label_clause}"
    )


def subject_prompt_label(
    subject_area: str | None,
    topic: Topic,
    points: list[str],
    language: str,
) -> str:
    profile = resolve_subject_profile(subject_area, topic, f"{topic.title} {' '.join(points)}")
    index = 1 if language != "en" else 0
    return SUBJECT_PROMPT_LABELS[profile.example_domain][index]


def prompt_label_clause(visible_points: list[str], language: str) -> str:
    labels = [clean_prompt_phrase(label) for label in visible_points[:3]]
    labels = [label for label in labels if label and not is_generic_zh_label(label)]
    if not labels:
        return ""
    if language == "en":
        return f" Short labels may include: {', '.join(labels)}."
    return f"可用短标签：{'、'.join(labels)}。"


def clean_prompt_phrase(text: str) -> str:
    phrase = " ".join(text.split())
    phrase = re.sub(
        r"^(?:students|candidates|learners)\s+(?:should|must|are expected to)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    phrase = re.sub(
        r"^(?:be able to|understand|describe|explain|apply)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    for pattern in COURSE_PACKAGING_PATTERNS:
        phrase = re.sub(pattern, "", phrase, flags=re.IGNORECASE)
    phrase = re.sub(r"\s{2,}", " ", phrase).strip(" -:：,，;；")
    return phrase or "core concept visual"


def choose_visual_type(
    topic: Topic,
    points: list[str],
    subject_area: str | None = None,
) -> tuple[str, str, str]:
    """
    DEPRECATED: Python no longer uses keyword triggers to decide visual types.

    The LLM Writer must judge visual needs case-by-case in Phase 2 (concept writing).
    This function now returns a generic placeholder.

    For legacy compatibility (tests), returns text-ok to suppress automatic visual generation.
    """
    return (
        "generic visual placeholder",
        "text-ok",  # Suppresses automatic visual generation
        "LLM Writer must judge visual needs in Phase 2",
    )


def is_scope_exclusion_text(text: str) -> bool:
    text = text.rsplit(":", 1)[-1]
    exclusion_phrases = [
        "will not be set",
        "will not be assessed",
        "is not required",
        "are not required",
        "not required",
        "not be required",
        "not expected",
        "outside the scope",
    ]
    if not any(phrase in text for phrase in exclusion_phrases):
        return False
    learning_terms = [
        "restricted to",
        "include",
        "includes",
        "including",
        "to include",
        "use of",
        "application of",
        "applications of",
    ]
    return not any(term in text for term in learning_terms)


def choose_provider_for_visual(
    complexity: str,
    run_options: GuideRunOptions,
    visual_type: str = "",
) -> str:
    if complexity == "svg-basic":
        return "kroki"
    if run_options.image_provider == "prompt-queue":
        return "external-generation-required"
    if run_options.image_provider == "custom":
        return f"custom:{run_options.image_model or 'model-not-set'}"
    return run_options.image_provider


def is_professional_diagram_visual(visual_type: str) -> bool:
    text = visual_type.lower()
    if any(
        term in text
        for term in [
            "axis",
            "curve",
            "graph",
            "number line",
            "venn",
            "triangle",
            "geometry",
            "ph",
            "particle",
            "rate",
            "energy",
            "motion",
            "force",
            "collision",
            "probability",
            "statistics",
            "chart",
            "table",
            "circle",
            "trigonometry",
            "calculus",
            "function",
        ]
    ):
        return False
    return any(
        term in text
        for term in [
            "flow",
            "workflow",
            "hierarchy",
            "chain",
            "map",
            "timeline",
            "comparison",
            "source evidence",
            "checkpoint",
            "reconciliation",
            "organisation structure",
            "stakeholder",
            "ownership",
            "segmentation",
        ]
    )
