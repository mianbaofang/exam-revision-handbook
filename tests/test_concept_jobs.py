import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from intl_exam_guide.auditing.concept_jobs import (
    build_concept_jobs,
    concept_jobs_markdown,
    reviewed_concept_titles,
    write_concept_jobs,
)
from intl_exam_guide.models import Qualification, SourceRecord, SourceSnippet, Topic
from intl_exam_guide.planning.guide_plan import build_guide_plan


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_concept_explanations.py"
SCRIPT_SPEC = spec_from_file_location("import_concept_explanations", SCRIPT_PATH)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
SCRIPT_MODULE = module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)
load_concept_explanations = SCRIPT_MODULE.load_concept_explanations
apply_concept_explanations = SCRIPT_MODULE.apply_concept_explanations


def sample_plan():
    qualification = Qualification(
        title="International GCSE Economics",
        code="0000",
        qualification_type="international_gcse",
        subject_area="Economics",
        page_url="https://example.test/economics",
        summary=["Example"],
        topics=[
            Topic(
                title="2.3 - Market failure: External costs and benefits",
                points=["External costs and benefits affect third parties."],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="External costs and benefits affect third parties.",
                        matched_term="External costs",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/economics",
            specification_url="https://example.test/economics.pdf",
        ),
        audience_note="Example international students outside the UK.",
    )
    return build_guide_plan(
        qualification,
        output_language="zh-CN",
        explanation_style="friendly",
    )


def test_concept_jobs_are_bound_to_current_topic_source():
    jobs = build_concept_jobs(sample_plan())

    assert len(jobs) == 1
    assert jobs[0]["topic_title"] == "2.3 - Market failure: External costs and benefits"
    assert jobs[0]["source_points"] == ["External costs and benefits affect third parties"]
    assert jobs[0]["contract_version"] == "v0.5-visual-decision-pedagogy"
    assert jobs[0]["subject_pack"] == "economics"
    assert jobs[0]["writing_contract"]["subject_pack"] == "economics"
    assert jobs[0]["review_contract"]["id"] == "concept_001_review"
    assert "Stay inside topic_title and source_points" in str(jobs[0]["task"])


def test_concept_jobs_use_visible_source_points_without_pdf_boilerplate():
    plan = sample_plan()
    plan.qualification.topics[0].points = [
        "External costs and benefits affect third parties.",
        "Cambridge IGCSE Economics 0455 syllabus for 2027, 2028 and 2029. Subject content",
        "12www.cambridgeinternational.org/igcseBack to contents page",
        "Faculty feedback: Understanding how and why our climate is changing.",
    ]

    jobs = build_concept_jobs(plan)

    assert jobs[0]["source_points"] == ["External costs and benefits affect third parties"]
    assert "Back to contents" not in concept_jobs_markdown(jobs)
    assert "Faculty feedback" not in concept_jobs_markdown(jobs)


def test_concept_jobs_write_review_files_and_read_reviewed_titles(tmp_path):
    plan = sample_plan()

    jobs = write_concept_jobs(plan, tmp_path)
    concepts_dir = tmp_path / "concepts"
    review_path = concepts_dir / "concept_explanations.json"
    review_path.write_text(
        json.dumps(
            [
                {
                    "topic_title": jobs[0]["topic_title"],
                    "explanations": [
                        "外部成本是第三方承担的成本。",
                        "外部收益是第三方获得的收益。",
                    ],
                    "visual_decision": {
                        "recommended_route": "text-ok",
                        "no_visual_reason": "文字解释和例题已经能清楚说明本 topic 的学习重点。",
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert (concepts_dir / "concept_jobs.json").exists()
    assert "External costs" in (concepts_dir / "concept_jobs.md").read_text(encoding="utf-8")
    assert reviewed_concept_titles(tmp_path) == {jobs[0]["topic_title"]}
    assert "concept_001" in concept_jobs_markdown(jobs)


def test_import_concept_explanations_accepts_writer_concepts_schema(tmp_path):
    path = tmp_path / "concept_explanations.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "v0.5-concept-explanations",
                "concepts": [
                    {
                        "topic_title": "Topic A",
                        "explanations": ["Concept A", "Reason A"],
                        "visual_decision": {
                            "recommended_route": "text-ok",
                            "no_visual_reason": "The written explanation already carries the learning clearly.",
                        },
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    entries = load_concept_explanations(path)

    assert entries == [
        {
            "topic_title": "Topic A",
            "explanations": ["Concept A", "Reason A"],
            "visual_decision": {
                "recommended_route": "text-ok",
                "no_visual_reason": "The written explanation already carries the learning clearly.",
            },
        }
    ]


def test_apply_concept_explanations_replaces_matching_topic():
    plan = sample_plan()
    topic_title = plan.topic_guides[0].topic_title

    imported, missing = apply_concept_explanations(
        plan,
        [
            {
                "topic_title": topic_title,
                "explanations": [
                    "外部成本是生产或消费让第三方承担的成本。",
                    "外部收益是第三方获得但没有直接付费的收益。",
                ],
                "visual_decision": {
                    "recommended_route": "text-ok",
                    "no_visual_reason": "文字解释和例题已经能清楚说明本 topic 的学习重点。",
                },
            }
        ],
    )

    assert imported == 1
    assert missing == []
    assert plan.topic_guides[0].checklist == [
        "外部成本是生产或消费让第三方承担的成本。",
        "外部收益是第三方获得但没有直接付费的收益。",
    ]
