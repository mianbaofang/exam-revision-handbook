from __future__ import annotations

import html
import re

from intl_exam_guide.models import VisualBrief


def render_topic_visual_svg(visual: VisualBrief, index: int, language: str = "en") -> str:
    if language == "zh-CN":
        return render_zh_visual_svg(visual, index)
    text = " ".join([visual.visual_type, visual.focus_point, *visual.source_points]).lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    if any(
        word in text
        for word in ["ledger", "book-of-prime-entry", "source-document", "accounting process"]
    ):
        return render_accounting_flow_svg(index, "en")
    if "trial balance" in text:
        return render_trial_balance_svg(index, "en")
    if "control account" in text:
        return render_control_account_svg(index, "en")
    if "error correction" in text or "suspense account" in text:
        return render_error_correction_svg(index, "en")
    if "incomplete records" in text:
        return render_incomplete_records_svg(index, "en")
    if "partnership appropriation" in text or "partnership accounts" in text:
        return render_accounting_statement_variant_svg(
            index,
            "Partnership accounts",
            ("Profit share", "Current accounts", "Capital", "Drawings"),
        )
    if "manufacturing account" in text or "manufacturing accounts" in text:
        return render_accounting_statement_variant_svg(
            index,
            "Manufacturing account",
            ("Raw materials", "Prime cost", "Factory overheads", "Production cost"),
        )
    if "club receipts" in text or "non-profit" in text or "clubs" in text:
        return render_accounting_statement_variant_svg(
            index,
            "Club and non-profit accounts",
            ("Receipts", "Payments", "Subscriptions", "Accumulated fund"),
        )
    if "limited company" in text or "limited companies" in text:
        return render_accounting_statement_variant_svg(
            index,
            "Limited company statements",
            ("Revenue", "Expenses", "Equity", "Retained earnings"),
        )
    if any(word in text for word in ["bank reconciliation", "reconciliation", "verification"]):
        return render_reconciliation_svg(index, "en")
    if any(
        word in text
        for word in [
            "financial-statement",
            "financial statement",
            "ratio-analysis",
            "ratio analysis",
        ]
    ):
        return render_financial_statement_svg(index, "en")
    if any(word in text for word in ["demand-supply", "demand supply", "market scenario"]):
        return render_market_svg(index, "en", market_variant_from_text(text))
    if any(word in text for word in ["stakeholder influence"]):
        return render_stakeholder_svg(index, "en")
    if any(word in text for word in ["business ownership"]):
        return render_business_comparison_svg(index, "en")
    if any(word in text for word in ["cash-flow", "cash flow"]):
        return render_cash_flow_svg(index, "en")
    if any(word in text for word in ["break-even", "break even"]):
        return render_break_even_svg(index, "en")
    if any(word in text for word in ["marketing mix"]):
        return render_marketing_mix_svg(index, "en")
    if "customer segmentation" in text:
        return render_customer_segmentation_svg(index, "en")
    if "organisation structure" in text:
        return render_organisation_structure_svg(index, "en")
    if "quality assurance" in text:
        return render_quality_checkpoint_svg(index, "en")
    if "operations flow" in text:
        return render_operations_flow_svg(index, "en")
    if any(word in text for word in ["business decision", "people and organisation"]):
        return render_business_process_svg(index, "en")
    if any(word in text for word in ["historical timeline"]):
        return render_history_timeline_svg(index, "en")
    if any(word in text for word in ["cause and consequence"]):
        return render_history_cause_svg(index, "en")
    if any(word in text for word in ["source evidence"]):
        return render_history_source_svg(index, "en")
    if any(word in text for word in ["change and continuity"]):
        return render_history_comparison_svg(index, "en")
    if any(
        word in text
        for word in [
            "factors of production",
            "production-chain",
            "opportunity-cost",
            "opportunity cost",
        ]
    ):
        return render_economic_flow_svg(index, "en")
    if any(word in text for word in ["force and motion", "force arrows"]):
        return render_force_svg(index, "en")
    if any(word in text for word in ["distance-time", "motion graph"]):
        if "area under" in text or "gradients and area" in text or "gradient and area" in text:
            return render_velocity_area_svg(index)
        return render_motion_svg(index)
    if any(word in text for word in ["function graph", "equation-balance"]):
        if any(word in text for word in ["kinematic", "motion graph", "velocity", "acceleration"]):
            return render_math_topic_svg(
                index, "Kinematics visual", visual.focus_point, "mechanics:kinematics"
            )
        if any(
            word in text
            for word in [
                "straight line",
                "gradient",
                "mid-point",
                "midpoint",
                "distance between two points",
            ]
        ):
            return render_math_topic_svg(
                index, "Coordinate geometry visual", visual.focus_point, "coordinate:line"
            )
        if any(word in text for word in ["intersection", "solution of equations", "simultaneous"]):
            return render_math_topic_svg(
                index, "Intersection visual", visual.focus_point, "algebra:simultaneous"
            )
        return render_math_topic_svg(
            index,
            "Function graph and equation balance",
            visual.focus_point,
            zh_math_variant("algebra", text),
        )
    if any(word in text for word in ["binomial distribution", "bernoulli"]):
        return render_math_topic_svg(
            index, "Binomial distribution visual", visual.focus_point, "probability:binomial"
        )
    if any(word in text for word in ["random variable", "variance", "standard deviation"]):
        return render_math_topic_svg(
            index, "Discrete random variable visual", visual.focus_point, "probability:table"
        )
    if "statistics chart" in text:
        return render_statistics_svg(index)
    if any(word in text for word in ["set notation", "venn"]):
        return render_venn_svg(index, "en")
    if (
        "circle" in text
        and "tangent function" not in text
        and "tangent functions" not in text
        and any(word in text for word in ["radius", "tangent", "normal", "coordinate geometry"])
    ):
        return render_math_topic_svg(
            index,
            "Circle and coordinate visual",
            visual.focus_point,
            zh_math_variant("coordinate", text),
        )
    if any(
        word in text
        for word in ["derivative", "differentiation", "gradient of the tangent", "stationary"]
    ):
        return render_math_topic_svg(
            index, "Differentiation visual", visual.focus_point, zh_math_variant("calculus", text)
        )
    if any(word in text for word in ["sine", "cosine", "trigonometry", "trigonometric", "radian"]):
        focus_text = " ".join([visual.focus_point, *visual.source_points]).lower()
        return render_math_topic_svg(
            index, "Trigonometry visual", visual.focus_point, zh_math_variant("trig", focus_text)
        )
    mechanics_text = " ".join([visual.focus_point, *visual.source_points]).lower()
    if any(
        word in text
        for word in [
            "momentum",
            "impulse",
            "impact",
            "collision",
            "newton",
            "force",
            "tension",
            "connected particle",
        ]
    ):
        if any(
            word in mechanics_text
            for word in ["fixed surface", "smooth surface", "perpendicular to a fixed"]
        ):
            return render_math_topic_svg(
                index, "Mechanics visual", visual.focus_point, "mechanics:fixed-impact"
            )
        if any(
            word in mechanics_text for word in ["connected particle", "pulley", "string", "trailer"]
        ):
            return render_math_topic_svg(
                index, "Mechanics visual", visual.focus_point, "mechanics:connected"
            )
        if any(word in mechanics_text for word in ["momentum", "impulse", "impact", "collision"]):
            return render_math_topic_svg(
                index, "Mechanics visual", visual.focus_point, "mechanics:momentum"
            )
        return render_math_topic_svg(
            index, "Mechanics visual", visual.focus_point, "mechanics:newton"
        )
    if any(
        word in text
        for word in ["velocity", "acceleration", "kinematic", "motion graph", "distance-time"]
    ):
        return render_math_topic_svg(
            index, "Kinematics visual", visual.focus_point, "mechanics:kinematics"
        )
    if any(word in text for word in ["circle", "radius"]):
        return render_math_topic_svg(
            index,
            "Circle and coordinate visual",
            visual.focus_point,
            zh_math_variant("coordinate", text),
        )
    if any(
        word in text
        for word in ["intersection", "equal roots", "distinct real roots", "no real roots"]
    ):
        return render_math_topic_svg(
            index, "Intersection visual", visual.focus_point, "coordinate:intersection"
        )
    if any(
        word in text
        for word in [
            "straight line",
            "gradient",
            "mid-point",
            "midpoint",
            "distance between two points",
        ]
    ):
        return render_math_topic_svg(
            index, "Coordinate geometry visual", visual.focus_point, "coordinate:line"
        )
    if any(word in text for word in ["trapezium"]):
        return render_math_topic_svg(
            index, "Trapezium-rule visual", visual.focus_point, "integral:trapezium"
        )
    if any(word in text for word in ["integral", "integration", "area under", "area of a region"]):
        return render_math_topic_svg(
            index, "Integration visual", visual.focus_point, zh_math_variant("integral", text)
        )
    if any(
        word in text
        for word in ["derivative", "differentiation", "stationary", "gradient of the tangent"]
    ):
        return render_math_topic_svg(
            index, "Differentiation visual", visual.focus_point, zh_math_variant("calculus", text)
        )
    if any(word in text for word in ["binomial distribution", "bernoulli"]):
        return render_math_topic_svg(
            index, "Binomial distribution visual", visual.focus_point, "probability:binomial"
        )
    if any(word in text for word in ["random variable", "variance", "standard deviation"]):
        return render_math_topic_svg(
            index, "Discrete random variable visual", visual.focus_point, "probability:table"
        )
    if any(word in text for word in ["probability", "relative frequency", "equally likely"]):
        return render_math_topic_svg(
            index, "Probability visual", visual.focus_point, "probability:bars"
        )
    if any(
        word in text
        for word in [
            "surd",
            "indices",
            "exponent",
            "quadratic",
            "factorisation",
            "completing the square",
            "discriminant",
            "polynomial",
            "inequality",
        ]
    ):
        return render_math_topic_svg(
            index, "Algebra visual", visual.focus_point, zh_math_variant("algebra", text)
        )
    if any(word in text for word in ["gas tests", "common gas"]):
        return render_gas_tests_svg(index, "en")
    if any(word in tokens for word in ["acid", "acids", "base", "bases", "salt", "salts", "ph"]):
        return render_ph_svg(index)
    if any(word in text for word in ["solid", "liquid", "particle", "atom"]):
        return render_particles_svg(index)
    if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
        return render_bonding_svg(index)
    if any(word in text for word in ["organic", "hydrocarbon", "carbon"]):
        return render_organic_svg(index)
    if any(
        word in text
        for word in [
            "chemical analysis",
            "chromatography",
            "identification of common gases",
            "identification of ions",
        ]
    ):
        return render_analysis_svg(index)
    if any(word in text for word in ["rate", "equilibrium"]):
        return render_rate_svg(index)
    if any(word in text for word in ["energy", "exothermic", "endothermic"]):
        return render_energy_svg(index)
    if any(word in text for word in ["number line", "fraction", "ratio"]):
        return render_number_svg(index)
    if "algebra" in text:
        return render_math_topic_svg(
            index, "Algebra visual", visual.focus_point, zh_math_variant("algebra", text)
        )
    if "probability" in text:
        return render_math_topic_svg(
            index, "Statistics visual", visual.focus_point, "probability:bars"
        )
    if any(
        word in text
        for word in ["geometry diagram", "triangle", "trigonometry", "pythagoras", "transformation"]
    ):
        return render_triangle_svg(index)
    if any(word in text for word in ["data table", "graph interpretation"]):
        return render_statistics_svg(index)
    return render_concept_fallback_svg(index, visual.visual_type or "Study visual")


