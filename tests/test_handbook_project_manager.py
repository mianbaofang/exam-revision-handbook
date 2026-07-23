import json

from intl_exam_guide.coordination import (
    REQUIRED_SEQUENCE,
    HandbookProjectParameters,
    build_coordinator_prompt,
    build_project_state,
    parameters_from_generation_args,
    write_coordinator_artifacts,
)


def test_project_state_tracks_missing_preflight_and_handoffs():
    state = build_project_state(
        parameters=HandbookProjectParameters(exam_board="AQA", subject="Chemistry"),
    )
    payload = state.to_dict()

    assert payload["schema_version"] == "v0.6-handbook-project-manager"
    assert payload["project_status"] == "blocked"
    assert payload["required_sequence"] == REQUIRED_SEQUENCE
    assert "level" in payload["missing_preflight"]
    assert "course_market" in payload["missing_preflight"]
    assert "output_dir" in payload["missing_preflight"]
    assert "host_llm" == payload["handoffs"][0]["from_role"]
    assert payload["handoffs"][2]["to_role"] == "final_reviewer"


def test_coordinator_prompt_exposes_lightweight_workflow():
    prompt = build_coordinator_prompt(
        HandbookProjectParameters(
            exam_board="Cambridge",
            level="igcse",
            course_market="international",
            subject="Economics",
            term_support_language="zh-CN",
            explanation_style="friendly",
            infographic_capability="no",
            image_method="prompt-queue",
        )
    )

    assert "Boundary Compliance Gate" in prompt
    assert "Do not invent shortcuts" in prompt
    assert "allocate visuals by subject quota" in prompt

    assert "Lightweight Handbook Workflow Coordinator" in prompt
    assert "Analyst -> Writer -> Reviewer" in prompt
    assert "not mandatory separate agents" in prompt
    assert "missing_preflight" in prompt
    assert "handbook-project-manager.json" in prompt
    assert "provide or enable an external image-generation Skill or tool" in prompt
    assert "Do not infer a route" in prompt
    assert "Any missing or invalid field keeps the project blocked" in prompt
    assert "first-response form" in prompt
    assert "formal=exam-oriented" in prompt
    assert "explanation_style=<fixed value>" in prompt
    assert "course_market=<international|uk-domestic|not-applicable>" in prompt
    assert "Never infer course_market" in prompt


def test_write_coordinator_artifacts_records_deliverables(tmp_path):
    (tmp_path / "guide.html").write_text("<h1>Guide</h1>", encoding="utf-8")

    payload = write_coordinator_artifacts(
        tmp_path,
        HandbookProjectParameters(
            exam_board="AQA",
            level="igcse",
            course_market="international",
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


def test_generation_image_provider_never_infers_user_preflight_answer():
    parameters = parameters_from_generation_args(
        provider="Cambridge",
        level="a-level",
        subject="Physics",
        exam_year="2027",
        term_support_language="zh-CN",
        explanation_style="friendly",
        image_provider="custom",
    )

    assert parameters.image_method == "custom"
    assert parameters.infographic_capability is None
    assert "infographic_capability" in parameters.missing_required()


def test_preflight_state_rejects_missing_workflow_and_invalid_style(tmp_path):
    state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="AQA",
            level="igcse",
            course_market="international",
            subject="Biology",
            exam_year="2027",
            term_support_language="en",
            explanation_style="cinematic",
            infographic_capability="no",
        ),
        output_dir=tmp_path,
    )

    payload = state.to_dict()
    assert payload["project_status"] == "blocked"
    assert "workflow_mode" in payload["missing_preflight"]
    assert payload["invalid_preflight"] == ["explanation_style"]


def test_preflight_state_requires_route_verification_when_capability_is_yes(tmp_path):
    state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="AQA",
            level="igcse",
            course_market="international",
            subject="Biology",
            exam_year="2027",
            term_support_language="en",
            explanation_style="formal",
            infographic_capability="yes",
            image_method="imagegen",
            workflow_mode="single-host",
        ),
        output_dir=tmp_path,
    )

    assert state.project_status == "blocked"
    assert "image_route_verified" in state.missing_preflight


def test_complete_structured_preflight_unblocks_the_workflow(tmp_path):
    state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="CAIE",
            level="a-level",
            course_market="international",
            subject="Physics 9702",
            exam_year="2027",
            term_support_language="zh-CN",
            explanation_style="formal",
            infographic_capability="no",
            workflow_mode="single-host",
            batch_scope="one-handbook",
        ),
        output_dir=tmp_path,
    )

    assert state.project_status == "in_progress"
    assert state.missing_preflight == []
    assert state.invalid_preflight == []


def test_scoped_preflight_requires_an_explicit_course_market(tmp_path):
    state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="AQA",
            level="AS",
            subject="Mathematics",
            exam_year="2027",
            term_support_language="en",
            explanation_style="formal",
            infographic_capability="no",
            workflow_mode="single-host",
            batch_scope="one-handbook",
        ),
        output_dir=tmp_path,
    )

    assert state.project_status == "blocked"
    assert "course_market" in state.missing_preflight


def test_course_market_enforces_route_specific_values(tmp_path):
    uk_state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="Edexcel",
            level="IGCSE",
            course_market="uk-domestic",
            subject="Chemistry",
            exam_year="2027",
            term_support_language="en",
            explanation_style="formal",
            infographic_capability="no",
            workflow_mode="single-host",
            batch_scope="one-handbook",
        ),
        output_dir=tmp_path,
    )
    ap_state = build_project_state(
        parameters=HandbookProjectParameters(
            exam_board="College Board AP",
            level="AP",
            course_market="international",
            subject="Chemistry",
            exam_year="2027",
            term_support_language="en",
            explanation_style="formal",
            infographic_capability="no",
            workflow_mode="single-host",
            batch_scope="one-handbook",
        ),
        output_dir=tmp_path,
    )

    assert uk_state.project_status == "in_progress"
    assert uk_state.invalid_preflight == []
    assert ap_state.project_status == "blocked"
    assert ap_state.invalid_preflight == ["course_market"]
