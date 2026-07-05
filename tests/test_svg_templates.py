import re

from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.svg_templates import (
    html_escape,
    render_accounting_flow_svg,
    render_accounting_statement_variant_svg,
    render_algebra_svg,
    render_analysis_svg,
    render_bonding_svg,
    render_concept_fallback_svg,
    render_energy_svg,
    render_financial_statement_svg,
    render_flow_svg,
    render_force_svg,
    render_gas_tests_svg,
    render_market_svg,
    render_math_topic_svg,
    market_variant_from_text,
    render_motion_svg,
    render_number_svg,
    render_organic_svg,
    render_particles_svg,
    render_ph_svg,
    render_rate_svg,
    render_reconciliation_svg,
    render_statistics_svg,
    render_topic_visual_svg,
    render_triangle_svg,
    render_velocity_area_svg,
    render_zh_visual_svg,
    svg_multiline_text,
    wrap_words,
)
from intl_exam_guide.validation.checks import svg_structure_fingerprint


def visual(visual_type: str) -> VisualBrief:
    return VisualBrief(
        topic_title="Topic",
        focus_point="focus",
        trigger="trigger",
        visual_type=visual_type,
        complexity="svg-basic",
        image_provider="deterministic-svg",
        prompt="prompt",
        source_points=[],
    )


def visual_with_focus(visual_type: str, focus: str) -> VisualBrief:
    return VisualBrief(
        topic_title="Topic",
        focus_point=focus,
        trigger="trigger",
        visual_type=visual_type,
        complexity="svg-basic",
        image_provider="deterministic-svg",
        prompt="prompt",
        source_points=[focus],
    )


def assert_svg_contract(svg: str, title: str, index: int = 1) -> None:
    assert '<svg class="visual-svg"' in svg
    assert 'role="img"' in svg
    assert f'aria-labelledby="visual-title-{index}"' in svg
    assert f'<title id="visual-title-{index}">{title}</title>' in svg


def test_function_graph_router_uses_topic_specific_math_motifs():
    cases = [
        visual_with_focus(
            "function graph or coordinate visual",
            "Quadratic functions and their graphs.",
        ),
        visual_with_focus(
            "function graph or coordinate visual",
            "Interpreting solutions as intersection points of graphs.",
        ),
        visual_with_focus(
            "function graph or coordinate visual",
            "Equation of a straight line using gradients and mid-points.",
        ),
        visual_with_focus(
            "function graph or coordinate visual",
            "Sketching and interpreting kinematics graphs with velocity and acceleration.",
        ),
    ]

    svgs = [render_topic_visual_svg(case, index) for index, case in enumerate(cases, start=1)]

    assert len({svg_structure_fingerprint(svg) for svg in svgs}) == len(cases)
    assert "Quadratic functions and their graphs" in svgs[0]
    assert "intersections = simultaneous solutions" in svgs[1]
    assert "y=mx+c" in svgs[2]
    assert "velocity-time and displacement-time graphs" in svgs[3]


def test_trig_tangent_functions_do_not_route_to_circle_tangent_svg():
    brief = visual_with_focus(
        "trigonometry circle or graph visual",
        "Sine, cosine and tangent functions.",
    )

    svg = render_topic_visual_svg(brief, 1, "en")

    assert "sin, cos, tan" in svg
    assert "radius ⟂ tangent" not in svg


def test_coordinate_circle_visual_does_not_borrow_tangent_normal_svg():
    brief = visual_with_focus(
        "circle coordinate visual",
        "Coordinate geometry of the circle. The use of tangent and radius properties is required.",
    )

    svg = render_topic_visual_svg(brief, 1, "en")

    assert "(x-a)²+(y-b)²=r²" in svg
    assert "radius ⟂ tangent" not in svg


def test_math_topic_svg_uses_compact_internal_frame():
    svg = render_math_topic_svg(
        1,
        "Trigonometry visual",
        "The sine and cosine rules",
        "trig:triangle",
    )

    assert 'rect x="6" y="6" width="708" height="348"' in svg
    assert 'transform="translate(-28 -14) scale(1.15)"' in svg
    assert 'rect x="436" y="72" width="270" height="244"' in svg
    assert 'rect x="20" y="20" width="680" height="320"' not in svg