def render_number_svg(index: int) -> str:
    ticks = []
    labels = []
    for value in range(-3, 4):
        x = 104 + (value + 3) * 56
        ticks.append(f'<path d="M{x} 170v16" stroke="#172033" stroke-width="3"/>')
        labels.append(
            f'<text x="{x - 7}" y="212" font-size="17" font-weight="800" fill="#172033">{value}</text>'
        )
    fraction_segments = []
    for number in range(4):
        color = "#1354a5" if number < 3 else "#edf4ff"
        fraction_segments.append(
            f'<rect x="{456 + number * 42}" y="112" width="42" height="56" fill="{color}" stroke="#172033" stroke-width="2"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Number line, fraction bar, and ratio diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="70" fill="#1354a5" font-size="23" font-weight="800">Number sense</text>
  <path d="M88 178h368" stroke="#172033" stroke-width="4" marker-end="url(#numarrow-{index})"/>
  <defs><marker id="numarrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {"".join(ticks)}
  {"".join(labels)}
  <circle cx="328" cy="178" r="10" fill="#b83246"/>
  <text x="92" y="238" font-size="15" fill="#5b677a">
    <tspan x="92" dy="0">compare positions</tspan>
    <tspan x="92" dy="20">then check decimals and bounds</tspan>
  </text>
  <text x="454" y="94" font-size="19" font-weight="800" fill="#b83246">3 / 4</text>
  {"".join(fraction_segments)}
  <text x="454" y="198" font-size="16" fill="#5b677a">fraction bar: part-whole</text>
  <rect x="456" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="522" y="238" width="58" height="40" rx="8" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <rect x="596" y="238" width="58" height="40" rx="8" fill="#fff1f3" stroke="#b83246" stroke-width="3"/>
  <text x="462" y="304" font-size="18" font-weight="800" fill="#1f7a5b">2</text>
  <text x="598" y="304" font-size="18" font-weight="800" fill="#b83246">1</text>
  <text x="504" y="314" font-size="15" fill="#5b677a">ratio blocks</text>
</svg>
"""


def render_algebra_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Function graph and equation balance</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Algebra links symbols to shapes</text>
  <rect x="58" y="92" width="282" height="210" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M96 262V118M96 262h210" stroke="#172033" stroke-width="4"/>
  <path d="M100 244C130 228 160 204 190 174C226 138 256 126 302 126" fill="none" stroke="#b83246" stroke-width="5"/>
  <path d="M97 207h208M145 262V120M195 262V120M245 262V120" stroke="#d7deea" stroke-width="2"/>
  <text x="110" y="136" font-size="18" font-weight="800" fill="#b83246">graph of a rule</text>
  <text x="248" y="286" font-size="17" font-weight="800">x</text>
  <text x="76" y="130" font-size="17" font-weight="800">y</text>
  <rect x="396" y="104" width="260" height="178" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <path d="M526 138v88M448 226h156" stroke="#172033" stroke-width="5" stroke-linecap="round"/>
  <path d="M468 154l-42 72h84z" fill="#edf4ff" stroke="#1354a5" stroke-width="3"/>
  <path d="M584 154l-42 72h84z" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <text x="436" y="205" font-size="25" font-weight="800" fill="#1354a5">x + 3</text>
  <text x="564" y="205" font-size="25" font-weight="800" fill="#1f7a5b">7</text>
  <text x="430" y="82" font-size="18" font-weight="800" fill="#d99a24">equation balance</text>
  <text x="418" y="314" font-size="16" fill="#5b677a">transform both sides, then check the solution</text>
</svg>
"""


def render_statistics_svg(index: int) -> str:
    points = [(300, 228), (328, 205), (358, 214), (388, 174), (424, 158), (456, 126)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#b83246"/>' for x, y in points)
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Statistics chart and probability visual</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="52" y="68" fill="#1354a5" font-size="23" font-weight="800">Data becomes evidence</text>
  <rect x="58" y="94" width="178" height="190" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <path d="M92 246V126M92 246h112" stroke="#172033" stroke-width="4"/>
  <rect x="108" y="200" width="24" height="46" fill="#1354a5"/>
  <rect x="144" y="170" width="24" height="76" fill="#1f7a5b"/>
  <rect x="180" y="140" width="24" height="106" fill="#d99a24"/>
  <text x="78" y="274" font-size="14" fill="#5b677a">compare groups</text>
  <rect x="268" y="94" width="210" height="190" rx="14" fill="#fffaf1" stroke="#d99a24"/>
  <path d="M300 246V120M300 246h168" stroke="#172033" stroke-width="4"/>
  {dots}
  <path d="M300 236L462 124" stroke="#1f7a5b" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="310" y="274" font-size="14" fill="#5b677a">describe trend</text>
  <rect x="510" y="94" width="150" height="190" rx="14" fill="#fff7f8" stroke="#e5aab4"/>
  <circle cx="545" cy="164" r="7" fill="#b83246"/>
  <path d="M552 164h28M580 164l38-42M580 164l38 42" stroke="#172033" stroke-width="3" fill="none"/>
  <circle cx="624" cy="122" r="7" fill="#1f7a5b"/>
  <circle cx="624" cy="206" r="7" fill="#d99a24"/>
  <text x="528" y="238" font-size="14" fill="#5b677a">probability tree</text>
</svg>
"""


def render_particles_svg(index: int) -> str:
    dots = []
    for row in range(3):
        for col in range(4):
            dots.append(
                f'<circle cx="{92 + col * 22}" cy="{102 + row * 22}" r="7" fill="#1354a5"/>'
            )
    liquid = [
        '<circle cx="330" cy="118" r="8" fill="#1f7a5b"/>',
        '<circle cx="356" cy="132" r="8" fill="#1f7a5b"/>',
        '<circle cx="315" cy="150" r="8" fill="#1f7a5b"/>',
        '<circle cx="372" cy="164" r="8" fill="#1f7a5b"/>',
        '<circle cx="342" cy="176" r="8" fill="#1f7a5b"/>',
    ]
    gas = [
        '<circle cx="535" cy="92" r="8" fill="#b83246"/>',
        '<circle cx="606" cy="125" r="8" fill="#b83246"/>',
        '<circle cx="558" cy="180" r="8" fill="#b83246"/>',
    ]
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Particle model diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="48" y="58" fill="#b83246" font-size="20" font-weight="800">Particle model</text>
  <rect x="70" y="82" width="130" height="130" rx="14" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="290" y="82" width="130" height="130" rx="14" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="510" y="82" width="130" height="130" rx="14" fill="#fff1f3" stroke="#e5aab4"/>
  {"".join(dots)}
  {"".join(liquid)}
  {"".join(gas)}
  <path d="M220 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <path d="M440 146h48" stroke="#d99a24" stroke-width="4" marker-end="url(#arrow-{index})"/>
  <defs><marker id="arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
  <text x="92" y="250" font-size="22" font-weight="800" fill="#1354a5">solid</text>
  <text x="322" y="250" font-size="22" font-weight="800" fill="#1f7a5b">liquid</text>
  <text x="552" y="250" font-size="22" font-weight="800" fill="#b83246">gas</text>
  <text x="70" y="292" font-size="16" fill="#5b677a">arrangement and movement explain state changes</text>
</svg>
"""


def render_triangle_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Right triangle diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="62" y="70" fill="#1354a5" font-size="22" font-weight="800">5-12-13 right triangle</text>
  <path d="M220 285h92L220 65z" fill="#ffffff" stroke="#111827" stroke-width="5"/>
  <path d="M220 259h26v26" fill="none" stroke="#111827" stroke-width="4"/>
  <text x="187" y="67" font-size="34" font-weight="800">A</text>
  <text x="320" y="306" font-size="34" font-weight="800">B</text>
  <text x="187" y="306" font-size="34" font-weight="800">C</text>
  <text x="245" y="324" font-size="25" font-weight="700">5 cm</text>
  <text x="120" y="184" font-size="25" font-weight="700">12 cm</text>
  <text x="288" y="166" font-size="25" font-weight="700">13 cm</text>
  <rect x="440" y="108" width="190" height="130" rx="14" fill="#f7fbff" stroke="#9cbce8"/>
  <text x="466" y="150" font-size="22" font-weight="800" fill="#b83246">c² = a² + b²</text>
  <text x="466" y="188" font-size="19" fill="#172033">5² + 12² = 169</text>
  <text x="466" y="222" font-size="19" fill="#172033">c = 13 cm</text>
</svg>
"""


def render_motion_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Distance-time graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="23" font-weight="800">Distance-time graph</text>
  <path d="M100 280V92M100 280h500" stroke="#172033" stroke-width="4"/>
  <path d="M105 255L235 195L365 195L540 105" fill="none" stroke="#1354a5" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="105" cy="255" r="7" fill="#b83246"/>
  <circle cx="235" cy="195" r="7" fill="#b83246"/>
  <circle cx="365" cy="195" r="7" fill="#b83246"/>
  <circle cx="540" cy="105" r="7" fill="#b83246"/>
  <path d="M235 195h130" stroke="#d99a24" stroke-width="5"/>
  <text x="118" y="104" font-size="17" font-weight="800" fill="#b83246">distance</text>
  <text x="552" y="310" font-size="17" font-weight="800" fill="#1f7a5b">time</text>
  <text x="128" y="236" font-size="16" fill="#5b677a">moving</text>
  <text x="260" y="184" font-size="16" fill="#9b6a10">stationary</text>
  <text x="430" y="136" font-size="16" fill="#5b677a">faster speed</text>
  <text x="104" y="322" font-size="15" fill="#5b677a">steeper line = greater speed</text>
</svg>
"""


def render_velocity_area_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Velocity-time graph: gradient and area</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="54" y="70" fill="#1354a5" font-size="23" font-weight="800">Velocity-time graph</text>
  <path d="M92 282V86M92 282h520" stroke="#172033" stroke-width="4"/>
  <path d="M116 248L268 130L480 130L590 210" fill="none" stroke="#1354a5" stroke-width="6" stroke-linejoin="round"/>
  <path d="M116 248L268 130H480L590 210V282H116z" fill="#1354a5" opacity="0.12"/>
  <path d="M146 224L246 146" stroke="#b83246" stroke-width="5" marker-end="url(#vel-grad-{index})"/>
  <path d="M304 132v148M480 132v148" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="116" y="104" font-size="17" font-weight="800" fill="#b83246">velocity</text>
  <text x="560" y="312" font-size="17" font-weight="800" fill="#1f7a5b">time</text>
  <text x="262" y="116" font-size="16" font-weight="800" fill="#1354a5">constant velocity</text>
  <text x="170" y="202" font-size="16" font-weight="800" fill="#b83246">gradient = acceleration</text>
  <text x="284" y="258" font-size="16" font-weight="800" fill="#9b6a10">area = displacement</text>
  <defs>
    <marker id="vel-grad-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0 10 5 0 10z" fill="#b83246"/>
    </marker>
  </defs>
</svg>
"""


def render_rate_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Rate of reaction graph</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M95 275V70M95 275h520" stroke="#172033" stroke-width="4"/>
  <path d="M100 260C180 150 255 100 410 94C500 91 565 91 615 91" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M100 260C170 190 250 160 420 156C505 154 570 154 615 154" fill="none" stroke="#d99a24" stroke-width="6"/>
  <text x="118" y="66" font-size="18" font-weight="800" fill="#b83246">product formed</text>
  <text x="548" y="306" font-size="18" font-weight="800" fill="#1f7a5b">time</text>
  <text x="430" y="88" font-size="18" fill="#1354a5">faster rate</text>
  <text x="430" y="150" font-size="18" fill="#9b6a10">slower rate</text>
</svg>
"""


def render_energy_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Reaction energy profile</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <path d="M90 280V70M90 280h540" stroke="#172033" stroke-width="4"/>
  <path d="M120 245C230 245 235 88 350 88C465 88 470 185 600 185" fill="none" stroke="#b83246" stroke-width="6"/>
  <path d="M145 245h92M505 185h92" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M350 98v135" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 7"/>
  <text x="120" y="270" font-size="17" font-weight="800">reactants</text>
  <text x="500" y="210" font-size="17" font-weight="800">products</text>
  <text x="365" y="160" font-size="18" fill="#9b6a10">activation energy</text>
  <text x="110" y="62" font-size="18" font-weight="800" fill="#b83246">energy</text>
</svg>
"""


def render_ph_svg(index: int) -> str:
    segments = []
    colors = ["#b83246", "#d45c3f", "#d99a24", "#95b84a", "#1f7a5b", "#217c9b", "#1354a5"]
    for i, color in enumerate(colors):
        segments.append(f'<rect x="{84 + i * 76}" y="146" width="76" height="54" fill="{color}"/>')
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">pH scale and salt preparation</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="88" font-size="24" font-weight="800" fill="#1354a5">pH scale</text>
  {"".join(segments)}
  <text x="86" y="226" font-size="18" font-weight="800">0</text>
  <text x="300" y="226" font-size="18" font-weight="800">7</text>
  <text x="590" y="226" font-size="18" font-weight="800">14</text>
  <text x="94" y="130" font-size="18" fill="#b83246">acid</text>
  <text x="312" y="130" font-size="18" fill="#1f7a5b">neutral</text>
  <text x="548" y="130" font-size="18" fill="#1354a5">alkali</text>
</svg>
"""


def render_organic_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Hydrocarbon chain diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="82" font-size="24" font-weight="800" fill="#1354a5">hydrocarbon model</text>
  <path d="M178 178h100h100h100" stroke="#172033" stroke-width="5"/>
  <g fill="#1354a5" stroke="#172033" stroke-width="3">
    <circle cx="178" cy="178" r="32"/><circle cx="278" cy="178" r="32"/>
    <circle cx="378" cy="178" r="32"/><circle cx="478" cy="178" r="32"/>
  </g>
  <g fill="#ffffff" font-size="24" font-weight="800" text-anchor="middle">
    <text x="178" y="187">C</text><text x="278" y="187">C</text>
    <text x="378" y="187">C</text><text x="478" y="187">C</text>
  </g>
  <text x="160" y="272" font-size="18" fill="#5b677a">structure helps explain reactions and properties</text>
</svg>
"""


def render_analysis_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Chromatography diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="140" y="72" width="170" height="235" rx="18" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <path d="M170 250h110" stroke="#1354a5" stroke-width="4"/>
  <path d="M225 250V98" stroke="#172033" stroke-width="3"/>
  <circle cx="225" cy="223" r="11" fill="#b83246"/>
  <circle cx="225" cy="178" r="11" fill="#d99a24"/>
  <circle cx="225" cy="130" r="11" fill="#1f7a5b"/>
  <path d="M430 96h105M430 154h105M430 212h105" stroke="#d7deea" stroke-width="4"/>
  <text x="430" y="88" font-size="18" font-weight="800" fill="#1f7a5b">separated spots</text>
  <text x="430" y="246" font-size="18" fill="#5b677a">compare position and colour</text>
</svg>
"""


def render_bonding_svg(index: int) -> str:
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">Bonding and structure diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="70" y="74" font-size="24" font-weight="800" fill="#1354a5">bonding model</text>
  <rect x="74" y="104" width="150" height="150" rx="16" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="285" y="104" width="150" height="150" rx="16" fill="#ecf8f3" stroke="#a7d5c3"/>
  <rect x="496" y="104" width="150" height="150" rx="16" fill="#fff1f3" stroke="#e5aab4"/>
  <g fill="#1354a5"><circle cx="124" cy="150" r="16"/><circle cx="174" cy="150" r="16"/><circle cx="124" cy="202" r="16"/><circle cx="174" cy="202" r="16"/></g>
  <g fill="#ffffff" font-size="15" font-weight="800" text-anchor="middle"><text x="124" y="155">+</text><text x="174" y="155">-</text><text x="124" y="207">-</text><text x="174" y="207">+</text></g>
  <g stroke="#172033" stroke-width="4"><path d="M332 178h56"/><path d="M360 150v56"/></g>
  <g fill="#1f7a5b"><circle cx="332" cy="178" r="18"/><circle cx="388" cy="178" r="18"/><circle cx="360" cy="150" r="18"/><circle cx="360" cy="206" r="18"/></g>
  <g fill="#b83246"><circle cx="542" cy="150" r="16"/><circle cx="600" cy="150" r="16"/><circle cx="542" cy="204" r="16"/><circle cx="600" cy="204" r="16"/></g>
  <path d="M526 176h90M571 132v92" stroke="#d99a24" stroke-width="3" stroke-dasharray="6 6"/>
  <text x="116" y="286" font-size="20" font-weight="800" fill="#1354a5">ionic</text>
  <text x="315" y="286" font-size="20" font-weight="800" fill="#1f7a5b">covalent</text>
  <text x="530" y="286" font-size="20" font-weight="800" fill="#b83246">metallic</text>
</svg>
"""


def render_accounting_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("原始凭证", "日记账", "分类账", "试算平衡")
        if zh
        else ("Source document", "Prime entry", "Ledger", "Trial balance")
    )
    title = "会计记录流程" if zh else "Accounting records flow"
    return render_flow_svg(index, title, labels, "#1354a5", "#1f7a5b")


def render_reconciliation_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("现金账", "银行对账单", "差异项目", "调整后余额")
        if zh
        else ("Cash book", "Bank statement", "Timing items", "Adjusted balance")
    )
    title = "核对与调节流程" if zh else "Verification and reconciliation"
    return render_flow_svg(index, title, labels, "#1f7a5b", "#d99a24")


def render_trial_balance_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Trial balance verification table" if not zh else "试算平衡核对表"
    headers = ("Debit", "Credit") if not zh else ("借方", "贷方")
    rows = (("Cash", "1 200", ""), ("Sales", "", "1 200"), ("Totals", "1 200", "1 200"))
    body = []
    for row_index, row in enumerate(rows):
        y = 132 + row_index * 50
        body.append(
            f'<rect x="116" y="{y - 30}" width="488" height="46" fill="#fbfcff" stroke="#d7deea"/>'
        )
        body.append(
            f'<text x="142" y="{y}" font-size="17" font-weight="800" fill="#1354a5">{html_escape(row[0])}</text>'
        )
        body.append(
            f'<text x="344" y="{y}" font-size="17" font-weight="800" fill="#172033">{html_escape(row[1])}</text>'
        )
        body.append(
            f'<text x="502" y="{y}" font-size="17" font-weight="800" fill="#172033">{html_escape(row[2])}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <text x="340" y="96" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[0])}</text>
  <text x="494" y="96" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[1])}</text>
  {"".join(body)}
  <text x="142" y="304" font-size="16" fill="#5b677a">equal totals reveal arithmetical balance, not every error</text>
</svg>
"""


def render_control_account_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Subsidiary ledger", "Control account", "Compare totals", "Investigate difference")
        if not zh
        else ("明细账", "控制账户", "比较合计", "追查差异")
    )
    title = "Control account reconciliation" if not zh else "控制账户核对"
    return render_flow_svg(index, title, labels, "#1354a5", "#b83246")


def render_error_correction_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Find error", "Classify type", "Journal correction", "Check suspense")
        if not zh
        else ("发现错误", "判断类型", "日记账更正", "检查暂记账")
    )
    title = "Error correction and suspense flow" if not zh else "错账更正流程"
    return render_flow_svg(index, title, labels, "#b83246", "#1f7a5b")


