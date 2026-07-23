from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceRecord
from intl_exam_guide.providers.base import ExamBoardProvider, Link
from intl_exam_guide.providers.common import (
    BasicPageParser,
    attach_pdf_content,
    clean_text,
    dedupe_links,
    first_node_text,
    is_pdf_url,
    is_url,
    parse_page,
    subject_slug_from_query,
    title_from_url,
)


AP_COURSES_URL = "https://apstudents.collegeboard.org/courses"
AP_STUDENTS_HOST = "apstudents.collegeboard.org"
AP_CENTRAL_HOST = "apcentral.collegeboard.org"
AP_OVERVIEW_PATHS = {
    "/courses/ap-career-kickstart",
    "/courses/ap-computer-science-program",
}
AP_COURSE_PATH_RE = re.compile(r"^/courses/ap-[a-z0-9-]+/?$")
AP_UNIT_RE = re.compile(r"^Unit\s+(\d+)\s*:\s*(.+)$", re.IGNORECASE)
AP_EFFECTIVE_FALL_RE = re.compile(r"\bEffective\s+Fall\s+(20\d{2})\b", re.IGNORECASE)


class CollegeBoardAPProvider(ExamBoardProvider):
    name = "collegeboard"
    supported_levels = ("advanced_placement",)

    def discover_subject_pages(self) -> list[Link]:
        parser = parse_page(AP_COURSES_URL)
        courses = []
        for link in parser.links:
            if not is_official_ap_course_url(link.href):
                continue
            title = clean_text(link.text)
            if not title.startswith("AP "):
                continue
            courses.append(
                Link(
                    text=title,
                    href=canonical_course_url(link.href),
                    qualification_type="advanced_placement",
                )
            )
        return sorted(dedupe_links(courses), key=lambda link: link.text)

    def list_qualifications(self, subject_url: str) -> list[Link]:
        qualification = self.parse_qualification(subject_url, level="ap")
        return [
            Link(
                text=qualification.title,
                href=qualification.page_url,
                qualification_type="advanced_placement",
                specification_url=qualification.source.specification_url,
            )
        ]

    def find_qualification(
        self, query: str, level: str | None = None, exam_year: str | None = None
    ) -> Link:
        validate_ap_level(level)
        validate_ap_exam_year(exam_year)
        if is_url(query):
            validate_official_ap_input_url(query)
            return Link(
                text=title_from_url(query),
                href=canonical_course_url(query) if not is_pdf_url(query) else query,
                qualification_type="advanced_placement",
                selected_exam_year=exam_year,
            )

        candidates = self.discover_subject_pages()
        query_key = ap_course_key(query)
        exact = [
            link
            for link in candidates
            if query_key
            in {
                ap_course_key(link.text),
                ap_course_key(urllib.parse.urlparse(link.href).path.rsplit("/", 1)[-1]),
            }
        ]
        if len(exact) == 1:
            exact[0].selected_exam_year = exam_year
            return exact[0]

        partial = [link for link in candidates if query_key and query_key in ap_course_key(link.text)]
        if len(partial) == 1:
            partial[0].selected_exam_year = exam_year
            return partial[0]
        if len(partial) > 1:
            raise ValueError(format_ap_candidate_choices(query, partial))
        raise ValueError(
            f"College Board AP could not match {query!r} to one official AP course. "
            "Use an exact course title from the AP directory or provide the official course URL."
        )

    def parse_qualification(
        self, page_url: str, level: str | None = None, exam_year: str | None = None
    ) -> Qualification:
        validate_ap_level(level)
        selected_exam_year = validate_ap_exam_year(exam_year)
        validate_official_ap_input_url(page_url)

        if is_pdf_url(page_url):
            title = ap_title_from_ced_url(page_url)
            return self._qualification_from_parts(
                title=title,
                page_url=page_url,
                ced_url=page_url,
                units=[],
                exam_year=selected_exam_year,
            )

        parser = parse_page(page_url)
        title = clean_text(first_node_text(parser, "h1") or parser.title or title_from_url(page_url))
        if not title.startswith("AP "):
            raise ValueError(
                "The supplied College Board page is not an AP subject page with an AP course title."
            )
        ced_link = select_core_ced_link(parser)
        units = ap_units_from_parser(parser)
        return self._qualification_from_parts(
            title=title,
            page_url=canonical_course_url(page_url),
            ced_url=ced_link.href,
            units=units,
            exam_year=selected_exam_year,
        )

    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        ced_url = qualification.source.specification_url
        if not ced_url:
            raise ValueError("No College Board AP Course and Exam Description is attached.")
        validate_official_ced_url(ced_url)
        selected_exam_year = validate_ap_exam_year(
            exam_year or qualification.selected_exam_year
        )
        qualification.selected_exam_year = selected_exam_year
        qualification.source.selected_exam_year = selected_exam_year

        filename_label = subject_slug_from_query(qualification.subject_area or qualification.title)
        qualification = attach_pdf_content(
            qualification,
            output_dir,
            ced_url,
            self.name,
            exam_year=selected_exam_year,
            filename_label=filename_label or "ap-course",
        )
        extracted_path = qualification.source.extracted_text_path
        if extracted_path:
            text = Path(extracted_path).read_text(encoding="utf-8", errors="replace")
            effective_year = effective_fall_year_from_text(text)
            if effective_year:
                qualification.source.issue_version = f"CED effective Fall {effective_year}"
                validate_ced_effective_for_exam_year(effective_year, selected_exam_year)
        return qualification

    def apply_listing_metadata(self, qualification: Qualification, link: Link) -> Qualification:
        qualification.source.listing_subject = link.text
        qualification.source.listing_qualification_type = "advanced_placement"
        if link.selected_exam_year and not qualification.selected_exam_year:
            qualification.selected_exam_year = link.selected_exam_year
            qualification.source.selected_exam_year = link.selected_exam_year
        return qualification

    def _qualification_from_parts(
        self,
        *,
        title: str,
        page_url: str,
        ced_url: str,
        units: list[str],
        exam_year: str | None,
    ) -> Qualification:
        subject = ap_subject_area(title)
        summary = [
            "The official College Board Course and Exam Description is the core source for this AP course."
        ]
        if units:
            summary.append(f"The official course page exposes {len(units)} numbered units.")
        family = "College Board Advanced Placement (AP)"
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            course_market="not-applicable",
            specification_url=ced_url,
            qualification_family=family,
            selected_exam_year=exam_year,
        )
        return Qualification(
            title=title,
            code=None,
            qualification_type="advanced_placement",
            subject_area=subject,
            page_url=page_url,
            summary=summary,
            topics=[],
            assessments=[],
            source=source,
            audience_note=(
                "College Board AP courses are college-level courses for secondary-school students. "
                "Course authorization, availability, and exam registration depend on the school or "
                "authorized test center."
            ),
            provider=self.name,
            qualification_family=family,
            selected_exam_year=exam_year,
            route_tags=["College Board", "AP", "Course and Exam Description"],
        )


