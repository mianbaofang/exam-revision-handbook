from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

from intl_exam_guide import __version__
from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceSnippet,
    Topic,
)
from intl_exam_guide.parsing.markdown_companion import write_markdown_companion
from intl_exam_guide.parsing.pdf_text import extract_pdf_pages, extract_pdf_text
from intl_exam_guide.providers.base import Link


USER_AGENT = (
    f"exam-revision-handbook/{__version__} "
    "(+https://github.com/mianbaofang/exam-revision-handbook) source-traceable"
)


@dataclass
class TextNode:
    tag: str
    text: str


class BasicPageParser(HTMLParser):
    """Small static HTML parser for provider subject and specification pages."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.stack: list[str] = []
        self.nodes: list[TextNode] = []
        self.links: list[Link] = []
        self.title: str | None = None
        self._title_parts: list[str] | None = None
        self._link_href: str | None = None
        self._link_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        attr_map = dict(attrs)
        if tag == "title":
            self._title_parts = []
        if tag == "a":
            href = attr_map.get("href")
            if href:
                self._link_href = urllib.parse.urljoin(self.base_url, href)
                self._link_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._title_parts is not None:
            self.title = clean_text(" ".join(self._title_parts)) or self.title
            self._title_parts = None
        if tag == "a" and self._link_href:
            text = clean_text(" ".join(self._link_parts)) or self._link_href.rsplit("/", 1)[-1]
            self.links.append(Link(text=text, href=self._link_href))
            self._link_href = None
            self._link_parts = []
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        tag = self.stack[-1] if self.stack else ""
        self.nodes.append(TextNode(tag=tag, text=text))
        if self._title_parts is not None:
            self._title_parts.append(text)
        if self._link_href:
            self._link_parts.append(text)


def fetch_bytes(url: str, timeout: int = 45) -> bytes:
    url = safe_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 45) -> str:
    data = fetch_bytes(url, timeout=timeout)
    return data.decode("utf-8", errors="replace")


def parse_page(url: str) -> BasicPageParser:
    parser = BasicPageParser(base_url=url)
    parser.feed(fetch_text(url))
    return parser


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("\u2013", "-").replace("\u2014", "-")
    value = normalize_extracted_symbols(value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_extracted_symbols(value: str | None) -> str:
    if not value:
        return ""
    if "A \u222a B, A \u222a B" in value and any(
        marker in value for marker in ("n(A)", "A\u2032", "\u03be", "intersection")
    ):
        return value.replace("A \u222a B, A \u222a B", "A \u222a B, A \u2229 B")
    return value


def safe_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parsed.path, safe="/:%")
    query = urllib.parse.quote(parsed.query, safe="=&?/%:+,")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, query, parsed.fragment))


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def is_pdf_url(value: str) -> bool:
    return ".pdf" in urllib.parse.urlparse(value).path.lower()


def first_node_text(source: object, *tags: str) -> str | None:
    nodes = getattr(source, "nodes", source)
    if not isinstance(nodes, Iterable):
        return None
    for node in nodes:
        if isinstance(node, TextNode) and node.tag in tags:
            return node.text
    return None


def code_from_text(value: str) -> str | None:
    match = re.search(r"\((\d{4})\)|\b(\d{4})\b", value)
    if match:
        return match.group(1) or match.group(2)
    return None


def title_from_url(url: str) -> str:
    slug = Path(urllib.parse.urlparse(url).path).stem
    slug = re.sub(r"\b(pdf|spec|specification|syllabus)\b", "", slug, flags=re.I)
    return clean_text(slug.replace("-", " ").replace("_", " ")).title() or url


def normalize_level(level: str | None) -> str | None:
    if not level:
        return None
    return level.lower().replace("_", "-").strip()


def subject_terms_from_query(query: str) -> list[str]:
    text = query.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\b20\d{2}\b", " ", text)
    text = re.sub(
        r"\b(oxfordaqa|oxford|aqa|pearson|edexcel|cambridge|caie|cie|international|gcse|igcse|as|a|level|a-level|alevel|ial|syllabus|specification|spec|pdf|guide|revision|handbook)\b",
        " ",
        text,
    )
    terms = re.findall(r"[a-z0-9]+", text)
    return [term for term in terms if len(term) > 1 and not re.fullmatch(r"\d{4}", term)]


def subject_slug_from_query(query: str) -> str:
    return "-".join(subject_terms_from_query(query))


def format_candidate_choices(provider_label: str, query: str, candidates: list[Link]) -> str:
    lines = [
        f"{provider_label} found multiple official candidates for {query!r}, so it cannot choose safely.",
        "Reply with one exact URL/code from the list below:",
    ]
    for index, link in enumerate(candidates, start=1):
        code = code_from_text(link.text) or code_from_text(link.href) or "no-code"
        qtype = link.qualification_type or "unknown-level"
        lines.append(f"{index}. {link.text} [{code}, {qtype}] - {link.href}")
    return "\n".join(lines)


def dedupe_links(links: list[Link]) -> list[Link]:
    seen: set[str] = set()
    result: list[Link] = []
    for link in links:
        key = link.href.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(link)
    return result


def infer_qualification_type(text: str, url: str = "", level: str | None = None) -> str:
    combined = f"{text} {url} {level or ''}".lower()
    if "international-advanced-level" in combined or "international advanced level" in combined:
        return "international_as_a_level"
    if "as & a level" in combined or "as and a level" in combined:
        return "international_as_a_level"
    if "a-level" in combined or "a level" in combined or "ial" in combined:
        return "international_as_a_level"
    if "international-gcse" in combined or "international gcse" in combined:
        return "international_gcse"
    if "igcse" in combined or normalize_level(level) in {"gcse", "igcse", "international-gcse"}:
        return "international_gcse"
    return "unknown"


def qualification_family(provider: str, qtype: str) -> str:
    if provider == "pearson":
        return (
            "Pearson Edexcel International AS/A Level"
            if qtype == "international_as_a_level"
            else "Pearson Edexcel International GCSE"
        )
    if provider == "cambridge":
        return (
            "Cambridge International AS & A Level"
            if qtype == "international_as_a_level"
            else "Cambridge IGCSE"
        )
    if provider == "collegeboard":
        return "College Board Advanced Placement (AP)"
    return provider


def find_pdf_link(
    parser: BasicPageParser,
    include_terms: tuple[str, ...],
    exclude_terms: tuple[str, ...] = (),
) -> str | None:
    candidates: list[tuple[int, str]] = []
    for link in parser.links:
        combined = f"{link.text} {link.href}".lower()
        if ".pdf" not in combined:
            continue
        if exclude_terms and any(term in combined for term in exclude_terms):
            continue
        score = sum(10 for term in include_terms if term in combined)
        if "download" in combined:
            score += 2
        if score:
            candidates.append((score, link.href))
    if candidates:
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]
    for link in parser.links:
        if ".pdf" in link.href.lower():
            return link.href
    return None


def first_teaching_from_nodes(nodes: list[TextNode]) -> str | None:
    return first_value_after_label(nodes, "First teaching")


def first_assessment_from_nodes(nodes: list[TextNode]) -> str | None:
    return first_value_after_label(nodes, "First external assessment") or first_value_after_label(
        nodes, "First assessment"
    )


def first_value_after_label(nodes: list[TextNode], label: str) -> str | None:
    label_lower = label.lower()
    for index, node in enumerate(nodes):
        text = node.text
        lower = text.lower()
        if label_lower not in lower:
            continue
        inline = text.split(":", 1)[1].strip() if ":" in text else ""
        if inline:
            return inline
        for next_node in nodes[index + 1 : index + 4]:
            if next_node.text and ":" not in next_node.text:
                return next_node.text
    return None


def attach_pdf_content(
    qualification: Qualification,
    output_dir: Path,
    pdf_url: str,
    provider_prefix: str,
    exam_year: str | None = None,
    filename_label: str | None = None,
) -> Qualification:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_bytes = fetch_bytes(pdf_url)
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    code = filename_label or qualification.code or provider_prefix
    pdf_path = output_dir / f"{provider_prefix}-{code}-specification.pdf"
    text_path = output_dir / f"{provider_prefix}-{code}-specification.txt"
    pdf_path.write_bytes(pdf_bytes)

    pages = extract_pdf_pages(pdf_path)
    text_path.write_text(extract_pdf_text(pdf_path), encoding="utf-8")
    write_markdown_companion(pdf_path, source_pdf_sha256=digest, output_dir=output_dir)

    # Write candidate hints (page text only, no topic parsing)
    # These are optional reference hints for the LLM Analyst.
    # The LLM must read the evidence and decide topics itself.
    hints_path = output_dir / f"{provider_prefix}-{code}-syllabus-candidate-hints.json"
    hints_path.write_text(
        json.dumps(
            {
                "schema_version": "v0.5-evidence-hints",
                "status": "evidence-only",
                "note": "Python extracted page text only. The LLM syllabus_outline_analyst must read the official evidence and decide topic boundaries.",
                "pages": [
                    {"page": page_num, "text": text[:5000]} for page_num, text in pages[:100]
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    assessments = parse_assessments_from_pdf(pages)
    if assessments:
        qualification.assessments = assessments
    qualification.command_words = parse_command_words_from_pdf(pages)
    qualification.assessment_objectives = parse_assessment_objectives_from_pdf(pages)

    qualification.source.specification_url = pdf_url
    qualification.source.specification_sha256 = digest
    qualification.source.specification_path = str(pdf_path)
    qualification.source.extracted_text_path = str(text_path)
    qualification.source.downloaded_at = datetime.now(UTC).isoformat()
    if exam_year and not qualification.selected_exam_year:
        qualification.selected_exam_year = exam_year
        qualification.source.selected_exam_year = exam_year
    return qualification


def parse_generic_topics_from_pdf(pages: list[tuple[int, str]]) -> list[Topic]:
    """
    DEPRECATED: Python no longer attempts to parse topics automatically.

    The LLM syllabus_outline_analyst must read syllabus-evidence.json and decide
    topic boundaries. This function now returns empty list.

    Use build_syllabus_evidence() + write_syllabus_evidence() instead.
    """
    return []


def parse_pearson_topic_tables(pages: list[tuple[int, str]]) -> list[Topic]:
    """DEPRECATED: See parse_generic_topics_from_pdf"""
    return []


def parse_pearson_subsection_line(line: str) -> tuple[str, str, str | None] | None:
    match = re.match(r"^(\d{1,2})\s+(.+)$", line)
    if not match:
        return None
    rest = clean_text(match.group(2))
    if not rest or re.fullmatch(r"\d+", rest):
        return None
    objective = re.search(r"\b([a-z]\)\s+.+)$", rest)
    if objective:
        title = clean_text(rest[: objective.start()])
        point = clean_text(objective.group(1))
    else:
        title = rest
        point = None
    if not title or len(title) > 90:
        return None
    return match.group(1), title, point


def is_pearson_title_continuation(line: str) -> bool:
    if re.match(r"^[a-z]\)\s+", line, re.I):
        return False
    lower = line.lower()
    if lower.startswith(("topic ", "paper ", "assessment ", "section ")):
        return False
    return 2 <= len(line) <= 45


def is_pearson_front_matter_line(line: str) -> bool:
    lower = line.lower()
    return (
        lower.startswith("specification - issue")
        or "pearson education limited" in lower
        or "world-class qualification" in lower
        or lower.startswith("we have guided pearson")
        or lower.startswith("chief education advisor")
    )


def select_content_pages(pages: list[tuple[int, str]]) -> list[tuple[int, str]]:
    detailed_start = first_detailed_topic_page(pages)
    if detailed_start is not None:
        detailed_selected: list[tuple[int, str]] = []
        for page_number, page_text in pages:
            if page_number < detailed_start:
                continue
            page_lower = page_text.lower()
            if page_number > detailed_start and re.search(
                r"\b(details of (?:the )?assessment|assessment information|scheme of assessment|appendix|appendices|command words|what else you need to know)\b",
                page_lower,
            ):
                break
            lines = [clean_text(line) for line in page_text.splitlines() if clean_text(line)]
            detailed_selected.append((page_number, "\n".join(lines)))
        return detailed_selected

    selected: list[tuple[int, str]] = []
    started = False
    for page_number, page_text in pages:
        lines = [clean_text(line) for line in page_text.splitlines() if clean_text(line)]
        page_lower = "\n".join(lines).lower()
        if (
            not started
            and page_number > 3
            and re.search(
                r"\b(subject content|syllabus content|course content|content guidance|detailed content)\b",
                page_lower,
            )
        ):
            started = True
        if not started:
            continue
        if selected and re.search(
            r"\b(details of (?:the )?assessment|assessment overview|assessment information|scheme of assessment|appendix|appendices|command words|what else you need to know)\b",
            page_lower,
        ):
            break
        selected.append((page_number, "\n".join(lines)))
    return selected


def first_detailed_topic_page(pages: list[tuple[int, str]]) -> int | None:
    for page_number, page_text in pages:
        if page_number <= 4:
            continue
        lower = page_text.lower()
        if "contents" in lower and "assessment information" in lower:
            continue
        if "content overview" in lower and "subject content" not in lower:
            continue
        if "syllabus overview" in lower and "subject content" not in lower:
            continue
        for raw_line in page_text.splitlines():
            line = clean_topic_line(raw_line)
            code = parse_standalone_topic_code(line)
            heading = parse_topic_heading(line)
            if code and "." in code:
                return page_number
            if heading and "." in heading[0]:
                return page_number
    return None


def parse_numbered_topics(pages: list[tuple[int, str]]) -> list[Topic]:
    """DEPRECATED: See parse_generic_topics_from_pdf"""
    return []


def parse_topic_heading(line: str) -> tuple[str, str] | None:
    line = re.sub(r"\s+\.{2,}\s*\d+$", "", line).strip()
    line = re.sub(r"\s+\d{1,3}$", "", line).strip()
    match = re.match(
        r"^((?:\d+\.){1,4}\d+|[A-Z]{1,3}\d{1,3}[A-Z]?|FP\d|P\d|M\d|S\d)\s+(.{3,120})$",
        line,
    )
    if not match:
        return None
    code = match.group(1).rstrip(".")
    if code.upper().startswith("AO"):
        return None
    title = clean_text(match.group(2)).strip(":- ")
    if not title or len(title) < 3:
        return None
    if title.lower().startswith(("page ", "back to contents", "www.", "cambridge ", "pearson ")):
        return None
    return code, title


def parse_standalone_topic_code(line: str) -> str | None:
    line = line.strip().rstrip(".")
    if re.fullmatch(r"\d+(?:\.\d+){1,4}", line):
        return line
    if re.fullmatch(r"[A-Z]{1,3}\d{1,3}[A-Z]?|FP\d|P\d|M\d|S\d", line):
        if line.upper().startswith("AO"):
            return None
        return line
    return None


def is_standalone_topic_title(line: str) -> bool:
    if not is_topic_point(line):
        return False
    lower = line.lower()
    if lower.startswith(("students should", "candidates should", "content ", "notes ")):
        return False
    if len(line) > 90:
        return False
    return True


def parse_content_overview_topics(pages: list[tuple[int, str]]) -> list[Topic]:
    """DEPRECATED: See parse_generic_topics_from_pdf"""
    return []


def parse_humanities_topics(pages: list[tuple[int, str]]) -> list[Topic]:
    """DEPRECATED: See parse_generic_topics_from_pdf"""
    return []


def parse_humanities_heading(line: str) -> tuple[str, str] | None:
    cleaned = re.sub(r"\s+\.{2,}\s*\d+$", "", line).strip()
    cleaned = re.sub(r"\s+\d{1,3}$", "", cleaned).strip()
    option_match = re.match(r"^([A-Z]\d{1,2})\s+(.{6,150})$", cleaned)
    if option_match and not option_match.group(1).upper().startswith("AO"):
        title = clean_text(option_match.group(2)).strip(":- ")
        if is_humanities_option_title(title):
            return option_match.group(1), title
    question_match = re.match(r"^(\d{1,2})\s+(.{10,150}\?)$", cleaned)
    if question_match:
        title = clean_text(question_match.group(2)).strip(":- ")
        if is_humanities_question_title(title):
            return question_match.group(1), title
    return None


def is_humanities_option_title(title: str) -> bool:
    lower = title.lower()
    if lower.startswith(("paper ", "assessment ", "content overview", "students must study")):
        return False
    return len(title.split()) >= 3


def is_humanities_question_title(title: str) -> bool:
    lower = title.lower()
    if lower.startswith(
        (
            "paper ",
            "assessment ",
            "content overview",
            "students must study",
            "why choose this syllabus",
        )
    ):
        return False
    if title.endswith("?") and re.match(
        r"^(?:why|how|what|were|was|did|to what extent|who)\b", lower
    ):
        return True
    return any(
        marker in lower
        for marker in (
            "war",
            "revolution",
            "reform",
            "origins",
            "relations",
            "control",
            "conflict",
            "peace",
            "depth",
            "world",
            "china",
            "russia",
            "germany",
            "usa",
            "britain",
            "important",
            "responsible",
            "successful",
            "cause",
            "impact",
            "diversity",
        )
    )


def is_humanities_topic_point(line: str) -> bool:
    if not is_topic_point(line):
        return False
    lower = line.lower()
    if lower.startswith(
        ("ao1", "ao2", "ao3", "paper ", "component ", "students must study", "students will")
    ):
        return False
    return not any(
        marker in lower
        for marker in (
            "assessment objective",
            "candidates answer",
            "externally assessed",
            "marks",
            "minutes",
            "written paper",
        )
    )


def chunk_informative_lines(pages: list[tuple[int, str]]) -> list[Topic]:
    """DEPRECATED: See parse_generic_topics_from_pdf"""
    return []


def parse_assessments_from_pdf(pages: list[tuple[int, str]]) -> list[AssessmentPaper]:
    papers: list[AssessmentPaper] = []
    seen: set[str] = set()
    for page_number, page_text in pages:
        lower = page_text.lower()
        if not re.search(
            r"\b(paper|unit|component)\s+\d|^[a-z]{1,3}\d\.\d\s+assessment information", lower, re.M
        ):
            continue
        lines = [clean_text(line) for line in page_text.splitlines() if clean_text(line)]
        for index, line in enumerate(lines):
            unit_match = re.match(r"^([A-Z]{1,3}\d)\.\d\s+Assessment information\b", line)
            if unit_match:
                unit_code = unit_match.group(1)
                title = f"Unit {unit_code}: Assessment information"
                normalized = title.lower()
                if normalized in seen:
                    continue
                seen.add(normalized)
                context = lines[index : index + 12]
                details = dedupe([item for item in context if is_assessment_detail(item)])[:8]
                papers.append(
                    AssessmentPaper(
                        title=title,
                        details=details or [line],
                        source_snippets=[
                            SourceSnippet(
                                page=page_number,
                                text=clean_text(" ".join(context))[:900],
                                matched_term=title,
                            )
                        ],
                        code=unit_code,
                        duration=extract_first(
                            r"\b\d+\s*(?:hours?|minutes)(?:\s+(?:and\s+)?\d+\s*minutes)?\b", context
                        ),
                        marks=extract_first(r"\b\d+\s*marks?\b", context),
                        weighting=extract_first(r"\b\d+(?:\.\d+)?%", context),
                        route_tags=route_tags_from_context(context),
                    )
                )
                continue
            for title in paper_titles_from_line(line):
                normalized = title.lower()
                if normalized in seen:
                    continue
                seen.add(normalized)
                context = lines[index : index + 7]
                details = dedupe([item for item in context if is_assessment_detail(item)])[:8]
                paper = AssessmentPaper(
                    title=title,
                    details=details or [line],
                    source_snippets=[
                        SourceSnippet(
                            page=page_number,
                            text=clean_text(" ".join(context))[:900],
                            matched_term=title,
                        )
                    ],
                    code=extract_component_code(" ".join(context)),
                    duration=extract_first(
                        r"\b\d+\s*(?:hours?|minutes)(?:\s+(?:and\s+)?\d+\s*minutes)?\b", context
                    ),
                    marks=extract_first(r"\b\d+\s*marks?\b", context),
                    weighting=extract_first(r"\b\d+(?:\.\d+)?%", context),
                    route_tags=route_tags_from_context(context),
                )
                papers.append(paper)
    return papers[:16]


def paper_titles_from_line(line: str) -> list[str]:
    pattern = re.compile(
        r"\b(?:Paper|Unit|Component)\s+\d+[A-Z]?(?::\s*.*?|\s+-\s*.*?|\s+.*?)(?=\s+(?:Paper|Unit|Component)\s+\d|$)",
        re.I,
    )
    titles = []
    for match in pattern.finditer(line):
        title = clean_text(match.group(0)).strip(" .")
        title = re.sub(r"\s{2,}", " ", title)
        title = re.sub(
            r"\b(?:\d+\s*marks?|\d+(?:\.\d+)?%|\d+\s*(?:hour|hours|minutes)).*$",
            "",
            title,
            flags=re.I,
        ).strip(" -:")
        if len(title) >= 7:
            titles.append(title[:120])
    return titles


def parse_command_words_from_pdf(pages: list[tuple[int, str]]) -> list[str]:
    words: list[str] = []
    in_section = False
    for _, page_text in pages:
        for raw_line in page_text.splitlines():
            line = clean_text(raw_line)
            lower = line.lower()
            if "command words" in lower:
                in_section = True
                continue
            if in_section and re.match(r"^\d+\s+", line):
                break
            if in_section:
                match = re.match(r"^([A-Z][A-Za-z ]{2,28})\s+[-:]", line)
                if match:
                    words.append(match.group(1).strip())
                elif re.fullmatch(r"[A-Z][a-z]{3,18}", line):
                    words.append(line)
    return dedupe(words)[:24]


def parse_assessment_objectives_from_pdf(pages: list[tuple[int, str]]) -> list[str]:
    objectives: list[str] = []
    for page_number, page_text in pages:
        if "assessment objective" not in page_text.lower() and "ao1" not in page_text.lower():
            continue
        for raw_line in page_text.splitlines():
            line = clean_text(raw_line)
            match = re.match(r"^(AO\d)\s+(.{3,120})", line)
            if match:
                objectives.append(f"{match.group(1)} {match.group(2)}")
        if objectives:
            break
    return dedupe(objectives)[:12]


def clean_topic_line(line: str) -> str:
    line = clean_text(line)
    line = line.strip("\u2022*- ")
    return clean_text(line)


def is_topic_point(line: str) -> bool:
    if len(line) < 6 or is_noise_line(line):
        return False
    if parse_topic_heading(line):
        return False
    lower = line.lower()
    if re.match(
        r"^\d+\s+(details of the assessment|assessment information|appendix|appendices|command words)\b",
        lower,
    ):
        return False
    bad_prefixes = (
        "back to contents",
        "content additional information",
        "content guidance",
        "details of the assessment",
        "students should be able to",
        "students will",
        "candidates should be able to",
        "candidates should have an understanding of",
        "www.",
        "copyright",
        "pearson edexcel",
        "cambridge international",
        "version ",
    )
    return not lower.startswith(bad_prefixes)


def is_noise_line(line: str) -> bool:
    lower = line.lower().strip()
    if not lower or re.fullmatch(r"\d+", lower):
        return True
    if lower in {"content", "subject content", "syllabus overview", "contents"}:
        return True
    return lower.startswith(("©", "page ", "back to contents page"))


def is_admin_heading(title: str) -> bool:
    lower = title.lower()
    return lower in {"subject content", "syllabus content", "content"} or lower.startswith(
        (
            "why choose",
            "assessment overview",
            "assessment objectives",
            "assessment information",
            "details of assessment",
            "details of the assessment",
            "what else you need to know",
        )
    )


def is_assessment_detail(line: str) -> bool:
    lower = line.lower()
    return bool(
        re.search(
            r"\b(hour|minute|marks?|externally assessed|written|multiple-choice|structured|practical|calculator|non-calculator|coursework|assessment|questions?)\b|\d+(?:\.\d+)?%",
            lower,
        )
    )


def extract_component_code(context: str) -> str | None:
    match = re.search(r"\b[A-Z]{1,5}\d{1,4}/\d{2}\b", context)
    return match.group(0) if match else None


def extract_first(pattern: str, context: list[str]) -> str | None:
    text = " ".join(context)
    match = re.search(pattern, text, re.I)
    return match.group(0) if match else None


def route_tags_from_context(context: list[str]) -> list[str]:
    text = " ".join(context).lower()
    tags = []
    for label in ["Core", "Extended", "Foundation", "Higher", "AS", "A2", "Modular", "Linear"]:
        if label.lower() in text:
            tags.append(label)
    return tags


def concise_title(line: str) -> str:
    title = re.split(r"[.;:]", line, maxsplit=1)[0].strip()
    return title[:80] or "Specification point"


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = clean_text(value)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def dedupe_topics(topics: list[Topic]) -> list[Topic]:
    seen: set[str] = set()
    result: list[Topic] = []
    for topic in topics:
        key = topic.title.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(topic)
    return result
