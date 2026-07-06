import pytest
import json
import io

import intl_exam_guide.cli as cli_module
from intl_exam_guide.cli import main
from intl_exam_guide.models import (
    AssessmentPaper,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
)
from intl_exam_guide.planning.guide_plan import (
    build_guide_plan,
    choose_visual_type,
    concrete_example,
    concrete_example_zh,
    zh_point_label,
    zh_visual_type,
)
from intl_exam_guide.planning.subject_profiles import resolve_subject_profile
from intl_exam_guide.rendering.handbook_package import write_handbook_package
from intl_exam_guide.rendering.html import render_cover, render_html, subject_display_name
from intl_exam_guide.rendering.output_names import default_handbook_stem, find_handbook_html
from intl_exam_guide.rendering.visual_assets import (
    has_renderable_infographic,
    scientific_vector_route,
)
from intl_exam_guide.providers.base import Link
from intl_exam_guide.validation.checks import review_summary, validate_plan


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_cli_json_output_survives_legacy_stdout_encoding(monkeypatch):
    buffer = io.BytesIO()
    legacy_stdout = io.TextIOWrapper(buffer, encoding="cp1252", errors="strict")
    monkeypatch.setattr(cli_module.sys, "stdout", legacy_stdout)

    cli_module.print_json_payload({"formula": "x − 1"})
    legacy_stdout.flush()

    assert b"\\u2212" in buffer.getvalue()


def sample_qualification() -> Qualification:
    return Qualification(
        title="International GCSE Chemistry Example (9202)",
        code="9202",
        qualification_type="international_gcse",
        subject_area="Chemistry",
        page_url="https://example.test/chemistry/",
        summary=["International GCSE linear qualification for international students."],
        topics=[
            Topic(
                title="Bonding and structure",
                points=[
                    "Describe ionic, covalent and metallic bonding",
                    "Explain how bonding affects properties",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Students should describe ionic, covalent and metallic bonding.",
                        matched_term="Bonding and structure",
                    )
                ],
            )
        ],
        assessments=[AssessmentPaper(title="Paper 1", details=["1 hour 30 minutes"])],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/chemistry/",
            specification_url="https://example.test/chemistry-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )


def sample_downloaded_qualification() -> Qualification:
    topic_specs = [
        ("3.1 - Source documents", ["source documents and books of prime entry"]),
        ("3.2 - Trial balance", ["prepare and explain the purpose of a trial balance"]),
        (
            "3.3 - Control accounts",
            ["prepare trade receivables and trade payables control accounts"],
        ),
        (
            "3.4 - Correction of errors",
            ["correct errors using journal entries and suspense accounts"],
        ),
        ("3.5 - Bank reconciliation", ["prepare a bank reconciliation statement"]),
        ("3.6 - Accounting ratios", ["calculate liquidity and profitability ratios"]),
    ]
    topics = []
    for index, (title, points) in enumerate(topic_specs, start=1):
        topics.append(
            Topic(
                title=title,
                points=points,
                source_snippets=[
                    SourceSnippet(
                        page=10 + index,
                        text=f"{title} {' '.join(points)}",
                        matched_term=title,
                    )
                ],
            )
        )
    return Qualification(
        title="International GCSE Accounting Example (9999)",
        code="9999",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=["International GCSE linear qualification for international students."],
        topics=topics,
        assessments=[
            AssessmentPaper(
                title="Paper 1",
                details=["1 hour 30 minutes"],
                source_snippets=[
                    SourceSnippet(
                        page=30, text="Paper 1 is 1 hour 30 minutes.", matched_term="Paper 1"
                    )
                ],
            )
        ],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/accounting/",
            specification_url="https://example.test/accounting-spec.pdf",
            specification_sha256="abc",
            specification_path="source/spec.pdf",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )


def test_default_handbook_name_uses_board_level_subject_time():
    qualification = Qualification(
        title="International GCSE Mathematics (9260)",
        code="9260",
        qualification_type="international_gcse",
        subject_area="Mathematics",
        page_url="https://example.test/mathematics/",
        summary=[],
        topics=[],
        assessments=[],
        source=SourceRecord(provider="oxfordaqa", page_url="https://example.test/mathematics/"),
        audience_note="For international students.",
        provider="OxfordAQA",
    )

    assert (
        default_handbook_stem(qualification, "20260706-1430")
        == "oxfordaqa-igcse-mathematics-20260706-1430"
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_discover_cli_lists_subject_pages_offline(monkeypatch, capsys):
    class FakeProvider:
        def discover_subject_pages(self):
            return [
                Link(
                    text="Accounting",
                    href="https://example.test/accounting/",
                )
            ]

    monkeypatch.setattr(cli_module, "get_provider", lambda _name: FakeProvider())

    result = cli_module.main(["discover", "--provider", "fake"])

    assert result == 0
    assert "Accounting\thttps://example.test/accounting/" in capsys.readouterr().out


def test_generate_cli_runs_provider_chain_offline(monkeypatch, tmp_path):
    calls = []

    class FakeProvider:
        def find_qualification(self, query, level=None, exam_year=None):
            calls.append(("find", query, level, exam_year))
            return Link(text="Accounting", href="https://example.test/accounting/")

        def parse_qualification(self, page_url, level=None, exam_year=None):
            calls.append(("parse", page_url, level, exam_year))
            return sample_downloaded_qualification()

        def apply_listing_metadata(self, qualification, link):
            calls.append(("metadata", link.text))
            qualification.source.listing_subject = link.text
            return qualification

        def download_specification(self, qualification, output_dir, exam_year=None):
            calls.append(("download", str(output_dir.name), exam_year))
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "spec.pdf").write_bytes(b"%PDF-1.4\n")
            return qualification

    monkeypatch.setattr(cli_module, "get_provider", lambda _name: FakeProvider())
    output_dir = tmp_path / "generated"

    result = cli_module.main(
        [
            "generate",
            "--provider",
            "fake",
            "--query",
            "Accounting 9999",
            "--level",
            "igcse",
            "--out",
            str(output_dir),
        ]
    )

    assert result == 0
    assert calls == [
        ("find", "Accounting 9999", "igcse", None),
        ("parse", "https://example.test/accounting/", "igcse", None),
        ("metadata", "Accounting"),
        ("download", "source", None),
    ]
    assert (output_dir / "qualification.json").exists()
    assert (output_dir / "syllabus-evidence.json").exists()
    assert not (output_dir / "guide.html").exists()
    assert not (output_dir / "guide-plan.json").exists()
    assert not (output_dir / "validation.json").exists()


