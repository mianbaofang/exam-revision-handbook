import pytest
from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide
from intl_exam_guide.planning.visual_routing import (
    build_visual_brief,
    choose_provider_for_visual,
    choose_visual_type,
)


def route(title: str, points: list[str], subject: str | None) -> tuple[str, str, str]:
    return choose_visual_type(Topic(title=title, points=points), points, subject)


def guide() -> TopicGuide:
    return TopicGuide(
        topic_title="Topic",
        essence="Explain the idea.",
        analogy="Use a simple analogy.",
        mini_worked_example="Apply it once.",
        worked_solution_steps=["Read", "Plan", "Answer", "Check"],
        pitfall="Avoid guessing.",
        checklist=["Explain", "Apply", "Check"],
        diagram_brief="Show the flow.",
    )


def options(language: str = "en", provider: str = "prompt-queue") -> GuideRunOptions:
    return GuideRunOptions(
        requested_subject="Accounting",
        image_provider=provider,
        explanation_style="friendly",
        output_language=language,
        image_model="reviewed-model",
    )


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_build_visual_brief_returns_none_for_text_only_generic_topic():
    brief = build_visual_brief(
        Topic(title="Portfolio review", points=["creative annotation"]),
        guide(),
        options(),
        "Art and Design",
    )

    assert brief is None


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_physics_visual_routing_draws_only_central_diagrams():
    assert (
        route(
            "1.1 - use the following units",
            ["kilogram (kg), metre (m), newton (N)."],
            "Physics",
        )[1]
        == "text-ok"
    )
    assert (
        route(
            "5.5 - know and use the relationship between pressure, force and area",
            ["pressure = force / area"],
            "Physics",
        )[1]
        == "text-ok"
    )
    assert (
        route(
            "7.19 - know that fission produces daughter nuclei and neutrons",
            ["number of neutrons"],
            "Physics",
        )[1]
        == "text-ok"
    )
    assert (
        route(
            "1.21 - describe the forces acting on falling objects",
            ["weight and air resistance"],
            "Physics",
        )[1]
        == "text-ok"
    )
    visual_type, complexity, _ = route(
        "1.17 - know and use the relationship between unbalanced force, mass and acceleration",
        ["force = mass x acceleration"],
        "Physics",
    )
    assert visual_type == "mechanics force or collision diagram"
    assert complexity == "svg-basic"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_chemistry_visual_routing_avoids_unsafe_local_svg():
    assert (
        route(
            "3.1.3 - The Periodic Table",
            ["Group properties and periodic trends."],
            "Chemistry",
        )[1]
        == "text-ok"
    )
    assert (
        route(
            "3.4.1 - Purity and chromatography",
            ["Use chromatography to separate mixtures."],
            "Chemistry",
        )[1]
        == "text-ok"
    )
    assert (
        route(
            "3.6.3 - The mole concept",
            ["Amount of substance and moles."],
            "Chemistry",
        )[1]
        == "text-ok"
    )
    visual_type, complexity, _ = route(
        "3.9.1 - Exothermic and endothermic reactions",
        ["Energy profile diagrams."],
        "Chemistry",
    )
    assert visual_type == "reaction energy profile diagram"
    assert complexity == "svg-basic"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_build_visual_brief_keeps_english_visible_fields():
    brief = build_visual_brief(
        Topic(
            title="3.1.8 - Prepare accounting records from source documents",
            points=["Use source documents, books of prime entry and ledger accounts."],
        ),
        guide(),
        options(),
        "Accounting",
    )

    assert brief is not None
    assert brief.focus_point == "Use source documents, books of prime entry and ledger accounts"
    assert brief.visual_type == "source-document to book-of-prime-entry and ledger flow diagram"
    assert brief.trigger == "accounting records need a precise source-to-ledger flow diagram"
    assert brief.image_provider == "kroki"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_professional_diagram_routes_use_kroki_between_local_svg_and_infographic():
    brief = build_visual_brief(
        Topic(
            title="2.1 - Organisation structure",
            points=["Organisation structure, hierarchy, chain of command and span of control."],
        ),
        guide(),
        options(),
        "Business",
    )

    assert brief is not None
    assert brief.complexity == "svg-basic"
    assert brief.image_provider == "kroki"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_exact_curve_and_axis_visuals_stay_local_svg_not_kroki():
    brief = build_visual_brief(
        Topic(
            title="P1.4 - Integration",
            points=["Interpretation of the definite integral as the area under a curve."],
        ),
        guide(),
        options(),
        "Mathematics",
    )

    assert brief is not None
    assert brief.complexity == "svg-basic"
    assert brief.image_provider == "deterministic-svg"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_collision_momentum_uses_local_svg_not_external_infographic():
    brief = build_visual_brief(
        Topic(
            title="M1.4 - Momentum and impulse",
            points=[
                "The principle of conservation of momentum applied to two particles in direct collision."
            ],
        ),
        guide(),
        options(),
        "Mathematics",
    )

    assert brief is not None
    assert brief.visual_type == "mechanics before-after collision diagram"
    assert brief.complexity == "svg-basic"
    assert brief.image_provider == "deterministic-svg"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_function_transformations_use_local_svg_not_external_infographic():
    brief = build_visual_brief(
        Topic(
            title="P1.1 - Algebra",
            points=["Knowledge of the effect of simple transformations on the graph of y = f (x)."],
        ),
        guide(),
        options(),
        "Mathematics",
    )

    assert brief is not None
    assert brief.visual_type == "function graph transformation visual"
    assert brief.complexity == "svg-basic"
    assert brief.image_provider == "deterministic-svg"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_triangle_area_formula_does_not_duplicate_sine_rule_visual():
    visual_type, complexity, _ = route(
        "PP1.2 - Trigonometry: The area of a triangle in the form ab Csin2",
        ["The area of a triangle in the form ab Csin2."],
        "Mathematics",
    )

    assert visual_type == "text explanation with no custom visual"
    assert complexity == "text-ok"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_motion_graph_gradient_area_uses_motion_graph_svg():
    visual_type, complexity, _ = route(
        "M1.1 - Motion in a straight line with constant acceleration",
        ["Use of gradients and area under graphs to solve problems."],
        "Mathematics",
    )

    assert visual_type == "motion graph visual"
    assert complexity == "svg-basic"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_term_support_language_keeps_visual_fields_in_english():
    brief = build_visual_brief(
        Topic(
            title="3.1.8 - Prepare accounting records from source documents",
            points=["Use source documents, books of prime entry and ledger accounts."],
        ),
        guide(),
        options(language="zh-CN"),
        "Accounting",
    )

    assert brief is not None
    assert brief.focus_point == "Use source documents, books of prime entry and ledger accounts"
    assert brief.visual_type == "source-document to book-of-prime-entry and ledger flow diagram"
    assert brief.trigger == "accounting records need a precise source-to-ledger flow diagram"
    assert brief.image_provider == "kroki"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_records_route_only_draws_true_recording_processes():
    list_cases = [
        ("3.1.3 - Source documents are", ["Source documents are invoices and credit notes."]),
        (
            "3.1.4 - Books of prime entry are",
            ["Books of prime entry include sales and purchases journals."],
        ),
        (
            "3.3.11 - Record the sale of a non-current asset in the books of account",
            ["Record disposals in the books of account."],
        ),
    ]

    for title, points in list_cases:
        visual_type, complexity, _ = route(title, points, "Accounting")
        assert complexity == "text-ok"
        assert visual_type == "text explanation with optional table"

    visual_type, complexity, _ = route(
        "3.2.9 - How to correct errors in double entry records",
        ["Correct errors in accounting records and explain suspense accounts."],
        "Accounting",
    )

    assert complexity == "svg-basic"
    assert visual_type == "error correction and suspense account flow"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_verification_routes_do_not_collapse_into_bank_reconciliation():
    cases = [
        (
            "3.2.1 - Verification of the double entry records",
            [
                "Verification techniques are trial balance, ledger control accounts and bank reconciliation statements."
            ],
            "text explanation with optional table",
            "text-ok",
        ),
        (
            "3.2.5 - Prepare, understand and interpret trade payables and trade receivables ledger control accounts",
            ["Prepare and interpret trade payables and trade receivables ledger control accounts."],
            "control account reconciliation diagram",
            "svg-basic",
        ),
        (
            "3.2.10 - The effect of errors on profit calculations",
            [
                "The effect of errors includes the adjustment of profit or loss following the correction of errors."
            ],
            "error correction and suspense account flow",
            "svg-basic",
        ),
        (
            "3.4.8 - Prepare and comment on income statements and statements of financial position from a trial balance",
            [
                "Prepare statements from a trial balance including adjustments from accounting concepts."
            ],
            "text explanation with optional accounting table",
            "text-ok",
        ),
        (
            "3.4.15 - Prepare and comment on the internal financial statements of limited liability companies",
            ["Prepare financial statements for limited liability companies."],
            "limited company financial statement layout",
            "svg-basic",
        ),
    ]

    for title, points, expected_type, expected_complexity in cases:
        visual_type, complexity, _ = route(title, points, "Accounting")
        assert visual_type == expected_type
        assert complexity == expected_complexity


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_image_prompt_keeps_board_and_course_packaging_out_of_model_prompt():
    brief = build_visual_brief(
        Topic(
            title="OxfordAQA 9660 P1.3 - Trigonometry",
            points=[
                "OxfordAQA International AS Level students should understand "
                "sine, cosine and tangent functions",
            ],
        ),
        guide(),
        options(),
        "Mathematics",
    )

    assert brief is not None
    assert "Topic: mathematics:" in brief.prompt
    assert "sine, cosine and tangent functions" in brief.prompt
    assert "institutional logos" in brief.prompt
    for leaked in ["Oxford", "AQA", "International", "AS Level", "9660"]:
        assert leaked not in brief.prompt


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_term_support_image_prompt_is_english_content_only_not_source_metadata():
    brief = build_visual_brief(
        Topic(
            title="OxfordAQA 9660 P1.3 - Trigonometry",
            points=[
                "OxfordAQA International AS unit P1 sine, cosine and tangent functions",
            ],
        ),
        guide(),
        options(language="zh-CN"),
        "Mathematics",
    )

    assert brief is not None
    assert "Topic: mathematics:" in brief.prompt
    assert "institutional logos" in brief.prompt
    assert "sine" in brief.prompt
    assert "制作一张中文学习信息图" not in brief.prompt
    for leaked in ["Oxford", "AQA", "International", "9660", "国际课程", "官方英文来源"]:
        assert leaked not in brief.prompt


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_choose_provider_for_visual_covers_svg_custom_and_passthrough_routes():
    assert choose_provider_for_visual("svg-basic", options()) == "llm-svg"
    assert (
        choose_provider_for_visual("infographic", options(provider="custom"))
        == "custom:reviewed-model"
    )
    assert (
        choose_provider_for_visual("infographic", options(provider="reviewed-assets"))
        == "reviewed-assets"
    )


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_visual_routing_does_not_treat_ordinary_set_as_venn():
    visual_type, complexity, trigger = route(
        "P1.4 - Integration: Questions involving regions partially above and below the x-axis",
        ["Questions involving regions partially above and below the x-axis will not be set."],
        "Mathematics",
    )

    assert "Venn" not in visual_type
    assert "set notation" not in visual_type
    assert complexity == "text-ok"
    assert "exclusions" in trigger


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_math_visual_routing_avoids_duplicate_intersection_svg_for_adjacent_methods():
    visual_type, complexity, _ = route(
        "P1.1 - Algebra: Geometrical interpretation of algebraic solution of equations",
        [
            "Geometrical interpretation of algebraic solution of equations and use of intersection points of graphs of functions to solve equations."
        ],
        "Mathematics",
    )

    assert complexity == "text-ok"
    assert visual_type == "text explanation with no custom visual"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_visual_routes_cover_ratio_and_default_text_branch():
    ratio_type, ratio_complexity, _ = route(
        "Ratio analysis", ["liquidity profitability"], "Accounting"
    )
    default_type, default_complexity, _ = route(
        "Ethics overview", ["stewardship and responsibility"], "Accounting"
    )

    assert ratio_complexity == "text-ok"
    assert ratio_type == "text explanation with optional table"
    assert default_complexity == "text-ok"
    assert default_type == "text explanation with optional table"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_visual_routes_do_not_overdraw_adjustments_or_ratios():
    depreciation_type, depreciation_complexity, _ = route(
        "2.5 - Depreciation",
        ["Record accounting entries for depreciation and non-current assets."],
        "Accounting",
    )
    ratio_type, ratio_complexity, _ = route(
        "4.4 - The calculation and interpretation of accounting ratios",
        ["Calculate ratios using financial statements and interpret liquidity and profitability."],
        "Accounting",
    )

    assert depreciation_complexity == "text-ok"
    assert depreciation_type == "text explanation with optional table"
    assert ratio_complexity == "text-ok"
    assert ratio_type == "text explanation with optional table"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_bank_reconciliation_prefers_reconciliation_over_ledger_flow():
    visual_type, complexity, _ = route(
        "3.3 - Bank reconciliation",
        ["cash book bank statement unpresented cheques and outstanding lodgements"],
        "Accounting",
    )

    assert complexity == "svg-basic"
    assert "reconciliation" in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_depreciation_reducing_balance_is_not_reconciliation():
    visual_type, complexity, _ = route(
        "2.5 - Depreciation",
        ["Distinguish between straight line and reducing balance methods of depreciation."],
        "Accounting",
    )

    assert complexity == "text-ok"
    assert "reconciliation" not in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_statement_variants_use_topic_specific_professional_svgs():
    visual_type, complexity, trigger = route(
        "5.4 - Company financial statements",
        ["Prepare financial statements for companies."],
        "Accounting",
    )

    assert complexity == "svg-basic"
    assert visual_type == "limited company financial statement layout"
    assert "statement layout detail" in trigger


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_accounting_manufacturer_statements_do_not_route_to_records_flow():
    visual_type, complexity, _ = route(
        "4.5 - Financial statements of a manufacturer",
        ["Prepare financial statements and manufacturing accounts from books of account."],
        "Accounting",
    )

    assert complexity == "svg-basic"
    assert visual_type == "manufacturing account cost-flow layout"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_business_production_does_not_match_product_marketing_mix_substring():
    visual_type, complexity, _ = route(
        "Production processes",
        ["Methods of production and efficiency."],
        "Business",
    )

    assert complexity == "svg-basic"
    assert "operations flow" in visual_type
    assert "marketing mix" not in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_business_product_word_alone_does_not_force_marketing_mix_visual():
    visual_type, complexity, _ = route(
        "Good customer services",
        ["product knowledge and customer service expectations"],
        "Business",
    )

    assert complexity == "text-ok"
    assert "marketing mix" not in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_business_visual_routes_are_not_swallowed_by_economics_text_branch():
    cases = [
        (
            "Break-even analysis",
            ["fixed costs variable costs revenue break-even chart"],
            "break-even",
        ),
        (
            "Cash-flow forecasting",
            ["cash inflows outflows opening closing balance forecast"],
            "cash-flow",
        ),
        (
            "Marketing mix",
            ["product price place promotion"],
            "marketing mix",
        ),
        (
            "Stakeholders",
            ["main stakeholders of businesses and their objectives"],
            "stakeholder",
        ),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Business")

        assert complexity == "svg-basic"
        assert expected in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_history_visual_routes_cover_common_humanities_structures():
    cases = [
        (
            "Causes of the First World War",
            ["cause factor chain: alliances, arms race, imperial tension"],
            "cause",
        ),
        (
            "Chronology of reform",
            ["timeline period sequence"],
            "timeline",
        ),
        (
            "Using historical sources",
            ["source evidence interpretation reliability"],
            "source evidence",
        ),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "History")

        assert complexity == "svg-basic"
        assert expected in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_history_visual_routes_do_not_draw_every_cause_word():
    visual_type, complexity, _ = route(
        "What caused the First World War?",
        ["What caused the First World War?"],
        "History",
    )

    assert complexity == "text-ok"
    assert "history organizer" in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_economics_visual_routes_only_draw_named_curve_topics():
    visual_type, complexity, _ = route(
        "Market equilibrium",
        ["demand supply price equilibrium"],
        "Economics",
    )

    assert complexity == "svg-basic"
    assert "demand-supply" in visual_type

    for title, points in [
        ("Movements along a demand curve", ["movements along a demand curve"]),
        ("Movements along a supply curve", ["movements along a supply curve"]),
        (
            "Consequences of changes in foreign exchange rate",
            ["consequences of changes in foreign exchange rate"],
        ),
        ("Macroeconomics", ["government inflation trade exchange imports exports"]),
        ("Production resources", ["land labour capital enterprise factors"]),
        ("Business finance", ["business revenue profit cash"]),
    ]:
        visual_type, complexity, _ = route(title, points, "Economics")

        assert complexity == "text-ok"
        assert visual_type == "text explanation with optional mini case"

    default_type, default_complexity, _ = route(
        "Economics concepts",
        ["consumer welfare incentives"],
        "Economics",
    )
    assert default_complexity == "text-ok"
    assert default_type == "text explanation with optional mini case"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_economics_visual_routes_do_not_draw_every_market_word():
    text_only_cases = [
        (
            "Shifts of a PPC",
            [
                "causes and consequences of shifts of a PPC in terms of an economy's growth",
                "market forces of demand and supply, market equilibrium and disequilibrium",
            ],
        ),
        ("Price changes", ["causes and consequences of price changes"]),
        ("Calculation of PED", ["calculation of price elasticity of demand"]),
        ("Market failure", ["causes and consequences of market failure"]),
        ("Taxation", ["fiscal policy taxation and government aims"]),
        ("Causes of inflation", ["causes and consequences of inflation"]),
        ("Wage determination", ["reasons for differences in wages"]),
    ]

    for title, points in text_only_cases:
        visual_type, complexity, _ = route(title, points, "Economics")

        assert complexity == "text-ok"
        assert visual_type == "text explanation with optional mini case"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_chemistry_visual_routes_cover_structure_calculation_and_no_match_paths():
    bonding_type, bonding_complexity, _ = route(
        "Bonding", ["ionic covalent metallic structure"], "Chemistry"
    )
    calculation_type, calculation_complexity, _ = route(
        "Electrolysis", ["electrolysis moles concentration"], "Chemistry"
    )
    fallback_type, fallback_complexity, _ = route(
        "Chemistry overview", ["safe laboratory conduct"], "Chemistry"
    )

    assert bonding_complexity == "infographic"
    assert "bonding and structure" in bonding_type
    assert calculation_complexity == "infographic"
    assert "chemistry process" in calculation_type
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_chemistry_visual_routes_do_not_overmatch_generic_gas_or_structure_words():
    states_type, states_complexity, _ = route(
        "3.1.1 - Solids, liquids and gases",
        [
            "The three states of matter are solid, liquid and gas; particles are arranged differently."
        ],
        "Chemistry",
    )
    bonding_type, bonding_complexity, _ = route(
        "3.2.1 - Chemical bonds",
        ["Ionic, covalent and metallic bonding and structure."],
        "Chemistry",
    )
    reactivity_type, reactivity_complexity, _ = route(
        "3.3.1.1 - The reactivity series",
        ["Reactivity of metals with water, oxygen and dilute acids."],
        "Chemistry",
    )

    assert states_complexity == "svg-basic"
    assert "particle model" in states_type
    assert bonding_complexity == "infographic"
    assert "bonding and structure" in bonding_type
    assert reactivity_complexity == "infographic"
    assert "chemistry process" in reactivity_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_mathematics_visual_routes_cover_remaining_infographic_branches():
    cases = [
        ("Construction", ["locus bearings constructions"], "geometry construction"),
        ("Matrices", ["vectors matrices transformations"], "matrix"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "infographic"
        assert expected in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_mathematics_visual_routes_use_svg_only_for_exact_diagrams():
    cases = [
        ("Calculus", ["calculus tangent gradient"], "calculus graph"),
        ("Circle", ["equation of a circle"], "geometry"),
    ]

    for title, points, expected in cases:
        visual_type, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "svg-basic"
        assert expected in visual_type


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_as_math_symbolic_topics_do_not_get_unnecessary_visuals():
    cases = [
        (
            "P1.1 - Algebra: Use and manipulation of surds",
            [
                "Use and manipulation of surds. To include simplification and rationalisation of the denominator of a fraction."
            ],
        ),
        (
            "P1.1 - Algebra: Application of the Factor Theorem",
            ["Application of the Factor Theorem and Remainder Theorem."],
        ),
        (
            "P1.5 - Sequences and series: Arithmetic series",
            ["Arithmetic series."],
        ),
    ]

    for title, points in cases:
        _, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "text-ok"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_as_math_trigonometry_is_not_misrouted_as_calculus_tangent():
    visual_type, complexity, trigger = route(
        "PP1.2 - Trigonometry: Sine, cosine and tangent functions",
        ["Sine, cosine and tangent functions."],
        "Mathematics",
    )

    assert complexity == "svg-basic"
    assert "trigonometry" in visual_type
    assert "calculus" not in visual_type
    assert "angle" in trigger or "curve" in trigger


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_scope_exclusion_notes_are_text_only_visuals():
    visual_type, complexity, trigger = route(
        "M1.4 - Momentum: Knowledge of Newton's law of restitution is not required",
        ["Knowledge of Newton's law of restitution is not required."],
        "Mathematics",
    )

    assert complexity == "text-ok"
    assert visual_type == "scope note for text explanation"
    assert "exclusions" in trigger


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_as_math_formula_topics_stay_text_only_after_visual_tightening():
    cases = [
        (
            "P1.2 - Coordinate geometry: Conditions for two straight lines to be parallel or perpendicular to each other",
            ["Conditions for two straight lines to be parallel or perpendicular to each other."],
        ),
        (
            "PP1.2 - Trigonometry: Degree and radian measure",
            ["Degree and radian measure."],
        ),
        (
            "S1.3 - Bernoulli and binomial distributions: Mean and variance of a Bernoulli",
            ["Mean and variance of a Bernoulli distribution."],
        ),
        (
            "S1.2 - Discrete random variables: The number of possible outcomes will be finite",
            ["The number of possible outcomes will be finite."],
        ),
        (
            "S1.1 - Further probability: Assigning probabilities to events using relative frequencies or equally likely outcomes",
            [
                "Assigning probabilities to events using relative frequencies or equally likely outcomes."
            ],
        ),
        (
            "S1.3 - Bernoulli and binomial distributions: Calculation of probabilities using formula and tables",
            ["Calculation of probabilities using formula and tables."],
        ),
        (
            "M1.3 - Forces and Newton's Laws: Normal Reactions",
            ["Normal Reactions."],
        ),
        (
            "M1.4 - Momentum and impulse: Concept of momentum",
            ["Concept of momentum."],
        ),
    ]

    for title, points in cases:
        _, complexity, _ = route(title, points, "Mathematics")

        assert complexity == "text-ok"


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_as_math_keeps_svg_for_graphs_forces_and_collisions():
    cases = [
        (
            "PP1.2 - Trigonometry: Their graphs, symmetries and periodicity",
            ["Their graphs, symmetries and periodicity."],
            "svg-basic",
        ),
        (
            "M1.3 - Forces and Newton's Laws: Newton's three laws of motion",
            ["Newton's three laws of motion."],
            "svg-basic",
        ),
        (
            "M1.4 - Momentum and impulse: Direct impact with a fixed surface",
            ["Direct impact with a fixed surface."],
            "svg-basic",
        ),
        (
            "M1.4 - Momentum and impulse: The principle of conservation of momentum applied to two particles",
            ["The principle of conservation of momentum applied to two particles."],
            "svg-basic",
        ),
    ]

    for title, points, expected_complexity in cases:
        visual_type, complexity, trigger = route(title, points, "Mathematics")

        assert complexity == expected_complexity
        if expected_complexity == "infographic":
            assert "collision" in visual_type
            assert "generic SVG" in trigger


@pytest.mark.skip(
    reason="Deprecated: Python no longer uses keyword routing. LLM Writer judges visuals in Phase 2."
)
def test_generic_and_unmatched_routes_cover_data_and_text_only_paths():
    data_type, data_complexity, _ = route("Data handling", ["tables graphs measurement"], None)
    maths_data_type, maths_data_complexity, _ = route(
        "Data handling", ["data tables measurements"], "Mathematics"
    )
    fallback_type, fallback_complexity, _ = route(
        "Creative portfolio", ["annotation process"], None
    )

    assert data_complexity == "svg-basic"
    assert data_type == "data table and graph interpretation visual"
    assert maths_data_complexity == "svg-basic"
    assert maths_data_type == "statistics chart visual"
    assert fallback_complexity == "text-ok"
    assert fallback_type == "text explanation with concept map only"
