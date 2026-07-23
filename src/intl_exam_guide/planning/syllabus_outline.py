from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceSnippet, Topic

SYLLABUS_OUTLINE_FILE = "syllabus-outline.json"
SYLLABUS_EVIDENCE_FILE = "syllabus-evidence.json"
CONTRACT_VERSION = "v0.5-llm-syllabus-outline"
ATOMIC_COVERAGE_CONTRACT = "atomic-examinable-point-v1"
ALLOWED_SOURCE_KINDS = {
    "coded_point",
    "bullet",
    "sub_bullet",
    "table_row",
    "skill_statement",
    "formula_requirement",
    "restriction",
    "application_statement",
    "prose_clause",
    "single_requirement",
    "knowledge_statement",
    "conceptual_relationship",
    "practical_requirement",
    "data_handling_requirement",
    "source_analysis_requirement",
    "extended_response_requirement",
    "language_requirement",
    "portfolio_requirement",
    "other_source_bound_requirement",
}
ALLOWED_CONTAINER_DETAIL_MODELS = {
    "single_examinable_point",
    "multiple_examinable_points",
    "no_examinable_content",
}
ALLOWED_CLUSTER_RELATIONSHIPS = {
    "same_concept",
    "prerequisite_chain",
    "jointly_assessed_procedure",
    "definition_and_application",
    "other_source_justified",
}

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