def test_motion_graph_gradient_area_uses_distinct_velocity_area_svg():
    sketch = visual_with_focus(
        "motion graph visual",
        "Sketching and interpreting kinematics graphs.",
    )
    area = visual_with_focus(
        "motion graph visual",
        "Use of gradients and area under graphs to solve problems.",
    )

    sketch_svg = render_topic_visual_svg(sketch, 1, "en")
    area_svg = render_topic_visual_svg(area, 2, "en")

    assert "Distance-time graph" in sketch_svg
    assert "Velocity-time graph: gradient and area" in area_svg
    assert "area = displacement" in area_svg
    assert "Velocity-time graph: gradient and area" in render_velocity_area_svg(3)
    assert svg_structure_fingerprint(sketch_svg) != svg_structure_fingerprint(area_svg)


def test_mechanics_routes_use_topic_specific_structures():
    connected = visual_with_focus(
        "mechanics force or collision diagram",
        "Connected particle problems with a light inextensible string passing over a smooth pulley.",
    )
    momentum = visual_with_focus(
        "mechanics before-after collision diagram",
        "The principle of conservation of momentum applied to two particles.",
    )
    fixed_surface = visual_with_focus(
        "mechanics before-after collision diagram",
        "Direct impact with a fixed surface, perpendicular to a fixed smooth surface.",
    )

    svgs = [
        render_topic_visual_svg(connected, 1, "en"),
        render_topic_visual_svg(momentum, 2, "en"),
        render_topic_visual_svg(fixed_surface, 3, "en"),
    ]

    assert "same acceleration" in svgs[0]
    assert "total momentum conserved" in svgs[1]
    assert "perpendicular impact" in svgs[2]
    assert len({svg_structure_fingerprint(svg) for svg in svgs}) == 3


def test_probability_statistics_routes_use_topic_specific_structures():
    random_variable = visual_with_focus(
        "statistics chart visual",
        "Discrete random variables and their associated probability distributions.",
    )
    binomial = visual_with_focus(
        "statistics chart visual",
        "Binomial distribution. Introduced as the sum of independent Bernoulli trials.",
    )

    random_svg = render_topic_visual_svg(random_variable, 1, "en")
    binomial_svg = render_topic_visual_svg(binomial, 2, "en")

    assert "E(X), Var(X)" in random_svg
    assert "X ~ B(n,p)" in binomial_svg
    assert "Data becomes evidence" not in random_svg
    assert "Data becomes evidence" not in binomial_svg
    assert svg_structure_fingerprint(random_svg) != svg_structure_fingerprint(binomial_svg)


def test_svg_topic_router_covers_english_subject_routes():
    route_expectations = [
        ("ledger flow diagram", "Accounting records flow"),
        ("bank reconciliation verification", "Verification and reconciliation"),
        ("trial balance verification table", "Trial balance verification table"),
        ("control account reconciliation diagram", "Control account reconciliation"),
        ("error correction and suspense account flow", "Error correction and suspense flow"),
        ("incomplete records reconstruction flow", "Incomplete records reconstruction"),
        ("financial statement ratio-analysis", "Financial statement layout"),
        ("demand-supply market scenario", "Demand and supply market diagram"),
        ("stakeholder influence map", "Stakeholder influence map"),
        ("business ownership comparison table", "Business ownership comparison"),
        ("cash-flow timeline and balance table", "Cash-flow timeline"),
        ("break-even chart with cost and revenue lines", "Break-even chart"),
        ("marketing mix quadrant visual", "Marketing mix"),
        ("customer segmentation map", "Customer segmentation map"),
        ("organisation structure hierarchy diagram", "Organisation structure hierarchy"),
        ("quality assurance checkpoint diagram", "Quality assurance checkpoint loop"),
        ("operations flow and quality checkpoint diagram", "Operations flow and checkpoints"),
        ("business decision flow diagram", "Business decision flow"),
        ("historical timeline visual", "Historical timeline"),
        ("cause and consequence chain", "Cause and consequence chain"),
        ("source evidence comparison visual", "Source evidence comparison"),
        ("change and continuity comparison visual", "Change and continuity comparison"),
        ("factors of production opportunity cost", "Economic choice flow"),
        ("set notation venn", "Set notation and Venn regions"),
        ("force and motion force arrows", "Force and motion diagram"),
        ("common gas tests", "Common gas tests observation chart"),
        ("acid base ph", "pH scale and salt preparation"),
        ("particle solid liquid atom", "Particle model diagram"),
        ("bond ionic covalent structure", "Bonding and structure diagram"),
        ("organic hydrocarbon carbon", "Hydrocarbon chain diagram"),
        ("chemical analysis chromatography", "Chromatography diagram"),
        ("distance-time motion graph", "Distance-time graph"),
        ("rate equilibrium", "Rate of reaction graph"),
        ("energy exothermic endothermic", "Reaction energy profile"),
        ("number line fraction ratio", "Number line, fraction bar, and ratio diagram"),
        ("function graph equation-balance algebra", "Function graph and equation balance"),
        ("statistics chart probability", "Statistics chart and probability visual"),
        ("geometry diagram triangle pythagoras", "Right triangle diagram"),
        ("data table graph interpretation", "Statistics chart and probability visual"),
    ]

    for index, (visual_type, expected_title) in enumerate(route_expectations, start=1):
        svg = render_topic_visual_svg(visual(visual_type), index, "en")
        assert_svg_contract(svg, expected_title, index)

    fallback = render_topic_visual_svg(visual("unmatched custom visual"), 99, "en")
    assert_svg_contract(fallback, "unmatched custom visual", 99)


