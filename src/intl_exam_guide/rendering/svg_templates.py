from __future__ import annotations

import html
import re

from intl_exam_guide.models import VisualBrief


def render_topic_visual_svg(visual: VisualBrief, index: int, language: str = "en") -> str:
    """Render only a neutral placeholder for legacy callers.

    Deliverable v0.5 visuals are supplied by the LLM/external asset workflow and
    recorded in visual_manifest.json.  Python must not pick subject-specific SVG
    templates from keywords.
    """

    title = visual.visual_type.strip() or visual.focus_point.strip() or "Reviewed visual asset"
    return render_concept_fallback_svg(index, title)


def render_concept_fallback_svg(index: int, title: str) -> str:
    safe_title = html_escape(title or "Reviewed visual asset")
    return f'''<svg class="visual-svg" width="720" height="360" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}" xmlns="http://www.w3.org/2000/svg">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="6" y="6" width="708" height="348" rx="26" fill="#f8fafc" stroke="#94a3b8" stroke-width="3"/>
  <rect x="34" y="34" width="652" height="78" rx="18" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
  <text x="360" y="82" text-anchor="middle" font-size="24" font-weight="700" fill="#0f172a">{safe_title}</text>
  <g transform="translate(78 150)">
    <rect x="0" y="0" width="160" height="90" rx="16" fill="#ffffff" stroke="#64748b" stroke-width="2"/>
    <rect x="202" y="0" width="160" height="90" rx="16" fill="#ffffff" stroke="#64748b" stroke-width="2"/>
    <rect x="404" y="0" width="160" height="90" rx="16" fill="#ffffff" stroke="#64748b" stroke-width="2"/>
    <path d="M160 45 H202 M362 45 H404" stroke="#0f766e" stroke-width="5" stroke-linecap="round"/>
    <text x="80" y="40" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">Source</text>
    <text x="80" y="65" text-anchor="middle" font-size="14" fill="#475569">evidence</text>
    <text x="282" y="40" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">Writer</text>
    <text x="282" y="65" text-anchor="middle" font-size="14" fill="#475569">visual decision</text>
    <text x="484" y="40" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">Reviewed</text>
    <text x="484" y="65" text-anchor="middle" font-size="14" fill="#475569">asset</text>
  </g>
  <text x="360" y="300" text-anchor="middle" font-size="16" fill="#475569">Final diagrams are generated or imported from the LLM-approved visual manifest.</text>
</svg>'''


def render_flow_svg(
    index: int,
    title: str,
    labels: tuple[str, ...],
    color_a: str = "#2563eb",
    color_b: str = "#0f766e",
) -> str:
    safe_title = html_escape(title)
    safe_labels = [html_escape(label) for label in labels[:4]] or ["Source", "Decision", "Review"]
    while len(safe_labels) < 4:
        safe_labels.append("Check")
    return f'''<svg class="visual-svg" width="720" height="360" viewBox="0 0 720 360" role="img" aria-labelledby="visual-title-{index}" xmlns="http://www.w3.org/2000/svg">
  <title id="visual-title-{index}">{safe_title}</title>
  <rect x="6" y="6" width="708" height="348" rx="24" fill="#ffffff" stroke="{html_escape(color_a)}" stroke-width="3"/>
  <text x="360" y="52" text-anchor="middle" font-size="24" font-weight="700" fill="#0f172a">{safe_title}</text>
  <g transform="translate(60 120)">
    <rect x="0" y="0" width="130" height="86" rx="14" fill="#eff6ff" stroke="{html_escape(color_a)}" stroke-width="2"/>
    <rect x="160" y="0" width="130" height="86" rx="14" fill="#ecfeff" stroke="{html_escape(color_b)}" stroke-width="2"/>
    <rect x="320" y="0" width="130" height="86" rx="14" fill="#eff6ff" stroke="{html_escape(color_a)}" stroke-width="2"/>
    <rect x="480" y="0" width="130" height="86" rx="14" fill="#ecfeff" stroke="{html_escape(color_b)}" stroke-width="2"/>
    <path d="M130 43 H160 M290 43 H320 M450 43 H480" stroke="#334155" stroke-width="4"/>
    <text x="65" y="50" text-anchor="middle" font-size="15" fill="#0f172a">{safe_labels[0]}</text>
    <text x="225" y="50" text-anchor="middle" font-size="15" fill="#0f172a">{safe_labels[1]}</text>
    <text x="385" y="50" text-anchor="middle" font-size="15" fill="#0f172a">{safe_labels[2]}</text>
    <text x="545" y="50" text-anchor="middle" font-size="15" fill="#0f172a">{safe_labels[3]}</text>
  </g>
</svg>'''