def build_syllabus_outline_prompt(
    qualification: Qualification,
    evidence: SyllabusEvidence,
    markdown_text: str | None = None,
    markdown_extraction: dict[str, object] | None = None,
) -> str:
    """
    Build detailed prompt for the LLM Analyst to produce a source-driven outline.

    Python extracts evidence only. The Analyst decides the structure for the current
    specification, records that decision, and maps final teachable units to source
    coverage. Python validates self-consistency; it does not impose a provider or
    subject template.
    """
    payload = json.dumps(evidence.to_dict(), ensure_ascii=False, indent=2)
    markdown_report = json.dumps(markdown_extraction or {}, ensure_ascii=False, indent=2)
    markdown_payload = markdown_text or "[source/specification.md was not available to this prompt]"
    return "\n".join(
        [
            "=" * 80,
            "PHASE 1: SYLLABUS OUTLINE ANALYST",
            "=" * 80,
            "",
            "You are the syllabus_outline_analyst. Read the official specification Markdown companion",
            "and the page-level PDF evidence, then produce a source-driven outline for a revision handbook.",
            "",
            "IMPORTANT: Python has not chosen the topic split. Python only extracted page text and",
            "converted the official PDF to Markdown for your reading. You decide the structure from",
            "this specific syllabus. Do not follow a fixed exam-board, provider, subject, or topic-count template.",
            "",
            "MANDATORY INPUTS:",
            "- source/specification.md: MarkItDown Markdown companion for reading headings, tables, bullets, and boundaries.",
            "- source/markdown-extraction.json: conversion status and warnings; PDF-to-Markdown can lose formula fidelity.",
            "- syllabus-evidence.json: page-level evidence from the official PDF; this is the source truth for pages and snippets.",
            "",
            "Use Markdown to identify official document structure, heading levels, table membership, bullet ownership,",
            "and content/assessment/appendix boundaries. Use page-level evidence to verify page numbers, source snippets,",
            "and coverage. If Markdown and page-level evidence conflict, page-level evidence wins.",
            "",
            "Python must not parse Markdown to split topics. Topic splitting, merging, structure judgement, and",
            "source coverage decisions are your Analyst responsibility and must be written explicitly in syllabus-outline.json.",
            "",
            "WORKFLOW:",
            "",
            "1. Decide the source structure for this syllabus",
            "   - Read source/specification.md and syllabus-evidence.json together, then state how this PDF organizes examinable content.",
            "   - The structure may be flat, nested, mixed, route-based, table-based, code-based,",
            "     objective-based, or another form visible in the PDF.",
            "   - Record that judgement in structure_analysis. If there are structural entries",
            "     such as parts, units, papers, components, routes, sections, or sub-sections,",
            "     list them in official_structure. If the source is genuinely flat, say so in",
            "     structure_analysis and official_structure may contain a single root or be empty.",
            "",
            "2. Extract source coverage items",
            "   - Treat every official Topic, Unit, Section, chapter, or table heading as a",
            "     structural container by default, not as a final teaching topic. Descend below",
            "     it until you reach the lowest independently teachable or assessable statements.",
            "   - List the actual examinable content items that must be covered: rows, bullets,",
            "     coded syllabus points, skill statements, table cells, formula requirements,",
            "     restrictions, or application statements.",
            "   - Keep paired table text together when one row is clarified by another row or",
            "     an Additional information column.",
            "   - Do not merge unrelated source items just to make the outline shorter. Do not",
            "     split a single indivisible source item merely to reach a count.",
            "   - Split when the source contains distinct command-verb/object pairs, bullets,",
            "     sub-bullets, coded points, formulas, conditions, exceptions, applications,",
            "     or separately assessable procedures, even when they share one Topic heading.",
            "   - This rule is provider-, qualification-, and subject-independent. A lowest",
            "     requirement may be knowledge, a concept or relationship, calculation,",
            "     practical work, source/data analysis, extended writing, language performance,",
            "     portfolio evidence, or another source-bound assessable demand.",
            "   - Do not require a command verb when this source expresses examinable content",
            "     as a knowledge statement, theme, text, practical outcome, or assessment",
            "     objective. Do not use a fixed vocabulary or fixed number of items per container.",
            "",
            "2A. Prove that you reached source-detail depth",
            "   - Set coverage_granularity.contract to atomic-examinable-point-v1.",
            "   - For every lowest official container, write one container_audit entry and",
            "     classify it as single_examinable_point, multiple_examinable_points, or",
            "     no_examinable_content. Cite a page and short evidence excerpt.",
            "   - multiple_examinable_points requires at least two source_coverage_ids.",
            "   - single_examinable_point requires a source-based explanation of why no deeper",
            "     split exists. A short heading, shared theme, or LLM preference is not proof.",
            "   - Every source_coverage item must record source_kind, exam_action, and",
            "     atomicity='atomic'. A structural heading is not an allowed source_kind.",
            "",
            "3. Audit teaching granularity for every source item",
            "   - For each source_coverage item, decide how it will be treated:",
            "     independent_topic, merged_into_topic, prerequisite, or sub_skill.",
            "   - If a source item is merged, name the target topic and explain why the",
            "     items belong together for teaching. Do not merge merely because they share",
            "     a container heading.",
            "   - The handbook table of contents must let the Reviewer trace each official",
            "     source item to a visible topic, sub-skill, explanation, example, or practice.",
            "",
            "4. Split final teachable knowledge units",
            "   - topics[] is the final list consumed by the handbook writer. Each entry should",
            "     be one teachable knowledge unit or a tightly linked cluster justified by the",
            "     current syllabus evidence.",
            "   - Use a split-first rule: each final topic maps at least one independently",
            "     assessable source item. A tightly linked topic may map several independent",
            "     items when the audit explains why separate teaching would be misleading",
            "     and records visible treatment for every item. Do not force micro-topics.",
            "   - If a topic maps multiple source items, add cluster_justification with a",
            "     relationship and a source-based why_not_separate explanation.",
            "   - A structural label can appear in parent_path, but a topic title should name",
            "     what the student learns, not only where it sits in the PDF.",
            "   - For each topic, include parent_path and source_coverage_ids so the Writer and",
            "     Reviewer can trace it back to your source coverage map.",
            "   - Do not compress a course into a small number of directory-level themes for",
            "     speed. Do not make source_coverage one item per broad Topic merely because",
            "     the PDF uses Topic headings. Before delivery, compare each container audit",
            "     with the actual rows, bullets, clauses, codes, and requirements beneath it.",
            "",
            "5. Extract exam points and source snippets",
            "   - exam_points should be specific source-bound claims, skills, formula uses,",
            "     restrictions, or applications.",
            "   - source_snippets should quote short evidence from the PDF with page numbers.",
            "   - Keep handbook content in English; glossary support is handled later.",
            "",
            "OUTPUT JSON SCHEMA:",
            "{",
            '  "schema_version": "v0.5-llm-syllabus-outline",',
            '  "status": "llm-analyst-approved",',
            '  "source_inputs": {',
            '    "markdown_companion_read": true,',
            '    "page_evidence_read": true,',
            '    "markdown_extraction_status": "success",',
            '    "raw_pdf_available_to_llm": false,',
            '    "markdown_path": "source/specification.md",',
            '    "page_evidence_path": "syllabus-evidence.json",',
            '    "markdown_extraction_path": "source/markdown-extraction.json"',
            "  },",
            '  "cross_check": {',
            '    "markdown_structure_used": "Explain the headings, tables, bullets, and boundaries used from Markdown.",',
            '    "page_evidence_used": "Explain how page-level evidence verified pages, snippets, and source coverage.",',
            '    "mismatches": [],',
            '    "markdown_omissions": [],',
            '    "unresolved_source_gaps": []',
            "  },",
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
            '  "coverage_granularity": {',
            '    "contract": "atomic-examinable-point-v1",',
            '    "unit_definition": "The lowest independently teachable or assessable statement in this source.",',
            '    "container_audit": [',
            "      {",
            '        "container_id": "STRUCTURE_ID_FROM_SOURCE or ROOT for a flat source",',
            '        "container_title": "Official container title or Flat source",',
            '        "detail_model": "single_examinable_point | multiple_examinable_points | no_examinable_content",',
            '        "source_coverage_ids": ["SC001"],',
            '        "evidence_page": 12,',
            '        "evidence_excerpt": "Short source excerpt proving the detail found inside this container",',
            '        "single_point_rationale": "Required for single_examinable_point; explain why no deeper assessable split exists."',
            "      }",
            "    ]",
            "  },",
            '  "source_coverage": [',
            "    {",
            '      "id": "SC001",',
            '      "parent_path": ["Structural heading from this PDF", "Optional subsection from this PDF"],',
            '      "content": "One examinable source item from this PDF",',
            '      "additional_information": "Clarifying source text from the same row, bullet, or linked column",',
            '      "source_kind": "coded_point | bullet | sub_bullet | table_row | skill_statement | formula_requirement | restriction | application_statement | prose_clause | single_requirement | knowledge_statement | conceptual_relationship | practical_requirement | data_handling_requirement | source_analysis_requirement | extended_response_requirement | language_requirement | portfolio_requirement | other_source_bound_requirement",',
            '      "exam_action": "The independently assessable demand. Use a source-backed command when present; otherwise state the knowledge, performance, practical, analytical, or portfolio demand without inventing one.",',
            '      "atomicity": "atomic",',
            '      "page": 12',
            "    }",
            "  ],",
            '  "granularity_audit": [',
            "    {",
            '      "source_coverage_id": "SC001",',
            '      "teaching_treatment": "independent_topic | merged_into_topic | prerequisite | sub_skill",',
            '      "target_topic_title": "Topic title that visibly teaches this source item",',
            '      "merge_rationale": "Required when merged_into_topic or sub_skill; explain the teaching reason.",',
            '      "visible_treatment": "Where the handbook will show this item: topic title, explanation, worked example, practice, or sub-skill."',
            "    }",
            "  ],",
            '  "topics": [',
            "    {",
            '      "title": "Teachable knowledge unit named from the source evidence",',
            '      "parent_path": ["Structural heading from this PDF", "Optional subsection from this PDF"],',
            '      "source_coverage_ids": ["SC001"],',
            '      "split_rationale": "One source row with its clarification forms one teachable unit.",',
            '      "cluster_justification": null,',
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
            "1. Read all three inputs: source/specification.md, source/markdown-extraction.json, and syllabus-evidence.json.",
            "",
            "2. If Markdown and page-level evidence conflict, page-level evidence is authoritative for source truth.",
            "",
            "3. Do not rely on candidate hints or Python guesses. Python did not split topics from Markdown.",
            "",
            "4. Let this syllabus decide the structure. Do not require any preselected layers",
            "   provider-specific labels, subject template, command-verb list, or fixed split count.",
            "",
            "5. Do not collapse detailed examinable content into container headings. If you list",
            "   multiple source_coverage items under a container, topics[] must show how those",
            "   items are taught or tightly clustered.",
            "   An official label such as Topic, Unit, Section, or chapter is a parent_path",
            "   container unless container_audit proves it contains one indivisible exam point.",
            "",
            "6. Do not invent board/subject information. If the evidence is unclear, output",
            "   an issues array explaining the uncertainty instead of guessing.",
            "",
            "AFTER YOU OUTPUT THIS JSON:",
            "- Python validates self-consistency: topics[] must map to source_coverage and",
            "  must not simply reuse structure entries as collapsed teaching units.",
            "- Python writes qualification.json from topics[] for the Writer.",
            "- The structure_analysis, official_structure, and source_coverage remain in",
            "  syllabus-outline.json for mechanical checks and final review.",
            "- If invalid, the host LLM returns exact schema or evidence issues to you for repair.",
            "",
            "DELIVERY CHECKLIST:",
            "- source_inputs confirms Markdown companion and page evidence were both read.",
            "- cross_check records Markdown structure use, page-evidence verification, mismatches, omissions, and unresolved gaps.",
            "- structure_analysis explains how this exact PDF is organized.",
            "- source_coverage records the actual examinable items selected from the source.",
            "- coverage_granularity audits every lowest source container and every source_coverage",
            "  item is an atomic assessable statement with source_kind and exam_action.",
            "- topics[] contains final teachable knowledge units or justified tight clusters.",
            "- No official directory-level heading has been silently promoted to a final topic",
            "  unless its audit proves that it contains exactly one indivisible requirement.",
            "- Every topic has exam_points, source_snippets, parent_path, and source_coverage_ids.",
            "- schema_version is v0.5-llm-syllabus-outline.",
            "",
            "HANDOFF NOTE:",
            '"Syllabus outline approved with [X] teachable knowledge units mapped to [Y] source coverage items. Ready for Handbook Writer."',
            "",
            "=" * 80,
            "source/markdown-extraction.json:",
            "=" * 80,
            "",
            markdown_report,
            "",
            "source/specification.md:",
            "=" * 80,
            "",
            markdown_payload[:120000]
            + (
                "\n\n[... truncated; read the full source/specification.md file in the package ...]"
                if len(markdown_payload) > 120000
                else ""
            ),
            "",
            "syllabus-evidence.json (page-level source truth; read all pages):",
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

    issues.extend(_validate_source_inputs_cross_check(data))

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
    elif not str(structure_analysis.get("lowest_source_unit") or "").strip():
        issues.append(
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must name structure_analysis.lowest_source_unit below container headings.",
            )
        )
    if isinstance(structure_analysis, dict):
        structure_model = str(structure_analysis.get("model") or "").strip().lower()
        if structure_model in {"nested", "mixed", "route-based", "table-based", "code-based"}:
            official_structure = data.get("official_structure")
            if not isinstance(official_structure, list) or not any(
                isinstance(item, dict) and str(item.get("id") or "").strip()
                for item in official_structure
            ):
                issues.append(
                    SyllabusOutlineIssue(
                        "error",
                        "Non-flat structure_analysis.model requires official_structure entries "
                        "so container headings cannot silently become final topics.",
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
    granularity_issues, single_point_coverage_ids = _validate_coverage_granularity(
        data, coverage_ids
    )
    issues.extend(granularity_issues)
    for coverage_index, item in enumerate(coverage_items, start=1):
        coverage_id = str(item.get("id") or "").strip()
        if not coverage_id:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_coverage item {coverage_index} is missing a stable id."
                )
            )
        source_kind = str(item.get("source_kind") or "").strip()
        if source_kind not in ALLOWED_SOURCE_KINDS:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"source_coverage item {coverage_index} has invalid source_kind: "
                    f"{source_kind or 'missing'}",
                )
            )
        if str(item.get("atomicity") or "").strip() != "atomic":
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"source_coverage item {coverage_index} must declare atomicity='atomic'.",
                )
            )
        if not str(item.get("exam_action") or "").strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_coverage item {coverage_index} is missing exam_action."
                )
            )
        content = str(item.get("content") or "").strip()
        if not content:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_coverage item {coverage_index} is missing content."
                )
            )
        elif (
            _normalize_text(content) in structure_titles
            or _normalize_structure_title(content) in structure_titles
        ) and coverage_id not in single_point_coverage_ids:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"source_coverage item {coverage_index} reuses a structural container "
                    "without a single-point container audit.",
                )
            )
        try:
            page = int(item.get("page", 0))
        except (TypeError, ValueError):
            page = 0
        if page <= 0:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_coverage item {coverage_index} has invalid page."
                )
            )
    used_coverage_ids: set[str] = set()
    issues.extend(_validate_granularity_audit(data, coverage_ids))

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
    issues.extend(_validate_topic_primary_coverage(data, topics))
    return issues


