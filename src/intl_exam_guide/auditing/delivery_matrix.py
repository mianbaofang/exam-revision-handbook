from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from intl_exam_guide.validation.checks import is_svg_repetition_problem, summary_int


@dataclass(frozen=True)
class DeliveryExpectation:
    min_topics: int
    min_practice_per_topic: int
    require_assessments: bool
    require_visual_manifest: bool
    allow_pending_infographics: bool
    allow_pending_concepts: bool = False
    allow_repetitive_svg: bool = False


@dataclass(frozen=True)
class DeliveryCase:
    id: str
    provider: str
    level: str
    subject: str
    language: str
    claim_status: str
    expected: DeliveryExpectation


def load_delivery_matrix(path: Path) -> list[DeliveryCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases: list[DeliveryCase] = []
    for item in raw:
        expected = DeliveryExpectation(**item["expected"])
        cases.append(
            DeliveryCase(
                id=item["id"],
                provider=item["provider"],
                level=item["level"],
                subject=item["subject"],
                language=item["language"],
                claim_status=item["claim_status"],
                expected=expected,
            )
        )
    return cases


def evaluate_case_summary(case: DeliveryCase, summary: dict[str, object]) -> list[str]:
    failures: list[str] = []
    topics = summary_int(summary, "topics")
    practice = summary_int(summary, "practice_cards")
    assessments = summary_int(summary, "assessments")
    if topics < case.expected.min_topics:
        failures.append(
            f"{case.id}: expected at least {case.expected.min_topics} topics, got {topics}"
        )
    if topics and practice < topics * case.expected.min_practice_per_topic:
        failures.append(f"{case.id}: expected practice coverage for each topic")
    if case.expected.require_assessments and assessments < 1:
        failures.append(f"{case.id}: expected assessment extraction")
    if case.expected.require_visual_manifest and not summary.get("has_visual_manifest"):
        failures.append(f"{case.id}: expected visual manifest")
    if (
        not case.expected.allow_pending_concepts
        and case.claim_status == "verified"
        and summary_int(summary, "pending_concept_explanations")
    ):
        failures.append(
            f"{case.id}: pending concept explanations are not allowed for verified delivery"
        )
    if not case.expected.allow_pending_infographics and summary_int(
        summary, "pending_infographic_assets"
    ):
        failures.append(f"{case.id}: pending infographic assets are not allowed for final samples")
    if case.claim_status == "verified":
        delivery_status = str(summary.get("delivery_status") or "")
        if delivery_status and delivery_status != "ready":
            failures.append(
                f"{case.id}: verified delivery must have ready status, got {delivery_status}"
            )
    if case.claim_status == "verified" and not case.expected.allow_repetitive_svg:
        svg_total = summary_int(summary, "svg_files")
        title_problem = False
        structure_problem = False
        if svg_total:
            title_problem = is_svg_repetition_problem(
                svg_total,
                summary_int(summary, "svg_unique_titles", svg_total),
                summary_int(summary, "svg_max_title_repeats"),
            )
            structure_problem = is_svg_repetition_problem(
                svg_total,
                summary_int(summary, "svg_unique_structures", svg_total),
                summary_int(summary, "svg_max_structure_repeats"),
            )
        if title_problem or structure_problem:
            failures.append(
                f"{case.id}: SVG visual drafts are too repetitive for verified delivery"
            )
    return failures
