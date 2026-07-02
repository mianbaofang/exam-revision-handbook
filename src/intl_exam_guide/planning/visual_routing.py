from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Topic, TopicGuide, VisualBrief
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.planning.localization import (
    is_generic_zh_label,
    zh_point_label,
    zh_point_labels,
    zh_visual_trigger,
    zh_visual_type,
)
from intl_exam_guide.planning.source_points import visible_source_points
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile


SUBJECT_PROMPT_LABELS = {
    "accounting": ("accounting", "会计"),
    "biology": ("biology", "生物"),
    "business": ("business", "商业"),
    "chemistry": ("chemistry", "化学"),
    "economics": ("economics and business", "经济与商业"),
    "generic": ("this subject", "本学科"),
    "history": ("history", "历史"),
    "mathematics": ("mathematics", "数学"),
    "physics": ("physics", "物理"),
}

COURSE_PACKAGING_PATTERNS = [
    r"\b(?:Oxford\s*)?AQA\b",
    r"\bOxfordAQA\b",
    r"\bPearson\b",
    r"\bEdexcel\b",
    r"\bCambridge\b",
    r"\bCAIE\b",
    r"\bInternational\s+(?:GCSE|AS(?:[-\s]A[-\s]level|[-\s]A-level|\s+Level)?|A[-\s]level)\b",
    r"\bIGCSE\b",
    r"\bGCSE\b",
    r"\bAS[-\s]A[-\s]level\b",
    r"\bAS[-\s]A-level\b",
    r"\bAS\s+Level\b",
    r"\bA[-\s]level\b",
    r"\bA\s+Level\b",
    r"\bAS\s+unit\s+[A-Z]?\d+\b",
    r"\bcourse\s+code\s*[·:,-]?\s*\d+\b",
    r"\bcode\s*[·:,-]?\s*\d+\b",
    r"课程代码\s*[·:：,-]?\s*\d+",
    r"国际课程",
    r"官方英文来源",
    r"AS\s*[A-Z]?\d+",
]


