from __future__ import annotations

import pytest

from intl_exam_guide import cli as cli_module
from intl_exam_guide.models import GuideRunOptions
from intl_exam_guide.providers import get_provider, infer_provider_from_url
from intl_exam_guide.providers import collegeboard as collegeboard_module
from intl_exam_guide.providers.collegeboard import (
    CollegeBoardAPProvider,
    ap_course_key,
    ap_units_from_parser,
    effective_fall_year_from_text,
    select_core_ced_link,
    validate_ced_effective_for_exam_year,
    validate_official_ced_url,
)
from intl_exam_guide.providers.common import BasicPageParser
from intl_exam_guide.providers.common import qualification_family
from intl_exam_guide.rendering.cover import render_cover
from intl_exam_guide.rendering.output_names import board_slug, level_slug
from intl_exam_guide.rendering.styles import stylesheet
from intl_exam_guide.validation.checks import validate_qualification_notes


def parsed_page(html: str, url: str = "https://apstudents.collegeboard.org/courses"):
    parser = BasicPageParser(url)
    parser.feed(html)
    return parser


def directory_parser() -> BasicPageParser:
    return parsed_page(
        """
        <a href="/courses/ap-calculus-ab">AP Calculus AB</a>
        <a href="/courses/ap-calculus-bc">AP Calculus BC</a>
        <a href="/courses/ap-cybersecurity">AP Cybersecurity</a>
        <a href="/courses/ap-career-kickstart">About AP Career Kickstart</a>
        <a href="/courses/ap-computer-science-program">About the AP Computer Science Courses</a>
        <a href="https://example.test/courses/ap-fake">AP Fake</a>
        """
    )


def course_parser() -> BasicPageParser:
    return parsed_page(
        """
        <title>AP Cybersecurity - AP Students</title>
        <h1>AP Cybersecurity</h1>
        <strong>Unit 1: Introduction to Security</strong>
        <strong>Unit 2: Securing Spaces</strong>
        <a href="https://apcentral.collegeboard.org/media/pdf/ap-cybersecurity-course-and-exam-description.pdf">
          <h3>AP Cybersecurity Course and Exam Description</h3>
        </a>
        <a href="https://apcentral.collegeboard.org/media/pdf/ap-cybersecurity-course-and-exam-description-clarification.pdf">
          <h3>AP Cybersecurity Course and Exam Description Clarifications and Corrections</h3>
        </a>
        """,
        "https://apstudents.collegeboard.org/courses/ap-cybersecurity",
    )


def test_collegeboard_provider_is_registered_and_inferred_from_official_urls():
    assert get_provider("collegeboard").name == "collegeboard"
    assert get_provider("ap").name == "collegeboard"
    assert (
        infer_provider_from_url("https://apstudents.collegeboard.org/courses/ap-biology")
        == "collegeboard"
    )
    assert (
        infer_provider_from_url(
            "https://apcentral.collegeboard.org/media/pdf/ap-biology-course-and-exam-description.pdf"
        )
        == "collegeboard"
    )


def test_ap_discovery_excludes_overview_and_nonofficial_pages(monkeypatch):
    monkeypatch.setattr(collegeboard_module, "parse_page", lambda _url: directory_parser())

    links = CollegeBoardAPProvider().discover_subject_pages()

    assert [link.text for link in links] == [
        "AP Calculus AB",
        "AP Calculus BC",
        "AP Cybersecurity",
    ]
    assert all(link.qualification_type == "advanced_placement" for link in links)


def test_ap_subject_query_requires_exact_choice_when_multiple_courses_match(monkeypatch):
    monkeypatch.setattr(collegeboard_module, "parse_page", lambda _url: directory_parser())
    provider = CollegeBoardAPProvider()

    selected = provider.find_qualification("AP Cybersecurity", "ap", "2027")
    assert selected.text == "AP Cybersecurity"
    assert selected.selected_exam_year == "2027"

    with pytest.raises(ValueError, match="multiple official courses") as exc:
        provider.find_qualification("Calculus", "ap")
    assert "AP Calculus AB" in str(exc.value)
    assert "AP Calculus BC" in str(exc.value)


def test_ap_course_page_selects_only_core_ced_and_records_units(monkeypatch):
    monkeypatch.setattr(collegeboard_module, "parse_page", lambda _url: course_parser())

    qualification = CollegeBoardAPProvider().parse_qualification(
        "https://apstudents.collegeboard.org/courses/ap-cybersecurity",
        "ap",
        "2027",
    )

    assert qualification.title == "AP Cybersecurity"
    assert qualification.qualification_type == "advanced_placement"
    assert qualification.qualification_family == "College Board Advanced Placement (AP)"
    assert qualification.subject_area == "Cybersecurity"
    assert qualification.source.specification_url.endswith(
        "ap-cybersecurity-course-and-exam-description.pdf"
    )
    assert "clarification" not in qualification.source.specification_url
    assert qualification.selected_exam_year == "2027"
    assert qualification.summary[-1] == "The official course page exposes 2 numbered units."