def render_incomplete_records_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Known figures", "Missing account", "Reconstruct total", "Use in statements")
        if not zh
        else ("已知数据", "缺失账户", "重建合计", "填入报表")
    )
    title = "Incomplete records reconstruction" if not zh else "不完整记录重建"
    return render_flow_svg(index, title, labels, "#d99a24", "#1354a5")


def render_financial_statement_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "财务报表结构" if zh else "Financial statement layout"
    labels = (
        ("收入", "成本", "利润", "资产", "负债", "资本")
        if zh
        else ("Revenue", "Cost", "Profit", "Assets", "Liabilities", "Capital")
    )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="64" y="104" width="260" height="198" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="396" y="104" width="260" height="198" rx="14" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  <text x="88" y="142" font-size="20" font-weight="800" fill="#b83246">{html_escape(labels[0])}</text>
  <text x="88" y="182" font-size="20" font-weight="800" fill="#172033">- {html_escape(labels[1])}</text>
  <path d="M88 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="88" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[2])}</text>
  <text x="420" y="142" font-size="20" font-weight="800" fill="#1354a5">{html_escape(labels[3])}</text>
  <text x="420" y="184" font-size="20" font-weight="800" fill="#b83246">- {html_escape(labels[4])}</text>
  <path d="M420 205h190" stroke="#d7deea" stroke-width="4"/>
  <text x="420" y="246" font-size="22" font-weight="800" fill="#1f7a5b">= {html_escape(labels[5])}</text>
</svg>
"""


def render_accounting_statement_variant_svg(
    index: int, title: str, labels: tuple[str, str, str, str]
) -> str:
    lower = title.lower()
    safe_title = html_escape(title)
    safe_labels = tuple(html_escape(label) for label in labels)
    if "partnership" in lower:
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="24" font-weight="800">{safe_title}</text>
  <rect x="64" y="104" width="258" height="74" rx="12" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <text x="86" y="136" font-size="18" font-weight="800" fill="#172033">{safe_labels[0]}</text>
  <path d="M92 154h202" stroke="#d99a24" stroke-width="4"/>
  <text x="86" y="170" font-size="14" fill="#5b677a">appropriation before partner balances</text>
  <rect x="392" y="104" width="104" height="172" rx="10" fill="#f7fbff" stroke="#1354a5" stroke-width="3"/>
  <rect x="526" y="104" width="104" height="172" rx="10" fill="#f7fbff" stroke="#1354a5" stroke-width="3"/>
  <path d="M444 116v148M578 116v148M402 152h84M536 152h84" stroke="#172033" stroke-width="3"/>
  <text x="444" y="96" text-anchor="middle" font-size="15" font-weight="800" fill="#1354a5">Partner A</text>
  <text x="578" y="96" text-anchor="middle" font-size="15" font-weight="800" fill="#1354a5">Partner B</text>
  <text x="414" y="184" font-size="13" fill="#b83246">{safe_labels[3]}</text>
  <text x="548" y="184" font-size="13" fill="#b83246">{safe_labels[3]}</text>
  <path d="M322 142C356 142 358 188 392 188" fill="none" stroke="#1f7a5b" stroke-width="4" marker-end="url(#acct-partner-{index})"/>
  <text x="82" y="236" font-size="16" font-weight="800" fill="#1f7a5b">{safe_labels[1]} connect profit share to capital/current balances</text>
  <defs><marker id="acct-partner-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker></defs>
</svg>
"""
    if "manufacturing" in lower:
        nodes = []
        for pos, label in enumerate(safe_labels):
            y = 92 + pos * 58
            nodes.append(
                f'<rect x="230" y="{y}" width="260" height="40" rx="10" fill="#f7fbff" stroke="#1354a5" stroke-width="3"/>'
            )
            nodes.append(
                f'<text x="360" y="{y + 26}" text-anchor="middle" font-size="16" font-weight="800" fill="#172033">{label}</text>'
            )
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="24" font-weight="800">{safe_title}</text>
  {"".join(nodes)}
  <path d="M360 132v18M360 190v18M360 248v18" stroke="#d99a24" stroke-width="5" marker-end="url(#acct-mfg-{index})"/>
  <path d="M104 164h92v94h92" fill="none" stroke="#1f7a5b" stroke-width="4"/>
  <text x="76" y="156" font-size="15" font-weight="800" fill="#1f7a5b">add overheads</text>
  <text x="500" y="270" font-size="15" fill="#5b677a">cost flow, not final sales revenue</text>
  <defs><marker id="acct-mfg-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
</svg>
"""
    if "club" in lower or "non-profit" in lower:
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="24" font-weight="800">{safe_title}</text>
  <rect x="62" y="104" width="260" height="188" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="398" y="104" width="260" height="188" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <text x="192" y="136" text-anchor="middle" font-size="18" font-weight="800" fill="#9b6a10">{safe_labels[0]} and {safe_labels[1]}</text>
  <path d="M96 160h190M96 208h190M96 256h190" stroke="#d7deea" stroke-width="3"/>
  <circle cx="112" cy="184" r="10" fill="#d99a24"/><circle cx="112" cy="232" r="10" fill="#b83246"/>
  <text x="130" y="190" font-size="15" fill="#172033">cash book movement</text>
  <text x="130" y="238" font-size="15" fill="#172033">not all income/expense</text>
  <text x="528" y="136" text-anchor="middle" font-size="18" font-weight="800" fill="#1f7a5b">Income and expenditure</text>
  <path d="M432 160h190M432 208h190M432 256h190" stroke="#d7deea" stroke-width="3"/>
  <text x="448" y="188" font-size="15" font-weight="800" fill="#1354a5">{safe_labels[2]}</text>
  <text x="448" y="236" font-size="15" font-weight="800" fill="#1354a5">{safe_labels[3]}</text>
  <path d="M322 198h64" stroke="#1354a5" stroke-width="5" stroke-dasharray="8 6" marker-end="url(#acct-club-{index})"/>
  <defs><marker id="acct-club-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1354a5"/></marker></defs>
</svg>
"""
    rows = []
    for pos, label in enumerate(safe_labels):
        y = 118 + pos * 48
        fill = "#edf4ff" if pos % 2 == 0 else "#ecf8f3"
        stroke = "#1354a5" if pos % 2 == 0 else "#1f7a5b"
        rows.append(
            f'<rect x="92" y="{y}" width="254" height="36" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
        )
        rows.append(
            f'<text x="116" y="{y + 24}" font-size="16" font-weight="800" fill="#172033">{label}</text>'
        )
        rows.append(
            f'<rect x="420" y="{y}" width="180" height="36" rx="10" fill="#ffffff" stroke="#d7deea" stroke-width="3"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{safe_title}</text>
  <text x="420" y="102" font-size="15" font-weight="800" fill="#b83246">amount / movement</text>
  {"".join(rows)}
  <path d="M346 136h58M346 184h58M346 232h58M346 280h58" stroke="#d99a24" stroke-width="4" marker-end="url(#acct-var-{index})"/>
  <defs><marker id="acct-var-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
</svg>
"""


def market_variant_from_text(text: str) -> str:
    focus = text.lower()
    if "disequilibrium" in focus:
        return "disequilibrium"
    if "foreign exchange" in focus or "exchange rate" in focus:
        return "foreign_exchange"
    supply_shift_clues = [
        "changes in supply",
        "change in supply",
        "supply curve shifts",
        "shifts of a supply curve",
        "shift of a supply curve",
        "determine the supply",
        "supply for goods",
        "supply of goods",
        "increase in supply",
        "decrease in supply",
    ]
    demand_shift_clues = [
        "changes in demand",
        "change in demand",
        "demand curve shifts",
        "shifts of a demand curve",
        "shift of a demand curve",
        "determine the demand",
        "demand for goods",
        "demand of goods",
        "increase in demand",
        "decrease in demand",
    ]
    if any(clue in focus for clue in supply_shift_clues):
        return "supply"
    if any(clue in focus for clue in demand_shift_clues):
        return "demand"
    return "equilibrium"


def render_market_svg(index: int, language: str, variant: str = "equilibrium") -> str:
    zh = language == "zh-CN"
    title = "市场供需图" if zh else "Demand and supply market diagram"
    demand = "需求" if zh else "Demand"
    supply = "供给" if zh else "Supply"
    price = "价格" if zh else "Price"
    qty = "数量" if zh else "Quantity"
    equilibrium = "均衡" if zh else "Equilibrium"
    if variant == "foreign_exchange":
        market = "外汇市场" if zh else "Foreign exchange market"
        currency = "货币数量" if zh else "Quantity of currency"
        rate = "汇率" if zh else "Exchange rate"
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(market)} rate diagram</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(market)}</text>
  <path d="M118 286V88M118 286h478" stroke="#172033" stroke-width="4"/>
  <path d="M160 126C258 144 396 196 560 266" fill="none" stroke="#b83246" stroke-width="6"/>
  <path d="M164 268C286 224 430 156 566 112" fill="none" stroke="#1f7a5b" stroke-width="6"/>
  <circle cx="358" cy="188" r="10" fill="#d99a24"/>
  <path d="M358 188v98M118 188h240" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="134" y="92" font-size="17" font-weight="800">{html_escape(rate)}</text>
  <text x="456" y="318" font-size="17" font-weight="800">{html_escape(currency)}</text>
  <text x="530" y="132" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)} of currency</text>
  <text x="530" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)} for currency</text>
  <text x="376" y="184" font-size="17" font-weight="800" fill="#9b6a10">rate</text>
</svg>
"""
    if variant == "disequilibrium":
        shortage = "短缺" if zh else "Shortage"
        surplus = "过剩" if zh else "Surplus"
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)} - disequilibrium</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">Market disequilibrium</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M150 118L548 260" stroke="#b83246" stroke-width="6"/>
  <path d="M150 260L548 118" stroke="#1f7a5b" stroke-width="6"/>
  <path d="M198 144h312" stroke="#d99a24" stroke-width="5" stroke-dasharray="9 7"/>
  <path d="M198 234h312" stroke="#6c63ff" stroke-width="5" stroke-dasharray="9 7"/>
  <path d="M236 144v90M470 144v90" stroke="#172033" stroke-width="3"/>
  <text x="250" y="136" font-size="17" font-weight="800" fill="#9b6a10">{html_escape(surplus)}</text>
  <text x="312" y="256" font-size="17" font-weight="800" fill="#544bd1">{html_escape(shortage)}</text>
  <text x="552" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)}</text>
  <text x="552" y="126" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
