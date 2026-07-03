from intl_exam_guide.models import SourceSnippet, Topic
from intl_exam_guide.planning.practice_generator import (
    build_practice_item,
    choose_command_word,
    choose_difficulty,
    concrete_example,
    concrete_example_zh,
    contextualize_question,
)


def combined_text(parts: tuple[str, list[str], list[str], list[str]]) -> str:
    question, frame, steps, checkpoints = parts
    return " ".join([question, *frame, *steps, *checkpoints]).lower()


def test_build_practice_item_uses_requested_style_and_source_snippets():
    topic = Topic(
        title="3.1.2 - Sources and recording of data",
        points=["Source documents are purchase invoices and sales invoices."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Source documents include purchase invoices and sales invoices.",
                matched_term="Source documents",
            )
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=0,
        qualification_type="international_gcse",
        explanation_style="detective",
        output_language="en",
        subject_area="Accounting",
    )

    combined = " ".join([item.question, *item.public_solution_steps]).lower()
    assert item.command_word == "state"
    assert item.source_snippets == topic.source_snippets
    assert item.question.startswith("Case file:")
    assert "purchase invoice" in combined or "sales invoice" in combined
    assert "ledger" in combined


def test_chinese_practice_focus_falls_back_from_untranslated_formula_detail():
    topic = Topic(
        title="P1.1 - Algebra: Solution of linear and quadratic inequalities",
        points=[
            "Solution of linear and quadratic inequalities.",
            "eg 2 2xx + /greaterthanorequalangled6",
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=1,
        qualification_type="international_as_a_level",
        explanation_style="friendly",
        output_language="zh-CN",
        subject_area="Mathematics",
    )

    assert item.focus_point == "一次与二次不等式求解"
    assert "本节核心主题" not in item.focus_point


def test_accounting_and_chemistry_examples_route_to_subject_specific_branches():
    accounting_question, _, accounting_steps, _ = concrete_example(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    accounting_text = " ".join([accounting_question, *accounting_steps]).lower()

    chemistry_question, _, chemistry_steps, _ = concrete_example(
        Topic(
            title="3.6.4 - Molar concentrations",
            points=["Concentration is related to number of moles and volume of solution."],
        ),
        "Concentration is related to number of moles and volume of solution.",
        0,
        "Chemistry",
    )
    chemistry_text = " ".join([chemistry_question, *chemistry_steps]).lower()

    assert "ledger" in accounting_text
    assert "ratio 2:5" not in accounting_text
    assert "concentration" in chemistry_text
    assert "mol/dm3" in chemistry_text
    assert "ledger" not in chemistry_text


def test_physics_examples_route_to_physics_not_math_fallbacks():
    cases = [
        (
            "5.5 - pressure, force and area",
            "pressure = force / area",
            ["pressure", "400 pa"],
        ),
        (
            "5.21 - pressure and Kelvin temperature of a fixed mass of gas",
            "gas at constant volume",
            ["constant volume", "pressure increases"],
        ),
        (
            "7.19 - fission of U-235",
            "number of neutrons",
            ["fission", "daughter nuclei"],
        ),
    ]

    for title, focus, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, 0, "Physics"))
        assert "right-angled triangle" not in text
        assert "drink is mixed" not in text
        for expected in expected_terms:
            assert expected in text


def test_mathematics_algebra_example_is_not_generic():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="A2 - Algebra and equations", points=["Solve linear equations."]),
        "Solve linear equations.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "solve 3(x - 2) + 5 = 20" in combined
    assert "x = 7" in combined
    assert "memorised phrase" not in combined


def test_mathematics_trapezium_rule_example_uses_approximation_not_exact_integration():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.5 - Integration: Approximation of the area under a curve using the trapezium rule",
            points=["Approximation of the area under a curve using the trapezium rule."],
        ),
        "Approximation of the area under a curve using the trapezium rule.",
        1,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "trapezium rule" in combined
    assert "estimate" in combined or "approximation" in combined
    assert "antiderivative" not in combined
    assert "integral from" not in combined