def test_extract_evidence_cli_writes_evidence_only(monkeypatch, tmp_path):
    calls = []

    class FakeProvider:
        def find_qualification(self, query, level=None, exam_year=None):
            calls.append(("find", query, level, exam_year))
            return Link(text="Accounting", href="https://example.test/accounting/")

        def parse_qualification(self, page_url, level=None, exam_year=None):
            calls.append(("parse", page_url, level, exam_year))
            return sample_downloaded_qualification()

        def apply_listing_metadata(self, qualification, link):
            calls.append(("metadata", link.text))
            return qualification

        def download_specification(self, qualification, output_dir, exam_year=None):
            calls.append(("download", str(output_dir.name), exam_year))
            output_dir.mkdir(parents=True, exist_ok=True)
            text_path = output_dir / "specification.txt"
            text_path.write_text(
                "--- Page 1 ---\nStudents should explain source documents.\n"
                "--- Page 2 ---\nStudents should prepare a trial balance.",
                encoding="utf-8",
            )
            qualification.source.extracted_text_path = str(text_path)
            qualification.source.specification_path = str(output_dir / "specification.pdf")
            return qualification

    monkeypatch.setattr(cli_module, "get_provider", lambda _name: FakeProvider())
    output_dir = tmp_path / "evidence"

    result = cli_module.main(
        [
            "extract-evidence",
            "--provider",
            "fake",
            "--query",
            "Accounting 9999",
            "--level",
            "igcse",
            "--exam-year",
            "2027",
            "--out",
            str(output_dir),
        ]
    )

    assert result == 0
    assert calls == [
        ("find", "Accounting 9999", "igcse", "2027"),
        ("parse", "https://example.test/accounting/", "igcse", "2027"),
        ("metadata", "Accounting"),
        ("download", "source", "2027"),
    ]
    evidence = json.loads((output_dir / "syllabus-evidence.json").read_text(encoding="utf-8"))
    qualification = json.loads((output_dir / "qualification.json").read_text(encoding="utf-8"))
    assert evidence["course"]["title"] == "International GCSE Accounting Example (9999)"
    assert [page["page"] for page in evidence["pages"]] == [1, 2]
    assert "source documents" in evidence["pages"][0]["text"]
    assert qualification["source"]["extracted_text_path"].endswith("specification.txt")
    assert not (output_dir / "guide.html").exists()
    assert not (output_dir / "guide-plan.json").exists()
    assert not (output_dir / "validation.json").exists()


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_demo_cli_generates_offline_guide(tmp_path):
    output_dir = tmp_path / "demo"
    result = main(
        [
            "demo",
            "--out",
            str(output_dir),
            "--image-provider",
            "deterministic-svg",
            "--explanation-style",
            "friendly",
            "--language",
            "en",
            "--skip-pdf",
        ]
    )
    assert result == 1
    handbook_html = find_handbook_html(output_dir)
    assert handbook_html.exists()
    assert (output_dir / "guide-plan.json").exists()
    assert (output_dir / "qualification.json").exists()
    assert (output_dir / "run-options.json").exists()
    assert (output_dir / "delivery-contract.json").exists()
    assert not (output_dir / "agent-orchestration.json").exists()
    assert (output_dir / "handbook-package.json").exists()
    assert (output_dir / "sections" / "00_css.txt").exists()
    assert (output_dir / "sections" / "03_topic_navigation.txt").exists()
    assert (output_dir / "sections" / "04_topic_guides_and_examples.txt").exists()
    assert (output_dir / "images" / "visual_manifest.json").exists()
    assert len(list((output_dir / "images").glob("*.svg"))) == 2
    html = handbook_html.read_text(encoding="utf-8")
    assert html.count('class="topic-diagram"') == 0
    assert html.count('class="visual-example"') == 2
    assert "Concept Map" not in html
    assert "Visual Worked Example" in html
    assert "Review Check" not in html
    assert 'data-review-state="draft"' not in html
    assert "How to Study" in html
    assert "Guide Setup" in html
    assert "Study route" not in html
    assert "key idea -> worked example -> error review" not in html
    assert "图文解释" not in html
    assert "Worked Example" in html
    assert "Solution" in html
    assert "Check" in html
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["qualification"] == "International GCSE Demo Science (9000)"
    assert validation["review_summary"]["image_provider"] == "deterministic-svg"
    assert validation["review_summary"]["explanation_style"] == "friendly"
    assert validation["review_summary"]["output_language"] == "en"
    assert validation["review_summary"]["visual_briefs"] == 2
    assert validation["review_summary"]["visual_examples_in_html"] == 2
    assert validation["review_summary"]["section_files"] == 7
    assert validation["review_summary"]["image_files"] == 2
    assert validation["review_summary"]["has_visual_manifest"] is True
    assert validation["review_summary"]["has_package_manifest"] is True
    assert validation["review_summary"]["concept_jobs"] == 3
    assert validation["review_summary"]["pending_concept_explanations"] == 3
    assert validation["delivery_status"] == "blocked_errors"
    assert validation["delivery_state"] == "blocked"
    # CLI demo runs without a real LLM Analyst pass; the syllabus outline is a
    # CLI fallback placeholder. Final-ready requires outline-source:llm-analyst.
    assert any("syllabus_outline_analyst" in issue["message"] for issue in validation["issues"])
    delivery_contract = json.loads(
        (output_dir / "delivery-contract.json").read_text(encoding="utf-8")
    )
    assert delivery_contract["delivery_state"] == "blocked"
    assert delivery_contract["course_spec"]["title"] == validation["qualification"]
    assert "agent_orchestration" not in validation
    assert "agent_orchestration" not in delivery_contract
    assert delivery_contract["workflow"]["mode"] == "llm-owned-lightweight-workflow"
    assert [role["role_id"] for role in delivery_contract["workflow"]["roles"]] == [
        "analyst",
        "writer",
        "reviewer",
    ]
    assert validation["delivery_status"] == "blocked_errors"
    assert validation["delivery_state"] == "blocked"
    assert any(
        "Python-generated" in issue["message"] for issue in validation["issues"]
    )
    assert any(
        "topic concept explanations still need LLM/Agent review" in issue["message"]
        for issue in validation["issues"]
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_demo_cli_generates_english_guide_with_chinese_term_glossary(tmp_path):
    output_dir = tmp_path / "demo-zh"
    result = main(
        [
            "demo",
            "--out",
            str(output_dir),
            "--image-provider",
            "deterministic-svg",
            "--explanation-style",
            "friendly",
            "--language",
            "zh-CN",
            "--skip-pdf",
        ]
    )
    assert result == 1
    html = find_handbook_html(output_dir).read_text(encoding="utf-8")
    assert 'lang="en"' in html
    assert "How to Study" in html
    assert "Study Roadmap" in html
    assert "Professional Term Glossary" in html
    assert "Simplified Chinese" in html
    assert "定义" in html
    assert "学习路径" not in html
    assert "核心概念 -> 例题 -> 错题回看" not in html
    assert "Quick Navigation" in html
    assert 'href="#topic-1"' in html
    assert 'id="topic-1"' in html
    assert "Visual Worked Example" in html
    assert "Worked Example" in html
    assert "Solution" in html
    assert "Check" in html
    assert "Command:" in html
    assert "Can explain" not in html
    assert "Review Check" not in html
    assert 'data-review-state="draft"' not in html
    assert "知识单元 1" not in html
    assert "大纲点 1" not in html
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["review_summary"]["output_language"] == "zh-CN"
    assert validation["review_summary"]["concept_jobs"] == 3
    assert validation["review_summary"]["pending_concept_explanations"] == 3
    assert validation["delivery_status"] == "blocked_errors"
    assert validation["delivery_state"] == "blocked"
    assert any(
        "Python-generated" in issue["message"] for issue in validation["issues"]
    )
    assert any(
        "topic concept explanations still need LLM/Agent review" in issue["message"]
        for issue in validation["issues"]
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_cover_is_course_identity_only():
    qualification = sample_qualification()
    qualification.provider = "OxfordAQA"
    qualification.source.provider = "OxfordAQA"
    html = render_cover(
        qualification,
        build_guide_plan(
            qualification, output_language="en", explanation_style="friendly"
        ).run_options,
    )

    assert "AQA" in html
    assert "Oxford International AQA Examinations" in html
    assert "Chemistry Example" in html
    assert "9202" in html
    assert "Specification / syllabus version" in html
    assert "Knowledge units" not in html
    assert "Assessment papers" not in html
    assert "Style" not in html
    assert "How to Study" not in html


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_cover_keeps_unknown_provider_neutral():
    qualification = sample_qualification()
    qualification.provider = None
    qualification.source.provider = "synthetic-demo"
    qualification.source.specification_url = "https://example.test/synthetic-spec.pdf"
    html = render_cover(
        qualification,
        build_guide_plan(
            qualification, output_language="en", explanation_style="friendly"
        ).run_options,
    )

    assert "Unspecified exam board" in html
    assert "board-neutral" in html
    assert "Oxford International AQA Examinations" not in html
    assert "board-aqa" not in html


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_cover_uses_provider_version_fields():
    qualification = sample_qualification()
    qualification.provider = "cambridge"
    qualification.source.provider = "cambridge"
    qualification.qualification_family = "Cambridge IGCSE"
    qualification.source.issue_version = "2027-2029 syllabus"
    qualification.source.selected_exam_year = "2027"
    html = render_cover(
        qualification,
        build_guide_plan(
            qualification, output_language="en", explanation_style="friendly"
        ).run_options,
    )

    assert "CAIE" in html
    assert "Cambridge International Education" in html
    assert "Cambridge IGCSE" in html
    assert "2027-2029 syllabus" in html
    assert "2027" in html


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_generated_infographic_assets_are_preserved_and_rendered(tmp_path):
    output_dir = tmp_path / "chemistry"
    qualification = Qualification(
        title="International GCSE Chemistry Example (9202)",
        code="9202",
        qualification_type="international_gcse",
        subject_area="Chemistry",
        page_url="https://example.test/chemistry/",
        summary=["International GCSE linear qualification for international students."],
        topics=[
            Topic(
                title="Bonding and structure",
                points=[
                    "Describe ionic, covalent and metallic bonding",
                    "Explain how bonding affects properties",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text="Students should describe ionic, covalent and metallic bonding and explain how bonding affects properties.",
                        matched_term="Bonding and structure",
                    )
                ],
            )
        ],
        assessments=[
            AssessmentPaper(
                title="Paper 1",
                details=["1 hour 30 minutes", "90 marks", "50% of qualification"],
            )
        ],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/chemistry/",
            specification_url="https://example.test/chemistry-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )
    plan = build_guide_plan(
        qualification,
        image_provider="gpt-image-2",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    # CLI-fallback-style evidence package for unit tests: simulate the
    # syllabus-evidence.json/syllabus-outline.json writes that the real CLI does.
    qualification = Qualification(
        title=plan.qualification.title,
        code=plan.qualification.code,
        qualification_type=plan.qualification.qualification_type,
        subject_area=plan.qualification.subject_area,
        page_url=plan.qualification.page_url,
        summary=plan.qualification.summary,
        topics=plan.qualification.topics,
        assessments=plan.qualification.assessments,
        source=plan.qualification.source,
        audience_note=plan.qualification.audience_note,
        provider=plan.qualification.provider,
        qualification_family=plan.qualification.qualification_family,
        selected_exam_year=plan.qualification.selected_exam_year,
        route_tags=[*plan.qualification.route_tags, "outline-source:cli-fallback"],
        command_words=plan.qualification.command_words,
        assessment_objectives=plan.qualification.assessment_objectives,
    )
    plan = type(plan)(
        qualification=qualification,
        run_options=plan.run_options,
        topic_guides=plan.topic_guides,
        practice_items=plan.practice_items,
        visual_briefs=plan.visual_briefs,
        diagram_briefs=plan.diagram_briefs,
        revision_stages=plan.revision_stages,
    )
    from intl_exam_guide.planning.syllabus_outline import (
        write_syllabus_evidence,
        write_syllabus_outline,
    )

    write_syllabus_evidence(plan.qualification, output_dir, [])
    write_syllabus_outline(
        output_dir,
        {
            "schema_version": "v0.5-cli-fallback-outline",
            "topics": [
                {
                    "title": topic.title,
                    "exam_points": list(topic.points),
                    "source_snippets": [
                        {"page": s.page, "text": s.text, "matched_term": s.matched_term}
                        for s in topic.source_snippets
                    ],
                }
                for topic in plan.qualification.topics
            ],
        },
    )
    assert plan.run_options.image_provider == "prompt-queue"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run-options.json").write_text(
        json.dumps(plan.run_options.__dict__, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_handbook_package(plan, output_dir)
    images_dir = output_dir / "images"
    manifest_path = images_dir / "visual_manifest.json"
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_payload["schema_version"] == 2
    manifest = manifest_payload["visuals"]
    assert manifest[0]["asset_status"] == "external-generation-required"
    assert manifest[0]["file"] is None

    render_html(plan, output_dir / "guide.html", manifest_path)
    fallback_html = (output_dir / "guide.html").read_text(encoding="utf-8")
    assert "Infographic Pending" in fallback_html
    assert "Infographic Queue" not in fallback_html
    assert "Prompt queue" not in fallback_html
    assert "SVG Fallback - Review Needed" not in fallback_html
    fallback_summary = review_summary(plan, output_dir=output_dir)
    assert fallback_summary["generated_infographic_assets"] == 0
    assert fallback_summary["svg_fallback_assets"] == 0
    assert fallback_summary["pending_infographic_assets"] == 1
    fallback_warnings = [issue.message for issue in validate_plan(plan, output_dir=output_dir)]
    assert any("1 infographic briefs are queued" in message for message in fallback_warnings)

    image_name = "visual_001_bonding-infographic.png"
    (images_dir / image_name).write_bytes(b"fake-png")
    manifest[0]["file"] = image_name
    manifest[0]["asset_status"] = "generated"
    manifest_payload["visuals"] = manifest
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_handbook_package(plan, output_dir)
    render_html(plan, output_dir / "guide.html", manifest_path)

    html = (output_dir / "guide.html").read_text(encoding="utf-8")
    assert f'src="images/{image_name}"' in html
    assert "Generated Infographic" in html
    assert "Infographic Queue" not in html
    generated_summary = review_summary(plan, output_dir=output_dir)
    assert generated_summary["generated_infographic_assets"] == 1
    assert generated_summary["svg_fallback_assets"] == 0
    assert generated_summary["pending_infographic_assets"] == 0
    assert not [
        issue for issue in validate_plan(plan, output_dir=output_dir) if issue.severity == "error"
    ]


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_recommended_image_labels_are_not_treated_as_callable_providers():
    qualification = sample_qualification()

    for label in ["gpt-image-2", "qwen-image-pro", "sensenova-u1-fast"]:
        plan = build_guide_plan(
            qualification,
            image_provider=label,
            explanation_style="friendly",
            output_language="en",
            requested_subject="chemistry",
        )

        assert plan.run_options.image_provider == "prompt-queue"
        assert all(
            brief.image_provider in {"deterministic-svg", "external-generation-required"}
            for brief in plan.visual_briefs
        )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_sensenova_generated_assets_are_renderable_infographics(tmp_path):
    image_path = tmp_path / "visual_001_accounting.png"
    image_path.write_bytes(b"fake-png")
    entry = {
        "file": image_path.name,
        "asset_status": "sensenova-generated",
        "complexity": "infographic",
    }

    assert has_renderable_infographic(entry, tmp_path)


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_svg_safe_charts_are_marked_as_scientific_vector_fallbacks():
    assert (
        scientific_vector_route("statistics chart and probability visual")
        == "scripted-scientific-vector"
    )
    assert (
        scientific_vector_route("reaction energy profile diagram") == "scripted-scientific-vector"
    )
    assert scientific_vector_route("text explanation with concept map only") == "hand-authored-svg"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_custom_image_provider_requires_set_environment_variable(monkeypatch):
    qualification = sample_qualification()
    monkeypatch.delenv("CUSTOM_IMAGE_KEY", raising=False)

    plan = build_guide_plan(
        qualification,
        image_provider="custom",
        image_model="school-image-model",
        image_endpoint_url="https://images.example.test/v1/images/generations",
        image_api_key_env="CUSTOM_IMAGE_KEY",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )

    assert plan.run_options.image_provider == "prompt-queue"

    monkeypatch.setenv("CUSTOM_IMAGE_KEY", "test-key")
    plan = build_guide_plan(
        qualification,
        image_provider="custom",
        image_model="school-image-model",
        image_endpoint_url="https://images.example.test/v1/images/generations",
        image_api_key_env="CUSTOM_IMAGE_KEY",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )

    assert plan.run_options.image_provider == "custom"
    assert not [issue for issue in validate_plan(plan) if issue.severity == "error"]


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_term_support_mode_keeps_english_body_and_traceable_source_snippets(tmp_path):
    output_dir = tmp_path / "zh-guide"
    raw_source = "Students should describe ionic, covalent and metallic bonding and explain how bonding affects properties."
    qualification = Qualification(
        title="International GCSE Chemistry Example (9202)",
        code="9202",
        qualification_type="international_gcse",
        subject_area="Chemistry",
        page_url="https://example.test/chemistry/",
        summary=["International GCSE linear qualification for international students."],
        topics=[
            Topic(
                title="Bonding and structure",
                points=[
                    "Describe ionic, covalent and metallic bonding",
                    "Explain how bonding affects properties",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=12,
                        text=raw_source,
                        matched_term="Bonding and structure",
                    )
                ],
            )
        ],
        assessments=[
            AssessmentPaper(
                title="Paper 1",
                details=["1 hour 30 minutes", "90 marks", "50% of qualification"],
            )
        ],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/chemistry/",
            specification_url="https://example.test/chemistry-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )
    plan = build_guide_plan(
        qualification,
        image_provider="gpt-image-2",
        explanation_style="friendly",
        output_language="zh-CN",
        requested_subject="chemistry",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_handbook_package(plan, output_dir)
    render_html(plan, output_dir / "guide.html", output_dir / "images" / "visual_manifest.json")

    html = (output_dir / "guide.html").read_text(encoding="utf-8")
    assert raw_source not in html
    assert "describe ionic, covalent and metallic bonding" in html
    assert '<html lang="en">' in html
    assert "Professional Term Glossary" in html
    assert "中文 / English" not in html


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_term_support_language_visual_prompts_stay_english():
    qualification = Qualification(
        title="International GCSE Economics Example (9214)",
        code="9214",
        qualification_type="international_gcse",
        subject_area="Economics",
        page_url="https://example.test/economics/",
        summary=["International GCSE linear qualification for international students."],
        topics=[
            Topic(
                title="3.1.3.1 - Demand for goods and services",
                points=[
                    "Factors which determine demand",
                    "Movement along a demand curve and shifts of the demand curve",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=20,
                        text="Students should understand factors which determine demand.",
                        matched_term="Demand for goods and services",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/economics/",
            specification_url="https://example.test/economics-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )
    plan = build_guide_plan(
        qualification,
        image_provider="gpt-image-2",
        explanation_style="friendly",
        output_language="zh-CN",
        requested_subject="economics",
    )

    prompt = plan.visual_briefs[0].prompt
    assert "Create a polished educational worksheet infographic" in prompt
    assert "large topic banner" in prompt
    assert "Quick Q&A or practice box" in prompt
    assert "Topic: economics and business" in prompt
    assert "Short labels may include" in prompt
    assert "Factors which determine demand" in prompt
    assert "制作一张中文学习信息图" not in prompt
    assert "International" not in prompt
    assert "GCSE" not in prompt


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_subject_specific_examples_do_not_cross_subjects():
    maths_solution_question, _, _, _ = concrete_example(
        Topic(
            title="A4 - Notation and manipulation",
            points=["solve linear equations and check the solution"],
        ),
        "solve linear equations and check the solution",
        1,
        "Mathematics",
    )
    assert "neutralisation" not in maths_solution_question.lower()
    assert "hydrochloric" not in maths_solution_question.lower()
    assert "expand" in maths_solution_question.lower() or "line" in maths_solution_question.lower()

    equilibrium_price_question, _, _, _ = concrete_example(
        Topic(
            title="3.1.3.3 - Equilibrium price",
            points=["equilibrium price is determined by demand and supply"],
        ),
        "equilibrium price is determined by demand and supply",
        1,
        "Economics",
    )
    assert "reaction" not in equilibrium_price_question.lower()
    assert "drought" in equilibrium_price_question.lower()
    assert "equilibrium price" in equilibrium_price_question.lower()

    chemistry_question, _, _, _ = concrete_example(
        Topic(
            title="3.1.1 - Solids, liquids and gases",
            points=["Matter can be classified in terms of the three states of matter."],
        ),
        "Matter can be classified in terms of the three states of matter.",
        0,
    )
    assert "diffusion" in chemistry_question.lower()
    assert "chromatography" not in chemistry_question.lower()

    nano_question, _, _, _ = concrete_example(
        Topic(
            title="3.2.4 - Nanoparticles C",
            points=["Nanoparticles have a high surface area to volume ratio."],
        ),
        "Nanoparticles have a high surface area to volume ratio.",
        0,
    )
    assert "surface area" in nano_question.lower()
    assert "ratio 2:5" not in nano_question.lower()

    concentration_question, _, _, _ = concrete_example(
        Topic(
            title="3.6.4 - molar concentrations",
            points=["Concentration is related to number of moles and volume of solution."],
        ),
        "Concentration is related to number of moles and volume of solution.",
        0,
    )
    assert "concentration" in concentration_question.lower()
    assert "ratio 2:5" not in concentration_question.lower()

    carbon_question, _, _, _ = concrete_example(
        Topic(
            title="3.2.3 - Structure and bonding of carbon",
            points=["Diamond and graphite have different structures and properties."],
        ),
        "Diamond and graphite have different structures and properties.",
        0,
    )
    assert "diamond" in carbon_question.lower()
    assert "graphite" in carbon_question.lower()

    economics_question, _, _, _ = concrete_example(
        Topic(
            title="3.1.1.2 - The factors of production",
            points=["The factors of production"],
        ),
        "The factors of production",
        0,
    )
    assert "bakery" in economics_question.lower()
    assert "factor of production" in economics_question.lower()

    specialisation_question, _, _, _ = concrete_example(
        Topic(
            title="3.1.2.3 - Specialisation, division of labour, and exchange",
            points=["The benefits and costs of specialisation and division of labour."],
        ),
        "The benefits and costs of specialisation and division of labour.",
        0,
    )
    assert "division of labour" in specialisation_question.lower()
    assert "bakery uses wheat" not in specialisation_question.lower()


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_subject_profiles_are_broad_not_per_course_definitions():
    maths_profile = resolve_subject_profile(
        "Mathematics",
        Topic(title="N4 - Structure and calculation", points=[]),
        "sets, factors and multiples",
    )
    economics_profile = resolve_subject_profile(
        "Economics",
        Topic(title="3.1.3.3 - Equilibrium price", points=[]),
        "demand supply market price",
    )
    generic_profile = resolve_subject_profile(
        "Art and Design",
        Topic(title="2.1 - Portfolio development", points=[]),
        "portfolio annotation and creative process",
    )
    accounting_profile = resolve_subject_profile(
        "Accounting",
        Topic(title="3.1.2 - Books of prime entry", points=[]),
        "source documents ledger accounts double entry",
    )

    assert maths_profile.family == "mathematics"
    assert economics_profile.family == "social-science"
    assert accounting_profile.family == "business-finance"
    assert accounting_profile.example_domain == "accounting"
    assert generic_profile.example_domain == "generic"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_accounting_examples_do_not_borrow_mathematics_templates():
    question, _, steps, _ = concrete_example(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    combined = " ".join([question, *steps]).lower()
    assert "mean and range" not in combined
    assert "median and range" not in combined
    assert "purchase invoice" in combined or "sales invoice" in combined
    assert "ledger" in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_accounting_chinese_examples_translate_visible_terms():
    question, _, steps, checkpoints = concrete_example_zh(
        Topic(
            title="3.1.2 - Sources and recording of data",
            points=["Source documents are purchase invoices and sales invoices."],
        ),
        "Source documents are purchase invoices and sales invoices.",
        0,
        "Accounting",
    )
    combined = " ".join([question, *steps, *checkpoints])

    assert "购货发票" in combined
    assert "原始凭证" in combined
    assert "分类账" in combined
    assert "purchase invoice" not in combined
    assert "purchases journal" not in combined
    assert "ledger accounts" not in combined
    assert "source document" not in combined
    assert "book of prime entry" not in combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_practice_variants_are_not_duplicate_questions():
    plan = build_guide_plan(
        sample_qualification(),
        questions_per_topic=2,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="zh-CN",
        requested_subject="chemistry",
    )

    questions = [item.question for item in plan.practice_items]

    assert len(questions) == 2
    assert len(set(questions)) == 2


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_chinese_point_labels_do_not_use_generic_syllabus_placeholder():
    label = zh_point_label("Source documents are purchase invoices and sales invoices.", 0)

    assert "官方大纲要求" not in label
    assert "凭证" in label


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_validation_rejects_chinese_syllabus_placeholder_text():
    plan = build_guide_plan(
        sample_qualification(),
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="zh-CN",
        requested_subject="chemistry",
    )
    plan.topic_guides[0].essence = "本单元第 1 个细分要求"
    plan.practice_items[0].question = "围绕“知识点 1”完成一道原创练习。"

    issues = validate_plan(plan)

    assert any(
        issue.severity == "error" and "non-English body text" in issue.message for issue in issues
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_validation_rejects_duplicate_practice_questions_per_topic():
    plan = build_guide_plan(
        sample_qualification(),
        questions_per_topic=2,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )
    plan.practice_items[1].question = plan.practice_items[0].question

    issues = validate_plan(plan)

    assert any(
        issue.severity == "error" and "repeat the same question" in issue.message
        for issue in issues
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_downloaded_specification_with_too_few_topics_is_an_error():
    qualification = sample_qualification()
    qualification.source.specification_path = "source/spec.pdf"

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )
    issues = validate_plan(plan)

    assert any(
        issue.severity == "error" and "Only 1 syllabus topics" in issue.message for issue in issues
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_downloaded_specification_with_generic_content_units_is_an_error():
    qualification = sample_qualification()
    qualification.source.specification_path = "source/spec.pdf"
    qualification.topics = [
        Topic(
            title=f"Content unit {index} - fallback",
            points=[f"fallback point {index}"],
            source_snippets=[
                SourceSnippet(
                    page=10 + index,
                    text=f"fallback point {index}",
                    matched_term="fallback",
                )
            ],
        )
        for index in range(1, 7)
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )
    issues = validate_plan(plan)

    assert any(
        issue.severity == "error" and "generic Content unit topics" in issue.message
        for issue in issues
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_downloaded_specification_without_assessments_is_an_error():
    qualification = sample_qualification()
    qualification.source.specification_path = "source/spec.pdf"
    qualification.assessments = []
    qualification.topics = [
        Topic(
            title=f"3.{index} - Specific topic",
            points=[f"specific point {index}"],
            source_snippets=[
                SourceSnippet(
                    page=10 + index,
                    text=f"specific point {index}",
                    matched_term="specific",
                )
            ],
        )
        for index in range(1, 7)
    ]

    plan = build_guide_plan(
        qualification,
        image_provider="prompt-queue",
        explanation_style="friendly",
        output_language="en",
        requested_subject="chemistry",
    )
    issues = validate_plan(plan)

    assert any(
        issue.severity == "error" and "No assessment papers were extracted" in issue.message
        for issue in issues
    )


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_accounting_subject_display_name_is_localized():
    qualification = Qualification(
        title="International GCSE Accounting (9215)",
        code="9215",
        qualification_type="international_gcse",
        subject_area="Accounting",
        page_url="https://example.test/accounting/",
        summary=["International GCSE linear qualification for international students."],
        topics=[],
        assessments=[],
        source=SourceRecord(provider="test", page_url="https://example.test/accounting/"),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )

    assert subject_display_name(qualification) == "会计学"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_unknown_subject_uses_generic_fallback_instead_of_cross_subject_templates():
    question, _, steps, _ = concrete_example(
        Topic(
            title="2.1 - Design solution and visual balance",
            points=["explore solutions, equilibrium and factors in a design brief"],
        ),
        "explore solutions, equilibrium and factors in a design brief",
        0,
        "Art and Design",
    )
    combined = " ".join([question, *steps]).lower()
    assert "hydrochloric" not in combined
    assert "neutralisation" not in combined
    assert "demand" not in combined
    assert "supply" not in combined
    assert "using only the syllabus point" in combined
    assert "relationship or boundary" in combined

    visual_type, complexity, _ = choose_visual_type(
        Topic(
            title="2.1 - Design solution and visual balance",
            points=["explore solutions, equilibrium and factors in a design brief"],
        ),
        ["explore solutions, equilibrium and factors in a design brief"],
    )
    assert complexity == "text-ok"
    assert visual_type == "text explanation with concept map only"


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_explicit_non_showcase_subjects_do_not_use_showcase_templates():
    art_topic = Topic(
        title="A1 - Portfolio solution and visual balance",
        points=["explore solutions, equilibrium, gas colour and factors in a design brief"],
    )
    art_profile = resolve_subject_profile(
        "Art and Design",
        art_topic,
        "explore solutions, equilibrium, gas colour and factors in a design brief",
    )
    assert art_profile.example_domain == "generic"

    visual_type, complexity, _ = choose_visual_type(
        art_topic,
        art_topic.points,
        "Art and Design",
    )
    assert complexity == "text-ok"
    assert visual_type == "text explanation with concept map only"

    question, _, steps, _ = concrete_example(
        art_topic,
        art_topic.points[0],
        0,
        "Art and Design",
    )
    combined = " ".join([question, *steps]).lower()
    assert "ratio 2:5" not in combined
    assert "reaction" not in combined
    assert "demand" not in combined

    zh_question, _, zh_steps, _ = concrete_example_zh(
        art_topic,
        art_topic.points[0],
        0,
        "Art and Design",
    )
    zh_combined = " ".join([zh_question, *zh_steps])
    assert "化学" not in zh_combined
    assert "经济" not in zh_combined
    assert "比例" not in zh_combined


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_full_plan_respects_arbitrary_subject_boundary():
    qualification = Qualification(
        title="International GCSE Physics Example",
        code="0000",
        qualification_type="international_gcse",
        subject_area="Physics",
        page_url="https://example.test/physics/",
        summary=["Example only."],
        topics=[
            Topic(
                title="3.1 - Gas pressure and equilibrium factors",
                points=["explain gas pressure using particles and factors affecting pressure"],
                source_snippets=[
                    SourceSnippet(
                        page=10,
                        text="Students should explain gas pressure and factors affecting pressure.",
                        matched_term="Gas pressure",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/physics/",
            specification_url="https://example.test/physics-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="Example only.",
    )
    plan = build_guide_plan(
        qualification,
        image_provider="gpt-image-2",
        explanation_style="friendly",
        output_language="en",
        requested_subject="physics",
    )

    practice_text = " ".join(
        [plan.practice_items[0].question, *plan.practice_items[0].public_solution_steps]
    ).lower()
    assert "limewater" not in practice_text
    assert "oxygen gas" not in practice_text
    assert "demand" not in practice_text
    assert not plan.visual_briefs


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_two_practice_items_for_same_topic_are_not_duplicates():
    qualification = Qualification(
        title="International GCSE Economics Example (9214)",
        code="9214",
        qualification_type="international_gcse",
        subject_area="Economics",
        page_url="https://example.test/economics/",
        summary=["International GCSE linear qualification for international students."],
        topics=[
            Topic(
                title="3.1.3.3 - Equilibrium price",
                points=[
                    "equilibrium price is determined by demand and supply",
                    "changes in supply and demand affect equilibrium price and quantity",
                ],
                source_snippets=[
                    SourceSnippet(
                        page=20,
                        text="Students should understand equilibrium price and demand and supply.",
                        matched_term="Equilibrium price",
                    )
                ],
            )
        ],
        assessments=[],
        source=SourceRecord(
            provider="test",
            page_url="https://example.test/economics/",
            specification_url="https://example.test/economics-spec.pdf",
            specification_sha256="abc",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )
    plan = build_guide_plan(
        qualification,
        questions_per_topic=2,
        image_provider="gpt-image-2",
        explanation_style="life",
        output_language="en",
        requested_subject="economics",
    )
    questions = [item.question for item in plan.practice_items]
    assert len(questions) == 2
    assert len(set(questions)) == 2
    assert all("reaction" not in question.lower() for question in questions)


@pytest.mark.skip(reason="Deprecated: Test relies on Python parser/routing. LLM now handles this.")
def test_visual_type_classifier_uses_subject_specific_infographics():
    set_visual, set_complexity, _ = choose_visual_type(
        Topic(
            title="N9 - Structure and calculation",
            points=["use language and notation of sets including n(A), union and intersection"],
        ),
        ["use language and notation of sets including n(A), union and intersection"],
    )
    assert set_complexity == "svg-basic"
    assert "set notation" in set_visual
    assert "statistics" not in set_visual

    chromatography_visual, chromatography_complexity, _ = choose_visual_type(
        Topic(
            title="3.4.1 - Purity and chromatography",
            points=["A mixture consists of two or more substances not chemically combined."],
        ),
        ["A mixture consists of two or more substances not chemically combined."],
    )
    assert chromatography_complexity == "text-ok"
    assert "chromatography" in chromatography_visual
    assert "geometry" not in chromatography_visual

    gas_visual, gas_complexity, _ = choose_visual_type(
        Topic(
            title="3.4.2 - Identification of common gases C",
            points=["A glowing splint relights in a test tube of oxygen gas."],
        ),
        ["A glowing splint relights in a test tube of oxygen gas."],
    )
    assert gas_complexity == "svg-basic"
    assert "gas tests" in gas_visual
    assert zh_visual_type(gas_visual) == "气体检验观察信息图"
    assert zh_visual_type("accounting process infographic with records") == "会计记录流程图"

    economics_visual, economics_complexity, _ = choose_visual_type(
        Topic(
            title="3.1.1.2 - The factors of production",
            points=["The factors of production are land, labour, capital and enterprise."],
        ),
        ["The factors of production are land, labour, capital and enterprise."],
    )
    assert economics_complexity == "text-ok"
    assert "mini case" in economics_visual
