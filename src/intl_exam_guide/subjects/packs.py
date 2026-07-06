from __future__ import annotations

from dataclasses import asdict, dataclass

from intl_exam_guide.models import Topic
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile


PRIORITY_SUBJECT_NAMES = {
    "mathematics",
    "physics",
    "chemistry",
    "economics",
    "business",
    "biology",
    "accounting",
}


@dataclass(frozen=True)
class SubjectPack:
    name: str
    example_domain: str
    priority: bool
    concept_focus: tuple[str, ...]
    practice_focus: tuple[str, ...]
    visual_boundary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


PACKS_BY_DOMAIN = {
    "mathematics": SubjectPack(
        name="mathematics",
        example_domain="mathematics",
        priority=True,
        concept_focus=("definition", "symbol relationship", "method boundary"),
        practice_focus=("concrete numeric prompt", "public solution steps", "answer check"),
        visual_boundary="Use exact graphs, axes, geometry, or text-only algebra; do not draw optional diagrams.",
    ),
    "physics": SubjectPack(
        name="physics",
        example_domain="physics",
        priority=True,
        concept_focus=("physical quantity", "cause-effect relationship", "unit or condition"),
        practice_focus=("known values", "formula or law", "unit check"),
        visual_boundary="Use force, motion, wave, circuit, or energy visuals only when central.",
    ),
    "chemistry": SubjectPack(
        name="chemistry",
        example_domain="chemistry",
        priority=True,
        concept_focus=("particle or structure", "reaction/process boundary", "observable evidence"),
        practice_focus=("substance/context", "chemical rule", "conclusion"),
        visual_boundary="Use structures, particles, apparatus, and process diagrams only when the source point needs them.",
    ),
    "economics": SubjectPack(
        name="economics",
        example_domain="economics",
        priority=True,
        concept_focus=("economic agent", "incentive or constraint", "trade-off/result"),
        practice_focus=("scenario", "cause and consequence", "judgement or calculation"),
        visual_boundary="Use curves and flows only for named diagram relationships.",
    ),
    "business": SubjectPack(
        name="business",
        example_domain="business",
        priority=True,
        concept_focus=("business decision", "stakeholder or market effect", "case boundary"),
        practice_focus=("business context", "cause-effect link", "judgement or recommendation"),
        visual_boundary="Use ownership, stakeholder, marketing, operations, organisation, and finance visuals only when they clarify the business decision.",
    ),
    "biology": SubjectPack(
        name="biology",
        example_domain="biology",
        priority=True,
        concept_focus=("structure or process", "function relationship", "condition or limitation"),
        practice_focus=("biological context", "mechanism", "evidence-based conclusion"),
        visual_boundary="Use process and structure visuals only when labels are source-bound.",
    ),
    "accounting": SubjectPack(
        name="accounting",
        example_domain="accounting",
        priority=True,
        concept_focus=("record or statement", "transaction relationship", "control boundary"),
        practice_focus=("source document/data", "ledger or statement step", "reconciliation check"),
        visual_boundary="Use flows, T-accounts, tables, and statement layouts; avoid decorative diagrams.",
    ),
    "generic": SubjectPack(
        name="generic",
        example_domain="generic",
        priority=False,
        concept_focus=("source concept", "relationship or boundary", "why this point matters"),
        practice_focus=("source-bound prompt", "application", "check against source wording"),
        visual_boundary="Use text unless the source explicitly requires a graph, table, or process.",
    ),
}

PRIORITY_SUBJECT_PACKS = {
    name: pack for name, pack in PACKS_BY_DOMAIN.items() if name in PRIORITY_SUBJECT_NAMES
}


def resolve_subject_pack(
    subject_area: str | None,
    topic: Topic | None,
    source_text: str,
) -> SubjectPack:
    safe_topic = topic or Topic(title="", points=[])
    profile = resolve_subject_profile(subject_area, safe_topic, source_text)
    return PACKS_BY_DOMAIN.get(profile.example_domain, PACKS_BY_DOMAIN["generic"])


def build_subject_writing_job(
    *,
    job_id: str,
    topic_title: str,
    student_title: str,
    source_points: list[str],
    output_language: str,
    pack: SubjectPack,
) -> dict[str, object]:
    return {
        "id": job_id,
        "contract_version": "v0.5-visual-decision-pedagogy",
        "subject_pack": pack.name,
        "priority_subject": pack.priority,
        "topic_title": topic_title,
        "student_title": student_title,
        "output_language": output_language,
        "source_points": source_points,
        "required_concept_focus": list(pack.concept_focus),
        "required_practice_focus": list(pack.practice_focus),
        "visual_boundary": pack.visual_boundary,
        "must_answer": [
            "what the concept is",
            "what relationship or boundary it describes",
            "why it is central to this syllabus point",
        ],
        "must_not": [
            "copy long official text",
            "write a procedural mastery checklist as the concept explanation",
            "borrow another subject's template",
            "import adjacent topics not present in source_points",
        ],
    }


def build_subject_review_job(
    *,
    writing_job_id: str,
    topic_title: str,
    output_language: str,
    pack: SubjectPack,
) -> dict[str, object]:
    return {
        "id": f"{writing_job_id}_review",
        "contract_version": "v0.5-visual-decision-review",
        "subject_pack": pack.name,
        "topic_title": topic_title,
        "output_language": output_language,
        "questions": [
            "Does the explanation stay inside the current topic_title and source_points?",
            "Does it explain concept, relationship or boundary, and syllabus importance?",
            "Does it avoid checklist-only wording and cross-subject examples?",
            "Is it specific enough that a different topic could not reuse the same text?",
        ],
        "verdicts": ["pass", "revise", "blocked"],
    }
