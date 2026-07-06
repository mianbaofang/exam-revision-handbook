from __future__ import annotations

from typing import Any

from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.icons import render_icon
from intl_exam_guide.rendering.text import html_escape
from intl_exam_guide.rendering.visual_assets import has_renderable_infographic


def render_infographic_required(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any] | None,
    source_label: str,
    language: str,
) -> str:
    if asset and has_renderable_infographic(asset):
        return _render_generated_infographic(title, visual, asset, source_label, language)
    return _render_pending_infographic(title, visual, asset, source_label, language)


def _render_generated_infographic(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any],
    source_label: str,
    language: str,
) -> str:
    filename = str(asset["file"])
    caption = "Generated Infographic" if language == "en" else "已生成信息图"
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    question = (
        "Use the infographic to explain or apply:"
        if language == "en"
        else "用这张信息图解释或应用："
    )
    prompt_label = "Generation prompt" if language == "en" else "生图提示词"
    visual_steps = (
        [
            "Read the labels and locate the key relationship.",
            "Match the visual evidence to one precise syllabus term.",
            "Write the final answer in the command word's form.",
        ]
        if language == "en"
        else [
            "阅读标签，定位核心关系。",
            "把图中证据对应到一个准确的大纲术语。",
            "按指令词要求写出最终答案。",
        ]
    )
    step_items = "".join(f"<li>{html_escape(step)}</li>" for step in visual_steps)
    return f"""
<figure class="visual-example generated-infographic" aria-label="Generated infographic for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="generated-infographic-grid">
    <img class="infographic-image" src="images/{html_escape(filename)}" alt="{html_escape(title)} infographic for {html_escape(visual.focus_point)}">
    <div class="visual-notes">
      <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
      <p class="visual-question">{html_escape(question)} <strong>{html_escape(visual.focus_point)}</strong>.</p>
      <ol>{step_items}</ol>
    </div>
  </div>
</figure>
"""


def _render_pending_infographic(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any] | None,
    source_label: str,
    language: str,
) -> str:
    provider = visual.image_provider
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    if provider.startswith("ask-user"):
        status = (
            "external infographic generation pending"
            if language == "en"
            else "复杂信息图待外部生成"
        )
    else:
        status = (
            f"waiting for reviewed image asset from {provider}"
            if language == "en"
            else f"等待 {provider} 生成并复核"
        )
    caption = "Infographic Pending" if language == "en" else "信息图待补充"
    why_label = "Why this needs a visual" if language == "en" else "为什么需要图解"
    type_label = "Visual type" if language == "en" else "图形类型"
    focus_label = "Focus" if language == "en" else "聚焦知识点"
    replacement_note = _render_replacement_note(asset, language)
    return f"""
<figure class="visual-example infographic-required" aria-label="Infographic pending for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="infographic-card">
    <div class="visual-model">{html_escape(status)}</div>
    <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
    {replacement_note}
    <p><strong>{html_escape(why_label)}:</strong> {html_escape(visual.trigger)}</p>
    <p><strong>{html_escape(type_label)}:</strong> {html_escape(visual.visual_type)}</p>
    <p><strong>{html_escape(focus_label)}:</strong> {html_escape(visual.focus_point)}</p>
  </div>
</figure>
"""


def _render_replacement_note(asset: dict[str, Any] | None, language: str) -> str:
    visual_id = str((asset or {}).get("id") or "").strip()
    if not visual_id:
        return ""
    note = (
        "A reviewed infographic will replace this placeholder in the final version."
        if language == "en"
        else "最终版本会用复核后的信息图替换这个占位说明。"
    )
    return f'<p class="visual-placeholder-note">{html_escape(note)}</p>'
