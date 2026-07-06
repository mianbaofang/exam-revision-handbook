from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceSnippet, Topic

SYLLABUS_OUTLINE_FILE = "syllabus-outline.json"
SYLLABUS_EVIDENCE_FILE = "syllabus-evidence.json"
CONTRACT_VERSION = "v0.5-llm-syllabus-outline"

PLACEHOLDER_PATTERNS = [
    r"^topic\s+\d+$",
    r"^content\s+unit\s+\d+$",
    r"^unit\s+\d+$",
    r"^syllabus\s+point$",
    r"^learning\s+objective$",
]


@dataclass(frozen=True)
class SyllabusEvidencePage:
    page: int
    text: str


@dataclass(frozen=True)
class SyllabusEvidence:
    schema_version: str
    course: dict[str, object]
    pages: list[SyllabusEvidencePage] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "course": self.course,
            "pages": [asdict(page) for page in self.pages],
        }


@dataclass(frozen=True)
class SyllabusOutlineIssue:
    severity: str
    message: str


@dataclass(frozen=True)
class SyllabusOutlineResult:
    qualification: Qualification
    outline: dict[str, object]
    issues: list[SyllabusOutlineIssue]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def build_syllabus_evidence(
    qualification: Qualification,
    pages: list[tuple[int, str]] | None = None,
    *,
    max_chars_per_page: int = 5000,
) -> SyllabusEvidence:
    """Build page-level evidence for an LLM Analyst without deciding topics."""

    page_items = [
        SyllabusEvidencePage(page=page, text=" ".join(text.split())[:max_chars_per_page])
        for page, text in pages or []
        if text.strip()
    ]
    course: dict[str, object] = {
        "title": qualification.title,
        "code": qualification.code,
        "qualification_type": qualification.qualification_type,
        "subject_area": qualification.subject_area,
        "provider": qualification.provider or qualification.source.provider,
        "page_url": qualification.page_url,
        "specification_url": qualification.source.specification_url,
        "specification_sha256": qualification.source.specification_sha256,
        "selected_exam_year": qualification.selected_exam_year,
    }
    return SyllabusEvidence(
        schema_version=CONTRACT_VERSION,
        course=course,
        pages=page_items,
    )


