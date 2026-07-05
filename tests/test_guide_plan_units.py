import pytest
import os

from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
)
from intl_exam_guide.planning.guide_plan import (
    build_guide_plan,
    build_topic_guide,
    build_revision_stages,
    build_run_options,
    normalize_image_provider,
)
from intl_exam_guide.planning.source_points import clean_source_point, visible_source_points


def sample_accounting_qualification() -> Qualification:
    return Qualification(
        title="International GCSE Accounting (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=["Example qualification."],
        topics=[
            Topic(
                title="2.1 - Source documents and ledgers",
                points=[
                    "Source documents include purchase invoices and sales invoices.",
                    "Ledger entries record the double entry effect of transactions.",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Source documents include purchase invoices and sales invoices.",
                        matched_term="Source documents",
                    )
                ],
            )
        ],
        assessments=[AssessmentPaper(title="Paper 1", details=["1 hour 30 minutes"])],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/accounting/",
            specification_url="https://example.test/accounting-spec.pdf",
        ),
        audience_note="Example only.",
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_build_guide_plan_creates_guides_practice_and_visual_briefs():
    plan = build_guide_plan(
        sample_accounting_qualification(),
        questions_per_topic=2,
        image_provider="prompt-queue",
        explanation_style="detective",
        output_language="en",
        requested_subject="accounting",
    )

    assert plan.run_options.requested_subject == "accounting"
    assert plan.run_options.image_provider == "prompt-queue"
    assert len(plan.topic_guides) == 1
    assert len(plan.practice_items) == 2
    assert len(plan.visual_briefs) == 1
    assert plan.visual_briefs[0].image_provider == "kroki"
    question = plan.practice_items[0].question.lower()
    assert "invoice" in question
    assert "source document" in question
    assert "accounting record" in question
    assert len({item.question for item in plan.practice_items}) == 2


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_term_support_language_keeps_generated_plan_body_english():
    plan = build_guide_plan(
        sample_accounting_qualification(),
        questions_per_topic=1,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="zh-CN",
        requested_subject="accounting",
    )

    assert plan.run_options.output_language == "zh-CN"
    assert plan.revision_stages[0].startswith("Stage 1")
    assert plan.topic_guides[0].worked_solution_steps[0].startswith("Read")
    assert plan.practice_items[0].command_word in {
        "Calculate",
        "Describe",
        "Explain",
        "Identify",
        "state",
    }
    assert plan.visual_briefs[0].prompt.startswith("Create ")


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_checklist_mastery_includes_topic_context_for_repeated_source_points():
    qualification = sample_accounting_qualification()
    repeated_points = [
        "a) Explain the causes of depreciation.",
        "b) Distinguish between straight line and reducing balance methods.",
    ]
    qualification.topics = [
        Topic(
            title="2.5 - Depreciation",
            points=list(repeated_points),
            source_snippets=[
                SourceSnippet(page=20, text="Depreciation in bookkeeping", matched_term="2.5")
            ],
        ),
        Topic(
            title="5.2 - Depreciation",
            points=list(repeated_points),
            source_snippets=[
                SourceSnippet(page=35, text="Depreciation in final accounts", matched_term="5.2")
            ],
        ),
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="accounting",
    )

    checklist_first_lines = [guide.checklist[0] for guide in plan.topic_guides]

    assert checklist_first_lines[0] != checklist_first_lines[1]
    assert "2.5 - Depreciation" in checklist_first_lines[0]
    assert "5.2 - Depreciation" in checklist_first_lines[1]


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_build_guide_plan_completes_parser_fragment_topic_titles():
    qualification = sample_accounting_qualification()
    qualification.subject_area = "Mathematics"
    qualification.topics = [
        Topic(
            title="P1.5 - Sequences and series: Arithmetic series,",
            points=[
                "Arithmetic series, including the formula for the sum of the first n natural numbers.",
                "To include ∑ notation for sums of series.",
            ],
            source_snippets=[
                SourceSnippet(
                    page=12, text="Arithmetic series, including the formula", matched_term="P1.5"
                )
            ],
        ),
        Topic(
            title="P1.5 - Sequences and series: The binomial expansion of",
            points=[
                "The binomial expansion of",
                "(1+ x)n for positive integer n.",
                "To include the notations n! and n r",
            ],
            source_snippets=[
                SourceSnippet(page=12, text="The binomial expansion of (1+x)n", matched_term="P1.5")
            ],
        ),
        Topic(
            title="P1.1 - Algebra: Use of the Remainder Theorem and the",
            points=["Use of the Remainder Theorem and the"],
            source_snippets=[
                SourceSnippet(
                    page=10, text="Use of the Remainder Theorem and the", matched_term="P1.1"
                )
            ],
        ),
        Topic(
            title="M1.1 - Motion: Difference bet...",
            points=[
                "Difference between displacement and distance, and between velocity and speed."
            ],
            source_snippets=[
                SourceSnippet(
                    page=17,
                    text="Difference between displacement and distance",
                    matched_term="M1.1",
                )
            ],
        ),
        Topic(
            title="P1.1 - Algebra: Use of factorisation, −± −bb ac a",
            points=["Use of factorisation, −± −bb ac a"],
            source_snippets=[
                SourceSnippet(
                    page=10, text="Use of factorisation, quadratic formula", matched_term="P1.1"
                )
            ],
        ),
        Topic(
            title="P1.5 - Sequences and series: Students should be familiar with the notation |r|<1 in this context",
            points=["Students should be familiar with the notation |r|<1 in this context."],
            source_snippets=[
                SourceSnippet(
                    page=12,
                    text="Students should be familiar with the notation |r|<1",
                    matched_term="P1.5",
                )
            ],
        ),
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="mathematics",
    )

    titles = [topic.title for topic in plan.qualification.topics]
    assert titles == [
        "P1.5 - Sequences and series: Arithmetic series, including the formula for the sum of the first n natural numbers",
        "P1.5 - Sequences and series: The binomial expansion of (1 + x)^n for positive integer n",
        "P1.1 - Algebra: Use of the Remainder Theorem and the Factor Theorem",
        "M1.1 - Motion: Difference between displacement and distance, and between velocity and speed",
        "P1.1 - Algebra: Use of factorisation, completing the square and the quadratic formula",
        "P1.5 - Sequences and series: Notation |r|<1 in this context",
    ]
    structured_text = " ".join(
        " ".join([topic.title, *topic.points]) for topic in plan.qualification.topics
    )
    assert "−± −bb ac a" not in structured_text
    assert (
        "Use of factorisation, completing the square and the quadratic formula" in structured_text
    )
    visible_text = " ".join(
        " ".join([guide.essence, *guide.checklist]) for guide in plan.topic_guides
    )
    assert ", is a" not in visible_text
    assert ",:" not in visible_text
    assert "The binomial expansion of is" not in visible_text


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_clean_source_point_removes_embedded_syllabus_shell():
    assert (
        clean_source_point("The factors of production Students should be able to")
        == "The factors of production"
    )
    assert (
        clean_source_point("Identifying market structures Students should be able to understand:")
        == "Identifying market structures"
    )
    assert (
        clean_source_point(
            "Students should be able to understand the nature of an economic resource"
        )
        == "understand the nature of an economic resource"
    )
    assert (
        clean_source_point("Use of the Remainder Theorem and the")
        == "Use of the Remainder Theorem and the Factor Theorem"
    )
    assert clean_source_point("eg 2 2xx + /greaterthanorequalangled6") == "eg 2x^2 + x >= 6"
    assert (
        clean_source_point("tan sin cosθ θ θ= ; and sinc os 122 +=θθ")
        == "tan theta = sin theta / cos theta; and sin^2 theta + cos^2 theta = 1"
    )
    assert (
        clean_source_point("The binomial expansion of (1+ x)n for positive integer n.")
        == "The binomial expansion of (1 + x)^n for positive integer n"
    )
    assert (
        clean_source_point("The notations f' (x) or d d y x will be used.")
        == "The notations f' (x) or dy/dx will be used"
    )
    assert (
        clean_source_point("The area of a triangle in the form ab Csin2")
        == "The area of a triangle in the form 1/2 ab sin C"
    )
    assert clean_source_point("2t as vtt= 2") == "s = ut + 1/2 at^2 and v = u + at"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_source_points_remove_cambridge_page_boilerplate():
    topic = Topic(
        title="1.2.2 Quantity and quality of factors of production",
        points=[
            "causes of changes in the quantity and quality of factors of production",
            "Cambridge IGCSE Economics 0455 syllabus for 2027, 2028 and 2029. Subject content",
            "12www.cambridgeinternational.org/igcseBack to contents page",
            "Faculty feedback: Understanding how and why our climate is changing.",
            "Feedback from: Dr Example, Cambridge Zero",
        ],
    )

    assert visible_source_points(topic) == [
        "causes of changes in the quantity and quality of factors of production"
    ]
    assert (
        clean_source_point(
            "main influences on whether supply is elastic or inelastic Cambridge IGCSE Economics 0455 syllabus for 2027, 2028 and 2029. Subject content 15www.cambridgeinternational.org/igcseBack to contents page"
        )
        == "main influences on whether supply is elastic or inelastic"
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_source_points_remove_pearson_page_boilerplate_and_formula_noise():
    topic = Topic(
        title="5.5 - pressure, force and area",
        points=[
            "forcepressure area=",
            "Specification - Issue 4 - September 2024 © Pearson Education Limited 2024",
            "(b) Density and pressure",
            "Students should:",
        ],
    )

    assert visible_source_points(topic) == ["pressure = force / area"]
    assert clean_source_point("force = mass ¡Á acceleration") == "force = mass x acceleration"
    assert (
        clean_source_point(
            "Using algebraic methods. Students will be expected to interpret the result"
        )
        == "Using algebraic methods. interpret the result"
    )
    assert (
        clean_source_point("Students should be familiar with the notation |r|<1")
        == "the notation |r|<1"
    )
    assert clean_source_point("Candidates should have an understanding of: demand") == "demand"
    assert clean_source_point("a) Explain the purpose of the:") == ""
    assert clean_source_point("a) Apply the following accounting concepts:") == ""
    assert clean_source_point("a) Explain the causes of depreciation.") == "causes of depreciation"
    assert (
        clean_source_point(
            "b) Distinguish between straight line and reducing balance methods of depreciation."
        )
        == "straight line and reducing balance methods of depreciation"
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_student_facing_points_skip_syllabus_shell_phrases():
    qualification = sample_accounting_qualification()
    qualification.topics = [
        Topic(
            title="3.2 - Corrections of errors",
            points=[
                "Candidates should have an understanding of:",
                "how to correct errors using journal entries",
                "how to prepare suspense accounts",
            ],
        ),
        Topic(
            title="2.3 - Ledger accounting",
            points=[
                "a) Explain the purpose of the:",
                "nominal ledger",
                "sales ledger",
            ],
        ),
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="accounting",
    )
    combined = " ".join(
        [
            *[guide.checklist[0] for guide in plan.topic_guides],
            *[item.focus_point for item in plan.practice_items],
            *[brief.focus_point for brief in plan.visual_briefs],
        ]
    ).lower()

    assert "candidates should have an understanding" not in combined
    assert "explain the purpose of the:" not in combined
    assert "how to correct errors using journal entries" in combined
    assert "nominal ledger" in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_student_facing_points_skip_split_pearson_accounting_shells():
    qualification = sample_accounting_qualification()
    qualification.topics = [
        Topic(
            title="1.2 - Accounting concepts",
            points=[
                "a) Understand the significance of the following accounting",
                "concepts:",
                "consistency",
                "prudence",
            ],
        )
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="accounting",
    )
    combined = " ".join(
        [
            plan.topic_guides[0].checklist[0],
            plan.practice_items[0].focus_point,
            plan.practice_items[0].question,
        ]
    ).lower()
    practice_text = " ".join(
        [plan.practice_items[0].focus_point, plan.practice_items[0].question]
    ).lower()

    assert "understand the significance of the following accounting" not in combined
    assert "concepts:" not in practice_text
    assert "consistency" in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_student_facing_points_skip_pearson_business_organisation_shells():
    qualification = sample_accounting_qualification()
    qualification.topics = [
        Topic(
            title="1.1 - Types of business organisation",
            points=[
                "a) Explain the characteristics of:",
                "public sector organisations",
                "private sector organisations",
                "sole traders",
                "partnerships.",
            ],
        )
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="accounting",
    )
    combined = " ".join(
        [
            plan.topic_guides[0].checklist[0],
            plan.practice_items[0].focus_point,
            plan.practice_items[0].question,
        ]
    ).lower()

    assert "explain the characteristics of" not in combined
    assert "public sector organisations" in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_student_facing_points_merge_wrapped_pearson_accounting_lines():
    qualification = sample_accounting_qualification()
    qualification.topics = [
        Topic(
            title="5.3 - Irrecoverable debts",
            points=[
                "a) Explain why it is necessary to provide a provision for",
                "irrecoverable debts.",
                "b) Distinguish between an irrecoverable debt and a provision for",
                "an irrecoverable debt.",
            ],
        ),
        Topic(
            title="2.4 - Capital expenditure and revenue expenditure",
            points=[
                "a) Explain the terms:",
                "capital expenditure",
                "revenue expenditure.",
                "b) Explain the importance of the correct treatment of capital",
                "expenditure and revenue expenditure.",
            ],
        ),
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="accounting",
    )
    combined = " ".join(
        [
            *[guide.checklist[0] for guide in plan.topic_guides],
            *[item.focus_point for item in plan.practice_items],
        ]
    ).lower()

    assert "provide a provision for irrecoverable debts" in combined
    assert "provide a provision for," not in combined
    assert "the terms:" not in combined
    assert "capital expenditure" in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_build_run_options_normalizes_invalid_choices_without_bilingual_mode():
    qualification = sample_accounting_qualification()

    options = build_run_options(
        qualification=qualification,
        requested_subject=None,
        image_provider="sensenova-u1-fast",
        explanation_style="unknown-style",
        output_language="fr",
        exam_year=None,
        image_model=None,
        image_endpoint_url=None,
        image_api_key_env=None,
    )

    assert options.requested_subject == qualification.title
    assert options.image_provider == "prompt-queue"
    assert options.explanation_style == "friendly"
    assert options.output_language == "en"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_custom_image_provider_requires_all_custom_fields_and_environment(monkeypatch):
    monkeypatch.delenv("SCHOOL_IMAGE_KEY", raising=False)

    assert (
        normalize_image_provider(
            "custom",
            "school-model",
            "https://images.example.test/v1/images/generations",
            "SCHOOL_IMAGE_KEY",
        )
        == "prompt-queue"
    )

    monkeypatch.setenv("SCHOOL_IMAGE_KEY", "test-value")

    assert (
        normalize_image_provider(
            "custom",
            "school-model",
            "https://images.example.test/v1/images/generations",
            "SCHOOL_IMAGE_KEY",
        )
        == "custom"
    )
    assert os.environ["SCHOOL_IMAGE_KEY"] == "test-value"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_revision_stages_are_readable_text():
    stages = build_revision_stages("international_as_a_level", "zh-CN")

    assert stages == [
        "第 1 阶段 - 单元地图：先分清 AS、A2 或模块单元，再做综合题。",
        "第 2 阶段 - 建构：把每个单元点整理成短讲解、一道应用题和一个易错点。",
        "第 3 阶段 - 测试：先按单元练，再把不同单元放在一起做综合练习。",
    ]
    assert not any(" / " in stage for stage in stages)


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_concept_explanation_is_source_bound_not_subject_hardcoded():
    guide = build_topic_guide(
        Topic(
            title="2.3 - Market failure: External costs and benefits",
            points=[
                "External costs and benefits. Candidates should understand how third parties are affected."
            ],
        ),
        "international_gcse",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert len(guide.checklist) >= 3
    assert "概念草稿" not in checklist
    assert "核心内容" in checklist
    assert "需要说清的关系" in checklist
    assert "市场" in checklist or "External" not in checklist
    assert "本节核心主题" not in checklist
    assert "带情境或数据的小题" not in checklist
    assert "常见错误" not in checklist


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_concept_explanation_avoids_math_template_for_accounting_topic():
    guide = build_topic_guide(
        Topic(
            title="3.1 - Accounting: Bank reconciliation",
            points=[
                "Bank reconciliation statements including unpresented cheques and outstanding lodgements."
            ],
        ),
        "international_gcse",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "银行对账" in checklist
    assert "二次方程" not in checklist
    assert "牛顿" not in checklist


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_momentum_concept_explanation_is_not_collision_template():
    guide = build_topic_guide(
        Topic(
            title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): Concept of momentum",
            points=["Concept of momentum."],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "动量概念" in checklist or "动量" in checklist
    assert "碰前" not in checklist


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_checklist_filters_untranslated_secondary_point_placeholders():
    guide = build_topic_guide(
        Topic(
            title="P1.1 - Algebra: Solution of linear and quadratic inequalities",
            points=[
                "Solution of linear and quadratic inequalities.",
                "eg 2 2xx + /greaterthanorequalangled6",
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    visible_text = " ".join([*guide.checklist, guide.diagram_brief])

    assert "一次与二次不等式求解" in visible_text
    assert "本节核心主题" not in visible_text


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_concept_explanation_does_not_cross_wire_ambiguous_source_notes():
    guide = build_topic_guide(
        Topic(
            title="P1.3 - Differentiation: Applications of differentiation",
            points=[
                "Applications of differentiation to gradients, tangents and normals, "
                "maxima and minima and stationary points, increasing and decreasing functions.",
                "Questions will not be set requiring the determination of or knowledge of "
                "points of inflection.",
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "微分" in checklist
    assert "集合与韦恩图" not in checklist


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_newton_laws_explanation_is_not_overwritten_by_resistive_forces():
    guide = build_topic_guide(
        Topic(
            title="M1.3 - Forces and Newton’s Laws: Newton’ s three laws of motion",
            points=[
                "Newton’ s three laws of motion. Restricted to dynamics in a straight line "
                "on the horizontal or motion vertically including resistive forces."
            ],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "牛顿" in checklist
    assert "掌握：阻力" not in checklist


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_concept_explanation_is_not_action_checklist():
    guide = build_topic_guide(
        Topic(
            title="P1.3 - Differentiation: The derivative of f (x) as the gradient of the tangent",
            points=["The derivative of f (x) as the gradient of the tangent."],
        ),
        "international_as_a_level",
        "friendly",
        "zh-CN",
    )

    checklist = " ".join(guide.checklist)

    assert "概念草稿" not in checklist
    assert "导数" in checklist
    assert "核心内容" in checklist
    assert "需要说清的关系" in checklist
    assert "会识别" not in checklist
    assert "会操作" not in checklist
    assert "会检查" not in checklist