</svg>
"""
    if variant == "demand":
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)} - {html_escape(demand)} shift</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(demand)} shift in a market</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M166 118L552 258" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M146 250L502 120" stroke="#b83246" stroke-width="5" stroke-dasharray="9 7"/>
  <path d="M196 260L552 130" stroke="#b83246" stroke-width="7"/>
  <path d="M328 176C370 160 408 152 446 146" fill="none" stroke="#d99a24" stroke-width="4" marker-end="url(#market-demand-{index})"/>
  <circle cx="328" cy="184" r="8" fill="#d99a24"/>
  <circle cx="392" cy="176" r="8" fill="#d99a24"/>
  <text x="504" y="124" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)} increases</text>
  <text x="552" y="264" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
  <defs><marker id="market-demand-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
</svg>
"""
    if variant == "supply":
        return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)} - {html_escape(supply)} shift</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(supply)} shift in a market</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M154 122L546 260" stroke="#b83246" stroke-width="5"/>
  <path d="M164 270L524 116" stroke="#1f7a5b" stroke-width="5" stroke-dasharray="9 7"/>
  <path d="M214 270L574 116" stroke="#1f7a5b" stroke-width="7"/>
  <path d="M342 190C382 204 420 218 456 232" fill="none" stroke="#d99a24" stroke-width="4" marker-end="url(#market-supply-{index})"/>
  <circle cx="342" cy="190" r="8" fill="#d99a24"/>
  <circle cx="410" cy="206" r="8" fill="#d99a24"/>
  <text x="542" y="114" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)} increases</text>
  <text x="554" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
  <defs><marker id="market-supply-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
</svg>
"""
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="60" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <path d="M118 284V92M118 284h470" stroke="#172033" stroke-width="4"/>
  <path d="M150 118L548 260" stroke="#b83246" stroke-width="6"/>
  <path d="M150 260L548 118" stroke="#1f7a5b" stroke-width="6"/>
  <circle cx="350" cy="188" r="10" fill="#d99a24"/>
  <path d="M350 188v96M118 188h232" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="555" y="266" font-size="18" font-weight="800" fill="#b83246">{html_escape(demand)}</text>
  <text x="552" y="126" font-size="18" font-weight="800" fill="#1f7a5b">{html_escape(supply)}</text>
  <text x="132" y="96" font-size="17" font-weight="800">{html_escape(price)}</text>
  <text x="520" y="314" font-size="17" font-weight="800">{html_escape(qty)}</text>
  <text x="366" y="184" font-size="17" font-weight="800" fill="#9b6a10">{html_escape(equilibrium)}</text>
</svg>
"""