def _validate_source_inputs_cross_check(data: dict[str, object]) -> list[SyllabusOutlineIssue]:
    issues: list[SyllabusOutlineIssue] = []
    source_inputs = data.get("source_inputs")
    if not isinstance(source_inputs, dict):
        return [
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must include source_inputs confirming Markdown companion and page evidence use.",
            )
        ]
    for input_field in ("markdown_companion_read", "page_evidence_read"):
        if source_inputs.get(input_field) is not True:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"source_inputs.{input_field} must be true."
                )
            )
    status = str(source_inputs.get("markdown_extraction_status") or "").strip()
    if not status:
        issues.append(
            SyllabusOutlineIssue(
                "error", "source_inputs.markdown_extraction_status must record the MarkItDown status."
            )
        )

    cross_check = data.get("cross_check")
    if not isinstance(cross_check, dict):
        return [
            *issues,
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must include cross_check for Markdown/page-evidence comparison.",
            ),
        ]
    for cross_check_field in ("markdown_structure_used", "page_evidence_used"):
        if not str(cross_check.get(cross_check_field) or "").strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"cross_check.{cross_check_field} must be described."
                )
            )
    for list_field in ("mismatches", "markdown_omissions", "unresolved_source_gaps"):
        if not isinstance(cross_check.get(list_field), list):
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"cross_check.{list_field} must be a list."
                )
            )
    return issues


