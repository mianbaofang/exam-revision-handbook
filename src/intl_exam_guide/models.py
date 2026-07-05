from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceSnippet:
    page: int
    text: str
    matched_term: str


@dataclass
class Topic:
    title: str
    points: list[str] = field(default_factory=list)
    level_tags: list[str] = field(default_factory=list)
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class AssessmentPaper:
    title: str
    details: list[str] = field(default_factory=list)
    source_snippets: list[SourceSnippet] = field(default_factory=list)
    # Multi-provider fields (Phase 2): component/unit code, duration, marks, weighting, route.
    code: str | None = None
    duration: str | None = None
    marks: str | None = None
    weighting: str | None = None
    route_tags: list[str] = field(default_factory=list)


@dataclass
class SourceRecord:
    provider: str
    page_url: str
    specification_url: str | None = None
    listing_subject: str | None = None
    listing_qualification_type: str | None = None
    listing_group_label: str | None = None
    listing_style_class: str | None = None
    specification_sha256: str | None = None
    specification_path: str | None = None
    extracted_text_path: str | None = None
    downloaded_at: str | None = None
    # Multi-provider fields (Phase 2): version, teaching dates, syllabus year range.
    qualification_family: str | None = None
    issue_version: str | None = None
    first_teaching: str | None = None
    first_assessment: str | None = None
    syllabus_year_range: str | None = None
    selected_exam_year: str | None = None


@dataclass
class Qualification:
    title: str
    code: str | None
    qualification_type: str
    subject_area: str | None
    page_url: str
    summary: list[str]
    topics: list[Topic]
    assessments: list[AssessmentPaper]
    source: SourceRecord
    audience_note: str
    # Multi-provider fields (Phase 2).
    provider: str | None = None
    qualification_family: str | None = None
    selected_exam_year: str | None = None
    route_tags: list[str] = field(default_factory=list)
    command_words: list[str] = field(default_factory=list)
    assessment_objectives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Qualification":
        source = SourceRecord(**data["source"])
        topics = [
            Topic(
                title=topic["title"],
                points=topic.get("points", []),
                level_tags=topic.get("level_tags", []),
                source_snippets=[
                    SourceSnippet(**snippet) for snippet in topic.get("source_snippets", [])
                ],
            )
            for topic in data.get("topics", [])
        ]
        assessments = [
            AssessmentPaper(
                title=paper["title"],
                details=paper.get("details", []),
                source_snippets=[
                    SourceSnippet(**snippet) for snippet in paper.get("source_snippets", [])
                ],
                code=paper.get("code"),
                duration=paper.get("duration"),
                marks=paper.get("marks"),
                weighting=paper.get("weighting"),
                route_tags=paper.get("route_tags", []),
            )
            for paper in data.get("assessments", [])
        ]
        return cls(
            title=data["title"],
            code=data.get("code"),
            qualification_type=data["qualification_type"],
            subject_area=data.get("subject_area"),
            page_url=data["page_url"],
            summary=data.get("summary", []),
            topics=topics,
            assessments=assessments,
            source=source,
            audience_note=data["audience_note"],
            provider=data.get("provider"),
            qualification_family=data.get("qualification_family"),
            selected_exam_year=data.get("selected_exam_year"),
            route_tags=data.get("route_tags", []),
            command_words=data.get("command_words", []),
            assessment_objectives=data.get("assessment_objectives", []),
        )


@dataclass
class GuideRunOptions:
    requested_subject: str
    image_provider: str
    explanation_style: str
    output_language: str
    exam_year: str | None = None
    image_model: str | None = None
    image_endpoint_url: str | None = None
    image_api_key_env: str | None = None


@dataclass
class PracticeItem:
    topic_title: str
    command_word: str
    difficulty: str
    focus_point: str
    question: str
    answer_frame: list[str]
    public_solution_steps: list[str]
    answer_checkpoints: list[str]
    source_points: list[str]
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class TopicGuide:
    topic_title: str
    essence: str
    analogy: str
    mini_worked_example: str
    worked_solution_steps: list[str]
    pitfall: str
    checklist: list[str]
    diagram_brief: str
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class VisualBrief:
    topic_title: str
    focus_point: str
    trigger: str
    visual_type: str
    complexity: str
    image_provider: str
    prompt: str
    source_points: list[str]
    source_snippets: list[SourceSnippet] = field(default_factory=list)
    llm_visual_spec: bool = False
    svg_fit: str = ""


@dataclass
class GuidePlan:
    qualification: Qualification
    run_options: GuideRunOptions
    topic_guides: list[TopicGuide]
    practice_items: list[PracticeItem]
    visual_briefs: list[VisualBrief]
    diagram_briefs: list[str]
    revision_stages: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuidePlan":
        def snippets(items: list[dict[str, Any]] | None) -> list[SourceSnippet]:
            return [SourceSnippet(**item) for item in items or []]

        return cls(
            qualification=Qualification.from_dict(data["qualification"]),
            run_options=GuideRunOptions(**data["run_options"]),
            topic_guides=[
                TopicGuide(
                    topic_title=item["topic_title"],
                    essence=item["essence"],
                    analogy=item["analogy"],
                    mini_worked_example=item["mini_worked_example"],
                    worked_solution_steps=item.get("worked_solution_steps", []),
                    pitfall=item["pitfall"],
                    checklist=item.get("checklist", []),
                    diagram_brief=item["diagram_brief"],
                    source_snippets=snippets(item.get("source_snippets")),
                )
                for item in data.get("topic_guides", [])
            ],
            practice_items=[
                PracticeItem(
                    topic_title=item["topic_title"],
                    command_word=item["command_word"],
                    difficulty=item["difficulty"],
                    focus_point=item["focus_point"],
                    question=item["question"],
                    answer_frame=item.get("answer_frame", []),
                    public_solution_steps=item.get("public_solution_steps", []),
                    answer_checkpoints=item.get("answer_checkpoints", []),
                    source_points=item.get("source_points", []),
                    source_snippets=snippets(item.get("source_snippets")),
                )
                for item in data.get("practice_items", [])
            ],
            visual_briefs=[
                VisualBrief(
                    topic_title=item["topic_title"],
                    focus_point=item["focus_point"],
                    trigger=item["trigger"],
                    visual_type=item["visual_type"],
                    complexity=item["complexity"],
                    image_provider=item["image_provider"],
                    prompt=item["prompt"],
                    source_points=item.get("source_points", []),
                    source_snippets=snippets(item.get("source_snippets")),
                    llm_visual_spec=bool(item.get("llm_visual_spec", False)),
                    svg_fit=str(item.get("svg_fit", "") or ""),
                )
                for item in data.get("visual_briefs", [])
            ],
            diagram_briefs=data.get("diagram_briefs", []),
            revision_stages=data.get("revision_stages", []),
        )
