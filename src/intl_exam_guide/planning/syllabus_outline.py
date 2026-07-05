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
    Build detailed prompt for LLM Analyst to read syllabus evidence and produce authoritative outline.

    This is Phase 1 of the three-phase workflow. The LLM must:
    1. Read all pages in the evidence
    2. Identify real teaching topics (not placeholder headings)
    3. Extract specific exam points for each topic
    4. Record source snippets with page numbers
    """
    payload = json.dumps(evidence.to_dict(), ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "=" * 80,
            "PHASE 1: SYLLABUS OUTLINE ANALYST",
            "=" * 80,
            "",
            "You are the syllabus_outline_analyst. Your task is to read the official specification",
            "PDF evidence and produce an authoritative topic outline for the revision handbook.",
            "",
            "IMPORTANT: Python has NOT decided the topics. Python only extracted page text.",
            "YOU must identify topic boundaries, exam points, and teaching structure.",
            "",
            "INPUT:",
            "The following JSON contains:",
            "- course.title, course.code, course.qualification_type, course.subject_area",
            "- pages[]: array of {page: number, text: string} from the official PDF",
            "- specification_url, page_url",
            "",
            "YOUR TASK:",
            "",
            "1. Read all pages carefully",
            "   - Look for topic headings (often numbered like '3.1.8' or with clear titles)",
            "   - Distinguish between section structure and actual teaching topics",
            "   - Note any foundation/extended or AS/A2 level distinctions",
            "",
            "2. Identify REAL teaching topics",
            "   - Good: '3.1.8 Prepare accounting records from source documents'",
            "   - Good: 'Ionic, covalent and metallic bonding'",
            "   - Bad: 'Content 1.1' (too generic)",
            "   - Bad: 'Unit A' (structural placeholder)",
            "   - If the PDF only has generic headings, infer the actual topics from the content",
            "",
            "3. Extract specific exam points for each topic",
            "   - Good: 'Use source documents, books of prime entry and ledger accounts'",
            "   - Good: 'Describe ionic bonding and explain properties of ionic compounds'",
            "   - Bad: 'Students should understand the content' (too vague)",
            "   - Bad: 'Cover the syllabus' (not specific)",
            "   - Aim for 2-8 exam points per topic",
            "",
            "4. Record source snippets",
            "   - For each topic, save 1-3 short text snippets showing where you found it",
            "   - Include the page number",
            "   - Include the matched_term (the heading/keyword you matched)",
            "",
            "5. Check for level tags",
            "   - If the syllabus distinguishes foundation/extended: add level_tags",
            "   - If the syllabus distinguishes AS/A2: add level_tags",
            "   - Otherwise leave level_tags empty",
            "",
            "OUTPUT JSON SCHEMA:",
            "{",
            '  "schema_version": "v0.5-llm-syllabus-outline",',
            '  "status": "llm-analyst-approved",',
            '  "course_spec": {',
            '    "title": "International GCSE Chemistry",',
            '    "code": "9202",',
            '    "qualification_type": "international_gcse",',
            '    "subject_area": "Chemistry",',
            '    "provider": "edexcel",',
            '    "page_url": "https://...",',
            '    "specification_url": "https://...pdf"',
            "  },",
            '  "topics": [',
            "    {",
            '      "title": "3.1.8 Prepare accounting records from source documents",',
            '      "exam_points": [',
            '        "Use source documents",',
            '        "Prepare books of prime entry",',
            '        "Prepare ledger accounts"',
            "      ],",
            '      "level_tags": ["foundation", "extended"],',
            '      "source_snippets": [',
            "        {",
            '          "page": 12,',
            '          "text": "Students should be able to use source documents...",',
            '          "matched_term": "source documents"',
            "        }",
            "      ]",
            "    }",
            "  ]",
            "}",
            "",
            "CRITICAL RULES:",
            "",
            "1. Do NOT rely on any *-candidate-hints.json files in the evidence.",
            "   Those are optional Python suggestions only. Read the PDF pages yourself.",
            "",
            "2. Do NOT accept 'Content 1.1' or 'Unit A' as teaching topics.",
            "   Find the actual topic names from the content.",
            "",
            "3. Do NOT output exam_points like 'Understand the topic' or 'Cover material'.",
            "   Be specific. Quote from the syllabus.",
            "",
            "4. Each topic MUST have:",
            "   - At least one exam_point",
            "   - At least one source_snippet with page number",
            "",
            "5. Do NOT invent board/subject information.",
            "   If the evidence is unclear, output an 'issues' array instead of guessing.",
            "",
            "6. Keep all handbook content in English.",
            "   (If user requested a term glossary in another language, that's handled in Phase 2)",
            "",
            "AFTER YOU OUTPUT THIS JSON:",
            "- Python will validate your JSON schema",
            "- Coordinator will check for placeholder topics and missing source snippets",
            "- Python will write qualification.json (authoritative topics)",
            "- Python will generate concept_jobs.json (your Phase 2 writing task list)",
            "- If valid, Coordinator hands the package to handbook_writer",
            "- If invalid, Coordinator returns exact schema or evidence issues to you for repair",
            "",
            "DELIVERY CHECKLIST:",
            "- All topics have real teaching titles, not 'Content 1.1' or 'Unit A'",
            "- Each topic has 2-8 specific exam_points unless the official syllabus is narrower",
            "- Each topic has at least one source_snippet with a page number",
            "- No topic title, exam point, or snippet is placeholder text",
            "- schema_version is v0.5-llm-syllabus-outline",
            "",
            "HANDOFF NOTE TO COORDINATOR:",
            '"Syllabus outline approved with [X] topics. Ready for Handbook Writer to generate teaching content."',
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

    raw_topic_entries = data_dict.get("topics")
    topic_entries: list[object] = (
        list(raw_topic_entries) if isinstance(raw_topic_entries, list) else []
    )
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
    topics = data.get("topics")
    if not isinstance(topics, list) or not topics:
        issues.append(
            SyllabusOutlineIssue("error", "Analyst outline must include non-empty topics.")
        )
        return issues
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