def is_official_ap_course_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    return (
        parsed.scheme == "https"
        and (parsed.hostname or "").lower() == AP_STUDENTS_HOST
        and bool(AP_COURSE_PATH_RE.fullmatch(parsed.path))
        and path not in AP_OVERVIEW_PATHS
    )


def canonical_course_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", "")
    )


def validate_official_ap_input_url(url: str) -> None:
    if is_pdf_url(url):
        validate_official_ced_url(url)
        return
    if not is_official_ap_course_url(url):
        raise ValueError(
            "College Board AP inputs must be an official apstudents.collegeboard.org course page "
            "or an official apcentral.collegeboard.org Course and Exam Description PDF."
        )


def validate_official_ced_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() != AP_CENTRAL_HOST
        or not path.endswith(".pdf")
        or "course-and-exam-description" not in path
        or any(term in path for term in ("clarification", "correction"))
    ):
        raise ValueError(
            "The selected AP source is not an official core College Board Course and Exam "
            "Description PDF. Clarification/correction files are supplemental only."
        )


def select_core_ced_link(parser: BasicPageParser) -> Link:
    candidates = []
    for link in parser.links:
        title = clean_text(link.text)
        lower = title.lower()
        if not lower.endswith("course and exam description"):
            continue
        try:
            validate_official_ced_url(link.href)
        except ValueError:
            continue
        candidates.append(Link(text=title, href=link.href, qualification_type="advanced_placement"))
    candidates = dedupe_links(candidates)
    if len(candidates) != 1:
        raise ValueError(
            "Expected exactly one official core Course and Exam Description on the AP course "
            f"page, but found {len(candidates)}. Do not guess between AP documents."
        )
    return candidates[0]


def ap_units_from_parser(parser: BasicPageParser) -> list[str]:
    units: dict[int, str] = {}
    for node in parser.nodes:
        match = AP_UNIT_RE.fullmatch(clean_text(node.text))
        if match:
            units[int(match.group(1))] = clean_text(match.group(2))
    return [f"Unit {number}: {units[number]}" for number in sorted(units)]


def ap_course_key(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"\bcollege\s+board\b", " ", value)
    value = re.sub(r"^\s*ap\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def ap_subject_area(title: str) -> str:
    return re.sub(r"^AP\s+", "", clean_text(title), flags=re.IGNORECASE).strip()


def ap_title_from_ced_url(url: str) -> str:
    title = title_from_url(url)
    title = re.sub(r"\s+Course And Exam Description.*$", "", title, flags=re.IGNORECASE)
    if not title.lower().startswith("ap "):
        title = f"AP {title}"
    return clean_text(title)


def format_ap_candidate_choices(query: str, candidates: list[Link]) -> str:
    lines = [
        f"College Board AP found multiple official courses for {query!r}.",
        "Choose one exact course title or URL:",
    ]
    lines.extend(f"{index}. {link.text} - {link.href}" for index, link in enumerate(candidates, 1))
    return "\n".join(lines)


def validate_ap_level(level: str | None) -> None:
    if level and level.lower().replace("-", "_") not in {"ap", "advanced_placement"}:
        raise ValueError("College Board provider supports only the AP / Advanced Placement level.")


def validate_ap_exam_year(value: str | None) -> str | None:
    if value is None:
        return None
    if not re.fullmatch(r"20\d{2}", value.strip()):
        raise ValueError(f"Invalid AP exam year: {value!r}. Use a four-digit year.")
    return value.strip()


def effective_fall_year_from_text(text: str) -> int | None:
    match = AP_EFFECTIVE_FALL_RE.search(text[:20000])
    return int(match.group(1)) if match else None


def validate_ced_effective_for_exam_year(
    effective_fall_year: int, exam_year: str | None
) -> None:
    if exam_year and int(exam_year) < effective_fall_year + 1:
        raise ValueError(
            f"The selected CED is effective Fall {effective_fall_year} and is not applicable "
            f"to the {exam_year} AP exam year."
        )