def test_mathematics_inequality_example_solves_an_inequality():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.1 - Algebra: Solution of linear and quadratic inequalities",
            points=["Solution of linear and quadratic inequalities."],
        ),
        "Solution of linear and quadratic inequalities.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "inequality" in combined
    assert "<" in combined or ">" in combined
    assert "interval" in combined or "number line" in combined
    assert "solve x^2 - 5x + 6 = 0" not in combined


def test_mathematics_binomial_expansion_example_is_not_sequence_or_distribution():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.5 - Sequences and series: The binomial expansion of (1 + x)^n for positive integer n",
            points=["The binomial expansion of (1 + x)^n for positive integer n."],
        ),
        "The binomial expansion of (1 + x)^n for positive integer n.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "expand" in combined
    assert "(1" in combined
    assert "arithmetic sequence" not in combined
    assert "x ~ b" not in combined


def test_mathematics_trigonometric_equation_example_solves_interval():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="PP1.2 - Trigonometry: Solution of simple trigonometric equations in a given interval",
            points=["Solution of simple trigonometric equations in a given interval of degrees or radians."],
        ),
        "Solution of simple trigonometric equations in a given interval of degrees or radians.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "solve" in combined
    assert "interval" in combined
    assert "convert pi/3" not in combined
    assert "pi radians = 180" not in combined


def test_mathematics_sine_cosine_rule_example_is_triangle_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="PP1.2 - Trigonometry: The sine and cosine rules",
            points=["The sine and cosine rules."],
        ),
        "The sine and cosine rules.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "triangle" in combined
    assert "cosine rule" in combined or "sine rule" in combined
    assert "pi/3" not in combined
    assert "radians = 180" not in combined


def test_mathematics_triangle_area_example_is_not_radian_conversion():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="PP1.2 - Trigonometry: Area of a triangle",
            points=["Area of a triangle using 1/2 ab sin C."],
        ),
        "Area of a triangle using 1/2 ab sin C.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "area" in combined
    assert "1/2" in combined
    assert "sin" in combined
    assert "pi/3" not in combined


def test_mathematics_trig_graph_example_is_not_quadratic_vertex():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="PP1.2 - Trigonometry: Their graphs, symmetries and periodicity",
            points=["Their graphs, symmetries and periodicity."],
        ),
        "Their graphs, symmetries and periodicity.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "sin" in combined or "cos" in combined or "tan" in combined
    assert "period" in combined or "symmetry" in combined
    assert "vertex" not in combined
    assert "line of symmetry x = 3" not in combined


def test_mathematics_simultaneous_equations_example_is_not_generic_quadratic():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.1 - Algebra: Simultaneous equations",
            points=["Solution of simultaneous equations."],
        ),
        "Solution of simultaneous equations.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "simultaneous" in combined
    assert "x^2 - x - 6" in combined
    assert "x^2 - 5x + 6 = 0" not in combined


def test_mathematics_unknown_topic_fallback_does_not_import_quadratic_roots():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.9 - Algebra: Specialist notation boundary",
            points=["Specialist notation boundary."],
        ),
        "Specialist notation boundary.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "specialist notation boundary" in combined
    assert "x^2 - 5x + 6" not in combined
    assert "both roots" not in combined


def test_mathematics_geometric_ratio_notation_example_uses_convergence_condition():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="P1.5 - Sequences and series: Notation |r|<1 in this context",
            points=["the notation |r|<1 in this context"],
        ),
        "the notation |r|<1 in this context",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "|r|<1" in combined.replace(" ", "")
    assert "convergent" in combined or "converges" in combined
    assert "arithmetic sequence" not in combined


def test_mathematics_variable_acceleration_example_uses_calculus_not_suvat():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="M1.2 - Motion in a straight line with variable acceleration",
            points=["Use differentiation and integration with displacement, velocity and acceleration."],
        ),
        "Use differentiation and integration with displacement, velocity and acceleration.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "differentiate" in combined or "integrate" in combined
    assert "s(t)" in combined or "v(t)" in combined
    assert "v = u + at" not in combined


