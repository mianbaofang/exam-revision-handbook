from __future__ import annotations

import re

from intl_exam_guide.models import GuideRunOptions, Qualification
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.rendering.text import html_attribute_escape, html_escape, subject_display_name


def render_cover(qualification: Qualification, options: GuideRunOptions) -> str:
    language = handbook_body_language(options.output_language)
    board = exam_board_identity(qualification)
    context = cover_context(qualification, options, board, language)

    if board["class_name"] == "board-edexcel":
        return render_edexcel_cover(context, language)
    if board["class_name"] == "board-caie":
        return render_cambridge_cover(context, language)
    if board["class_name"] == "board-ap":
        return render_ap_cover(context, language)
    return render_aqa_cover(context, language)


def cover_context(
    qualification: Qualification,
    options: GuideRunOptions,
    board: dict[str, str],
    language: str,
) -> dict[str, str]:
    code = qualification.code or ""
    version = cover_version_label(qualification, options, language)
    year = (
        options.exam_year
        or qualification.selected_exam_year
        or qualification.source.selected_exam_year
    )
    return {
        "board_class": html_attribute_escape(board["class_name"]),
        "board_short": board["short"],
        "board_full": board["full"],
        "qtype": qualification_type_display(qualification),
        "subject": cover_subject_title(qualification, language),
        "study_title": cover_study_title(qualification, language),
        "code_html": cover_course_code(code, language),
        "identity_html": cover_identity_grid(version, year, language),
        "signal_html": cover_signal_grid(language),
    }


def render_aqa_cover(context: dict[str, str], language: str) -> str:
    return render_fixed_cover(context, language, "aqa")


def render_edexcel_cover(context: dict[str, str], language: str) -> str:
    return render_fixed_cover(context, language, "edexcel")


def render_cambridge_cover(context: dict[str, str], language: str) -> str:
    return render_fixed_cover(context, language, "caie")


def render_ap_cover(context: dict[str, str], language: str) -> str:
    return render_fixed_cover(context, language, "ap")


def render_fixed_cover(
    context: dict[str, str],
    language: str,
    template_name: str,
) -> str:
    board_class = context["board_class"]
    if language == "en":
        exam_board_label = "Exam board"
        guide_label = "Revision Guide"
        identity_label = "Course identity"
        description = "Specification-led revision guide"
    else:
        exam_board_label = "考试局"
        guide_label = "复习手册"
        identity_label = "课程身份"
        description = "基于官方考试大纲的复习手册"

    return f"""
<section class="cover {board_class} cover-template-{template_name}">
  <div class="exam-board-theme-strip {board_class}" aria-hidden="true"></div>
  <div class="cover-mast cover-{template_name}-mast">
    <div class="exam-board-name">
      <span>{exam_board_label}</span>
      <strong>{html_escape(context["board_full"])}</strong>
    </div>
    <div class="cover-signature-card">
      <span>{html_escape(context["board_short"])}</span>
      <strong>{guide_label}</strong>
      <em>{html_escape(context["qtype"])}</em>
    </div>
  </div>
  <div class="cover-main cover-{template_name}-main">
    <div class="cover-title-lockup">
      <div class="qualification-pill">{html_escape(context["qtype"])}</div>
      <h1>{html_escape(context["subject"])}</h1>
      {context["code_html"]}
    </div>
    <div class="cover-spec-card">
      <span>{identity_label}</span>
      <strong>{html_escape(context["study_title"])}</strong>
      <p>{description}</p>
    </div>
  </div>
  <div class="cover-footer cover-{template_name}-footer">
    {context["identity_html"]}
    {context["signal_html"]}
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
        items.append(
            f"<div><span>{html_escape(label)}</span><strong>{html_escape(version)}</strong></div>"
        )
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
    course_market = qualification.source.course_market
    if "pearson" in source or "edexcel" in source:
        return {
            "short": "Edexcel",
            "full": (
                "Pearson Edexcel Qualifications"
                if course_market == "uk-domestic"
                else "Pearson Edexcel International Qualifications"
            ),
            "class_name": "board-edexcel",
        }
    if "cambridge" in source or "caie" in source:
        return {
            "short": "CAIE",
            "full": "Cambridge International Education",
            "class_name": "board-caie",
        }
    if "collegeboard" in source or "college board" in source or "advanced placement" in source:
        return {
            "short": "AP",
            "full": "College Board Advanced Placement",
            "class_name": "board-ap",
        }
    if "oxfordaqa" in source or "oxford international aqa" in source or "aqa" in source:
        return {
            "short": "AQA",
            "full": "AQA Qualifications" if course_market == "uk-domestic" else "Oxford International AQA Examinations",
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
    if qualification.qualification_type == "uk_gcse":
        return "GCSE"
    if qualification.qualification_type == "uk_as_a_level":
        return "A-Level"
    if qualification.qualification_type == "advanced_placement":
        return "Advanced Placement (AP)"
    return "International A-Level"


def cover_subject_title(qualification: Qualification, language: str) -> str:
    if language == "zh-CN":
        label = subject_display_name(qualification)
        if label != "本课程":
            return label
        return stripped_subject_title(qualification)
    return stripped_subject_title(qualification)


def cover_study_title(qualification: Qualification, language: str) -> str:
    subject = cover_subject_title(qualification, language)
    if language != "en":
        return f"{subject} 复习手册"

    qtype = qualification_type_display(qualification)
    normalized = qtype.lower().replace("-", " ")
    if "igcse" in normalized or "international gcse" in normalized:
        level = "IGCSE"
    elif "advanced placement" in normalized:
        level = "AP"
    elif "as only" in normalized:
        level = "AS"
    elif "a level" in normalized:
        level = "A-Level"
    else:
        level = qtype
    return f"{level} {subject} study guide"


def stripped_subject_title(qualification: Qualification) -> str:
    title = re.sub(r"\s*\([^)]*\)\s*$", "", qualification.title).strip()
    for prefix in (
        "International GCSE",
        "International A-Level",
        "International AS-A-level",
        "International AS and A-level",
        "Cambridge IGCSE",
        "Cambridge International AS & A Level",
        "Edexcel International GCSE",
        "Pearson Edexcel International GCSE",
        "College Board Advanced Placement (AP)",
        "AP",
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