def render_stakeholder_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Stakeholder influence map" if not zh else "利益相关者影响图"
    center = "Business decision" if not zh else "企业决策"
    labels = (
        ("Owners", "Employees", "Customers", "Suppliers", "Community")
        if not zh
        else ("所有者", "员工", "顾客", "供应商", "社区")
    )
    positions = [(350, 102), (188, 166), (512, 166), (246, 266), (454, 266)]
    nodes = []
    for label, (x, y) in zip(labels, positions, strict=True):
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="48" fill="#f7fbff" stroke="#1354a5" stroke-width="3"/>'
        )
        nodes.append(
            f'<text x="{x}" y="{y + 5}" font-size="15" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(label)}</text>'
        )
        nodes.append(
            f'<path d="M{x} {y + (40 if y < 190 else -40)}L350 190" stroke="#d99a24" stroke-width="3" stroke-dasharray="6 6"/>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="270" y="156" width="160" height="70" rx="16" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <text x="350" y="198" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(center)}</text>
  {"".join(nodes)}
</svg>
"""


def render_business_comparison_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Business ownership comparison" if not zh else "企业所有制比较"
    headers = ("Control", "Risk", "Finance") if not zh else ("控制权", "风险", "资金")
    rows = (
        (
            ("Sole trader", "High", "Unlimited", "Owner savings"),
            ("Partnership", "Shared", "Unlimited", "Partners"),
            ("Ltd company", "Directors", "Limited", "Shares"),
        )
        if not zh
        else (
            ("个体经营", "高", "无限", "自有资金"),
            ("合伙", "共享", "无限", "合伙人"),
            ("有限公司", "董事", "有限", "股份"),
        )
    )
    row_svg = []
    for row_index, row in enumerate(rows):
        y = 132 + row_index * 58
        row_svg.append(
            f'<rect x="58" y="{y - 28}" width="604" height="50" fill="#fbfcff" stroke="#d7deea"/>'
        )
        for col, value in enumerate(row):
            x = 76 + col * 150
            fill = "#1354a5" if col == 0 else "#172033"
            row_svg.append(
                f'<text x="{x}" y="{y}" font-size="16" font-weight="800" fill="{fill}">{html_escape(value)}</text>'
            )
    header_svg = "".join(
        f'<text x="{226 + idx * 150}" y="96" font-size="14" font-weight="800" fill="#b83246">{html_escape(label)}</text>'
        for idx, label in enumerate(headers)
    )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="70" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  {header_svg}
  {"".join(row_svg)}
</svg>
"""


def render_cash_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Cash-flow timeline" if not zh else "现金流时间线"
    labels = (
        ("Opening", "Inflows", "Outflows", "Closing")
        if not zh
        else ("期初", "流入", "流出", "期末")
    )
    nodes = []
    for pos, label in enumerate(labels):
        x = 92 + pos * 158
        nodes.append(
            f'<rect x="{x}" y="142" width="110" height="70" rx="14" fill="#ffffff" stroke="#1354a5" stroke-width="4"/>'
        )
        nodes.append(
            f'<text x="{x + 55}" y="183" font-size="16" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(label)}</text>'
        )
        if pos < 3:
            nodes.append(
                f'<path d="M{x + 118} 176h42" stroke="#172033" stroke-width="4" marker-end="url(#cash-arrow-{index})"/>'
            )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <defs><marker id="cash-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {"".join(nodes)}
  <text x="94" y="260" font-size="17" fill="#5b677a">{html_escape("closing balance = opening + inflows - outflows" if not zh else "期末余额 = 期初 + 流入 - 流出")}</text>
</svg>
"""


def render_break_even_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Break-even chart" if not zh else "盈亏平衡图"
    sales = "Revenue" if not zh else "收入"
    costs = "Total cost" if not zh else "总成本"
    output = "Output" if not zh else "产量"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <path d="M96 280V92M96 280h510" stroke="#172033" stroke-width="4"/>
  <path d="M112 250L580 96" stroke="#1f7a5b" stroke-width="6"/>
  <path d="M112 210L580 128" stroke="#b83246" stroke-width="6"/>
  <circle cx="362" cy="168" r="10" fill="#d99a24"/>
  <path d="M362 168v112" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="498" y="98" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(sales)}</text>
  <text x="486" y="150" font-size="17" font-weight="800" fill="#b83246">{html_escape(costs)}</text>
  <text x="310" y="160" font-size="16" font-weight="800" fill="#9b6a10">{html_escape(title)}</text>
  <text x="538" y="312" font-size="17" font-weight="800">{html_escape(output)}</text>
</svg>
"""


def render_marketing_mix_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Marketing mix" if not zh else "营销组合"
    labels = (
        ("Product", "Price", "Place", "Promotion") if not zh else ("产品", "价格", "渠道", "促销")
    )
    colors = ("#1354a5", "#1f7a5b", "#d99a24", "#b83246")
    cells = []
    for i, label in enumerate(labels):
        x = 136 + (i % 2) * 230
        y = 112 + (i // 2) * 104
        cells.append(
            f'<rect x="{x}" y="{y}" width="194" height="78" rx="16" fill="#ffffff" stroke="{colors[i]}" stroke-width="4"/>'
        )
        cells.append(
            f'<text x="{x + 97}" y="{y + 48}" font-size="21" font-weight="800" fill="{colors[i]}" text-anchor="middle">{html_escape(label)}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  {"".join(cells)}
</svg>
"""


def render_business_process_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Context", "Options", "Decision", "Outcome")
        if not zh
        else ("情境", "选择", "决策", "结果")
    )
    title = "Business decision flow" if not zh else "商业决策流程"
    return render_flow_svg(index, title, labels, "#1354a5", "#b83246")


def render_operations_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Input", "Process", "Output", "Efficiency") if not zh else ("投入", "流程", "产出", "效率")
    )
    title = "Operations flow and checkpoints" if not zh else "运营流程与检查点"
    return render_flow_svg(index, title, labels, "#1354a5", "#1f7a5b")


def render_quality_checkpoint_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Standard", "Inspect", "Feedback", "Improve")
        if not zh
        else ("标准", "检查", "反馈", "改进")
    )
    title = "Quality assurance checkpoint loop" if not zh else "质量保证循环"
    return render_flow_svg(index, title, labels, "#1f7a5b", "#d99a24")


def render_organisation_structure_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Organisation structure hierarchy" if not zh else "组织结构层级图"
    labels = (
        ("Director", "Manager A", "Manager B", "Team")
        if not zh
        else ("负责人", "经理A", "经理B", "团队")
    )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="280" y="96" width="160" height="58" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="138" y="206" width="160" height="58" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <rect x="422" y="206" width="160" height="58" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M360 154v34M218 188h284M218 188v18M502 188v18" stroke="#172033" stroke-width="4"/>
  <text x="360" y="132" font-size="18" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(labels[0])}</text>
  <text x="218" y="241" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(labels[1])}</text>
  <text x="502" y="241" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(labels[2])}</text>
  <text x="302" y="304" font-size="16" fill="#5b677a">{html_escape(labels[3])}: span of control and chain of command</text>
</svg>
"""


def render_customer_segmentation_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Customer segmentation map" if not zh else "顾客细分图"
    labels = ("Age", "Income", "Needs", "Location") if not zh else ("年龄", "收入", "需求", "地区")
    return render_flow_svg(index, title, labels, "#b83246", "#1354a5")


def render_history_timeline_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Historical timeline" if not zh else "历史时间线"
    labels = (
        ("Context", "Trigger", "Turning point", "Outcome")
        if not zh
        else ("背景", "导火索", "转折", "结果")
    )
    ticks = []
    for pos, label in enumerate(labels):
        x = 110 + pos * 160
        ticks.append(f'<circle cx="{x}" cy="184" r="13" fill="#1354a5"/>')
        ticks.append(f'<path d="M{x} 184v48" stroke="#1354a5" stroke-width="3"/>')
        ticks.append(
            f'<text x="{x}" y="260" font-size="16" font-weight="800" fill="#172033" text-anchor="middle">{html_escape(label)}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <path d="M88 184h548" stroke="#172033" stroke-width="5"/>
  {"".join(ticks)}
</svg>
"""


def render_history_cause_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("Long-term cause", "Short-term trigger", "Event", "Consequence")
        if not zh
        else ("长期原因", "短期触发", "事件", "后果")
    )
    title = "Cause and consequence chain" if not zh else "原因与后果链"
    return render_flow_svg(index, title, labels, "#b83246", "#1354a5")


def render_history_source_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Source evidence comparison" if not zh else "史料证据比较"
    labels = (
        ("Provenance", "Content", "Inference", "Limit")
        if not zh
        else ("出处", "内容", "推论", "局限")
    )
    return render_flow_svg(index, title, labels, "#1f7a5b", "#d99a24")


def render_history_comparison_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "Change and continuity comparison" if not zh else "变化与延续比较"
    before = "Before" if not zh else "之前"
    after = "After" if not zh else "之后"
    change = "Change" if not zh else "变化"
    continuity = "Continuity" if not zh else "延续"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="86" y="116" width="220" height="122" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="414" y="116" width="220" height="122" rx="16" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M314 176h92" stroke="#172033" stroke-width="5" marker-end="url(#hist-comp-{index})"/>
  <defs><marker id="hist-comp-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="196" y="166" font-size="23" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(before)}</text>
  <text x="524" y="166" font-size="23" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(after)}</text>
  <text x="176" y="284" font-size="19" font-weight="800" fill="#b83246">{html_escape(change)}</text>
  <text x="414" y="284" font-size="19" font-weight="800" fill="#9b6a10">{html_escape(continuity)}</text>
</svg>
"""


def render_economic_flow_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    labels = (
        ("选择", "资源限制", "机会成本", "经济结果")
        if zh
        else ("Choice", "Scarce resources", "Opportunity cost", "Economic outcome")
    )
    title = "经济选择流程" if zh else "Economic choice flow"
    return render_flow_svg(index, title, labels, "#d99a24", "#1354a5")


def render_venn_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "集合与韦恩图" if zh else "Set notation and Venn regions"
    union = "并集" if zh else "Union"
    intersect = "交集" if zh else "Intersection"
    outside = "补集" if zh else "Complement"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="86" y="104" width="360" height="198" rx="16" fill="#f7fbff" stroke="#172033" stroke-width="3"/>
  <circle cx="228" cy="200" r="82" fill="#1354a5" fill-opacity=".35" stroke="#1354a5" stroke-width="4"/>
  <circle cx="310" cy="200" r="82" fill="#b83246" fill-opacity=".32" stroke="#b83246" stroke-width="4"/>
  <text x="178" y="202" font-size="22" font-weight="800">A</text>
  <text x="350" y="202" font-size="22" font-weight="800">B</text>
  <text x="250" y="205" font-size="18" font-weight="800" fill="#172033">A ∩ B</text>
  <rect x="488" y="118" width="150" height="46" rx="10" fill="#edf4ff" stroke="#9cbce8"/>
  <rect x="488" y="178" width="150" height="46" rx="10" fill="#fff1f3" stroke="#e5aab4"/>
  <rect x="488" y="238" width="150" height="46" rx="10" fill="#fffaf1" stroke="#d99a24"/>
  <text x="508" y="148" font-size="18" font-weight="800" fill="#1354a5">{html_escape(union)}</text>
  <text x="508" y="208" font-size="18" font-weight="800" fill="#b83246">{html_escape(intersect)}</text>
  <text x="508" y="268" font-size="18" font-weight="800" fill="#9b6a10">{html_escape(outside)}</text>
</svg>
"""


def render_force_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "力与运动示意图" if zh else "Force and motion diagram"
    force = "合力" if zh else "resultant force"
    accel = "加速度方向" if zh else "acceleration"
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <rect x="258" y="152" width="170" height="88" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M248 196h-126" stroke="#b83246" stroke-width="7" marker-end="url(#force-left-{index})"/>
  <path d="M438 196h164" stroke="#1f7a5b" stroke-width="9" marker-end="url(#force-right-{index})"/>
  <defs>
    <marker id="force-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="force-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
  <text x="284" y="204" font-size="22" font-weight="800">object</text>
  <text x="110" y="164" font-size="17" font-weight="800" fill="#b83246">smaller force</text>
  <text x="452" y="164" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(force)}</text>
  <text x="452" y="274" font-size="17" font-weight="800" fill="#1f7a5b">{html_escape(accel)} →</text>
</svg>
"""


def render_gas_tests_svg(index: int, language: str) -> str:
    zh = language == "zh-CN"
    title = "气体检验观察图" if zh else "Common gas tests observation chart"
    headers = ("气体", "检验", "观察") if zh else ("Gas", "Test", "Observation")
    rows = (
        (
            ("氧气", "带火星木条", "复燃"),
            ("氢气", "燃着木条", "爆鸣"),
            ("二氧化碳", "石灰水", "变浑浊"),
        )
        if zh
        else (
            ("Oxygen", "glowing splint", "relights"),
            ("Hydrogen", "lit splint", "squeaky pop"),
            ("CO₂", "limewater", "turns cloudy"),
        )
    )
    row_svg = []
    for row_index, row in enumerate(rows):
        y = 130 + row_index * 56
        row_svg.append(
            f'<rect x="70" y="{y - 30}" width="580" height="48" fill="#fbfcff" stroke="#d7deea"/>'
        )
        row_svg.append(
            f'<text x="92" y="{y}" font-size="17" font-weight="800" fill="#1354a5">{html_escape(row[0])}</text>'
        )
        row_svg.append(
            f'<text x="258" y="{y}" font-size="17" fill="#172033">{html_escape(row[1])}</text>'
        )
        row_svg.append(
            f'<text x="486" y="{y}" font-size="17" fill="#1f7a5b">{html_escape(row[2])}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="72" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <text x="92" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[0])}</text>
  <text x="258" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[1])}</text>
  <text x="486" y="100" font-size="15" font-weight="800" fill="#b83246">{html_escape(headers[2])}</text>
  {"".join(row_svg)}
</svg>
"""


def render_flow_svg(
    index: int,
    title: str,
    labels: tuple[str, str, str, str],
    primary: str,
    secondary: str,
) -> str:
    cards = []
    for position, label in enumerate(labels):
        x = 64 + position * 160
        color = primary if position % 2 == 0 else secondary
        cards.append(
            f'<rect x="{x}" y="138" width="124" height="84" rx="14" fill="#ffffff" stroke="{color}" stroke-width="4"/>'
            f'<text x="{x + 62}" y="188" font-size="16" font-weight="800" fill="{color}" text-anchor="middle">{html_escape(label)}</text>'
        )
        if position < 3:
            ax = x + 132
            cards.append(
                f'<path d="M{ax} 180h38" stroke="#172033" stroke-width="4" marker-end="url(#flow-arrow-{index})"/>'
            )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="78" fill="#1354a5" font-size="24" font-weight="800">{html_escape(title)}</text>
  <defs><marker id="flow-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  {"".join(cards)}
</svg>
"""


def render_concept_fallback_svg(index: int, title: str) -> str:
    heading = title or "Study visual"
    labels = ("Key idea", "Question evidence", "Checked answer")
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(heading)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <text x="58" y="76" font-size="24" font-weight="800" fill="#1354a5">{html_escape(heading[:48])}</text>
  <rect x="82" y="130" width="158" height="96" rx="16" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="282" y="130" width="158" height="96" rx="16" fill="#fffaf1" stroke="#d99a24" stroke-width="3"/>
  <rect x="482" y="130" width="158" height="96" rx="16" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="3"/>
  <path d="M246 178h30M446 178h30" stroke="#172033" stroke-width="4" marker-end="url(#concept-arrow-{index})"/>
  <defs><marker id="concept-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="161" y="184" font-size="18" font-weight="800" fill="#1354a5" text-anchor="middle">{html_escape(labels[0])}</text>
  <text x="361" y="184" font-size="18" font-weight="800" fill="#9b6a10" text-anchor="middle">{html_escape(labels[1])}</text>
  <text x="561" y="184" font-size="18" font-weight="800" fill="#1f7a5b" text-anchor="middle">{html_escape(labels[2])}</text>
</svg>
"""


def render_zh_math_topic_svg(index: int, title: str, focus: str, variant: str) -> str:
    base_variant = variant.split(":", 1)[0]
    display_title = zh_math_specific_title(title, focus)
    labels_by_variant = {
        "algebra": ("识别结构", "代入变形", "检验解"),
        "calculus": ("看曲线", "取斜率", "判结论"),
        "integral": ("定边界", "算面积", "查符号"),
        "series": ("找首项", "看公差/公比", "写求和"),
        "trig": ("定角度", "选公式", "查周期"),
        "probability": ("列结果", "算概率", "验总和"),
        "mechanics": ("画受力", "列方程", "查方向"),
        "coordinate": ("定坐标", "写方程", "验几何"),
    }
    labels = labels_by_variant.get(base_variant, ("读图", "建模", "检查"))
    cards = []
    for position, label in enumerate(labels):
        x = 456
        y = 96 + position * 72
        cards.append(
            f'<rect x="{x}" y="{y}" width="232" height="52" rx="10" fill="#ffffff" '
            f'stroke="#d7deea" stroke-width="2"/>'
            f'<text x="{x + 18}" y="{y + 34}" font-size="20" font-weight="800" '
            f'fill="#172033">{html_escape(label)}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(display_title)}</title>
  <rect x="6" y="6" width="708" height="348" rx="16" fill="#ffffff" stroke="#d7deea"/>
  <text x="30" y="52" fill="#1354a5" font-size="26" font-weight="800">{html_escape(display_title)}</text>
  <g transform="translate(-28 -14) scale(1.15)">{render_zh_math_motif(index, variant, focus)}</g>
  <rect x="436" y="72" width="270" height="244" rx="16" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  {"".join(cards)}
</svg>
"""


def render_math_topic_svg(index: int, title: str, focus: str, variant: str) -> str:
    base_variant = variant.split(":", 1)[0]
    display_title = math_specific_title(title, focus)
    labels_by_variant = {
        "algebra": ("spot structure", "transform", "check"),
        "calculus": ("read curve", "take gradient", "interpret"),
        "integral": ("set bounds", "find area", "check sign"),
        "series": ("first term", "common rule", "sum"),
        "trig": ("angle", "formula", "period"),
        "probability": ("outcomes", "probability", "total"),
        "mechanics": ("direction", "equation", "units"),
        "coordinate": ("coordinates", "equation", "geometry"),
    }
    labels = labels_by_variant.get(base_variant, ("read", "model", "check"))
    cards = []
    for position, label in enumerate(labels):
        x = 456
        y = 96 + position * 72
        cards.append(
            f'<rect x="{x}" y="{y}" width="232" height="52" rx="10" fill="#ffffff" '
            f'stroke="#d7deea" stroke-width="2"/>'
            f'<text x="{x + 18}" y="{y + 34}" font-size="20" font-weight="800" '
            f'fill="#172033">{html_escape(label)}</text>'
        )
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(display_title)}</title>
  <rect x="6" y="6" width="708" height="348" rx="16" fill="#ffffff" stroke="#d7deea"/>
  <text x="30" y="52" fill="#1354a5" font-size="26" font-weight="800">{html_escape(display_title)}</text>
  <g transform="translate(-28 -14) scale(1.15)">{render_math_motif(index, variant, focus)}</g>
  <rect x="436" y="72" width="270" height="244" rx="16" fill="#f7fbff" stroke="#9cbce8" stroke-width="3"/>
  {"".join(cards)}
</svg>
"""


def math_specific_title(default_title: str, focus: str) -> str:
    clean = re.sub(r"\s+", " ", (focus or "").strip(" .;:"))
    if not clean or clean.lower() == "focus":
        return default_title
    clean = clean.replace("&lt;", "<").replace("&gt;", ">")
    if len(clean) > 42:
        clean = clean[:39].rstrip() + "..."
    return clean


def render_math_motif(index: int, variant: str, focus: str = "") -> str:
    motif = render_zh_math_motif(index, variant, focus)
    replacements = {
        "化简 / 分母有理化": "simplify / rationalise",
        "看根的个数": "count real roots",
        "因式 / 余式定理": "factor / remainder theorem",
        "解集写区间": "solution set",
        "平移 / 反射 / 伸缩": "shift / reflect / stretch",
        "交点 = 联立解": "intersections = simultaneous solutions",
        "同一个导数意义": "same derivative idea",
        "割线逼近切线": "secant tends to tangent",
        "判断极大 / 极小": "classify maxima/minima",
        "切线斜率": "tangent gradient",
        "积分是求导的反向": "integration reverses differentiation",
        "梯形近似": "trapezium approximation",
        "a 到 b 的面积": "area from a to b",
        "x 轴下方为负": "below x-axis is negative",
        "带符号面积": "signed area",
        "项、系数、幂次": "terms, coefficients, powers",
        "公式或表格求概率": "use formula or table",
        "速度-时间图与位移-时间图": "velocity-time and displacement-time graphs",
        "斜率与面积": "gradient and area",
        "方向先定正": "choose positive direction",
        "冲量 = 动量变化": "impulse = change in momentum",
        "联立找交点": "solve simultaneously",
        "面积": "area",
        "解后代回检查": "substitute back to check",
    }
    for zh, en in replacements.items():
        motif = motif.replace(zh, en)
    return motif


def zh_math_specific_title(default_title: str, focus: str) -> str:
    clean = re.sub(r"\s+", " ", (focus or "").strip(" 。.；;:："))
    if not clean or clean.lower() == "focus":
        return default_title
    clean = clean.replace("&lt;", "<").replace("&gt;", ">")
    if len(clean) > 16:
        clean = clean[:15] + "…"
    if clean.endswith("图解"):
        return clean
    return f"{clean}图解"


def zh_math_variant(base: str, text: str) -> str:
    if base == "algebra":
        if any(word in text for word in ["根式", "surd"]):
            return "algebra:surd"
        if any(word in text for word in ["指数", "indices", "exponents"]):
            return "algebra:index"
        if any(word in text for word in ["判别式", "discriminant"]):
            return "algebra:discriminant"
        if any(word in text for word in ["配方", "completing"]):
            return "algebra:complete-square"
        if any(word in text for word in ["因式", "factorisation", "factor theorem"]):
            return "algebra:factor"
        if any(word in text for word in ["不等式", "inequal"]):
            return "algebra:inequality"
        if any(word in text for word in ["除法", "余式", "division", "remainder"]):
            return "algebra:division"
        if any(word in text for word in ["变换", "平移", "反射", "伸缩", "transformation"]):
            return "algebra:transform"
        if any(word in text for word in ["联立", "simultaneous"]):
            return "algebra:simultaneous"
        return "algebra:quadratic"
    if base == "calculus":
        if any(word in text for word in ["记号", "notation"]):
            return "calculus:notation"
        if any(word in text for word in ["第一原理", "first principles"]):
            return "calculus:first-principles"
        if any(word in text for word in ["二阶", "second order"]):
            return "calculus:second"
        if any(word in text for word in ["多项式", "polynomial", "rational number"]):
            return "calculus:power-rule"
        if any(word in text for word in ["驻点", "最大", "最小", "stationary", "maxima", "minima"]):
            return "calculus:stationary"
        return "calculus:tangent"
    if base == "integral":
        if any(word in text for word in ["不定", "反导", "reverse", "indefinite"]):
            return "integral:reverse"
        if any(word in text for word in ["多项式", "rational number"]):
            return "integral:power-rule"
        if any(word in text for word in ["梯形", "trapezium"]):
            return "integral:trapezium"
        if any(
            word in text
            for word in ["x-axis", "x axis", "below", "negative value", "signed", "region between"]
        ):
            return "integral:signed-area"
        if any(word in text for word in ["定积分", "definite"]):
            return "integral:definite"
        return "integral:area"
    if base == "series":
        if any(word in text for word in ["等差", "arithmetic"]):
            return "series:arithmetic"
        if any(word in text for word in ["收敛", "|r|", "infinity", "convergent"]):
            return "series:infinity"
        if any(word in text for word in ["等比", "geometric"]):
            return "series:geometric"
        if any(word in text for word in ["二项式", "binomial"]):
            return "series:binomial"
        return "series:sequence"
    if base == "probability":
        if any(word in text for word in ["二项分布", "伯努利", "binomial", "bernoulli"]):
            return "probability:binomial"
        if any(
            word in text
            for word in ["随机变量", "均值", "方差", "标准差", "random variable", "variance"]
        ):
            return "probability:table"
        if any(
            word in text
            for word in ["条件", "乘法", "加法", "conditional", "multiplication", "addition"]
        ):
            return "probability:tree"
        return "probability:bars"
    if base == "trig":
        if any(
            word in text for word in ["sine rule", "cosine rule", "area of a triangle", "triangle"]
        ):
            return "trig:triangle"
        if any(word in text for word in ["graph", "graphs", "symmetries", "periodicity"]):
            return "trig:graph"
        if any(word in text for word in ["equation", "identity", "identities"]):
            return "trig:identity"
        return "trig:unit-circle"
    if base == "mechanics":
        if any(
            word in text
            for word in ["速度", "位移", "加速度", "运动学", "velocity", "acceleration"]
        ):
            return "mechanics:kinematics"
        if any(word in text for word in ["牛顿", "newton"]):
            return "mechanics:newton"
        if any(word in text for word in ["动量", "冲量", "碰撞", "momentum", "impulse", "impact"]):
            return "mechanics:momentum"
        return "mechanics:forces"
    if base == "coordinate":
        if "coordinate geometry of the circle" in text:
            return "coordinate:circle"
        if any(word in text for word in ["tangent", "normal"]):
            return "coordinate:tangent"
        if any(word in text for word in ["translation", "transformed"]):
            return "coordinate:translation"
        if any(word in text for word in ["圆", "circle"]):
            return "coordinate:circle"
        if any(word in text for word in ["交点", "intersection"]):
            return "coordinate:intersection"
        return "coordinate:line"
    return base


def render_zh_math_motif(index: int, variant: str, focus: str = "") -> str:
    if variant == "algebra:surd":
        return """
  <rect x="82" y="146" width="244" height="82" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="104" y="198" font-size="34" font-weight="800" fill="#1354a5">√50 = 5√2</text>
  <path d="M110 244h190" stroke="#b83246" stroke-width="4"/>
  <text x="118" y="276" font-size="18" font-weight="800" fill="#b83246">化简 / 分母有理化</text>
"""
    if variant == "algebra:index":
        return """
  <rect x="86" y="126" width="80" height="80" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="196" y="126" width="80" height="80" rx="12" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M168 166h26" stroke="#172033" stroke-width="4" marker-end="url(#idx-arrow)"/>
  <text x="106" y="176" font-size="24" font-weight="800" fill="#1354a5">aᵐ</text>
  <text x="214" y="176" font-size="24" font-weight="800" fill="#1f7a5b">aⁿ</text>
  <text x="106" y="250" font-size="26" font-weight="800" fill="#b83246">aᵐaⁿ=aᵐ⁺ⁿ</text>
  <defs><marker id="idx-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:discriminant":
        return """
  <path d="M78 270V112M78 270h284" stroke="#172033" stroke-width="4"/>
  <path d="M114 248C158 126 274 126 328 248" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M116 220h212" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 6"/>
  <text x="102" y="118" font-size="24" font-weight="800" fill="#b83246">Δ=b²-4ac</text>
  <text x="112" y="306" font-size="18" font-weight="800" fill="#1f7a5b">看根的个数</text>
"""
    if variant == "algebra:complete-square":
        return """
  <rect x="78" y="118" width="118" height="118" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="204" y="118" width="70" height="118" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <rect x="78" y="244" width="118" height="42" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="92" y="104" font-size="24" font-weight="800" fill="#b83246">x²+6x</text>
  <text x="106" y="318" font-size="22" font-weight="800" fill="#1f7a5b">(x+3)² - 9</text>
"""
    if variant == "algebra:factor":
        return """
  <rect x="76" y="138" width="104" height="70" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="214" y="138" width="104" height="70" rx="12" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M184 174h26" stroke="#172033" stroke-width="4" marker-end="url(#factor-arrow)"/>
  <text x="96" y="181" font-size="24" font-weight="800" fill="#1354a5">f(a)=0</text>
  <text x="228" y="181" font-size="24" font-weight="800" fill="#1f7a5b">(x-a)</text>
  <text x="102" y="260" font-size="20" font-weight="800" fill="#b83246">因式 / 余式定理</text>
  <defs><marker id="factor-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:inequality":
        ticks = "".join(
            f'<path d="M{x} 202v18" stroke="#172033" stroke-width="3"/>'
            for x in [94, 142, 190, 238, 286, 334]
        )
        return f"""
  <path d="M76 211h288" stroke="#172033" stroke-width="4" marker-end="url(#ineq-arrow)"/>
  {ticks}
  <circle cx="238" cy="211" r="12" fill="#ffffff" stroke="#b83246" stroke-width="5"/>
  <path d="M238 211h96" stroke="#b83246" stroke-width="8"/>
  <text x="102" y="146" font-size="24" font-weight="800" fill="#1354a5">解集写区间</text>
  <text x="130" y="270" font-size="22" font-weight="800" fill="#b83246">x ≥ a</text>
  <defs><marker id="ineq-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "algebra:division":
        return """
  <rect x="78" y="124" width="252" height="60" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M112 214h184M112 248h184" stroke="#172033" stroke-width="4"/>
  <text x="100" y="162" font-size="22" font-weight="800" fill="#1354a5">f(x) ÷ (x-a)</text>
  <text x="116" y="238" font-size="21" font-weight="800" fill="#b83246">商 + 余数</text>
  <text x="118" y="292" font-size="18" font-weight="800" fill="#1f7a5b">余数 = f(a)</text>
"""
    if variant == "algebra:transform":
        return """
  <path d="M80 270V116M80 270h278" stroke="#172033" stroke-width="4"/>
  <path d="M102 238C142 154 226 154 272 238" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M144 218C184 134 268 134 314 218" fill="none" stroke="#b83246" stroke-width="5" stroke-dasharray="8 6"/>
  <path d="M272 146h42" stroke="#d99a24" stroke-width="5" marker-end="url(#trans-arrow)"/>
  <text x="112" y="110" font-size="22" font-weight="800" fill="#1f7a5b">平移 / 反射 / 伸缩</text>
  <defs><marker id="trans-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker></defs>
"""
    if variant == "algebra:simultaneous":
        return """
  <path d="M78 270V116M78 270h284" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C148 144 260 144 326 246" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 232L332 142" stroke="#b83246" stroke-width="5"/>
  <circle cx="222" cy="186" r="9" fill="#d99a24"/>
  <text x="104" y="112" font-size="22" font-weight="800" fill="#1f7a5b">交点 = 联立解</text>
"""
    if variant == "calculus:notation":
        return """
  <rect x="76" y="128" width="272" height="106" rx="16" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <text x="100" y="176" font-size="31" font-weight="800" fill="#1354a5">f′(x)</text>
  <text x="212" y="176" font-size="31" font-weight="800" fill="#b83246">dy/dx</text>
  <text x="104" y="260" font-size="19" font-weight="800" fill="#1f7a5b">同一个导数意义</text>
"""
    if variant == "calculus:first-principles":
        return """
  <path d="M82 264V130M82 264h272" stroke="#172033" stroke-width="4"/>
  <path d="M104 240C150 206 198 164 328 142" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M158 216h96M254 216v-38" stroke="#b83246" stroke-width="4" stroke-dasharray="7 5"/>
  <text x="108" y="112" font-size="22" font-weight="800" fill="#b83246">h → 0</text>
  <text x="118" y="304" font-size="19" font-weight="800" fill="#1f7a5b">割线逼近切线</text>
"""
    if variant == "calculus:second":
        return """
  <path d="M82 272V118M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 238C168 96 240 96 332 238" fill="none" stroke="#1354a5" stroke-width="6"/>
  <circle cx="218" cy="126" r="9" fill="#d99a24"/>
  <text x="112" y="108" font-size="22" font-weight="800" fill="#b83246">f″(x)</text>
  <text x="118" y="306" font-size="19" font-weight="800" fill="#1f7a5b">判断极大 / 极小</text>
"""
    if variant == "calculus:power-rule":
        return """
  <rect x="82" y="122" width="252" height="72" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="82" y="218" width="252" height="72" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M208 197v18" stroke="#172033" stroke-width="4" marker-end="url(#pow-arrow)"/>
  <text x="108" y="166" font-size="27" font-weight="800" fill="#1354a5">xⁿ</text>
  <text x="108" y="263" font-size="27" font-weight="800" fill="#1f7a5b">nxⁿ⁻¹</text>
  <defs><marker id="pow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "calculus:stationary":
        return """
  <path d="M82 272V112M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C144 126 202 126 226 190C250 254 304 254 344 138" fill="none" stroke="#1354a5" stroke-width="6"/>
  <circle cx="202" cy="142" r="8" fill="#b83246"/><circle cx="278" cy="238" r="8" fill="#1f7a5b"/>
  <path d="M168 142h70M244 238h70" stroke="#d99a24" stroke-width="4"/>
  <text x="106" y="104" font-size="20" font-weight="800" fill="#b83246">dy/dx = 0</text>
"""
    if variant == "integral:reverse":
        return """
  <rect x="82" y="128" width="108" height="72" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="244" y="128" width="108" height="72" rx="14" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M196 164h42" stroke="#172033" stroke-width="5" marker-end="url(#int-rev)"/>
  <text x="110" y="172" font-size="24" font-weight="800" fill="#1354a5">f′(x)</text>
  <text x="268" y="172" font-size="24" font-weight="800" fill="#1f7a5b">f(x)+c</text>
  <text x="98" y="264" font-size="22" font-weight="800" fill="#b83246">积分是求导的反向</text>
  <defs><marker id="int-rev" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "integral:power-rule":
        return """
  <rect x="84" y="122" width="244" height="74" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="84" y="222" width="244" height="74" rx="14" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <text x="112" y="168" font-size="27" font-weight="800" fill="#1354a5">xⁿ</text>
  <text x="112" y="267" font-size="25" font-weight="800" fill="#9b6a10">xⁿ⁺¹/(n+1)</text>
"""
    if variant == "integral:trapezium":
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M104 242L154 198L204 176L254 156L318 132" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 274V242L154 198V274ZM154 274V198L204 176V274ZM204 274V176L254 156V274ZM254 274V156L318 132V274Z" fill="#d99a24" fill-opacity=".28" stroke="#d99a24" stroke-width="3"/>
  <text x="110" y="112" font-size="22" font-weight="800" fill="#b83246">梯形近似</text>
"""
    if variant == "integral:definite":
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M110 250C160 206 220 154 344 132" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M130 274V236M318 274V138" stroke="#b83246" stroke-width="4" stroke-dasharray="7 6"/>
  <path d="M130 236C176 196 226 164 318 138L318 274L130 274Z" fill="#d99a24" fill-opacity=".28"/>
  <text x="112" y="112" font-size="22" font-weight="800" fill="#b83246">a 到 b 的面积</text>
  <text x="124" y="310" font-size="20" font-weight="800" fill="#1354a5">∫ₐᵇ f(x) dx</text>
"""
    if variant == "integral:signed-area":
        return """
  <path d="M80 206h282M80 286V106" stroke="#172033" stroke-width="4"/>
  <path d="M104 172C148 120 204 126 238 194C268 254 312 262 346 222" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M118 206C154 154 202 138 238 194L238 206Z" fill="#1f7a5b" fill-opacity=".25"/>
  <path d="M238 206C268 254 312 262 342 222L342 206Z" fill="#b83246" fill-opacity=".25"/>
  <path d="M238 116v170" stroke="#d99a24" stroke-width="3" stroke-dasharray="7 6"/>
  <text x="106" y="108" font-size="21" font-weight="800" fill="#1f7a5b">带符号面积</text>
  <text x="114" y="314" font-size="19" font-weight="800" fill="#b83246">x 轴下方为负</text>
"""
    if variant == "series:arithmetic":
        return """
  <circle cx="106" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="184" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="262" cy="186" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M136 186h18M214 186h18" stroke="#172033" stroke-width="4"/>
  <text x="96" y="194" font-size="22" font-weight="800">a</text>
  <text x="168" y="194" font-size="22" font-weight="800">a+d</text>
  <text x="238" y="194" font-size="22" font-weight="800">a+2d</text>
  <text x="108" y="266" font-size="24" font-weight="800" fill="#b83246">Sₙ = n/2(...)</text>
"""
    if variant == "series:geometric":
        return """
  <rect x="86" y="206" width="36" height="36" fill="#1354a5"/>
  <rect x="150" y="184" width="58" height="58" fill="#1f7a5b"/>
  <rect x="236" y="148" width="92" height="92" fill="#d99a24"/>
  <path d="M124 224h24M210 213h24" stroke="#172033" stroke-width="4"/>
  <text x="94" y="126" font-size="24" font-weight="800" fill="#b83246">乘以 r</text>
  <text x="104" y="292" font-size="22" font-weight="800" fill="#1354a5">a, ar, ar²</text>
"""
    if variant == "series:infinity":
        return """
  <path d="M88 210C124 150 168 150 204 210C240 270 284 270 320 210C284 150 240 150 204 210C168 270 124 270 88 210Z" fill="none" stroke="#1354a5" stroke-width="6"/>
  <text x="92" y="122" font-size="24" font-weight="800" fill="#b83246">|r| &lt; 1</text>
  <text x="112" y="292" font-size="22" font-weight="800" fill="#1f7a5b">S∞ = a/(1-r)</text>
"""
    if variant == "series:binomial":
        return """
  <rect x="72" y="126" width="268" height="60" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M136 194l-38 54M206 194v54M276 194l38 54" stroke="#172033" stroke-width="4"/>
  <text x="96" y="166" font-size="26" font-weight="800" fill="#1354a5">(a+b)ⁿ</text>
  <text x="80" y="284" font-size="20" font-weight="800" fill="#b83246">项、系数、幂次</text>
"""
    if variant == "probability:table":
        rows = []
        for row, values in enumerate([("x", "0", "1", "2"), ("P", ".2", ".5", ".3")]):
            y = 150 + row * 50
            rows.append(
                f'<text x="96" y="{y}" font-size="20" font-weight="800" fill="#1354a5">{values[0]}</text>'
            )
            for col, value in enumerate(values[1:]):
                rows.append(
                    f'<text x="{158 + col * 62}" y="{y}" font-size="20" font-weight="800">{value}</text>'
                )
        return f"""
  <rect x="72" y="112" width="270" height="122" rx="14" fill="#ffffff" stroke="#d7deea" stroke-width="4"/>
  <path d="M72 170h270M134 112v122" stroke="#d7deea" stroke-width="3"/>
  {"".join(rows)}
  <text x="96" y="286" font-size="21" font-weight="800" fill="#b83246">E(X), Var(X)</text>
"""
    if variant == "probability:tree":
        return """
  <circle cx="92" cy="176" r="8" fill="#b83246"/>
  <path d="M100 176L196 128M100 176L196 224M204 128L312 104M204 128L312 152M204 224L312 200M204 224L312 248" stroke="#172033" stroke-width="4"/>
  <g fill="#1354a5"><circle cx="196" cy="128" r="8"/><circle cx="196" cy="224" r="8"/></g>
  <g fill="#1f7a5b"><circle cx="312" cy="104" r="8"/><circle cx="312" cy="152" r="8"/><circle cx="312" cy="200" r="8"/><circle cx="312" cy="248" r="8"/></g>
  <text x="104" y="112" font-size="20" font-weight="800" fill="#b83246">乘法 / 条件</text>
"""
    if variant == "probability:binomial":
        bars = []
        for pos, height in enumerate([36, 76, 112, 76, 36]):
            x = 86 + pos * 48
            bars.append(
                f'<rect x="{x}" y="{254 - height}" width="28" height="{height}" fill="#1354a5"/>'
            )
        return f"""
  <path d="M72 270V118M72 270h292" stroke="#172033" stroke-width="4"/>
  {"".join(bars)}
  <text x="96" y="104" font-size="23" font-weight="800" fill="#b83246">X ~ B(n,p)</text>
  <text x="112" y="306" font-size="19" font-weight="800" fill="#1f7a5b">公式或表格求概率</text>
"""
    if variant == "mechanics:kinematics":
        return """
  <path d="M82 272V112M82 272h280" stroke="#172033" stroke-width="4"/>
  <path d="M104 250L190 210L276 166L344 122" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M190 210h86" stroke="#d99a24" stroke-width="5" stroke-dasharray="7 6"/>
  <text x="106" y="104" font-size="22" font-weight="800" fill="#b83246">速度-时间图与位移-时间图</text>
  <text x="112" y="306" font-size="19" font-weight="800" fill="#1f7a5b">斜率与面积</text>
"""
    if variant == "mechanics:newton":
        return f"""
  <rect x="152" y="172" width="110" height="70" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M142 206h-64" stroke="#b83246" stroke-width="7" marker-end="url(#newton-left-{index})"/>
  <path d="M272 206h84" stroke="#1f7a5b" stroke-width="9" marker-end="url(#newton-right-{index})"/>
  <text x="88" y="126" font-size="24" font-weight="800" fill="#1354a5">ΣF = ma</text>
  <text x="112" y="288" font-size="19" font-weight="800" fill="#b83246">方向先定正</text>
  <defs>
    <marker id="newton-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="newton-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
"""
    if variant == "mechanics:connected":
        return f"""
  <circle cx="214" cy="136" r="34" fill="#ffffff" stroke="#172033" stroke-width="5"/>
  <path d="M214 170V230M214 136H110" stroke="#172033" stroke-width="5" fill="none"/>
  <rect x="78" y="202" width="64" height="46" rx="8" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="184" y="230" width="62" height="52" rx="8" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M110 226h-44" stroke="#b83246" stroke-width="6" marker-end="url(#conn-left-{index})"/>
  <path d="M215 282v34" stroke="#1f7a5b" stroke-width="6" marker-end="url(#conn-down-{index})"/>
  <text x="92" y="194" font-size="20" font-weight="800" fill="#1354a5">T</text>
  <text x="226" y="314" font-size="20" font-weight="800" fill="#1f7a5b">mg</text>
  <text x="90" y="106" font-size="22" font-weight="800" fill="#b83246">same acceleration</text>
  <defs>
    <marker id="conn-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="conn-down-{index}" viewBox="0 0 10 10" refX="5" refY="9" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 5 10 10 0z" fill="#1f7a5b"/></marker>
  </defs>
"""
    if variant == "mechanics:momentum":
        return f"""
  <text x="86" y="104" font-size="22" font-weight="800" fill="#1354a5">before</text>
  <text x="260" y="104" font-size="22" font-weight="800" fill="#1f7a5b">after</text>
  <circle cx="116" cy="166" r="28" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="246" cy="166" r="22" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M148 166h62" stroke="#b83246" stroke-width="7" marker-end="url(#mom-in-{index})"/>
  <path d="M92 252h92M222 252h92" stroke="#172033" stroke-width="4"/>
  <circle cx="118" cy="252" r="24" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <circle cx="256" cy="252" r="24" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M144 252h54M282 252h54" stroke="#1f7a5b" stroke-width="6" marker-end="url(#mom-out-{index})"/>
  <text x="84" y="314" font-size="20" font-weight="800" fill="#b83246">total momentum conserved</text>
  <defs>
    <marker id="mom-in-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker>
    <marker id="mom-out-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
  </defs>
"""
    if variant == "mechanics:fixed-impact":
        return f"""
  <rect x="296" y="96" width="28" height="206" fill="#172033"/>
  <path d="M324 104l34-22M324 148l34-22M324 192l34-22M324 236l34-22M324 280l34-22" stroke="#5b677a" stroke-width="4"/>
  <circle cx="118" cy="190" r="30" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M154 190h102" stroke="#b83246" stroke-width="7" marker-end="url(#impact-in-{index})"/>
  <circle cx="252" cy="250" r="20" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M248 250h-96" stroke="#1f7a5b" stroke-width="6" marker-end="url(#impact-out-{index})"/>
  <path d="M296 96v206" stroke="#111827" stroke-width="4"/>
  <text x="84" y="110" font-size="22" font-weight="800" fill="#1354a5">perpendicular impact</text>
  <text x="86" y="314" font-size="20" font-weight="800" fill="#b83246">reverse velocity direction</text>
  <defs>
    <marker id="impact-in-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker>
    <marker id="impact-out-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#1f7a5b"/></marker>
  </defs>
"""
    if variant == "coordinate:translation":
        return """
  <path d="M80 272V96M80 272h282" stroke="#172033" stroke-width="4"/>
  <circle cx="172" cy="204" r="48" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="5"/>
  <circle cx="264" cy="148" r="48" fill="#edf4ff" stroke="#1354a5" stroke-width="5" stroke-dasharray="8 6"/>
  <path d="M172 204L264 148" stroke="#b83246" stroke-width="5" marker-end="url(#circle-trans)"/>
  <text x="108" y="104" font-size="22" font-weight="800" fill="#1354a5">centre moves, radius stays</text>
  <defs><marker id="circle-trans" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker></defs>
"""
    if variant == "coordinate:tangent":
        return """
  <path d="M80 272V96M80 272h282" stroke="#172033" stroke-width="4"/>
  <circle cx="210" cy="184" r="72" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M210 184L276 156" stroke="#1354a5" stroke-width="4"/>
  <path d="M236 100L316 288" stroke="#b83246" stroke-width="5"/>
  <path d="M188 238L320 136" stroke="#d99a24" stroke-width="4" stroke-dasharray="8 6"/>
  <circle cx="276" cy="156" r="8" fill="#172033"/>
  <text x="104" y="104" font-size="22" font-weight="800" fill="#b83246">radius ⟂ tangent</text>
  <text x="104" y="306" font-size="20" font-weight="800" fill="#1354a5">(x-a)²+(y-b)²=r²</text>
"""
    if variant == "coordinate:circle":
        return """
  <path d="M80 272V96M80 272h282" stroke="#172033" stroke-width="4"/>
  <circle cx="212" cy="180" r="74" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="5"/>
  <path d="M212 180h74" stroke="#b83246" stroke-width="4"/>
  <text x="112" y="104" font-size="22" font-weight="800" fill="#1354a5">(x-a)²+(y-b)²=r²</text>
"""
    if variant == "coordinate:intersection":
        return """
  <path d="M80 272V106M80 272h282" stroke="#172033" stroke-width="4"/>
  <path d="M102 250C160 132 260 132 338 250" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M104 232L336 126" stroke="#b83246" stroke-width="5"/>
  <circle cx="186" cy="194" r="8" fill="#d99a24"/><circle cx="286" cy="150" r="8" fill="#d99a24"/>
  <text x="106" y="104" font-size="22" font-weight="800" fill="#1f7a5b">联立找交点</text>
"""
    if variant.startswith("calculus"):
        return """
  <path d="M78 274V104M78 274h288" stroke="#172033" stroke-width="4"/>
  <path d="M104 246C150 174 196 128 258 150C300 164 326 218 352 246" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M132 218L324 156" stroke="#b83246" stroke-width="5"/>
  <circle cx="226" cy="164" r="8" fill="#d99a24"/>
  <text x="108" y="104" font-size="22" font-weight="800" fill="#b83246">切线斜率</text>
  <text x="118" y="310" font-size="20" font-weight="800" fill="#1f7a5b">dy/dx</text>
"""
    if variant.startswith("integral"):
        return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M108 250C160 218 204 166 270 148C306 138 332 134 354 130L354 274L108 274Z" fill="#d99a24" fill-opacity=".28"/>
  <path d="M108 250C160 218 204 166 270 148C306 138 332 134 354 130" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M108 274V250M354 274V130" stroke="#b83246" stroke-width="4" stroke-dasharray="7 6"/>
  <text x="132" y="164" font-size="20" font-weight="800" fill="#9b6a10">面积</text>
  <text x="116" y="306" font-size="22" font-weight="800" fill="#1354a5">∫ f(x) dx</text>
"""
    if variant.startswith("series"):
        bars = []
        for pos, height in enumerate([52, 74, 96, 118]):
            x = 88 + pos * 58
            bars.append(
                f'<rect x="{x}" y="{258 - height}" width="34" height="{height}" fill="#1354a5"/>'
            )
        return f"""
  <path d="M70 274h286" stroke="#172033" stroke-width="4"/>
  {"".join(bars)}
  <path d="M284 136h52" stroke="#b83246" stroke-width="5" marker-end="url(#series-arrow-{index})"/>
  <defs><marker id="series-arrow-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#b83246"/></marker></defs>
  <text x="92" y="120" font-size="22" font-weight="800" fill="#b83246">a, r</text>
  <text x="248" y="196" font-size="22" font-weight="800" fill="#1f7a5b">Sₙ</text>
"""
    if variant == "trig:triangle":
        return """
  <path d="M94 260L318 260L240 128Z" fill="#fffaf1" stroke="#d99a24" stroke-width="5"/>
  <path d="M94 260L240 128M240 128L318 260" stroke="#172033" stroke-width="3"/>
  <text x="110" y="250" font-size="18" font-weight="800" fill="#1354a5">A</text>
  <text x="296" y="250" font-size="18" font-weight="800" fill="#1354a5">B</text>
  <text x="238" y="120" font-size="18" font-weight="800" fill="#1354a5">C</text>
  <text x="106" y="98" font-size="20" font-weight="800" fill="#b83246">sine / cosine rule</text>
  <text x="126" y="304" font-size="20" font-weight="800" fill="#1f7a5b">match sides to angles</text>
"""
    if variant == "trig:graph":
        return """
  <path d="M72 196h294M94 286V104" stroke="#172033" stroke-width="4"/>
  <path d="M84 196C116 116 158 116 190 196C222 276 264 276 296 196C328 116 354 132 368 164" fill="none" stroke="#1354a5" stroke-width="5"/>
  <path d="M84 196C116 276 158 276 190 196C222 116 264 116 296 196C328 276 354 260 368 228" fill="none" stroke="#b83246" stroke-width="5" stroke-dasharray="8 6"/>
  <text x="108" y="104" font-size="22" font-weight="800" fill="#1354a5">sin x</text>
  <text x="254" y="104" font-size="22" font-weight="800" fill="#b83246">cos x</text>
  <text x="112" y="318" font-size="20" font-weight="800" fill="#1f7a5b">period and symmetry</text>
"""
    if variant == "trig:identity":
        return """
  <rect x="78" y="122" width="268" height="72" rx="14" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <rect x="112" y="224" width="204" height="58" rx="12" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M212 198v22" stroke="#172033" stroke-width="4" marker-end="url(#trig-id)"/>
  <text x="104" y="168" font-size="25" font-weight="800" fill="#1354a5">tan x = sin x / cos x</text>
  <text x="136" y="262" font-size="22" font-weight="800" fill="#b83246">solve in interval</text>
  <defs><marker id="trig-id" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
"""
    if variant == "trig" or variant == "trig:unit-circle":
        return """
  <circle cx="204" cy="194" r="88" fill="#fffaf1" stroke="#d99a24" stroke-width="4"/>
  <path d="M204 194h118M204 194l74-65M278 129v65" stroke="#172033" stroke-width="4"/>
  <path d="M238 194A34 34 0 0 0 230 171" fill="none" stroke="#b83246" stroke-width="4"/>
  <text x="286" y="186" font-size="18" font-weight="800" fill="#1354a5">cos</text>
  <text x="286" y="156" font-size="18" font-weight="800" fill="#1f7a5b">sin</text>
  <text x="146" y="314" font-size="21" font-weight="800" fill="#b83246">sin, cos, tan</text>
"""
    if variant.startswith("probability"):
        return """
  <path d="M74 270V134M74 270h148" stroke="#172033" stroke-width="4"/>
  <rect x="98" y="218" width="28" height="52" fill="#1354a5"/>
  <rect x="138" y="174" width="28" height="96" fill="#1f7a5b"/>
  <rect x="178" y="202" width="28" height="68" fill="#d99a24"/>
  <path d="M270 160h44M314 160l42-38M314 160l42 38" stroke="#172033" stroke-width="4" fill="none"/>
  <circle cx="270" cy="160" r="8" fill="#b83246"/><circle cx="356" cy="122" r="8" fill="#1354a5"/><circle cx="356" cy="198" r="8" fill="#1f7a5b"/>
  <text x="96" y="116" font-size="20" font-weight="800" fill="#b83246">P(X=x)</text>
"""
    if variant.startswith("mechanics"):
        return f"""
  <rect x="162" y="174" width="96" height="64" rx="12" fill="#edf4ff" stroke="#1354a5" stroke-width="4"/>
  <path d="M150 206h-70" stroke="#b83246" stroke-width="7" marker-end="url(#mech-left-{index})"/>
  <path d="M270 206h88" stroke="#1f7a5b" stroke-width="8" marker-end="url(#mech-right-{index})"/>
  <path d="M210 166v-64" stroke="#d99a24" stroke-width="6" marker-end="url(#mech-up-{index})"/>
  <defs>
    <marker id="mech-left-{index}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M10 0 0 5 10 10z" fill="#b83246"/></marker>
    <marker id="mech-right-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#1f7a5b"/></marker>
    <marker id="mech-up-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#d99a24"/></marker>
  </defs>
  <text x="158" y="284" font-size="24" font-weight="800" fill="#1354a5">F=ma</text>
"""
    if variant.startswith("coordinate"):
        return """
  <path d="M78 276V92M78 276h292" stroke="#172033" stroke-width="4"/>
  <circle cx="214" cy="184" r="72" fill="#ecf8f3" stroke="#1f7a5b" stroke-width="4"/>
  <path d="M104 248L344 112" stroke="#b83246" stroke-width="5"/>
  <circle cx="214" cy="184" r="6" fill="#1354a5"/>
  <text x="230" y="180" font-size="17" font-weight="800" fill="#1354a5">(a,b)</text>
  <text x="116" y="118" font-size="20" font-weight="800" fill="#b83246">y=mx+c</text>
"""
    return """
  <path d="M80 274V126M80 274h282" stroke="#172033" stroke-width="4"/>
  <path d="M106 246C150 172 202 130 260 150C300 164 324 218 350 246" fill="none" stroke="#1354a5" stroke-width="6"/>
  <path d="M122 220h204" stroke="#d99a24" stroke-width="4" stroke-dasharray="7 6"/>
  <text x="120" y="126" font-size="22" font-weight="800" fill="#b83246">x²</text>
  <text x="238" y="306" font-size="20" font-weight="800" fill="#1f7a5b">解后代回检查</text>
"""


def render_zh_visual_svg(visual: VisualBrief, index: int) -> str:
    title = visual.visual_type or "图文结合学习图"
    focus = visual.focus_point or title
    text = " ".join([title, focus, *visual.source_points]).lower()
    if any(word in text for word in ["会计记录", "原始", "分类账", "初始记录"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["核对", "银行对账", "试算平衡"]):
        return render_reconciliation_svg(index, "zh-CN")
    if any(word in text for word in ["财务报表", "比率"]):
        return render_financial_statement_svg(index, "zh-CN")
    if any(word in text for word in ["会计调整", "影响"]):
        return render_accounting_flow_svg(index, "zh-CN")
    if any(word in text for word in ["市场", "供需", "需求", "供给", "demand", "supply"]):
        return render_market_svg(index, "zh-CN", market_variant_from_text(text))
    if any(word in text for word in ["生产要素", "机会成本", "经济选择"]):
        return render_economic_flow_svg(index, "zh-CN")
    if any(word in text for word in ["集合", "韦恩"]):
        return render_venn_svg(index, "zh-CN")
    if any(word in text for word in ["力与运动", "合力"]):
        return render_force_svg(index, "zh-CN")
    if any(
        word in text
        for word in ["色谱", "层析", "分离", "纯度", "chromatography", "separation", "purity"]
    ):
        return render_analysis_svg(index)
    if any(
        word in text
        for word in ["有机", "烃", "原油", "聚合物", "organic", "hydrocarbon", "crude", "polymer"]
    ):
        return render_organic_svg(index)
    if any(
        word in text
        for word in [
            "键",
            "离子",
            "共价",
            "金属键",
            "结构",
            "bond",
            "bonding",
            "ionic",
            "covalent",
            "metallic",
            "structure",
        ]
    ):
        return render_bonding_svg(index)
    if any(
        word in text
        for word in [
            "粒子",
            "固体",
            "液体",
            "气态",
            "solid",
            "liquid",
            "particles",
            "states of matter",
        ]
    ):
        return render_particles_svg(index)
    if (
        "气体检验" in text
        or "gas test" in text
        or any(
            word in text
            for word in ["limewater", "splint", "hydrogen", "oxygen", "carbon dioxide", "chlorine"]
        )
    ):
        return render_gas_tests_svg(index, "zh-CN")
    if "酸碱" in text or re.search(r"\bph\b", text):
        return render_ph_svg(index)
    if any(word in text for word in ["速率", "平衡", "rate", "equilibrium", "haber"]):
        return render_rate_svg(index)
    if any(
        word in text for word in ["放热", "吸热", "能量", "exothermic", "endothermic", "energy"]
    ):
        return render_energy_svg(index)
    if any(
        word in text
        for word in [
            "三角函数",
            "正弦",
            "余弦",
            "正切",
            "弧度",
            "周期",
            "sine",
            "cosine",
            "trigonometric",
        ]
    ):
        return render_zh_math_topic_svg(index, "三角函数图", focus, "trig")
    if any(
        word in text
        for word in [
            "牛顿",
            "力学",
            "重力",
            "速度",
            "位移",
            "加速度",
            "动量",
            "冲量",
            "碰撞",
            "张力",
            "法向",
            "阻力",
            "运动学",
            "newton",
            "velocity",
            "acceleration",
            "momentum",
            "impulse",
        ]
    ):
        return render_zh_math_topic_svg(
            index, "力学关系图", focus, zh_math_variant("mechanics", text)
        )
    if any(
        word in text
        for word in ["坐标", "直线", "圆", "斜率", "交点", "coordinate", "straight line", "circle"]
    ):
        return render_zh_math_topic_svg(
            index, "坐标几何图", focus, zh_math_variant("coordinate", text)
        )
    if any(
        word in text
        for word in ["积分", "面积", "梯形", "integral", "integration", "area", "trapezium"]
    ):
        return render_zh_math_topic_svg(
            index, "积分面积图", focus, zh_math_variant("integral", text)
        )
    if any(
        word in text
        for word in [
            "导数",
            "微分",
            "切线",
            "法线",
            "驻点",
            "derivative",
            "differentiation",
            "tangent",
            "gradient",
        ]
    ):
        return render_zh_math_topic_svg(
            index, "微分与切线图", focus, zh_math_variant("calculus", text)
        )
    if any(
        word in text
        for word in [
            "数列",
            "级数",
            "等差",
            "等比",
            "二项式",
            "sequence",
            "series",
            "binomial expansion",
        ]
    ):
        return render_zh_math_topic_svg(
            index, "数列与级数图", focus, zh_math_variant("series", text)
        )
    if any(
        word in text
        for word in [
            "概率",
            "随机变量",
            "二项分布",
            "伯努利",
            "均值",
            "方差",
            "标准差",
            "统计",
            "probability",
            "distribution",
            "variance",
        ]
    ):
        return render_zh_math_topic_svg(
            index, "概率与分布图", focus, zh_math_variant("probability", text)
        )
    if any(
        word in text
        for word in [
            "代数",
            "二次",
            "方程",
            "不等式",
            "多项式",
            "函数",
            "根式",
            "指数",
            "因式",
            "余式",
            "配方",
            "algebra",
            "quadratic",
            "equation",
            "function",
            "polynomial",
            "surd",
        ]
    ):
        return render_zh_math_topic_svg(
            index, "代数关系图", focus, zh_math_variant("algebra", text)
        )
    if any(word in text for word in ["几何"]):
        return render_triangle_svg(index)
    fallback_title = title if title != "图文结合学习图" else focus
    return f"""
<svg class="visual-svg" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}">
  <title id="visual-title-{index}">{html_escape(fallback_title)}</title>
  <rect x="20" y="20" width="680" height="320" rx="20" fill="#ffffff" stroke="#d7deea"/>
  <rect x="54" y="58" width="210" height="244" rx="18" fill="#edf4ff" stroke="#9cbce8" stroke-width="3"/>
  <rect x="292" y="58" width="170" height="104" rx="16" fill="#ecf8f3" stroke="#a7d5c3" stroke-width="3"/>
  <rect x="292" y="198" width="170" height="104" rx="16" fill="#fff3d8" stroke="#e6c36d" stroke-width="3"/>
  <rect x="492" y="58" width="174" height="244" rx="18" fill="#fff1f3" stroke="#e5aab4" stroke-width="3"/>
  <path d="M264 180h28M462 110h30M462 250h30" stroke="#172033" stroke-width="4" marker-end="url(#arrow-zh-{index})"/>
  <defs><marker id="arrow-zh-{index}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#172033"/></marker></defs>
  <text x="92" y="106" font-size="25" font-weight="800" fill="#1354a5">图解</text>
  {svg_multiline_text(title, 92, 148, 10, 28, 24, 800, "#172033")}
  <text x="326" y="106" font-size="22" font-weight="800" fill="#1f7a5b">观察</text>
  <text x="326" y="246" font-size="22" font-weight="800" fill="#8a5f11">方法</text>
  <text x="530" y="108" font-size="22" font-weight="800" fill="#b83246">检查</text>
  <text x="326" y="136" font-size="16" fill="#5b677a">先看图中关系</text>
  <text x="326" y="276" font-size="16" fill="#5b677a">再写解题步骤</text>
  <text x="530" y="144" font-size="16" fill="#5b677a">最后回到题问</text>
  <text x="530" y="176" font-size="16" fill="#5b677a">术语、单位、结论</text>
</svg>
"""


def svg_multiline_text(
    value: str,
    x: int,
    y: int,
    max_chars: int,
    line_height: int,
    size: int = 12,
    weight: int = 700,
    fill: str = "#172033",
) -> str:
    lines = wrap_words(value, max_chars=max_chars)[:3]
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{html_escape(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}">{"".join(tspans)}</text>'
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    words = value.replace("/", " / ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
    if current:
        lines.append(current)
    return lines or [value[:max_chars]]


def html_escape(value: str) -> str:
    return html.escape(value, quote=True)