def test_svg_topic_router_covers_chinese_subject_routes():
    route_expectations = [
        ("会计记录流程图", "会计记录流程"),
        ("银行对账核对图", "核对与调节流程"),
        ("财务报表比率图", "财务报表结构"),
        ("会计调整影响图", "会计记录流程"),
        ("市场供需曲线", "市场供需图"),
        ("生产要素和机会成本", "经济选择流程"),
        ("集合韦恩图", "集合与韦恩图"),
        ("力与运动合力", "力与运动示意图"),
        ("气体检验观察", "气体检验观察图"),
        ("粒子模型", "Particle model diagram"),
        ("酸碱 pH", "pH scale and salt preparation"),
        ("几何三角形", "Right triangle diagram"),
        ("统计概率图", "概率与分布图"),
    ]

    for index, (visual_type, expected_title) in enumerate(route_expectations, start=1):
        svg = render_topic_visual_svg(visual(visual_type), index, "zh-CN")
        assert_svg_contract(svg, expected_title, index)

    fallback = render_zh_visual_svg(visual("复杂自定义图文学习图"), 77)
    assert_svg_contract(fallback, "复杂自定义图文学习图", 77)
    assert "复杂自定义图文学习图" in fallback


def test_chinese_svg_router_uses_chemistry_source_points_before_generic_labels():
    cases = [
        (
            "图文结合学习图",
            "第 3.1.1 节",
            ["solid liquid gas particles states of matter"],
            "Particle model diagram",
        ),
        (
            "图文结合学习图",
            "第 3.4.1 节",
            ["chromatography separates mixtures and checks purity"],
            "Chromatography diagram",
        ),
        (
            "图文结合学习图",
            "第 3.8.1 节",
            ["rate of reaction and equilibrium"],
            "Rate of reaction graph",
        ),
        (
            "图文结合学习图",
            "第 3.9.1 节",
            ["exothermic and endothermic energy changes"],
            "Reaction energy profile",
        ),
        (
            "图文结合学习图",
            "第 3.10.1 节",
            ["organic chemistry hydrocarbons crude oil polymers"],
            "Hydrocarbon chain diagram",
        ),
    ]

    for index, (visual_type, focus, source_points, expected_title) in enumerate(cases, start=1):
        brief = visual(visual_type)
        brief.focus_point = focus
        brief.source_points = source_points
        svg = render_topic_visual_svg(brief, index, "zh-CN")

        assert_svg_contract(svg, expected_title, index)


def test_chinese_generic_svg_fallback_uses_topic_specific_title():
    brief = visual("图文结合学习图")
    brief.focus_point = "第 9.9 节"

    svg = render_topic_visual_svg(brief, 12, "zh-CN")

    assert_svg_contract(svg, "第 9.9 节", 12)


def test_chinese_math_svg_router_uses_distinct_subject_templates():
    cases = [
        ("二次函数图像", "二次函数图像图解", "x²"),
        ("导数与曲线梯度", "导数与曲线梯度图解", "切线斜率"),
        ("定积分与曲线下面积", "定积分与曲线下面积图解", "面积"),
        ("等比数列求和", "等比数列求和图解", "r"),
        ("正弦、余弦与正切", "正弦、余弦与正切图解", "sin"),
        ("二项分布", "二项分布图解", "X ~ B(n,p)"),
        ("牛顿三大运动定律", "牛顿三大运动定律图解", "ΣF = ma"),
    ]
    titles = set()

    for index, (focus, expected_title, expected_label) in enumerate(cases, start=1):
        brief = visual("图文结合学习图")
        brief.focus_point = focus
        brief.source_points = [focus]
        svg = render_topic_visual_svg(brief, index, "zh-CN")

        assert_svg_contract(svg, expected_title, index)
        assert expected_label in svg
        titles.add(expected_title)

    assert len(titles) == len(cases)


