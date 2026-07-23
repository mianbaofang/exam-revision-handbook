import json

import pytest
from pypdf import PdfWriter

from intl_exam_guide import cli as cli_module
import intl_exam_guide.auditing.final_review as final_review_module
import intl_exam_guide.auditing.delivery_gate as delivery_gate_module
from intl_exam_guide.auditing.delivery_gate import audit_delivery
from intl_exam_guide.auditing.pdf_delivery import (
    ControlledDeliveryError,
    PdfTechnicalValidationError,
    copy_current_pdf_to_delivery,
    inspect_current_delivery,
    inspect_current_pdf,
)
from intl_exam_guide.auditing.review_ledger import (
    expected_review_items,
    review_ledger_evidence,
    write_review_ledger_index,
)
from intl_exam_guide.auditing.final_review import (
    build_agent_self_review,
    build_final_review_packet,
    build_final_review_prompt,
    export_reviewed_pdf,
    file_sha256,
    HtmlReviewRequiredError,
    invalidate_pdf_export,
    product_review_evidence,
    write_final_review_packet,
)
from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.validation.checks import ValidationIssue
from intl_exam_guide.rendering.output_names import find_handbook_html
from intl_exam_guide.rendering.render_snapshot import (
    canonical_json_sha256,
    inspect_current_render,
    write_render_snapshot,
)
from intl_exam_guide.rendering.output_names import (
    find_current_handbook_pdf,
    find_handbook_pdf,
)


