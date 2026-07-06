from __future__ import annotations

from intl_exam_guide.planning.syllabus_outline import (
    apply_syllabus_outline_response,
    validate_syllabus_outline,
)
from intl_exam_guide.models import Qualification, SourceRecord


def outline_base() -> dict[str, object]:
    return {
        "schema_version": "v0.5-llm-syllabus-outline",
        "status": "llm-analyst-approved",
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


def test_outline_validation_accepts_small_llm_led_flat_split():
    issues = validate_syllabus_outline(outline_base())

    assert [issue for issue in issues if issue.severity == "error"] == []


def test_outline_validation_rejects_collapsed_declared_structure_title():
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
