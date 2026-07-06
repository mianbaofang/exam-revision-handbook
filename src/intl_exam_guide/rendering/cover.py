from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Qualification
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.rendering.text import html_attribute_escape, html_escape, subject_display_name


def render_cover(qualification: Qualification, options: GuideRunOptions) -> str:
    language = handbook_body_language(options.output_language)
    board = exam_board_identity(qualification)
    board_class = html_attribute_escape(board["class_name"])
    qtype = qualification_type_display(qualification)
    subject = cover_subject_title(qualification, language)
    code = qualification.code or ""
    version = cover_version_label(qualification, options, language)
    year = (
        options.exam_year
        or qualification.selected_exam_year
        or qualification.source.selected_exam_year
    )
    identity_html = cover_identity_grid(version, year, language)
    code_html = cover_course_code(code, language)
    signal_html = cover_signal_grid(language)
    if language == "en":
        return f"""
<section class="cover {board_class}">
  <div class="exam-board-theme-strip {board_class}" aria-hidden="true"></div>
  <div class="cover-mast">
    <div class="exam-board-name">
      <span>Exam board</span>
      <strong>{html_escape(board["full"])}</strong>
    </div>
    <div class="cover-signature-card">
      <span>{html_escape(board["short"])}</span>
      <strong>Revision Guide</strong>
      <em>{html_escape(qtype)}</em>
    </div>
  </div>
  <div class="cover-main">
    <div class="cover-title-lockup">
      <div class="qualification-pill">{html_escape(qtype)}</div>
      <h1>{html_escape(subject)}</h1>
      {code_html}
    </div>
    <div class="cover-spec-card">
      <span>Course identity</span>
      <strong>{html_escape(board["short"])} handbook</strong>
      <p>Specification-led revision guide</p>
    </div>
  </div>
  <div class="cover-footer">
    {identity_html}
    {signal_html}
  </div>
</section>
"""
    return f"""
<section class="cover {board_class}">
  <div class="exam-board-theme-strip {board_class}" aria-hidden="true"></div>
  <div class="cover-mast">
    <div class="exam-board-name">
      <span>考试局</span>
      <strong>{html_escape(board["full"])}</strong>
    </div>
    <div class="cover-signature-card">
      <span>{html_escape(board["short"])}</span>
      <strong>复习手册</strong>
      <em>{html_escape(qtype)}</em>
    </div>
  </div>
  <div class="cover-main">
    <div class="cover-title-lockup">
      <div class="qualification-pill">{html_escape(qtype)}</div>
      <h1>{html_escape(subject)}</h1>
      {code_html}
    </div>
    <div class="cover-spec-card">
      <span>课程身份</span>
      <strong>{html_escape(board["short"])} 手册</strong>
      <p>基于官方考试大纲的复习手册</p>
    </div>
  </div>
  <div class="cover-footer">
    {identity_html}
    {signal_html}
  </div>
</section>
"""


def cover_course_code(code: str, language: str) -> str:
    if not code:
        return ""
    label = "Course code" if language == "en" else "课程代码"
    return (
        '<div class="course-code">'
        f"<span>{html_escape(label)}</span>"
        f"<strong>{html_escape(code)}</strong>"
        "</div>"
    )


def cover_signal_grid(language: str) -> str:
    if language == "en":
        items = [
            ("01", "Syllabus aligned"),
            ("02", "Topic based"),
            ("03", "Practice ready"),
        ]
    else:
        items = [
            ("01", "匹配大纲"),
            ("02", "按主题组织"),
            ("03", "练习导向"),
        ]
    cells = "".join(
        f"<div><span>{html_escape(number)}</span><strong>{html_escape(label)}</strong></div>"
        for number, label in items
    )
    return f'<div class="cover-signal-grid">{cells}</div>'


def cover_identity_grid(version: str, year: str | None, language: str) -> str:
    items: list[str] = []
    if version and not is_cover_version_fallback(version, language):
        label = "Specification / syllabus version" if language == "en" else "考试大纲版本"
        items.append(f"<div><span>{html_escape(label)}</span><strong>{html_escape(version)}</strong></div>")
    if year:
        label = "Target exam year" if language == "en" else "目标考试年份"
        items.append(f"<div><span>{html_escape(label)}</span><strong>{html_escape(year)}</strong></div>")
    if not items:
        return ""
    return f'<div class="cover-identity-grid">{"".join(items)}</div>'


def is_cover_version_fallback(version: str, language: str) -> bool:
    fallback = "See official specification/syllabus PDF" if language == "en" else "见官方考试大纲 PDF"
    return version.strip() == fallback


def exam_board_identity(qualification: Qualification) -> dict[str, str]:
    source = " ".join(
        part
        for part in [
            qualification.provider,
            qualification.source.provider,
            qualification.qualification_family,
            qualification.source.qualification_family,
            qualification.page_url,
            qualification.source.specification_url or "",
        ]
        if part
    ).lower()
    if "pearson" in source or "edexcel" in source:
        return {
            "short": "Edexcel",
            "full": "Pearson Edexcel International Qualifications",
            "class_name": "board-edexcel",
        }
    if "cambridge" in source or "caie" in source:
        return {
            "short": "CAIE",
            "full": "Cambridge International Education",
            "class_name": "board-caie",
        }
    if "oxfordaqa" in source or "oxford international aqa" in source or "aqa" in source:
        return {
            "short": "AQA",
            "full": "Oxford International AQA Examinations",
            "class_name": "board-aqa",
        }
    return {
        "short": "Board",
        "full": "Unspecified exam board",
        "class_name": "board-neutral",
    }


def qualification_type_display(qualification: Qualification) -> str:
    if qualification.qualification_family:
        return qualification.qualification_family
    if qualification.source.qualification_family:
        return qualification.source.qualification_family
    if qualification.qualification_type == "international_gcse":
        return "International GCSE"
    return "International AS-A-level"


def cover_subject_title(qualification: Qualification, language: str) -> str:
    if language == "zh-CN":
        label = subject_display_name(qualification)
        if label != "本课程":
            return label
        return stripped_subject_title(qualification)
    return stripped_subject_title(qualification)


def stripped_subject_title(qualification: Qualification) -> str:
    title = re.sub(r"\s*\([^)]*\)\s*$", "", qualification.title).strip()
    for prefix in (
        "International GCSE",
        "International AS-A-level",
        "International AS and A-level",
        "Cambridge IGCSE",
        "Cambridge International AS & A Level",
        "Edexcel International GCSE",
        "Pearson Edexcel International GCSE",
    ):
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix) :].strip(" -–—:")
            break
    return title or qualification.subject_area or qualification.title


def cover_version_label(
    qualification: Qualification,
    options: GuideRunOptions,
    language: str,
) -> str:
    source = qualification.source
    if source.issue_version:
        return source.issue_version
    if source.syllabus_year_range:
        suffix = "syllabus" if language == "en" else "考试大纲"
        return f"{source.syllabus_year_range} {suffix}"
    exam_year = options.exam_year or qualification.selected_exam_year or source.selected_exam_year
    if exam_year:
        return f"{exam_year} exams" if language == "en" else f"{exam_year} 考试"
    return "See official specification/syllabus PDF" if language == "en" else "见官方考试大纲 PDF"