def test_chinese_math_svg_router_does_not_treat_graph_as_ph():
    brief = visual("图文结合学习图")
    brief.focus_point = "函数图像"
    brief.source_points = ["Graphs of functions; sketching curves defined by simple equations."]

    svg = render_topic_visual_svg(brief, 1, "zh-CN")

    assert_svg_contract(svg, "函数图像图解", 1)
    assert "pH scale" not in svg


def test_chinese_math_svg_router_prefers_specific_routes_before_calculus_words():
    cases = [
        ("直线方程与梯度", "Equation of a straight line and gradient", "y=mx+c"),
        (
            "不定积分是微分的反向过程",
            "Indefinite integration as the reverse of differentiation",
            "积分是求导的反向",
        ),
        (
            "圆的切线与法线方程",
            "Coordinate geometry of a circle tangent and normal",
            "(x-a)²+(y-b)²=r²",
        ),
    ]

    for index, (focus, source, expected_label) in enumerate(cases, start=1):
        brief = visual("图文结合学习图")
        brief.focus_point = focus
        brief.source_points = [source]
        svg = render_topic_visual_svg(brief, index, "zh-CN")

        assert expected_label in svg
        assert "切线斜率" not in svg


def test_integral_area_svgs_distinguish_definite_area_from_signed_x_axis_region():
    definite = visual("calculus graph and area annotation")
    definite.focus_point = "Interpretation of the definite integral as the area under a curve."
    definite.source_points = [definite.focus_point]
    signed_region = visual("calculus graph and area annotation")
    signed_region.focus_point = (
        "Integration to determine the area of a region between a curve and the x-axis. "
        "To include regions wholly below the x-axis, ie knowledge that the integral will "
        "give a negative value."
    )
    signed_region.source_points = [signed_region.focus_point]

    definite_svg = render_topic_visual_svg(definite, 47, "en")
    signed_svg = render_topic_visual_svg(signed_region, 49, "en")

    assert "area from a to b" in definite_svg
    assert "below x-axis" in signed_svg
    assert "signed area" in signed_svg
    assert svg_structure_fingerprint(definite_svg) != svg_structure_fingerprint(signed_svg)


def test_chinese_kinematics_svg_avoids_bilingual_slash_label():
    brief = visual("图文结合学习图")
    brief.focus_point = "运动学图像绘制与解读"
    brief.source_points = ["velocity-time and displacement-time graphs"]

    svg = render_topic_visual_svg(brief, 1, "zh-CN")

    assert "速度-时间图与位移-时间图" in svg
    assert "v-t / s-t" not in svg


def test_chinese_math_svg_router_uses_focus_specific_titles_at_scale():
    focuses = [
        "根式化简",
        "指数运算",
        "二次函数判别式",
        "配方法",
        "因式定理",
        "线性与二次不等式",
        "代数除法与余式定理",
        "函数图像变换",
        "联立方程交点",
        "导数记号",
        "第一原理求导",
        "二阶导数判断",
        "定积分面积",
        "梯形法则",
        "等比数列求和",
        "二项分布",
        "牛顿三大运动定律",
    ]
    titles = []

    for index, focus in enumerate(focuses, start=1):
        brief = visual("图文结合学习图")
        brief.focus_point = focus
        brief.source_points = [focus]
        svg = render_topic_visual_svg(brief, index, "zh-CN")
        titles.append(re.search(r"<title[^>]*>(.*?)</title>", svg).group(1))

    assert len(set(titles)) >= 15
    assert "代数关系图" not in titles
    assert "微分与切线图" not in titles


