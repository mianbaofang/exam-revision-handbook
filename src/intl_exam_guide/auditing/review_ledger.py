from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from intl_exam_guide.models import GuidePlan
from intl_exam_guide.planning.identifiers import stable_requirement_id
from intl_exam_guide.rendering.render_snapshot import inspect_current_render
from intl_exam_guide.rendering.visual_assets import load_visual_manifest


REVIEW_LEDGER_DIR = "review-ledger"
REVIEW_LEDGER_INDEX = "index.json"
REVIEW_LEDGER_SCHEMA_VERSION = "v1-review-ledger-index"
TOPIC_SHARD_SCHEMA_VERSION = "v1-topic-review-shard"
VISUAL_SHARD_SCHEMA_VERSION = "v1-visual-review-shard"
HOLISTIC_REVIEW_SCHEMA_VERSION = "v1-holistic-html-review"
MAX_REVIEWS_PER_SHARD = 25


def expected_review_items(output_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    plan = _load_plan(output_dir, issues)
    topics = [
        {"topic_id": topic_id, "topic_title": title}
        for topic_id, title in _expected_topics(plan, issues).items()
    ]
    visuals = [
        {"visual_id": visual_id, "asset_sha256": asset_hash}
        for visual_id, asset_hash in _expected_visuals(output_dir).items()
    ]
    return topics, visuals


def write_review_ledger_index(output_dir: Path) -> Path:
    """Hash LLM-authored review shards without creating review decisions."""

    output_dir = output_dir.resolve()
    render = inspect_current_render(output_dir)
    if render.get("complete") is not True:
        raise ValueError("Current render snapshot must be complete before indexing review shards.")
    pointer = render.get("pointer")
    if not isinstance(pointer, dict):
        raise ValueError("Current render pointer is unavailable.")
    ledger_dir = output_dir / REVIEW_LEDGER_DIR
    holistic_path = ledger_dir / "holistic.json"
    if not holistic_path.is_file():
        raise ValueError("review-ledger/holistic.json must be written by the LLM Reviewer first.")
    topic_shards = [_indexed_file(path) for path in sorted(ledger_dir.glob("topics-*.json"))]
    visual_shards = [_indexed_file(path) for path in sorted(ledger_dir.glob("visuals-*.json"))]
    payload = {
        "schema_version": REVIEW_LEDGER_SCHEMA_VERSION,
        "render_snapshot_id": pointer.get("snapshot_id"),
        "html_sha256": pointer.get("html_sha256"),
        "topic_shards": topic_shards,
        "visual_shards": visual_shards,
        "holistic_review": _indexed_file(holistic_path),
    }
    index_path = ledger_dir / REVIEW_LEDGER_INDEX
    index_path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return index_path


def review_ledger_evidence(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    ledger_dir = output_dir / REVIEW_LEDGER_DIR
    index_path = ledger_dir / REVIEW_LEDGER_INDEX
    issues: list[dict[str, str]] = []
    render = inspect_current_render(output_dir)
    raw_pointer = render.get("pointer")
    pointer: dict[str, Any] = dict(raw_pointer) if isinstance(raw_pointer, dict) else {}
    snapshot_id = str(pointer.get("snapshot_id") or "")
    html_sha256 = str(pointer.get("html_sha256") or "")
    if render.get("complete") is not True:
        _add(issues, "review.render_snapshot_invalid", "Review ledger has no valid current render.")

    plan = _load_plan(output_dir, issues)
    expected_topics = _expected_topics(plan, issues)
    expected_visuals = _expected_visuals(output_dir)
    index = _read_json_object(index_path)
    if index is None:
        _add(issues, "review.ledger_missing", "Missing or invalid review-ledger/index.json.")
        return _ledger_result(
            issues, index_path, expected_topics, expected_visuals, {}, snapshot_id, html_sha256
        )
    if index.get("schema_version") != REVIEW_LEDGER_SCHEMA_VERSION:
        _add(issues, "review.ledger_schema", "Review ledger index schema_version is unsupported.")
    _check_binding(index, snapshot_id, html_sha256, "review ledger index", issues)

    topic_reviews: list[dict[str, Any]] = []
    visual_reviews: list[dict[str, Any]] = []
    for record in _records(index.get("topic_shards"), "topic_shards", issues):
        shard = _load_indexed_file(ledger_dir, record, issues)
        if shard is not None:
            topic_reviews.extend(
                _validate_shard(
                    shard,
                    TOPIC_SHARD_SCHEMA_VERSION,
                    snapshot_id,
                    html_sha256,
                    "topic",
                    issues,
                )
            )
    for record in _records(index.get("visual_shards"), "visual_shards", issues):
        shard = _load_indexed_file(ledger_dir, record, issues)
        if shard is not None:
            visual_reviews.extend(
                _validate_shard(
                    shard,
                    VISUAL_SHARD_SCHEMA_VERSION,
                    snapshot_id,
                    html_sha256,
                    "visual",
                    issues,
                )
            )

    _validate_topic_reviews(topic_reviews, expected_topics, issues)
    _validate_visual_reviews(visual_reviews, expected_visuals, issues)
    holistic_record = index.get("holistic_review")
    if not isinstance(holistic_record, dict):
        _add(issues, "review.holistic_missing", "Review ledger index has no holistic review.")
    else:
        holistic = _load_indexed_file(ledger_dir, holistic_record, issues)
        if holistic is not None:
            _validate_holistic(holistic, snapshot_id, html_sha256, issues)
    return _ledger_result(
        issues,
        index_path,
        expected_topics,
        expected_visuals,
        index,
        snapshot_id,
        html_sha256,
    )


def _validate_topic_reviews(
    reviews: list[dict[str, Any]],
    expected: dict[str, str],
    issues: list[dict[str, str]],
) -> None:
    reviewed_ids: list[str] = []
    for review in reviews:
        topic_id = str(review.get("topic_id") or "")
        reviewed_ids.append(topic_id)
        if review.get("topic_title") != expected.get(topic_id):
            _add(issues, "review.topic_identity", f"Topic review identity mismatch: {topic_id}.")
        _validate_item_review(
            review,
            topic_id,
            [
                "factual_accuracy_checked",
                "worked_example_checked",
                "source_traceability_checked",
                "teaching_value_checked",
            ],
            issues,
        )
    _validate_exact_coverage(reviewed_ids, set(expected), "topic", issues)


def _validate_visual_reviews(
    reviews: list[dict[str, Any]],
    expected: dict[str, str],
    issues: list[dict[str, str]],
) -> None:
    reviewed_ids: list[str] = []
    for review in reviews:
        visual_id = str(review.get("visual_id") or "")
        reviewed_ids.append(visual_id)
        if str(review.get("asset_sha256") or "") != expected.get(visual_id):
            _add(issues, "review.visual_asset_hash", f"Visual review hash mismatch: {visual_id}.")
        _validate_item_review(
            review,
            visual_id,
            [
                "semantic_contract_checked",
                "semantic_accuracy_checked",
                "teaching_value_checked",
                "layout_checked",
            ],
            issues,
        )
    _validate_exact_coverage(reviewed_ids, set(expected), "visual", issues)


def _validate_item_review(
    review: dict[str, Any],
    item_id: str,
    true_fields: list[str],
    issues: list[dict[str, str]],
) -> None:
    if review.get("decision") != "approved":
        _add(issues, "review.item_not_approved", f"Review decision is not approved: {item_id}.")
    for field in true_fields:
        if review.get(field) is not True:
            _add(issues, "review.item_incomplete", f"{item_id} requires {field}=true.")
    if not isinstance(review.get("findings"), list):
        _add(issues, "review.item_incomplete", f"{item_id} findings must be a list.")
    if not _evidence_locations(review.get("evidence_locations")):
        _add(
            issues,
            "review.item_evidence_missing",
            f"{item_id} requires a screenshot or browser viewport evidence location.",
        )
    if _positive_int(review.get("review_iteration")) is None:
        _add(issues, "review.item_incomplete", f"{item_id} review_iteration must be positive.")


def _validate_holistic(
    review: dict[str, Any],
    snapshot_id: str,
    html_sha256: str,
    issues: list[dict[str, str]],
) -> None:
    if review.get("schema_version") != HOLISTIC_REVIEW_SCHEMA_VERSION:
        _add(issues, "review.holistic_schema", "Holistic review schema_version is unsupported.")
    _check_binding(review, snapshot_id, html_sha256, "holistic review", issues)
    for field in [
        "html_opened_and_visually_inspected",
        "complete_html_reviewed",
        "cover_and_navigation_checked",
        "cross_page_consistency_checked",
        "responsive_layout_checked",
        "notation_and_encoding_checked",
    ]:
        if review.get(field) is not True:
            _add(issues, "review.holistic_incomplete", f"Holistic review requires {field}=true.")
    if review.get("decision") != "approved":
        _add(issues, "review.holistic_not_approved", "Holistic HTML review is not approved.")
    if review.get("unresolved_fixable_issues") not in (None, []):
        _add(issues, "review.holistic_unresolved", "Holistic review has unresolved issues.")
    if not isinstance(review.get("findings"), list):
        _add(issues, "review.holistic_incomplete", "Holistic review findings must be a list.")
    if not _evidence_locations(review.get("evidence_locations")):
        _add(
            issues,
            "review.holistic_evidence_missing",
            "Holistic review requires desktop/mobile screenshot or browser viewport locations.",
        )
    if _positive_int(review.get("review_iteration")) is None:
        _add(issues, "review.holistic_incomplete", "Holistic review_iteration must be positive.")


def _validate_shard(
    shard: dict[str, Any],
    schema_version: str,
    snapshot_id: str,
    html_sha256: str,
    label: str,
    issues: list[dict[str, str]],
) -> list[dict[str, Any]]:
    if shard.get("schema_version") != schema_version:
        _add(issues, f"review.{label}_shard_schema", f"{label} shard schema is unsupported.")
    _check_binding(shard, snapshot_id, html_sha256, f"{label} shard", issues)
    reviews = shard.get("reviews")
    if not isinstance(reviews, list):
        _add(issues, f"review.{label}_shard_invalid", f"{label} shard reviews must be a list.")
        return []
    if len(reviews) > MAX_REVIEWS_PER_SHARD:
        _add(
            issues,
            f"review.{label}_shard_oversized",
            f"{label} shard exceeds {MAX_REVIEWS_PER_SHARD} reviews.",
        )
    return [review for review in reviews if isinstance(review, dict)]


def _validate_exact_coverage(
    reviewed_ids: list[str],
    expected_ids: set[str],
    label: str,
    issues: list[dict[str, str]],
) -> None:
    if len(reviewed_ids) != len(set(reviewed_ids)):
        _add(issues, f"review.{label}_duplicate", f"Review ledger has duplicate {label} IDs.")
    missing = sorted(expected_ids - set(reviewed_ids))
    extra = sorted(set(reviewed_ids) - expected_ids)
    if missing:
        _add(issues, f"review.{label}_missing", f"Review ledger misses {len(missing)} {label}(s).")
    if extra:
        _add(issues, f"review.{label}_unknown", f"Review ledger has {len(extra)} unknown {label}(s).")


def _load_plan(output_dir: Path, issues: list[dict[str, str]]) -> GuidePlan | None:
    path = output_dir / "guide-plan.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("root must be an object")
        return GuidePlan.from_dict(payload)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        _add(issues, "review.plan_invalid", "Review ledger cannot load guide-plan.json.")
        return None


def _expected_topics(
    plan: GuidePlan | None, issues: list[dict[str, str]]
) -> dict[str, str]:
    if plan is None:
        return {}
    topics_by_title = {topic.title: topic for topic in plan.qualification.topics}
    expected: dict[str, str] = {}
    for guide in plan.topic_guides:
        topic = topics_by_title.get(guide.topic_title)
        if topic is None:
            _add(
                issues,
                "review.topic_identity",
                f"Topic guide has no exact qualification topic: {guide.topic_title}.",
            )
            continue
        expected[stable_requirement_id(topic)] = guide.topic_title
    return expected


def _expected_visuals(output_dir: Path) -> dict[str, str]:
    expected: dict[str, str] = {}
    for entry in load_visual_manifest(output_dir / "images"):
        rendered = entry.get("rendered_asset")
        if not isinstance(rendered, dict) or rendered.get("renders_in_html") is not True:
            continue
        visual_id = str(entry.get("visual_id") or entry.get("id") or "")
        raw_asset = entry.get("asset")
        asset: dict[str, Any] = dict(raw_asset) if isinstance(raw_asset, dict) else {}
        asset_hash = str(rendered.get("sha256") or asset.get("sha256") or "")
        if visual_id:
            expected[visual_id] = asset_hash
    return expected


def _records(
    value: object, field: str, issues: list[dict[str, str]]
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _add(issues, "review.ledger_index_invalid", f"Review ledger {field} must be a list.")
        return []
    return [record for record in value if isinstance(record, dict)]


def _load_indexed_file(
    ledger_dir: Path,
    record: dict[str, Any],
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    path = _confined_ledger_path(ledger_dir, record.get("file"))
    if path is None or not path.is_file():
        _add(issues, "review.ledger_file_missing", "Review ledger indexed file is missing.")
        return None
    if str(record.get("sha256") or "") != _file_sha256(path):
        _add(issues, "review.ledger_file_hash", f"Review ledger file hash mismatch: {path.name}.")
        return None
    value = _read_json_object(path)
    if value is None:
        _add(issues, "review.ledger_file_invalid", f"Review ledger file is invalid: {path.name}.")
    return value


def _check_binding(
    value: dict[str, Any],
    snapshot_id: str,
    html_sha256: str,
    label: str,
    issues: list[dict[str, str]],
) -> None:
    if value.get("render_snapshot_id") != snapshot_id or value.get("html_sha256") != html_sha256:
        _add(issues, "review.binding_mismatch", f"{label} is not bound to the current render.")


def _ledger_result(
    issues: list[dict[str, str]],
    index_path: Path,
    expected_topics: dict[str, str],
    expected_visuals: dict[str, str],
    index: dict[str, Any],
    snapshot_id: str,
    html_sha256: str,
) -> dict[str, object]:
    return {
        "complete": not issues,
        "issues": issues,
        "index_path": str(index_path),
        "index_sha256": _file_sha256(index_path) if index_path.is_file() else None,
        "index": index,
        "render_snapshot_id": snapshot_id,
        "html_sha256": html_sha256,
        "expected_topic_count": len(expected_topics),
        "expected_visual_count": len(expected_visuals),
    }


def _indexed_file(path: Path) -> dict[str, str]:
    return {"file": path.name, "sha256": _file_sha256(path)}


def _confined_ledger_path(ledger_dir: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = ledger_dir / value
    try:
        resolved = candidate.resolve()
        resolved.relative_to(ledger_dir.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _positive_int(value: object) -> int | None:
    try:
        number = int(str(value))
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _evidence_locations(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _add(issues: list[dict[str, str]], code: str, message: str) -> None:
    issues.append({"code": code, "message": message})