def test_mathematics_force_of_gravity_example_uses_weight_formula():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="M1.3 - Forces and Newton's Laws: Force of gravity",
            points=["Force of gravity. W = mg"],
        ),
        "Force of gravity. W = mg",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "w = mg" in combined
    assert "weight" in combined
    assert "resultant force" not in combined


def test_mathematics_vertical_motion_under_gravity_uses_g_and_direction():
    question, frame, steps, checkpoints = concrete_example(
        Topic(
            title="M1.1 - Motion in a straight line with constant acceleration: Vertical motion under gravity",
            points=["Vertical motion under gravity."],
        ),
        "Vertical motion under gravity.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "g" in combined
    assert "upwards" in combined or "downwards" in combined
    assert "9.8" in combined


def test_biology_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Cell membranes", points=["Osmosis across cell membranes."]),
        "Osmosis across cell membranes.",
        0,
        "Biology",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "water moves out" in combined
    assert "osmosis" in combined
    assert "ledger" not in combined


def test_economics_example_is_subject_specific():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Basic economic problem", points=["Scarcity creates economic choices."]),
        "Scarcity creates economic choices.",
        0,
        "Economics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "scarce" in combined
    assert "choose" in combined or "choice" in combined
    assert "ledger" not in combined


def test_generic_example_fallback_remains_exam_focused():
    question, frame, steps, checkpoints = concrete_example(
        Topic(title="Unmapped topic", points=["Use the named concept accurately."]),
        "Use the named concept accurately.",
        0,
        "Unmapped Subject",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "using only the syllabus point" in combined
    assert "relationship or boundary" in combined
    assert "without borrowing another subject's template" in combined


def test_mathematics_examples_cover_major_strands():
    cases = [
        ("N1 - Number", "Ratio and percentage calculations.", 1, ["scale 1:25,000", "1.5 km"]),
        ("N2 - Bounds", "Rounding and bounds.", 1, ["lower bound", "12.35 kg"]),
        ("A3 - Functions", "Functions and graphs.", 1, ["gradient", "y-intercept"]),
        ("A4 - Sequences", "Sequences and nth term.", 0, ["4n + 1", "20th term"]),
        ("G1 - Angles", "Angles around a point.", 1, ["360 degrees", "135 degrees"]),
        ("S1 - Probability", "Probability of outcomes.", 1, ["even outcomes", "1/2"]),
        ("S2 - Statistics", "Mean and range.", 0, ["mean", "range"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Mathematics"))
        for expected in expected_terms:
            assert expected in text


def test_mathematics_specialist_fallbacks_stay_concrete_for_as_topics():
    cases = [
        ("P1.3 - Differentiation", "The derivative as the gradient of the tangent.", "切线"),
        ("PP1.3 - Exponential and logarithms", "Logarithms and the laws of logarithms.", "log"),
        ("S1.2 - Discrete random variables", "Mean and variance of a discrete random variable.", "概率"),
        ("M1.3 - Forces and Newton's Laws", "Newton's Second Law F = ma.", "力"),
    ]

    for title, focus, expected in cases:
        question, frame, steps, checkpoints = concrete_example_zh(
            Topic(title=title, points=[focus]),
            focus,
            0,
            "Mathematics",
        )
        combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

        assert "完成一道原创练习" not in combined
        assert "先找关键信息" not in combined
        assert expected in combined


def test_a_level_math_momentum_examples_do_not_route_to_newton_force_template():
    momentum_topic = Topic(
        title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): The principle of conservation of momentum applied to two particles",
        points=["The principle of conservation of momentum applied to two particles."],
    )
    direct_impact_topic = Topic(
        title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): Direct impact with a fixed surface",
        points=["Direct impact with a fixed surface. Restricted to particles which are moving perpendicular to a fixed smooth surface."],
    )
    impulse_topic = Topic(
        title="M1.4 - Momentum and impulse (Restricted to motion in a straight line): Impulse",
        points=["Impulse. Impulse = change in momentum"],
    )

    zh_momentum = combined_text(
        concrete_example_zh(momentum_topic, momentum_topic.points[0], 0, "Mathematics")
    )
    zh_direct_impact = combined_text(
        concrete_example_zh(direct_impact_topic, direct_impact_topic.points[0], 0, "Mathematics")
    )
    en_impulse = combined_text(concrete_example(impulse_topic, impulse_topic.points[0], 0, "Mathematics"))

    assert "合力" not in zh_momentum
    assert "牛顿第二定律" not in zh_momentum
    assert "动量守恒" in zh_momentum
    assert "8/3" in zh_momentum
    assert "固定墙" in zh_direct_impact
    assert "动量变化" in zh_direct_impact
    assert "resultant force" not in en_impulse
    assert "impulse = -7 n s" in en_impulse


def test_a_level_math_rational_terms_do_not_misroute_to_ratio_examples():
    surd_topic = Topic(
        title="P1.1 - Algebra: Use and manipulation of surds",
        points=[
            "Use and manipulation of surds. To include simplification and rationalisation of the denominator of a fraction."
        ],
    )
    index_topic = Topic(
        title="P1.1 - Algebra: Laws of indices for all rational exponents",
        points=["Laws of indices for all rational exponents."],
    )

    zh_surd = combined_text(
        concrete_example_zh(surd_topic, surd_topic.points[0], 0, "Mathematics")
    )
    zh_indices = combined_text(
        concrete_example_zh(index_topic, index_topic.points[0], 0, "Mathematics")
    )
    en_surd = combined_text(concrete_example(surd_topic, surd_topic.points[0], 0, "Mathematics"))

    assert "果汁" not in zh_surd
    assert "果汁" not in zh_indices
    assert "juice" not in en_surd.lower()
    assert "sqrt(72)" in zh_surd
    assert "a^(3/2)" in zh_indices
    assert "sqrt(72)" in en_surd


def test_a_level_math_pure_algebra_examples_match_focus():
    cases = [
        (
            "P1.1 - Algebra: Quadratic functions and their graphs",
            "Quadratic functions and their graphs. To include reference to the vertex and line of symmetry of the graph.",
            ["顶点", "对称轴", "(3,2)"],
        ),
        (
            "P1.1 - Algebra: The discriminant of a quadratic function",
            "The discriminant of a quadratic function. To include the conditions for equal roots, for distinct real roots and for no real roots",
            ["判别式", "没有实根"],
        ),
        (
            "P1.1 - Algebra: Factorisation of quadratic polynomials",
            "Factorisation of quadratic polynomials. eg factorisation of 2x2 + x −6",
            ["因式分解", "(2x-3)(x+2)"],
        ),
        (
            "P1.1 - Algebra: Completing the square",
            "Completing the square. eg x2 + 6x−1 = (x+3)2−10;",
            ["配方", "(x+3)^2 - 10"],
        ),
    ]

    for title, focus, expected_terms in cases:
        text = combined_text(concrete_example_zh(Topic(title=title, points=[focus]), focus, 0, "Mathematics"))
        assert "果汁" not in text
        for expected in expected_terms:
            assert expected in text


def test_chemistry_examples_cover_visual_and_calculation_branches():
    cases = [
        ("Nanoparticles", "Nanoparticles and surface area.", 0, ["surface area to volume ratio", "catalyst"]),
        ("Carbon structures", "Diamond graphite graphene structure and bonding of carbon.", 1, ["graphite", "conduct electricity"]),
        ("States", "States of matter and diffusion.", 1, ["melting", "liquid water"]),
        ("Atomic particles", "Atomic proton neutron electron.", 1, ["2+ charge", "electrons"]),
        ("Moles", "Moles mass conservation.", 0, ["magnesium oxide", "4.0 g"]),
        ("Analysis", "Gas tests.", 1, ["limewater", "carbon dioxide"]),
        ("Acids", "Acid base alkali salt pH.", 1, ["neutralises", "pH rises"]),
        ("Rates", "Rate equilibrium reversible reaction.", 0, ["collision theory", "reaction rate"]),
        ("Energy", "Exothermic endothermic energy.", 1, ["endothermic", "absorbed"]),
        ("Carbonates", "Carbonates decompose.", 1, ["thermal decomposition", "copper oxide"]),
        ("Organic", "Hydrocarbon polymer crude.", 1, ["poly(ethene)", "polymerisation"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Chemistry"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_accounting_examples_cover_statement_and_verification_branches():
    cases = [
        ("Verification", "Trial balance and bank reconciliation.", 1, ["bank reconciliation", "external bank evidence"]),
        ("Errors", "Trial balance correction of errors.", 0, ["trial balance", "error of principle"]),
        ("Adjustments", "Depreciation and irrecoverable receivables.", 1, ["annual depreciation", "$1,000"]),
        ("Statements", "Financial statements income statement.", 1, ["gross profit", "$3,800"]),
        ("Partnership", "Partnership financial statements.", 0, ["appropriation account", "profit sharing"]),
        ("Ratios", "Ratio profitability liquidity.", 1, ["current ratio", "1.5 : 1"]),
        ("Fallback", "Accounting ethics note.", 0, ["accounting idea", "business scenario"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Accounting"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_economics_examples_cover_core_topic_branches():
    cases = [
        ("Specialisation", "Specialisation and division of labour.", 1, ["specialisation", "factory"]),
        ("Factors", "Factors of production land capital enterprise.", 1, ["vans are capital", "founder is enterprise"]),
        ("Opportunity cost", "Opportunity cost and resource allocation.", 1, ["clinic", "sports centre"]),
        ("Sectors", "Primary secondary tertiary sectors.", 0, ["wheat farm", "service"]),
        ("Market", "Demand supply price equilibrium.", 1, ["supply curve shifts left", "quantity is likely to fall"]),
        ("Elasticity", "Elasticity calculation.", 1, ["ped = 40% / -20%", "price elastic"]),
        ("Costs", "Cost revenue profit production.", 0, ["total revenue = $8 x 200", "profit = $500"]),
        ("Policy", "Government inflation growth employment.", 1, ["taxes", "inflationary pressure"]),
        ("International trade", "Import export globalisation.", 0, ["appreciation", "imports become cheaper"]),
        ("Banking", "Money bank financial interest.", 1, ["interest rates", "borrowing becomes more expensive"]),
        ("Fallback", "Consumer behaviour.", 0, ["economic agent", "likely outcome"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Economics"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_economics_competitive_market_process_uses_non_price_competition_context():
    text = combined_text(
        concrete_example(
            Topic(
                title="3.1.4.5 - The competitive market process",
                points=[
                    "Firms do not just compete on price but competition will also lead firms to strive to improve products, reduce costs and improve the quality of the service provided."
                ],
            ),
            "Firms do not just compete on price but",
            1,
            "Economics",
        )
    ).lower()

    assert "non-price competition" in text
    assert "improve products" in text
    assert "oranges" not in text
    assert "supply curve shifts left" not in text


def test_contextualize_question_does_not_expose_incomplete_syllabus_fragments():
    question = "Two cafes compete through faster service and a loyalty app."

    assert (
        contextualize_question(question, "Firms do not just compete on price but", "en")
        == question
    )


def test_economics_competition_dynamics_uses_short_run_long_run_context():
    text = combined_text(
        concrete_example(
            Topic(
                title="3.3.3.8 - The dynamics of competition and competitive market processes",
                points=[
                    "Short-run and long-run benefits which may result from competition and competitive market processes."
                ],
            ),
            "Short-run and long-run benefits which may result",
            1,
            "Economics",
        )
    ).lower()

    assert "short run" in text or "short-run" in text
    assert "long run" in text or "long-run" in text
    assert "consumer" in text
    assert "oranges" not in text


def test_history_option_codes_do_not_route_to_mathematics_templates():
    topic = Topic(
        title="A1 - The origins and course of the First World War, 1905-18",
        points=["The origins and course of the First World War, 1905-18"],
    )

    question, frame, steps, checkpoints = concrete_example(topic, topic.points[0], 0, "History")
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "first world war" in combined
    assert "cause" in combined or "change" in combined or "source" in combined
    assert "solve 3(" not in combined
    assert "x = 7" not in combined


def test_history_question_topics_use_history_structure_not_generic_template():
    topic = Topic(
        title="6 - What caused the First World War?",
        points=["What caused the First World War?"],
    )

    question, frame, steps, checkpoints = concrete_example(topic, topic.points[0], 0, "History")
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "first world war" in combined
    assert "short-term cause" in combined or "longer-term cause" in combined or "two causes" in combined
    assert "definition, one application, and one check" not in combined


def test_business_examples_are_business_specific_not_generic_template():
    topic = Topic(
        title="3.1.4 - Stakeholders",
        points=["Main stakeholders of businesses.", "Objectives of stakeholders."],
    )

    question, frame, steps, checkpoints = concrete_example(topic, topic.points[0], 0, "Business")
    combined = " ".join([question, *frame, *steps, *checkpoints]).lower()

    assert "stakeholder" in combined
    assert "business" in combined
    assert "definition, one application, and one check" not in combined


def test_biology_examples_cover_molecule_and_genetics_branches():
    cases = [
        ("Water", "Water solvent dipole transport.", 0, ["polar solvent", "transport"]),
        ("Carbohydrate", "Carbohydrate starch glucose.", 0, ["glucose is a monosaccharide", "starch is a polysaccharide"]),
        ("Lipid", "Lipid triglyceride ester fatty acid glycerol.", 0, ["triglyceride", "ester bonds"]),
        ("DNA", "DNA RNA replication nucleotide gene genetic.", 0, ["complementary base", "genetic information"]),
        ("Fallback", "Ecology adaptation.", 0, ["cause-and-effect", "biological structure"]),
    ]

    for title, focus, number, expected_terms in cases:
        text = combined_text(concrete_example(Topic(title=title, points=[focus]), focus, number, "Biology"))
        for expected in expected_terms:
            assert expected.lower() in text


def test_chinese_examples_cover_subject_specific_branches():
    cases = [
        ("Chemistry", Topic(title="Atomic structure", points=["atomic proton neutron electron"]), "atomic proton neutron electron", ["原子序数", "质量数"]),
        ("Chemistry", Topic(title="Acid base", points=["acid base alkali salt pH"]), "acid base alkali salt pH", ["化学解释题", "结论"]),
        ("Economics", Topic(title="Demand and supply", points=["demand supply market price"]), "demand supply market price", ["需求曲线", "均衡"]),
        ("Accounting", Topic(title="Bank reconciliation", points=["trial balance bank reconciliation"]), "trial balance bank reconciliation", ["银行调节表", "现金簿"]),
        ("Mathematics", Topic(title="G1 - Geometry", points=["triangle geometry"]), "triangle geometry", ["直角三角形", "斜边"]),
        ("Unmapped", Topic(title="Unknown", points=["source detail"]), "source detail", ["只围绕", "来源点"]),
    ]

    for subject, topic, focus, expected_terms in cases:
        text = combined_text(concrete_example_zh(topic, focus, 0, subject))
        for expected in expected_terms:
            assert expected in text


def test_chinese_mathematics_ratio_example_uses_chinese_units_and_symbols():
    question, frame, steps, checkpoints = concrete_example_zh(
        Topic(title="N1 - Ratio", points=["Ratio and percentage calculations."]),
        "Ratio and percentage calculations.",
        0,
        "Mathematics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints])

    assert "350 毫升" in combined
    assert "ml" not in combined.lower()
    assert "140 / 2" not in combined
    assert "5 x 70" not in combined


def test_command_words_and_difficulty_rotate_by_level_and_language():
    assert [choose_command_word(i, "international_gcse") for i in range(4)] == [
        "state",
        "describe",
        "explain",
        "suggest",
    ]
    assert [choose_command_word(i, "international_as_a_level") for i in range(4)] == [
        "explain",
        "analyse",
        "compare",
        "evaluate",
    ]
    assert [choose_command_word(i, "international_gcse", "zh-CN") for i in range(4)] == [
        "写出",
        "描述",
        "解释",
        "提出",
    ]
    assert [choose_difficulty(i) for i in range(3)] == ["core", "standard", "stretch"]
    assert [choose_difficulty(i, "zh-CN") for i in range(3)] == ["基础", "标准", "挑战"]


def test_major_example_branches_have_distinct_even_and_odd_variants():
    cases = [
        ("Mathematics", Topic(title="N1 - Ratio", points=["Ratio and percentage calculations."]), "ratio", ["350 ml", "1.5 km"]),
        ("Mathematics", Topic(title="A3 - Functions", points=["Functions and graphs."]), "function graph", ["x = -3 or x = 3", "y = 11"]),
        ("Mathematics", Topic(title="A4 - Sequences", points=["Sequences and nth term."]), "sequence nth term", ["4n + 1", "31 is in the sequence"]),
        ("Mathematics", Topic(title="G1 - Angles", points=["Angles around a point."]), "angles", ["112 degrees", "135 degrees"]),
        ("Mathematics", Topic(title="S1 - Probability", points=["Probability outcomes."]), "probability", ["blue counters", "even outcomes"]),
        ("Chemistry", Topic(title="Organic", points=["Hydrocarbon polymer crude."]), "hydrocarbon polymer crude", ["co2 and h2o", "poly(ethene)"]),
        ("Accounting", Topic(title="Ratios", points=["Ratio profitability liquidity."]), "ratio profitability liquidity", ["gross profit margin", "current ratio"]),
        ("Economics", Topic(title="Market", points=["Demand supply price equilibrium."]), "demand supply price equilibrium", ["demand shifts to the right", "supply curve shifts left"]),
    ]

    for subject, topic, focus, expected_terms in cases:
        even_text = combined_text(concrete_example(topic, focus, 0, subject))
        odd_text = combined_text(concrete_example(topic, focus, 1, subject))

        assert even_text != odd_text
        assert expected_terms[0].lower() in even_text
        assert expected_terms[1].lower() in odd_text


def test_chinese_practice_example_keeps_student_facing_text_chinese():
    question, frame, steps, checkpoints = concrete_example_zh(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints])

    assert "原始凭证" in combined
    assert "购货发票" in combined
    assert "source document" not in combined.lower()
    assert "purchase invoice" not in combined.lower()


def test_mathematics_kinematics_graph_example_is_not_quadratic_vertex():
    topic = Topic(
        title="M1.1 - Motion in a straight line with constant acceleration: Sketching and interpreting kinematics graphs",
        points=["Sketching and interpreting kinematics graphs."],
    )

    text = combined_text(concrete_example(topic, topic.points[0], 0, "Mathematics"))

    assert "displacement-time graph" in text
    assert "horizontal" in text
    assert "motion story" in text
    assert "vertex" not in text
    assert "(x - 3)^2" not in text


def test_mathematics_intersection_graph_example_solves_intersections():
    topic = Topic(
        title="P1.1 - Algebra: Geometrical interpretation of algebraic solution of equations",
        points=["Use of intersection points of graphs of functions to solve equations."],
    )

    text = combined_text(concrete_example(topic, topic.points[0], 0, "Mathematics"))

    assert "intersection" in text
    assert "repeated root" in text
    assert "graphs touch" in text or "just touch" in text
    assert "vertex" not in text
