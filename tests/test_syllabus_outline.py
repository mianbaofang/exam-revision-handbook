from __future__ import annotations

from intl_exam_guide.planning.syllabus_outline import (
    apply_syllabus_outline_response,
    build_syllabus_evidence,
    build_syllabus_outline_prompt,
    validate_syllabus_outline,
)
from intl_exam_guide.models import Qualification, SourceRecord


def outline_base() -> dict[str, object]:
    return {
        "schema_version": "v0.5-llm-syllabus-outline",
        "status": "llm-analyst-approved",
        "source_inputs": {
            "markdown_companion_read": True,
            "page_evidence_read": True,
            "markdown_extraction_status": "success",
            "raw_pdf_available_to_llm": False,
        },
        "cross_check": {
            "markdown_structure_used": "Markdown showed the two skill statements as flat bullets.",
            "page_evidence_used": "Page-level evidence confirmed both bullets and page references.",
            "mismatches": [],
            "markdown_omissions": [],
            "unresolved_source_gaps": [],
        },
        "structure_analysis": {
            "model": "flat",
            "rationale": "The PDF lists two standalone skill statements with no deeper hierarchy.",
            "lowest_source_unit": "skill statements",
        },
        "official_structure": [],
        "source_coverage": [
            {
                "id": "SC001",
                "parent_path": [],
                "content": "Use ratios to compare quantities.",
                "page": 4,
            },
            {
                "id": "SC002",
                "parent_path": [],
                "content": "Solve direct proportion problems.",
                "page": 4,
            },
        ],
        "granularity_audit": [
            {
                "source_coverage_id": "SC001",
                "teaching_treatment": "independent_topic",
                "target_topic_title": "Ratios for comparing quantities",
                "merge_rationale": "",
                "visible_treatment": "Dedicated topic with explanation and practice coverage.",
            },
            {
                "source_coverage_id": "SC002",
                "teaching_treatment": "independent_topic",
                "target_topic_title": "Direct proportion problems",
                "merge_rationale": "",
                "visible_treatment": "Dedicated topic with explanation and practice coverage.",
            },
        ],
        "topics": [
            {
                "title": "Ratios for comparing quantities",
                "parent_path": [],
                "source_coverage_ids": ["SC001"],
                "split_rationale": "One source skill statement is one teachable unit.",
                "exam_points": ["Use ratios to compare quantities."],
                "source_snippets": [
                    {
                        "page": 4,
                        "text": "Use ratios to compare quantities.",
                        "matched_term": "ratios",
                    }
                ],
            },
            {
                "title": "Direct proportion problems",
                "parent_path": [],
                "source_coverage_ids": ["SC002"],
                "split_rationale": "One source skill statement is one teachable unit.",
                "exam_points": ["Solve direct proportion problems."],
                "source_snippets": [
                    {
                        "page": 4,
                        "text": "Solve direct proportion problems.",
                        "matched_term": "direct proportion",
                    }
                ],
            },
        ],
    }


def test_syllabus_outline_prompt_includes_dual_track_inputs_and_page_priority():
    qualification = Qualification(
        title="Test Mathematics",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Mathematics",
        page_url="https://example.test/math",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/math",
            specification_url="https://example.test/spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="For test students.",
    )
    evidence = build_syllabus_evidence(qualification, [(4, "Use ratios to compare quantities.")])
    prompt = build_syllabus_outline_prompt(
        qualification,
        evidence,
        "# Specification\n\n## Ratio and proportion",
        {"status": "success", "markdown_path": "source/specification.md"},
    )

    assert "source/specification.md" in prompt
    assert "source/markdown-extraction.json" in prompt
    assert "syllabus-evidence.json" in prompt
    assert "page-level evidence wins" in prompt
    assert "Python must not parse Markdown to split topics" in prompt



def test_outline_validation_accepts_small_llm_led_flat_split():
    issues = validate_syllabus_outline(outline_base())

    assert [issue for issue in issues if issue.severity == "error"] == []



def test_outline_validation_requires_dual_track_audit_fields():
    outline = outline_base()
    outline["source_inputs"] = {"markdown_companion_read": False}
    outline.pop("cross_check")

    messages = [issue.message for issue in validate_syllabus_outline(outline)]

    assert any("source_inputs" in message for message in messages)
    assert any("cross_check" in message for message in messages)



