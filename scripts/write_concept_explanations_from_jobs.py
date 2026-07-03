from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write conservative source-bound concept explanations from concept_jobs.json."
    )
    parser.add_argument("output_dir", help="Generated guide output directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite concept_explanations.json.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    jobs_path = output_dir / "concepts" / "concept_jobs.json"
    target = output_dir / "concepts" / "concept_explanations.json"
    if not jobs_path.exists():
        raise SystemExit(f"missing concept jobs: {jobs_path}")
    if target.exists() and not args.force:
        raise SystemExit(f"concept explanations already exist: {target}; use --force")

    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    if not isinstance(jobs, list):
        raise SystemExit("concept_jobs.json must contain a list")
    explanations = [write_entry(job) for job in jobs if isinstance(job, dict)]
    target.write_text(json.dumps(explanations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "written": len(explanations), "path": str(target)}, ensure_ascii=False))
    return 0


def write_entry(job: dict[str, object]) -> dict[str, object]:
    topic_title = str(job.get("topic_title") or "")
    source_points = [str(point) for point in job.get("source_points", []) if str(point).strip()]
    subject_pack = str(job.get("subject_pack") or "").lower()
    first_point = clean_point(source_points[0] if source_points else topic_title)
    topic_focus = clean_topic_focus(topic_title)
    # Term-support languages add a glossary only; handbook body prose stays English.
    return write_en_entry(topic_title, topic_focus, first_point, source_points, subject_pack)


def write_en_entry(
    topic_title: str,
    topic_focus: str,
    first_point: str,
    source_points: list[str],
    subject_pack: str,
) -> dict[str, object]:
    lower = " ".join([topic_title, *source_points]).lower()
    concept = en_concept_name(topic_title, topic_focus, first_point, subject_pack)
    relation = en_relationship_sentence(concept, lower, source_points, subject_pack)
    boundary = en_boundary_sentence(concept, lower, source_points, subject_pack)
    steps = en_steps(concept, lower, subject_pack)
    pitfall = en_pitfall(concept, lower, subject_pack)
    return {
        "topic_title": topic_title,
        "essence": en_essence(concept, lower, source_points, subject_pack),
        "analogy": en_analogy(concept, lower, subject_pack),
        "mini_worked_example": en_mini_example(concept, lower, subject_pack),
        "worked_solution_steps": steps,
        "pitfall": pitfall,
        "explanations": [
            en_definition_sentence(concept, lower, source_points, subject_pack),
            relation,
            boundary,
        ],
    }


def write_zh_entry(
    topic_title: str,
    topic_focus: str,
    first_point: str,
    source_points: list[str],
    subject_pack: str,
) -> dict[str, object]:
    concept = topic_focus or first_point
    return {
        "topic_title": topic_title,
        "essence": f"本节核心是把“{concept}”理解成一个明确的概念、关系或边界，而不是背一串关键词。",
        "analogy": f"可以把“{concept}”看成题目里的路标：它告诉你该看哪种关系、该停在哪个范围内。",
        "mini_worked_example": f"遇到本节题目时，先确认题目真正问的是“{concept}”中的哪一条关系，再写计算、解释或判断。",
        "worked_solution_steps": [
            "先圈出题目给出的对象、条件和限制词。",
            f"把这些信息对应到“{concept}”这一课纲点。",
            "写出本节需要的关系、公式、图像特征或判断依据。",
            "最后检查答案有没有越过课纲点给出的范围。",
        ],
        "pitfall": "最常见的失分是只写熟悉词汇，却没有说明本节课纲点要求的具体关系或限制。",
        "explanations": [
            f"“{concept}”是本节要掌握的核心对象，需要能说明它本身表示什么。",
            "它描述的是题目条件之间的关系，或课纲明确限定的适用范围。",
            "它重要是因为本节例题和考试小问都会先要求你识别这个关系，再进行计算、解释或判断。",
        ],
    }


