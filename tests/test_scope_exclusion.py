from intl_exam_guide.models import AssessmentPaper, Qualification, SourceRecord, Topic
from intl_exam_guide.planning.guide_plan import build_guide_plan, is_scope_exclusion_topic
from intl_exam_guide.validation.checks import review_summary, validate_plan


def sample_math_qualification() -> Qualification:
    return Qualification(
        title="International AS Mathematics",
        code="9660",
        qualification_type="international_as_a_level",
        subject_area="Mathematics",
        page_url="https://example.test/maths/",
        summary=["Example qualification."],
        topics=[
            Topic(
                title="P1.1 - Algebra: Quadratic functions and their graphs",
                points=["Quadratic functions and their graphs."],
            ),
            Topic(
                title="P1.4 - Integration: Questions involving regions partially above and below the x-axis will not be set",
                points=[
                    "Questions involving regions partially above and below the x-axis will not be set."
                ],
            ),
            Topic(
                title="M1.4 - Momentum: Knowledge of Newton's law of restitution is not required",
                points=["Knowledge of Newton's law of restitution is not required."],
            ),
            Topic(
                title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): Knowledge of Newton's law of restitution is not required",
                points=["Knowledge of Newton's law of restitution is not required."],
            ),
        ],
        assessments=[AssessmentPaper(title="Paper 1")],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/maths/",
            specification_url="https://example.test/maths-spec.pdf",
            specification_sha256="hash",
        ),
        audience_note="Example only.",
    )


def test_scope_exclusion_notes_do_not_become_handbook_topics():
    qualification = sample_math_qualification()

    plan = build_guide_plan(
        qualification,
        questions_per_topic=1,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="Mathematics",
    )

    assert is_scope_exclusion_topic(qualification.topics[1]) is True
    assert is_scope_exclusion_topic(qualification.topics[2]) is True
    assert is_scope_exclusion_topic(qualification.topics[3]) is True
    assert [guide.topic_title for guide in plan.topic_guides] == [
        "P1.1 - Algebra: Quadratic functions and their graphs"
    ]
    assert [item.topic_title for item in plan.practice_items] == [
        "P1.1 - Algebra: Quadratic functions and their graphs"
    ]
    assert all("will not be set" not in brief.topic_title for brief in plan.visual_briefs)


def test_validation_counts_only_teachable_handbook_topics_for_coverage():
    qualification = sample_math_qualification()
    plan = build_guide_plan(
        qualification,
        questions_per_topic=1,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="Mathematics",
    )

    messages = [issue.message for issue in validate_plan(plan)]
    summary = review_summary(plan)

    assert "Topic guide coverage does not match topic count." not in messages
    assert not any("will not be set" in message for message in messages)
    assert summary["source_topics"] == 4
    assert summary["topics"] == 1
    assert summary["scope_exclusion_topics"] == 3