def _validate_coverage_granularity(
    data: dict[str, object], coverage_ids: set[str]
) -> tuple[list[SyllabusOutlineIssue], set[str]]:
    granularity = data.get("coverage_granularity")
    if not isinstance(granularity, dict):
        return (
            [
                SyllabusOutlineIssue(
                    "error",
                    "Analyst outline must include coverage_granularity proving source-detail depth.",
                )
            ],
            set(),
        )

    issues: list[SyllabusOutlineIssue] = []
    if str(granularity.get("contract") or "").strip() != ATOMIC_COVERAGE_CONTRACT:
        issues.append(
            SyllabusOutlineIssue(
                "error",
                f"coverage_granularity.contract must be {ATOMIC_COVERAGE_CONTRACT}.",
            )
        )
    if not str(granularity.get("unit_definition") or "").strip():
        issues.append(
            SyllabusOutlineIssue(
                "error", "coverage_granularity.unit_definition must define an atomic exam point."
            )
        )

    raw_audits = granularity.get("container_audit")
    audits = (
        [item for item in raw_audits if isinstance(item, dict)]
        if isinstance(raw_audits, list)
        else []
    )
    if not audits:
        issues.append(
            SyllabusOutlineIssue(
                "error", "coverage_granularity.container_audit must inspect every lowest container."
            )
        )
        return issues, set()

    audited_containers: set[str] = set()
    audited_coverage_ids: set[str] = set()
    single_point_coverage_ids: set[str] = set()
    for index, audit in enumerate(audits, start=1):
        container_id = str(audit.get("container_id") or "").strip()
        if not container_id:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"container_audit item {index} is missing container_id."
                )
            )
        elif container_id in audited_containers:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"container_audit repeats container_id: {container_id}."
                )
            )
        audited_containers.add(container_id)

        if not str(audit.get("container_title") or "").strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"container_audit item {index} is missing container_title."
                )
            )
        detail_model = str(audit.get("detail_model") or "").strip()
        if detail_model not in ALLOWED_CONTAINER_DETAIL_MODELS:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"container_audit item {index} has invalid detail_model: "
                    f"{detail_model or 'missing'}.",
                )
            )
        raw_ids = audit.get("source_coverage_ids")
        item_ids = (
            [str(value).strip() for value in raw_ids if str(value).strip()]
            if isinstance(raw_ids, list)
            else []
        )
        unknown = [coverage_id for coverage_id in item_ids if coverage_id not in coverage_ids]
        if unknown:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"container_audit item {index} references unknown source_coverage ids: "
                    + ", ".join(unknown[:8]),
                )
            )
        duplicates = audited_coverage_ids.intersection(item_ids)
        if duplicates:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    "source_coverage items must belong to one lowest container audit; repeated: "
                    + ", ".join(sorted(duplicates)[:8]),
                )
            )
        audited_coverage_ids.update(item_ids)

        if detail_model == "multiple_examinable_points" and len(item_ids) < 2:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"container_audit item {index} declares multiple exam points but maps "
                    f"only {len(item_ids)} source_coverage item(s).",
                )
            )
        if detail_model == "single_examinable_point":
            if len(item_ids) != 1:
                issues.append(
                    SyllabusOutlineIssue(
                        "error",
                        f"container_audit item {index} declares one exam point and must map "
                        "exactly one source_coverage item.",
                    )
                )
            else:
                single_point_coverage_ids.add(item_ids[0])
            if not str(audit.get("single_point_rationale") or "").strip():
                issues.append(
                    SyllabusOutlineIssue(
                        "error",
                        f"container_audit item {index} must justify why no deeper split exists.",
                    )
                )
        if detail_model == "no_examinable_content" and item_ids:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"container_audit item {index} declares no examinable content but maps "
                    "source_coverage items.",
                )
            )
        try:
            evidence_page = int(audit.get("evidence_page", 0))
        except (TypeError, ValueError):
            evidence_page = 0
        if evidence_page <= 0:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"container_audit item {index} has invalid evidence_page."
                )
            )
        if not str(audit.get("evidence_excerpt") or "").strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"container_audit item {index} is missing evidence_excerpt."
                )
            )

    expected_containers = _official_leaf_structure_ids(data) or {"ROOT"}
    missing_containers = sorted(expected_containers - audited_containers)
    if missing_containers:
        issues.append(
            SyllabusOutlineIssue(
                "error",
                "container_audit is missing lowest official container(s): "
                + ", ".join(missing_containers[:8]),
            )
        )
    missing_coverage = sorted(coverage_ids - audited_coverage_ids)
    if missing_coverage:
        issues.append(
            SyllabusOutlineIssue(
                "error",
                "container_audit does not account for source_coverage item(s): "
                + ", ".join(missing_coverage[:8]),
            )
        )
    return issues, single_point_coverage_ids