def test_ap_ced_selection_and_unit_helpers_reject_unsafe_candidates():
    parser = course_parser()

    selected = select_core_ced_link(parser)
    assert selected.text == "AP Cybersecurity Course and Exam Description"
    assert ap_units_from_parser(parser) == [
        "Unit 1: Introduction to Security",
        "Unit 2: Securing Spaces",
    ]

    with pytest.raises(ValueError, match="not an official core"):
        validate_official_ced_url(
            "https://apcentral.collegeboard.org/media/pdf/ap-latin-course-and-exam-description-clarification.pdf"
        )
    with pytest.raises(ValueError, match="not an official core"):
        validate_official_ced_url(
            "https://example.test/ap-cybersecurity-course-and-exam-description.pdf"
        )


def test_ap_download_records_ced_effective_version_and_checks_exam_year(monkeypatch, tmp_path):
    qualification = CollegeBoardAPProvider().parse_qualification(
        "https://apcentral.collegeboard.org/media/pdf/"
        "ap-cybersecurity-course-and-exam-description.pdf",
        "ap",
        "2027",
    )

    def fake_attach(qualification, output_dir, pdf_url, provider_prefix, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        text_path = output_dir / "collegeboard-cybersecurity-specification.txt"
        text_path.write_text(
            "AP Cybersecurity COURSE AND EXAM DESCRIPTION Effective Fall 2026",
            encoding="utf-8",
        )
        qualification.source.extracted_text_path = str(text_path)
        qualification.source.specification_url = pdf_url
        assert provider_prefix == "collegeboard"
        assert kwargs["filename_label"] == "cybersecurity"
        return qualification

    monkeypatch.setattr(collegeboard_module, "attach_pdf_content", fake_attach)
    downloaded = CollegeBoardAPProvider().download_specification(
        qualification, tmp_path, "2027"
    )

    assert downloaded.source.issue_version == "CED effective Fall 2026"
    assert downloaded.selected_exam_year == "2027"

    with pytest.raises(ValueError, match="not applicable to the 2026 AP exam year"):
        CollegeBoardAPProvider().download_specification(qualification, tmp_path, "2026")


def test_ap_effective_year_and_course_key_helpers():
    assert effective_fall_year_from_text("Effective Fall 2025") == 2025
    assert effective_fall_year_from_text("No version here") is None
    assert ap_course_key("College Board AP Calculus AB") == "calculus ab"
    assert qualification_family("collegeboard", "advanced_placement") == (
        "College Board Advanced Placement (AP)"
    )
    validate_ced_effective_for_exam_year(2025, "2026")
    with pytest.raises(ValueError, match="not applicable"):
        validate_ced_effective_for_exam_year(2025, "2025")


def test_ap_cover_uses_independent_template_palette_and_output_slugs(monkeypatch):
    monkeypatch.setattr(collegeboard_module, "parse_page", lambda _url: course_parser())
    qualification = CollegeBoardAPProvider().parse_qualification(
        "https://apstudents.collegeboard.org/courses/ap-cybersecurity", "ap", "2027"
    )
    qualification.source.issue_version = "CED effective Fall 2026"
    options = GuideRunOptions(
        requested_subject="AP Cybersecurity",
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        exam_year="2027",
    )

    html = render_cover(qualification, options)
    css = stylesheet()

    assert 'class="cover board-ap cover-template-ap"' in html
    assert "College Board Advanced Placement" in html
    assert "AP Cybersecurity study guide" in html
    assert "CED effective Fall 2026" in html
    assert "2027" in html
    assert "Course code" not in html
    assert ".cover.board-ap" in css
    assert "--cover-primary: #0076a8" in css
    assert "--cover-accent: #f4c542" in css
    assert ".cover-template-ap .cover-main" in css
    assert "grid-template-columns: minmax(0, 1fr)" in css
    assert board_slug(qualification) == "collegeboard-ap"
    assert level_slug(qualification) == "ap"


def test_cli_infers_ap_provider_from_subject_name_and_accepts_ap_level():
    assert cli_module.resolve_provider(None, "AP Biology") == "collegeboard"
    assert cli_module.resolve_provider(None, "College Board AP Latin") == "collegeboard"


def test_ap_qualification_validation_checks_provider_binding(monkeypatch):
    monkeypatch.setattr(collegeboard_module, "parse_page", lambda _url: course_parser())
    qualification = CollegeBoardAPProvider().parse_qualification(
        "https://apstudents.collegeboard.org/courses/ap-cybersecurity", "ap", "2027"
    )

    class Plan:
        pass

    plan = Plan()
    plan.qualification = qualification
    assert validate_qualification_notes(plan) == []

    qualification.provider = "unknown"
    issues = validate_qualification_notes(plan)
    assert [issue.message for issue in issues] == [
        "Advanced Placement qualification is not bound to College Board."
    ]
