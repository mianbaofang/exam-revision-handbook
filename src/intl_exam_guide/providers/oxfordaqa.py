from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
)
from intl_exam_guide.parsing.markdown_companion import write_markdown_companion
from intl_exam_guide.parsing.pdf_text import extract_pdf_pages, extract_pdf_text
from intl_exam_guide.providers.base import ExamBoardProvider, Link
from intl_exam_guide.providers.common import (
    TextNode,
    clean_text,
    dedupe,
    fetch_bytes,
    fetch_text,
    first_node_text,
    infer_qualification_type,
    is_pdf_url,
    title_from_url,
)

BASE_URL = "https://www.oxfordaqa.com"
SUBJECTS_URL = f"{BASE_URL}/subjects/"


@dataclass
class NumericContentSection:
    code: str
    title: str
    page: int
    lines: list[str]


class PageParser(HTMLParser):
    """Small standard-library parser for OxfordAQA's mostly static pages."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.stack: list[str] = []
        self.nodes: list[TextNode] = []
        self.links: list[Link] = []
        self._link_href: str | None = None
        self._link_class: str | None = None
        self._link_parts: list[str] = []
        self._heading_parts: list[str] | None = None
        self._recent_h3: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        attr_map = dict(attrs)
        if tag == "h3":
            self._heading_parts = []
        if tag == "a":
            href = attr_map.get("href")
            if href:
                self._link_href = urllib.parse.urljoin(self.base_url, href)
                self._link_class = attr_map.get("class")
                self._link_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._link_href:
            text = clean_text(" ".join(self._link_parts))
            if text:
                self.links.append(
                    Link(
                        text=text,
                        href=self._link_href,
                        qualification_type=qualification_type_from_listing(text, self._link_class),
                        subject_heading=self._recent_h3,
                        group_label=listing_group_label(text, self._link_class),
                        style_class=self._link_class,
                    )
                )
            self._link_href = None
            self._link_class = None
            self._link_parts = []
        if tag == "h3" and self._heading_parts is not None:
            heading = clean_text(" ".join(self._heading_parts))
            if heading:
                self._recent_h3 = heading
            self._heading_parts = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        tag = self.stack[-1] if self.stack else ""
        self.nodes.append(TextNode(tag=tag, text=text))
        if self._link_href:
            self._link_parts.append(text)
        if self._heading_parts is not None:
            self._heading_parts.append(text)


def parse_page(url: str) -> PageParser:
    parser = PageParser(base_url=url)
    parser.feed(fetch_text(url))
    return parser


def code_from_title(title: str) -> str | None:
    match = re.search(r"\((\d{4})\)", title)
    return match.group(1) if match else None


def extract_qualification_code(query: str) -> str | None:
    matches = re.findall(r"\b(\d{4})\b", query)
    if len(matches) == 1:
        return matches[0]
    return None


def oxfordaqa_subject_area_from_title(title: str) -> str | None:
    cleaned = re.sub(
        r"\b(OxfordAQA|Oxford|AQA|International|GCSE|AS|A|and|Level|A-level|Specification|Syllabus|PDF|Version)\b|\(\d{4}\)",
        " ",
        title,
        flags=re.I,
    )
    cleaned = re.sub(r"\b\d{4}\b|\b\d+\.\d+\b", " ", cleaned)
    return clean_text(cleaned) or None


def qualification_type_from_title(title: str) -> str:
    lower = title.lower()
    if "international gcse" in lower:
        return "international_gcse"
    if "international as" in lower or "a-level" in lower:
        return "international_as_a_level"
    if "international extended project qualification" in lower:
        return "international_as_a_level"
    return "unknown"


def qualification_type_from_listing(text: str, style_class: str | None = None) -> str | None:
    if style_class:
        if "btn--type-8" in style_class:
            return "international_gcse"
        if "btn--type-7" in style_class:
            return "international_as_a_level"
    qtype = qualification_type_from_title(text)
    return None if qtype == "unknown" else qtype


def listing_group_label(text: str, style_class: str | None = None) -> str | None:
    qtype = qualification_type_from_listing(text, style_class)
    if qtype == "international_gcse":
        return "blue International GCSE subject listing"
    if qtype == "international_as_a_level":
        return "red International AS-A-level subject listing"
    return None


def filter_candidates_by_level(candidates: list[Link], level_norm: str | None) -> list[Link]:
    if not level_norm:
        return candidates
    if level_norm in {"gcse", "igcse", "international-gcse"}:
        filtered = [
            candidate
            for candidate in candidates
            if candidate.qualification_type == "international_gcse"
            or "international gcse" in candidate.text.lower()
        ]
        return filtered or candidates
    if level_norm in {
        "as",
        "as-level",
        "international-as",
        "alevel",
        "a-level",
        "as-a-level",
        "international-as-a-level",
    }:
        filtered = [
            candidate
            for candidate in candidates
            if candidate.qualification_type == "international_as_a_level"
            or "international as" in candidate.text.lower()
            or "a-level" in candidate.text.lower()
        ]
        return filtered or candidates
    return candidates


def normalize_level_scope(level: str | None) -> str:
    if not level:
        return "qualification"
    normalized = level.lower().replace("_", "-").strip()
    if normalized in {"as", "as-level", "international-as"}:
        return "as"
    if normalized in {"a-level", "alevel", "international-a-level"}:
        return "a-level"
    return "qualification"


def filter_assessments_for_level_scope(
    papers: list[AssessmentPaper],
    level: str | None,
) -> list[AssessmentPaper]:
    if normalize_level_scope(level) != "as":
        return papers
    filtered = [
        paper
        for paper in papers
        if paper.title.lower().startswith("as ")
        or paper.title.lower().startswith("assessment evidence")
    ]
    return filtered or papers


class OxfordAQAProvider(ExamBoardProvider):
    name = "oxfordaqa"
    supported_levels = ("international_gcse", "international_as_a_level")

    def discover_subject_pages(self) -> list[Link]:
        parser = parse_page(SUBJECTS_URL)
        subjects: dict[str, Link] = {}
        for link in parser.links:
            parsed = urllib.parse.urlparse(link.href)
            if not parsed.path.startswith("/subjects/"):
                continue
            slug = parsed.path.strip("/").split("/")[-1]
            if not slug or slug == "subjects":
                continue
            if link.text.lower() in {"all subjects", "subjects"}:
                continue
            current = subjects.get(slug)
            if current is None or len(link.text) < len(current.text):
                subjects[slug] = link
        return sorted(subjects.values(), key=lambda item: item.text)

    def list_qualifications(self, subject_url: str) -> list[Link]:
        parser = parse_page(subject_url)
        seen: dict[str, Link] = {}
        for link in parser.links:
            path = urllib.parse.urlparse(link.href).path
            if "/qualifications/" not in path:
                continue
            if link.qualification_type not in {"international_gcse", "international_as_a_level"}:
                continue
            seen[link.href] = link
        return list(seen.values())

    def find_qualification(
        self, query: str, level: str | None = None, exam_year: str | None = None
    ) -> Link:
        if query.startswith("http://") or query.startswith("https://"):
            qtype = infer_qualification_type(query, query, level)
            return Link(
                text=title_from_url(query),
                href=query,
                qualification_type=None if qtype == "unknown" else qtype,
                specification_url=query if is_pdf_url(query) else None,
            )

        query_norm = query.lower().strip()
        code_query = extract_qualification_code(query_norm)
        candidates: list[Link] = []
        for subject in self.discover_subject_pages():
            if code_query:
                candidates.extend(self.list_qualifications(subject.href))
                continue
            if query_norm not in subject.text.lower() and query_norm not in subject.href.lower():
                continue
            candidates.extend(self.list_qualifications(subject.href))

        if not candidates:
            raise ValueError(
                f"No OxfordAQA subject-page candidates found for query: {query!r}. "
                "Provide the official qualification page URL, direct specification PDF URL, "
                "or exact four-digit qualification code."
            )

        if code_query:
            exact = self.find_by_qualification_code(candidates, code_query, level)
            if exact:
                return exact
            raise ValueError(f"No OxfordAQA qualification found for code: {code_query!r}")

        scored: list[tuple[int, Link]] = []
        for candidate in candidates:
            text = candidate.text.lower()
            href = candidate.href.lower()
            score = 0
            if query_norm in text or query_norm in href:
                score += 20
            if re.fullmatch(r"\d{4}", query_norm) and f"({query_norm})" in text:
                score += 50
            if level:
                level_norm = level.lower().replace("_", "-")
                if (
                    level_norm in {"gcse", "igcse", "international-gcse"}
                    and "international gcse" in text
                ):
                    score += 30
                if level_norm in {
                    "as",
                    "as-level",
                    "international-as",
                    "alevel",
                    "a-level",
                    "as-a-level",
                    "international-as-a-level",
                }:
                    if "international as" in text or "a-level" in text:
                        score += 30
            if score:
                scored.append((score, candidate))

        if not scored:
            raise ValueError(f"No OxfordAQA qualification found for query: {query!r}")

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def find_by_qualification_code(
        self,
        candidates: list[Link],
        code: str,
        level: str | None = None,
    ) -> Link | None:
        level_norm = level.lower().replace("_", "-") if level else None
        preferred = filter_candidates_by_level(candidates, level_norm)
        fallback = candidates if preferred != candidates else []
        for group in (preferred, fallback):
            for candidate in group:
                text = candidate.text.lower()
                href = candidate.href.lower()
                if f"({code})" in text or code in href:
                    return candidate
            for candidate in group:
                try:
                    qualification = self.parse_qualification(candidate.href)
                except (OSError, TimeoutError, urllib.error.URLError, ValueError):
                    continue
                if qualification.code == code:
                    return Link(
                        text=qualification.title,
                        href=candidate.href,
                        qualification_type=candidate.qualification_type,
                        subject_heading=candidate.subject_heading,
                        group_label=candidate.group_label,
                        style_class=candidate.style_class,
                    )
        return None

    def parse_qualification(
        self, page_url: str, level: str | None = None, exam_year: str | None = None
    ) -> Qualification:
        if is_pdf_url(page_url):
            title = title_from_url(page_url)
            qtype = infer_qualification_type(title, page_url, level)
            code = code_from_title(title) or extract_qualification_code(title) or extract_qualification_code(page_url)
            source = SourceRecord(
                provider=self.name,
                page_url=page_url,
                specification_url=page_url,
            )
            return Qualification(
                title=title,
                code=code,
                qualification_type=qtype,
                subject_area=oxfordaqa_subject_area_from_title(title),
                page_url=page_url,
                summary=[],
                topics=[],
                assessments=[],
                source=source,
                audience_note=audience_note(qtype),
                route_tags=[f"level-scope:{normalize_level_scope(level)}"] if level else [],
            )

        parser = parse_page(page_url)
        title = first_node_text(parser.nodes, "h1") or title_from_links(parser.links, page_url)
        code = code_from_title(title)
        qtype = qualification_type_from_title(title)
        subject_area = breadcrumb_subject(parser.nodes)
        summary = section_text(
            parser.nodes, start_text=title, end_text="Syllabus summary", max_items=8
        )
        # Topics are no longer extracted from web page.
        # The LLM Analyst will read syllabus-evidence.json from the PDF and decide topics.
        topics: list[Topic] = []
        assessments = extract_assessments(parser.nodes)
        specification_url = find_specification_url(parser.links)
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            specification_url=specification_url,
        )
        route_tags = [f"level-scope:{normalize_level_scope(level)}"] if level else []
        return Qualification(
            title=title,
            code=code,
            qualification_type=qtype,
            subject_area=subject_area,
            page_url=page_url,
            summary=summary,
            topics=topics,
            assessments=assessments,
            source=source,
            audience_note=audience_note(qtype),
            route_tags=route_tags,
        )

    def apply_listing_metadata(self, qualification: Qualification, link: Link) -> Qualification:
        if qualification.qualification_type == "unknown" and link.qualification_type:
            qualification.qualification_type = link.qualification_type
            qualification.audience_note = audience_note(link.qualification_type)
        if link.subject_heading:
            qualification.source.listing_subject = link.subject_heading
        if link.qualification_type:
            qualification.source.listing_qualification_type = link.qualification_type
        if link.group_label:
            qualification.source.listing_group_label = link.group_label
        if link.style_class:
            qualification.source.listing_style_class = link.style_class
        return qualification

    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        if not qualification.source.specification_url:
            raise ValueError("No specification PDF URL found on qualification page.")

        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_bytes = fetch_bytes(qualification.source.specification_url)
        digest = hashlib.sha256(pdf_bytes).hexdigest()
        code = qualification.code or "unknown"
        pdf_path = output_dir / f"oxfordaqa-{code}-specification.pdf"
        text_path = output_dir / f"oxfordaqa-{code}-specification.txt"
        pdf_path.write_bytes(pdf_bytes)
        pages = extract_pdf_pages(pdf_path)
        text_path.write_text(extract_pdf_text(pdf_path), encoding="utf-8")
        write_markdown_companion(pdf_path, source_pdf_sha256=digest, output_dir=output_dir)
        level_scope = qualification_level_scope(qualification)

        # Write candidate hints (page text only, no topic parsing)
        # These are optional reference hints for the LLM Analyst.
        # The LLM must read the evidence and decide topics itself.
        hints_path = output_dir / f"oxfordaqa-{code}-syllabus-candidate-hints.json"
        hints_path.write_text(
            json.dumps(
                {
                    "schema_version": "v0.5-evidence-hints",
                    "status": "evidence-only",
                    "note": "Python extracted page text only. The LLM syllabus_outline_analyst must read the official evidence and decide topic boundaries.",
                    "level_scope": level_scope,
                    "pages": [
                        {"page": page_num, "text": text[:5000]} for page_num, text in pages[:100]
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        attach_source_snippets(qualification, pages)
        qualification.assessments = filter_assessments_for_level_scope(
            qualification.assessments,
            level_scope,
        )

        qualification.source.specification_sha256 = digest
        qualification.source.specification_path = str(pdf_path)
        qualification.source.extracted_text_path = str(text_path)
        qualification.source.downloaded_at = datetime.now(UTC).isoformat()
        return qualification


def qualification_level_scope(qualification: Qualification) -> str | None:
    for tag in qualification.route_tags:
        if tag.startswith("level-scope:"):
            return tag.split(":", 1)[1]
    return None


def title_from_links(links: list[Link], page_url: str) -> str:
    for link in links:
        if link.href.rstrip("/") == page_url.rstrip("/"):
            return link.text
    return page_url.rstrip("/").split("/")[-1].replace("-", " ").title()


def breadcrumb_subject(nodes: list[TextNode]) -> str | None:
    h1_seen = False
    recent: list[str] = []
    for node in nodes:
        if node.tag == "h1":
            h1_seen = True
            break
        recent.append(node.text)
    if not h1_seen:
        return None
    for text in reversed(recent):
        if text not in {"Home", "Subjects"} and not text.startswith("International"):
            return text
    return None


def section_text(
    nodes: list[TextNode],
    start_text: str,
    end_text: str,
    max_items: int | None = None,
) -> list[str]:
    started = False
    values: list[str] = []
    for node in nodes:
        if node.text == start_text:
            started = True
            continue
        if not started:
            continue
        if node.text == end_text:
            break
        if node.tag in {"p", "li"} and len(node.text) > 20:
            values.append(node.text)
        if max_items and len(values) >= max_items:
            break
    return dedupe(values)


def extract_topics(nodes: list[TextNode]) -> list[Topic]:
    """DEPRECATED: Python no longer parses topics. LLM Analyst decides topics from evidence."""
    return []


def topics_from_region(region: list[TextNode], default_title: str | None = None) -> list[Topic]:
    """DEPRECATED: Python no longer parses topics. LLM Analyst decides topics from evidence."""
    return []


def extract_detailed_topics_from_pdf(
    pages: list[tuple[int, str]],
    level: str | None = None,
) -> list[Topic]:
    """DEPRECATED: Python no longer parses topics. LLM Analyst decides topics from evidence."""
    return []


def extract_oxfordaqa_mathematics_module_topics(
    pages: list[tuple[int, str]],
    level: str | None = None,
) -> list[Topic]:
    allowed_prefixes = {"P1", "PP1", "S1", "M1"}
    if normalize_level_scope(level) != "as":
        allowed_prefixes |= {"P2", "S2", "M2"}

    topics: list[Topic] = []
    current_code: str | None = None
    current_title: str | None = None
    current_page: int | None = None
    current_lines: list[str] = []
    used_titles: set[str] = set()
    saw_math_module = False

    def flush() -> None:
        nonlocal current_code, current_title, current_page, current_lines
        if current_code and current_title and current_page is not None:
            for unit_title, unit_points in split_section_units(current_lines):
                if not unit_points:
                    continue
                title = unique_topic_title(
                    f"{current_code} - {current_title}: {unit_title}",
                    used_titles,
                )
                snippet = clean_text(" ".join([current_code, current_title, *unit_points[:5]]))
                topics.append(
                    Topic(
                        title=title,
                        points=unit_points[:8],
                        source_snippets=[
                            SourceSnippet(
                                page=current_page,
                                text=snippet_around(snippet, unit_points[0], radius=420),
                                matched_term=current_code,
                            )
                        ],
                    )
                )
        current_code = None
        current_title = None
        current_page = None
        current_lines = []

    module_re = re.compile(r"^((?:P1|PP1|S1|M1|P2|S2|M2)\.\d+):\s+(.+)$")
    for page_number, page_text in pages:
        for raw_line in page_text.splitlines():
            line = clean_text(raw_line)
            if not line:
                continue
            if normalize_level_scope(level) == "as" and re.match(r"^3\.3(\s|$)", line):
                flush()
                current_code = None
                continue
            if current_code and re.match(r"^3\.\d+(?:\.\d+)?\s+", line):
                flush()
                current_code = None
                continue
            module_match = module_re.match(line)
            if module_match:
                saw_math_module = True
                flush()
                module_code = module_match.group(1)
                module_prefix = module_code.split(".", 1)[0]
                if module_prefix in allowed_prefixes:
                    current_code = module_code
                    current_title = strip_bullet(module_match.group(2))
                    current_page = page_number
                    current_lines = []
                continue
            if current_code and not is_oxfordaqa_math_boilerplate(line):
                current_lines.append(line)
    flush()
    if not saw_math_module:
        return []
    return clean_topics(topics)


def is_oxfordaqa_math_boilerplate(line: str) -> bool:
    lower = line.lower()
    if lower in {"content additional information"}:
        return True
    ignored_prefixes = (
        "--- page",
        "for international ",
        "oxfordaqa international",
        "students should learn the following formulae",
        "students may use relevant formulae",
        "students will be expected",
        "students will be required",
        "unit psm1 is comprised",
        "visit oxfordaqa.com",
        "scheme of assessment",
    )
    return lower.startswith(ignored_prefixes)


def choose_detailed_topics(
    reference_topics: list[Topic],
    numeric_topics: list[Topic],
    numeric_sections: list[NumericContentSection] | None = None,
) -> list[Topic]:
    reference_clean = clean_detailed_topics(reference_topics)
    if reference_clean:
        return reference_clean
    numeric_clean = clean_numeric_detailed_topics(numeric_topics)
    if len(numeric_clean) >= 6:
        return numeric_clean
    section_topics = expand_numeric_sections(numeric_sections or [])
    if len(section_topics) >= 6:
        return section_topics
    return numeric_clean if numeric_clean and all(topic.points for topic in numeric_clean) else []


def expand_numeric_sections(sections: list[NumericContentSection]) -> list[Topic]:
    topics: list[Topic] = []
    used_titles: set[str] = set()
    for section in sections:
        for index, (unit_title, unit_points) in enumerate(
            split_section_units(section.lines), start=1
        ):
            if not unit_points:
                continue
            title = unique_topic_title(f"{section.code}.{index} - {unit_title}", used_titles)
            snippet = clean_text(" ".join([section.code, section.title, *unit_points[:5]]))
            topics.append(
                Topic(
                    title=title,
                    points=unit_points[:8],
                    source_snippets=[
                        SourceSnippet(
                            page=section.page,
                            text=snippet_around(snippet, unit_points[0], radius=420),
                            matched_term=section.code,
                        )
                    ],
                )
            )
    return clean_topics(topics)


def split_section_units(lines: list[str]) -> list[tuple[str, list[str]]]:
    merged = merge_wrapped_lines(lines)
    units: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_points: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_points
        if current_title and current_points:
            units.append((current_title, dedupe(current_points)))
        current_title = None
        current_points = []

    for raw_line in merged:
        is_bullet = raw_line.strip().startswith(("•", "-", "*"))
        line = strip_bullet(raw_line)
        if not is_valid_detailed_content_line(line):
            continue
        if not is_bullet and starts_new_teachable_unit(line):
            flush()
            current_title = concise_unit_title(line)
            current_points = [line]
            continue
        if current_title is None:
            current_title = concise_unit_title(line)
            current_points = [line]
        else:
            current_points.append(line)
    flush()
    return units


def merge_wrapped_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for raw_line in lines:
        line = clean_text(raw_line)
        if not line:
            continue
        if merged and is_wrapped_continuation(merged[-1], line):
            merged[-1] = clean_text(f"{merged[-1]} {line}")
        else:
            merged.append(line)
    return merged


def is_wrapped_continuation(previous: str, current: str) -> bool:
    if current.strip().startswith(("•", "-", "*")):
        return False
    current_lower = current.lower()
    if (
        previous.strip().startswith(("•", "-", "*"))
        and not previous.rstrip().endswith((".", ")", ":"))
        and current
        and current[0].islower()
    ):
        return True
    if previous.rstrip().endswith((".", ":")):
        return False
    if current and current[0].islower():
        return True
    continuation_prefixes = (
        "and ",
        "or ",
        "for ",
        "from ",
        "of ",
        "to ",
        "with ",
        "using ",
        "including ",
    )
    return current_lower.startswith(continuation_prefixes)


def starts_new_teachable_unit(line: str) -> bool:
    lower = line.lower()
    if lower in {"content", "additional information"}:
        return False
    if is_formula_or_example_continuation_line(line):
        return False
    continuation_prefixes = (
        "including ",
        "could include",
        "will include",
        "may include",
        "to include",
        "note:",
        "the benefits",
        "limitations will include",
        "the form ",
        "the term ",
        "the notation ",
        "where ",
        "students are expected",
        "questions will",
        "questions may",
        "knowledge of the formulae",
        "maximum level of difficulty",
        "derivations of",
        "including use",
        "will be expected",
        "will be accepted",
    )
    return not lower.startswith(continuation_prefixes)


def is_section_title_continuation(line: str) -> bool:
    lower = line.lower()
    if lower.startswith(("content ", "content additional", "students ", "visit ")):
        return False
    return bool(line and line[0].islower() and is_valid_topic_title(line))


def concise_unit_title(line: str) -> str:
    title = re.split(
        r"\.\s+| including | could include | will include | may include ",
        line,
        maxsplit=1,
    )[0]
    title = title.strip().rstrip(".:")
    if len(title) > 88:
        title = title[:85].rstrip() + "..."
    return title or "Specification point"


def unique_topic_title(title: str, used_titles: set[str]) -> str:
    if title not in used_titles:
        used_titles.add(title)
        return title
    index = 2
    while f"{title} ({index})" in used_titles:
        index += 1
    unique = f"{title} ({index})"
    used_titles.add(unique)
    return unique


def is_numeric_topic_heading(code: str, title: str) -> bool:
    if len(code.split(".")) < 3:
        return False
    if re.search(r"\s+\d{1,3}$", title):
        return False
    lower = title.lower()
    if lower.startswith(("content", "scheme of assessment", "subject content")):
        return False
    return is_valid_topic_title(title)


def clean_numeric_detailed_topics(topics: list[Topic]) -> list[Topic]:
    cleaned = clean_topics(topics)
    codes = [topic.title.split(" - ", 1)[0] for topic in cleaned]
    leaf_topics: list[Topic] = []
    for topic, code in zip(cleaned, codes, strict=False):
        if any(other != code and other.startswith(f"{code}.") for other in codes):
            continue
        leaf_topics.append(topic)
    return leaf_topics


def is_reference_code(line: str) -> bool:
    return re.fullmatch(r"[A-Z]{1,3}\d+[A-Z]?", line.strip()) is not None


def is_valid_detailed_content_line(line: str) -> bool:
    lower = line.lower()
    ignored = {
        "core content extension content",
        "core content",
        "extension content",
        "content additional information",
        "students should be able to",
        "students should be able to:",
        "students should be able to understand",
        "students should be able to understand:",
        "+",
    }
    if lower in ignored:
        return False
    ignored_prefixes = (
        "visit oxfordaqa.com",
        "oxfordaqa international",
        "for exams ",
        "for international ",
        "page ",
    )
    if lower.startswith(ignored_prefixes):
        return False
    if re.fullmatch(r"\d+", lower):
        return False
    if is_formula_noise_line(line):
        return False
    return is_valid_topic_point(line)


def is_formula_or_example_continuation_line(line: str) -> bool:
    text = re.sub(r"\s+", " ", line.strip())
    lower = text.lower()
    if lower.startswith(("eg ", "e.g.", "for example", "where ")):
        return True
    if re.match(r"^[\d(=+\-*/∑∫]", text):
        return True
    if re.match(r"^[a-z]\s*[-=+\-*/]", lower):
        return True
    if re.match(r"^(?:e|var|p)\(", lower):
        return True
    if re.match(r"^[a-z]{1,3}\s+[a-z]{1,3}.*[=+\-*/]", lower):
        return True
    return False


def is_formula_noise_line(line: str) -> bool:
    text = re.sub(r"\s+", " ", line.strip())
    lower = text.lower()
    if re.search(r"[\uf000-\uf8ff]", text):
        return True
    if re.match(r"^[A-Z]{1,4}\d?\b.*[=()]", text):
        return True
    if re.match(r"(?i)^var\w*.*[=()]", text):
        return True
    if re.fullmatch(r"[=+\-*/;,\s]+", lower):
        return True
    if re.fullmatch(r"\d+(?:\s+\d+)+", lower):
        return True
    if re.fullmatch(r"(?:eg\s*)?[\d\s+\-*/=;,.()]+", lower):
        return True
    if re.search(r"\d|[=+\-*/^()<>∑∫]", text) and not formula_semantic_words(lower):
        return True
    if lower.startswith("eg ") and re.search(r"\d|[=+\-*/;]", lower):
        words = [word for word in re.findall(r"[a-z]+", lower) if word != "eg"]
        return not any(len(word) >= 3 for word in words)
    return False


def formula_semantic_words(lower: str) -> list[str]:
    math_function_words = {"cos", "sin", "tan", "log", "var", "exp", "sqrt"}
    return [
        word
        for word in re.findall(r"[a-z]+", lower)
        if len(word) >= 3 and word not in math_function_words
    ]


def clean_detailed_topics(topics: list[Topic]) -> list[Topic]:
    cleaned = clean_topics(topics)
    if len(cleaned) < 6:
        return []
    return cleaned


def topics_from_named_skill_section(nodes: list[TextNode]) -> list[Topic]:
    section_specs = [
        ("Taught skills", "Taught skills"),
        ("The International EPQ project process", "The International EPQ project process"),
        ("International GCSE Plus process", "International GCSE Plus process"),
    ]
    for start, title in section_specs:
        region = nodes_between_any(
            nodes,
            [start],
            ["Teaching resources available", "Teaching resources", "Assessment", "Recognition"],
        )
        topics = topics_from_region(region, default_title=title)
        if topics:
            return topics
    return []


def topics_from_assessment(nodes: list[TextNode]) -> list[Topic]:
    topics: list[Topic] = []
    for paper in extract_assessments(nodes):
        points = [
            strip_bullet(detail)
            for detail in paper.details
            if strip_bullet(detail) and not is_assessment_logistics(detail)
        ]
        if points:
            topics.append(Topic(title=paper.title, points=dedupe(points)))
    return clean_topics(topics)


def clean_topics(topics: list[Topic]) -> list[Topic]:
    cleaned: list[Topic] = []
    for topic in topics:
        title = strip_bullet(topic.title)
        if not is_valid_topic_title(title):
            continue
        points = [
            point
            for point in (strip_bullet(point) for point in topic.points)
            if is_valid_topic_point(point)
        ]
        cleaned.append(
            Topic(
                title=title,
                points=dedupe(points),
                level_tags=topic.level_tags,
                source_snippets=topic.source_snippets,
            )
        )
    return cleaned


def is_topic_heading(node: TextNode) -> bool:
    if not is_valid_topic_title(node.text):
        return False
    if node.tag in {"h3", "h4", "h5", "h6", "strong"}:
        return True
    if node.tag == "span":
        text = node.text.strip()
        return text.endswith(":") or text.lower() in {"as", "as:", "a-level only", "a-level only:"}
    return False


def topic_point_text(node: TextNode) -> str | None:
    if node.tag not in {"li", "p", "span"}:
        return None
    text = strip_bullet(node.text)
    if is_valid_topic_point(text):
        return text
    return None


def strip_bullet(text: str) -> str:
    return text.strip().lstrip("•*-").strip().rstrip(":").strip()


def is_valid_topic_title(text: str) -> bool:
    lower = text.lower().strip()
    if len(text.strip()) < 3 and lower != "as":
        return False
    ignored_prefixes = (
        "assessment objectives",
        "candidate record forms",
        "download",
        "for current cohorts",
        "new:",
        "please note",
        "please see",
        "revised for",
        "view ",
    )
    if lower.startswith(ignored_prefixes):
        return False
    if lower in {".", "and", "or"}:
        return False
    return True


def is_valid_topic_point(text: str) -> bool:
    if len(text.strip()) < 3:
        return False
    lower = text.lower().strip()
    ignored_prefixes = (
        "download ",
        "find out more",
        "please see",
        "published by",
        "request ",
        "view ",
    )
    if lower.startswith(ignored_prefixes):
        return False
    if lower in {".", "(pdf)", "(word)"}:
        return False
    return True


def extract_assessments(nodes: list[TextNode]) -> list[AssessmentPaper]:
    region = nodes_between_any(
        nodes, ["Assessment"], ["Thinking about switching", "Course specification"]
    )
    if not region:
        region = nodes_between(nodes, "Assessment", "Course specification")

    papers: list[AssessmentPaper] = []
    current: AssessmentPaper | None = None
    paper_re = re.compile(r"^(Core|Extension|AS|A-level|Paper|Unit|[A-Z].* Paper).*:?$")
    detail_re = re.compile(
        r"(marks|hour|%|exam|assessed|calculator|written|on-screen|qualification)", re.I
    )

    for node in region:
        text = node.text.rstrip(":")
        if is_assessment_heading(node, paper_re):
            if current:
                papers.append(current)
            current = AssessmentPaper(title=text)
            continue
        if current is None and node.tag in {"li", "p"} and is_valid_assessment_detail(node.text):
            current = AssessmentPaper(title="Assessment evidence and objectives")
        if current and (node.tag in {"li", "p", "span"} or detail_re.search(node.text)):
            if is_valid_assessment_detail(node.text):
                current.details.append(node.text)
    if current:
        papers.append(current)

    return papers


def is_assessment_heading(node: TextNode, paper_re: re.Pattern[str]) -> bool:
    text = node.text.strip().rstrip(":")
    if not is_valid_topic_title(text):
        return False
    if paper_re.search(text) and ("Paper" in text or "Unit" in text):
        return True
    lower = text.lower()
    project_headings = {
        "individual project",
        "group sustainability action project",
        "non-exam assessment (nea)",
    }
    return node.tag in {"strong", "h5", "h6"} and lower in project_headings


def is_valid_assessment_detail(text: str) -> bool:
    lower = strip_bullet(text).lower()
    if not lower:
        return False
    ignored_prefixes = (
        "candidate record forms",
        "download ",
        "find out more",
        "please note",
        "supporting assessment resources",
        "view ",
    )
    return not lower.startswith(ignored_prefixes)


def is_assessment_logistics(text: str) -> bool:
    lower = strip_bullet(text).lower()
    logistics_patterns = [
        r"^\d+\s*(marks?|%)",
        r"^\d+%\s+of",
        r"^\d+\s+hour",
        r"^first (as |a-level |gcse )?(exam|assessment)",
        r"^written exam",
        r"^closed-book exam",
        r"^open-book exam",
        r"^on-screen exam",
        r"^calculator",
        r"^non-calculator",
        r"^students answer",
        r"^assessed by",
        r"^the supervisor",
        r"^schools must",
    ]
    return any(re.search(pattern, lower) for pattern in logistics_patterns)


def nodes_between(nodes: list[TextNode], start: str, end: str) -> list[TextNode]:
    return nodes_between_any(nodes, [start], [end])


def nodes_between_any(nodes: list[TextNode], starts: list[str], ends: list[str]) -> list[TextNode]:
    start_index = index_matching(nodes, starts)
    if start_index is None:
        return []
    result: list[TextNode] = []
    for node in nodes[start_index + 1 :]:
        if matches_any(node.text, ends):
            break
        result.append(node)
    return result


def index_equal(nodes: list[TextNode], value: str) -> int | None:
    return index_matching(nodes, [value])


def index_matching(nodes: list[TextNode], values: list[str]) -> int | None:
    for index, node in enumerate(nodes):
        if matches_any(node.text, values):
            return index
    return None


def matches_any(text: str, values: list[str]) -> bool:
    key = normalized_heading(text)
    for value in values:
        expected = normalized_heading(value)
        if key == expected or key.startswith(f"{expected} "):
            return True
    return False


def normalized_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().rstrip(":")).lower()


def index_containing(nodes: list[TextNode], value: str) -> int | None:
    value = value.lower()
    for index, node in enumerate(nodes):
        if value in node.text.lower():
            return index
    return None


def find_specification_url(links: list[Link]) -> str | None:
    pdf_links = [link for link in links if ".pdf" in link.href.lower()]
    for link in pdf_links:
        combined = f"{link.text} {link.href}".lower()
        if "specification" in combined:
            return link.href
    for link in pdf_links:
        if "download here" in link.text.lower():
            return link.href
    return pdf_links[0].href if pdf_links else None


def audience_note(qualification_type: str) -> str:
    if qualification_type == "international_gcse":
        return (
            "OxfordAQA International GCSEs are designed for international students and "
            "schools following a British curriculum outside the UK. They are linear "
            "qualifications, so students normally take all exams in the same exam series "
            "at the end of the course. Availability can vary by region, school, and exam "
            "centre, so families should confirm local entry routes before relying on a study plan."
        )
    if qualification_type == "international_as_a_level":
        return (
            "OxfordAQA International AS-A-levels are modular international qualifications "
            "for international students in schools following a British curriculum outside the UK. "
            "Unit availability and entry routes should be confirmed locally."
        )
    return (
        "This is an OxfordAQA international qualification. Confirm the qualification type, "
        "local availability, and exam entry route with the school or centre."
    )


def attach_source_snippets(qualification: Qualification, pages: list[tuple[int, str]]) -> None:
    for topic in qualification.topics:
        if topic.source_snippets:
            topic.source_snippets = topic.source_snippets[:3]
            continue
        terms = [topic.title, *topic.points[:6]]
        topic.source_snippets = find_source_snippets(pages, terms, max_snippets=3)
    for paper in qualification.assessments:
        terms = [paper.title, *paper.details[:4]]
        paper.source_snippets = find_source_snippets(pages, terms, max_snippets=2)


def find_source_snippets(
    pages: list[tuple[int, str]],
    terms: list[str],
    max_snippets: int = 3,
) -> list[SourceSnippet]:
    snippets: list[SourceSnippet] = []
    used_pages: set[int] = set()
    searchable_pages = [
        (page_number, page_text)
        for page_number, page_text in pages
        if not is_likely_index_page(page_number, page_text)
    ]
    for raw_term in terms:
        term = raw_term.strip()
        if len(term) < 4:
            continue
        term_norm = normalize_for_search(term)
        for page_number, page_text in searchable_pages:
            if page_number in used_pages:
                continue
            page_norm = normalize_for_search(page_text)
            if term_norm not in page_norm:
                continue
            snippets.append(
                SourceSnippet(
                    page=page_number,
                    text=snippet_around(page_text, term),
                    matched_term=term,
                )
            )
            used_pages.add(page_number)
            break
        if len(snippets) >= max_snippets:
            break
    return snippets


def is_likely_index_page(page_number: int, page_text: str) -> bool:
    if page_number <= 3:
        return True
    text = normalize_for_search(page_text)
    syllabus_body_markers = (
        "content additional information",
        "students should",
        "students must",
    )
    if any(marker in text for marker in syllabus_body_markers):
        return False
    index_markers = (
        "contents",
        "specification at a glance",
        "scheme of assessment",
        "general administration",
    )
    return sum(marker in text for marker in index_markers) >= 2


def normalize_for_search(value: str) -> str:
    value = value.replace("\u2013", "-").replace("\u2014", "-")
    value = re.sub(r"\s+", " ", value)
    return value.lower().strip()


def snippet_around(page_text: str, term: str, radius: int = 420) -> str:
    text = clean_text(page_text)
    text_lower = text.lower()
    term_lower = clean_text(term).lower()
    index = text_lower.find(term_lower)
    if index < 0:
        return text[: radius * 2].strip()
    start = max(0, index - radius)
    end = min(len(text), index + len(term) + radius)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"
