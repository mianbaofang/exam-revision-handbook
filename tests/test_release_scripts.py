import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.rendering.handbook_package import write_visual_assets


SAMPLES = {
    "mathematics-9260-sample": (90, 180, 39),
    "economics-9214-sample": (38, 76, 38),
    "chemistry-9202-sample": (35, 70, 18),
}


def test_verify_release_samples_allows_pending_assets(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=False)

    result = run_verify(outputs, "--allow-pending")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert sum(item["pending_infographics"] for item in payload["samples"]) == 95
    assert all(item["has_pdf"] is False for item in payload["samples"])


def test_verify_release_samples_fails_final_when_assets_are_pending(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=False)

    result = run_verify(outputs)

    assert result.returncode == 1
    assert "missing guide.pdf" in result.stderr
    assert "missing final-review-packet.json" in result.stderr
    assert "missing delivery-contract.json" in result.stderr
    assert "infographic asset(s) still pending" in result.stderr


def test_verify_release_samples_passes_completed_outputs(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=True)

    result = run_verify(outputs)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert sum(item["generated_infographics"] for item in payload["samples"]) == 95
    assert all(item["pending_infographics"] == 0 for item in payload["samples"])
    assert all(item["has_pdf"] is True for item in payload["samples"])
    assert all(item["has_final_review"] is True for item in payload["samples"])
    assert all(item["has_delivery_contract"] is True for item in payload["samples"])


def test_verify_release_samples_requires_final_review_and_delivery_contract(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=True)
    (outputs / "mathematics-9260-sample" / "final-review-packet.json").unlink()
    (outputs / "economics-9214-sample" / "delivery-contract.json").unlink()

    result = run_verify(outputs)

    assert result.returncode == 1
    assert "mathematics-9260-sample: missing final-review-packet.json" in result.stderr
    assert "economics-9214-sample: missing delivery-contract.json" in result.stderr


def test_verify_release_samples_rejects_mixed_language_slash_labels(tmp_path):
    outputs = tmp_path / "outputs"
    write_sample_outputs(outputs, completed=True)
    html_path = outputs / "chemistry-9202-sample" / "guide.html"
    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(html + "<p>Learning guide / 学习手册</p>", encoding="utf-8")

    result = run_verify(outputs)

    assert result.returncode == 1
    assert "mixed-language label remains" in result.stderr


def test_verify_release_samples_defaults_to_current_release_evidence():
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_release_samples.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["evidence_manifest"].endswith(
        "docs\\release-evidence\\v0.6.0\\manifest.json"
    ) or payload["evidence_manifest"].endswith(
        "docs/release-evidence/v0.6.0/manifest.json"
    )
    assert payload["entries"]
    assert all(
        entry["status"] in {"candidate", "draft", "final-ready", "certified"}
        for entry in payload["entries"]
    )


