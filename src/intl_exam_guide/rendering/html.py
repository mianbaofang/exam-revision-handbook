from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from intl_exam_guide.models import (
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.planning.localization import zh_teachable_topic_title, zh_topic_keyword_label
from intl_exam_guide.planning.language_policy import (
    glossary_language,
    handbook_body_language,
    language_mode_label,
    with_body_language_options,
)
from intl_exam_guide.planning.source_points import (
    clean_source_point,
    merge_wrapped_source_points,
    visible_source_points,
)
from intl_exam_guide.planning.source_points import is_syllabus_shell
from intl_exam_guide.rendering.cover import render_cover
from intl_exam_guide.rendering.glossary import render_professional_glossary
from intl_exam_guide.rendering.icons import render_icon
from intl_exam_guide.rendering.infographics import render_infographic_required
from intl_exam_guide.rendering.output_names import default_handbook_paths
from intl_exam_guide.rendering.styles import stylesheet
from intl_exam_guide.rendering.story_modes import chinese_story_lines, english_story_lines
from intl_exam_guide.rendering.text import html_attribute_escape, html_escape, subject_display_name
from intl_exam_guide.rendering.visual_assets import (
    build_visual_asset_lookup,
    load_visual_manifest,
    visual_asset_key_from_brief,
)


def render_html(
    plan: GuidePlan,
    output_path: Path | None = None,
    visual_manifest_path: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    if output_path is None:
        base_dir = output_dir or Path(".")
        output_path = default_handbook_paths(base_dir, plan.qualification)[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qualification = plan.qualification
    selected_language = plan.run_options.output_language
    language = handbook_body_language(selected_language)
    body_options = with_body_language_options(plan.run_options)
    manifest_path = visual_manifest_path or output_path.parent / "images" / "visual_manifest.json"
    manifest_entries = load_visual_manifest(manifest_path)
    visual_assets = build_visual_asset_lookup(manifest_entries)
    html_lang = "zh-CN" if language == "zh-CN" else "en"
    page_title = (
        f"{qualification.title} Revision Guide"
        if language == "en"
        else f"{subject_display_name(qualification)}学习复习手册"
    )
    parts = [
        f'<!doctype html><html lang="{html_lang}"><head><meta charset="utf-8">',
        f"<title>{html_escape(page_title)}</title>",
        f"<style>{stylesheet()}</style></head><body>",
        render_cover(qualification, body_options),
        render_student_overview(qualification, plan.revision_stages, plan.run_options),
        render_professional_glossary(qualification, glossary_language(selected_language) or "en"),
        render_topic_map(qualification.topics, language, plan.topic_guides),
        render_topic_nav(qualification.topics, language, plan.topic_guides),
        render_topics(
            qualification.topics,
            plan.topic_guides,
            plan.practice_items,
            plan.visual_briefs,
            visual_assets,
            language,
            plan.run_options.explanation_style,
        ),
        render_reference_appendix(qualification, len(plan.practice_items), language),
        "</body></html>",
    ]
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def render_student_overview(
    qualification: Qualification,
    stages: list[str],
    options: GuideRunOptions,
) -> str:
    body_language = handbook_body_language(options.output_language)
    summary = "".join(f"<li>{html_escape(item)}</li>" for item in qualification.summary[:4])
    stage_items = "".join(f"<li>{html_escape(stage)}</li>" for stage in stages)
    return f"""
<section class="band student-overview">
  <h2>How to Study</h2>
  <div class="overview-grid">
    <article>
      <h3>Study Order</h3>
      <ol>{stage_items}</ol>
    </article>
    <article>
      <h3>Course Focus</h3>
      <ul>{summary}</ul>
    </article>
    <article>
      <h3>Guide Setup</h3>
      <ul>
        <li>Subject request: {html_escape(options.requested_subject)}</li>
        <li>Term support: {html_escape(language_mode_label(options.output_language))}</li>
        <li>Illustrations: {html_escape(image_provider_display(options, body_language))}</li>
        <li>Writing style: {html_escape(style_display(options.explanation_style, body_language))}</li>
      </ul>
    </article>
  </div>
</section>
"""


def style_display(style: str, language: str = "en") -> str:
    labels = (
        {
            "formal": "Formal",
            "friendly": "Friendly",
            "life": "Life Scene",
            "story": "Story",
            "detective": "Detective",
            "adventure": "Adventure",
        }
        if language == "en"
        else {
            "formal": "正经严谨",
            "friendly": "轻松愉快",
            "life": "生活场景",
            "story": "故事性强",
            "detective": "侦探推理",
            "adventure": "原创闯关",
        }
    )
    return labels.get(style, style)


def image_provider_display(options: GuideRunOptions, language: str = "en") -> str:
    if options.image_provider == "custom":
        model = options.image_model or ("custom model" if language == "en" else "自定义模型")
        return (
            f"custom illustration model: {model}"
            if language == "en"
            else f"自定义插图模型：{model}"
        )
    if options.image_provider == "prompt-queue":
        return (
            "complex visuals are tracked in the manifest; unfinished items stay in the image job queue"
            if language == "en"
            else "复杂图按清单生成与复核；未完成项会列入配图任务"
        )
    return (
        "visual assets are tracked for review before final delivery"
        if language == "en"
        else "配图资产会先进入复核清单，复核后才用于最终交付"
    )


def render_source_note(qualification: Qualification, language: str = "en") -> str:
    listing_note = render_listing_note(qualification, language)
    heading = "Audience and Sources" if language == "en" else "适用对象与来源"
    page_label = "Qualification page" if language == "en" else "课程页面"
    spec_label = "Specification PDF" if language == "en" else "考试大纲 PDF"
    hash_value = qualification.source.specification_sha256 or (
        "not downloaded" if language == "en" else "未下载"
    )
    audience_note = (
        qualification.audience_note
        if language == "en"
        else "本手册面向学习该国际课程的学生；官方英文说明保留在结构化来源文件中供复核。"
    )
    return f"""
<section class="band source">
  <h2>{html_escape(heading)}</h2>
  <p>{html_escape(audience_note)}</p>
  {listing_note}
  <ul>
    <li>{html_escape(page_label)}: <a href="{html_attribute_escape(qualification.page_url)}">{html_escape(qualification.page_url)}</a></li>
    <li>{html_escape(spec_label)}: {link_or_missing(qualification.source.specification_url, language)}</li>
    <li>PDF SHA-256: <code>{html_escape(hash_value)}</code></li>
  </ul>
</section>
"""


def render_language_policy() -> str:
    return """
<section class="band language-policy">
  <h2>Language Policy</h2>
  <ul class="plain">
    <li>The handbook body stays in English because the exam is in English.</li>
    <li>A selected support language adds a 30-50 item glossary; it does not translate the whole handbook.</li>
    <li>Template labels, explanations, worked examples, diagram text, and image prompts are not rendered as bilingual pairs.</li>
  </ul>
</section>
"""


def render_listing_note(qualification: Qualification, language: str = "en") -> str:
    source = qualification.source
    if not source.listing_subject:
        return ""
    pieces = []
    if source.listing_subject:
        label = "Subject group" if language == "en" else "科目组"
        pieces.append(f"{label}: {html_escape(source.listing_subject)}")
    if source.listing_group_label:
        label = "Website group" if language == "en" else "Website group"
        pieces.append(f"{label}: {html_escape(source.listing_group_label)}")
    if source.listing_style_class:
        label = "Detected class" if language == "en" else "Detected class"
        pieces.append(f"{label}: {html_escape(source.listing_style_class)}")
    return f'<p class="listing-note">{" · ".join(pieces)}</p>'


def render_summary(qualification: Qualification, language: str = "en") -> str:
    if language == "en":
        summary_items = qualification.summary[:5]
    else:
        summary_items = [
            "课程定位来自官方课程页面和考试大纲。",
            "详细学习内容按 PDF 大纲抽取结果整理。",
            "学生手册正文保持英文，术语对照表提供辅助语言支持。",
        ]
    items = "\n".join(f"<li>{html_escape(item)}</li>" for item in summary_items)
    heading = "Course Position" if language == "en" else "课程定位"
    return f"""
<section class="band">
  <h2>{html_escape(heading)}</h2>
  <ul class="plain">{items}</ul>
</section>
"""


def render_assessments(qualification: Qualification, language: str = "en") -> str:
    cards = []
    for index, paper in enumerate(qualification.assessments, start=1):
        if language == "en":
            title = paper.title
            detail_items = paper.details[:8]
        else:
            title = f"试卷 {index}"
            detail_items = [
                "考试时长、分值和占比以官方大纲为准。",
                "结构化输出中保留官方英文考试信息，便于老师或维护者复核。",
            ]
        details = "".join(f"<li>{html_escape(item)}</li>" for item in detail_items)
        cards.append(
            f'<article class="assessment"><h3>{html_escape(title)}</h3><ul>{details}</ul></article>'
        )
    if cards:
        body = "\n".join(cards)
    else:
        body = (
            '<p class="warning">No assessment structure was extracted. Review the source page manually.</p>'
            if language == "en"
            else '<p class="warning">没有抽取到考试结构，需要人工复核来源页面。</p>'
        )
    heading = "Assessment Structure" if language == "en" else "考试结构"
    return f'<section class="band"><h2>{html_escape(heading)}</h2><div class="assessment-grid">{body}</div></section>'


def render_topic_map(
    topics: list[Topic],
    language: str,
    topic_guides: list[TopicGuide] | None = None,
) -> str:
    rows = []
    guides = {guide.topic_title: guide for guide in topic_guides or []}
    display_topics = topics_with_guides(topics, topic_guides)
    display_titles = display_topic_titles(display_topics, language, topic_guides)
    for index, topic in enumerate(display_topics, start=1):
        guide = guides.get(topic.title)
        if language == "en":
            points = topic_map_mastery_text(guide, language) if guide else "Writer mastery summary missing."
            title = display_titles[index - 1]
        else:
            title = display_titles[index - 1]
            points = topic_map_mastery_text(guide, language) if guide else "缺少 Writer 写入的掌握目标。"
        title_link = f'<a href="#{topic_anchor(index)}">{html_escape(title)}</a>'
        rows.append(f"<tr><td>{index}</td><td>{title_link}</td><td>{html_escape(points)}</td></tr>")
    if language == "en":
        heading = "Study Roadmap"
        columns = "<tr><th>#</th><th>Knowledge unit</th><th>What to master</th></tr>"
    else:
        heading = "复习路线"
        columns = "<tr><th>#</th><th>知识单元</th><th>要掌握什么</th></tr>"
    return f"""
<section class="band">
  <h2>{heading}</h2>
  <table><thead>{columns}</thead>
  <tbody>{"".join(rows)}</tbody></table>
</section>
"""


def topic_map_mastery_text(guide: TopicGuide | None, language: str) -> str:
    """Roadmap mastery is Writer-owned; Python does not invent student-facing targets."""

    if guide and guide.mastery_summary.strip():
        return guide.mastery_summary.strip()
    return (
        "Writer mastery summary missing; keep this handbook in draft."
        if language == "en"
        else "缺少 Writer 写入的掌握目标；本手册只能作为草稿。"
    )


def display_topic_titles(
    topics: list[Topic],
    language: str,
    topic_guides: list[TopicGuide] | None = None,
) -> list[str]:
    titles = [
        display_topic_title(topic, index, language) for index, topic in enumerate(topics, start=1)
    ]
    duplicated = {title for title in titles if titles.count(title) > 1}
    if not duplicated:
        return titles

    guides = {guide.topic_title: guide for guide in topic_guides or []}
    used: set[str] = set()
    resolved: list[str] = []
    for index, (topic, title) in enumerate(zip(topics, titles, strict=True), start=1):
        if title not in duplicated:
            resolved_title = title
        else:
            suffix = unique_topic_title_suffix(topic, guides.get(topic.title), language)
            if suffix:
                if language == "zh-CN" and "：" in title:
                    resolved_title = f"{title.split('：', 1)[0]}：{suffix}"
                else:
                    left, right = ("（", "）") if language == "zh-CN" else (" (", ")")
                    resolved_title = f"{title}{left}{suffix}{right}"
            else:
                marker = f"第{index}项" if language == "zh-CN" else f"item {index}"
                left, right = ("（", "）") if language == "zh-CN" else (" (", ")")
                resolved_title = f"{title}{left}{marker}{right}"
        while resolved_title in used:
            marker = f"第{index}项" if language == "zh-CN" else f"item {index}"
            left, right = ("（", "）") if language == "zh-CN" else (" (", ")")
            resolved_title = f"{title}{left}{marker}{right}"
        used.add(resolved_title)
        resolved.append(resolved_title)
    return resolved


def unique_topic_title_suffix(topic: Topic, guide: TopicGuide | None, language: str) -> str:
    candidates: list[str] = []
    if guide and guide.mastery_summary.strip():
        candidates.append(guide.mastery_summary)
        candidates.append(guide.essence)
    if ":" in topic.title:
        candidates.append(topic.title.rsplit(":", 1)[-1])
    candidates.extend(topic.points[:1])

    for candidate in candidates:
        suffix = compact_topic_suffix(candidate, language)
        if suffix:
            return suffix
    return ""


def compact_topic_suffix(value: str, language: str) -> str:
    text = re.sub(r"\s+", " ", value).strip(" .。;；:：")
    if not text:
        return ""
    if language == "zh-CN":
        text = re.split(r"[。；;]", text, maxsplit=1)[0]
        if len(text) > 18:
            text = re.split(r"[，,]", text, maxsplit=1)[0]
        return truncate_topic_suffix(text, 18)

    text = re.split(r"[.;]", text, maxsplit=1)[0].strip()
    words = text.split()
    if len(words) > 7:
        text = " ".join(words[:7])
    return truncate_topic_suffix(text, 52)


def truncate_topic_suffix(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    compact = text[:max_length].rstrip(" ，,：:;；。+-−*/=()（）")
    return f"{compact}…"


def render_topic_nav(
    topics: list[Topic],
    language: str,
    topic_guides: list[TopicGuide] | None = None,
) -> str:
    heading = "Quick Navigation" if language == "en" else "快速目录"
    display_topics = topics_with_guides(topics, topic_guides)
    display_titles = display_topic_titles(display_topics, language, topic_guides)
    grouped_links: dict[str, list[str]] = {}
    for index, topic in enumerate(display_topics, start=1):
        title = display_titles[index - 1]
        group = topic_nav_group_label(topic, language)
        grouped_links.setdefault(group, []).append(
            f'<a href="#{topic_anchor(index)}"><span>T{index}</span>{html_escape(title)}</a>'
        )
    groups = []
    for group, links in grouped_links.items():
        groups.append(
            "<section class=\"topic-nav-group\">"
            f"<h3>{html_escape(group)}</h3>"
            f"<div class=\"topic-nav-links\">{''.join(links)}</div>"
            "</section>"
        )
    return f"""
<nav class="band topic-nav" aria-label="{html_escape(heading)}">
  <h2>{html_escape(heading)}</h2>
  <div class="topic-nav-grid">{"".join(groups)}</div>
</nav>
"""


def topic_nav_group_label(topic: Topic, language: str) -> str:
    code_match = re.match(r"^([A-Z]{1,5}\d*)\.\d+(?:\.KP\d+)?\b", topic.title.strip())
    if code_match:
        code = code_match.group(1)
        return f"{code} topics" if language == "en" else f"{code} 单元"
    numeric_match = re.match(r"^(\d+(?:\.\d+){0,2})\b", topic.title.strip())
    if numeric_match:
        code = numeric_match.group(1)
        return f"Section {code}" if language == "en" else f"第 {code} 节"
    for tag in topic.level_tags:
        clean = tag.strip()
        if clean:
            return f"{clean} topics" if language == "en" else f"{clean} 单元"
    return "Other topics" if language == "en" else "其他主题"


def topic_anchor(index: int) -> str:
    return f"topic-{index}"


def topics_with_guides(
    topics: list[Topic],
    topic_guides: list[TopicGuide] | None = None,
) -> list[Topic]:
    if not topic_guides:
        return topics
    guide_titles = {guide.topic_title for guide in topic_guides}
    matched_topics = [topic for topic in topics if topic.title in guide_titles]
    return matched_topics or topics


def render_revision_stages(stages: list[str], language: str = "en") -> str:
    items = "".join(f"<li>{html_escape(stage)}</li>" for stage in stages)
    heading = "Three-Stage Revision" if language == "en" else "三阶段复习法"
    return f'<section class="band"><h2>{html_escape(heading)}</h2><ol class="stage-list">{items}</ol></section>'


def render_topics(
    topics: list[Topic],
    topic_guides: list[TopicGuide],
    practice_items: list[PracticeItem],
    visual_briefs: list[VisualBrief],
    visual_assets: dict[str, dict[str, Any]] | None = None,
    language: str = "en",
    explanation_style: str = "friendly",
) -> str:
    grouped: dict[str, list[PracticeItem]] = {}
    for item in practice_items:
        grouped.setdefault(item.topic_title, []).append(item)
    guides = {guide.topic_title: guide for guide in topic_guides}
    visuals = {brief.topic_title: brief for brief in visual_briefs}

    sections = []
    display_topics = topics_with_guides(topics, topic_guides)
    display_titles = display_topic_titles(display_topics, language, topic_guides)
    for index, topic in enumerate(display_topics, start=1):
        guide = guides.get(topic.title)
        title = display_titles[index - 1]
        if language == "en":
            point_values = visible_source_points(topic, limit=5) if topic.points else []
        elif guide:
            point_values = guide.checklist[:4]
        else:
            point_values = ["根据官方大纲抽取结果复习本节内容。"]
        points = "".join(f"<li>{html_escape(point)}</li>" for point in point_values)
        if not points:
            points = (
                "<li>Use the official specification text to expand this topic into teachable sub-points.</li>"
                if language == "en"
                else "<li>根据官方大纲抽取结果复习本节内容。</li>"
            )
        examples = "\n".join(
            render_practice(item, language, title) for item in grouped.get(topic.title, [])[:2]
        )
        guide_block = render_topic_guide(guide, language) if guide else ""
        diagram_block = ""
        visual = visuals.get(topic.title)
        visual_block = (
            render_visual_example(topic, guide, visual, index, visual_assets, language)
            if guide and visual
            else ""
        )
        story_block = (
            render_story_modes(topic, guide, language, index)
            if guide and explanation_style in {"story", "detective", "adventure"}
            else ""
        )
        source_block = render_source_snippets(topic.source_snippets, language=language)
        key_heading = "Key Ideas" if language == "en" else "本节要掌握"
        logic_heading = "Exam Logic" if language == "en" else "做题逻辑"
        logic_focus = point_values[0] if point_values else title
        logic_goal = (
            render_exam_logic_goal(f"{title} {logic_focus}", language, logic_focus)
            if language == "en"
            else f"题目焦点：把 {logic_focus} 用到指令词要求的计算、读图、解释或判断中。"
        )
        topic_pitfall = guide.pitfall if guide and guide.pitfall else ""
        logic_pitfall = (
            f"Watch for: {topic_pitfall or 'answer the exact condition in the question before moving to the final line.'}"
            if language == "en"
            else f"注意：{topic_pitfall or '先回应题目的具体条件，再写最终答案。'}"
        )
        sections.append(
            f"""
<section class="topic" id="{topic_anchor(index)}">
  <h2>T{index}. {html_escape(title)}</h2>
  <div class="topic-grid">
    <div>
      <h3>{html_escape(key_heading)}</h3>
      <ul>{points}</ul>
    </div>
    <div class="logic-card">
      <h3>{html_escape(logic_heading)}</h3>
      <p>{html_escape(logic_goal)}</p>
      <p>{html_escape(logic_pitfall)}</p>
    </div>
  </div>
  {guide_block}
  {diagram_block}
  {visual_block}
  {story_block}
  {source_block}
  <div class="practice-block">{examples}</div>
</section>
"""
        )
    return "\n".join(sections)


def render_topic_guide(guide: TopicGuide, language: str) -> str:
    steps = "".join(f"<li>{html_escape(step)}</li>" for step in guide.worked_solution_steps)
    checklist = "".join(f"<li>{html_escape(item)}</li>" for item in guide.checklist)
    labels = (
        {
            "essence": "One-Sentence Essence",
            "analogy": "Everyday Analogy",
            "worked": "Method",
            "pitfall": "Exam Pitfall",
        }
        if language == "en"
        else {
            "essence": "一句话本质",
            "analogy": "生活化类比",
            "worked": "解题套路",
            "pitfall": "考试陷阱",
        }
    )
    return f"""
<div class="guide-grid">
  <article class="essence"><h3>{render_icon("target")}<span>{labels["essence"]}</span></h3><p>{html_escape(guide.essence)}</p></article>
  <article class="analogy"><h3>{render_icon("bridge")}<span>{labels["analogy"]}</span></h3><p>{html_escape(guide.analogy)}</p></article>
  <article class="worked"><h3>{render_icon("steps")}<span>{labels["worked"]}</span></h3><p>{html_escape(guide.mini_worked_example)}</p><ol>{steps}</ol></article>
  <article class="pitfall"><h3>{render_icon("alert")}<span>{labels["pitfall"]}</span></h3><p>{html_escape(guide.pitfall)}</p><ul>{checklist}</ul></article>
</div>
"""


def render_exam_logic_goal(focus: str, language: str, source_focus: str | None = None) -> str:
    display_focus = source_focus or focus
    if language != "en":
        return f"Question focus: stay inside this syllabus point: {display_focus}."
    lower = focus.lower()
    if any(word in lower for word in ["momentum", "impulse", "impact", "collision"]):
        action = "choose a positive direction, write signed momenta, and use the before-and-after relationship."
    elif any(
        word in lower
        for word in ["newton", "force", "friction", "normal reaction", "tension", "thrust"]
    ):
        action = "start with a force diagram, choose directions, and apply equilibrium or F = ma."
    elif any(
        word in lower for word in ["velocity", "speed", "displacement", "acceleration", "kinematic"]
    ) or ("motion" in lower and any(word in lower for word in ["graph", "gradient", "area under"])):
        action = (
            "identify the motion quantity or graph type before using formulae, gradients, or areas."
        )
    elif any(word in lower for word in ["probability", "random variable", "bernoulli", "binomial"]):
        action = "define the event or distribution first, then calculate the required probability or statistic."
    elif any(word in lower for word in ["sine", "cosine", "trigonometry"]):
        action = "connect the angle range, triangle rule, identity, or graph feature to the values requested."
    elif any(word in lower for word in ["integral", "integration", "area under", "trapezium"]):
        action = (
            "decide whether the task needs an antiderivative, a definite area, or an approximation."
        )
    elif any(word in lower for word in ["derivative", "differentiation", "tangent", "stationary"]):
        action = "connect the derivative to gradient, rate of change, tangent, normal, or stationary-point meaning."
    elif any(
        word in lower for word in ["circle", "straight line", "coordinate", "gradient", "midpoint"]
    ):
        action = "translate the geometry into coordinates, gradients, equations, distances, or intersections."
    elif any(word in lower for word in ["sequence", "series", "progression"]):
        action = (
            "identify the term, sum, ratio, or convergence condition before choosing a formula."
        )
    elif any(
        word in lower
        for word in [
            "surd",
            "indices",
            "factor",
            "polynomial",
            "quadratic",
            "equation",
            "inequality",
        ]
    ):
        action = "choose the algebraic form that exposes the roots, factors, signs, or exact simplification."
    else:
        action = "match the exact syllabus wording to the object, evidence, relationship, or judgement the question asks for."
    return f"Question focus: {action} Source point: {display_focus}"


def render_topic_diagram(topic: Topic, guide: TopicGuide, index: int, language: str) -> str:
    points = visible_source_points(topic, limit=4) if language == "en" else guide.checklist[:4]
    points = points or guide.checklist[:4] or [display_topic_title(topic, index, language)]
    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = format_source_reference(source, language, include_prefix=True)
    caption = "Concept Map" if language == "en" else "图文解释"
    action = "learn -> apply -> check" if language == "en" else "学习 -> 应用 -> 检查"
    topic_label = "TOPIC" if language == "en" else "主题"
    title = display_topic_title(topic, index, language)
    cards = []
    for number, point in enumerate(points[:4], start=1):
        cards.append(
            "<li>"
            f"<span>{number}</span>"
            f"<strong>{html_escape(point)}</strong>"
            f"<em>{html_escape(action)}</em>"
            "</li>"
        )
    return f"""
<figure class="topic-diagram" aria-label="Concept map for {html_escape(title)}">
  <figcaption>{html_escape(caption)}</figcaption>
  <div class="concept-html-map">
    <div class="concept-core">
      <span>{html_escape(topic_label)} {index}</span>
      <strong>{html_escape(title)}</strong>
      <small>{html_escape(source_label)}</small>
    </div>
    <ol>{"".join(cards)}</ol>
  </div>
</figure>
"""


def render_visual_example(
    topic: Topic,
    guide: TopicGuide,
    visual: VisualBrief,
    index: int,
    visual_assets: dict[str, dict[str, Any]] | None = None,
    language: str = "en",
) -> str:
    title = display_topic_title(topic, index, language)
    asset = (visual_assets or {}).get(visual_asset_key_from_brief(visual))
    if visual.complexity == "infographic":
        source = topic.source_snippets[0] if topic.source_snippets else None
        source_label = format_source_reference(source, language)
        return render_infographic_required(title, visual, asset, source_label, language)

    source = topic.source_snippets[0] if topic.source_snippets else None
    source_label = format_source_reference(source, language)
    visual_html = render_manifest_visual_asset(title, visual, asset) or render_pending_svg_visual(
        title, visual, asset, language
    )
    caption = "Visual Worked Example" if language == "en" else "图形例题"
    source_prefix = "Source anchor" if language == "en" else "来源依据"
    question = (
        "Use the diagram to explain or apply:" if language == "en" else "用这张图解释或应用："
    )
    visual_steps = (
        [
            "Label the visual feature that matches the syllabus point.",
            "Connect the label to one precise syllabus term.",
            "Finish with a sentence that answers the command word.",
        ]
        if language == "en"
        else [
            "标出图中对应大纲点的视觉特征。",
            "把标签连接到一个准确的大纲术语。",
            "用一句回应指令词的话收尾。",
        ]
    )
    step_items = "".join(f"<li>{html_escape(step)}</li>" for step in visual_steps)
    return f"""
<figure class="visual-example" aria-label="Visual worked example for {html_escape(title)}">
  <figcaption>{render_icon("visual")}<span>{html_escape(caption)}</span></figcaption>
  <div class="visual-grid">
    {visual_html}
    <div class="visual-notes">
      <div class="visual-source">{html_escape(source_prefix)}: {html_escape(source_label)}</div>
      <p class="visual-question">{html_escape(question)} <strong>{html_escape(visual.focus_point)}</strong>.</p>
      <ol>{step_items}</ol>
    </div>
  </div>
</figure>
"""


def render_manifest_visual_asset(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any] | None,
) -> str:
    if not asset:
        return ""
    filename = str(asset.get("file") or "")
    if not filename:
        return ""
    status = str(asset.get("asset_status") or "").lower()
    if visual.image_provider != "kroki" and status not in {
        "reviewed-generated",
        "generated",
        "provider-selected-generated",
    }:
        return ""
    if Path(filename).suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
        return ""
    return (
        f'<img class="visual-svg visual-asset" '
        f'src="images/{html_attribute_escape(filename)}" alt="{html_escape(title)} visual">'
    )


def render_pending_svg_visual(
    title: str,
    visual: VisualBrief,
    asset: dict[str, Any] | None,
    language: str,
) -> str:
    caption = "Reviewed visual required" if language == "en" else "需要复核后的图形资产"
    instruction = (
        "Use SVG only when it exactly fits the teaching idea; otherwise import an external infographic asset."
        if language == "en"
        else "只有完全匹配教学含义的图才使用 SVG；否则请导入外部信息图资产。"
    )
    visual_id = str((asset or {}).get("id") or "").strip()
    job_line = f"<p><strong>Visual ID:</strong> {html_escape(visual_id)}</p>" if visual_id else ""
    return f"""
<div class="infographic-card" aria-label="Reviewed visual required for {html_escape(title)}">
  <div class="visual-model">{html_escape(caption)}</div>
  <p>{html_escape(instruction)}</p>
  <p><strong>{html_escape("Visual type" if language == "en" else "图形类型")}:</strong> {html_escape(visual.visual_type)}</p>
  {job_line}
</div>
"""


def render_story_modes(topic: Topic, guide: TopicGuide, language: str, index: int) -> str:
    points = visible_source_points(topic, limit=1)
    focus = points[0] if points else guide.topic_title
    if language == "en":
        life, detective, quest = english_story_lines(topic.title, focus, index)
        return f"""
<div class="story-modes" aria-label="Narrative explanation styles for {html_escape(topic.title)}">
  <article>
    <h3>{render_icon("life")}<span>Life Scene</span></h3>
    <p>{life}</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>Detective Mode</span></h3>
    <p>{detective}</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>Adventure Mode</span></h3>
    <p>{quest}</p>
  </article>
</div>
"""
    title = display_topic_title(topic, index, language)
    focus = guide.checklist[0] if guide.checklist else "本节核心要求"
    life, detective, quest = chinese_story_lines(title, focus, index)
    return f"""
<div class="story-modes" aria-label="叙事化讲解风格：{html_escape(title)}">
  <article>
    <h3>{render_icon("life")}<span>生活场景</span></h3>
    <p>{life}</p>
  </article>
  <article>
    <h3>{render_icon("detective")}<span>侦探推理</span></h3>
    <p>{detective}</p>
  </article>
  <article>
    <h3>{render_icon("quest")}<span>闯关感讲解</span></h3>
    <p>{quest}</p>
  </article>
</div>
"""


def render_practice(item: PracticeItem, language: str, display_title: str | None = None) -> str:
    frame = "".join(f"<li>{html_escape(step)}</li>" for step in item.answer_frame)
    solution = "".join(f"<li>{html_escape(step)}</li>" for step in item.public_solution_steps)
    checkpoints = "".join(f"<li>{html_escape(point)}</li>" for point in item.answer_checkpoints)
    source = render_source_snippets(item.source_snippets, compact=True, language=language)
    labels = (
        {
            "worked": "Worked Example",
            "command": "Command",
            "difficulty": "Difficulty",
            "focus": "Focus",
            "try": "Try First",
            "solution": "Solution",
            "check": "Check",
        }
        if language == "en"
        else {
            "worked": "例题",
            "command": "指令词",
            "difficulty": "难度",
            "focus": "聚焦",
            "try": "先自己想",
            "solution": "解题步骤",
            "check": "检查答案",
        }
    )
    title = item.topic_title if language == "en" else (display_title or "本节内容")
    return f"""
<article class="practice">
  <h3>{render_icon("practice")}<span>{html_escape(title)} - {labels["worked"]}</span></h3>
  <div class="practice-meta">
    <span>{render_icon("command")}{labels["command"]}: {html_escape(item.command_word)}</span>
    <span>{render_icon("level")}{labels["difficulty"]}: {html_escape(item.difficulty)}</span>
    <span>{render_icon("focus")}{labels["focus"]}: {html_escape(item.focus_point)}</span>
  </div>
  <p class="practice-question">{html_escape(item.question)}</p>
  <h4>{render_icon("frame")}{labels["try"]}</h4>
  <ol>{frame}</ol>
  <h4>{render_icon("steps")}{labels["solution"]}</h4>
  <ol>{solution}</ol>
  <h4>{render_icon("check")}{labels["check"]}</h4>
  <ul>{checkpoints}</ul>
  {source}
</article>
"""


def render_reference_appendix(
    qualification: Qualification, practice_count: int, language: str
) -> str:
    listing_note = render_listing_note(qualification, language)
    assessment = render_assessments(qualification, language)
    heading = "Source Appendix" if language == "en" else "附录：来源与考试信息"
    practice_label = "Generated practice examples" if language == "en" else "生成例题数量"
    page_label = "Qualification page" if language == "en" else "课程页面"
    spec_label = "Specification PDF" if language == "en" else "考试大纲 PDF"
    hash_value = qualification.source.specification_sha256 or (
        "not downloaded" if language == "en" else "未下载"
    )
    audience_note = (
        qualification.audience_note
        if language == "en"
        else "官方英文来源和考试结构已保存在结构化输出中，供复核；学生手册正文保持英文，术语表提供辅助语言支持。"
    )
    return f"""
<section class="band source appendix">
  <h2>{html_escape(heading)}</h2>
  <p>{html_escape(audience_note)}</p>
  {listing_note}
  <ul>
    <li>{html_escape(page_label)}: <a href="{html_attribute_escape(qualification.page_url)}">{html_escape(qualification.page_url)}</a></li>
    <li>{html_escape(spec_label)}: {link_or_missing(qualification.source.specification_url, language)}</li>
    <li>PDF SHA-256: <code>{html_escape(hash_value)}</code></li>
    <li>{html_escape(practice_label)}: {practice_count}</li>
  </ul>
</section>
{assessment}
"""


def render_source_snippets(
    snippets: list[SourceSnippet], compact: bool = False, language: str = "en"
) -> str:
    summary = "Source anchor" if language == "en" else "来源依据"
    if not snippets:
        message = (
            "No page-level source snippet was matched for this section. Review manually."
            if language == "en"
            else "本节没有匹配到页码级来源片段，需要人工复核。"
        )
        return f'<details class="source-snippets"><summary>{html_escape(summary)}</summary><p class="warning">{html_escape(message)}</p></details>'
    css_class = "source-snippets compact" if compact else "source-snippets"
    if language == "zh-CN":
        review_note = (
            "官方英文来源片段已保存在结构化输出中，供老师或维护者复核；学生正文不混排英文原文。"
        )
        items = []
        for snippet in snippets:
            items.append(
                "<li>"
                f"<strong>第 {snippet.page} 页</strong> "
                f"<span>{html_escape(review_note)}</span>"
                "</li>"
            )
        return f'<details class="{css_class}"><summary>{html_escape(summary)}</summary><ul>{"".join(items)}</ul></details>'
    items = []
    for snippet in snippets:
        text = source_snippet_display_text(snippet.text)
        if compact and len(text) > 220:
            text = f"{text[:220].rstrip()}..."
        items.append(
            "<li>"
            f"<strong>p.{snippet.page}</strong> "
            f"<span>{html_escape(snippet.matched_term)}</span>"
            f"<blockquote>{html_escape(text)}</blockquote>"
            "</li>"
        )
    return f'<details class="{css_class}"><summary>{html_escape(summary)}</summary><ul>{"".join(items)}</ul></details>'


def source_snippet_display_text(text: str) -> str:
    source = re.sub(r"\s*•\s*", "; ", text)
    parts = re.split(r"\s+(?=[a-z]\)\s+)", source, flags=re.IGNORECASE)
    if len(parts) > 1:
        raw_parts = [clean_source_point(part).strip(" ;:") for part in parts]
        cleaned_parts = merge_wrapped_source_points(
            [part for part in raw_parts if part and not is_syllabus_shell(part)]
        )
        cleaned = "; ".join(part for part in cleaned_parts if part)
    else:
        cleaned = clean_source_point(source)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ;")
    return cleaned or "Source text recorded in the structured source files."


def format_source_reference(
    snippet: SourceSnippet | None,
    language: str = "en",
    include_prefix: bool = False,
) -> str:
    if not snippet:
        return "Source: review required" if language == "en" else "来源：需要复核"
    if language == "en":
        value = f"p.{snippet.page} - {snippet.matched_term}"
        return f"Source: {value}" if include_prefix else value
    value = f"第 {snippet.page} 页（官方原文见结构化来源文件）"
    return f"来源：{value}" if include_prefix else value


def link_or_missing(value: str | None, language: str = "en") -> str:
    if not value:
        missing = "missing" if language == "en" else "缺失"
        return f'<span class="warning">{html_escape(missing)}</span>'
    return f'<a href="{html_attribute_escape(value)}">{html_escape(value)}</a>'


def display_topic_title(topic: Topic, index: int, language: str) -> str:
    if language == "en":
        return topic.title
    return zh_teachable_topic_title(topic.title, index)


def localized_topic_title(title: str, index: int) -> str | None:
    keyword_title = zh_topic_keyword_label(title)
    if keyword_title:
        return keyword_title
    if re.search(r"[\u4e00-\u9fff]", title):
        return title[:32]
    return None