def _validate_topic_primary_coverage(
    data: dict[str, object], topics: list[object]
) -> list[SyllabusOutlineIssue]:
    topic_entries = [topic for topic in topics if isinstance(topic, dict)]
    topic_by_title: dict[str, dict[str, object]] = {}
    issues: list[SyllabusOutlineIssue] = []
    coverage_to_topics: dict[str, list[str]] = {}
    for index, topic in enumerate(topic_entries, start=1):
        title = str(topic.get("title") or "").strip()
        normalized = _normalize_text(title)
        if normalized in topic_by_title:
            issues.append(
                SyllabusOutlineIssue("error", f"Topic {index} duplicates topic title: {title}")
            )
        topic_by_title[normalized] = topic
        raw_ids = topic.get("source_coverage_ids") or topic.get("coverage_ids")
        topic_ids = (
            [str(value).strip() for value in raw_ids if str(value).strip()]
            if isinstance(raw_ids, list)
            else []
        )
        for coverage_id in topic_ids:
            coverage_to_topics.setdefault(coverage_id, []).append(title)

        if len(topic_ids) > 1:
            cluster = topic.get("cluster_justification")
            if not isinstance(cluster, dict):
                issues.append(
                    SyllabusOutlineIssue(
                        "error",
                        f"Topic {index} maps multiple atomic source items and requires "
                        "cluster_justification.",
                    )
                )
            else:
                relationship = str(cluster.get("relationship") or "").strip()
                if relationship not in ALLOWED_CLUSTER_RELATIONSHIPS:
                    issues.append(
                        SyllabusOutlineIssue(
                            "error",
                            f"Topic {index} has invalid cluster relationship: "
                            f"{relationship or 'missing'}.",
                        )
                    )
                if not str(cluster.get("why_not_separate") or "").strip():
                    issues.append(
                        SyllabusOutlineIssue(
                            "error",
                            f"Topic {index} cluster_justification must explain why the "
                            "atomic items should not be separate topics.",
                        )
                    )

    for coverage_id, target_titles in coverage_to_topics.items():
        if len(target_titles) > 1:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"source_coverage item {coverage_id} is mapped to multiple topics: "
                    + ", ".join(target_titles),
                )
            )

    raw_audit = data.get("granularity_audit")
    audit_entries = (
        [item for item in raw_audit if isinstance(item, dict)]
        if isinstance(raw_audit, list)
        else []
    )
    audit_by_topic: dict[str, list[dict[str, object]]] = {}
    for index, item in enumerate(audit_entries, start=1):
        target = str(item.get("target_topic_title") or "").strip()
        target_key = _normalize_text(target)
        coverage_id = str(
            item.get("source_coverage_id") or item.get("coverage_id") or ""
        ).strip()
        target_topic = topic_by_title.get(target_key)
        if target_topic is None:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"granularity_audit item {index} targets unknown topic: "
                    f"{target or 'missing'}.",
                )
            )
            continue
        raw_target_topic_ids = target_topic.get(
            "source_coverage_ids"
        ) or target_topic.get("coverage_ids")
        target_topic_ids = (
            {str(value).strip() for value in raw_target_topic_ids if str(value).strip()}
            if isinstance(raw_target_topic_ids, list)
            else set()
        )
        if coverage_id and coverage_id not in target_topic_ids:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"granularity_audit item {index} targets {target} but that topic does "
                    f"not map {coverage_id}.",
                )
            )
        audit_by_topic.setdefault(target_key, []).append(item)

    for index, topic in enumerate(topic_entries, start=1):
        title = str(topic.get("title") or "").strip()
        entries = audit_by_topic.get(_normalize_text(title), [])
        primary_count = sum(
            str(item.get("teaching_treatment") or "").strip() == "independent_topic"
            for item in entries
        )
        if primary_count < 1:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"Topic {index} must map at least one independent_topic source item; "
                    f"found {primary_count}.",
                )
            )
    return issues


