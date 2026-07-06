import json

from pypdf import PdfWriter

from intl_exam_guide import cli as cli_module
import intl_exam_guide.auditing.final_review as final_review_module
from intl_exam_guide.auditing.final_review import (
    build_agent_self_review,
    build_final_review_packet,
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
    assert "rendered handbook" in packet["workflow"]["reviewer_instruction"]
    assert packet["agent_self_review"]["status"] == "draft"
    assert packet["agent_self_review"]["must_not_present_as_final"] is True
    assert packet["quality_inspection"]["present"] is False
    assert packet["quality_inspection"]["complete"] is False
    assert packet["product_review_evidence"]["present"] is False
    assert packet["product_review_evidence"]["complete"] is False
    assert packet["manual_review_contract"]["required"] is True
    assert packet["manual_review_contract"]["required_artifact"] == "agent-product-review.json"
    assert "fix the generation logic" in packet["manual_review_contract"]["instruction"]
    assert "Should this output be presented as final" in " ".join(packet["review_questions"])


def test_final_review_packet_recomputes_machine_validation_from_current_code(tmp_path):
    write_recomputable_review_fixture(tmp_path)

    packet = build_final_review_packet(tmp_path)

    messages = [issue["message"] for issue in packet["machine_validation"]["issues"]]
    assert packet["machine_validation"]["validation_refreshed"] is True
    assert any("SVG visual titles are too repetitive" in message for message in messages)
    assert packet["agent_self_review"]["status"] == "blocked"
    assert packet["review_summary"]["svg_files"] == 12



def complete_product_review() -> dict[str, object]:
    return {
        "schema_version": "v0.4-agent-product-review",
        "visible_handbook_inspected": True,
        "syllabus_outline_compared": True,
        "pdf_pages_sampled": [1, 2],
        "visuals_inspected": True,
        "glossary_policy_checked": True,
        "repair_loop_completed": True,
        "repairs_made": [],
        "unresolved_fixable_issues": [],
        "decision": "complete",
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
    assert any("Final product review evidence is missing" in reason for reason in review["reasons"])


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


def test_agent_self_review_blocks_failed_quality_inspection():
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

    assert review["status"] == "blocked"
    assert any("Quality inspection failed" in reason for reason in review["reasons"])


def test_product_review_evidence_validates_review_and_repair_artifact(tmp_path):
    assert product_review_evidence(tmp_path)["complete"] is False
    (tmp_path / "agent-product-review.json").write_text(
        json.dumps(complete_product_review(), ensure_ascii=False),
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


def test_write_final_review_packet_rerenders_pdf_after_html(monkeypatch, tmp_path):
    write_recomputable_review_fixture(tmp_path)
    calls = []

    def fake_export_pdf(html_path, pdf_path):
        calls.append((html_path, pdf_path, html_path.read_text(encoding="utf-8")))
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return pdf_path

    monkeypatch.setattr(final_review_module, "export_pdf", fake_export_pdf)

    write_final_review_packet(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    assert calls
    assert calls[-1][1] == tmp_path / "guide.pdf"
    assert "Review Check" in calls[-1][2]
    assert validation["pdf"] == str(tmp_path / "guide.pdf")
    assert validation["pdf_error"] is None


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

    def fake_export_pdf(_html_path, pdf_path):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return pdf_path

    monkeypatch.setattr(final_review_module, "rerender_html", fake_rerender_html)
    monkeypatch.setattr(final_review_module, "export_pdf", fake_export_pdf)

    write_final_review_packet(tmp_path)

    validation = json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))
    messages = [issue["message"] for issue in validation["issues"]]
    assert "HTML output contains syllabus shell text in student-facing content." in messages