def write_review_fixture(output_dir):
    (output_dir / "validation.json").write_text(
        json.dumps(
            {
                "issues": [],
                "review_summary": {"topics": 3, "pending_infographic_assets": 1},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (output_dir / "guide.html").write_text(
        "<h2>代数：二次函数</h2><p>例题：Solve x^2 - 5x + 6 = 0.</p>",
        encoding="utf-8",
    )
    (output_dir / "qualification.json").write_text(
        json.dumps({"title": "AS Mathematics", "topics": [{"title": "Algebra"}]}),
        encoding="utf-8",
    )
    (output_dir / "guide-plan.json").write_text(
        json.dumps({"run_options": {"output_language": "zh-CN"}}),
        encoding="utf-8",
    )
    images = output_dir / "images"
    images.mkdir()
    (images / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "complexity": "infographic",
                    "asset_status": "svg-fallback-needs-review",
                }
            ]
        ),
        encoding="utf-8",
    )
    (images / "infographic_jobs.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "status": "needs_generation_or_review",
                    "prompt": "Create a quadratic infographic.",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_recomputable_review_fixture(output_dir):
    snippets = [
        SourceSnippet(
            page=10 + index,
            text=f"Students should understand Topic {index}.",
            matched_term=f"Topic {index}",
        )
        for index in range(12)
    ]
    topics = [
        Topic(
            title=f"Topic {index}",
            points=[f"Students should understand Topic {index}."],
            source_snippets=[snippets[index]],
        )
        for index in range(12)
    ]
    qualification = Qualification(
        title="International GCSE Sample",
        code="0000",
        qualification_type="international_gcse",
        subject_area="Sample",
        page_url="https://example.test/sample",
        summary=["International GCSE linear qualification."],
        topics=topics,
        assessments=[AssessmentPaper(title="Paper 1")],
        source=SourceRecord(
            provider="oxfordaqa",
            page_url="https://example.test/sample",
            specification_url="https://example.test/spec.pdf",
            specification_sha256="hash",
        ),
        audience_note="International GCSE linear qualification for international students outside the UK.",
    )
    plan = GuidePlan(
        qualification=qualification,
        run_options=GuideRunOptions(
            requested_subject="Sample",
            image_provider="deterministic-svg",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[
            TopicGuide(
                topic_title=topic.title,
                essence=f"{topic.title} has one concrete idea.",
                analogy=f"Treat {topic.title} like a labelled step.",
                mini_worked_example=f"Use {topic.title} in a short worked example.",
                worked_solution_steps=["Read", "Select", "Apply", "Check"],
                pitfall=f"Do not confuse {topic.title} with a generic heading.",
                checklist=["Name it", "Use it", "Check it"],
                diagram_brief=f"Show {topic.title} as a small diagram.",
            )
            for topic in topics
        ],
        practice_items=[
            PracticeItem(
                topic_title=topic.title,
                command_word="Explain",
                difficulty="medium",
                focus_point=f"{topic.title} focus",
                question=f"Explain how {topic.title} is used in this course.",
                answer_frame=["Identify", "Apply", "Check"],
                public_solution_steps=["Read", "Identify", "Apply", "Check"],
                answer_checkpoints=[topic.title, "clear method", "checked answer"],
                source_points=topic.points,
            )
            for topic in topics
        ],
        visual_briefs=[
            VisualBrief(
                topic_title=topic.title,
                focus_point=f"{topic.title} focus",
                trigger="diagram",
                visual_type="concept diagram",
                complexity="svg-basic",
                image_provider="deterministic-svg",
                prompt=f"Draw {topic.title}.",
                source_points=topic.points,
            )
            for topic in topics
        ],
        diagram_briefs=[],
        revision_stages=["Read", "Practise"],
    )
    (output_dir / "validation.json").write_text(
        json.dumps({"issues": [], "review_summary": {"topics": 12}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "qualification.json").write_text(
        json.dumps(qualification.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "guide-plan.json").write_text(
        json.dumps(plan.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "run-options.json").write_text(
        json.dumps(plan.run_options.__dict__, ensure_ascii=False),
        encoding="utf-8",
    )
    sections = output_dir / "sections"
    sections.mkdir()
    for index in range(5):
        (sections / f"{index:02}.txt").write_text("section", encoding="utf-8")
    (output_dir / "handbook-package.json").write_text("{}", encoding="utf-8")
    html = (
        "How to Study Study Roadmap One-Sentence Essence Method Worked Example "
        "Solution Check Exam Pitfall Source anchor Concept Map Visual Worked Example "
        + "".join(
            f'<section class="topic"><h2>{topic.title}</h2><figure class="topic-diagram"></figure></section>'
            for topic in topics
        )
    )
    (output_dir / "guide.html").write_text(html, encoding="utf-8")
    images = output_dir / "images"
    images.mkdir()
    for index in range(12):
        (images / f"visual_{index:03}.svg").write_text(
            f"<svg><title>Repeated diagram</title><rect x='1' y='1'/><text>{index}</text></svg>",
            encoding="utf-8",
        )
    (images / "visual_manifest.json").write_text("[]", encoding="utf-8")


def test_final_review_packet_includes_user_visible_evidence(tmp_path):
    write_review_fixture(tmp_path)

    packet = build_final_review_packet(tmp_path)

    assert packet["machine_validation"]["error_count"] == 0
    assert packet["visuals"]["pending_or_review_needed"] == ["visual_001"]
    assert packet["visuals"]["infographic_jobs"][0]["id"] == "visual_001"
    assert "代数：二次函数" in packet["rendered_excerpt"]
    assert packet["qualification"]["title"] == "AS Mathematics"
    assert packet["guide_plan"]["available"] is True
    assert packet["agent_review_required"] is True
    assert packet["workflow"]["mode"] == "lightweight-three-role"
    assert packet["workflow"]["roles"] == ["analyst", "writer", "reviewer"]
    assert "current rendered HTML" in packet["workflow"]["reviewer_instruction"]
    assert packet["html_review_gate"]["pdf_export_allowed"] is False
    assert packet["agent_self_review"]["status"] == "draft"
    assert packet["agent_self_review"]["must_not_present_as_final"] is True
    assert packet["quality_inspection"]["present"] is False
    assert packet["quality_inspection"]["complete"] is False
    assert packet["product_review_evidence"]["present"] is False
    assert packet["product_review_evidence"]["complete"] is False
    assert packet["manual_review_contract"]["required"] is True
    assert packet["manual_review_contract"]["required_artifact"] == "agent-product-review.json"
    assert "return to the Writer" in packet["manual_review_contract"]["instruction"]
    assert "Python diagnostics cannot supply" in packet["manual_review_contract"]["instruction"]
    assert "Should this output be presented as final" in " ".join(packet["review_questions"])


def test_final_review_packet_recomputes_machine_validation_from_current_code(tmp_path):
    write_recomputable_review_fixture(tmp_path)

    packet = build_final_review_packet(tmp_path)

    messages = [issue["message"] for issue in packet["machine_validation"]["issues"]]
    assert packet["machine_validation"]["validation_refreshed"] is True
    assert any("SVG visual titles are too repetitive" in message for message in messages)
    assert packet["agent_self_review"]["status"] == "blocked"
    assert packet["review_summary"]["svg_files"] == 12



def complete_product_review(
    html_sha256: str = "a" * 64,
    topic_titles: list[str] | None = None,
    visual_ids: list[str] | None = None,
) -> dict[str, object]:
    reviewed_topics = topic_titles or []
    reviewed_visuals = visual_ids or []
    return {
        "schema_version": "v0.6-llm-html-review",
        "reviewer_type": "llm",
        "html_opened_and_visually_inspected": True,
        "reviewed_html_sha256": html_sha256,
        "review_iteration": 1,
        "html_review_passed": True,
        "all_topics_reviewed": True,
        "topic_review_count": len(reviewed_topics),
        "reviewed_topic_titles": reviewed_topics,
        "subject_factual_accuracy_checked": True,
        "worked_examples_and_answers_checked": True,
        "all_rendered_visuals_reviewed": True,
        "rendered_visual_review_count": len(reviewed_visuals),
        "reviewed_visual_ids": reviewed_visuals,
        "visual_semantics_checked": True,
        "layout_checked": True,
        "machine_validation_used_only_as_supporting_evidence": True,
        "syllabus_outline_compared": True,
        "granularity_audit_checked": True,
        "merged_bullets_visible_in_handbook": True,
        "visuals_inspected": True,
        "cross_page_visual_repetition_checked": True,
        "notation_spot_check_completed": True,
        "glossary_policy_checked": True,
        "repair_loop_completed": True,
        "issues_found": [],
        "repairs_made": [],
        "unresolved_fixable_issues": [],
        "decision": "approved",
    }


def test_agent_self_review_requires_product_review_evidence():
    review = build_agent_self_review(
        {"error_count": 0},
        {},
        "Rendered student text",
        [],
        {
            "required": True,
            "file": "agent-product-review.json",
            "present": False,
            "complete": False,
            "issues": ["Missing agent-product-review.json."],
            "review": {},
        },
    )

    assert review["status"] == "draft"
    assert review["must_not_present_as_final"] is True
    assert any("Current-HTML LLM review evidence is missing" in reason for reason in review["reasons"])


def test_agent_self_review_ready_requires_complete_product_review_evidence():
    review = build_agent_self_review(
        {"error_count": 0},
        {},
        "Rendered student text",
        [],
        {
            "required": True,
            "file": "agent-product-review.json",
            "present": True,
            "complete": True,
            "issues": [],
            "review": complete_product_review(),
        },
        {
            "required": True,
            "file": "quality-inspection.json",
            "present": True,
            "complete": True,
            "issues": [],
            "inspection": {
                "schema_version": "v0.5-quality-inspection",
                "inspection_status": "pass",
                "recommendation": "pass_to_reviewer",
                "issues": [],
            },
        },
    )

    assert review["status"] == "ready"
    assert review["must_not_present_as_final"] is False


def test_agent_self_review_treats_python_quality_inspection_as_support_only():
    review = build_agent_self_review(
        {"error_count": 0},
        {},
        "Rendered student text",
        [],
        {
            "required": True,
            "file": "agent-product-review.json",
            "present": True,
            "complete": True,
            "issues": [],
            "review": complete_product_review(),
        },
        {
            "required": True,
            "file": "quality-inspection.json",
            "present": True,
            "complete": False,
            "issues": ["Required file missing: syllabus-outline.json."],
            "inspection": {"inspection_status": "fail"},
        },
    )

    assert review["status"] == "ready"
    assert review["must_not_present_as_final"] is False


def test_product_review_evidence_validates_review_and_repair_artifact(tmp_path):
    assert product_review_evidence(tmp_path)["complete"] is False
    html_path = tmp_path / "guide.html"
    html_path.write_text("<h1>Reviewed handbook</h1>", encoding="utf-8")
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(complete_product_review(file_sha256(html_path)), ensure_ascii=False),
        encoding="utf-8",
    )

    evidence = product_review_evidence(tmp_path)

    assert evidence["present"] is True
    assert evidence["complete"] is True
    assert evidence["issues"] == []


def test_final_review_packet_excerpt_omits_css_and_script(tmp_path):
    write_review_fixture(tmp_path)
    (tmp_path / "guide.html").write_text(
        """
        <style>:root { --ink: #172033; } body { margin: 0; }</style>
        <script>console.log("not reviewable student content")</script>
        <h1>Student-facing revision guide</h1>
        <p>Worked example: solve the equation and check the answer.</p>
        """,
        encoding="utf-8",
    )

    packet = build_final_review_packet(tmp_path)

    assert ":root" not in packet["rendered_excerpt"]
    assert "console.log" not in packet["rendered_excerpt"]
    assert "Student-facing revision guide" in packet["rendered_excerpt"]
    assert "Worked example" in packet["rendered_excerpt"]


def test_final_review_prompt_requires_llm_html_review_before_pdf(tmp_path):
    html_path = tmp_path / "guide.html"
    html_path.write_text("<h1>Current handbook</h1>", encoding="utf-8")
    evidence_path = tmp_path / "syllabus-evidence.json"
    evidence_path.write_text("{}", encoding="utf-8")
    validation_path = tmp_path / "validation.json"
    validation_path.write_text("{}", encoding="utf-8")

    prompt = build_final_review_prompt(html_path, evidence_path, validation_path)

    assert "Python cannot approve the handbook" in prompt
    assert "Do not generate or inspect a PDF during this stage" in prompt
    assert file_sha256(html_path) in prompt
    assert '"reviewer_type": "llm"' in prompt
    assert "with at most 25 reviews each" in prompt
    assert '"complete_html_reviewed"' in prompt
    assert '"decision": "<approved or revisions_required>"' in prompt
    assert '"html_opened_and_visually_inspected": "<true only after direct inspection>"' in prompt


def test_review_cli_writes_packet_and_prints_json(tmp_path, capsys):
    write_review_fixture(tmp_path)

    result = cli_module.main(["review", "--out", str(tmp_path)])

    assert result == 0
    packet_path = tmp_path / "final-review-packet.json"
    assert packet_path.exists()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["visuals"]["pending_or_review_needed"] == ["visual_001"]
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["final_review_packet"] == str(packet_path)


def test_write_final_review_packet_refreshes_validation_json(tmp_path):
    write_recomputable_review_fixture(tmp_path)

    write_final_review_packet(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    packet = json.loads((tmp_path / "final-review-packet.json").read_text(encoding="utf-8"))
    contract = json.loads((tmp_path / "delivery-contract.json").read_text(encoding="utf-8"))
    assert not (tmp_path / "agent-orchestration.json").exists()
    assert validation["validation_refreshed"] is True
    assert validation["review_summary"] == packet["review_summary"]
    assert validation["delivery_status"] == packet["machine_validation"]["delivery_status"]
    assert contract["delivery_state"] == validation["delivery_state"]
    assert contract["pedagogical_units"][0]["delivery_state"] == validation["delivery_state"]
    assert "agent_orchestration" not in packet
    assert "agent_orchestration" not in contract
    assert contract["workflow"]["mode"] == "llm-owned-lightweight-workflow"


def test_write_final_review_packet_does_not_continue_after_rerender_failure(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    (tmp_path / "guide-plan.json").write_text("{", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Unable to rerender"):
        write_final_review_packet(tmp_path)

    assert not (tmp_path / "final-review-packet.json").exists()


def test_write_final_review_packet_never_exports_pdf(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    old_pdf = tmp_path / "guide.pdf"
    old_pdf.write_bytes(b"%PDF-1.4\n")

    def fail_export_pdf(_html_path, _pdf_path):
        raise AssertionError("review must not export PDF")

    monkeypatch.setattr(final_review_module, "export_pdf", fail_export_pdf)

    write_final_review_packet(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    assert old_pdf.exists()
    assert validation["pdf"] is None
    assert validation["pdf_error"] is None
    assert validation["pdf_export_gate"]["status"] == "pending_current_html_review"


def test_write_final_review_packet_strips_legacy_review_panel_before_html_review(
    monkeypatch, tmp_path
):
    write_recomputable_review_fixture(tmp_path)
    html_path = tmp_path / "guide.html"
    html_path.write_text(
        html_path.read_text(encoding="utf-8")
        + '<section class="band delivery-panel" data-review-state="needs-review"><h2>Review Check</h2><strong>Needs visible review</strong></section>',
        encoding="utf-8",
    )
    def fake_rerender_html(_output_dir):
        final_review_module.strip_internal_review_panel_from_file(html_path)

    monkeypatch.setattr(final_review_module, "rerender_html", fake_rerender_html)

    write_final_review_packet(tmp_path)

    reviewed_html = html_path.read_text(encoding="utf-8")
    assert "Review Check" not in reviewed_html
    assert "Needs visible review" not in reviewed_html
    assert "data-review-state" not in reviewed_html
    assert "delivery-panel" not in reviewed_html


def test_write_final_review_packet_validates_the_rerendered_html(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)

    def fake_rerender_html(output_dir):
        html = "How to Study Study Roadmap One-Sentence Essence Method Worked Example Solution Check Exam Pitfall "
        html += "Source anchor Concept Map Visual Worked Example "
        html += "".join(
            f'<section class="topic"><h2>Topic {index}</h2></section>' for index in range(12)
        )
        html += "<p>Students should be able to understand the nature of an economic resource.</p>"
        (output_dir / "guide.html").write_text(html, encoding="utf-8")

    monkeypatch.setattr(final_review_module, "rerender_html", fake_rerender_html)

    write_final_review_packet(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    messages = [issue["message"] for issue in validation["issues"]]
    assert "HTML output contains syllabus shell text in student-facing content." in messages


def test_export_reviewed_pdf_rejects_missing_llm_html_review(tmp_path):
    write_recomputable_review_fixture(tmp_path)

    with pytest.raises(HtmlReviewRequiredError, match="requires LLM approval"):
        export_reviewed_pdf(tmp_path)

    assert not list(tmp_path.glob("*.pdf"))


def test_export_reviewed_pdf_rejects_review_for_stale_html(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    html_path = tmp_path / "guide.html"
    topic_titles = [f"Topic {index}" for index in range(12)]
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(complete_product_review(file_sha256(html_path), topic_titles)),
        encoding="utf-8",
    )
    html_path.write_text(html_path.read_text(encoding="utf-8") + "<p>Changed</p>", encoding="utf-8")

    with pytest.raises(HtmlReviewRequiredError, match="does not match the current HTML"):
        export_reviewed_pdf(tmp_path)

    assert not list(tmp_path.glob("*.pdf"))


def test_export_reviewed_pdf_rejects_incomplete_topic_review_coverage(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    html_path = tmp_path / "guide.html"
    incomplete_titles = [f"Topic {index}" for index in range(11)]
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(complete_product_review(file_sha256(html_path), incomplete_titles)),
        encoding="utf-8",
    )

    with pytest.raises(HtmlReviewRequiredError, match="missing 1 required topic"):
        export_reviewed_pdf(tmp_path)


def test_export_reviewed_pdf_rejects_unreviewed_rendered_visual(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    html_path = tmp_path / "guide.html"
    topic_titles = [f"Topic {index}" for index in range(12)]
    (tmp_path / "images" / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "topic_title": "Topic 0",
                    "asset_status": "generated",
                    "file": "visual_000.svg",
                    "complexity": "svg-basic",
                }
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(complete_product_review(file_sha256(html_path), topic_titles)),
        encoding="utf-8",
    )

    with pytest.raises(HtmlReviewRequiredError, match="missing 1 required rendered visual"):
        export_reviewed_pdf(tmp_path)


def test_export_reviewed_pdf_allows_current_html_llm_approval(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    plan_path = tmp_path / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["visual_briefs"] = []
    plan["content_provenance"] = "llm-authored"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    html_path = tmp_path / "guide.html"
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    write_current_product_review_v07(tmp_path)
    calls = []

    def fake_export_pdf(source_html, pdf_path):
        calls.append((source_html, pdf_path))
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return pdf_path

    monkeypatch.setattr(final_review_module, "export_pdf", fake_export_pdf)
    monkeypatch.setattr(
        final_review_module,
        "inspect_pdf_candidate",
        lambda _plan, _path: {
            "status": "passed",
            "blockers": [],
            "warnings": [],
            "summary": {"pdf_pages": 1},
        },
    )
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    pdf_path = export_reviewed_pdf(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    assert calls[0][0] == html_path
    assert calls[0][1] != pdf_path
    assert calls[0][1].name.endswith(".candidate.pdf")
    assert pdf_path.exists()
    assert validation["pdf"] == str(pdf_path)
    assert validation["pdf_export_gate"]["reviewed_html_sha256"] == file_sha256(html_path)
    assert validation["pdf_export_gate"]["status"] == "passed"
    assert inspect_current_pdf(tmp_path)["complete"] is True
    assert len(list((tmp_path / "pdf-exports").glob("*.json"))) == 1


def test_export_reviewed_pdf_does_not_promote_failed_pdf_candidate(monkeypatch, tmp_path):
    _prepare_approved_no_visual_fixture(tmp_path)

    def fake_export_pdf(_source_html, pdf_path):
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return pdf_path

    monkeypatch.setattr(final_review_module, "export_pdf", fake_export_pdf)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    with pytest.raises(PdfTechnicalValidationError, match="no meaningful text"):
        export_reviewed_pdf(tmp_path)

    assert not (tmp_path / "current-pdf.json").exists()
    assert not (tmp_path / "guide.pdf").exists()
    assert not list(tmp_path.glob("*.candidate.pdf"))


def test_controlled_delivery_blocks_conflict_until_explicit_supersede(
    monkeypatch, tmp_path
):
    pdf_path = _export_fake_current_pdf(monkeypatch, tmp_path)
    delivery_dir = tmp_path / "delivery"
    delivery_dir.mkdir()
    destination = delivery_dir / "guide.pdf"
    destination.write_bytes(b"old delivery")

    with pytest.raises(ControlledDeliveryError, match="different file"):
        copy_current_pdf_to_delivery(tmp_path, delivery_dir)

    assert destination.read_bytes() == b"old delivery"
    delivered = copy_current_pdf_to_delivery(
        tmp_path, delivery_dir, supersede_existing=True
    )

    assert delivered == destination
    assert file_sha256(delivered) == file_sha256(pdf_path)
    assert len(list((delivery_dir / "superseded").glob("guide-*.pdf"))) == 1
    assert inspect_current_delivery(tmp_path)["complete"] is True


def test_pdf_invalidation_preserves_historical_file_but_clears_current_status(
    monkeypatch, tmp_path
):
    pdf_path = _export_fake_current_pdf(monkeypatch, tmp_path)

    invalidate_pdf_export(tmp_path)

    pointer = json.loads((tmp_path / "current-pdf.json").read_text(encoding="utf-8"))
    assert pdf_path.exists()
    assert pointer["status"] == "stale"
    assert inspect_current_pdf(tmp_path)["complete"] is False
    assert find_current_handbook_pdf(tmp_path) is None
    assert find_handbook_pdf(tmp_path) == pdf_path


def test_audit_delivery_reports_state_specific_next_action(monkeypatch, tmp_path):
    _prepare_approved_no_visual_fixture(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    assert audit_delivery(tmp_path)["next_actions"][0]["action"] == "export_pdf"

    _export_fake_current_pdf(monkeypatch, tmp_path, prepared=True)
    assert audit_delivery(tmp_path)["next_actions"] == [
        {"action": "complete", "reason_codes": []}
    ]

    copy_current_pdf_to_delivery(tmp_path, tmp_path / "delivery")
    assert audit_delivery(tmp_path)["next_actions"] == [
        {"action": "complete", "reason_codes": []}
    ]
    (tmp_path / "delivery" / "guide.pdf").write_bytes(b"changed after delivery")
    assert audit_delivery(tmp_path)["next_actions"] == [
        {
            "action": "refresh_controlled_delivery_copy",
            "reason_codes": ["delivery.stale"],
        }
    ]


def _prepare_approved_no_visual_fixture(output_dir):
    write_recomputable_review_fixture(output_dir)
    plan_path = output_dir / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["visual_briefs"] = []
    plan["content_provenance"] = "llm-authored"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    write_current_render_snapshot(output_dir)
    write_complete_review_ledger(output_dir)
    write_current_product_review_v07(output_dir)


def _export_fake_current_pdf(monkeypatch, output_dir, *, prepared=False):
    if not prepared:
        _prepare_approved_no_visual_fixture(output_dir)

    def fake_export_pdf(_source_html, pdf_path):
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return pdf_path

    monkeypatch.setattr(final_review_module, "export_pdf", fake_export_pdf)
    monkeypatch.setattr(
        final_review_module,
        "inspect_pdf_candidate",
        lambda _plan, _path: {
            "status": "passed",
            "blockers": [],
            "warnings": [],
            "summary": {"pdf_pages": 1},
        },
    )
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])
    return export_reviewed_pdf(output_dir)


def write_current_visual_manifest(
    output_dir,
    *,
    decision="approved",
    review_status="reviewed",
    stored_hash=None,
):
    asset_path = output_dir / "images" / "visual_001.svg"
    asset_path.write_text(
        "<svg><line x1='0' y1='0' x2='10' y2='10'/></svg>", encoding="utf-8"
    )
    asset_hash = stored_hash or file_sha256(asset_path)
    manifest = {
        "schema_version": 2,
        "visuals": [
            {
                "id": "visual_001",
                "visual_id": "visual_001",
                "review_status": review_status,
                "asset_status": "generated",
                "file": asset_path.name,
                "asset": {"file": asset_path.name, "sha256": asset_hash},
                "visual_need": {"reviewer_visual_decision": decision},
                "recommended_route": {"route": "exact-svg"},
            }
        ],
    }
    (output_dir / "images" / "visual_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def write_current_product_review(output_dir, visual_ids=None):
    html_path = output_dir / "guide.html"
    topic_titles = [f"Topic {index}" for index in range(12)]
    (output_dir / "agent-product-review.json").write_text(
        json.dumps(
            complete_product_review(file_sha256(html_path), topic_titles, visual_ids or [])
        ),
        encoding="utf-8",
    )


def write_current_render_snapshot(output_dir):
    plan = GuidePlan.from_dict(
        json.loads((output_dir / "guide-plan.json").read_text(encoding="utf-8"))
    )
    return write_render_snapshot(
        output_dir,
        output_dir / "guide.html",
        plan,
        output_dir / "images" / "visual_manifest.json",
    )


def write_complete_review_ledger(output_dir):
    pointer = json.loads((output_dir / "current-render.json").read_text(encoding="utf-8"))
    topic_items, visual_items = expected_review_items(output_dir)
    ledger_dir = output_dir / "review-ledger"
    ledger_dir.mkdir(exist_ok=True)
    for index in range(0, len(topic_items), 25):
        reviews = [
            {
                **item,
                "decision": "approved",
                "factual_accuracy_checked": True,
                "worked_example_checked": True,
                "source_traceability_checked": True,
                "teaching_value_checked": True,
                "findings": [],
                "evidence_locations": [f"guide.html#{item['topic_id']} @ desktop"],
                "review_iteration": 1,
            }
            for item in topic_items[index : index + 25]
        ]
        (ledger_dir / f"topics-{index // 25 + 1:03}.json").write_text(
            json.dumps(
                {
                    "schema_version": "v1-topic-review-shard",
                    "render_snapshot_id": pointer["snapshot_id"],
                    "html_sha256": pointer["html_sha256"],
                    "reviews": reviews,
                }
            ),
            encoding="utf-8",
        )
    for index in range(0, len(visual_items), 25):
        reviews = [
            {
                **item,
                "decision": "approved",
                "semantic_contract_checked": True,
                "semantic_accuracy_checked": True,
                "teaching_value_checked": True,
                "layout_checked": True,
                "findings": [],
                "evidence_locations": [f"guide.html#{item['visual_id']} @ desktop"],
                "review_iteration": 1,
            }
            for item in visual_items[index : index + 25]
        ]
        (ledger_dir / f"visuals-{index // 25 + 1:03}.json").write_text(
            json.dumps(
                {
                    "schema_version": "v1-visual-review-shard",
                    "render_snapshot_id": pointer["snapshot_id"],
                    "html_sha256": pointer["html_sha256"],
                    "reviews": reviews,
                }
            ),
            encoding="utf-8",
        )
    (ledger_dir / "holistic.json").write_text(
        json.dumps(
            {
                "schema_version": "v1-holistic-html-review",
                "render_snapshot_id": pointer["snapshot_id"],
                "html_sha256": pointer["html_sha256"],
                "html_opened_and_visually_inspected": True,
                "complete_html_reviewed": True,
                "cover_and_navigation_checked": True,
                "cross_page_consistency_checked": True,
                "responsive_layout_checked": True,
                "notation_and_encoding_checked": True,
                "decision": "approved",
                "findings": [],
                "evidence_locations": [
                    "guide.html @ desktop full-scroll",
                    "guide.html @ mobile full-scroll",
                ],
                "unresolved_fixable_issues": [],
                "review_iteration": 1,
            }
        ),
        encoding="utf-8",
    )
    return write_review_ledger_index(output_dir)


def write_current_product_review_v07(output_dir):
    pointer = json.loads((output_dir / "current-render.json").read_text(encoding="utf-8"))
    ledger = review_ledger_evidence(output_dir)
    (output_dir / "agent-product-review.json").write_text(
        json.dumps(
            {
                "schema_version": "v0.7-llm-html-review-ledger",
                "reviewer_type": "llm",
                "html_opened_and_visually_inspected": True,
                "complete_html_reviewed": True,
                "reviewed_html_sha256": pointer["html_sha256"],
                "render_snapshot_id": pointer["snapshot_id"],
                "review_ledger_index_sha256": ledger["index_sha256"],
                "review_iteration": 1,
                "html_review_passed": True,
                "machine_validation_used_only_as_supporting_evidence": True,
                "repair_loop_completed": True,
                "issues_found": [],
                "repairs_made": [],
                "unresolved_fixable_issues": [],
                "decision": "approved",
            }
        ),
        encoding="utf-8",
    )
def test_export_reviewed_pdf_rejects_current_validation_error(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    plan_path = tmp_path / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["visual_briefs"] = []
    plan["content_provenance"] = "llm-authored"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    write_current_product_review(tmp_path)
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(
        delivery_gate_module,
        "validate_plan",
        lambda *args, **kwargs: [ValidationIssue("error", "Current validation failed.")],
    )

    with pytest.raises(HtmlReviewRequiredError, match="Current validation failed"):
        export_reviewed_pdf(tmp_path)

    assert not list(tmp_path.glob("*.pdf"))


@pytest.mark.parametrize("decision", ["pending", "rejected"])
def test_export_reviewed_pdf_rejects_pending_or_rejected_visual(
    monkeypatch, tmp_path, decision
):
    write_recomputable_review_fixture(tmp_path)
    write_current_visual_manifest(tmp_path, decision=decision)
    write_current_product_review(tmp_path, ["visual_001"])
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    with pytest.raises(HtmlReviewRequiredError, match="reviewer_visual_decision"):
        export_reviewed_pdf(tmp_path)


def test_export_reviewed_pdf_rejects_unreviewed_rendered_svg(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_visual_manifest(tmp_path, review_status="pending")
    write_current_product_review(tmp_path, ["visual_001"])
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    with pytest.raises(HtmlReviewRequiredError, match="review_status is pending"):
        export_reviewed_pdf(tmp_path)


def test_export_reviewed_pdf_rejects_stale_visual_asset_hash(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_visual_manifest(tmp_path, stored_hash="0" * 64)
    write_current_product_review(tmp_path, ["visual_001"])
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    with pytest.raises(HtmlReviewRequiredError, match="SHA-256 does not match"):
        export_reviewed_pdf(tmp_path)


def test_export_pdf_cli_refuses_unreviewed_html(tmp_path, capsys):
    write_recomputable_review_fixture(tmp_path)

    result = cli_module.main(["export-pdf", "--out", str(tmp_path)])

    assert result == 2
    assert "requires LLM approval" in capsys.readouterr().err


def test_audit_delivery_is_read_only_and_reports_current_blockers(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    before = {
        path.relative_to(tmp_path): file_sha256(path)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    report = audit_delivery(tmp_path)

    after = {
        path.relative_to(tmp_path): file_sha256(path)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert before == after
    assert report["delivery_eligible"] is False
    codes = {issue["code"] for issue in report["blockers"]}
    assert "review.current_html_unapproved" in codes
    assert "render.current_pointer_missing" in codes
    assert "visual.manifest_empty" in codes
    assert report["machine_validation"]["html_only"] is True


def test_audit_delivery_allows_current_reviewed_html_without_visuals(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    plan_path = tmp_path / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["visual_briefs"] = []
    plan["content_provenance"] = "llm-authored"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    write_current_product_review_v07(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    report = audit_delivery(tmp_path)

    assert report["delivery_eligible"] is True
    assert report["blockers"] == []


def test_review_ledger_detects_missing_topic_after_reindex(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    shard_path = tmp_path / "review-ledger" / "topics-001.json"
    shard = json.loads(shard_path.read_text(encoding="utf-8"))
    shard["reviews"].pop()
    shard_path.write_text(json.dumps(shard), encoding="utf-8")
    write_review_ledger_index(tmp_path)

    evidence = review_ledger_evidence(tmp_path)

    assert evidence["complete"] is False
    assert any(issue["code"] == "review.topic_missing" for issue in evidence["issues"])


def test_review_ledger_detects_stale_shard_hash(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    shard_path = tmp_path / "review-ledger" / "topics-001.json"
    shard_path.write_text(shard_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    evidence = review_ledger_evidence(tmp_path)

    assert any(issue["code"] == "review.ledger_file_hash" for issue in evidence["issues"])


def test_review_ledger_requires_approved_visual_review(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_visual_manifest(tmp_path)
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    shard_path = tmp_path / "review-ledger" / "visuals-001.json"
    shard = json.loads(shard_path.read_text(encoding="utf-8"))
    shard["reviews"][0]["decision"] = "revisions_required"
    shard_path.write_text(json.dumps(shard), encoding="utf-8")
    write_review_ledger_index(tmp_path)

    evidence = review_ledger_evidence(tmp_path)

    assert any(issue["code"] == "review.item_not_approved" for issue in evidence["issues"])


def test_review_ledger_requires_visible_evidence_locations(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    shard_path = tmp_path / "review-ledger" / "topics-001.json"
    shard = json.loads(shard_path.read_text(encoding="utf-8"))
    shard["reviews"][0]["evidence_locations"] = []
    shard_path.write_text(json.dumps(shard), encoding="utf-8")
    write_review_ledger_index(tmp_path)

    evidence = review_ledger_evidence(tmp_path)

    assert any(
        issue["code"] == "review.item_evidence_missing" for issue in evidence["issues"]
    )


def test_review_ledger_rejects_oversized_shard(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    write_complete_review_ledger(tmp_path)
    shard_path = tmp_path / "review-ledger" / "topics-001.json"
    shard = json.loads(shard_path.read_text(encoding="utf-8"))
    shard["reviews"] = [shard["reviews"][0] for _ in range(26)]
    shard_path.write_text(json.dumps(shard), encoding="utf-8")
    write_review_ledger_index(tmp_path)

    evidence = review_ledger_evidence(tmp_path)

    assert any(issue["code"] == "review.topic_shard_oversized" for issue in evidence["issues"])


def test_index_review_ledger_cli_hashes_existing_llm_shards(tmp_path, capsys):
    write_recomputable_review_fixture(tmp_path)
    write_current_render_snapshot(tmp_path)
    index_path = write_complete_review_ledger(tmp_path)
    index_path.unlink()

    result = cli_module.main(["index-review-ledger", "--out", str(tmp_path)])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["review_ledger_index"] == str(index_path)
    assert index_path.exists()


def test_audit_delivery_blocks_pending_visual_and_stale_asset_hash(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    html_path = tmp_path / "guide.html"
    topic_titles = [f"Topic {index}" for index in range(12)]
    asset_path = tmp_path / "images" / "visual_001.svg"
    asset_path.write_text("<svg><line x1='0' y1='0' x2='10' y2='10'/></svg>", encoding="utf-8")
    manifest = {
        "schema_version": 2,
        "visuals": [
            {
                "id": "visual_001",
                "visual_id": "visual_001",
                "review_status": "pending",
                "asset_status": "generated",
                "file": asset_path.name,
                "asset": {"file": asset_path.name, "sha256": "0" * 64},
                "visual_need": {"reviewer_visual_decision": "pending"},
                "recommended_route": {"route": "exact-svg"},
            }
        ],
    }
    (tmp_path / "images" / "visual_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(
            complete_product_review(file_sha256(html_path), topic_titles, ["visual_001"])
        ),
        encoding="utf-8",
    )
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    report = audit_delivery(tmp_path)

    codes = {issue["code"] for issue in report["blockers"]}
    assert "visual.decision_pending" in codes
    assert "visual.asset_unreviewed" in codes
    assert "visual.asset_hash_mismatch" in codes


def test_audit_delivery_blocks_manifest_not_bound_to_current_plan(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    manifest_path = tmp_path / "images" / "visual_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_stale",
                        "key": "stale||visual||entry||infographic",
                        "spec_hash": "f" * 64,
                        "recommended_route": {"route": "text-ok"},
                        "visual_need": {"reviewer_visual_decision": "approved"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    report = audit_delivery(tmp_path)

    codes = {issue["code"] for issue in report["blockers"]}
    assert "visual.manifest_plan_mismatch" in codes


def test_audit_delivery_blocks_python_fallback_provenance(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    plan_path = tmp_path / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["visual_briefs"] = []
    plan["content_provenance"] = "llm-authored"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    concepts = tmp_path / "concepts"
    concepts.mkdir()
    (concepts / "concept_explanations.json").write_text(
        json.dumps(
            [
                {
                    "topic_id": "requirement-test",
                    "topic_title": "Topic 0",
                    "provenance": "python-fallback",
                    "delivery_eligible": False,
                    "visual_decision": {"source": "python-draft-fallback"},
                }
            ]
        ),
        encoding="utf-8",
    )
    write_current_product_review(tmp_path)
    write_current_render_snapshot(tmp_path)
    monkeypatch.setattr(delivery_gate_module, "validate_plan", lambda *args, **kwargs: [])

    report = audit_delivery(tmp_path)

    assert any(issue["code"] == "content.python_fallback" for issue in report["blockers"])


def test_render_snapshot_uses_canonical_json_and_preserves_history(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    first_pointer = write_current_render_snapshot(tmp_path)
    first_snapshot = tmp_path / first_pointer["snapshot_file"]
    plan_path = tmp_path / "guide-plan.json"
    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_path.write_text(
        json.dumps(plan_payload, ensure_ascii=False, indent=4, sort_keys=True),
        encoding="utf-8",
    )

    equivalent_pointer = write_current_render_snapshot(tmp_path)

    assert equivalent_pointer["snapshot_id"] == first_pointer["snapshot_id"]
    assert first_snapshot.exists()
    assert canonical_json_sha256({"text": "e\u0301", "value": 1}) == canonical_json_sha256(
        {"value": 1, "text": "é"}
    )

    plan_payload["revision_stages"].append("Recheck")
    plan_path.write_text(json.dumps(plan_payload), encoding="utf-8")
    second_pointer = write_current_render_snapshot(tmp_path)

    assert second_pointer["snapshot_id"] != first_pointer["snapshot_id"]
    assert len(list((tmp_path / "render-snapshots").glob("*.json"))) == 2
    assert first_snapshot.exists()


def test_current_render_pointer_beats_newer_mtime_and_detects_input_change(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    pointer = write_current_render_snapshot(tmp_path)
    newer_html = tmp_path / "newer-but-not-current.html"
    newer_html.write_text("<h1>Not reviewed</h1>", encoding="utf-8")

    assert find_handbook_html(tmp_path) == tmp_path / pointer["html_path"]
    assert inspect_current_render(tmp_path)["complete"] is True

    plan_path = tmp_path / "guide-plan.json"
    plan_path.write_text(plan_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert inspect_current_render(tmp_path)["complete"] is True

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["revision_stages"].append("Changed after review")
    plan_path.write_text(json.dumps(payload), encoding="utf-8")
    inspection = inspect_current_render(tmp_path)

    assert inspection["complete"] is False
    assert {issue["code"] for issue in inspection["issues"]} == {
        "render.input_hash_mismatch"
    }


def test_new_render_snapshot_marks_previous_pdf_pointer_stale(tmp_path):
    write_recomputable_review_fixture(tmp_path)
    first = write_current_render_snapshot(tmp_path)
    (tmp_path / "current-pdf.json").write_text(
        json.dumps(
            {
                "schema_version": "v1-current-pdf-pointer",
                "status": "current",
                "render_snapshot_id": first["snapshot_id"],
            }
        ),
        encoding="utf-8",
    )
    plan_path = tmp_path / "guide-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["revision_stages"].append("Changed")
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    write_current_render_snapshot(tmp_path)

    current_pdf = json.loads((tmp_path / "current-pdf.json").read_text(encoding="utf-8"))
    assert current_pdf["status"] == "stale"
    assert current_pdf["invalidated_reason"] == "render snapshot changed"


def test_audit_delivery_cli_reports_blocked_without_writing_files(tmp_path, capsys):
    write_recomputable_review_fixture(tmp_path)

    result = cli_module.main(["audit-delivery", "--out", str(tmp_path)])

    report = json.loads(capsys.readouterr().out)
    assert result == 2
    assert report["mode"] == "read-only-delivery-audit"
    assert report["delivery_eligible"] is False