def build_visual_brief(
    topic: Topic,
    guide: TopicGuide,
    run_options: GuideRunOptions,
    subject_area: str | None = None,
) -> VisualBrief | None:
    points = visible_source_points(topic, limit=4)
    focus = points[0]
    visual_type, complexity, trigger = choose_visual_type(topic, points, subject_area)
    if complexity == "text-ok":
        return None
    provider = choose_provider_for_visual(complexity, run_options, visual_type)
    body_language = handbook_body_language(run_options.output_language)
    if body_language == "en":
        visible_focus = focus
        visible_points = points
        visible_visual_type = visual_type
        visible_trigger = trigger
    else:
        visible_focus = zh_point_label(focus)
        visible_points = [
            label for label in zh_point_labels(points) if not is_generic_zh_label(label)
        ]
        if not visible_points:
            visible_points = ["本节核心概念"]
        if is_generic_zh_label(visible_focus):
            visible_focus = visible_points[0]
        visible_visual_type = zh_visual_type(visual_type)
        visible_trigger = zh_visual_trigger(trigger)
    prompt = build_content_only_image_prompt(
        topic=topic,
        points=points,
        subject_area=subject_area,
        language=body_language,
        focus=visible_focus,
        visual_type=visible_visual_type,
        visible_points=visible_points,
    )
    return VisualBrief(
        topic_title=topic.title,
        focus_point=visible_focus,
        trigger=visible_trigger,
        visual_type=visible_visual_type,
        complexity=complexity,
        image_provider=provider,
        prompt=prompt,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def build_content_only_image_prompt(
    *,
    topic: Topic,
    points: list[str],
    subject_area: str | None,
    language: str,
    focus: str,
    visual_type: str,
    visible_points: list[str],
) -> str:
    """Build the prompt submitted to image models without board/source packaging."""

    language = handbook_body_language(language)
    subject = subject_prompt_label(subject_area, topic, points, language)
    clean_focus = clean_prompt_phrase(focus)
    clean_type = clean_prompt_phrase(visual_type)
    label_clause = prompt_label_clause(visible_points, language)
    return (
        "Create a polished educational worksheet infographic for a revision guide. "
        f"Topic: {subject}: {clean_focus}. "
        f"Visual task: {clean_type}. "
        "Use a clean landscape layout with a large topic banner, clear teaching panels, "
        "pastel subject colors, readable black labels, accurate diagrams or icons, "
        "and a small Quick Q&A or practice box. "
        "Show only the diagrams, formulas, and short labels needed for this topic. "
        "Do not add institutional logos, course-cover headers, badges, footers, "
        f"or watermarks.{label_clause}"
    )


def subject_prompt_label(
    subject_area: str | None,
    topic: Topic,
    points: list[str],
    language: str,
) -> str:
    profile = resolve_subject_profile(subject_area, topic, f"{topic.title} {' '.join(points)}")
    index = 1 if language != "en" else 0
    return SUBJECT_PROMPT_LABELS[profile.example_domain][index]


def prompt_label_clause(visible_points: list[str], language: str) -> str:
    labels = [clean_prompt_phrase(label) for label in visible_points[:3]]
    labels = [label for label in labels if label and not is_generic_zh_label(label)]
    if not labels:
        return ""
    if language == "en":
        return f" Short labels may include: {', '.join(labels)}."
    return f"可用短标签：{'、'.join(labels)}。"


def clean_prompt_phrase(text: str) -> str:
    phrase = " ".join(text.split())
    phrase = re.sub(
        r"^(?:students|candidates|learners)\s+(?:should|must|are expected to)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    phrase = re.sub(
        r"^(?:be able to|understand|describe|explain|apply)\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    for pattern in COURSE_PACKAGING_PATTERNS:
        phrase = re.sub(pattern, "", phrase, flags=re.IGNORECASE)
    phrase = re.sub(r"\s{2,}", " ", phrase).strip(" -:：,，;；")
    return phrase or "core concept visual"


def choose_visual_type(
    topic: Topic,
    points: list[str],
    subject_area: str | None = None,
) -> tuple[str, str, str]:
    text = f"{topic.title} {' '.join(points)}".lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    has = tokens.__contains__
    has_phrase = text.__contains__
    profile = resolve_subject_profile(subject_area, topic, text)

    if is_scope_exclusion_text(text):
        return "scope note for text explanation", "text-ok", "exam-scope exclusions should be kept as notes, not visuals"

    if profile.example_domain == "accounting":
        title_text = topic.title.lower()
        ratio_terms = ["ratio", "liquidity", "profitability", "analysis"]
        statement_terms = [
            "statement",
            "statements",
            "profit",
            "position",
            "partnership",
            "company",
            "manufacturing",
            "non-profit",
        ]
        if (
            "verification of the double entry records" in title_text
            and "bank reconciliation" not in title_text
            and "control account" not in title_text
            and "trial balance" not in title_text
        ):
            return "text explanation with optional table", "text-ok", "verification overview is a comparison of tools, not one reconciliation diagram"
        if any(term in title_text for term in ratio_terms) or (
            any(has(word) for word in ratio_terms)
            and not any(has(word) for word in statement_terms)
        ):
            return "text explanation with optional table", "text-ok", "ratio formula and interpretation topics are clearer as worked calculations"
        if title_text.strip() in {"financial statements", "final accounts"} and (
            has_phrase("income statement") or has_phrase("statement of financial position")
        ):
            return (
                "financial-statement layout summary table",
                "svg-basic",
                "financial-statement topics need a compact statement layout table",
            )
        if any(term in title_text for term in ["income statement", "statement of financial position", "financial statement"]) and not any(
            has(word)
            for word in [
                "partnership",
                "company",
                "companies",
                "limited",
                "liability",
                "manufacturing",
                "non",
                "profit",
                "club",
                "trial",
            ]
        ):
            return "text explanation with optional accounting table", "text-ok", "generic financial statement topics are clearer as worked examples than repeated layout diagrams"
        if (
            any(term in title_text for term in statement_terms)
            or any(has(word) for word in ["statement", "statements", "partnership", "company", "manufacturing"])
        ) and not any(
            marker in title_text
            for marker in ["correction of errors", "correct errors", "effect of errors", "control account", "bank reconciliation"]
        ):
            if "incomplete records" in title_text:
                return "incomplete records reconstruction flow", "svg-basic", "incomplete records need a reconstruction sequence"
            if "partnership" in title_text:
                return "partnership appropriation and current account layout", "svg-basic", "partnership accounts need profit appropriation and partner-current structure"
            if "manufacturing" in title_text or "manufacturer" in title_text or has_phrase("manufacturing accounts"):
                return "manufacturing account cost-flow layout", "svg-basic", "manufacturing accounts need prime cost to production cost flow"
            if "club" in title_text or "non-profit" in title_text:
                return "club receipts-payments and income-expenditure layout", "svg-basic", "club accounts need a receipts-to-income-expenditure distinction"
            if (
                "limited company" in title_text
                or "limited companies" in title_text
                or "limited liability" in title_text
                or "company accounts" in title_text
                or "company financial statements" in title_text
                or has_phrase("financial statements for companies")
            ):
                return "limited company financial statement layout", "svg-basic", "limited company accounts need statement layout detail"
            return "text explanation with optional accounting table", "text-ok", "generic financial statement topics are clearer as worked examples than repeated layout diagrams"
        if (
            any(phrase in title_text for phrase in ["trial balance", "control account", "bank reconciliation", "correction of errors", "correct errors", "effect of errors", "incomplete records"])
            or has_phrase("trial balance")
            or has_phrase("control account")
            or has_phrase("control accounts")
            or has_phrase("bank reconciliation")
            or has_phrase("correction of errors")
            or has_phrase("correct errors")
            or has_phrase("effect of errors")
            or has_phrase("incomplete records")
        ):
            if "control account" in title_text or "control accounts" in title_text:
                return "control account reconciliation diagram", "svg-basic", "control accounts need a ledger-to-control comparison"
            if "correction of errors" in title_text or "correct errors" in title_text or "effect of errors" in title_text:
                return "error correction and suspense account flow", "svg-basic", "error correction needs a detect-correct-check sequence"
            if "bank reconciliation" in title_text:
                return "bank reconciliation workflow diagram", "svg-basic", "bank reconciliation needs a precise comparison and correction flow"
            if "incomplete records" in title_text:
                return "incomplete records reconstruction flow", "svg-basic", "incomplete records need a reconstruction sequence"
            if "trial balance" in title_text:
                return "trial balance verification table", "svg-basic", "trial balance needs a debit-credit equality check"
            if has_phrase("control account") or has_phrase("control accounts"):
                return "control account reconciliation diagram", "svg-basic", "control accounts need a ledger-to-control comparison"
            if has_phrase("correction of errors") or has_phrase("correct errors") or has_phrase("effect of errors"):
                return "error correction and suspense account flow", "svg-basic", "error correction needs a detect-correct-check sequence"
            return "bank reconciliation workflow diagram", "svg-basic", "bank reconciliation needs a precise comparison and correction flow"
        if any(has(word) for word in ["depreciation", "receivables", "payables", "irrecoverable", "accruals", "prudence", "concepts"]):
            return "text explanation with optional table", "text-ok", "adjustments are safer as source-bound explanation unless a statement layout is required"
        if any(
            phrase in title_text
            for phrase in [
                "source documents are",
                "books of prime entry are",
                "books of account",
            ]
        ):
            return "text explanation with optional table", "text-ok", "record lists and book references are clearer as source-bound explanation than repeated flowcharts"
        records_flow_terms = [
            "source document",
            "source documents",
            "book of prime entry",
            "books of prime entry",
            "ledger account",
            "ledger accounts",
            "recording of transactions",
            "prepare accounting records",
            "prepare and understand accounting records",
        ]
        if any(term in text for term in records_flow_terms) or has_phrase("double entry system"):
            return "source-document to book-of-prime-entry and ledger flow diagram", "svg-basic", "accounting records need a precise source-to-ledger flow diagram"
        return "text explanation with optional table", "text-ok", "accounting point can be explained without a custom visual"

    if profile.example_domain == "business":
        title_text = topic.title.lower()
        if "stakeholder" in text:
            return "stakeholder influence map", "svg-basic", "stakeholder objectives are clearer as an influence-and-interest map"
        if any(marker in title_text for marker in ["ownership", "sole trader", "partnership", "limited company", "franchise"]):
            return "business ownership comparison table", "svg-basic", "ownership forms need a compact comparison of control, risk, and finance"
        if any(marker in text for marker in ["cash flow", "cash-flow", "inflow", "outflow", "opening balance", "closing balance", "forecast"]):
            return "cash-flow timeline and balance table", "svg-basic", "cash-flow topics need a time sequence and balance movement"
        if any(marker in text for marker in ["break-even", "breakeven", "fixed cost", "variable cost", "margin of safety"]):
            return "break-even chart with cost and revenue lines", "svg-basic", "break-even needs cost and revenue lines on axes"
        if "marketing mix" in title_text:
            return "marketing mix quadrant visual", "svg-basic", "marketing mix decisions are clearer in a four-part organizer"
        if "market segmentation" in title_text or "identifying and understanding customers" in title_text:
            return "customer segmentation map", "svg-basic", "customer and segmentation topics need a compact market map"
        if any(marker in text for marker in ["organisational structure", "organisational structures", "organisation chart", "span of control", "chain of command"]):
            return "organisation structure hierarchy diagram", "svg-basic", "organisational structure needs hierarchy and reporting lines"
        if any(marker in title_text for marker in ["production process", "production processes", "quality", "stock control"]):
            if "quality" in title_text:
                return "quality assurance checkpoint diagram", "svg-basic", "quality topics need a standards-check-feedback loop"
            return "operations flow and quality checkpoint diagram", "svg-basic", "operations topics need a process flow with checkpoints"
        return "text explanation with optional business mini case", "text-ok", "business point can be explained with source-bound examples unless a flow, map, or chart is central"

    if profile.example_domain == "economics":
        title_text = topic.title.lower()
        if any(
            phrase in title_text
            for phrase in [
                "movements along a demand curve",
                "movements along a supply curve",
                "consequences of changes in foreign exchange rate",
            ]
        ):
            return "text explanation with optional mini case", "text-ok", "curve movement and consequence topics are clearer as source-bound explanation unless a graph change is requested"
        if any(
            marker in text
            for marker in [
                "ppc",
                "production possibility",
                "ped",
                "pes",
                "elasticity",
                "market failure",
                "government intervention",
                "taxation",
                "monetary policy",
                "supply-side policy",
                "economic growth",
                "recession",
                "inflation",
                "price changes",
                "wage determination",
                "differences in wages",
                "demand for factors",
            ]
        ):
            return "text explanation with optional mini case", "text-ok", "economic calculations, causes, and policies are clearer as source-bound text"
        if (
            any(
                phrase in title_text
                for phrase in [
                    "demand curve",
                    "supply curve",
                    "market equilibrium",
                    "market disequilibrium",
                    "determination of foreign exchange rate",
                    "foreign exchange rate",
                ]
            )
            or has_phrase("demand curve")
            or has_phrase("supply curve")
            or has_phrase("market equilibrium")
            or has_phrase("market disequilibrium")
            or has_phrase("determination of foreign exchange rate")
            or has_phrase("foreign exchange rate")
        ):
            return "demand-supply curve and market diagram", "svg-basic", "market relationships need precise curve axes and labels"
        if "price mechanism" in title_text:
            return "text explanation with optional mini case", "text-ok", "price mechanism can be explained as coordinated incentives without a separate curve"
        if any(has(word) for word in ["factor", "factors", "land", "labour", "capital", "enterprise", "production"]):
            return "text explanation with optional mini case", "text-ok", "production factors can be classified in text without a custom image"
        if any(has(word) for word in ["scarcity", "choice", "choices", "opportunity", "cost", "costs", "allocation"]):
            return "text explanation with optional mini case", "text-ok", "economic choice can be explained as a source-bound trade-off sentence"
        if any(has(word) for word in ["sector", "sectors", "primary", "secondary", "tertiary"]):
            return "text explanation with optional mini case", "text-ok", "sector classification is usually clear as a short case list"
        if any(has(word) for word in ["money", "bank", "financial", "interest"]):
            return "text explanation with optional mini case", "text-ok", "financial roles can be explained without a custom image unless a flow is explicitly requested"
        if any(has(word) for word in ["government", "inflation", "growth", "employment", "trade", "exchange", "imports", "exports"]):
            return "text explanation with optional mini case", "text-ok", "macroeconomic trade-offs are safer as text unless a specific diagram is named"
        if any(has(word) for word in ["business", "revenue", "profit", "profits", "cash"]):
            return "text explanation with optional mini case", "text-ok", "business cases can be handled with source-bound text and calculations"
        return "text explanation with optional mini case", "text-ok", "economic point can be explained without a custom visual"

    if profile.example_domain == "history":
        if any(has(word) for word in ["timeline", "chronology", "chronological", "sequence", "period"]):
            return "historical timeline visual", "svg-basic", "chronology needs a clear sequence of events or periods"
        if any(has(word) for word in ["source", "sources", "evidence", "interpretation", "reliability", "provenance"]):
            return "source evidence comparison visual", "svg-basic", "source work needs evidence, provenance, and inference side by side"
        if any(has(word) for word in ["change", "continuity", "similarity", "difference"]):
            return "change and continuity comparison visual", "svg-basic", "comparison history questions need a structured before-after organizer"
        if any(has(word) for word in ["cause", "causes", "consequence", "consequences", "impact", "significance"]) and any(
            has(word) for word in ["factor", "factors", "chain", "sequence"]
        ):
            return "cause and consequence chain", "svg-basic", "causal history questions need a chain from factor to result"
        return "text explanation with optional history organizer", "text-ok", "history point can be explained in text unless chronology, causation, source evidence, or comparison is central"

    if profile.example_domain == "chemistry":
        if any(has(word) for word in ["electrolysis", "reactivity"]):
            return "chemistry process infographic", "infographic", "electrolysis and reactivity need linked apparatus, particles, and observations"
        if any(has(word) for word in ["rate", "rates", "haber"]):
            return "reaction-rate graph and particle explanation", "svg-basic", "rate topics need a precise graph before any richer illustration"
        if any(has(word) for word in ["periodic", "group", "groups", "transition"]):
            return "text explanation with structured comparison", "text-ok", "periodic trends are safer as source-bound text unless a reviewed table is supplied"
        if any(
            phrase in text
            for phrase in [
                "conservation of mass",
                "amount of substance",
                "mole concept",
                "molar concentration",
                "molar concentrations",
                "quantitative",
            ]
        ) or any(has(word) for word in ["mole", "moles", "molar", "concentration", "concentrations"]):
            return "text explanation with worked calculation", "text-ok", "quantity topics are clearer as worked calculations than as separate images"
        if any(has(word) for word in ["bond", "bonds", "bonding", "ionic", "covalent", "metallic", "structure", "structures"]):
            return "bonding and structure model", "infographic", "bonding and structure relationships need visual spatial explanation"
        if any(has(word) for word in ["organic", "hydrocarbon", "hydrocarbons", "polymer", "polymers", "crude", "carboxylic"]):
            return "organic structure and reaction pathway infographic", "infographic", "organic structures and pathways need labelled visual representation"
        if any(has(word) for word in ["electrolysis", "reactivity"]):
            return "chemistry process infographic", "infographic", "electrolysis and reactivity need linked apparatus, particles, and observations"
        if any(has(word) for word in ["chromatography", "purity", "pure", "mixture", "mixtures", "separation"]):
            return "chromatography text explanation with optional method notes", "text-ok", "chromatography needs a reviewed labelled method diagram before visual delivery"
        if any(has(word) for word in ["salt", "salts", "redox", "equilibrium"]):
            return "text explanation with structured chemistry steps", "text-ok", "this chemistry relationship is safer as text unless a reviewed process diagram is supplied"
        if any(has(word) for word in ["solid", "liquid", "liquids", "particle", "particles", "atom", "atoms"]):
            return "particle model with labelled states", "svg-basic", "state changes are clearer with particle arrangement and movement"
        if (
            has_phrase("gas test")
            or has_phrase("gas tests")
            or any(has(word) for word in ["splint", "limewater", "ammonia", "oxygen", "hydrogen", "chlorine"])
        ):
            return "common gas tests observation chart", "svg-basic", "gas tests need a structured observation and conclusion chart"
        if any(has(word) for word in ["acid", "acids", "base", "bases", "alkali", "alkalis", "salt", "salts", "ph"]):
            return "pH scale and preparation flow diagram", "svg-basic", "scales and preparation flow are clearer as diagrams"
        if any(has(word) for word in ["rate", "rates", "haber"]):
            return "reaction-rate graph and particle explanation", "svg-basic", "rate topics need a precise graph before any richer illustration"
        if any(has(word) for word in ["energy", "exothermic", "endothermic"]):
            if "calculating" in text or "calculation" in text:
                return "text explanation with worked calculation", "text-ok", "energy calculations are clearer as worked calculations than as separate images"
            return "reaction energy profile diagram", "svg-basic", "energy profile curves are visual by nature"

    if profile.example_domain == "physics":
        if has_phrase("use the following units") or has("units"):
            return "text explanation with worked calculation", "text-ok", "unit lists are clearer as text and conversion practice"
        if has_phrase("distance-time") or has_phrase("speed-time") or has_phrase("velocity-time"):
            return "distance-time motion graph visual", "svg-basic", "motion graphs need axes and labelled line segments"
        if "falling objects" in text:
            return "text explanation with optional force notes", "text-ok", "falling-object force balance is safer as text unless a reviewed free-body diagram is supplied"
        if "force arrows" in text or "draw force arrows" in text:
            return "force and motion force arrows", "svg-basic", "explicit force-arrow tasks need a labelled free-body style diagram"
        if any(
            phrase in text
            for phrase in [
                "forces acting",
                "free-body",
                "free body",
                "unbalanced force",
                "resultant force",
            ]
        ):
            return "mechanics force or collision diagram", "svg-basic", "force questions need precise arrows and labels"
        if any(has(word) for word in ["circuit", "electricity", "current", "voltage", "magnet", "magnetic", "motor"]):
            return "text explanation with optional apparatus sketch", "text-ok", "electromagnetism is safer as text unless a reviewed apparatus diagram is supplied"
        if any(has(word) for word in ["pressure", "density", "gas", "gases", "temperature", "fission", "fusion", "radioactive"]):
            return "text explanation with worked calculation", "text-ok", "physics formula and nuclear topics are clearer as source-bound worked steps unless a reviewed diagram is supplied"
        return "text explanation with optional diagram", "text-ok", "physics point can be explained without a custom visual unless a graph, force diagram, or circuit is central"

    if profile.example_domain == "mathematics":
        if any(has(word) for word in ["surd", "surds", "rationalisation", "rationalization"]):
            return "text explanation with no custom visual", "text-ok", "surds are clearer as worked algebra steps than as a separate image"
        if has_phrase("laws of indices") or has_phrase("rational exponents"):
            return "text explanation with no custom visual", "text-ok", "index laws are clearer as worked algebra steps than as a separate image"
        if (
            has_phrase("number line")
            or has_phrase("fraction bar")
            or has_phrase("ratio diagram")
            or any(
                has(word)
                for word in [
                    "percentage",
                    "percentages",
                    "decimal",
                    "decimals",
                    "ratio",
                    "proportion",
                    "bounds",
                    "rounding",
                ]
            )
        ):
            return "number line, fraction bar, and ratio visual", "svg-basic", "number work is clearer with position, part-whole, and proportion diagrams"
        if has_phrase("number of possible outcomes will be finite") or (
            has_phrase("calculation of probabilities") and has("formula") and has("tables")
        ) or (
            has_phrase("assigning probabilities") and has_phrase("relative frequencies")
        ):
            return "text explanation with no custom visual", "text-ok", "probability formula and finite-outcome topics are clearer as worked calculations"
        if (
            has("venn")
            or has("subset")
            or has("subsets")
            or has("union")
            or has("complement")
            or has_phrase("set notation")
        ):
            return "set notation and Venn diagram", "svg-basic", "set notation needs regions and symbol labels"
        if has_phrase("effect of simple transformations on the graph") or (
            has("transformations") and has_phrase("graph of y = f")
        ):
            return "function graph transformation visual", "svg-basic", "function transformations need before-after graph sketches"
        if any(has(word) for word in ["matrix", "matrices", "vector", "vectors", "transformation", "transformations"]):
            return "transformation, matrix, or vector infographic", "infographic", "multi-step geometry movement and vector reasoning need a richer labelled visual"
        if any(has(word) for word in ["construction", "constructions", "locus", "loci", "bearing", "bearings"]):
            return "geometry construction or bearings infographic", "infographic", "construction and bearings diagrams need precise labels and step annotations"
        if any(
            has(word)
            for word in [
                "histogram",
                "histograms",
                "cumulative",
                "scatter",
                "statistics",
                "statistical",
                "chart",
                "charts",
                "data",
                "table",
                "tables",
                "measurement",
                "measurements",
            ]
        ) or (
            has_phrase("probability distributions")
            and not any(has(word) for word in ["mean", "variance", "deductions", "conditions"])
        ) or (
            has_phrase("binomial distribution")
            and not any(has(word) for word in ["mean", "variance", "deductions", "conditions", "calculation"])
        ):
            return "statistics chart visual", "svg-basic", "statistical chart topics need the exact chart structure"
        if has_phrase("probability tree") or any(has(word) for word in ["tree", "venn"]):
            return "probability tree or Venn visual", "svg-basic", "probability diagrams need branches or regions"
        if any(has(word) for word in ["trigonometry", "trigonometric", "sine", "cosine", "radian", "radians"]):
            if not any(
                phrase in text
                for phrase in [
                    "sine and cosine rules",
                    "sine, cosine and tangent functions",
                    "graphs, symmetries and periodicity",
                ]
            ):
                return "text explanation with no custom visual", "text-ok", "trigonometric formula topics can be taught with worked steps unless graph or triangle structure is central"
            return "trigonometry circle or graph visual", "svg-basic", "trigonometric ratios and graphs need angle or curve structure"
        if has_phrase("translation of circles"):
            return "text explanation with no custom visual", "text-ok", "circle translations can be taught by coordinate changes without a separate image"
        if any(has(word) for word in ["circle", "circles", "triangle", "triangles", "angle", "angles", "pythagoras"]):
            return "simple labelled geometry diagram", "svg-basic", "geometry shape relationships need labels"
        if has_phrase("motion in a straight line") and any(has(word) for word in ["graph", "graphs", "gradient", "gradients", "area"]):
            return "motion graph visual", "svg-basic", "motion graphs need axes, gradients, and area links"
        if any(has(word) for word in ["tangent", "gradient", "area", "regions", "curve", "curves", "x-axis"]):
            return "calculus graph and area annotation", "svg-basic", "calculus graph reasoning needs annotated graph features"
        if has_phrase("conditions for two straight lines") or has_phrase("product of the gradients"):
            return "text explanation with no custom visual", "text-ok", "parallel and perpendicular gradient rules are clearer as short worked algebra steps"
        if has_phrase("using algebraic methods"):
            return "text explanation with no custom visual", "text-ok", "algebraic intersection methods are clearer as equation-solving steps"
        if has_phrase("geometrical interpretation of algebraic solution"):
            return "text explanation with no custom visual", "text-ok", "geometrical interpretation can share the worked graph method without a duplicate visual"
        if any(has(word) for word in ["graph", "graphs", "sketch", "coordinate", "coordinates"]):
            return "function graph or coordinate visual", "svg-basic", "graphs and coordinate geometry are visual by nature"
        if has_phrase("distance-time") or has_phrase("speed-time") or has_phrase("velocity-time"):
            return "motion graph visual", "svg-basic", "motion graphs need axes and labelled line segments"
        if any(has(word) for word in ["force", "forces", "newton"]):
            if any(
                phrase in text
                for phrase in [
                    "force of gravity",
                    "normal reactions",
                    "resistive forces",
                    "tensions in strings",
                    "thrusts in rods",
                ]
            ):
                return "text explanation with no custom visual", "text-ok", "individual force definitions can be taught with notation and worked examples"
            if not (has("newton") or has_phrase("connected particle")):
                return "text explanation with no custom visual", "text-ok", "individual force definitions can be taught with notation and worked examples"
            return "mechanics force or collision diagram", "svg-basic", "mechanics questions need arrows, bodies, or before-after states"
        if any(has(word) for word in ["momentum", "impulse", "collision", "collisions"]):
            if not (has("collision") or has("collisions") or has_phrase("conservation of momentum") or has_phrase("direct impact")):
                return "text explanation with no custom visual", "text-ok", "momentum and impulse definitions can be taught with equations unless before-after states are central"
            return "mechanics before-after collision diagram", "svg-basic", "collision and momentum questions need a precise before-after schematic"
        return "text explanation with no custom visual", "text-ok", "symbolic mathematics can be taught with worked steps instead of a separate image"

    if profile.example_domain == "generic":
        if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
            return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
        return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

    if (
        has("venn")
        or has("sets")
        or has("subset")
        or has("subsets")
        or has("union")
        or has("complement")
        or has_phrase("set notation")
    ):
        return "set notation and Venn diagram infographic", "infographic", "set notation needs Venn regions and symbol labels, not a generic statistics chart"
    if any(
        has(word)
        for word in [
            "number",
            "numbers",
            "fraction",
            "fractions",
            "percentage",
            "percentages",
            "decimal",
            "decimals",
            "ratio",
            "proportion",
        ]
    ):
        return "number line, fraction bar, and ratio visual", "svg-basic", "number work is clearer with position, part-whole, and proportion diagrams"

    if any(has(word) for word in ["matrix", "matrices", "vector", "vectors", "transformation", "transformations"]):
        return "transformation, matrix, or vector infographic", "infographic", "multi-step geometry movement and vector reasoning need a richer labelled visual"
    if any(has(word) for word in ["construction", "constructions", "locus", "loci", "bearing", "bearings"]):
        return "geometry construction or bearings infographic", "infographic", "construction and bearings diagrams need precise labels and step annotations"
    if any(has(word) for word in ["histogram", "histograms", "cumulative", "sampling", "population"]):
        return "statistics method infographic", "infographic", "statistical representations need the exact chart type instead of a generic SVG"
    if any(
        has(word)
        for word in [
            "calculus",
            "derivative",
            "differentiation",
            "integral",
            "integration",
            "tangent",
            "gradient",
            "area",
            "regions",
            "x-axis",
        ]
    ):
        return "calculus graph and area annotation infographic", "infographic", "calculus, area, and graph reasoning need carefully annotated graph features"

    if any(
        has(word)
        for word in [
            "algebra",
            "function",
            "functions",
            "equation",
            "equations",
            "inequality",
            "inequalities",
            "sequence",
            "sequences",
        ]
    ):
        return "function graph and equation-balance visual", "svg-basic", "algebra is clearer when symbols connect to graphs and transformations"
    if any(
        has(word)
        for word in [
            "triangle",
            "triangles",
            "angle",
            "angles",
            "pythagoras",
        ]
    ):
        return "simple labelled triangle or angle diagram", "svg-basic", "simple geometry can be drawn accurately with deterministic SVG"
    if any(has(word) for word in ["geometry", "geometric", "measure", "measures", "mensuration", "trigonometry", "circle", "circles", "volume", "surface"]):
        return "geometry or mensuration infographic", "infographic", "non-trivial geometry needs diagrams that match the exact shape and labels"
    if any(
        has(word)
        for word in [
            "probability",
            "statistics",
            "statistical",
            "chart",
            "charts",
            "scatter",
            "correlation",
            "distribution",
            "distributions",
        ]
    ):
        return "statistics chart and probability visual", "svg-basic", "statistics and probability are clearer with charts, tables, and chance diagrams"
    if has_phrase("distance-time") or any(has(word) for word in ["speed", "distance"]):
        return "distance-time graph visual", "svg-basic", "distance-time graphs can be drawn safely with deterministic axes and a labelled line"
    if any(has(word) for word in ["force", "forces", "motion"]):
        return "force and motion infographic", "infographic", "force and motion questions need context-specific arrows and labels"
    if any(has(word) for word in ["graph", "graphs", "table", "tables", "data", "measurement", "measurements"]):
        return "data table and graph interpretation visual", "svg-basic", "data handling and graph reading are clearer with annotated visuals"
    return "text explanation with concept map only", "text-ok", "plain source-bound explanation is sufficient"

def is_scope_exclusion_text(text: str) -> bool:
    text = text.rsplit(":", 1)[-1]
    exclusion_phrases = [
        "will not be set",
        "will not be assessed",
        "is not required",
        "are not required",
        "not required",
        "not be required",
        "not expected",
        "outside the scope",
    ]
    if not any(phrase in text for phrase in exclusion_phrases):
        return False
    learning_terms = [
        "restricted to",
        "include",
        "includes",
        "including",
        "to include",
        "use of",
        "application of",
        "applications of",
    ]
    return not any(term in text for term in learning_terms)

def choose_provider_for_visual(
    complexity: str,
    run_options: GuideRunOptions,
    visual_type: str = "",
) -> str:
    if complexity == "svg-basic":
        if is_professional_diagram_visual(visual_type):
            return "kroki"
        return "deterministic-svg"
    if run_options.image_provider in {"prompt-queue", "deterministic-svg"}:
        return "external-generation-required"
    if run_options.image_provider == "custom":
        return f"custom:{run_options.image_model or 'model-not-set'}"
    return run_options.image_provider


def is_professional_diagram_visual(visual_type: str) -> bool:
    text = visual_type.lower()
    if any(
        term in text
        for term in [
            "axis",
            "curve",
            "graph",
            "number line",
            "venn",
            "triangle",
            "geometry",
            "ph",
            "particle",
            "rate",
            "energy",
            "motion",
            "force",
            "collision",
            "probability",
            "statistics",
            "chart",
            "table",
            "circle",
            "trigonometry",
            "calculus",
            "function",
        ]
    ):
        return False
    return any(
        term in text
        for term in [
            "flow",
            "workflow",
            "hierarchy",
            "chain",
            "map",
            "timeline",
            "comparison",
            "source evidence",
            "checkpoint",
            "reconciliation",
            "organisation structure",
            "stakeholder",
            "ownership",
            "segmentation",
        ]
    )