def write_syllabus_evidence(
    qualification: Qualification,
    output_dir: Path,
    pages: list[tuple[int, str]] | None = None,
) -> Path:
    evidence = build_syllabus_evidence(qualification, pages)
    path = output_dir / SYLLABUS_EVIDENCE_FILE
    path.write_text(json.dumps(evidence.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_syllabus_outline_prompt(qualification: Qualification, evidence: SyllabusEvidence) -> str:
    """
    Build detailed prompt for the LLM Analyst to produce a source-driven outline.

    Python extracts evidence only. The Analyst decides the structure for the current
    specification, records that decision, and maps final teachable units to source
    coverage. Python validates self-consistency; it does not impose a provider or
    subject template.
    """
    payload = json.dumps(evidence.to_dict(), ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "=" * 80,
            "PHASE 1: SYLLABUS OUTLINE ANALYST",
            "=" * 80,
            "",
            "You are the syllabus_outline_analyst. Read the official specification evidence",
            "and produce a source-driven outline for a revision handbook.",
            "",
            "IMPORTANT: Python has not chosen the topic split. Python only extracted page text.",
            "You decide the structure from this specific syllabus. Do not follow a fixed",
            "exam-board, provider, subject, or topic-count template.",
            "",
            "INPUT:",
            "The following JSON contains:",
            "- course.title, course.code, course.qualification_type, course.subject_area",
            "- pages[]: array of {page: number, text: string} from the official PDF",
            "- specification_url, page_url",
            "",
            "WORKFLOW:",
            "",
            "1. Decide the source structure for this syllabus",
            "   - Read the evidence and state how this PDF organizes examinable content.",
            "   - The structure may be flat, nested, mixed, route-based, table-based, code-based,",
            "     objective-based, or another form visible in the PDF.",
            "   - Record that judgement in structure_analysis. If there are structural entries",
            "     such as parts, units, papers, components, routes, sections, or sub-sections,",
            "     list them in official_structure. If the source is genuinely flat, say so in",
            "     structure_analysis and official_structure may contain a single root or be empty.",
            "",
            "2. Extract source coverage items",
            "   - List the actual examinable content items that must be covered: rows, bullets,",
            "     coded syllabus points, skill statements, table cells, formula requirements,",
            "     restrictions, or application statements.",
            "   - Keep paired table text together when one row is clarified by another row or",
            "     an Additional information column.",
            "   - Do not merge unrelated source items just to make the outline shorter. Do not",
            "     split a single indivisible source item merely to reach a count.",
            "",
            "3. Split final teachable knowledge units",
            "   - topics[] is the final list consumed by the handbook writer. Each entry should",
            "     be one teachable knowledge unit or a tightly linked cluster justified by the",
            "     current syllabus evidence.",
            "   - A structural label can appear in parent_path, but a topic title should name",
            "     what the student learns, not only where it sits in the PDF.",
            "   - For each topic, include parent_path and source_coverage_ids so the Writer and",
            "     Reviewer can trace it back to your source coverage map.",
            "",
            "4. Extract exam points and source snippets",
            "   - exam_points should be specific source-bound claims, skills, formula uses,",
            "     restrictions, or applications.",
            "   - source_snippets should quote short evidence from the PDF with page numbers.",
            "   - Keep handbook content in English; glossary support is handled later.",
            "",
            "OUTPUT JSON SCHEMA:",
            "{",
            '  "schema_version": "v0.5-llm-syllabus-outline",',
            '  "status": "llm-analyst-approved",',
            '  "course_spec": {',
            '    "title": "Use course.title from the input evidence",',
            '    "code": "Use course.code from the input evidence",',
            '    "qualification_type": "Use course.qualification_type from the input evidence",',
            '    "subject_area": "Use course.subject_area from the input evidence",',
            '    "provider": "Use course.provider from the input evidence",',
            '    "page_url": "Use course.page_url from the input evidence",',
            '    "specification_url": "Use course.specification_url from the input evidence"',
            "  },",
            '  "structure_analysis": {',
            '    "model": "flat | nested | mixed | route-based | table-based | code-based | other",',
            '    "rationale": "Explain how this specific PDF organizes examinable content.",',
            '    "lowest_source_unit": "Rows, bullets, coded points, skill statements, or another source unit visible here."',
            "  },",
            '  "official_structure": [',
            "    {",
            '      "id": "STRUCTURE_ID_FROM_SOURCE",',
            '      "title": "A structural heading exactly as it appears in this PDF",',
            '      "role": "source-structure",',
            '      "parent_id": null,',
            '      "page_start": 10,',
            '      "page_end": 12',
            "    }",
            "  ],",
            '  "source_coverage": [',
            "    {",
            '      "id": "SC001",',
            '      "parent_path": ["Structural heading from this PDF", "Optional subsection from this PDF"],',
            '      "content": "One examinable source item from this PDF",',
            '      "additional_information": "Clarifying source text from the same row, bullet, or linked column",',
            '      "page": 12',
            "    }",
            "  ],",
            '  "topics": [',
            "    {",
            '      "title": "Teachable knowledge unit named from the source evidence",',
            '      "parent_path": ["Structural heading from this PDF", "Optional subsection from this PDF"],',
            '      "source_coverage_ids": ["SC001"],',
            '      "split_rationale": "One source row with its clarification forms one teachable unit.",',
            '      "exam_points": [',
            '        "Specific examinable claim or skill copied from this PDF",',
            '        "Second source-bound point only if it belongs in the same teachable unit"',
            "      ],",
            '      "level_tags": [],',
            '      "source_snippets": [',
            "        {",
            '          "page": 12,',
            '          "text": "Short quote from the source evidence",',
            '          "matched_term": "term or phrase matched in this PDF"',
            "        }",
            "      ]",
            "    }",
            "  ],",
            '  "coverage_notes": "Briefly explain any judgement calls, merged items, or ambiguous source structure."',
            "}",
            "",
            "CRITICAL RULES:",
            "",
            "1. Read the PDF evidence itself. Do not rely on candidate hints or Python guesses.",
            "",
            "2. Let this syllabus decide the structure. Do not require any preselected layers,",
            "   provider-specific labels, or minimum topic count.",
            "",
            "3. Do not collapse detailed examinable content into container headings. If you list",
            "   multiple source_coverage items under a container, topics[] must show how those",
            "   items are taught or tightly clustered.",
            "",
            "4. Do not invent board/subject information. If the evidence is unclear, output",
            "   an issues array explaining the uncertainty instead of guessing.",
            "",
            "AFTER YOU OUTPUT THIS JSON:",
            "- Python validates self-consistency: topics[] must map to source_coverage and",
            "  must not simply reuse structure entries as collapsed teaching units.",
            "- Python writes qualification.json from topics[] for the Writer.",
            "- The structure_analysis, official_structure, and source_coverage remain in",
            "  syllabus-outline.json for quality inspection and final review.",
            "- If invalid, Coordinator returns exact schema or evidence issues to you for repair.",
            "",
            "DELIVERY CHECKLIST:",
            "- structure_analysis explains how this exact PDF is organized.",
            "- source_coverage records the actual examinable items selected from the source.",
            "- topics[] contains final teachable knowledge units or justified tight clusters.",
            "- Every topic has exam_points, source_snippets, parent_path, and source_coverage_ids.",
            "- schema_version is v0.5-llm-syllabus-outline.",
            "",
            "HANDOFF NOTE TO COORDINATOR:",
            '"Syllabus outline approved with [X] teachable knowledge units mapped to [Y] source coverage items. Ready for Handbook Writer."',
            "",
            "=" * 80,
            "OFFICIAL EVIDENCE (read all pages):",
            "=" * 80,
            "",
            payload,
        ]
    )


def apply_syllabus_outline_response(
    qualification: Qualification,
    response: str | dict[str, object],
) -> SyllabusOutlineResult:
    data = _parse_outline_response(response)
    data_dict: dict[str, object] = data if isinstance(data, dict) else {}
    issues = validate_syllabus_outline(data_dict)
    if any(issue.severity == "error" for issue in issues):
        return SyllabusOutlineResult(qualification=qualification, outline=data_dict, issues=issues)

    topic_entries = _outline_topic_entries(data_dict)
    topics = [
        _topic_from_outline_entry(entry) for entry in topic_entries if isinstance(entry, dict)
    ]
    updated = Qualification(
        title=qualification.title,
        code=qualification.code,
        qualification_type=qualification.qualification_type,
        subject_area=qualification.subject_area,
        page_url=qualification.page_url,
        summary=qualification.summary,
        topics=topics,
        assessments=qualification.assessments,
        source=qualification.source,
        audience_note=qualification.audience_note,
        provider=qualification.provider,
        qualification_family=qualification.qualification_family,
        selected_exam_year=qualification.selected_exam_year,
        route_tags=[*qualification.route_tags, "outline-source:llm-analyst"],
        command_words=qualification.command_words,
        assessment_objectives=qualification.assessment_objectives,
    )
    data.setdefault("schema_version", CONTRACT_VERSION)
    return SyllabusOutlineResult(qualification=updated, outline=data, issues=issues)


def write_syllabus_outline(output_dir: Path, outline: dict[str, object]) -> Path:
    path = output_dir / SYLLABUS_OUTLINE_FILE
    path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def validate_syllabus_outline(data: dict[str, object]) -> list[SyllabusOutlineIssue]:
    issues: list[SyllabusOutlineIssue] = []
    topics = _outline_topic_entries(data)
    if not topics:
        issues.append(
            SyllabusOutlineIssue("error", "Analyst outline must include non-empty topics.")
        )
        return issues

    structure_analysis = data.get("structure_analysis")
    if not isinstance(structure_analysis, dict) or not str(
        structure_analysis.get("rationale") or ""
    ).strip():
        issues.append(
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must include structure_analysis.rationale explaining the structure found in this PDF.",
            )
        )

    coverage = data.get("source_coverage")
    coverage_items = [item for item in coverage if isinstance(item, dict)] if isinstance(coverage, list) else []
    if not coverage_items:
        issues.append(
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must include source_coverage items selected from the PDF evidence.",
            )
        )

    structure_titles = _official_structure_titles(data)
    coverage_ids = {str(item.get("id") or "").strip() for item in coverage_items}
    coverage_ids.discard("")
    for coverage_index, item in enumerate(coverage_items, start=1):
        if not str(item.get("id") or "").strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_coverage item {coverage_index} is missing a stable id."
                )
            )
    used_coverage_ids: set[str] = set()

    for index, topic in enumerate(topics, start=1):
        if not isinstance(topic, dict):
            issues.append(SyllabusOutlineIssue("error", f"Topic {index} must be an object."))
            continue
        title = str(topic.get("title") or "").strip()
        if not title:
            issues.append(SyllabusOutlineIssue("error", f"Topic {index} is missing a title."))
        if _is_placeholder(title):
            issues.append(
                SyllabusOutlineIssue("error", f"Topic {index} title is a placeholder: {title}")
            )
        points = topic.get("exam_points") or topic.get("points")
        if not isinstance(points, list) or not [point for point in points if str(point).strip()]:
            issues.append(SyllabusOutlineIssue("error", f"Topic {index} must include exam_points."))
        snippets = topic.get("source_snippets")
        if not isinstance(snippets, list) or not snippets:
            issues.append(
                SyllabusOutlineIssue("error", f"Topic {index} must include source_snippets.")
            )
        else:
            for snippet_index, snippet in enumerate(snippets, start=1):
                if not isinstance(snippet, dict):
                    issues.append(
                        SyllabusOutlineIssue(
                            "error", f"Topic {index} snippet {snippet_index} must be an object."
                        )
                    )
                    continue
                if not str(snippet.get("text") or "").strip():
                    issues.append(
                        SyllabusOutlineIssue(
                            "error", f"Topic {index} snippet {snippet_index} is missing text."
                        )
                    )
                try:
                    int(snippet.get("page", 0))
                except (TypeError, ValueError):
                    issues.append(
                        SyllabusOutlineIssue(
                            "error", f"Topic {index} snippet {snippet_index} has invalid page."
                        )
                    )
        raw_topic_coverage = topic.get("source_coverage_ids") or topic.get("coverage_ids")
        topic_coverage_ids = (
            [str(value).strip() for value in raw_topic_coverage if str(value).strip()]
            if isinstance(raw_topic_coverage, list)
            else []
        )
        if not topic_coverage_ids:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"Topic {index} must include source_coverage_ids from source_coverage."
                )
            )
        for coverage_id in topic_coverage_ids:
            used_coverage_ids.add(coverage_id)
            if coverage_items and coverage_id not in coverage_ids:
                issues.append(
                    SyllabusOutlineIssue(
                        "error",
                        f"Topic {index} references unknown source_coverage id: {coverage_id}",
                    )
                )
        if _collapses_declared_structure(title, topic_coverage_ids, structure_titles):
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"Topic {index} reuses a declared structure title while covering multiple source items: {title}",
                )
            )

    if coverage_ids:
        unused = sorted(coverage_ids - used_coverage_ids)
        if unused:
            preview = ", ".join(unused[:8])
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"source_coverage has {len(unused)} item(s) not mapped to topics: {preview}",
                )
            )
    return issues


