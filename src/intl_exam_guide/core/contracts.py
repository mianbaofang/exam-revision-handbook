from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class DeliveryState(StrEnum):
    """Mechanical package state for a generated handbook package."""

    UNSUPPORTED = "unsupported"
    BLOCKED = "blocked"
    DRAFT = "draft"
    NEEDS_REVIEW = "needs-review"

    @classmethod
    def from_delivery_status(cls, status: str | None) -> "DeliveryState":
        if status == "ready":
            return cls.NEEDS_REVIEW
        if status in {"draft_needs_concept_review", "draft_needs_image_review"}:
            return cls.DRAFT
        if status == "blocked_errors":
            return cls.BLOCKED
        return cls.UNSUPPORTED


@dataclass(frozen=True)
class SourceAnchor:
    page: int | None
    matched_term: str
    text: str = ""

    @classmethod
    def from_snippet(cls, snippet: object) -> "SourceAnchor":
        return cls(
            page=getattr(snippet, "page", None),
            matched_term=str(getattr(snippet, "matched_term", "") or ""),
            text=str(getattr(snippet, "text", "") or ""),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CourseSpec:
    """Normalized source-of-truth course contract derived from provider output."""

    provider: str
    title: str
    code: str | None
    qualification_type: str
    subject_area: str | None
    page_url: str
    specification_url: str | None
    specification_sha256: str | None
    selected_exam_year: str | None
    syllabus_year_range: str | None
    topic_count: int
    assessment_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LearningUnit:
    """Smallest teachable unit after source filtering or an LLM Analyst outline."""

    id: str
    title: str
    source_topic_title: str
    source_points: list[str]
    source_anchors: list[SourceAnchor] = field(default_factory=list)
    subject_area: str | None = None
    level_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["source_anchors"] = [anchor.to_dict() for anchor in self.source_anchors]
        return payload


@dataclass(frozen=True)
class PedagogicalUnit:
    """Student-facing production contract for one learning unit."""

    learning_unit_id: str
    topic_title: str
    writing_job_id: str
    review_job_id: str
    concept_explanations: list[str] = field(default_factory=list)
    practice_count: int = 0
    visual_spec_ids: list[str] = field(default_factory=list)
    delivery_state: DeliveryState = DeliveryState.DRAFT

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["delivery_state"] = self.delivery_state.value
        return payload


def course_spec_from_qualification(qualification: object) -> CourseSpec:
    source = getattr(qualification, "source")
    return CourseSpec(
        provider=str(getattr(qualification, "provider", None) or getattr(source, "provider", "")),
        title=str(getattr(qualification, "title", "")),
        code=getattr(qualification, "code", None),
        qualification_type=str(getattr(qualification, "qualification_type", "")),
        subject_area=getattr(qualification, "subject_area", None),
        page_url=str(getattr(qualification, "page_url", "") or getattr(source, "page_url", "")),
        specification_url=getattr(source, "specification_url", None),
        specification_sha256=getattr(source, "specification_sha256", None),
        selected_exam_year=(
            getattr(qualification, "selected_exam_year", None)
            or getattr(source, "selected_exam_year", None)
        ),
        syllabus_year_range=getattr(source, "syllabus_year_range", None),
        topic_count=len(getattr(qualification, "topics", []) or []),
        assessment_count=len(getattr(qualification, "assessments", []) or []),
    )


def learning_units_from_qualification(qualification: object) -> list[LearningUnit]:
    units: list[LearningUnit] = []
    subject_area = getattr(qualification, "subject_area", None)
    for index, topic in enumerate(getattr(qualification, "topics", []) or [], start=1):
        title = str(getattr(topic, "title", ""))
        points = [str(point) for point in (getattr(topic, "points", []) or [])]
        anchors = [
            SourceAnchor.from_snippet(snippet)
            for snippet in (getattr(topic, "source_snippets", []) or [])
        ]
        units.append(
            LearningUnit(
                id=f"unit_{index:03d}",
                title=title,
                source_topic_title=title,
                source_points=points,
                source_anchors=anchors,
                subject_area=subject_area,
                level_tags=[str(tag) for tag in (getattr(topic, "level_tags", []) or [])],
            )
        )
    return units


def pedagogical_units_from_plan(
    plan: object,
    delivery_state: DeliveryState = DeliveryState.DRAFT,
) -> list[PedagogicalUnit]:
    visual_ids_by_topic = _visual_ids_by_topic(plan)
    practice_counts = _practice_counts_by_topic(plan)
    learning_unit_ids = {
        unit.title: unit.id
        for unit in learning_units_from_qualification(getattr(plan, "qualification"))
    }
    units: list[PedagogicalUnit] = []
    for index, guide in enumerate(getattr(plan, "topic_guides", []) or [], start=1):
        topic_title = str(getattr(guide, "topic_title", ""))
        units.append(
            PedagogicalUnit(
                learning_unit_id=learning_unit_ids.get(topic_title, f"unit_{index:03d}"),
                topic_title=topic_title,
                writing_job_id=f"concept_{index:03d}",
                review_job_id=f"concept_review_{index:03d}",
                concept_explanations=[
                    str(item) for item in (getattr(guide, "checklist", []) or [])
                ],
                practice_count=practice_counts.get(topic_title, 0),
                visual_spec_ids=visual_ids_by_topic.get(topic_title, []),
                delivery_state=delivery_state,
            )
        )
    return units


def _practice_counts_by_topic(plan: object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in getattr(plan, "practice_items", []) or []:
        title = str(getattr(item, "topic_title", ""))
        counts[title] = counts.get(title, 0) + 1
    return counts


def _visual_ids_by_topic(plan: object) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for index, brief in enumerate(getattr(plan, "visual_briefs", []) or [], start=1):
        title = str(getattr(brief, "topic_title", ""))
        values.setdefault(title, []).append(f"visual_{index:03d}")
    return values


def lightweight_workflow_payload() -> dict[str, object]:
    return {
        "mode": "llm-owned-lightweight-workflow",
        "roles": [
            {
                "role_id": "analyst",
                "owns": "Read syllabus-evidence.json and write syllabus-outline.json.",
            },
            {
                "role_id": "writer",
                "owns": "Write concept explanations, mastery_summary, and per-topic visual_decision records.",
            },
            {
                "role_id": "reviewer",
                "owns": "Open the rendered handbook and compare it with evidence and outline artifacts.",
            },
        ],
        "python_boundary": [
            "Python renders and validates artifacts mechanically.",
            "Python does not decide syllabus splits, write teaching content, decide visuals, or approve final quality.",
        ],
    }


def course_contract_payload(
    plan: object,
    delivery_status: str | None = None,
    *,
    quality_inspection_complete: bool = False,
    **_: object,
) -> dict[str, Any]:
    """Build a lightweight serializable contract packet while preserving plan data."""

    qualification = getattr(plan, "qualification")
    delivery_state = DeliveryState.from_delivery_status(delivery_status)
    return {
        "schema_version": "v0.5-lightweight-contract",
        "delivery_state": delivery_state.value,
        "workflow": lightweight_workflow_payload(),
        "quality_inspection_complete": quality_inspection_complete,
        "course_spec": course_spec_from_qualification(qualification).to_dict(),
        "learning_units": [
            unit.to_dict() for unit in learning_units_from_qualification(qualification)
        ],
        "pedagogical_units": [
            unit.to_dict() for unit in pedagogical_units_from_plan(plan, delivery_state)
        ],
    }