def test_direct_svg_helpers_escape_titles_and_keep_core_labels():
    assert "Accounting records flow" in render_accounting_flow_svg(1, "en")
    assert "Verification and reconciliation" in render_reconciliation_svg(1, "en")
    assert "Financial statement layout" in render_financial_statement_svg(1, "en")
    assert "Demand and supply market diagram" in render_market_svg(1, "en")
    assert "Force and motion diagram" in render_force_svg(1, "en")
    assert "Common gas tests observation chart" in render_gas_tests_svg(1, "en")
    assert "Number sense" in render_number_svg(1)
    assert "Algebra links symbols to shapes" in render_algebra_svg(1)
    assert "Data becomes evidence" in render_statistics_svg(1)
    assert "Particle model" in render_particles_svg(1)
    assert "Right triangle diagram" in render_triangle_svg(1)
    assert "Distance-time graph" in render_motion_svg(1)
    assert "Rate of reaction graph" in render_rate_svg(1)
    assert "Reaction energy profile" in render_energy_svg(1)
    assert "pH scale" in render_ph_svg(1)
    assert "hydrocarbon model" in render_organic_svg(1)
    assert "Chromatography diagram" in render_analysis_svg(1)
    assert "bonding model" in render_bonding_svg(1)
    assert "Economic choice flow" in render_flow_svg(
        1,
        "Economic choice flow",
        ("Choice", "Scarce resources", "Opportunity cost", "Outcome"),
        "#111111",
        "#222222",
    )

    escaped = render_concept_fallback_svg(2, "A&B <topic>")
    assert "A&amp;B &lt;topic&gt;" in escaped
    assert "Key idea" in escaped
    assert html_escape('"quoted" & <tag>') == "&quot;quoted&quot; &amp; &lt;tag&gt;"


def test_market_demand_and_supply_shift_svgs_are_distinct():
    demand_svg = render_market_svg(1, "en", "demand")
    supply_svg = render_market_svg(2, "en", "supply")

    assert "Demand increases" in demand_svg
    assert "Supply increases" in supply_svg
    assert svg_structure_fingerprint(demand_svg) != svg_structure_fingerprint(supply_svg)


def test_market_curve_svgs_cover_distinct_economics_variants():
    cases = [
        ("Shifts of a demand curve", "demand", "Demand increases"),
        ("Shifts of a supply curve", "supply", "Supply increases"),
        ("Market equilibrium", "equilibrium", "Equilibrium"),
        ("Market disequilibrium", "disequilibrium", "Shortage"),
        ("Determination of foreign exchange rate", "foreign_exchange", "Exchange rate"),
    ]
    fingerprints = []

    for index, (text, expected_variant, expected_label) in enumerate(cases, start=1):
        variant = market_variant_from_text(text)
        svg = render_market_svg(index, "en", variant)
        fingerprints.append(svg_structure_fingerprint(svg))

        assert variant == expected_variant
        assert expected_label in svg

    assert len(set(fingerprints)) == len(cases)


def test_accounting_statement_variant_svgs_use_distinct_professional_layouts():
    variants = [
        ("Partnership accounts", ("Profit share", "Current accounts", "Capital", "Drawings")),
        (
            "Manufacturing account",
            ("Raw materials", "Prime cost", "Factory overheads", "Production cost"),
        ),
        (
            "Club and non-profit accounts",
            ("Receipts", "Payments", "Subscriptions", "Accumulated fund"),
        ),
        ("Limited company statements", ("Revenue", "Expenses", "Equity", "Retained earnings")),
    ]

    fingerprints = []
    for index, (title, labels) in enumerate(variants, start=1):
        svg = render_accounting_statement_variant_svg(index, title, labels)
        assert_svg_contract(svg, title, index)
        fingerprints.append(svg_structure_fingerprint(svg))

    assert len(set(fingerprints)) == len(variants)


def test_svg_text_wrapping_helpers_are_deterministic():
    assert wrap_words("alpha beta gamma", max_chars=10) == ["alpha beta", "gamma"]
    assert wrap_words("abcdefghijkl", max_chars=5) == ["abcde"]
    assert wrap_words("alpha/beta gamma", max_chars=10) == ["alpha /", "beta gamma"]
    assert wrap_words("", max_chars=5) == [""]

    text = svg_multiline_text(
        "alpha beta gamma delta",
        x=10,
        y=20,
        max_chars=11,
        line_height=12,
        size=14,
        weight=600,
        fill="#000000",
    )

    assert '<text x="10" y="20" fill="#000000" font-size="14" font-weight="600">' in text
    assert '<tspan x="10" dy="0">alpha beta</tspan>' in text
    assert '<tspan x="10" dy="12">gamma delta</tspan>' in text

    truncated = svg_multiline_text(
        "one two three four five six seven eight nine ten",
        x=10,
        y=20,
        max_chars=8,
        line_height=12,
    )

    assert truncated.count("<tspan") == 3
    assert "seven" not in truncated
