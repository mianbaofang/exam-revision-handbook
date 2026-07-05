from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Qualification
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.rendering.text import html_escape, subject_display_name


def render_cover(qualification: Qualification, options: GuideRunOptions) -> str:
    language = handbook_body_language(options.output_language)
    board = exam_board_identity(qualification)
    qtype = qualification_type_display(qualification)
    subject = cover_subject_title(qualification, language)
    code = qualification.code or ("Unknown" if language == "en" else "未知")
    version = cover_version_label(qualification, options, language)
    year = (
        options.exam_year
        or qualification.selected_exam_year
        or qualification.source.selected_exam_year
    )
    scope_note = cover_scope_note(qualification, language)
    scope_html = f'<p class="course-scope-note">{html_escape(scope_note)}</p>' if scope_note else ""
    if language == "en":
        return f"""
<section class="cover">
  <div class="cover-mast">
    <div class="exam-board-badge {html_escape(board["class_name"])}">{html_escape(board["short"])}</div>
    <div class="exam-board-name">
      <span>Official exam board</span>
      <strong>{html_escape(board["full"])}</strong>
    </div>
  </div>
  <div class="cover-title-lockup">
    <div class="qualification-pill">{html_escape(qtype)}</div>
    <h1>{html_escape(subject)}</h1>
    <div class="course-code">Course code · {html_escape(code)}</div>
    {scope_html}
  </div>
  <div class="cover-identity-grid">
    <div><span>Specification / syllabus version</span><strong>{html_escape(version)}</strong></div>
    <div><span>Target exam year</span><strong>{html_escape(year or "Not specified")}</strong></div>
  </div>
</section>
"""
    return f"""
<section class="cover">
  <div class="cover-mast">
    <div class="exam-board-badge {html_escape(board["class_name"])}">{html_escape(board["short"])}</div>
    <div class="exam-board-name">
      <span>官方考试局</span>
      <strong>{html_escape(board["full"])}</strong>
    </div>
  </div>
  <div class="cover-title-lockup">
    <div class="qualification-pill">{html_escape(qtype)}</div>
    <h1>{html_escape(subject)}</h1>
    <div class="course-code">课程代码 · {html_escape(code)}</div>
    {scope_html}
  </div>
  <div class="cover-identity-grid">
    <div><span>考试大纲版本</span><strong>{html_escape(version)}</strong></div>
    <div><span>目标考试年份</span><strong>{html_escape(year or "未指定")}</strong></div>
  </div>
</section>
"""


def cover_scope_note(qualification: Qualification, language: str) -> str:
    if not is_oxfordaqa_as_math_9660_with_mechanics(qualification):
        return ""
    if language == "en":
        return (
            "Current AS route: Unit P1 + Unit PSM1. PSM1 includes Pure Maths, "
            "Statistics and Mechanics, so M1 forces, Newton's laws, momentum and "
            "collision topics are part of this mathematics specification."
        )
    return (
        "当前 AS 路线：Unit P1 + Unit PSM1。PSM1 包含 Pure Maths、Statistics "
        "和 Mechanics，所以 M1 的力、牛顿定律、动量与碰撞属于本数学大纲的应用力学部分。"
    )


def is_oxfordaqa_as_math_9660_with_mechanics(qualification: Qualification) -> bool:
    source_blob = " ".join(
        part
        for part in [
            qualification.title,
            qualification.code or "",
            qualification.subject_area or "",
            qualification.qualification_type,
            qualification.provider or "",
            qualification.source.provider,
            qualification.page_url,
            qualification.source.specification_url or "",
            *qualification.route_tags,
        ]
        if part
    ).lower()
    if "9660" not in source_blob:
        return False
    if "mathematics" not in source_blob:
        return False
    if not ("oxfordaqa" in source_blob or "oxford international aqa" in source_blob):
        return False

    content_blob = " ".join(
        [
            *(topic.title for topic in qualification.topics),
            *(point for topic in qualification.topics for point in topic.points),
            *(paper.title for paper in qualification.assessments),
            *(detail for paper in qualification.assessments for detail in paper.details),
        ]
    ).lower()
    return "psm1" in content_blob and ("mechanics" in content_blob or "m1." in content_blob)


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
