from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "write_concept_explanations_from_jobs.py"
SCRIPT_SPEC = spec_from_file_location("write_concept_explanations_from_jobs", SCRIPT_PATH)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
SCRIPT_MODULE = module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)


def test_momentum_restricted_to_straight_line_does_not_use_coordinate_geometry():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.4 - Momentum and impulse (Restricted to motion in a straight line): Concept of momentum",
            "source_points": ["Concept of momentum. Momentum = mv"],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(entry["explanations"]).lower()
    assert "p = mv" in text
    assert "midpoint" not in text
    assert "intercepts" not in text


def test_newtons_laws_in_straight_line_do_not_use_coordinate_geometry():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.3 - Forces and Newton's Laws: Newton's three laws of motion",
            "source_points": [
                "Newton's three laws of motion. Restricted to dynamics in a straight line with constant forces."
            ],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "resultant force" in text or "f = ma" in text
    assert "coordinates" not in text
    assert "midpoint" not in text
    assert "intercepts" not in text


def test_newton_force_units_keep_distinct_concept_explanations():
    topics = [
        (
            "M1.3 - Forces and Newton's Laws: Force of gravity",
            "Force of gravity. W = mg",
        ),
        (
            "M1.3 - Forces and Newton's Laws: Tensions in strings and rods, thrusts in rods",
            "Tensions in strings and rods, thrusts in rods.",
        ),
        (
            "M1.3 - Forces and Newton's Laws: Normal Reactions",
            "Normal Reactions.",
        ),
    ]

    first_explanations = []
    for title, point in topics:
        entry = SCRIPT_MODULE.write_entry(
            {
                "topic_title": title,
                "source_points": [point],
                "output_language": "en",
                "subject_pack": "mathematics",
            }
        )
        first_explanations.append(entry["explanations"][0])

    assert len(set(first_explanations)) == len(first_explanations)
    assert any("weight" in value.lower() for value in first_explanations)
    assert any("tension" in value.lower() for value in first_explanations)
    assert any("normal reaction" in value.lower() for value in first_explanations)


def test_competitive_market_process_explanation_is_not_generic_economics_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.4.5 - The competitive market process",
            "source_points": [
                "Firms do not just compete on price but competition will also lead firms to strive to improve products, reduce costs and improve the quality of the service provided."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            *entry["worked_solution_steps"],
            entry["pitfall"],
            *entry["explanations"],
        ]
    ).lower()
    assert "non-price competition" in text
    assert "improve product quality" in text
    assert "real market situation" not in text
    assert "set of nudges" not in text


def test_generic_economics_concept_explanation_uses_source_point_not_empty_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.1.1 - Economic activity",
            "source_points": [
                "Needs and wants",
                "The central purpose of economic activity",
                "The key economic decisions",
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    first = entry["explanations"][0].lower()

    assert "economic activity is about needs and wants" in first
    assert "names the exact idea" not in first
    assert "3.1.1.1" not in first


def test_accounting_business_topic_does_not_trigger_trigonometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "1.1 - Types of business organisation",
            "source_points": [
                "a) Explain the characteristics of:",
                "public sector organisations",
                "private sector organisations",
                "sole traders",
                "partnerships.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "angles to side ratios" not in text
    assert "periodic graph values" not in text
    assert "public sector organisations" in text


def test_term_support_language_still_writes_english_concept_body():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 Algebra: Quadratic functions",
            "source_points": ["Sketch and interpret quadratic graphs."],
            "output_language": "zh-CN",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    )

    assert "quadratic" in text.lower()
    assert not any("\u4e00" <= char <= "\u9fff" for char in text)


def test_generic_math_entry_avoids_template_phrases_and_ocr_noise():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion: Knowledge and use of constant acceleration equations",
            "source_points": ["2t as vtt= 2"],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    )
    lower = text.lower()

    assert "2t as vtt" not in text
    assert "s = ut + 1/2 at^2" in text
    assert "specific syllabus idea" not in lower
    assert "relationship named in this source point" not in lower
    assert "define the idea and apply only" not in lower


