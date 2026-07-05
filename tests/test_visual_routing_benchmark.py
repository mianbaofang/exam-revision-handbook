import pytest
from intl_exam_guide.models import Topic, VisualBrief
from intl_exam_guide.planning.guide_plan import choose_visual_type
from intl_exam_guide.planning.guide_plan import zh_visual_type
from intl_exam_guide.rendering.svg_templates import render_topic_visual_svg
from intl_exam_guide.rendering.story_modes import chinese_story_lines, english_story_lines


def route(title: str, points: list[str], subject: str) -> tuple[str, str, str]:
    return choose_visual_type(Topic(title=title, points=points), points, subject)


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_complex_subject_visuals_are_routed_to_infographic_queue():
    cases = [
        (
            "3.1 - Source documents and books of prime entry",
            ["source documents, books of prime entry, ledger accounts, double entry"],
            "Accounting",
            "ledger flow",
            "svg-basic",
        ),
        (
            "2.4.2 - Market equilibrium",
            ["demand curve, supply curve, equilibrium price, market changes"],
            "Economics",
            "demand-supply",
            "svg-basic",
        ),
        (
            "8.3 - Gas tests",
            ["test for hydrogen, oxygen, carbon dioxide and chlorine using observations"],
            "Chemistry",
            "gas tests",
            "svg-basic",
        ),
        (
            "4.1 - Set notation and Venn diagrams",
            ["use set notation including n(A), union, intersection and complement"],
            "Mathematics",
            "Venn",
            "svg-basic",
        ),
        (
            "5.2 - Forces and motion",
            ["draw force arrows and explain acceleration in a real scenario"],
            "Physics",
            "force and motion",
            "svg-basic",
        ),
    ]

    for title, points, subject, expected_phrase, expected_complexity in cases:
        visual_type, complexity, trigger = route(title, points, subject)

        assert complexity == expected_complexity, (subject, visual_type, trigger)
        assert expected_phrase.lower() in visual_type.lower()


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_additional_visual_routes_do_not_overqueue_optional_images():
    cases = [
        (
            "Accounting",
            "Adjustments",
            ["depreciation, receivables, payables and prudence"],
            "text-ok",
            "optional table",
        ),
        (
            "Accounting",
            "Financial statements",
            ["income statement, statement of financial position and ratio analysis"],
            "svg-basic",
            "financial-statement",
        ),
        (
            "Economics",
            "Sectors",
            ["primary, secondary and tertiary sectors"],
            "text-ok",
            "mini case",
        ),
        (
            "Economics",
            "Banking",
            ["money, banks, financial markets and interest rates"],
            "text-ok",
            "mini case",
        ),
        (
            "Chemistry",
            "Rates",
            ["rate of reaction, equilibrium and reversible reactions"],
            "svg-basic",
            "reaction-rate",
        ),
        (
            "Chemistry",
            "Organic",
            ["organic chemistry, hydrocarbons, polymers and crude oil"],
            "infographic",
            "organic",
        ),
        (
            "Mathematics",
            "Matrices",
            ["vectors, matrices and transformations"],
            "infographic",
            "matrix",
        ),
    ]

    for subject, title, points, expected_complexity, expected_phrase in cases:
        visual_type, complexity, trigger = route(title, points, subject)

        assert complexity == expected_complexity, (subject, visual_type, trigger)
        assert expected_phrase.lower() in visual_type.lower()


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_simple_svg_routes_stay_subject_specific():
    cases = [
        (
            "1.2 - Ratio and proportion",
            ["use ratio notation and fractions on a number line"],
            "Mathematics",
            "number line",
            "Number line",
        ),
        (
            "6.1 - Right-angled triangles",
            ["use Pythagoras' theorem in a simple right-angled triangle"],
            "Mathematics",
            "geometry",
            "Right triangle",
        ),
        (
            "7.2 - Acids and alkalis",
            ["use the pH scale and describe neutralisation"],
            "Chemistry",
            "pH scale",
            "pH scale",
        ),
        (
            "3.4 - Distance-time graphs",
            ["interpret a distance-time graph"],
            "Physics",
            "distance-time",
            "Distance-time",
        ),
    ]

    for title, points, subject, visual_phrase, svg_title in cases:
        visual_type, complexity, _ = route(title, points, subject)
        svg = render_topic_visual_svg(
            VisualBrief(
                topic_title=title,
                focus_point=points[0],
                trigger="benchmark",
                visual_type=visual_type,
                complexity=complexity,
                image_provider="deterministic-svg",
                prompt="benchmark",
                source_points=points,
            ),
            index=1,
        )

        assert complexity == "svg-basic", (subject, visual_type)
        assert visual_phrase.lower() in visual_type.lower()
        assert svg_title in svg


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_additional_simple_svg_routes_use_deterministic_diagrams():
    cases = [
        ("Chemistry", "States", ["solid liquid particles atoms"], "particle model"),
        ("Chemistry", "Energy", ["exothermic and endothermic energy profiles"], "energy profile"),
        (
            "Mathematics",
            "Sampling",
            ["histograms, cumulative frequency, sampling and population"],
            "statistics chart",
        ),
        (
            "Mathematics",
            "Probability",
            ["probability statistics charts and data"],
            "statistics chart",
        ),
        ("Generic", "Data skills", ["measurements, tables and graphs"], "data table"),
    ]

    for subject, title, points, expected_phrase in cases:
        visual_type, complexity, _ = route(title, points, subject)

        assert complexity == "svg-basic", (subject, visual_type)
        assert expected_phrase.lower() in visual_type.lower()


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_plain_symbolic_mathematics_does_not_get_a_visual_by_default():
    visual_type, complexity, _ = route(
        "Algebra",
        ["algebra equations functions and sequences"],
        "Mathematics",
    )

    assert complexity == "text-ok"
    assert visual_type == "text explanation with no custom visual"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_statistics_is_not_used_as_generic_fallback_for_unrelated_topics():
    unrelated_cases = [
        (
            "Accounting",
            "bank reconciliation",
            ["cash book, bank statement, unpresented cheques"],
            "svg-basic",
        ),
        (
            "Chemistry",
            "chromatography",
            ["separate dyes using chromatography and calculate Rf values"],
            "text-ok",
        ),
        (
            "Economics",
            "opportunity cost",
            ["choices, scarcity, opportunity cost, trade-offs"],
            "text-ok",
        ),
    ]

    for subject, title, points, expected_complexity in unrelated_cases:
        visual_type, complexity, _ = route(title, points, subject)

        assert complexity == expected_complexity
        assert "statistics" not in visual_type.lower()


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_complex_svg_fallbacks_use_subject_templates():
    cases = [
        (
            "3.1 - Source documents and books of prime entry",
            ["source documents, books of prime entry, ledger accounts, double entry"],
            "Accounting",
            "Accounting records flow",
            "Prime entry",
        ),
        (
            "2.4.2 - Market equilibrium",
            ["demand curve, supply curve, equilibrium price, market changes"],
            "Economics",
            "Demand and supply market diagram",
            "Equilibrium",
        ),
        (
            "4.1 - Set notation and Venn diagrams",
            ["use set notation including n(A), union, intersection and complement"],
            "Mathematics",
            "Set notation and Venn regions",
            "A ∩ B",
        ),
        (
            "8.3 - Gas tests",
            ["test for hydrogen, oxygen, carbon dioxide and chlorine using observations"],
            "Chemistry",
            "Common gas tests observation chart",
            "limewater",
        ),
        (
            "5.2 - Forces and motion",
            ["draw force arrows and explain acceleration in a real scenario"],
            "Physics",
            "Force and motion diagram",
            "resultant force",
        ),
    ]

    for title, points, subject, expected_title, expected_label in cases:
        visual_type, complexity, _ = route(title, points, subject)
        svg = render_topic_visual_svg(
            VisualBrief(
                topic_title=title,
                focus_point=points[0],
                trigger="benchmark",
                visual_type=visual_type,
                complexity=complexity,
                image_provider="external-generation-required",
                prompt="benchmark",
                source_points=points,
            ),
            index=1,
        )

        assert complexity in {"infographic", "svg-basic"}
        assert expected_title in svg
        assert expected_label in svg
        assert "Particle model" not in svg


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_chinese_visual_type_keeps_accounting_specific_route():
    visual_type, complexity, _ = route(
        "2.2 - Books of original entry",
        ["source documents, books of prime entry, ledger accounts"],
        "Accounting",
    )
    zh_type = zh_visual_type(visual_type)
    svg = render_topic_visual_svg(
        VisualBrief(
            topic_title="2.2 - Books of original entry",
            focus_point="原始凭证与初始记录账簿",
            trigger="benchmark",
            visual_type=zh_type,
            complexity=complexity,
            image_provider="external-generation-required",
            prompt="benchmark",
            source_points=["source documents"],
        ),
        index=1,
        language="zh-CN",
    )

    assert zh_type == "会计记录流程图"
    assert "会计记录流程" in svg
    assert "原始凭证" in svg


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_story_modes_choose_topic_specific_scenes():
    accounting = english_story_lines("Ledger accounts", "source documents", 1)
    economics = english_story_lines("Demand and supply", "market equilibrium", 1)
    chemistry = chinese_story_lines("气体检验", "氧气复燃", 1)
    maths = chinese_story_lines("集合与韦恩图", "交集区域", 1)

    assert "shop's records" in accounting[0]
    assert "curve or trade-off" in economics[1]
    assert "实验台" in chemistry[0]
    assert "图上的标记" in maths[0]
