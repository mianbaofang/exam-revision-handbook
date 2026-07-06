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

    assert payload["schema_version"] == "v0.5-lightweight-contract"
    assert payload["delivery_state"] == "needs-review"
    assert "agent_orchestration" not in payload
    assert payload["workflow"]["mode"] == "llm-owned-lightweight-workflow"
    assert [role["role_id"] for role in payload["workflow"]["roles"]] == [
        "analyst",
        "writer",
        "reviewer",
    ]
    assert payload["course_spec"]["provider"] == "oxfordaqa"
    assert payload["learning_units"][0]["id"] == "unit_001"
    assert payload["pedagogical_units"][0]["writing_job_id"] == "concept_001"
    assert payload["pedagogical_units"][0]["learning_unit_id"] == "unit_001"
    assert payload["pedagogical_units"][0]["delivery_state"] == "needs-review"


def test_course_contract_payload_never_promotes_to_final_ready():
    payload = course_contract_payload(
        guide_plan(),
        delivery_status="ready",
        agent_review_ready=True,
        quality_inspection_complete=True,
    )

    assert payload["delivery_state"] == "needs-review"
    assert payload["pedagogical_units"][0]["delivery_state"] == "needs-review"
    assert payload["quality_inspection_complete"] is True


def test_course_contract_payload_keeps_review_performed_as_external_context():
    payload = course_contract_payload(
        guide_plan(),
        delivery_status="ready",
        agent_review_ready=False,
        final_review_complete=True,
    )

    assert payload["delivery_state"] == "needs-review"
    assert "Python does not decide syllabus splits" in " ".join(
        payload["workflow"]["python_boundary"]
    )