def test_linear_and_quadratic_inequalities_explanation_is_conceptual_not_filler():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 - Algebra: Solution of linear and quadratic inequalities",
            "source_points": ["Solution of linear and quadratic inequalities."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "x-values" in text
    assert "satisfy" in text
    assert "sign" in text
    assert "unit's main idea" not in text
    assert "signpost" not in text


def test_trapezium_rule_explanation_is_not_generic_graph_features():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.4 - Integration: Approximation of the area under a curve using the trapezium rule",
            "source_points": ["Approximation of the area under a curve using the trapezium rule."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "trapezium rule" in text
    assert "estimate" in text or "approximation" in text
    assert "root, gradient, asymptote, vertex" not in text


def test_trig_graph_explanation_uses_periodicity_not_generic_roots():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "PP1.2 - Trigonometry: Their graphs, symmetries and periodicity",
            "source_points": ["Their graphs, symmetries and periodicity."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "period" in text or "symmet" in text
    assert "root, gradient, asymptote, vertex" not in text


def test_notation_source_shell_is_not_written_as_student_phrase():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.5 - Sequences and series: Students should be familiar with the notation |r|<1 in this context",
            "source_points": ["Students should be familiar with the notation |r|<1 in this context."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join([entry["essence"], *entry["explanations"]]).lower()

    assert "students should be familiar" not in text
    assert "so state what the relationship means" not in text
    assert "|r|<1" in text


def test_vertical_motion_under_gravity_explanation_uses_gravity_model():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Vertical motion under gravity",
            "source_points": ["Vertical motion under gravity."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "gravity" in text
    assert "g" in text
    assert "direction" in text or "sign" in text
    assert "condition, notation, or relationship" not in text


def test_binomial_expansion_explanation_is_algebraic_not_probability_model():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.5 - Sequences and series: The binomial expansion of (1 + x)^n for positive integer n",
            "source_points": ["The binomial expansion of (1 + x)^n for positive integer n."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "binomial coefficients" in text
    assert "expand" in text
    assert "uncertain outcomes" not in text


def test_variable_acceleration_explanation_uses_calculus_not_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.2 - Motion in a straight line with variable acceleration: Relationship between displacement, velocity and acceleration",
            "source_points": ["Relationship between displacement, velocity and acceleration."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "ds/dt" in text
    assert "dv/dt" in text
    assert "differentiat" in text
    assert "condition, notation, or relationship" not in text


def test_constant_motion_quantities_do_not_use_variable_acceleration_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Displacement, speed, velocity, acceleration",
            "source_points": ["Displacement, speed, velocity, acceleration."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "speed = distance/time" in text
    assert "velocity = displacement/time" in text
    assert "ds/dt" not in text
    assert "dv/dt" not in text


def test_generic_math_fallback_avoids_old_condition_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.9 - Algebra: Specialist notation boundary",
            "source_points": ["Specialist notation boundary."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            *entry["explanations"],
        ]
    ).lower()

    assert "condition, notation, or relationship" not in text
    assert "calculate, sketch, solve, or interpret" not in text
    assert "specialist notation boundary" in text


def test_math_fallback_does_not_emit_repeated_product_review_template_phrases():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 - Algebra: Simple algebraic division",
            "source_points": ["Simple algebraic division."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "named mathematical condition" not in text
    assert "question tells you whether" not in text
    assert "calculation, sketch, proof, or interpretation" not in text
    assert "matching formula, graph feature, definition, or rule" not in text
    assert "given data or condition" not in text
    assert "actual condition, sign, unit, or notation" not in text


def test_business_topic_does_not_trigger_math_or_physics_templates():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "1.2 - Stakeholders",
            "source_points": [
                "Main stakeholders of businesses.",
                "Objectives of stakeholders and how they can conflict.",
            ],
            "output_language": "en",
            "subject_pack": "business",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "business" in text
    assert "stakeholder" in text
    assert "angles to side ratios" not in text
    assert "periodic graph values" not in text
    assert "two skaters" not in text
    assert "masses and velocities" not in text
    assert "momentum equation" not in text


def test_accounting_depreciation_does_not_trigger_coordinate_geometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "2.5 - Depreciation",
            "source_points": [
                "a) Explain the causes of depreciation.",
                "b) Distinguish between straight line and reducing balance methods of depreciation.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "gradient, intercepts, coordinates" not in text
    assert "causes of depreciation" in text


def test_same_named_accounting_units_keep_section_identity():
    first = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "2.5 - Depreciation",
            "source_points": ["a) Explain the causes of depreciation."],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )
    second = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "5.2 - Depreciation",
            "source_points": ["a) Explain the causes of depreciation."],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    assert first["explanations"] != second["explanations"]
    assert "2.5 - Depreciation" in first["explanations"][0]
    assert "5.2 - Depreciation" in second["explanations"][0]


def test_accounting_wrapped_source_points_are_merged_before_writing():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "5.3 - Irrecoverable debts",
            "source_points": [
                "a) Explain why it is necessary to provide a provision for",
                "irrecoverable debts.",
                "b) Distinguish between an irrecoverable debt and a provision for",
                "an irrecoverable debt.",
            ],
            "output_language": "en",
            "subject_pack": "accounting",
        }
    )

    text = " ".join(entry["explanations"]).lower()

    assert "provide a provision for irrecoverable debts" in text
    assert "provide a provision for and" not in text


def test_competition_dynamics_explanation_is_distinct_from_basic_competitive_process():
    basic = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.1.4.5 - The competitive market process",
            "source_points": [
                "Firms do not just compete on price but competition will also lead firms to strive to improve products, reduce costs and improve the quality of the service provided."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )
    dynamic = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "3.3.3.8 - The dynamics of competition and competitive market processes",
            "source_points": [
                "Short-run and long-run benefits which may result from competition and competitive market processes."
            ],
            "output_language": "en",
            "subject_pack": "economics",
        }
    )

    assert basic["explanations"] != dynamic["explanations"]
    dynamic_text = " ".join(dynamic["explanations"]).lower()
    assert "short-run" in dynamic_text
    assert "long-run" in dynamic_text


def test_kinematics_graph_explanation_is_motion_specific_not_coordinate_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Sketching and interpreting kinematics graphs",
            "source_points": ["Sketching and interpreting kinematics graphs."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "velocity-time" in text
    assert "displacement-time" in text
    assert "axes" in text
    assert "shape" in text
    assert "acceleration" in text
    assert "coordinates, distance, and midpoint" not in text
    assert "root, gradient, asymptote, vertex" not in text


def test_intersection_graph_topics_have_distinct_mastery_requirements():
    broad = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 - Algebra: Geometrical interpretation of algebraic solution of equations and use of intersection points of graphs of functions to solve equations",
            "source_points": ["Geometrical interpretation of algebraic solution of equations and use of intersection points of graphs of functions to solve equations."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )
    two_way = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.1 - Algebra: Interpreting the solutions of equations as the intersection points of graphs and vice versa",
            "source_points": ["Interpreting the solutions of equations as the intersection points of graphs and vice versa."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    assert broad["explanations"][:2] != two_way["explanations"][:2]
    assert "number of algebraic roots" in " ".join(broad["explanations"]).lower()
    assert "reversible" in " ".join(two_way["explanations"]).lower()


def test_kinematics_graph_topics_have_distinct_mastery_requirements():
    sketch = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Sketching and interpreting kinematics graphs",
            "source_points": ["Sketching and interpreting kinematics graphs."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )
    gradient_area = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Use of gradients and area under graphs to solve problems",
            "source_points": ["Use of gradients and area under graphs to solve problems."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    assert sketch["explanations"][:2] != gradient_area["explanations"][:2]
    assert "motion story" in " ".join(sketch["explanations"]).lower()
    assert "area under velocity-time" in " ".join(gradient_area["explanations"]).lower()


def test_trigonometry_tangent_does_not_trigger_differentiation_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "PP1.2 - Trigonometry: Sine, cosine and tangent functions",
            "source_points": ["Sine, cosine and tangent functions."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["explanations"],
        ]
    ).lower()

    assert "angle inputs" in text or "angle measures" in text
    assert "ratio" in text
    assert "exact local rate of change" not in text
    assert "speed camera" not in text


def test_differentiation_tangent_does_not_trigger_trigonometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "P1.3 - Differentiation: The derivative of f(x) as the gradient of the tangent",
            "source_points": ["The derivative of f(x) as the gradient of the tangent to the graph."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join([entry["essence"], entry["analogy"], *entry["explanations"]]).lower()

    assert "rate of change" in text or "gradient" in text
    assert "angles to ratios" not in text
    assert "side ratios" not in text


def test_trigonometry_subtopics_have_distinct_mastery_text():
    cases = [
        (
            "PP1.2 - Trigonometry: The sine and cosine rules",
            "The sine and cosine rules.",
        ),
        (
            "PP1.2 - Trigonometry: The area of a triangle in the form 1/2 ab sin C",
            "The area of a triangle in the form 1/2 ab sin C.",
        ),
        (
            "PP1.2 - Trigonometry: Degree and radian measure",
            "Degree and radian measure.",
        ),
        (
            "PP1.2 - Trigonometry: Knowledge and use of tan theta = sin theta / cos theta; and sin^2 theta + cos^2 theta = 1",
            "Knowledge and use of tan theta = sin theta / cos theta; and sin^2 theta + cos^2 theta = 1.",
        ),
    ]

    entries = [
        SCRIPT_MODULE.write_entry(
            {
                "topic_title": title,
                "source_points": [point],
                "output_language": "en",
                "subject_pack": "mathematics",
            }
        )
        for title, point in cases
    ]

    first_explanations = [entry["explanations"][0] for entry in entries]
    assert len(set(first_explanations)) == len(first_explanations)
    assert any("sine rule" in value.lower() for value in first_explanations)
    assert any("1/2 ab sin c" in value.lower() for value in first_explanations)
    assert any("radian" in value.lower() for value in first_explanations)
    assert any("identity" in value.lower() or "sin^2" in value.lower() for value in first_explanations)


def test_circle_tangent_pitfall_does_not_use_differentiation_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "PP1.1 - Circle: The equation of the tangent and normal at a given point to a circle",
            "source_points": ["The equation of the tangent and normal at a given point to a circle."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join([entry["essence"], entry["pitfall"], *entry["explanations"]]).lower()

    assert "circle" in text
    assert "coordinates" in text or "radius" in text
    assert "rate of change" not in text
    assert "stationary-point" not in text


def test_constant_acceleration_equations_do_not_trigger_coordinate_geometry_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.1 - Motion in a straight line with constant acceleration: Knowledge and use of constant acceleration equations",
            "source_points": ["Knowledge and use of constant acceleration equations."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["worked_solution_steps"],
            *entry["explanations"],
        ]
    ).lower()

    assert "s, u, v, a, and t" in text
    assert "constant acceleration" in text
    assert "map grid" not in text
    assert "coordinates, gradients, distances" not in text


def test_fixed_surface_collision_does_not_trigger_coordinate_perpendicular_template():
    entry = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.4 - Momentum and impulse (Restricted to motion in a straight line): Direct impact with a fixed surface",
            "source_points": [
                "Direct impact with a fixed surface. Restricted to particles which are moving perpendicular to a fixed smooth surface."
            ],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    text = " ".join(
        [
            entry["essence"],
            entry["analogy"],
            entry["mini_worked_example"],
            entry["pitfall"],
            *entry["explanations"],
        ]
    ).lower()

    assert "rebound" in text or "fixed smooth surface" in text
    assert "momentum" in text or "velocity" in text
    assert "coordinates, gradients" not in text
    assert "map grid" not in text


def test_variable_acceleration_subtopics_have_distinct_mastery_requirements():
    relationship = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.2 - Motion in a straight line with variable acceleration: Relationship between displacement, velocity and acceleration",
            "source_points": ["Relationship between displacement, velocity and acceleration."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )
    application = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.2 - Motion in a straight line with variable acceleration: Application of calculus techniques will be required to solve problems",
            "source_points": ["Application of calculus techniques will be required to solve problems."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )
    boundary = SCRIPT_MODULE.write_entry(
        {
            "topic_title": "M1.2 - Motion in a straight line with variable acceleration: Problems will be restricted to the calculus in the AS unit P1",
            "source_points": ["Problems will be restricted to the calculus in the AS unit P1."],
            "output_language": "en",
            "subject_pack": "mathematics",
        }
    )

    first_lines = {relationship["explanations"][0], application["explanations"][0], boundary["explanations"][0]}
    assert len(first_lines) == 3
    assert "v = ds/dt" in " ".join(relationship["explanations"]).lower()
    assert "s -> v -> a" in " ".join(application["explanations"]).lower()
    assert "as pure 1" in " ".join(boundary["explanations"]).lower()
