"""Tests for the canonical concept-writing integration boundary."""

from __future__ import annotations

import json

import pytest

from intl_exam_guide.llm.provider import ConceptExplanation, ConceptJob
from intl_exam_guide.models import Qualification, SourceRecord, Topic
from intl_exam_guide.planning.concept_integration import (
    VisualDecisionContractError,
    apply_concept_entries,
    apply_concept_explanations,
    collect_concept_jobs,
    concept_entries_from_explanations,
)
from intl_exam_guide.planning.guide_plan import build_guide_plan
from intl_exam_guide.planning.identifiers import stable_requirement_id
from intl_exam_guide.rendering.output_names import default_handbook_stem
from intl_exam_guide.skill_interface import SkillHandbookGenerator


@pytest.fixture
def sample_topics():
    return [
        Topic(
            title="Newton's Laws of Motion",
            points=[
                "Newton's first law (inertia)",
                "Newton's second law (F=ma)",
                "Newton's third law (action-reaction)",
            ],
        ),
        Topic(
            title="Energy and Work",
            points=[
                "Work done by a force",
                "Kinetic energy",
                "Potential energy",
            ],
        ),
    ]


@pytest.fixture
def sample_qualification(sample_topics):
    return Qualification(
        title="IGCSE Physics",
        code="0625",
        qualification_type="international_gcse",
        subject_area="Physics",
        page_url="https://example.com/physics",
        summary=["Test physics course"],
        topics=sample_topics,
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.com/physics",
            specification_url="https://example.com/physics.pdf",
        ),
        audience_note="For IGCSE students",
    )


@pytest.fixture
def generated_explanations():
    return [
        ConceptExplanation(
            concept_term="Newton's first law (inertia)",
            explanation="Newton's first law says motion only changes when a resultant external force acts.",
            analogy="A puck on smooth ice keeps moving until friction or a wall changes its motion.",
            example="A book on a table stays still until a push supplies an external force.",
            common_misconception="Students often say objects stop naturally, instead of naming friction as a force.",
            status="generated",
            metadata={"model": "mock"},
        ),
        ConceptExplanation(
            concept_term="Work done by a force",
            explanation="Work done is energy transferred when a force moves an object through a distance.",
            analogy="Pushing a trolley farther with the same force transfers more energy.",
            example="Lifting a weight transfers energy against gravity.",
            common_misconception="Holding a heavy object still is effort, but no mechanical work is done without movement.",
            status="generated",
            metadata={"model": "mock"},
        ),
    ]


class TestCollectConceptJobs:
    def test_collect_concept_jobs_basic(self, sample_topics):
        jobs = collect_concept_jobs(sample_topics, "Physics", "international_gcse")

        assert len(jobs) == 2
        assert all(isinstance(job, ConceptJob) for job in jobs)
        assert jobs[0].subject == "Physics"
        assert jobs[0].level == "IGCSE"
        assert jobs[0].topic_title == "Newton's Laws of Motion"
        assert jobs[0].concept_term == "Newton's first law (inertia)"
        assert jobs[0].topic_id == stable_requirement_id(sample_topics[0])
        assert jobs == collect_concept_jobs(sample_topics, "Physics", "international_gcse")

    def test_collect_concept_jobs_a_level(self, sample_topics):
        jobs = collect_concept_jobs(sample_topics, "Physics", "international_as_a_level")

        assert len(jobs) == 2
        assert all(job.level == "A-Level" for job in jobs)

    def test_collect_concept_jobs_no_points(self):
        topics = [Topic(title="Empty Topic", points=[])]
        jobs = collect_concept_jobs(topics, "Physics", "international_gcse")

        assert len(jobs) == 1
        assert jobs[0].concept_term == "Empty Topic"