def render_accounting_flow_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed accounting flow asset")


def render_reconciliation_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed reconciliation asset")


def render_trial_balance_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed table asset")


def render_control_account_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed control account asset")


def render_error_correction_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed correction flow asset")


def render_incomplete_records_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed reconstruction asset")


def render_financial_statement_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed statement asset")


def render_accounting_statement_variant_svg(
    index: int,
    title: str,
    labels: tuple[str, ...],
) -> str:
    return render_flow_svg(index, title, labels)


def market_variant_from_text(text: str) -> str:
    lowered = text.lower()
    if "foreign" in lowered or "exchange" in lowered:
        return "foreign_exchange"
    if "disequilibrium" in lowered or "shortage" in lowered or "surplus" in lowered:
        return "disequilibrium"
    if "supply" in lowered and "shift" in lowered:
        return "supply"
    if "demand" in lowered and "shift" in lowered:
        return "demand"
    return "equilibrium"


def render_market_svg(index: int, language: str = "en", variant: str = "equilibrium") -> str:
    return render_concept_fallback_svg(index, "Reviewed market diagram asset")


def render_stakeholder_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed stakeholder map asset")


def render_business_comparison_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed comparison asset")


def render_cash_flow_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed cash-flow asset")


def render_break_even_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed break-even asset")


def render_marketing_mix_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed marketing mix asset")


def render_business_process_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed business process asset")


def render_operations_flow_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed operations asset")


def render_quality_checkpoint_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed quality checkpoint asset")


def render_organisation_structure_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed organisation asset")


def render_customer_segmentation_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed segmentation asset")


def render_history_timeline_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed timeline asset")


def render_history_cause_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed cause chain asset")


def render_history_source_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed source evidence asset")


def render_history_comparison_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed comparison asset")


def render_economic_flow_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed flow asset")


def render_venn_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed Venn asset")


def render_force_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed force diagram asset")


def render_gas_tests_svg(index: int, language: str = "en") -> str:
    return render_concept_fallback_svg(index, "Reviewed observation chart asset")


def render_number_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed number visual asset")


def render_algebra_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed algebra visual asset")


def render_statistics_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed statistics asset")


def render_particles_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed particle model asset")


def render_triangle_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed geometry asset")


def render_motion_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed motion graph asset")


def render_velocity_area_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed graph area asset")


def render_rate_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed rate graph asset")


def render_energy_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed energy diagram asset")


def render_ph_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed scale asset")


def render_organic_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed model asset")


def render_analysis_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed analysis asset")


def render_bonding_svg(index: int) -> str:
    return render_concept_fallback_svg(index, "Reviewed structure asset")


def render_math_topic_svg(index: int, title: str, focus: str, variant: str) -> str:
    return render_concept_fallback_svg(index, title)


def render_zh_math_topic_svg(index: int, title: str, focus: str, variant: str) -> str:
    return render_concept_fallback_svg(index, title)


def math_specific_title(default_title: str, focus: str) -> str:
    return default_title


def render_math_motif(index: int, variant: str, focus: str = "") -> str:
    return ""


def zh_math_specific_title(default_title: str, focus: str) -> str:
    return default_title


def zh_math_variant(base: str, text: str) -> str:
    return base


def render_zh_math_motif(index: int, variant: str, focus: str = "") -> str:
    return ""


def render_zh_visual_svg(visual: VisualBrief, index: int) -> str:
    return render_topic_visual_svg(visual, index, "zh-CN")


def svg_multiline_text(value: str, max_chars: int = 24) -> str:
    lines = wrap_words(value, max_chars)
    return "".join(
        f'<tspan x="0" dy="{0 if i == 0 else 18}">{html_escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    words = value.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def html_escape(value: str) -> str:
    return html.escape(str(value), quote=True)
