from intl_exam_guide.core import (
    DeliveryState,
    course_contract_payload,
    course_spec_from_qualification,
    learning_units_from_qualification,
    pedagogical_units_from_plan,
)
from intl_exam_guide.models import (
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)


def qualification() -> Qualification:
    return Qualification(
        title="International AS Mathematics (9660)",
        code="9660",
        qualification_type="international_as_a_level",
        subject_area="Mathematics",
        page_url="https://example.test/math",
        summary=["Modular AS qualification."],
        topics=[
            Topic(
                title="P1.1 - Algebra: Surds",
                points=["Use and manipulate surds."],
                level_tags=["P1"],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Use and manipulate surds.",
                        matched_term="P1.1",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(
            provider="oxfordaqa",
            page_url="https://example.test/math",
            specification_url="https://example.test/spec.pdf",
            specification_sha256="abc123",
            selected_exam_year="2027",
            syllabus_year_range="2026-2028",
        ),
        audience_note="International students outside the UK.",
        provider="oxfordaqa",
        selected_exam_year="2027",
    )


def guide_plan() -> GuidePlan:
    topic_title = "P1.1 - Algebra: Surds"
    return GuidePlan(
        qualification=qualification(),
        run_options=GuideRunOptions(
            requested_subject="AQA AS Mathematics",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="zh-CN",
        ),
        topic_guides=[
            TopicGuide(
                topic_title=topic_title,
                essence="Surds are exact square-root forms.",
                analogy="Keep the root exact.",
                mini_worked_example="Simplify sqrt(72).",
                worked_solution_steps=["Read", "Factor", "Simplify", "Check"],
                pitfall="Do not round too early.",
                checklist=["Surds describe exact roots.", "They preserve exact value."],
                diagram_brief="No diagram needed.",
            )
        ],
        practice_items=[
            PracticeItem(
                topic_title=topic_title,
                command_word="calculate",
                difficulty="core",
                focus_point="surds",
                question="Simplify sqrt(72).",
                answer_frame=["Factor 72."],
                public_solution_steps=["72=36x2", "sqrt(72)=6sqrt(2)", "Check exactness", "Answer"],
                answer_checkpoints=["Exact", "Simplified", "No decimal"],
                source_points=["Use and manipulate surds."],
            )
        ],
        visual_briefs=[
            VisualBrief(
                topic_title=topic_title,
                focus_point="surds",
                trigger="symbolic maths is clearer as text",
                visual_type="text explanation with no custom visual",
                complexity="text-ok",
                image_provider="prompt-queue",
                prompt="No image.",
                source_points=["Use and manipulate surds."],
            )
        ],
        diagram_briefs=[],
        revision_stages=[],
    )


def test_course_spec_normalizes_existing_qualification():
    spec = course_spec_from_qualification(qualification())

    assert spec.provider == "oxfordaqa"
    assert spec.code == "9660"
    assert spec.topic_count == 1
    assert spec.specification_sha256 == "abc123"
    assert spec.selected_exam_year == "2027"


def test_learning_units_keep_source_anchors_and_level_tags():
    units = learning_units_from_qualification(qualification())

    assert units[0].id == "unit_001"
    assert units[0].source_points == ["Use and manipulate surds."]
    assert units[0].source_anchors[0].page == 12
    assert units[0].source_anchors[0].matched_term == "P1.1"
    assert units[0].level_tags == ["P1"]


def test_pedagogical_units_link_guides_practice_and_visuals():
    units = pedagogical_units_from_plan(guide_plan())

    assert units[0].writing_job_id == "concept_001"
    assert units[0].review_job_id == "concept_review_001"
    assert units[0].practice_count == 1
    assert units[0].visual_spec_ids == ["visual_001"]
    assert units[0].delivery_state == DeliveryState.DRAFT


def test_course_contract_payload_exposes_delivery_state_without_mutating_plan():
    payload = course_contract_payload(guide_plan(), delivery_status="ready")

    assert payload["schema_version"] == "v0.4-core-mvp"
    assert payload["delivery_state"] == "review-ready"
    orchestration = payload["agent_orchestration"]
    roles = {role["role_id"]: role for role in orchestration["roles"]}
    runtime_contract = orchestration["agent_runtime_contract"]
    assert orchestration["multi_agent_required"] is True
    assert "subagent support must dispatch" in runtime_contract["automatic_dispatch"]
    assert "do not present it as final-ready" in runtime_contract["fallback_without_subagents"]
    assert orchestration["final_reviewer_independent"] is True
    assert roles["syllabus_outline_analyst"]["status"] == "complete"
    assert roles["handbook_writer"]["status"] == "complete"
    assert roles["final_reviewer"]["status"] == "pending"
    assert roles["final_reviewer"]["independent_from"] == [
        "syllabus_outline_analyst",
        "handbook_writer",
    ]
    assert "fresh Agent/LLM context" in roles["final_reviewer"]["dispatch_brief"][0]
    assert payload["course_spec"]["provider"] == "oxfordaqa"
    assert payload["learning_units"][0]["id"] == "unit_001"
    assert payload["pedagogical_units"][0]["writing_job_id"] == "concept_001"
    assert payload["pedagogical_units"][0]["learning_unit_id"] == "unit_001"
    assert payload["pedagogical_units"][0]["delivery_state"] == "review-ready"


def test_course_contract_payload_final_ready_requires_agent_review():
    payload = course_contract_payload(guide_plan(), delivery_status="ready", agent_review_ready=True)

    assert payload["delivery_state"] == "final-ready"
    assert payload["pedagogical_units"][0]["delivery_state"] == "final-ready"
    roles = {role["role_id"]: role for role in payload["agent_orchestration"]["roles"]}
    assert roles["final_reviewer"]["status"] == "complete"
    assert roles["final_reviewer"]["evidence"] == ["final-review-packet.json"]


def test_course_contract_payload_separates_review_performed_from_ready_verdict():
    payload = course_contract_payload(
        guide_plan(),
        delivery_status="ready",
        agent_review_ready=False,
        final_review_complete=True,
    )

    roles = {role["role_id"]: role for role in payload["agent_orchestration"]["roles"]}
    assert payload["delivery_state"] == "review-ready"
    assert roles["final_reviewer"]["status"] == "complete"
