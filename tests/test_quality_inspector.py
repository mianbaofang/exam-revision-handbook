import json

from intl_exam_guide.auditing.quality_inspector import (
    build_quality_inspector_prompt,
    inspect_handbook_output,
    write_quality_inspection,
)


MODULE_TEXT = " ".join(
    [
        "International GCSE Revision Guide Specification",
        "How to Study",
        "Study Roadmap Topic Map",
        "One-Sentence Essence Worked Example",
        "Practice",
        "Assessment Paper",
        "Revision Checklist",
    ]
)


def write_minimum_package(tmp_path, *, html_text=MODULE_TEXT, concept_count=2):
    (tmp_path / "guide.html").write_text(f"<html><body>{html_text}</body></html>", encoding="utf-8")
    (tmp_path / "qualification.json").write_text(
        json.dumps({"topics": [{"title": "A"}, {"title": "B"}]}),
        encoding="utf-8",
    )
    (tmp_path / "syllabus-outline.json").write_text(json.dumps({"topics": []}), encoding="utf-8")
    (tmp_path / "guide-plan.json").write_text(json.dumps({}), encoding="utf-8")
    (tmp_path / "validation.json").write_text(json.dumps({}), encoding="utf-8")
    concepts = tmp_path / "concepts"
    concepts.mkdir()
    (concepts / "concept_jobs.json").write_text(json.dumps([{}, {}]), encoding="utf-8")
    (concepts / "concept_explanations.json").write_text(
        json.dumps([{"topic_title": str(index)} for index in range(concept_count)]),
        encoding="utf-8",
    )
    images = tmp_path / "images"
    images.mkdir()
    (images / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "complexity": "svg-basic",
                        "svg_fit": "exact",
                        "asset_status": "reviewed-generated",
                        "review_status": "reviewed",
                        "prompt": "Draw a clear concept map.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_quality_inspector_passes_complete_package(tmp_path):
    write_minimum_package(tmp_path)

    result = inspect_handbook_output(tmp_path)

    assert result.inspection_status == "pass"
    assert result.recommendation == "pass_to_reviewer"
    assert result.checks["topic_count"] == 2
    assert result.checks["concept_explanations"]["entry_count"] == 2


def test_quality_inspector_fails_missing_file_and_placeholder(tmp_path):
    write_minimum_package(
        tmp_path, html_text=f"{MODULE_TEXT} [insert explanation here]", concept_count=1
    )
    (tmp_path / "syllabus-outline.json").unlink()

    result = inspect_handbook_output(tmp_path)
    messages = [issue.message for issue in result.issues]

    assert result.inspection_status == "fail"
    assert result.recommendation == "return_to_writer"
    assert any("syllabus-outline.json" in message for message in messages)
    assert any("Placeholder" in message for message in messages)
    assert any("covers 1 of 2" in message for message in messages)


def test_quality_inspector_fails_missing_concept_explanations(tmp_path):
    write_minimum_package(tmp_path)
    (tmp_path / "concepts" / "concept_explanations.json").unlink()

    result = inspect_handbook_output(tmp_path)
    messages = [issue.message for issue in result.issues]

    assert result.inspection_status == "fail"
    assert any("concepts/concept_explanations.json" in message for message in messages)


def test_quality_inspector_fails_non_exact_or_unreviewed_svg(tmp_path):
    write_minimum_package(tmp_path)
    (tmp_path / "images" / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "complexity": "svg-basic",
                        "asset_status": "svg-draft",
                        "review_status": "draft",
                        "prompt": "Draw a broad force diagram.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = inspect_handbook_output(tmp_path)
    messages = [issue.message for issue in result.issues]

    assert result.inspection_status == "fail"
    assert any("svg_fit=exact" in message for message in messages)
    assert any("has not been reviewed" in message for message in messages)


def test_quality_inspection_writer_and_prompt(tmp_path):
    write_minimum_package(tmp_path)

    path = write_quality_inspection(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    prompt = build_quality_inspector_prompt(tmp_path)

    assert payload["schema_version"] == "v0.5-quality-inspection"
    assert payload["inspection_status"] == "pass"
    assert "Quality Inspector" in prompt
    assert "pass_to_reviewer" in prompt
    assert (tmp_path / "quality-inspection-prompt.md").exists()