def _parse_outline_response(response: str | dict[str, object]) -> dict[str, object]:
    if isinstance(response, dict):
        return response
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
        text = re.sub(r"```$", "", text).strip()
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Analyst outline response must be a JSON object.")
    return data


def _outline_topic_entries(data: dict[str, object]) -> list[object]:
    raw_topic_entries = data.get("topics")
    if isinstance(raw_topic_entries, list):
        return list(raw_topic_entries)
    raw_knowledge_points = data.get("knowledge_points")
    if isinstance(raw_knowledge_points, list):
        return list(raw_knowledge_points)
    return []


def _topic_from_outline_entry(entry: dict[str, object]) -> Topic:
    raw_points = entry.get("exam_points") or entry.get("points") or []
    points = (
        [str(point).strip() for point in raw_points if str(point).strip()]
        if isinstance(raw_points, list)
        else []
    )
    raw_tags = entry.get("level_tags") or []
    tags = (
        [str(tag).strip() for tag in raw_tags if str(tag).strip()]
        if isinstance(raw_tags, list)
        else []
    )
    snippets = []
    raw_snippets = entry.get("source_snippets") or []
    if isinstance(raw_snippets, list):
        for item in raw_snippets:
            if not isinstance(item, dict):
                continue
            snippets.append(
                SourceSnippet(
                    page=int(item.get("page") or 0),
                    text=str(item.get("text") or "").strip(),
                    matched_term=str(item.get("matched_term") or entry.get("title") or "").strip(),
                )
            )
    return Topic(
        title=str(entry.get("title") or "").strip(),
        points=points,
        level_tags=tags,
        source_snippets=snippets,
    )


def _is_placeholder(title: str) -> bool:
    normalized = " ".join(title.lower().split())
    return any(re.match(pattern, normalized) for pattern in PLACEHOLDER_PATTERNS)


def _official_structure_titles(data: dict[str, object]) -> set[str]:
    structure = data.get("official_structure")
    if not isinstance(structure, list):
        return set()
    titles: set[str] = set()
    for item in structure:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "")
        if not title.strip():
            continue
        titles.add(_normalize_text(title))
        titles.add(_normalize_structure_title(title))
    titles.discard("")
    return titles


def _collapses_declared_structure(
    title: str,
    coverage_ids: list[str],
    structure_titles: set[str],
) -> bool:
    if len(coverage_ids) <= 1:
        return False
    normalized_title = _normalize_text(title)
    structure_title = _normalize_structure_title(title)
    return normalized_title in structure_titles or structure_title in structure_titles


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _normalize_structure_title(value: str) -> str:
    text = _normalize_text(value)
    text = re.sub(
        r"^(?:section\s+|unit\s+|paper\s+|component\s+)?[a-z]*\d+(?:\.\d+)*[a-z]*\b\s*[:.\-–—)]?\s*",
        "",
        text,
    )
    return text.strip()
