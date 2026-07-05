from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.infographics import render_infographic_required


def sample_visual(provider: str = "prompt-queue") -> VisualBrief:
    return VisualBrief(
        topic_title="Bonding",
        focus_point="ionic bonding and properties",
        trigger="spatial structure and property links need a labelled visual",
        visual_type="bonding and structure infographic",
        complexity="infographic",
        image_provider=provider,
        prompt="Create a labelled bonding infographic anchored to the syllabus point.",
        source_points=["Describe ionic bonding."],
    )


def test_render_generated_infographic_branch():
    html = render_infographic_required(
        "Bonding",
        sample_visual("gpt-image-2"),
        {
            "file": "visual_001_bonding.png",
            "asset_status": "generated",
            "image_provider": "gpt-image-2",
        },
        "page 12",
        "en",
    )

    assert "generated-infographic" in html
    assert "Generated Infographic" in html
    assert "visual_001_bonding.png" in html
    assert "gpt-image-2" not in html
    assert "reviewed visual asset" not in html
    assert "Infographic Queue" not in html


def test_svg_fallback_stays_pending_until_reviewed_raster_is_imported():
    html = render_infographic_required(
        "Bonding",
        sample_visual(),
        {
            "id": "visual_001",
            "file": "visual_001_bonding.svg",
            "asset_status": "svg-fallback-needs-review",
            "image_provider": "deterministic-svg",
            "llm_visual_approved": True,
        },
        "page 12",
        "en",
    )

    assert "infographic-required" in html
    assert "Infographic Queue" in html
    assert "visual_001_bonding.svg" not in html
    assert "Prompt queue" in html
    assert "Visual job:" in html
    assert "visual_001" in html
    assert (
        "Generate or import a reviewed image for this visual ID to replace it automatically."
        in html
    )
    assert "Generated Infographic" not in html


def test_render_pending_infographic_branch():
    html = render_infographic_required(
        "Bonding",
        sample_visual("ask-user-infographic"),
        {
            "id": "visual_001",
            "asset_status": "external-generation-required",
        },
        "page 12",
        "en",
    )

    assert "infographic-required" in html
    assert "Infographic Queue" in html
    assert "external infographic generation pending" in html
    assert "Prompt queue" in html
    assert "bonding and structure infographic" in html
    assert "Visual job:" in html
    assert "visual_001" in html


def test_svg_fallback_replacement_note_respects_chinese_language():
    html = render_infographic_required(
        "Bonding",
        sample_visual(),
        {
            "id": "visual_001",
            "file": "visual_001_bonding.svg",
            "asset_status": "svg-fallback-needs-review",
            "image_provider": "deterministic-svg",
            "llm_visual_approved": True,
        },
        "第 12 页",
        "zh-CN",
    )

    assert "信息图任务：" in html
    assert "visual_001" in html
    assert "visual_001_bonding.svg" not in html
    assert "导入这个 visual ID 对应的复核图片后，会自动替换当前草图。" in html
    assert "Generate or import" not in html
