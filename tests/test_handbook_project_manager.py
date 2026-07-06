import json

from intl_exam_guide.coordination import (
    REQUIRED_SEQUENCE,
    HandbookProjectParameters,
    build_coordinator_prompt,
    build_project_state,
    write_coordinator_artifacts,
)


def test_project_state_tracks_missing_preflight_and_handoffs():
    state = build_project_state(
        parameters=HandbookProjectParameters(exam_board="AQA", subject="Chemistry"),
    )
    payload = state.to_dict()

    assert payload["schema_version"] == "v0.5-handbook-project-manager"
    assert payload["project_status"] == "blocked"
    assert payload["required_sequence"] == REQUIRED_SEQUENCE
    assert "level" in payload["missing_preflight"]
    assert "host_llm" == payload["handoffs"][0]["from_role"]
    assert payload["handoffs"][2]["to_role"] == "final_reviewer"


def test_coordinator_prompt_exposes_lightweight_workflow():
    prompt = build_coordinator_prompt(
        HandbookProjectParameters(
            exam_board="Cambridge",
            level="igcse",
            subject="Economics",
            term_support_language="zh-CN",
            explanation_style="friendly",
            infographic_capability="no",
            image_method="prompt-queue",
        )
    )

    assert "Lightweight Handbook Workflow Coordinator" in prompt
    assert "Analyst -> Writer -> Reviewer" in prompt
    assert "not mandatory separate agents" in prompt
    assert "missing_preflight" in prompt
    assert "handbook-project-manager.json" in prompt


def test_write_coordinator_artifacts_records_deliverables(tmp_path):
    (tmp_path / "guide.html").write_text("<h1>Guide</h1>", encoding="utf-8")

    payload = write_coordinator_artifacts(
        tmp_path,
        HandbookProjectParameters(
            exam_board="AQA",
            level="igcse",
            subject="Chemistry",
            term_support_language="en",
            explanation_style="friendly",
            infographic_capability="no",
        ),
        current_phase="inspection",
        quality_gates_passed=["analyst", "writer"],
    )

    assert payload["current_phase"] == "inspection"
    assert payload["deliverables"]["guide_html"] == str(tmp_path / "guide.html")
    state = json.loads((tmp_path / "handbook-project-manager.json").read_text(encoding="utf-8"))
    assert state["quality_gates_passed"] == ["analyst", "writer"]
    assert (tmp_path / "handbook-project-manager-prompt.md").exists()
