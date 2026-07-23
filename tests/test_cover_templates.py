from __future__ import annotations

import pytest

from intl_exam_guide.models import GuideRunOptions, Qualification, SourceRecord
from intl_exam_guide.rendering.cover import render_cover
from intl_exam_guide.rendering.styles import stylesheet


def qualification_for(
    *,
    provider: str,
    title: str,
    code: str,
    family: str,
    issue_version: str | None = None,
    syllabus_year_range: str | None = None,
    exam_year: str,
) -> Qualification:
    return Qualification(
        title=title,
        code=code,
        qualification_type="international_gcse",
        subject_area=title.rsplit(" ", 1)[-1],
        page_url=f"https://example.test/{provider}/course",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(
            provider=provider,
            page_url=f"https://example.test/{provider}/course",
            specification_url=f"https://example.test/{provider}/specification.pdf",
            qualification_family=family,
            issue_version=issue_version,
            syllabus_year_range=syllabus_year_range,
            selected_exam_year=exam_year,
        ),
        audience_note="International students",
        provider=provider,
        qualification_family=family,
        selected_exam_year=exam_year,
    )


def run_options(exam_year: str) -> GuideRunOptions:
    return GuideRunOptions(
        requested_subject="Test course",
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        exam_year=exam_year,
    )


@pytest.mark.parametrize(
    ("qualification", "template", "board_class", "board_name", "version", "year", "study_title"),
    [
        (
            qualification_for(
                provider="oxfordaqa",
                title="International AS and A-level Mathematics",
                code="9660",
                family="International AS only",
                issue_version="May/June 2018 onwards exams",
                exam_year="2027",
            ),
            "aqa",
            "board-aqa",
            "Oxford International AQA Examinations",
            "May/June 2018 onwards exams",
            "2027",
            "AS Mathematics study guide",
        ),
        (
            qualification_for(
                provider="pearson",
                title="Pearson Edexcel International GCSE Economics",
                code="4EC1",
                family="International GCSE",
                issue_version="Issue 3 - November 2024",
                exam_year="2027",
            ),
            "edexcel",
            "board-edexcel",
            "Pearson Edexcel International Qualifications",
            "Issue 3 - November 2024",
            "2027",
            "IGCSE Economics study guide",
        ),
        (
            qualification_for(
                provider="cambridge",
                title="Cambridge IGCSE Chemistry",
                code="0620",
                family="Cambridge IGCSE",
                syllabus_year_range="2026-2028",
                exam_year="2027",
            ),
            "caie",
            "board-caie",
            "Cambridge International Education",
            "2026-2028 syllabus",
            "2027",
            "IGCSE Chemistry study guide",
        ),
    ],
)
def test_supported_boards_share_the_fixed_aqa_cover_structure(
    qualification: Qualification,
    template: str,
    board_class: str,
    board_name: str,
    version: str,
    year: str,
    study_title: str,
) -> None:
    html = render_cover(qualification, run_options(year))

    assert f'class="cover {board_class} cover-template-{template}"' in html
    assert f'class="cover-mast cover-{template}-mast"' in html
    assert f'class="cover-main cover-{template}-main"' in html
    assert f'class="cover-footer cover-{template}-footer"' in html
    assert "cover-edexcel-header" not in html
    assert "cover-edexcel-body" not in html
    assert "cover-caie-header" not in html
    assert "cover-caie-body" not in html

    ordered_blocks = [
        'class="exam-board-name"',
        'class="cover-signature-card"',
        'class="cover-title-lockup"',
        'class="cover-spec-card"',
        'class="cover-footer',
    ]
    positions = [html.index(marker) for marker in ordered_blocks]
    assert positions == sorted(positions)

    assert board_name in html
    assert qualification.code in html
    assert version in html
    assert year in html
    assert study_title in html


def test_supported_board_palettes_remain_fixed_and_layout_overrides_are_removed() -> None:
    css = stylesheet()

    assert ".cover.board-aqa" in css
    assert "--cover-primary: #1354a5" in css
    assert "--cover-accent: #b83246" in css
    assert "--cover-warm: #d99a24" in css
    assert ".cover.board-edexcel" in css
    assert "--cover-primary: #00838a" in css
    assert "--cover-accent: #2864a5" in css
    assert "--cover-warm: #83cec7" in css
    assert ".cover.board-caie" in css
    assert "--cover-primary: #c3313e" in css
    assert "--cover-accent: #1c345b" in css
    assert "--cover-warm: #e6b84c" in css
    assert ".cover-template-edexcel .cover-edexcel-body" not in css
    assert ".cover-template-caie .cover-caie-body" not in css


def test_narrow_screen_cover_rules_do_not_apply_to_a4_print_layout() -> None:
    css = stylesheet()

    assert "@media screen and (max-width: 760px)" in css
    assert "@media (max-width: 760px)" not in css
    narrow_screen_rules = css.split("@media screen and (max-width: 760px)", 1)[1].split(
        "@media print", 1
    )[0]
    assert "min-height: auto" in narrow_screen_rules
    assert "grid-template-rows: auto" in narrow_screen_rules