class TestApplyProviderExplanations:
    def test_apply_concept_explanations_keeps_provider_compatibility(
        self,
        sample_qualification,
        generated_explanations,
    ):
        plan = build_guide_plan(
            sample_qualification,
            questions_per_topic=1,
            explanation_style="friendly",
            output_language="en",
        )

        updated_guides = apply_concept_explanations(plan.topic_guides, generated_explanations)

        assert "Newton's first law" in updated_guides[0].essence
        assert "puck" in updated_guides[0].analogy
        assert "Lifting a weight" in updated_guides[1].mini_worked_example

    def test_failed_explanations_are_not_applied(self, sample_qualification):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        original_essence = plan.topic_guides[0].essence

        updated = apply_concept_explanations(
            plan.topic_guides,
            [
                ConceptExplanation(
                    concept_term="Newton's first law (inertia)",
                    explanation="Should not apply",
                    status="failed",
                )
            ],
        )

        assert updated[0].essence == original_essence

    def test_apply_concept_explanations_does_not_use_substring_matching(
        self, sample_qualification
    ):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        original = plan.topic_guides[0].analogy

        updated = apply_concept_explanations(
            plan.topic_guides,
            [
                ConceptExplanation(
                    concept_term="Newton's first law",
                    explanation="A near match must not be guessed onto a topic.",
                    analogy="This must not be imported.",
                    status="generated",
                )
            ],
        )

        assert updated[0].analogy == original


class TestCanonicalConceptEntries:
    def test_provider_results_convert_to_importable_entries(
        self,
        sample_qualification,
        generated_explanations,
    ):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        jobs = collect_concept_jobs(
            plan.qualification.topics,
            plan.qualification.subject_area or "General",
            plan.qualification.qualification_type,
        )

        entries = concept_entries_from_explanations(jobs, generated_explanations)
        imported, missing = apply_concept_entries(plan, entries)

        assert imported == 2
        assert missing == []
        assert entries[0]["topic_title"] == "Newton's Laws of Motion"
        assert entries[0]["visual_decision"]["recommended_route"] == "text-ok"
        assert entries[0]["visual_decision"]["source"] == "python-draft-fallback"
        assert entries[0]["provenance"] == "python-fallback"
        assert entries[0]["delivery_eligible"] is False
        assert "no_visual_reason" in entries[0]["visual_decision"]
        assert len(entries[0]["explanations"]) >= 2
        assert "resultant external force" in plan.topic_guides[0].checklist[0]
        assert plan.practice_items[0].question == generated_explanations[0].example
        assert plan.practice_items[0].public_solution_steps

    def test_apply_concept_entries_imports_writer_visual_spec(self, sample_qualification):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        topic_title = plan.topic_guides[0].topic_title

        imported, missing = apply_concept_entries(
            plan,
            [
                {
                    "topic_title": topic_title,
                    "concept_term": "Newton's Laws of Motion",
                    "explanations": [
                        "Newton's laws describe how resultant force changes motion.",
                        "They matter because force questions first require a correct motion model.",
                    ],
                    "visual_decision": {
                        "recommended_route": "exact-svg",
                        "learning_claim": "Force-arrow geometry carries this relationship more clearly than text alone.",
                        "visual_teaching_value": "Students can see the resultant direction and label positions."
                    },
                    "visual_spec": {
                        "type": "force arrows on a particle",
                        "complexity": "svg-basic",
                        "svg_fit": "exact",
                        "focus_point": "resultant force direction",
                        "trigger": "force arrows exactly express the vector relationship",
                        "prompt": "Create a clean force-arrow diagram for one particle with labelled resultant force.",
                    },
                }
            ],
        )

        assert imported == 1
        assert missing == []
        assert len(plan.visual_briefs) == 1
        visual = plan.visual_briefs[0]
        assert visual.topic_title == topic_title
        assert visual.complexity == "svg-basic"
        assert visual.image_provider == "llm-svg"
        assert visual.llm_visual_spec is True
        assert visual.svg_fit == "exact"

    def test_apply_concept_entries_preserves_kroki_visual_route(self, sample_qualification):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        topic_title = plan.topic_guides[0].topic_title

        imported, missing = apply_concept_entries(
            plan,
            [
                {
                    "topic_title": topic_title,
                    "concept_term": "Newton's Laws of Motion",
                    "explanations": [
                        "Newton's laws describe how resultant force changes motion.",
                        "They matter because force questions first require a correct motion model.",
                    ],
                    "visual_decision": {
                        "recommended_route": "kroki-diagram",
                        "learning_claim": "A formal force relation diagram clarifies the model.",
                        "visual_teaching_value": "Students can read the relation as a structured diagram.",
                    },
                    "visual_spec": {
                        "type": "force relationship graph",
                        "focus_point": "resultant force direction",
                        "trigger": "Kroki can express the formal relationship exactly.",
                        "prompt": "Create a Kroki diagram showing resultant force and acceleration direction.",
                    },
                }
            ],
        )

        assert imported == 1
        assert missing == []
        assert len(plan.visual_briefs) == 1
        visual = plan.visual_briefs[0]
        assert visual.complexity == "svg-basic"
        assert visual.image_provider == "kroki"

    def test_apply_concept_entries_rejects_unknown_visual_route(self, sample_qualification):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        topic_title = plan.topic_guides[0].topic_title

        with pytest.raises(VisualDecisionContractError, match="recommended_route"):
            apply_concept_entries(
                plan,
                [
                    {
                        "topic_title": topic_title,
                        "explanations": ["One useful explanation.", "A second useful explanation."],
                        "visual_decision": {"recommended_route": "auto-diagram"},
                    }
                ],
            )

    def test_apply_concept_entries_rejects_text_ok_with_visual_spec(self, sample_qualification):
        plan = build_guide_plan(sample_qualification, questions_per_topic=1)
        topic_title = plan.topic_guides[0].topic_title

        with pytest.raises(VisualDecisionContractError, match="must not include visual_spec"):
            apply_concept_entries(
                plan,
                [
                    {
                        "topic_title": topic_title,
                        "explanations": ["One useful explanation.", "A second useful explanation."],
                        "visual_decision": {
                            "recommended_route": "text-ok",
                            "no_visual_reason": "The worked example already carries the learning clearly.",
                        },
                        "visual_spec": {
                            "type": "diagram",
                            "prompt": "Draw a diagram that contradicts text-ok.",
                        },
                    }
                ],
            )

    def test_build_guide_plan_stays_planning_only(self, sample_qualification):
        with pytest.raises(TypeError):
            build_guide_plan(sample_qualification, llm_provider=object())  # type: ignore[arg-type]


