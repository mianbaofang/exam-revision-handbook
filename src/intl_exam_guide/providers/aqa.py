from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceRecord
from intl_exam_guide.providers.base import ExamBoardProvider, Link
from intl_exam_guide.providers.common import (
    attach_pdf_content,
    clean_text,
    code_from_text,
    dedupe_links,
    find_pdf_link,
    format_candidate_choices,
    first_assessment_from_nodes,
    first_node_text,
    first_teaching_from_nodes,
    is_pdf_url,
    is_url,
    normalize_level,
    parse_page,
    subject_terms_from_query,
    title_from_url,
)


AQA_SUBJECTS_URL = "https://www.aqa.org.uk/subjects"
AQA_HOST = "www.aqa.org.uk"


class AQAUKProvider(ExamBoardProvider):
    """Official AQA GCSE and A-Level source route for UK centres."""

    name = "aqa_uk"
    supported_levels = ("uk_gcse", "uk_as_a_level")
    course_market = "uk-domestic"

    def discover_subject_pages(self) -> list[Link]:
        parser = parse_page(AQA_SUBJECTS_URL)
        pages = [
            Link(text=link.text, href=link.href)
            for link in parser.links
            if is_aqa_subject_page(link.href)
        ]
        return sorted(dedupe_links(pages), key=lambda link: link.text)

    def list_qualifications(self, subject_url: str) -> list[Link]:
        parser = parse_page(subject_url)
        links = [
            Link(
                text=clean_text(link.text),
                href=canonical_aqa_course_url(link.href),
                qualification_type=aqa_uk_qualification_type(link.text, link.href, None),
            )
            for link in parser.links
            if is_aqa_course_url(link.href)
        ]
        return dedupe_links(links)

    def find_qualification(
        self, query: str, level: str | None = None, exam_year: str | None = None
    ) -> Link:
        if is_url(query):
            if not is_aqa_source_url(query):
                raise ValueError("AQA UK source URLs must use an official aqa.org.uk host.")
            return Link(
                text=title_from_url(query),
                href=query,
                qualification_type=aqa_uk_qualification_type(query, query, level),
            )

        candidates = self._catalogue_candidates(query, level)
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise ValueError(format_candidate_choices("AQA UK", query, candidates))
        raise ValueError(
            "AQA UK could not confirm one official GCSE or A-Level course from the subject "
            "query. Provide the official AQA course-page URL or a qualification code."
        )

    def parse_qualification(
        self, page_url: str, level: str | None = None, exam_year: str | None = None
    ) -> Qualification:
        if is_pdf_url(page_url):
            return self._qualification_from_parts(
                title=title_from_url(page_url),
                page_url=page_url,
                specification_url=page_url,
                qtype=aqa_uk_qualification_type(page_url, page_url, level),
                first_teaching=None,
                first_assessment=None,
            )

        parser = parse_page(page_url)
        title = clean_text(first_node_text(parser, "h1") or parser.title or title_from_url(page_url))
        specification_url = find_pdf_link(
            parser,
            include_terms=("specification", "download"),
            exclude_terms=("past-paper", "past paper", "mark-scheme", "mark scheme", "guide"),
        )
        if not specification_url:
            raise ValueError(
                "No AQA UK specification PDF link found on the official course page."
            )
        return self._qualification_from_parts(
            title=title,
            page_url=page_url,
            specification_url=specification_url,
            qtype=aqa_uk_qualification_type(title, page_url, level),
            first_teaching=first_teaching_from_nodes(parser.nodes),
            first_assessment=first_assessment_from_nodes(parser.nodes),
        )

    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        if not qualification.source.specification_url:
            raise ValueError("No AQA UK specification PDF URL is attached to the qualification.")
        return attach_pdf_content(
            qualification,
            output_dir,
            qualification.source.specification_url,
            self.name,
            exam_year=exam_year,
        )

    def _catalogue_candidates(self, query: str, level: str | None) -> list[Link]:
        parser = parse_page(AQA_SUBJECTS_URL)
        terms = set(subject_terms_from_query(query))
        code = code_from_text(query)
        candidates: list[Link] = []
        for link in parser.links:
            if not is_aqa_course_url(link.href):
                continue
            qtype = aqa_uk_qualification_type(link.text, link.href, None)
            if not matches_aqa_level(qtype, level):
                continue
            combined = f"{link.text} {link.href}".lower()
            if code and code not in combined:
                continue
            if terms and not terms.issubset(set(re.findall(r"[a-z0-9]+", combined))):
                continue
            candidates.append(
                Link(
                    text=clean_text(link.text),
                    href=canonical_aqa_course_url(link.href),
                    qualification_type=qtype,
                )
            )
        return dedupe_links(candidates)

    def _qualification_from_parts(
        self,
        title: str,
        page_url: str,
        specification_url: str,
        qtype: str,
        first_teaching: str | None,
        first_assessment: str | None,
    ) -> Qualification:
        family = "AQA AS & A Level" if qtype == "uk_as_a_level" else "AQA GCSE"
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            course_market=self.course_market,
            specification_url=specification_url,
            qualification_family=family,
            first_teaching=first_teaching,
            first_assessment=first_assessment,
        )
        summary = [
            "AQA UK AS and A Level assessment follows the selected UK specification."
            if qtype == "uk_as_a_level"
            else "AQA UK GCSE assessment follows the selected UK specification."
        ]
        if first_teaching:
            summary.append(f"First teaching: {first_teaching}")
        if first_assessment:
            summary.append(f"First external assessment: {first_assessment}")
        return Qualification(
            title=aqa_uk_clean_title(title),
            code=code_from_text(title) or code_from_text(page_url),
            qualification_type=qtype,
            subject_area=aqa_uk_subject_area(title),
            page_url=page_url,
            summary=summary,
            topics=[],
            assessments=[],
            source=source,
            audience_note=(
                "AQA AS and A Levels are UK qualifications. Confirm the selected specification "
                "and exam series with the school or exam centre."
                if qtype == "uk_as_a_level"
                else "AQA GCSEs are UK qualifications. Confirm the selected specification, tier, "
                "and exam series with the school or exam centre."
            ),
            provider=self.name,
            qualification_family=family,
            route_tags=["AQA", "uk-domestic"],
        )