def test_verify_release_evidence_requires_product_review_for_final_ready(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "release": "v0.5.0",
                "overall_status": "final-ready",
                "entries": [
                    {
                        "id": "sample-final-ready",
                        "status": "final-ready",
                        "provider": "oxfordaqa",
                        "level": "as-level",
                        "subject": "Mathematics",
                        "language": "en",
                        "commands": ["python -m intl_exam_guide review --out outputs/sample"],
                        "output_dir": "outputs/sample",
                        "validation_summary": {
                            "error_count": 0,
                            "pending_concept_explanations": 0,
                            "pending_infographic_assets": 0,
                        },
                        "final_review": {"must_not_present_as_final": False},
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_release_samples.py"

    result = subprocess.run(
        [sys.executable, str(script), "--evidence-manifest", str(manifest)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "final-ready/certified entry must include product_review evidence" in result.stderr


def test_import_infographic_assets_updates_manifest(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001_custom.png").write_bytes(b"fake-png")
    (asset_dir / "visual_002.png").write_bytes(b"fake-png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "complexity": "infographic",
                        "asset_status": "external-generation-required",
                        "file": None,
                    },
                    {
                        "id": "visual_002",
                        "complexity": "infographic",
                        "asset_status": "external-generation-required",
                        "file": None,
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir, "--provider", "test-provider")

    assert result.returncode == 0
    manifest_payload = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    assert manifest_payload["schema_version"] == 2
    manifest = manifest_payload["visuals"]
    assert [entry["asset_status"] for entry in manifest] == [
        "reviewed-generated",
        "reviewed-generated",
    ]
    assert [entry["generated_by"] for entry in manifest] == ["test-provider", "test-provider"]
    assert all(entry["asset"]["sha256"] for entry in manifest)
    assert (images_dir / "visual_001_custom.png").exists()
    assert (images_dir / "visual_002.png").exists()
    assert "Imported 2 visual asset(s)." in result.stdout
    assert f"python -m intl_exam_guide review --out {output_dir}" in result.stdout


def test_import_infographic_assets_replaces_svg_fallback_by_visual_id(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.png").write_bytes(b"fake-png")
    (images_dir / "visual_001_old.svg").write_text("<svg></svg>", encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "complexity": "infographic",
                    "asset_status": "svg-fallback-needs-review",
                    "file": "visual_001_old.svg",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 0
    manifest = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    assert manifest[0]["file"] == "visual_001.png"
    assert manifest[0]["asset_status"] == "reviewed-generated"
    assert (images_dir / "visual_001.png").exists()


def test_import_infographic_assets_replaces_provider_selected_pending_asset(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.png").write_bytes(b"fake-png")
    (images_dir / "visual_001_pending.svg").write_text("<svg></svg>", encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "complexity": "infographic",
                    "asset_status": "provider-selected-pending-generation",
                    "file": "visual_001_pending.svg",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 0
    manifest = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    assert manifest[0]["file"] == "visual_001.png"
    assert manifest[0]["asset_status"] == "reviewed-generated"


def test_import_infographic_assets_replaces_pending_professional_diagram(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.svg").write_text('<svg viewBox="0 0 10 10"></svg>', encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "complexity": "svg-basic",
                        "asset_status": "professional-diagram-required",
                        "file": None,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 0
    manifest_payload = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_payload["visuals"]
    assert manifest[0]["file"] == "visual_001.svg"
    assert manifest[0]["asset_status"] == "reviewed-generated"
    assert manifest[0]["asset"]["width"] == 10
    assert manifest[0]["asset"]["height"] == 10


def test_import_infographic_assets_matches_previous_manifest_key_after_id_shift(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "previous-images"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_021.png").write_bytes(b"fake-png")
    key = "topic||focus||visual||infographic"
    (asset_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_021",
                    "key": key,
                    "complexity": "infographic",
                    "asset_status": "reviewed-generated",
                    "file": "visual_021.png",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_005",
                    "key": key,
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 0
    manifest = json.loads((images_dir / "visual_manifest.json").read_text(encoding="utf-8"))
    assert manifest[0]["file"] == "visual_005.png"
    assert manifest[0]["source_asset_file"] == "visual_021.png"
    assert manifest[0]["asset_status"] == "reviewed-generated"
    assert (images_dir / "visual_005.png").exists()


def test_import_infographic_assets_rerenders_html_with_imported_image(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.png").write_bytes(b"fake-png")
    snippet = SourceSnippet(page=12, text="Use tangent gradients.", matched_term="gradient")
    topic = Topic(
        title="P1.3 - Differentiation: Gradients and tangents",
        points=["Applications of differentiation to gradients and tangents."],
        source_snippets=[snippet],
    )
    qualification = Qualification(
        title="International AS Mathematics",
        code="9660",
        qualification_type="international_as_a_level",
        subject_area="Mathematics",
        page_url="https://example.test/math",
        summary=["AS mathematics."],
        topics=[topic],
        assessments=[AssessmentPaper(title="Paper P1", details=["1 hour 30 minutes"])],
        source=SourceRecord(provider="oxfordaqa", page_url="https://example.test/math"),
        audience_note="International AS students.",
    )
    plan = GuidePlan(
        qualification=qualification,
        run_options=GuideRunOptions(
            requested_subject="9660",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[
            TopicGuide(
                topic_title=topic.title,
                essence="Differentiation links a curve to a tangent gradient.",
                analogy="A tangent reads the slope at one instant.",
                mini_worked_example="Find the gradient, then write the tangent.",
                worked_solution_steps=["Read", "Differentiate", "Substitute", "Check"],
                pitfall="Do not use the normal gradient for the tangent.",
                checklist=["Master gradients.", "Apply differentiation.", "Check signs."],
                diagram_brief="Draw curve and tangent.",
                source_snippets=[snippet],
            )
        ],
        practice_items=[],
        visual_briefs=[
            VisualBrief(
                topic_title=topic.title,
                focus_point="gradient of the tangent",
                trigger="calculus and gradient reasoning need carefully annotated graph features",
                visual_type="calculus graph and area annotation infographic",
                complexity="infographic",
                image_provider="external-generation-required",
                prompt="Create a tangent-gradient infographic.",
                source_points=topic.points,
                source_snippets=[snippet],
            )
        ],
        diagram_briefs=[],
        revision_stages=["Study", "Practise"],
    )
    output_dir.mkdir(exist_ok=True)
    (output_dir / "guide-plan.json").write_text(
        json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "qualification.json").write_text(
        json.dumps(qualification.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_visual_assets(plan, images_dir)
    manifest_path = images_dir / "visual_manifest.json"
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_payload["visuals"][0]["visual_need"]["reviewer_visual_decision"] = "approved"
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")
    (output_dir / "guide.html").write_text(
        '<img src="images/visual_001_old-svg-fallback.svg">',
        encoding="utf-8",
    )
    old_pdf = output_dir / "guide.pdf"
    old_pdf.write_bytes(b"%PDF-1.4\n")
    (output_dir / "validation.json").write_text(
        json.dumps({"pdf": str(old_pdf)}), encoding="utf-8"
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 0
    html = (output_dir / "guide.html").read_text(encoding="utf-8")
    assert 'src="images/visual_001.png"' in html
    assert "svg-fallback.svg" not in html
    assert "Re-rendered handbook HTML" in result.stdout
    manifest_after = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_after["visuals"][0]["visual_need"]["reviewer_visual_decision"] == "pending"
    assert old_pdf.exists()
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["pdf"] is None
    assert validation["pdf_export_gate"]["status"] == "pending_current_html_review"


def test_import_scripts_cannot_bypass_reviewed_pdf_export():
    root = Path(__file__).resolve().parents[1]
    for name in ["import_infographic_assets.py", "import_concept_explanations.py"]:
        source = (root / "scripts" / name).read_text(encoding="utf-8")
        assert "export_pdf(" not in source


def test_import_infographic_assets_fails_when_required_asset_missing(tmp_path):
    output_dir = tmp_path / "guide"
    images_dir = output_dir / "images"
    asset_dir = tmp_path / "generated"
    images_dir.mkdir(parents=True)
    asset_dir.mkdir()
    (asset_dir / "visual_001.png").write_bytes(b"fake-png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                },
                {
                    "id": "visual_002",
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_import(output_dir, asset_dir)

    assert result.returncode == 1
    assert "visual_002" in result.stderr


def test_scan_for_raw_keys_does_not_print_secret_value(tmp_path):
    secret = "sk-" + "A" * 30
    (tmp_path / "leaky.txt").write_text(f"token={secret}\n", encoding="utf-8")

    result = run_key_scan(tmp_path)

    assert result.returncode == 1
    assert "raw_key_matches" in result.stdout
    assert "leaky.txt" in result.stdout
    assert secret not in result.stdout
    assert secret not in result.stderr


def test_scan_for_raw_keys_passes_clean_tree(tmp_path):
    (tmp_path / "clean.txt").write_text("no secret here\n", encoding="utf-8")

    result = run_key_scan(tmp_path)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["raw_key_matches"] == 0


def test_render_intro_animation_exposes_cli_help():
    result = run_render_intro_help()

    assert result.returncode == 0
    assert "--html" in result.stdout
    assert "--mp4" in result.stdout
    assert "--gif" in result.stdout


def test_intro_animation_does_not_hardcode_release_version_labels():
    repo_root = Path(__file__).resolve().parents[1]
    animation_files = [
        repo_root / "docs" / "assets" / "three-board-support-video" / "index.html",
        repo_root / "docs" / "assets" / "three-board-support-video" / "video.jsx",
        repo_root / "docs" / "assets" / "three-board-support-video-en" / "index.html",
        repo_root / "docs" / "assets" / "three-board-support-video-en" / "video.jsx",
    ]

    for animation_file in animation_files:
        text = animation_file.read_text(encoding="utf-8")
        release_labels = re.findall(r"v\d+\.\d+(?:\.\d+)?", text)
        assert release_labels == [], (animation_file, release_labels)


def test_intro_animation_embedded_sources_are_current():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "sync_intro_animation_sources.py"),
            "--check",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_intro_animation_uses_all_four_current_handbook_samples():
    repo_root = Path(__file__).resolve().parents[1]
    asset_root = repo_root / "docs" / "assets"
    sample_names = [
        "v060-oxfordaqa-biology-p12.jpg",
        "v060-oxfordaqa-biology-p21.jpg",
        "v060-oxfordaqa-biology-p28.jpg",
        "v060-caie-physics-p10.jpg",
        "v060-caie-physics-p25.jpg",
        "v060-caie-physics-p30.jpg",
        "v060-ap-chemistry-p11.jpg",
        "v060-ap-chemistry-p43.jpg",
        "v060-ap-chemistry-p91.jpg",
        "v060-edexcel-mathematics-p52.jpg",
        "v060-edexcel-mathematics-p74.jpg",
        "v060-edexcel-mathematics-p99.jpg",
    ]
    video_files = [
        asset_root / "three-board-support-video" / "video.jsx",
        asset_root / "three-board-support-video-en" / "video.jsx",
    ]

    for sample_name in sample_names:
        assert (asset_root / sample_name).is_file()
        for video_file in video_files:
            assert sample_name in video_file.read_text(encoding="utf-8")


@pytest.mark.skip(reason="Test needs update after architecture refactor.")
def test_public_repo_does_not_ship_built_in_image_router():
    repo_root = Path(__file__).resolve().parents[1]
    router_scripts = [
        path.name
        for path in (repo_root / "scripts").glob("*.py")
        if "router" in path.name and "image" in path.name
    ]
    assert router_scripts == []

    skill_text = (repo_root / "skill" / "SKILL.md").read_text(encoding="utf-8")
    assert "does not include a fixed built-in image-generation router" in skill_text
    assert "That does not mean image work must be manual" in skill_text
    assert "scripts/import_infographic_assets.py" in skill_text


@pytest.mark.skip(reason="Test needs update after architecture refactor.")
def test_skill_instructions_include_required_preflight_choices():
    skill_path = Path(__file__).resolve().parents[1] / "skill" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "name: igcse-a-level-revision-guide" in text
    assert "description:" in text
    assert "Subject choice" in text
    assert "Term-support language" in text
    assert "Exam year when needed" in text
    assert "Explanation style" in text
    assert "Do not ask the user to choose an image model before the base guide is generated" in text
    assert "how many complex infographic" in text
    assert "pending visual jobs" in text
    assert "handbook body, worked examples, labels, and" in text
    assert "30-50 item professional glossary" in text
    assert "Do not generate a fully translated handbook body" in text


def test_skill_blocks_until_external_image_capability_is_confirmed():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / "skill" / "SKILL.md").read_text(encoding="utf-8")
    agent_text = (repo_root / "skill" / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
    image_guide = (repo_root / "docs" / "IMAGE_MODEL_GUIDE.md").read_text(
        encoding="utf-8"
    )
    prompt_records = json.loads(
        (repo_root / "skill" / "test-prompts.json").read_text(encoding="utf-8")
    )

    required_question = "provide or enable an external image-generation Skill or tool"
    assert required_question in skill_text
    assert "This is a blocking question" in skill_text
    assert "do not infer" in skill_text.lower()
    assert "Do not silently select local generation" in skill_text
    assert "keeps the run at preflight" in skill_text
    assert required_question in agent_text
    assert required_question in image_guide
    handbook_prompts = {
        record["id"]: record["expected"]
        for record in prompt_records
        if record["id"] in {"aqa-accounting-zh", "edexcel-ambiguous-subject", "caie-exam-year"}
    }
    assert len(handbook_prompts) == 3
    assert all(required_question in expected for expected in handbook_prompts.values())


def test_public_docs_explain_delivery_matrix_and_final_review():
    readme = Path("README.md").read_text(encoding="utf-8")
    chinese_readme = Path("README.zh-CN.md").read_text(encoding="utf-8")
    operations = Path("docs/PROJECT_OPERATIONS.md").read_text(encoding="utf-8")

    for text in [readme, operations]:
        lowered = text.lower()
        assert "delivery matrix" in lowered
        assert "final-review-packet.json" in lowered
        assert "candidate routes" in lowered

    assert "交付矩阵" in chinese_readme
    assert "final-review-packet.json" in chinese_readme
    assert "候选路线" in chinese_readme


def test_public_skill_and_docs_state_the_automatic_acquisition_boundary():
    root_skill = Path("SKILL.md").read_text(encoding="utf-8")
    packaged_skill = Path("skill/SKILL.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    chinese_readme = Path("README.zh-CN.md").read_text(encoding="utf-8")

    for text in (root_skill, packaged_skill, readme):
        normalized = " ".join(text.split())
        assert "AQA, Edexcel, and CAIE" in normalized
        assert "College Board AP" in normalized
        assert "cannot use automatic acquisition" in normalized
        assert "unknown compatibility errors" in normalized

    assert "AQA、Edexcel、CAIE" in chinese_readme
    assert "College Board AP" in chinese_readme
    assert "不能使用自动获取功能" in chinese_readme
    assert "未知" in chinese_readme and "兼容" in chinese_readme


def test_release_checklist_requires_matrix_review_and_visual_job_ids():
    text = Path("docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")

    assert "delivery matrix" in text.lower()
    assert "python -m intl_exam_guide review --out <sample-output>" in text
    assert "images/infographic_jobs.md" in text
    assert "visual IDs need generation/review" in text


def run_verify(outputs: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_release_samples.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--legacy-outputs",
            "--outputs-root",
            str(outputs),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_key_scan(root: Path) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "scan_for_raw_keys.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_import(output_dir: Path, asset_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "import_infographic_assets.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(output_dir),
            "--asset-dir",
            str(asset_dir),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def run_render_intro_help() -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "render_intro_animation.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--help",
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def write_sample_outputs(outputs: Path, completed: bool) -> None:
    for sample, (topics, practice_cards, infographics) in SAMPLES.items():
        sample_dir = outputs / sample
        images_dir = sample_dir / "images"
        images_dir.mkdir(parents=True)

        (sample_dir / "run-options.json").write_text(
            json.dumps({"output_language": "en"}, indent=2),
            encoding="utf-8",
        )
        (sample_dir / "validation.json").write_text(
            json.dumps(
                {
                    "review_summary": {
                        "topics": topics,
                        "practice_cards": practice_cards,
                    },
                    "delivery_status": "ready" if completed else "draft_needs_image_review",
                    "delivery_state": "final-ready" if completed else "draft",
                    "issues": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        if completed:
            (sample_dir / "delivery-contract.json").write_text(
                json.dumps(
                    {
                        "schema_version": "v0.4-core-mvp",
                        "delivery_state": "final-ready",
                        "course_spec": {"title": sample},
                        "learning_units": [],
                        "pedagogical_units": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (sample_dir / "final-review-packet.json").write_text(
                json.dumps(
                    {
                        "machine_validation": {"delivery_status": "ready"},
                        "agent_self_review": {"must_not_present_as_final": False},
                        "product_review_evidence": {
                            "complete": True,
                            "file": "agent-product-review.json",
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        manifest = []
        html_images = []
        for index in range(1, infographics + 1):
            if completed:
                filename = f"visual_{index:03d}.png"
                (images_dir / filename).write_bytes(b"fake-png")
                status = "reviewed-generated"
                html_images.append(f'<img src="images/{filename}" alt="visual {index}">')
            else:
                filename = None
                status = "external-generation-required"
            manifest.append(
                {
                    "id": f"visual_{index:03d}",
                    "complexity": "infographic",
                    "asset_status": status,
                    "file": filename,
                }
            )
        (images_dir / "visual_manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        pending = "" if completed else "<section>Infographic Pending</section>"
        html = f'<html lang="en"><body><h1>{sample}</h1>{"".join(html_images)}{pending}</body></html>'
        (sample_dir / "guide.html").write_text(html, encoding="utf-8")
        if completed:
            (sample_dir / "agent-product-review.json").write_text(
                json.dumps(
                    {
                        "schema_version": "v0.6-llm-html-review",
                        "reviewer_type": "llm",
                        "html_opened_and_visually_inspected": True,
                        "reviewed_html_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
                        "review_iteration": 1,
                        "html_review_passed": True,
                        "all_topics_reviewed": True,
                        "topic_review_count": topics,
                        "reviewed_topic_titles": [
                            f"Topic {index}" for index in range(topics)
                        ],
                        "subject_factual_accuracy_checked": True,
                        "worked_examples_and_answers_checked": True,
                        "all_rendered_visuals_reviewed": True,
                        "rendered_visual_review_count": infographics,
                        "reviewed_visual_ids": [
                            f"visual_{index:03d}"
                            for index in range(1, infographics + 1)
                        ],
                        "visual_semantics_checked": True,
                        "layout_checked": True,
                        "syllabus_outline_compared": True,
                        "visuals_inspected": True,
                        "glossary_policy_checked": True,
                        "repair_loop_completed": True,
                        "issues_found": [],
                        "repairs_made": [],
                        "unresolved_fixable_issues": [],
                        "decision": "approved",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (sample_dir / "guide.pdf").write_bytes(b"%PDF-1.4\n")
