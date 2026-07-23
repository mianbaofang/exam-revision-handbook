from pathlib import Path

from intl_exam_guide.auditing.delivery_matrix import (
    DeliveryCase,
    DeliveryExpectation,
    evaluate_case_summary,
    load_delivery_matrix,
)


def test_delivery_matrix_loads_explicit_claims():
    cases = load_delivery_matrix(Path("tests/fixtures/delivery_matrix.json"))

    assert {case.provider for case in cases} >= {
        "oxfordaqa",
        "pearson",
        "cambridge",
        "collegeboard",
    }
    assert all(
        case.level in {"igcse", "international_as_a_level", "advanced_placement"}
        for case in cases
    )
    assert all(case.expected.min_topics >= 5 for case in cases)
    assert all(case.claim_status in {"verified", "candidate", "unsupported"} for case in cases)


def test_delivery_matrix_rejects_structurally_passing_but_thin_summary():
    case = DeliveryCase(
        id="sample",
        provider="oxfordaqa",
        level="igcse",
        subject="Chemistry",
        language="zh-CN",
        claim_status="verified",
        expected=DeliveryExpectation(
            min_topics=20,
            min_practice_per_topic=1,
            require_assessments=True,
            require_visual_manifest=True,
            allow_pending_infographics=True,
        ),
    )
    summary = {
        "topics": 6,
        "practice_cards": 6,
        "assessments": 0,
        "has_visual_manifest": False,
    }

    assert evaluate_case_summary(case, summary) == [
        "sample: expected at least 20 topics, got 6",
        "sample: expected assessment extraction",
        "sample: expected visual manifest",
    ]


def test_delivery_matrix_can_disallow_pending_infographics_for_final_samples():
    case = DeliveryCase(
        id="sample-final",
        provider="cambridge",
        level="igcse",
        subject="Economics",
        language="en",
        claim_status="verified",
        expected=DeliveryExpectation(
            min_topics=10,
            min_practice_per_topic=1,
            require_assessments=False,
            require_visual_manifest=False,
            allow_pending_infographics=False,
        ),
    )
    summary = {
        "topics": 10,
        "practice_cards": 10,
        "pending_infographic_assets": 1,
    }

    assert evaluate_case_summary(case, summary) == [
        "sample-final: pending infographic assets are not allowed for final samples"
    ]


def test_delivery_matrix_rejects_verified_outputs_with_unreviewed_concepts_or_draft_status():
    case = DeliveryCase(
        id="sample-concepts",
        provider="oxfordaqa",
        level="international_as_a_level",
        subject="Mathematics",
        language="zh-CN",
        claim_status="verified",
        expected=DeliveryExpectation(
            min_topics=6,
            min_practice_per_topic=1,
            require_assessments=True,
            require_visual_manifest=True,
            allow_pending_infographics=True,
        ),
    )
    summary = {
        "topics": 8,
        "practice_cards": 8,
        "assessments": 1,
        "has_visual_manifest": True,
        "pending_concept_explanations": 2,
        "delivery_status": "draft_needs_concept_review",
    }

    assert evaluate_case_summary(case, summary) == [
        "sample-concepts: pending concept explanations are not allowed for verified delivery",
        "sample-concepts: verified delivery must have ready status, got draft_needs_concept_review",
    ]


def test_delivery_matrix_rejects_repetitive_svg_drafts_for_verified_samples():
    case = DeliveryCase(
        id="sample-visuals",
        provider="pearson",
        level="igcse",
        subject="Accounting",
        language="en",
        claim_status="verified",
        expected=DeliveryExpectation(
            min_topics=10,
            min_practice_per_topic=1,
            require_assessments=True,
            require_visual_manifest=True,
            allow_pending_infographics=True,
        ),
    )
    summary = {
        "topics": 22,
        "practice_cards": 44,
        "assessments": 2,
        "has_visual_manifest": True,
        "svg_files": 22,
        "svg_unique_titles": 4,
        "svg_max_title_repeats": 8,
        "svg_unique_structures": 4,
        "svg_max_structure_repeats": 8,
    }

    assert evaluate_case_summary(case, summary) == [
        "sample-visuals: SVG visual drafts are too repetitive for verified delivery"
    ]