def is_aqa_source_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme == "https" and (parsed.hostname or "").lower().endswith("aqa.org.uk")


def is_aqa_subject_page(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return is_aqa_source_url(url) and bool(re.fullmatch(r"/subjects/[^/]+/?", parsed.path))


def is_aqa_course_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return is_aqa_source_url(url) and bool(
        re.fullmatch(r"/subjects/[^/]+/(?:gcse|a-level)/[^/]+(?:/specification)?/?", parsed.path)
    )


def canonical_aqa_course_url(url: str) -> str:
    return re.sub(r"/specification/?$", "", url).rstrip("/")


def aqa_uk_qualification_type(title: str, url: str, level: str | None) -> str:
    normalized = normalize_level(level)
    if normalized in {"as", "as-level", "a-level", "alevel", "as-a-level"}:
        return "uk_as_a_level"
    if normalized in {"gcse", "igcse"}:
        return "uk_gcse"
    combined = f"{title} {url}".lower()
    if "/a-level/" in combined or "a-level" in combined or "a level" in combined:
        return "uk_as_a_level"
    if "/gcse/" in combined or "gcse" in combined:
        return "uk_gcse"
    return "unknown"


def matches_aqa_level(qtype: str, level: str | None) -> bool:
    normalized = normalize_level(level)
    if normalized in {"gcse", "igcse"}:
        return qtype == "uk_gcse"
    if normalized in {"as", "as-level", "a-level", "alevel", "as-a-level"}:
        return qtype == "uk_as_a_level"
    return True


def aqa_uk_clean_title(title: str) -> str:
    return clean_text(re.sub(r"\s*\|\s*(?:Overview\s*\|\s*)?AQA\s*$", "", title, flags=re.I))


def aqa_uk_subject_area(title: str) -> str | None:
    cleaned = re.sub(r"\b(AQA|GCSE|AS|A\s*Level|Overview)\b|\(\d{4}\)", " ", title, flags=re.I)
    return clean_text(cleaned) or None