class TestSkillHostConceptFlow:
    @pytest.mark.anyio
    async def test_skill_generator_writes_concept_artifacts(self, sample_qualification, tmp_path):
        async def callback(prompt: str) -> str:
            assert "Return JSON only" in prompt
            return json.dumps(
                {
                    "essence": "The concept names the physics relationship in the source point.",
                    "analogy": "Treat it like a rule card for the situation.",
                    "mini_worked_example": "A student identifies the force or energy transfer before calculating.",
                    "pitfall": "Do not answer with a memorised keyword only.",
                    "explanations": [
                        "The concept describes the exact physics relationship named in the source point.",
                        "It matters because the question first checks whether the student identifies that relationship.",
                    ],
                }
            )

        generator = SkillHandbookGenerator(callback)
        html_path = await generator.generate(sample_qualification, tmp_path, skip_pdf=True)

        concepts_path = tmp_path / "concepts" / "concept_explanations.json"
        validation_path = tmp_path / "validation.json"
        plan_path = tmp_path / "guide-plan.json"

        assert html_path.parent == tmp_path
        assert html_path.suffix == ".html"
        assert html_path.stem.startswith(default_handbook_stem(sample_qualification).rsplit("-", 2)[0])
        assert concepts_path.exists()
        assert validation_path.exists()
        assert plan_path.exists()
        entries = json.loads(concepts_path.read_text(encoding="utf-8"))
        assert len(entries) == 2
        assert entries[0]["topic_title"] == "Newton's Laws of Motion"
        assert entries[0]["visual_decision"]["recommended_route"] == "text-ok"
        assert entries[0]["visual_decision"]["source"] == "python-draft-fallback"
        assert "no_visual_reason" in entries[0]["visual_decision"]