def _official_leaf_structure_ids(data: dict[str, object]) -> set[str]:
    structure = data.get("official_structure")
    if not isinstance(structure, list):
        return set()
    ids: set[str] = set()
    parent_ids: set[str] = set()
    for item in structure:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or "").strip()
        parent_id = str(item.get("parent_id") or "").strip()
        if item_id:
            ids.add(item_id)
        if parent_id:
            parent_ids.add(parent_id)
    return ids - parent_ids


def _validate_granularity_audit(
    data: dict[str, object],
    coverage_ids: set[str],
) -> list[SyllabusOutlineIssue]:
    audit = data.get("granularity_audit")
    if not isinstance(audit, list) or not audit:
        return [
            SyllabusOutlineIssue(
                "error",
                "Analyst outline must include granularity_audit for every source_coverage item.",
            )
        ]

    issues: list[SyllabusOutlineIssue] = []
    audited_ids: set[str] = set()
    valid_treatments = {"independent_topic", "merged_into_topic", "prerequisite", "sub_skill"}
    for index, item in enumerate(audit, start=1):
        if not isinstance(item, dict):
            issues.append(SyllabusOutlineIssue("error", f"granularity_audit item {index} must be an object."))
            continue
        coverage_id = str(item.get("source_coverage_id") or item.get("coverage_id") or "").strip()
        if not coverage_id:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"granularity_audit item {index} is missing source_coverage_id."
                )
            )
            continue
        audited_ids.add(coverage_id)
        if coverage_ids and coverage_id not in coverage_ids:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"granularity_audit item {index} references unknown source_coverage id: {coverage_id}",
                )
            )
        treatment = str(item.get("teaching_treatment") or "").strip()
        if treatment not in valid_treatments:
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"granularity_audit item {index} has invalid teaching_treatment: {treatment or 'missing'}",
                )
            )
        target = str(item.get("target_topic_title") or "").strip()
        visible = str(item.get("visible_treatment") or "").strip()
        if not target:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"granularity_audit item {index} must name target_topic_title."
                )
            )
        if not visible:
            issues.append(
                SyllabusOutlineIssue(
                    "error", f"granularity_audit item {index} must describe visible_treatment."
                )
            )
        if treatment in {"merged_into_topic", "sub_skill"} and not str(
            item.get("merge_rationale") or ""
        ).strip():
            issues.append(
                SyllabusOutlineIssue(
                    "error",
                    f"granularity_audit item {index} must explain merge_rationale for {treatment}.",
                )
            )
    missing = sorted(coverage_ids - audited_ids)
    if missing:
        preview = ", ".join(missing[:8])
        issues.append(
            SyllabusOutlineIssue(
                "error",
                f"granularity_audit is missing {len(missing)} source_coverage item(s): {preview}",
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
