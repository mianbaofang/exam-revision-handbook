import json

from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    VisualBrief,
)
from intl_exam_guide.rendering.handbook_package import write_visual_assets

from intl_exam_guide.auditing.visual_jobs import build_visual_jobs, visual_jobs_markdown


def sample_qualification() -> Qualification:
    return Qualification(
        title="International GCSE Chemistry Example (9202)",
        code="9202",
        qualification_type="international_gcse",
        subject_area="Chemistry",
        page_url="https://example.test/chemistry/",
        summary=["Students learn bonding, structure, and properties."],
        topics=[
            Topic(
                title="Bonding",
                points=["Describe ionic bonding."],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Students should describe ionic bonding.",
                        matched_term="ionic bonding",
                    )
                ],
            )
        ],
        assessments=[AssessmentPaper(title="Paper 1", details=["1 hour 30 minutes"])],
        source=SourceRecord(
            provider="cambridge",
            page_url="https://example.test/chemistry/",
        ),
        audience_note="International GCSE qualification.",
    )


def test_visual_jobs_explain_pending_generation_and_replacement():
    manifest = [
        {
            "id": "visual_001",
            "topic_title": "Bonding",
            "complexity": "infographic",
            "asset_status": "svg-fallback-needs-review",
            "file": "visual_001_bonding-svg-fallback.svg",
            "prompt": "Create bonding infographic.",
            "source_pages": [12],
        }
    ]

    jobs = build_visual_jobs(manifest)
    markdown = visual_jobs_markdown(jobs)

    assert jobs[0]["replacement_target"] == "visual_001"
    assert jobs[0]["status"] == "needs_generation_or_review"
    assert jobs[0]["complexity"] == "infographic"
    assert "visual_001" in markdown
    assert "Create bonding infographic." in markdown
    assert "Import with scripts/import_infographic_assets.py" in markdown
    assert "Generation choices" in markdown
    assert "PNG/JPG/WebP" in markdown
    assert "--asset-dir" in markdown
    assert "re-renders the named handbook HTML" in markdown


def test_visual_jobs_include_provider_selected_pending_generation():
    jobs = build_visual_jobs(
        [
            {
                "id": "visual_002",
                "topic_title": "Market equilibrium",
                "complexity": "infographic",
                "asset_status": "provider-selected-pending-generation",
                "file": "visual_002_market.svg",
                "prompt": "Create market equilibrium infographic.",
            }
        ]
    )

    assert jobs[0]["replacement_target"] == "visual_002"
    assert jobs[0]["status"] == "needs_generation_or_review"


def test_visual_jobs_include_pending_professional_diagrams():
    jobs = build_visual_jobs(
        [
            {
                "id": "visual_003",
                "topic_title": "Organisation structure",
                "complexity": "svg-basic",
                "visual_type": "organisation structure hierarchy",
                "asset_status": "professional-diagram-required",
                "file": None,
                "prompt": "Create organisation structure diagram.",
            }
        ]
    )

    assert jobs[0]["replacement_target"] == "visual_003"
    assert jobs[0]["complexity"] == "svg-basic"
    assert jobs[0]["visual_type"] == "organisation structure hierarchy"


def test_write_visual_assets_writes_infographic_jobs_outputs(tmp_path):
    visual = VisualBrief(
        topic_title="Bonding",
        focus_point="ionic bonding and properties",
        trigger="spatial structure and property links need a labelled visual",
        visual_type="bonding and structure infographic",
        complexity="infographic",
        image_provider="prompt-queue",
        prompt="Create bonding infographic.",
        source_points=["Describe ionic bonding."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should describe ionic bonding.",
                matched_term="ionic bonding",
            )
        ],
    )
    plan = GuidePlan(
        qualification=sample_qualification(),
        run_options=GuideRunOptions(
            requested_subject="Chemistry",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[],
        practice_items=[],
        visual_briefs=[visual],
        diagram_briefs=[],
        revision_stages=[],
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    write_visual_assets(plan, images_dir)

    jobs = json.loads((images_dir / "infographic_jobs.json").read_text(encoding="utf-8"))
    markdown = (images_dir / "infographic_jobs.md").read_text(encoding="utf-8")

    assert jobs == [
        {
            "id": "visual_001",
            "topic_title": "Bonding",
            "status": "needs_generation_or_review",
            "complexity": "infographic",
            "visual_type": "bonding and structure infographic",
            "current_file": None,
            "replacement_target": "visual_001",
            "prompt": "Create bonding infographic.",
            "source_pages": [12],
            "import_hint": "Import with scripts/import_infographic_assets.py using a file named with this visual ID.",
        }
    ]
    assert "visual_001" in markdown
    assert "Replacement target: visual_001" in markdown