def test_outline_validation_requires_granularity_audit_for_each_source_item():
    outline = outline_base()
    outline["granularity_audit"] = [
        {
            "source_coverage_id": "SC001",
            "teaching_treatment": "merged_into_topic",
            "target_topic_title": "Ratio and proportion skills",
            "visible_treatment": "Covered only by the broad topic title.",
        }
    ]

    messages = [issue.message for issue in validate_syllabus_outline(outline)]

    assert any("merge_rationale" in message for message in messages)
    assert any("granularity_audit is missing 1 source_coverage" in message for message in messages)



    outline = outline_base()
    outline["structure_analysis"] = {
        "model": "nested",
        "rationale": "The PDF groups the source rows under a section container.",
        "lowest_source_unit": "content rows",
    }
    outline["official_structure"] = [
        {
            "id": "S1",
            "title": "1.1 Ratio and proportion",
            "role": "source-structure",
            "parent_id": None,
            "page_start": 4,
            "page_end": 4,
        }
    ]
    outline["topics"] = [
        {
            "title": "1.1 Ratio and proportion",
            "parent_path": ["1.1 Ratio and proportion"],
            "source_coverage_ids": ["SC001", "SC002"],
            "split_rationale": "Incorrectly collapsed two rows into the section heading.",
            "exam_points": ["Use ratios and solve direct proportion problems."],
            "source_snippets": [
                {
                    "page": 4,
                    "text": "Use ratios to compare quantities. Solve direct proportion problems.",
                    "matched_term": "Ratio and proportion",
                }
            ],
        }
    ]

    messages = [issue.message for issue in validate_syllabus_outline(outline)]

    assert any("reuses a declared structure title" in message for message in messages)


def test_outline_validation_rejects_collapsed_declared_structure_title_without_code():
    outline = outline_base()
    outline["structure_analysis"] = {
        "model": "nested",
        "rationale": "The PDF groups the source rows under a numbered section container.",
        "lowest_source_unit": "content rows",
    }
    outline["official_structure"] = [
        {
            "id": "S1",
            "title": "1.1 Ratio and proportion",
            "role": "source-structure",
            "parent_id": None,
            "page_start": 4,
            "page_end": 4,
        }
    ]
    outline["topics"] = [
        {
            "title": "Ratio and proportion",
            "parent_path": ["1.1 Ratio and proportion"],
            "source_coverage_ids": ["SC001", "SC002"],
            "split_rationale": "Incorrectly collapsed two rows into the section heading.",
            "exam_points": ["Use ratios and solve direct proportion problems."],
            "source_snippets": [
                {
                    "page": 4,
                    "text": "Use ratios to compare quantities. Solve direct proportion problems.",
                    "matched_term": "Ratio and proportion",
                }
            ],
        }
    ]

    messages = [issue.message for issue in validate_syllabus_outline(outline)]

    assert any("reuses a declared structure title" in message for message in messages)


def test_outline_validation_rejects_source_coverage_without_stable_ids():
    outline = outline_base()
    outline["source_coverage"] = [
        {
            "parent_path": [],
            "content": "Use ratios to compare quantities.",
            "page": 4,
        }
    ]
    outline["topics"] = [
        {
            "title": "Ratios for comparing quantities",
            "parent_path": [],
            "source_coverage_ids": ["SC001"],
            "split_rationale": "One source skill statement is one teachable unit.",
            "exam_points": ["Use ratios to compare quantities."],
            "source_snippets": [
                {
                    "page": 4,
                    "text": "Use ratios to compare quantities.",
                    "matched_term": "ratios",
                }
            ],
        }
    ]

    messages = [issue.message for issue in validate_syllabus_outline(outline)]

    assert "source_coverage item 1 is missing a stable id." in messages
    assert any("references unknown source_coverage id: SC001" in message for message in messages)

    qualification = Qualification(
        title="Test Mathematics",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Mathematics",
        page_url="https://example.test/math",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(provider="test", page_url="https://example.test/math"),
        audience_note="For test students.",
    )

    result = apply_syllabus_outline_response(qualification, outline_base())

    assert result.ok
    assert [topic.title for topic in result.qualification.topics] == [
        "Ratios for comparing quantities",
        "Direct proportion problems",
    ]
    assert "outline-source:llm-analyst" in result.qualification.route_tags
