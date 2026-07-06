from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.svg_templates import (
    html_escape,
    market_variant_from_text,
    render_concept_fallback_svg,
    render_flow_svg,
    render_topic_visual_svg,
    svg_multiline_text,
    wrap_words,
)


def visual(visual_type: str) -> VisualBrief:
    return VisualBrief(
        topic_title="Topic",
        focus_point="focus",
        trigger="trigger",
        visual_type=visual_type,
        complexity="svg-basic",
        image_provider="llm-svg",
        prompt="prompt",
        source_points=[],
    )


def assert_svg_contract(svg: str, title: str, index: int = 1) -> None:
    assert '<svg class="visual-svg"' in svg
    assert 'role="img"' in svg
    assert f'aria-labelledby="visual-title-{index}"' in svg
    assert f'<title id="visual-title-{index}">{title}</title>' in svg


def test_topic_visual_svg_uses_neutral_manifest_placeholder_not_keyword_templates():
    svg = render_topic_visual_svg(visual("demand supply ledger force gas pH triangle"), 1, "en")

    assert_svg_contract(svg, "demand supply ledger force gas pH triangle", 1)
    assert "Final diagrams are generated or imported" in svg
    assert "Demand and supply market diagram" not in svg
    assert "Accounting records flow" not in svg
    assert "Common gas tests" not in svg


def test_topic_visual_svg_uses_focus_when_visual_type_is_missing():
    brief = visual("")
    brief.focus_point = "source-bound visual decision"

    svg = render_topic_visual_svg(brief, 2, "zh-CN")

    assert_svg_contract(svg, "source-bound visual decision", 2)
    assert "Writer" in svg
    assert "Reviewed" in svg


def test_direct_flow_helper_is_generic_and_escapes_content():
    svg = render_flow_svg(
        3,
        "A&B <topic>",
        ("Choice", "Evidence", "Decision", "Check"),
        "#111111",
        "#222222",
    )

    assert_svg_contract(svg, "A&amp;B &lt;topic&gt;", 3)
    assert "Choice" in svg
    assert "Evidence" in svg
    assert "Decision" in svg
    assert "Check" in svg


def test_fallback_svg_escapes_titles_and_keeps_reviewed_asset_message():
    svg = render_concept_fallback_svg(4, 'A&B <topic> "quoted"')

    assert "A&amp;B &lt;topic&gt; &quot;quoted&quot;" in svg
    assert "LLM-approved visual manifest" in svg
    assert html_escape('"quoted" & <tag>') == "&quot;quoted&quot; &amp; &lt;tag&gt;"


def test_market_variant_helper_remains_for_legacy_importers():
    assert market_variant_from_text("Determination of foreign exchange rate") == "foreign_exchange"
    assert market_variant_from_text("Market disequilibrium shortage") == "disequilibrium"
    assert market_variant_from_text("Shifts of a supply curve") == "supply"
    assert market_variant_from_text("Shifts of a demand curve") == "demand"
    assert market_variant_from_text("Market equilibrium") == "equilibrium"


def test_text_wrapping_helpers_remain_stable():
    assert wrap_words("alpha beta gamma", 10) == ["alpha beta", "gamma"]
    assert "<tspan" in svg_multiline_text("alpha beta gamma", 10)
