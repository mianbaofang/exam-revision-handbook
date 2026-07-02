import json

from intl_exam_guide.cli import main
from intl_exam_guide.rendering.delivery_panel import state_from_artifacts
from intl_exam_guide.validation.checks import ValidationIssue, delivery_status_from_issues


def test_delivery_status_blocks_errors_before_image_warnings():
    assert (
        delivery_status_from_issues(
            [ValidationIssue("error", "bad")],
            {"pending_infographic_assets": 10},
        )
        == "blocked_errors"
    )


def test_delivery_status_marks_pending_infographics_as_draft():
    assert delivery_status_from_issues([], {"pending_infographic_assets": 2}) == "draft_needs_image_review"


def test_delivery_status_marks_pending_concepts_before_images():
    assert (
        delivery_status_from_issues(
            [],
            {"pending_concept_explanations": 2, "pending_infographic_assets": 2},
        )
        == "draft_needs_concept_review"
    )


def test_delivery_status_ready_when_clean_and_no_pending_infographics():
    assert (
        delivery_status_from_issues(
            [],
            {"pending_concept_explanations": 0, "pending_infographic_assets": 0},
        )
        == "ready"
    )


def test_delivery_panel_does_not_upgrade_blocked_validation_to_review_ready():
    assert (
        state_from_artifacts(
            0,
            0,
            {"agent_self_review": {"status": "ready"}},
            {"delivery_status": "blocked_errors", "delivery_state": "candidate"},
        )
        == "candidate"
    )


def test_delivery_panel_requires_final_review_before_final_ready():
    assert (
        state_from_artifacts(
            0,
            0,
            {},
            {"delivery_status": "ready", "delivery_state": "review-ready"},
        )
        == "review-ready"
    )
    assert (
        state_from_artifacts(
            0,
            0,
            {"agent_self_review": {"status": "ready"}},
            {"delivery_status": "ready", "delivery_state": "final-ready"},
        )
        == "review-ready"
    )
    assert (
        state_from_artifacts(
            0,
            0,
            {
                "agent_self_review": {"status": "ready"},
                "product_review_evidence": {"complete": True},
            },
            {"delivery_status": "ready", "delivery_state": "final-ready"},
        )
        == "final-ready"
    )


def test_validation_json_contains_delivery_status(tmp_path):
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

    assert result == 0
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["delivery_status"] == "draft_needs_concept_review"
    assert validation["delivery_state"] == "draft"
    contract = json.loads((output_dir / "delivery-contract.json").read_text(encoding="utf-8"))
    assert contract["delivery_state"] == "draft"
    assert len(contract["learning_units"]) == validation["review_summary"]["source_topics"]
    assert validation["review_summary"]["concept_jobs"] == validation["review_summary"]["topic_guides"]
    assert validation["review_summary"]["pending_concept_explanations"] == validation["review_summary"]["topic_guides"]