def clean_point(value: str) -> str:
    text = clean_ocr_math_text(re.sub(r"\s+", " ", value).strip())
    action_words = r"(?:understand|identify|explain|describe|state|apply|prepare|calculate|distinguish)"
    text = re.sub(r"^[a-z]\)\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+significance\s+of\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+following\s+accounting\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+causes\s+of\s+(.+)$", r"causes of \1", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of(?:\s+the)?\s*:?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of\s+",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(rf"^{action_words}\s+between\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents will be expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents may be required to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents should be familiar with\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents are expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r"\bStudents should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bLearners should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bCandidates should have an understanding of\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bCandidates should\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = text.lstrip(":;,- ").strip()
    return text.rstrip(".")


def clean_ocr_math_text(value: str) -> str:
    text = value
    text = text.replace("/greaterthanorequalangled", ">=")
    text = re.sub(r"\beg\s+2\s+2xx\s*\+\s*>=\s*6\b", "eg 2x^2 + x >= 6", text)
    text = text.replace(
        "tan sin cosθ θ θ= ; and sinc os 122 +=θθ",
        "tan theta = sin theta / cos theta; and sin^2 theta + cos^2 theta = 1",
    )
    text = re.sub(r"\(1\s*\+\s*x\)\s*n\b", "(1 + x)^n", text)
    text = re.sub(r"\(a\s*\+\s*b\)\s*n\b", "(a + b)^n", text)
    text = text.replace("−± −bb ac a", "completing the square and the quadratic formula")
    text = text.replace("ab Csin2", "1/2 ab sin C")
    text = text.replace("d d y x", "dy/dx")
    text = text.replace("2t as vtt= 2", "s = ut + 1/2 at^2 and v = u + at")
    text = re.sub(r"\bxn\s*\+\s*1\s*=\s*f\s*\(\s*xn\s*\)", "x_(n+1) = f(x_n)", text)
    text = re.sub(r"\bx n\b", "x^n", text)
    text = re.sub(r"\bxn\b", "x^n", text)
    return text


def usable_source_fragments(source_points: list[str]) -> list[str]:
    fragments = []
    for point in source_points:
        cleaned = clean_point(point)
        if cleaned and not is_shell_fragment(cleaned):
            fragments.append(cleaned)
    return merge_wrapped_fragments(fragments)


def merge_wrapped_fragments(points: list[str]) -> list[str]:
    merged: list[str] = []
    for point in points:
        if merged and should_merge_fragment(merged[-1], point):
            merged[-1] = f"{merged[-1]} {point}".strip()
        else:
            merged.append(point)
    return merged


def should_merge_fragment(previous: str, current: str) -> bool:
    prev = previous.strip().lower()
    cur = current.strip()
    if not prev or not cur:
        return False
    if prev.endswith((",", ";", ":")):
        return True
    if prev.split()[-1] in {"and", "or", "for", "of", "the", "in", "to", "with", "capital", "raw", "provision"}:
        return True
    if cur and cur[0].islower() and prev.endswith((" other", "non-current", "books", "open")):
        return True
    return False


def is_shell_fragment(value: str) -> bool:
    lower = value.strip(" .:;").lower()
    if not lower:
        return True
    if lower in {"concepts", "the following accounting"}:
        return True
    return bool(
        re.fullmatch(
            r"(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)(?:\s+of)?",
            lower,
        )
    )


def clean_topic_focus(title: str) -> str:
    focus = title.rsplit(":", 1)[-1].strip() if ":" in title else title.strip()
    focus = re.sub(r"^[A-Z]{0,3}\d+(?:\.\d+)*\s*[-–—]\s*", "", focus).strip()
    focus = clean_point(focus).strip(" .;:")
    if focus.lower().startswith("the notation "):
        focus = "Notation " + focus[len("the notation ") :]
    return re.sub(r"\s+", " ", focus).strip()


def en_concept_name(topic_title: str, topic_focus: str, first_point: str, subject_pack: str) -> str:
    if (
        subject_pack == "accounting"
        and re.match(r"^\d+(?:\.\d+)+\s*-\s+", topic_title.strip())
        and ":" not in topic_title
    ):
        return topic_title.strip().rstrip(".")
    candidate = topic_focus if topic_focus and len(topic_focus) <= 120 else first_point
    candidate = clean_point(candidate).strip(" .;:")
    if candidate.lower().startswith("the notation "):
        candidate = "Notation " + candidate[len("the notation ") :]
    candidate = candidate.rstrip(".")
    return candidate or "this syllabus point"


def en_essence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The dynamics of competition is about how competitive pressure changes firm behaviour and creates different short-run and long-run benefits for consumers and markets."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The competitive market process is about how rivalry pushes firms to compete through price and non-price methods such as better products, lower costs, and improved service."
    if "use of factorisation" in lower:
        return "Use of factorisation is about turning a product form into solvable zero-factor equations."
    if "discriminant of a quadratic" in lower:
        return "The discriminant is about reading the nature of a quadratic equation from b^2 - 4ac before solving it."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "Using algebraic methods here means turning a graph intersection question into an equation, then using the number of real roots to interpret the geometry."
    if "translation of circles" in lower:
        return "Translation of circles is about moving the centre of a circle while keeping its radius unchanged."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "Assigning probabilities here means choosing the right basis: observed relative frequency or counting equally likely outcomes."
    if "inequalit" in lower:
        return "Solving linear and quadratic inequalities means finding the range of x-values that satisfy a condition, using algebra and sign reasoning rather than a single equality answer."
    if is_binomial_expansion_topic(lower):
        return "The binomial expansion is about using binomial coefficients to expand powers such as (1 + x)^n in order."
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return "Calculus techniques in variable-acceleration motion are about choosing differentiation or integration to move between s, v, and a."
    if variable_kind == "as_boundary":
        return "The AS boundary for variable acceleration keeps the mechanics inside the differentiation and integration techniques from Pure 1."
    if variable_kind:
        return "Variable-acceleration motion is about connecting displacement, velocity, and acceleration by differentiation and integration."
    if is_motion_quantity_distinction_topic(lower):
        return "Displacement and velocity are vector quantities, while distance and speed are scalar quantities; the difference changes signs and interpretation."
    if is_motion_quantity_overview_topic(lower):
        return "The basic kinematics quantities describe position change and motion rate: displacement, distance, velocity, speed, and acceleration each answer a different question."
    if "knowledge and use of constant acceleration" in lower or "constant acceleration equation" in lower:
        return "Constant-acceleration equations link displacement, initial velocity, final velocity, acceleration, and time when acceleration is fixed."
    if "vertical motion under gravity" in lower:
        return "Vertical motion under gravity is about using constant acceleration with gravitational acceleration acting downwards."
    if "average speed" in lower:
        return "Average speed measures total distance travelled per unit time, without using direction."
    if subject_pack == "accounting":
        return f"{concept} is about recording, classifying, or checking financial information in the required accounting format."
    if subject_pack == "business":
        return f"{concept} is about how a business decision affects objectives, stakeholders, customers, operations, finance, or people."
    if subject_pack == "economics":
        return f"{concept} is about how economic choices create incentives, constraints, and consequences."
    if subject_pack != "mathematics":
        return f"{concept} is the idea that must be explained through the evidence, condition, or effect named in this unit."
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return "Gradients and areas on kinematics graphs turn visual features into acceleration, velocity, displacement, or distance."
    if kinematics_graph_kind == "sketch_interpret":
        return "Sketching and interpreting kinematics graphs is about matching graph shape and axes to the motion being described."
    if kinematics_graph_kind:
        return "Kinematics graphs are about reading motion from the graph type: gradient and area have different meanings on displacement-time and velocity-time graphs."
    intersection_kind = intersection_graph_topic_kind(lower)
    if intersection_kind == "algebra_to_geometry":
        return "Geometrical interpretation of algebraic solution is about using roots of an equation to decide where graphs meet."
    if intersection_kind == "two_way_interpretation":
        return "Interpreting equation solutions as intersections means moving both ways between algebraic roots and visible crossing points."
    if intersection_kind:
        return "Intersection points of graphs are about turning the meeting point of two curves into simultaneous equations, then interpreting the coordinates."
    if (
        (
            "circle" in lower
            or "coordinate geometry" in lower
            or "midpoint" in lower
            or "perpendicular" in lower
            or ("straight line" in lower and "motion" not in lower)
        )
        and not any(word in lower for word in ["momentum", "impulse", "impact", "collision"])
    ):
        return f"{concept} is about translating geometric facts into coordinates, gradients, equations, or distances."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_essence(trig_kind)
    if any(word in lower for word in ["differentiat", "derivative", "gradient", "tangent"]):
        return f"{concept} is about using gradient as an exact local rate of change."
    if any(word in lower for word in ["integrat", "area", "trapezium"]):
        if "trapezium" in lower:
            return "The trapezium rule is about estimating area under a curve from ordinates and equal-width strips."
        return f"{concept} is about connecting accumulation, area, and the algebra of integration."
    if "exponential" in lower and "graph" in lower:
        return f"{concept} is about recognising how an exponential graph changes, especially its growth/decay shape and asymptote."
    if "graph" in lower or "curve" in lower:
        return f"{concept} is about reading a relationship from its shape, intercepts, gradients, or transformations on a graph."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_essence(trig_kind)
    if any(word in lower for word in ["probability", "binomial", "random variable"]):
        return f"{concept} is about modelling uncertain outcomes with a defined probability rule."
    if any(word in lower for word in ["momentum", "impulse", "impact", "collision"]):
        return f"{concept} tracks motion through mass, velocity, and the change caused by an impact or impulse."
    force_kind = force_topic_kind(lower)
    if force_kind == "gravity":
        return "Force of gravity is about modelling weight as W = mg in the force balance."
    if force_kind == "tension":
        return "Tension and thrust are about how strings and rods transmit pulling or pushing forces in a mechanics model."
    if force_kind == "normal":
        return "Normal reaction is about the contact force perpendicular to a surface."
    if force_kind == "friction":
        return "Friction is about the contact force that opposes motion or impending motion along a surface."
    if force_kind == "connected":
        return "Connected-particle problems are about applying Newton's laws to linked particles that share a constraint."
    if force_kind == "newton":
        return f"{concept} is about connecting resultant force to straight-line motion through Newton's laws."
    return source_bound_definition_sentence(concept, source_points, subject_pack)


def en_definition_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "Competition dynamics describe how firms respond over time to rival pressure, with short-run effects such as price or service changes and long-run effects such as innovation, efficiency, and consumer choice."
    if "competitive market process" in lower or "compete on price" in lower:
        return "Non-price competition means firms try to win customers by improving product quality, reducing costs, or improving service rather than only cutting price."
    if subject_pack in {"accounting", "business", "economics", "history"}:
        return source_bound_definition_sentence(concept, source_points, subject_pack)
    if "use of factorisation" in lower:
        return "Using factorisation to solve means rewriting an expression as factors and then applying the zero-product rule."
    if "discriminant of a quadratic" in lower:
        return "For ax^2 + bx + c = 0, the discriminant b^2 - 4ac tells whether the quadratic has two distinct real roots, one repeated real root, or no real roots."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "Algebraic methods connect coordinate geometry to equations: equal roots, distinct real roots, or no real roots describe how graphs meet."
    if "translation of circles" in lower:
        return "A translated circle has the same radius but a different centre, so only the centre coordinates change in the completed-square equation."
    if "relative frequencies" in lower:
        return "Relative frequency estimates probability by dividing how often an outcome occurs by the total number of trials."
    if "equally likely outcomes" in lower:
        return "Equally likely outcomes allow probability to be found by counting favourable outcomes over all possible outcomes."
    if "inequalit" in lower:
        return "An inequality describes a set of values rather than one value; solving it means preserving the inequality sign correctly and identifying the interval where the statement is true."
    if is_binomial_expansion_topic(lower):
        return "For positive integer n, the binomial expansion rewrites (1 + x)^n as a finite sum with coefficients from Pascal's triangle or the binomial coefficient formula."
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return "When acceleration varies with time, calculus supplies the model: differentiate s(t) to get v(t), differentiate v(t) to get a(t), and integrate in the reverse direction."
    if variable_kind == "as_boundary":
        return "This unit restricts variable-acceleration problems to AS Pure 1 calculus, so the required methods are basic differentiation and integration of familiar functions."
    if variable_kind:
        return "In variable-acceleration problems, v = ds/dt and a = dv/dt, so calculus replaces constant-acceleration SUVAT formulae unless acceleration is constant."
    if is_motion_quantity_distinction_topic(lower):
        return "Distance and speed ignore direction, but displacement and velocity include direction, so signs and chosen axes matter."
    if is_motion_quantity_overview_topic(lower):
        return "Displacement is change in position, speed is distance per time, velocity is displacement per time, and acceleration is change in velocity per time."
    if "knowledge and use of constant acceleration" in lower or "constant acceleration equation" in lower:
        return "Constant-acceleration equations, often called SUVAT equations, connect s, u, v, a, and t when acceleration is constant, for example v = u + at and s = ut + 1/2 at^2."
    if "average speed" in lower:
        return "Average speed is total distance divided by total time, so it is scalar and does not include direction."
    if "trapezium" in lower:
        return "The trapezium rule estimates area under a curve by adding trapezia formed from ordinates at equal intervals."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_definition(trig_kind)
    if "vertical motion under gravity" in lower:
        return "Vertical motion under gravity uses the constant-acceleration equations with acceleration equal to g downwards, or -g if upwards is positive."
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return "For kinematics graphs, gradient and area have assigned meanings: for example, velocity-time gradient gives acceleration and velocity-time area gives displacement."
    if kinematics_graph_kind == "sketch_interpret":
        return "A kinematics sketch should show the qualitative motion clearly, such as constant speed, acceleration, rest, or change of direction."
    if kinematics_graph_kind:
        return "A kinematics graph describes motion: on a displacement-time graph gradient gives velocity, while on a velocity-time graph gradient gives acceleration and area gives displacement."
    intersection_kind = intersection_graph_topic_kind(lower)
    if intersection_kind == "algebra_to_geometry":
        return "A geometrical interpretation turns the solved equation into a statement about how many times the relevant graphs intersect."
    if intersection_kind == "two_way_interpretation":
        return "A solution of an equation can be read as a graph intersection, and a visible intersection can be translated back into an equation solution."
    if intersection_kind:
        return "An intersection point is a coordinate where two graphs have the same x-value and y-value, so their equations are solved together."
    force_kind = force_topic_kind(lower)
    if force_kind == "gravity":
        return "Force of gravity is weight: W = mg, acting vertically downwards on a particle near the Earth's surface."
    if force_kind == "tension":
        return "Tension is a pulling force transmitted through a taut string; thrust is the pushing force a rod can exert."
    if force_kind == "normal":
        return "Normal reaction is the contact force from a surface acting perpendicular to that surface."
    if force_kind == "friction":
        return "Friction is a contact force along a surface that opposes relative motion or the tendency to move."
    if force_kind == "connected":
        return "Connected-particle problems treat linked bodies as a system while still applying Newton's second law to each relevant body."
    if force_kind == "newton":
        return "Newton's laws link the resultant force on a particle to its acceleration, equilibrium, or paired action-reaction forces in the stated straight-line model."
    if "exponential" in lower and "graph" in lower:
        return "An exponential graph has a changing rate of growth or decay and usually approaches an asymptote rather than behaving like a straight line."
    if "surd" in lower:
        return "Surds are exact square-root expressions kept in radical form when a decimal would lose exactness."
    if "indices" in lower or "exponent" in lower:
        return "Index laws are rules for rewriting powers so multiplication, division, roots, and fractional powers stay consistent."
    if "discriminant" in lower:
        return "The discriminant is the part of the quadratic formula that tells you how many real roots a quadratic has."
    if "factorisation" in lower:
        return "Factorisation rewrites a polynomial as a product, making roots and algebraic structure easier to see."
    if "completing the square" in lower:
        return "Completing the square rewrites a quadratic to expose its vertex and symmetry."
    if "conservation of momentum" in lower:
        return "Conservation of momentum says the total momentum of the two-particle system is unchanged across the impact when no external impulse is included."
    if "fixed surface" in lower or "restitution" in lower:
        return "A direct impact with a fixed smooth surface changes only the velocity component perpendicular to the surface."
    if "concept of momentum" in lower or "momentum = mv" in lower:
        return "Momentum is mass times velocity, so it combines how much matter is moving with how fast it moves."
    if "impulse" in lower:
        return "Impulse is the change in momentum produced by a force acting over a time interval."
    if "momentum" in lower:
        return "Momentum is mass times velocity, so it combines how much matter is moving with how fast it moves."
    return source_bound_definition_sentence(concept, source_points, subject_pack)


def source_bound_definition_sentence(
    concept: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    source_fragments = usable_source_fragments(source_points)
    fragment = next(
        (
            point
            for point in source_fragments
            if normalize_concept_text(point) != normalize_concept_text(concept)
        ),
        source_fragments[0] if source_fragments else concept,
    )
    if len(fragment) > 120:
        fragment = fragment[:117].rstrip() + "..."
    if subject_pack == "economics":
        return f"{concept} is about {fragment}, so explain the economic choice, resource, market, cost, or benefit in context."
    if subject_pack == "accounting":
        return f"{concept} is about {fragment}, so identify the record, statement, control, or accounting purpose in context."
    if subject_pack == "business":
        return f"{concept} is about {fragment}, so explain the business decision, stakeholder, market, operation, or finance link in context."
    if subject_pack == "history":
        return f"{concept} is about {fragment}, so explain the event, cause, consequence, source, or change in context."
    if normalize_concept_text(fragment) == normalize_concept_text(concept):
        if subject_pack == "mathematics":
            return (
                f"{concept} is the syllabus focus here; match the expression, graph, formula, or model "
                "in the question to this exact topic before starting the working."
            )
        return f"{concept} is the exact method, notation, or model for this unit; identify its required form before starting the working."
    return f"{concept} focuses on {fragment}; keep the working inside that stated form or restriction."


def normalize_concept_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def force_topic_kind(lower: str) -> str | None:
    if "force of gravity" in lower or "w = mg" in lower:
        return "gravity"
    if "tension" in lower or "thrust" in lower:
        return "tension"
    if "normal reaction" in lower or "normal reactions" in lower:
        return "normal"
    if "friction" in lower or "coefficient of friction" in lower:
        return "friction"
    if "connected particle" in lower or "connected particles" in lower:
        return "connected"
    if any(word in lower for word in ["newton", "force", "forces"]):
        return "newton"
    return None


def math_topic_family(lower: str) -> str:
    if is_binomial_expansion_topic(lower):
        return "binomial_expansion"
    if variable_acceleration_topic_kind(lower):
        return "variable_acceleration"
    if is_motion_quantity_distinction_topic(lower) or is_motion_quantity_overview_topic(lower):
        return "kinematics_quantities"
    if kinematics_graph_topic_kind(lower):
        return "kinematics_graph"
    if "constant acceleration equation" in lower or "knowledge and use of constant acceleration" in lower:
        return "constant_acceleration"
    if "average speed" in lower:
        return "kinematics_quantities"
    if force_topic_kind(lower):
        return "forces"
    if any(word in lower for word in ["momentum", "impulse", "impact", "collision"]):
        return "momentum"
    if any(word in lower for word in ["bernoulli", "binomial distribution"]):
        return "binomial_probability"
    if any(word in lower for word in ["probability", "random variable", "variance", "standard deviation"]):
        return "probability"
    if is_trig_graph_topic(lower) or any(word in lower for word in ["trigonometry", "sine", "cosine"]):
        return "trigonometry"
    if any(word in lower for word in ["integrat", "area under", "trapezium"]):
        return "integration"
    if any(word in lower for word in ["differentiat", "derivative", "tangent", "stationary"]) and not (
        "circle" in lower or "coordinate geometry" in lower
    ):
        return "differentiation"
    if any(
        word in lower
        for word in ["circle", "straight line", "coordinate", "gradient", "midpoint", "perpendicular", "parallel"]
    ):
        return "coordinate_geometry"
    if any(word in lower for word in ["sequence", "series", "geometric progression", "arithmetic progression"]):
        return "sequences"
    if any(
        word in lower
        for word in [
            "surd",
            "indices",
            "exponent",
            "factor",
            "polynomial",
            "quadratic",
            "simultaneous",
            "remainder theorem",
            "algebra",
            "function",
        ]
    ):
        return "algebra"
    return "mathematics"


def is_trig_graph_topic(lower: str) -> bool:
    return ("trigonometry" in lower or "trigonometric" in lower) and any(
        phrase in lower for phrase in ["their graphs", "symmetries", "periodicity", "period"]
    )


def trig_topic_kind(lower: str) -> str | None:
    if not any(word in lower for word in ["trigonometry", "sine", "cosine"]):
        return None
    if "sine and cosine rules" in lower:
        return "sine_cosine_rules"
    if "area of a triangle" in lower or "1/2 ab sin" in lower:
        return "triangle_area"
    if "degree and radian" in lower or "radian measure" in lower:
        return "radian_measure"
    if "tan theta = sin theta / cos theta" in lower or "sin^2" in lower:
        return "identities"
    if is_trig_graph_topic(lower):
        return "graphs"
    if "sine, cosine and tangent functions" in lower:
        return "basic_functions"
    return "trigonometry"


def is_kinematics_graph_topic(lower: str) -> bool:
    return any(
        word in lower for word in ["kinematic", "kinematics", "motion", "displacement", "velocity", "speed"]
    ) and any(phrase in lower for phrase in ["graph", "graphs", "gradient", "area under"])


def is_intersection_graph_topic(lower: str) -> bool:
    return "intersection point" in lower or "graphs of functions to solve equations" in lower


def intersection_graph_topic_kind(lower: str) -> str | None:
    if not is_intersection_graph_topic(lower):
        return None
    if "geometrical interpretation" in lower or "algebraic solution" in lower:
        return "algebra_to_geometry"
    if "vice versa" in lower or "interpreting the solutions of equations" in lower:
        return "two_way_interpretation"
    return "intersection"


def is_binomial_expansion_topic(lower: str) -> bool:
    return "binomial expansion" in lower or "(1 + x)^n" in lower or "(1+x)^n" in lower


def is_variable_acceleration_topic(lower: str) -> bool:
    return "variable acceleration" in lower or (
        "displacement" in lower
        and "velocity" in lower
        and "acceleration" in lower
        and ("differentiat" in lower or "integrat" in lower)
    )


def is_motion_quantity_distinction_topic(lower: str) -> bool:
    return "difference between displacement and distance" in lower or "difference between velocity and speed" in lower


def is_motion_quantity_overview_topic(lower: str) -> bool:
    return (
        "displacement" in lower
        and "speed" in lower
        and "velocity" in lower
        and "acceleration" in lower
        and not is_variable_acceleration_topic(lower)
    )


def kinematics_graph_topic_kind(lower: str) -> str | None:
    if not is_kinematics_graph_topic(lower):
        return None
    if "gradient" in lower or "area under" in lower:
        return "gradient_area"
    if "sketch" in lower or "interpreting" in lower:
        return "sketch_interpret"
    return "graph"


def variable_acceleration_topic_kind(lower: str) -> str | None:
    if not is_variable_acceleration_topic(lower):
        return None
    if "application of calculus techniques" in lower:
        return "calculus_application"
    if "restricted to the calculus" in lower or "as unit p1" in lower:
        return "as_boundary"
    return "relationship"


def en_relationship_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The relationship is between rival pressure, firms' responses, and the short-run or long-run benefits that may result for consumers and the market."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The relationship is that competition creates pressure on firms to improve product quality, reduce costs, and improve service so they can attract or keep customers."
    if subject_pack == "accounting":
        fragments = usable_source_fragments(source_points)
        if len(fragments) >= 2:
            return f"The relationship is between {fragments[0]} and {fragments[1]}, staying inside this accounting unit."
        if fragments:
            return f"The relationship to track is the accounting purpose named here: {fragments[0]}."
        return f"The relationship is the accounting record, statement, or control purpose that makes {concept} a separate syllabus point."
    if subject_pack == "economics":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the economic cause, choice, cost, or consequence named here: {fragments[0]}."
        return f"The relationship is the economic link that makes {concept} a separate syllabus point."
    if subject_pack == "business":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the business decision, stakeholder, market, operation, or finance link named here: {fragments[0]}."
        return f"The relationship is the business link that makes {concept} a separate syllabus point."
    if subject_pack == "history":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the event, cause, consequence, source, or change named here: {fragments[0]}."
        return f"The relationship is the historical link that makes {concept} a separate syllabus point."
    if "use of factorisation" in lower:
        return "The relationship is that if (x-a)(x-b)=0, then each factor gives one possible solution."
    if "discriminant of a quadratic" in lower:
        return "The relationship is between the sign of b^2 - 4ac and the number of real roots of a quadratic equation."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "The relationship is between the discriminant/root count of the equation and the number of geometric intersection points."
    if "translation of circles" in lower:
        return "The relationship is between the circle equation `(x-a)^2 + (y-b)^2 = r^2` and the centre `(a,b)` after translation."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "The relationship is that probability must be based either on repeated observations or on a clearly defined equally likely sample space."
    if "inequalit" in lower:
        return "The relationship is between the algebraic inequality, the sign of each factor or expression, and the interval of x-values that makes the statement true."
    if is_binomial_expansion_topic(lower):
        return "The relationship is between the term number, the binomial coefficient, and the matching power of x in the expansion."
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return "The relationship is the calculus chain s -> v -> a by differentiation and a -> v -> s by integration when suitable constants are known."
    if variable_kind == "as_boundary":
        return "The relationship is between the mechanics question and the AS Pure 1 calculus tools allowed by the syllabus boundary."
    if variable_kind:
        return "The relationship is v = ds/dt and a = dv/dt, with integration used to recover velocity or displacement when needed."
    if is_motion_quantity_distinction_topic(lower):
        return "The relationship is that scalar quantities measure size only, while vector quantities also carry direction."
    if is_motion_quantity_overview_topic(lower):
        return "The relationship is speed = distance/time, velocity = displacement/time, and acceleration = change in velocity/time in a straight-line model."
    if "knowledge and use of constant acceleration" in lower or "constant acceleration equation" in lower:
        return "The relationship is between s, u, v, a, and t in a model where acceleration stays constant."
    if "average speed" in lower:
        return "The relationship is average speed = total distance / total time."
    if "trapezium" in lower:
        return "The relationship is estimate = h/2(first ordinate + last ordinate + 2 x sum of middle ordinates), with h as the strip width."
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return "The relationship is graph operation to motion quantity: read a gradient for a rate and an area under velocity-time for displacement."
    if kinematics_graph_kind == "sketch_interpret":
        return "The relationship is between the drawn shape and the motion story, such as increasing velocity, constant velocity, or stopping."
    if kinematics_graph_kind:
        return "The relationship is between the graph type and the quantity read from it: displacement-time gradient gives velocity; velocity-time gradient gives acceleration and area gives displacement."
    intersection_kind = intersection_graph_topic_kind(lower)
    if intersection_kind == "algebra_to_geometry":
        return "The relationship is between the number of algebraic roots and whether the graphs meet, touch, or do not meet."
    if intersection_kind == "two_way_interpretation":
        return "The relationship is reversible: algebraic solutions locate intersections, and intersection coordinates verify solutions."
    if intersection_kind:
        return "The relationship is that two graphs meet where their equations have the same x and y values."
    if is_trig_graph_topic(lower):
        return "The relationship is between the angle input and the repeating function value, using period, symmetry, zeros, and asymptotes where relevant."
    if "vertical motion under gravity" in lower:
        return "The relationship is that velocity and displacement follow the SUVAT equations with the sign of g chosen from the positive direction."
    if "transformation" in lower and "f (x" in lower:
        return "The key relationship is whether the change acts on the output, as in y = f(x) + a or y = af(x), or on the input, as in y = f(x + a) or y = f(ax)."
    if "conservation of momentum" in lower:
        return "The relationship is that total momentum before impact equals total momentum after impact when the stated system is treated consistently."
    if "fixed surface" in lower:
        return "The relationship is between the velocity perpendicular to the wall before impact and the rebound velocity after impact."
    if "concept of momentum" in lower or "momentum = mv" in lower:
        return "The relationship is p = mv, including the sign of velocity when motion is restricted to one straight line."
    if "impulse" in lower:
        return "The relationship is impulse equals final momentum minus initial momentum, with direction signs kept consistent."
    if "momentum" in lower:
        return "The relationship is p = mv, including the sign of velocity when motion is restricted to one straight line."
    force_kind = force_topic_kind(lower)
    if force_kind == "gravity":
        return "The relationship is W = mg, so weight depends on mass and the gravitational field strength used in the question."
    if force_kind == "tension":
        return "The relationship is that tension or thrust must be placed in the correct direction before writing the resultant-force equation."
    if force_kind == "normal":
        return "The relationship is that the normal reaction balances or contributes to the perpendicular contact-force equation."
    if force_kind == "friction":
        return "The relationship is F <= mu R, with limiting friction F = mu R when the particle is about to slip."
    if force_kind == "connected":
        return "The relationship is that connected particles share a constraint, so their accelerations and internal tensions must be consistent."
    if force_kind == "newton":
        return "The relationship is that resultant force controls acceleration through F = ma; when resultant force is zero, the particle is in equilibrium or has constant velocity."
    if subject_pack == "accounting":
        fragments = usable_source_fragments(source_points)
        if len(fragments) >= 2:
            return f"The relationship is between {fragments[0]} and {fragments[1]}, staying inside this accounting unit."
        if fragments:
            return f"The relationship to track is the accounting purpose named here: {fragments[0]}."
        return f"The relationship is the accounting record, statement, or control purpose that makes {concept} a separate syllabus point."
    if subject_pack == "economics":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the economic cause, choice, cost, or consequence named here: {fragments[0]}."
        return f"The relationship is the economic link that makes {concept} a separate syllabus point."
    if subject_pack == "business":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the business decision, stakeholder, market, operation, or finance link named here: {fragments[0]}."
        return f"The relationship is the business link that makes {concept} a separate syllabus point."
    if subject_pack == "history":
        fragments = usable_source_fragments(source_points)
        if fragments:
            return f"The relationship to track is the event, cause, consequence, source, or change named here: {fragments[0]}."
        return f"The relationship is the historical link that makes {concept} a separate syllabus point."
    if "straight line" in lower and "motion" not in lower:
        return "The relationship is between gradient, intercepts, coordinates, distance, and midpoint on the same coordinate grid."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_relationship(trig_kind)
    if "external cost" in lower or "external benefit" in lower:
        return "The relationship is between private decisions and effects on third parties outside the transaction."
    if "bank reconciliation" in lower:
        return "The relationship is between the cash book balance, bank statement balance, timing differences, and errors."
    if source_points:
        return f"The relationship to track is: {clean_point(source_points[0])}."
    return f"The relationship is the boundary or link that makes {concept} a separate syllabus point."


def en_boundary_sentence(
    concept: str,
    lower: str,
    source_points: list[str],
    subject_pack: str,
) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The boundary is that the answer should separate short-run effects from long-run benefits instead of repeating a general definition of competition."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The boundary is that this point is not just a supply-and-demand shift; it is about firm behaviour inside competition, especially price and non-price competition."
    if any(word in lower for word in ["restricted", "only", "will not", "not required", "simple problems"]):
        return "The syllabus boundary matters here: include the stated restriction and do not expand into excluded cases."
    if subject_pack == "mathematics":
        return math_family_boundary(concept, math_topic_family(lower))
    if subject_pack == "accounting":
        return "It is central because marks depend on using the correct statement, ledger, or control purpose, not just a familiar business word."
    if subject_pack == "economics":
        return "It is central because exam answers need the chain from cause to consequence, not just a definition."
    return f"It is central because the rest of the question normally depends on recognising {concept} first."


def en_analogy(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "Think of competition as a race over several laps: an early price or service response can become longer-term efficiency or innovation."
    if "competitive market process" in lower or "compete on price" in lower:
        return "Think of rival firms as runners in a race: one can lower price, but another can still compete by offering a better product or faster service."
    if subject_pack == "accounting":
        return "Think of the accounting record as a receipt trail: each entry must explain where the number came from and where it goes."
    if subject_pack == "business":
        return "Think of the business as a control room: each decision changes costs, customers, workers, owners, or long-term direction."
    if subject_pack == "economics":
        return "Think of a market as a set of nudges: every cost, benefit, or rule changes somebody's choice."
    if subject_pack != "mathematics":
        return f"Think of {concept} as the named rule or condition the answer must use, not just a keyword to define."
    if "inequalit" in lower:
        return "Think of an inequality as a number-line filter: only the x-values that pass the condition stay in the answer."
    if is_kinematics_graph_topic(lower):
        return "Think of a kinematics graph as an instrument panel: the axis labels tell you whether to read gradient, area, or a value."
    if is_intersection_graph_topic(lower):
        return "Think of two graph lines crossing on a map: the crossing point must satisfy both routes at once."
    if "graph" in lower or "curve" in lower:
        return "Think of the graph as a map: the route shape tells you more than a list of isolated points."
    if "probability" in lower:
        return "Think of it as setting the rules of a game before you count possible results."
    if "momentum" in lower or "impact" in lower:
        return "Think of two skaters pushing off: direction and speed both matter, not just who is heavier."
    if any(word in lower for word in ["newton", "force", "forces", "friction", "normal reaction"]):
        return "Think of a trolley being pushed: only the unbalanced part of the forces changes its acceleration."
    return math_family_analogy(concept, math_topic_family(lower))


def en_mini_example(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "A typical question asks you to explain how competition may benefit consumers immediately and how it may improve efficiency, innovation, or choice over time."
    if "competitive market process" in lower or "compete on price" in lower:
        return "A typical question describes rival firms and asks why competition may lead to improved products, lower costs, or better service even when prices are not cut."
    if subject_pack == "accounting":
        return "A typical question gives transaction data and asks you to place it in the correct record or statement."
    if subject_pack == "business":
        return "A typical question gives a business situation and asks you to explain the effect on objectives, stakeholders, customers, operations, or finance."
    if subject_pack == "economics":
        return "A typical question gives a real market situation and asks you to explain the cause-and-effect chain."
    if subject_pack != "mathematics":
        return f"A typical question asks you to recognise {concept}, identify the relevant relationship, and apply it to the given situation."
    if "use of factorisation" in lower:
        return "A typical question asks you to factorise first, set each factor equal to zero, and list all valid solutions."
    if "discriminant of a quadratic" in lower:
        return "A typical question gives a quadratic and asks you to decide the nature of its roots from the sign of b^2 - 4ac."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "A typical question gives an intersection equation and asks you to decide whether the graphs meet once, twice, or not at all."
    if "translation of circles" in lower:
        return "A typical question gives a circle and a translation vector, then asks for the new centre or equation."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "A typical question gives either trial results or a fair sample space, then asks for the probability using the appropriate basis."
    if "inequalit" in lower:
        return "A typical question asks you to solve an inequality, show the critical values, and give the answer as an interval or on a number line."
    if is_binomial_expansion_topic(lower):
        return "A typical question asks you to expand (1 + x)^n up to a stated power of x using binomial coefficients."
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return "A typical question gives a time-dependent expression and asks you to choose differentiation or integration to find a motion quantity."
    if variable_kind == "as_boundary":
        return "A typical question stays within AS Pure 1 calculus while asking for velocity, acceleration, displacement, or a time condition."
    if variable_kind:
        return "A typical question gives s(t), v(t), or a(t), then asks you to differentiate or integrate to find the missing motion quantity."
    if is_motion_quantity_distinction_topic(lower):
        return "A typical question asks whether a value is distance, displacement, speed, or velocity, then expects the direction rule to be stated."
    if is_motion_quantity_overview_topic(lower):
        return "A typical question gives distance, displacement, time, or change in velocity and asks for the matching speed, velocity, or acceleration."
    if "trapezium" in lower:
        return "A typical question gives a table of x-values and y-values, then asks you to estimate the area using the trapezium rule."
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return "A typical question gives a velocity-time graph and asks for acceleration from gradient or displacement from area."
    if kinematics_graph_kind == "sketch_interpret":
        return "A typical question gives a motion description and asks you to sketch or read the matching displacement-time or velocity-time graph."
    if kinematics_graph_kind:
        return "A typical question gives a displacement-time or velocity-time graph and asks for a velocity, acceleration, displacement, or distance from gradient or area."
    intersection_kind = intersection_graph_topic_kind(lower)
    if intersection_kind == "algebra_to_geometry":
        return "A typical question asks you to form an equation from two graphs and use the root count to describe their intersections."
    if intersection_kind == "two_way_interpretation":
        return "A typical question asks you to explain how a solution read from a graph matches a value found algebraically."
    if intersection_kind:
        return "A typical question gives two equations or graphs and asks you to find or interpret their intersection points."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_mini_example(trig_kind)
    if is_trig_graph_topic(lower):
        return "A typical question asks for the period, symmetry, zeros, asymptotes, or a sketch feature of a sine, cosine, or tangent graph."
    if "vertical motion under gravity" in lower:
        return "A typical question asks for time, height, or velocity of a particle moving upwards or downwards under acceleration g."
    if "graph" in lower or "curve" in lower:
        return "A typical question gives an equation or graph feature, then asks you to connect it to intercepts, gradients, roots, or shape."
    if "probability" in lower:
        return "A typical question defines the outcomes first, then asks for a probability, expectation, or distribution value."
    if "momentum" in lower or "impact" in lower:
        return "A typical question gives masses and velocities, then asks you to write the before-and-after momentum equation."
    force_kind = force_topic_kind(lower)
    if force_kind == "gravity":
        return "A typical question gives a mass and asks for weight, or asks you to place W = mg correctly in a vertical force balance."
    if force_kind == "tension":
        return "A typical question gives a string or rod model and asks for the tension or thrust after resolving forces."
    if force_kind == "normal":
        return "A typical question gives a particle on a surface and asks for the normal reaction from perpendicular force balance."
    if force_kind == "friction":
        return "A typical question gives mu and R and asks for friction, limiting friction, or impending motion."
    if force_kind == "connected":
        return "A typical question gives linked particles and asks for a shared acceleration or internal tension."
    if force_kind == "newton":
        return "A typical question gives masses, forces, friction, or a connected-particle setup, then asks for acceleration, tension, or a missing force using F = ma."
    return math_family_mini_example(concept, math_topic_family(lower))


def en_steps(concept: str, lower: str, subject_pack: str) -> list[str]:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return [
            "Identify the competitive pressure or market change in the scenario.",
            "Explain the firm's short-run response, such as price, quality, or service adjustment.",
            "Explain the longer-run effect, such as efficiency, innovation, or greater consumer choice.",
            "State who benefits and why the benefit may not be immediate or guaranteed.",
        ]
    if "competitive market process" in lower or "compete on price" in lower:
        return [
            "Identify the rival firms or competitive pressure in the scenario.",
            "State whether the response is price competition or non-price competition.",
            "Explain the firm behaviour, such as product improvement, cost reduction, or service improvement.",
            "Link the behaviour to gaining or retaining customers.",
        ]
    if subject_pack == "accounting":
        return [
            "Identify the source document, transaction, or statement named in the question.",
            "Place each amount in the correct side, column, or section.",
            "Apply the relevant accounting rule or control purpose.",
            "Check that totals, balances, and labels answer the question.",
        ]
    if subject_pack == "business":
        return [
            "Identify the business decision, issue, or stakeholder named in the question.",
            "Explain the likely effect on costs, revenue, customers, workers, owners, or operations.",
            "Keep the answer inside the required business idea.",
            "Finish with a judgement or recommendation when the command word asks for one.",
        ]
    if subject_pack == "economics":
        return [
            "Identify the decision maker or market in the scenario.",
            "State the incentive, constraint, cost, or benefit involved.",
            "Explain the chain of effects using the correct economic term.",
            "Finish with the result or judgement asked for by the command word.",
        ]
    if subject_pack != "mathematics":
        return [
            "Identify the exact source-bound idea named by the question.",
            "State the relationship, boundary, or effect described in this unit.",
            "Apply it only to the given situation.",
            "Check that the answer does not import a different topic.",
        ]
    if "use of factorisation" in lower:
        return [
            "Rewrite the expression as a product of factors.",
            "Set each factor equal to zero.",
            "Solve each small equation.",
            "Check that all solutions have been included.",
        ]
    if "discriminant of a quadratic" in lower:
        return [
            "Identify a, b, and c from the quadratic equation.",
            "Calculate b^2 - 4ac carefully.",
            "Use the sign of the discriminant to classify the roots.",
            "State the root nature clearly without necessarily solving the equation.",
        ]
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return [
            "Form the equation that represents the intersection or geometric condition.",
            "Calculate or reason about the number of real roots.",
            "Translate the root count back into geometry.",
            "State the conclusion using words such as tangent, two intersections, or no real intersection.",
        ]
    if "translation of circles" in lower:
        return [
            "Read the original centre and radius from the circle equation.",
            "Apply the translation to the centre coordinates.",
            "Keep the radius unchanged.",
            "Write the new equation in completed-square form.",
        ]
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return [
            "Decide whether the information is observed frequency data or an equally likely sample space.",
            "Count the relevant outcomes or frequencies.",
            "Divide by the correct total.",
            "State whether the result is exact probability or an estimate.",
        ]
    if "inequalit" in lower:
        return [
            "Find the critical value or values where the related expression equals zero.",
            "Use algebra, a sign table, or a graph to decide which intervals satisfy the inequality.",
            "Keep the inequality sign consistent when multiplying or dividing by a negative value.",
            "Write the final answer as an interval or on a number line.",
        ]
    if is_binomial_expansion_topic(lower):
        return [
            "Identify n and the power of x required.",
            "Write the binomial coefficients in order.",
            "Pair each coefficient with the matching power of x.",
            "Stop at the requested term and keep terms in ascending or requested order.",
        ]
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return [
            "Identify the time-dependent expression supplied.",
            "Choose differentiation or integration from the quantity required.",
            "Apply the AS calculus rule carefully.",
            "Use any initial condition to find constants or final values.",
        ]
    if variable_kind == "as_boundary":
        return [
            "Check that the calculus required is inside AS Pure 1.",
            "Translate the mechanics wording into s, v, or a.",
            "Differentiate or integrate only as far as the syllabus allows.",
            "State the final motion quantity with units and signs.",
        ]
    if variable_kind:
        return [
            "Identify whether the question gives displacement, velocity, or acceleration.",
            "Differentiate to move from s to v and from v to a.",
            "Integrate to move from a to v or from v to s when initial conditions are given.",
            "Substitute the requested time and include units.",
        ]
    if is_motion_quantity_distinction_topic(lower):
        return [
            "Decide whether direction is relevant.",
            "Use distance or speed when only size is needed.",
            "Use displacement or velocity when direction or sign matters.",
            "State the unit and direction convention where required.",
        ]
    if is_motion_quantity_overview_topic(lower):
        return [
            "Identify the motion quantities given in the question.",
            "Choose the matching definition, such as speed = distance/time.",
            "Substitute values with consistent units.",
            "State whether the answer is scalar or vector if direction matters.",
        ]
    if "trapezium" in lower:
        return [
            "List the ordinates in order from the table or graph.",
            "Identify the equal strip width h.",
            "Double the middle ordinates, then add the first and last ordinates once.",
            "Multiply by h/2 and state that the answer is an estimate.",
        ]
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_steps(trig_kind)
    if is_trig_graph_topic(lower):
        return [
            "Identify whether the graph is sine, cosine, or tangent.",
            "Read the period and symmetry from the standard graph shape.",
            "Mark key values such as zeros, maxima, minima, or asymptotes.",
            "Keep the answer inside the stated angle interval.",
        ]
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return [
            "Identify the graph type from the axes.",
            "Use gradient for the relevant rate of change.",
            "Use area under a velocity-time graph for displacement or distance.",
            "Check units and signs from the graph scale.",
        ]
    if kinematics_graph_kind == "sketch_interpret":
        return [
            "Read the axes before interpreting the shape.",
            "Match straight or curved sections to the motion description.",
            "Mark key events such as rest, constant velocity, or acceleration.",
            "Keep the sketch consistent with the stated time interval.",
        ]
    if kinematics_graph_kind:
        return [
            "Check which motion quantity is on each axis.",
            "Use gradient only for the quantity named by that graph type.",
            "Use area under a velocity-time graph for displacement or distance when appropriate.",
            "Include signs and units in the final answer.",
        ]
    if is_intersection_graph_topic(lower):
        return [
            "Set the two equations equal when both describe y.",
            "Solve the resulting equation carefully.",
            "Substitute each solution back to find full coordinates.",
            "State the answer as graph intersections, not just algebraic roots.",
        ]
    if "vertical motion under gravity" in lower:
        return [
            "Choose a positive vertical direction.",
            "Write acceleration as g downwards, with the correct sign.",
            "Use the appropriate constant-acceleration equation.",
            "Check whether the answer describes upward motion, downward motion, or the highest point.",
        ]
    if "graph" in lower or "curve" in lower:
        return [
            "Identify the graph feature named in the question.",
            "Link it to the matching algebraic fact, such as roots, intercepts, gradient, vertex, or transformation.",
            "Use the equation or sketch to support the answer.",
            "Check that the final statement matches the requested feature.",
        ]
    if "momentum" in lower or "impact" in lower:
        return [
            "Choose a positive direction and keep it throughout.",
            "Write the before-impact and after-impact momentum terms.",
            "Apply the stated conservation, impulse, or restitution relationship.",
            "Check signs and units before giving the final velocity or statement.",
        ]
    if any(word in lower for word in ["newton", "force", "forces", "friction", "normal reaction"]):
        return [
            "Draw or imagine the force diagram in the stated straight line.",
            "Choose a positive direction for the motion.",
            "Write resultant force = mass x acceleration for the particle or system.",
            "Solve for the required acceleration, tension, or force with units.",
        ]
    if subject_pack == "mathematics":
        return math_family_steps(concept, math_topic_family(lower))
    return [
        "Read the item or relationship named in the question.",
        "Select the rule, definition, model, or evidence that matches it.",
        "Apply that rule to the given context.",
        "Finish with the form required by the command word.",
    ]


def trig_essence(kind: str) -> str:
    values = {
        "sine_cosine_rules": "The sine and cosine rules solve non-right-angled triangles by matching sides to their opposite angles.",
        "triangle_area": "The formula 1/2 ab sin C finds the area of a triangle from two sides and the included angle.",
        "radian_measure": "Radian measure links angle size to arc length, so angles can be used naturally with circular motion and trig graphs.",
        "basic_functions": "Sine, cosine, and tangent functions connect angle inputs to ratio values that can be read algebraically or graphically.",
        "graphs": "Trigonometric graphs are about periodic shape, symmetry, and how sine, cosine, and tangent values repeat.",
        "identities": "Trigonometric identities rewrite sin, cos, and tan expressions without changing their value.",
    }
    return values.get(kind, "Trigonometry links angles, ratios, identities, and graph behaviour.")


def trig_definition(kind: str) -> str:
    values = {
        "sine_cosine_rules": "The sine rule links a/sin A = b/sin B = c/sin C, while the cosine rule links one side to the other two sides and the included angle.",
        "triangle_area": "The area formula 1/2 ab sin C uses two side lengths and the angle between them, not a perpendicular height.",
        "radian_measure": "One radian is the angle made when arc length equals radius, so theta = arc length / radius.",
        "basic_functions": "The functions sin x, cos x, and tan x assign a value to each angle x, using triangle ratios and their graph extensions.",
        "graphs": "Trigonometric graphs show how sin x, cos x, and tan x repeat over angle intervals, including their period and symmetry.",
        "identities": "The identities tan theta = sin theta / cos theta and sin^2 theta + cos^2 theta = 1 allow expressions to be simplified or transformed.",
    }
    return values.get(kind, "A trigonometric relationship connects an angle to a side ratio, graph value, or equivalent expression.")


def trig_relationship(kind: str) -> str:
    values = {
        "sine_cosine_rules": "The relationship is between each side and the angle opposite it; choose sine rule or cosine rule from the information given.",
        "triangle_area": "The relationship is area = 1/2 ab sin C, where C is the included angle between sides a and b.",
        "radian_measure": "The relationship is theta = s/r, connecting angle in radians with arc length and radius.",
        "basic_functions": "The relationship is that each angle input has a sine, cosine, and tangent value, with signs depending on the quadrant or graph position.",
        "graphs": "The relationship is between the angle input and the repeating function value, using period, symmetry, zeros, and asymptotes where relevant.",
        "identities": "The relationship is equivalence: both sides of an identity represent the same value wherever the expressions are defined.",
    }
    return values.get(kind, "The relationship links angles to ratios or repeated graph values.")


def trig_mini_example(kind: str) -> str:
    values = {
        "sine_cosine_rules": "A typical question gives a non-right triangle and asks for a missing side or angle using the sine rule or cosine rule.",
        "triangle_area": "A typical question gives two sides and their included angle, then asks for the triangle's area.",
        "radian_measure": "A typical question asks you to convert between degrees and radians or use radians in an arc-length relationship.",
        "basic_functions": "A typical question asks for sin, cos, or tan values, signs, or related angle solutions within a stated interval.",
        "graphs": "A typical question asks for the period, symmetry, zeros, asymptotes, or a sketch feature of a sine, cosine, or tangent graph.",
        "identities": "A typical question asks you to simplify an expression or prove a statement using tan theta = sin theta / cos theta or sin^2 theta + cos^2 theta = 1.",
    }
    return values.get(kind, "A typical question gives angle information and asks you to apply the matching trigonometric relationship.")


def trig_steps(kind: str) -> list[str]:
    values = {
        "sine_cosine_rules": [
            "Label each side with its opposite angle.",
            "Choose sine rule when an opposite side-angle pair is available; otherwise consider cosine rule.",
            "Substitute values carefully.",
            "Check whether an angle ambiguity needs attention.",
        ],
        "triangle_area": [
            "Identify the two sides and their included angle.",
            "Substitute into area = 1/2 ab sin C.",
            "Use the angle unit required by the calculator mode.",
            "State the area with square units.",
        ],
        "radian_measure": [
            "Check whether the angle is in degrees or radians.",
            "Convert using pi radians = 180 degrees when needed.",
            "Use theta = s/r for arc-length relationships.",
            "Keep exact multiples of pi where appropriate.",
        ],
        "basic_functions": [
            "Identify which of sin, cos, or tan is involved.",
            "Use the stated angle interval or quadrant information.",
            "Find all valid values, not just the first calculator output.",
            "Check signs and exact-value form where required.",
        ],
        "graphs": [
            "Identify whether the graph is sine, cosine, or tangent.",
            "Read the period and symmetry from the standard graph shape.",
            "Mark key values such as zeros, maxima, minima, or asymptotes.",
            "Keep the answer inside the stated angle interval.",
        ],
        "identities": [
            "Choose the identity that links the expressions in the question.",
            "Rewrite one side using sin, cos, or tan relationships.",
            "Simplify algebraically without changing the domain.",
            "State the identity or solved expression clearly.",
        ],
    }
    return values.get(
        kind,
        [
            "Identify the angle relationship involved.",
            "Choose the matching trigonometric rule or identity.",
            "Substitute or transform carefully.",
            "Check the angle range and final form.",
        ],
    )


def trig_pitfall(kind: str) -> str:
    values = {
        "sine_cosine_rules": "The common error is matching a side with the wrong angle or using cosine rule when sine rule information is already paired.",
        "triangle_area": "The common error is using 1/2 base height when the question gives two sides and the included angle.",
        "radian_measure": "The common error is mixing degree mode and radian mode in the same calculation.",
        "basic_functions": "The common error is giving one angle answer while missing another valid value in the required range.",
        "graphs": "The common error is treating a trigonometric graph like a quadratic curve instead of using period and symmetry.",
        "identities": "The common error is treating an identity like an equation with only selected solutions, instead of preserving equivalence.",
    }
    return values.get(kind, "The common error is using a familiar trig fact without checking the angle range or graph feature.")


def math_family_analogy(concept: str, family: str) -> str:
    analogies = {
        "algebra": f"Treat {concept} like rearranging a toolkit: each algebraic form reveals a different route to roots, factors, or simplification.",
        "coordinate_geometry": f"Treat {concept} like reading a map grid: coordinates, gradients, distances, and equations describe the same location from different angles.",
        "differentiation": f"Treat {concept} like a speed camera for a curve: it tells you the instant rate or slope at the point that matters.",
        "integration": f"Treat {concept} like adding thin strips: the total area or accumulated quantity comes from combining many small pieces.",
        "sequences": f"Treat {concept} like spotting the rule in a pattern: once the step or ratio is known, any term or sum can be tracked.",
        "trigonometry": f"Treat {concept} like a triangle-and-wave translator: angles, ratios, and repeated graph features must agree.",
        "probability": f"Treat {concept} like setting up a fair game: outcomes, probabilities, and expected values must be defined before counting.",
        "binomial_probability": f"Treat {concept} like repeated yes/no trials: the number of trials, success probability, and independence carry the model.",
        "binomial_expansion": f"Treat {concept} like an ordered expansion recipe: each term takes its coefficient, power of x, and position from the binomial pattern.",
        "kinematics_quantities": f"Treat {concept} like a dashboard: distance, displacement, speed, velocity, and acceleration each report a different motion fact.",
        "kinematics_graph": f"Treat {concept} like a motion recorder: the graph type decides whether slope, area, or a coordinate is meaningful.",
        "constant_acceleration": f"Treat {concept} like a five-variable motion kit: once acceleration is constant, s, u, v, a, and t can be linked safely.",
        "variable_acceleration": f"Treat {concept} like moving between motion layers: differentiation goes from position to velocity to acceleration, integration comes back.",
        "forces": f"Treat {concept} like a force-balance sketch: the useful information appears only after directions and resultant force are clear.",
        "momentum": f"Treat {concept} like a before-and-after motion ledger: mass times velocity must be tracked with signs through the interaction.",
    }
    return analogies.get(
        family,
        f"Treat {concept} as the exact mathematical object in the question; its notation tells you which rule is allowed.",
    )


def math_family_mini_example(concept: str, family: str) -> str:
    examples = {
        "algebra": "A typical question gives an expression or equation and asks you to rewrite it into the form needed for roots, factors, simplification, or comparison.",
        "coordinate_geometry": "A typical question gives points, a line, or a circle and asks you to find an equation, gradient, distance, midpoint, tangent, or intersection.",
        "differentiation": "A typical question gives a function and asks for a derivative, gradient, tangent, normal, stationary point, or rate of change.",
        "integration": "A typical question gives a function, bounds, or ordinates and asks for an antiderivative, area, or area estimate.",
        "sequences": "A typical question gives terms or a rule and asks you to find a term, common difference or ratio, sum, or convergence condition.",
        "trigonometry": "A typical question gives a triangle, equation, or graph and asks you to connect angle measures with ratios, rules, identities, or periodic features.",
        "probability": "A typical question gives outcomes or a distribution and asks for a probability, expectation, variance, or interpretation.",
        "binomial_probability": "A typical question gives n and p and asks for a binomial probability, mean, variance, or condition check.",
        "binomial_expansion": "A typical question asks for selected terms of an expansion such as (1 + x)^n, usually up to a stated power of x.",
        "kinematics_quantities": "A typical question gives time, displacement, distance, velocity, speed, or acceleration and asks you to choose the matching definition.",
        "kinematics_graph": "A typical question gives a displacement-time or velocity-time graph and asks for a motion fact from slope, area, shape, or intercept.",
        "constant_acceleration": "A typical question gives three of s, u, v, a, and t, then asks for the missing motion quantity using a constant-acceleration equation.",
        "variable_acceleration": "A typical question gives s(t), v(t), or a(t) and asks you to differentiate or integrate to find the required motion quantity.",
        "forces": "A typical question gives a particle or connected system and asks for acceleration, reaction, friction, tension, thrust, or weight.",
        "momentum": "A typical question gives masses and velocities before or after an interaction and asks for momentum, impulse, or rebound information.",
    }
    return examples.get(
        family,
        f"A typical question gives the mathematical form for {concept} and asks you to use that form to reach the requested answer.",
    )


def math_family_steps(concept: str, family: str) -> list[str]:
    steps_by_family = {
        "algebra": [
            "Identify the expression, equation, or inequality form.",
            "Choose the algebraic move that changes the form without changing the meaning.",
            "Carry the manipulation carefully, keeping signs and powers consistent.",
            "State the result in the requested exact form.",
        ],
        "coordinate_geometry": [
            "Mark the given points, line, circle, or intersection information.",
            "Choose the relevant coordinate relationship: gradient, distance, midpoint, radius, tangent, or simultaneous equations.",
            "Substitute the coordinates into that relationship.",
            "Give the equation or coordinate in a clean final form.",
        ],
        "differentiation": [
            "Differentiate the function using the rule allowed by the syllabus point.",
            "Substitute the required x-value or solve the required derivative condition.",
            "Connect the derivative to gradient, tangent, normal, stationary point, or rate of change.",
            "Check that the answer matches the requested interpretation.",
        ],
        "integration": [
            "Choose whether the task needs an antiderivative, a definite integral, or an area estimate.",
            "Apply the integration or trapezium-rule setup with correct bounds or ordinates.",
            "Evaluate the expression or estimate carefully.",
            "State whether the result is exact area, signed area, or an approximation.",
        ],
        "sequences": [
            "Identify whether the sequence or series is arithmetic, geometric, or binomial.",
            "Write the term, sum, ratio, or coefficient relationship needed.",
            "Substitute the given values and simplify.",
            "Check any convergence or validity condition before the final answer.",
        ],
        "trigonometry": [
            "Identify the triangle, angle equation, identity, or graph feature.",
            "Choose the matching sine, cosine, tangent, rule, or periodic relationship.",
            "Use the required angle range or geometry condition.",
            "State all valid values or features, not just the first one found.",
        ],
        "probability": [
            "Define the event, random variable, or distribution from the question.",
            "Write the probability rule, expectation, variance, or table relationship.",
            "Substitute the given values and simplify.",
            "Check that probabilities are valid and the interpretation fits the context.",
        ],
        "binomial_probability": [
            "Check the Bernoulli/binomial conditions: fixed trials, success probability, and independence.",
            "Identify n, p, and the event being counted.",
            "Use the formula, table, mean, or variance relationship required.",
            "Check whether the question asks for exact, cumulative, or complementary probability.",
        ],
        "binomial_expansion": [
            "Identify n and the power of x required.",
            "Write the relevant binomial coefficients in order.",
            "Combine coefficients with the correct powers.",
            "Stop at the requested term or power.",
        ],
        "kinematics_quantities": [
            "Decide whether the quantity is scalar or vector.",
            "Choose distance/time, displacement/time, or change in velocity/time as appropriate.",
            "Keep direction signs consistent when displacement or velocity is used.",
            "Attach the correct unit to the final motion quantity.",
        ],
        "kinematics_graph": [
            "Read the graph type and axes first.",
            "Match gradient, area, intercept, or shape to its motion meaning.",
            "Use the graph evidence to calculate or describe the motion.",
            "Check that the answer uses the same time interval and units as the graph.",
        ],
        "constant_acceleration": [
            "List the known values among s, u, v, a, and t.",
            "Choose the constant-acceleration equation containing the required unknown.",
            "Substitute with a consistent sign convention.",
            "Check the unit and whether the result describes displacement, velocity, acceleration, or time.",
        ],
        "variable_acceleration": [
            "Identify which of s(t), v(t), or a(t) is given.",
            "Differentiate to move from s to v to a, or integrate to move back.",
            "Use any initial condition to find the constant of integration.",
            "Answer the motion question with the correct time and unit.",
        ],
        "forces": [
            "Draw or imagine the force diagram and choose positive direction.",
            "Resolve only the forces acting along the required line.",
            "Apply equilibrium or F = ma to the particle or system.",
            "Solve for the requested force, reaction, tension, friction, or acceleration.",
        ],
        "momentum": [
            "Choose a positive direction and write velocities with signs.",
            "Write momentum before and after the interaction.",
            "Apply conservation of momentum, impulse, or restitution as required.",
            "Check the final direction and units.",
        ],
    }
    return steps_by_family.get(
        family,
        [
            "Identify the exact mathematical form named in the question.",
            "Select the rule that belongs to that form.",
            "Apply the rule to the given numbers, graph, or expression.",
            "Give the answer in the notation requested by the command word.",
        ],
    )


def math_family_pitfall(concept: str, family: str) -> str:
    pitfalls = {
        "algebra": "The common error is changing the expression's value while trying to change its form.",
        "coordinate_geometry": "The common error is using the right formula with the wrong pair of points or the wrong sign for the gradient.",
        "differentiation": "The common error is finding a derivative but not connecting it to the tangent, normal, rate, or stationary-point condition asked for.",
        "integration": "The common error is treating an area estimate, an indefinite integral, and a definite integral as the same kind of answer.",
        "sequences": "The common error is using an arithmetic rule on a geometric pattern, or forgetting the convergence condition.",
        "trigonometry": "The common error is giving one angle answer while missing another valid value in the required range.",
        "probability": "The common error is calculating a number without defining the event or checking that the probabilities total sensibly.",
        "binomial_probability": "The common error is using a binomial formula before checking the Bernoulli conditions.",
        "binomial_expansion": "The common error is mixing the algebraic binomial expansion with the binomial probability distribution.",
        "kinematics_quantities": "The common error is dropping direction and turning displacement or velocity into distance or speed.",
        "kinematics_graph": "The common error is using a graph operation on the wrong graph type, such as taking area under a displacement-time graph.",
        "constant_acceleration": "The common error is using a constant-acceleration equation without checking signs and whether acceleration is actually constant.",
        "variable_acceleration": "The common error is using SUVAT equations when acceleration is not constant.",
        "forces": "The common error is adding force magnitudes without resolving signs and directions first.",
        "momentum": "The common error is changing the positive direction halfway through the momentum or impulse equation.",
    }
    return pitfalls.get(
        family,
        f"The common error is treating {concept} like a keyword instead of using its exact mathematical form.",
    )


def math_family_boundary(concept: str, family: str) -> str:
    boundaries = {
        "algebra": "This matters because exact algebraic form often decides whether roots, factors, or simplifications are valid.",
        "coordinate_geometry": "This matters because a coordinate answer is only correct when the geometry and algebra describe the same object.",
        "differentiation": "This matters because derivative answers must be tied to the requested slope, rate, or turning-point meaning.",
        "integration": "This matters because the bounds, sign, and approximation method change the meaning of the area found.",
        "sequences": "This matters because term, sum, ratio, and convergence questions use different formulae.",
        "trigonometry": "This matters because angle range, graph period, and triangle information decide which values are valid.",
        "probability": "This matters because the model decides whether the number is a probability, expectation, variance, or estimate.",
        "binomial_probability": "This matters because the binomial model is valid only when the trial conditions match the question.",
        "binomial_expansion": "This matters because expansion questions mark term structure and coefficients, not a probability model.",
        "kinematics_quantities": "This matters because scalar and vector motion quantities answer different physical questions in the mechanics unit.",
        "kinematics_graph": "This matters because graph type decides whether slope or area gives the required motion quantity.",
        "constant_acceleration": "This matters because SUVAT-style equations are valid only inside a constant-acceleration model.",
        "variable_acceleration": "This matters because calculus replaces SUVAT when acceleration is variable.",
        "forces": "This matters because Newton's laws work on the resultant force in the chosen direction, not on loose force labels.",
        "momentum": "This matters because momentum and impulse depend on signed velocity, so direction changes the answer.",
    }
    return boundaries.get(
        family,
        f"This matters because {concept} controls which mathematical rule is valid for the question.",
    )


def en_pitfall(concept: str, lower: str, subject_pack: str) -> str:
    if "dynamics of competition" in lower or "short-run and long-run benefits" in lower:
        return "The common error is listing benefits of competition without separating short-run responses from long-run market outcomes."
    if "competitive market process" in lower or "compete on price" in lower:
        return "The common error is treating competition as only a price cut and ignoring product quality, cost reduction, and service improvement."
    if subject_pack == "accounting":
        return "The common error is using the right number in the wrong account, side, or statement section."
    if subject_pack == "business":
        return "The common error is giving a definition without explaining the effect on the business or stakeholder in the context."
    if subject_pack == "economics":
        return "The common error is naming a concept without explaining the cause-and-effect chain in the scenario."
    if subject_pack != "mathematics":
        return f"The common error is writing a memorised phrase about {concept} without using the source-bound condition in the question."
    if "use of factorisation" in lower:
        return "The common error is finding the factors but not setting each factor equal to zero."
    if "discriminant of a quadratic" in lower:
        return "The common error is treating the discriminant as the root itself instead of using its sign to classify the roots."
    if "using algebraic methods" in lower or "equal roots" in lower or "distinct real roots" in lower or "no real roots" in lower:
        return "The common error is solving the equation but not translating the number of real roots back into the geometry."
    if "translation of circles" in lower:
        return "The common error is changing the radius or copying the centre signs incorrectly."
    if "relative frequencies" in lower or "equally likely outcomes" in lower:
        return "The common error is mixing an experimental estimate with exact equally likely counting."
    if "inequalit" in lower:
        return "The common error is solving the boundary equation but not checking which side of each boundary satisfies the inequality."
    if is_binomial_expansion_topic(lower):
        return "The common error is using a sequence formula or binomial probability formula instead of the algebraic expansion coefficients."
    variable_kind = variable_acceleration_topic_kind(lower)
    if variable_kind == "calculus_application":
        return "The common error is differentiating when the question requires reversing the chain by integration, or vice versa."
    if variable_kind == "as_boundary":
        return "The common error is importing a more advanced mechanics method instead of staying within the AS Pure 1 calculus boundary."
    if variable_kind:
        return "The common error is using constant-acceleration SUVAT formulae when the acceleration depends on time."
    if is_motion_quantity_distinction_topic(lower):
        return "The common error is treating displacement as distance or velocity as speed and losing the direction information."
    if is_motion_quantity_overview_topic(lower):
        return "The common error is mixing up the numerator in speed, velocity, and acceleration definitions."
    if "trapezium" in lower:
        return "The common error is forgetting to double the middle ordinates or presenting the estimate as an exact integral."
    trig_kind = trig_topic_kind(lower)
    if trig_kind:
        return trig_pitfall(trig_kind)
    if is_trig_graph_topic(lower):
        return "The common error is treating a trigonometric graph like a quadratic curve instead of using period and symmetry."
    kinematics_graph_kind = kinematics_graph_topic_kind(lower)
    if kinematics_graph_kind == "gradient_area":
        return "The common error is taking the right-looking gradient or area from the wrong graph type."
    if kinematics_graph_kind == "sketch_interpret":
        return "The common error is sketching a generic graph without matching the axes and motion description."
    if kinematics_graph_kind:
        return "The common error is using the right-looking graph operation on the wrong graph type, such as taking area under a displacement-time graph."
    if is_intersection_graph_topic(lower):
        return "The common error is giving only x-values when the question asks for intersection points as coordinates."
    if "vertical motion under gravity" in lower:
        return "The common error is using g with the wrong sign after choosing a positive direction."
    if "graph" in lower or "curve" in lower:
        return "Do not plot random points when the mark is for a named graph feature such as a root, gradient, asymptote, vertex, or transformation."
    if "momentum" in lower or "impact" in lower:
        return "The common error is changing direction signs halfway through the momentum or restitution equation."
    if any(word in lower for word in ["newton", "force", "forces", "friction", "normal reaction"]):
        return "The common error is adding all forces as positive instead of resolving them into the chosen direction before using F = ma."
    if subject_pack == "mathematics":
        return math_family_pitfall(concept, math_topic_family(lower))
    return f"The common error is using a memorised line about {concept} without connecting it to the evidence in the question."


if __name__ == "__main__":
    raise SystemExit(main())
