from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SAMPLES: dict[str, dict[str, int | str]] = {
    "mathematics-9260-sample": {
        "topics": 90,
        "practice_cards": 180,
        "infographics": 39,
        "language": "en",
    },
    "economics-9214-sample": {
        "topics": 38,
        "practice_cards": 76,
        "infographics": 38,
        "language": "en",
    },
    "chemistry-9202-sample": {
        "topics": 35,
        "practice_cards": 70,
        "infographics": 18,
        "language": "en",
    },
}

GENERATED_STATUSES = {
    "generated",
    "reviewed",
    "reviewed-generated",
    "provider-selected-generated",
}
RELEASE_STATUSES = {"candidate", "draft", "final-ready", "certified"}
PENDING_STATUSES = {
    "external-generation-required",
    "provider-selected-pending-generation",
    "infographic-provider-required",
}
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
BAD_MIXED_LABELS = [
    "Chinese / English",
    "中文 / English",
    "图文学习页 / Visual Guide",
    "复习路线 / Study Roadmap",
    "例题 / Worked Example",
]
MIXED_LANGUAGE_SLASH_PATTERN = re.compile(
    r"(?:[\u4e00-\u9fff][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[A-Za-z]"
    r"|[A-Za-z][^<>\n/]{0,40}\s/\s[^<>\n/]{0,40}[\u4e00-\u9fff])"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release sample guide completeness.")
    parser.add_argument(
        "--outputs-root",
        default="./outputs",
        help="Directory containing mathematics/economics/chemistry sample outputs.",
    )
    parser.add_argument(
        "--evidence-manifest",
        default="docs/release-evidence/v0.6.0/manifest.json",
        help="v0.5+ lightweight release-evidence manifest.",
    )
    parser.add_argument(
        "--legacy-outputs",
        action="store_true",
        help="Verify the legacy ignored outputs/*-sample directories instead of v0.5 evidence.",
    )
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Allow pending infographic assets. Use only before final image generation.",
    )
    args = parser.parse_args()

    if not args.legacy_outputs:
        return verify_release_evidence(Path(args.evidence_manifest).resolve())
    return verify_legacy_outputs(Path(args.outputs_root).resolve(), args.allow_pending)


def verify_legacy_outputs(outputs_root: Path, allow_pending: bool) -> int:
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for sample, expected in SAMPLES.items():
        row, sample_failures = verify_sample(outputs_root / sample, sample, expected, allow_pending)
        rows.append(row)
        failures.extend(sample_failures)

    print(
        json.dumps(
            {"outputs_root": str(outputs_root), "samples": rows}, ensure_ascii=False, indent=2
        )
    )
    if failures:
        print("\nRelease sample verification failed:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


def verify_release_evidence(manifest_path: Path) -> int:
    failures: list[str] = []
    manifest = read_json(manifest_path, {})
    if not isinstance(manifest, dict):
        failures.append(f"{manifest_path}: release evidence manifest is not an object")
        manifest = {}
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        failures.append(f"{manifest_path}: entries must be a non-empty list")
        entries = []
    release = str(manifest.get("release") or "")
    if not supported_release_version(release):
        failures.append(f"{manifest_path}: release must be a v0.5.0+ version")
    if str(manifest.get("overall_status") or "") not in RELEASE_STATUSES:
        failures.append(
            f"{manifest_path}: overall_status must be one of {sorted(RELEASE_STATUSES)}"
        )
    linked_report = manifest.get("linked_report")
    repo_root = manifest_path.parents[3]
    if (
        isinstance(linked_report, str)
        and linked_report
        and not (repo_root / linked_report).exists()
    ):
        failures.append(f"{manifest_path}: linked_report does not exist: {linked_report}")

    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append(f"{manifest_path}: entry is not an object")
            continue
        row, entry_failures = verify_evidence_entry(entry)
        rows.append(row)
        failures.extend(entry_failures)

    print(
        json.dumps(
            {"evidence_manifest": str(manifest_path), "entries": rows}, ensure_ascii=False, indent=2
        )
    )
    if failures:
        print("\nRelease evidence verification failed:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    return 0


def supported_release_version(release: str) -> bool:
    match = re.fullmatch(r"v(\d+)\.(\d+)(?:\.(\d+))?(?:[-+].*)?", release)
    if not match:
        return False
    major, minor = (int(match.group(1)), int(match.group(2)))
    return (major, minor) >= (0, 5)


def verify_evidence_entry(entry: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    entry_id = str(entry.get("id") or "<missing-id>")
    failures: list[str] = []
    required = ["id", "status", "provider", "level", "subject", "language", "commands"]
    for key in required:
        if not entry.get(key):
            failures.append(f"{entry_id}: missing {key}")
    status = str(entry.get("status") or "")
    if status not in RELEASE_STATUSES:
        failures.append(f"{entry_id}: status must be one of {sorted(RELEASE_STATUSES)}")
    commands = entry.get("commands")
    if not isinstance(commands, list) or not commands:
        failures.append(f"{entry_id}: commands must be a non-empty list")

    summary = entry.get("validation_summary")
    if not isinstance(summary, dict):
        failures.append(f"{entry_id}: validation_summary must be an object")
        summary = {}
    if int(summary.get("error_count") or 0) != 0:
        failures.append(f"{entry_id}: validation_summary error_count must be 0")

    final_review = entry.get("final_review")
    if not isinstance(final_review, dict):
        failures.append(f"{entry_id}: final_review must be an object")
        final_review = {}
    must_not_present = final_review.get("must_not_present_as_final")
    pending_concepts = int(summary.get("pending_concept_explanations") or 0)
    pending_images = int(summary.get("pending_infographic_assets") or 0)
    if status in {"final-ready", "certified"}:
        if pending_concepts or pending_images:
            failures.append(
                f"{entry_id}: final-ready/certified entries cannot have pending concept or image work"
            )
        if must_not_present is not False:
            failures.append(
                f"{entry_id}: final-ready/certified entry must allow final presentation"
            )
        product_review = entry.get("product_review")
        if not isinstance(product_review, dict):
            failures.append(
                f"{entry_id}: final-ready/certified entry must include product_review evidence"
            )
        else:
            if product_review.get("complete") is not True:
                failures.append(f"{entry_id}: product_review.complete must be true")
            if product_review.get("artifact") != "agent-product-review.json":
                failures.append(
                    f"{entry_id}: product_review.artifact must be agent-product-review.json"
                )
            if product_review.get("decision") != "final-ready":
                failures.append(f"{entry_id}: product_review.decision must be final-ready")
    elif must_not_present is not True:
        failures.append(f"{entry_id}: draft/candidate entry must not be presentable as final")

    output_dir = str(entry.get("output_dir") or "")
    if output_dir and (Path(output_dir).is_absolute() or not output_dir.startswith("outputs/")):
        failures.append(f"{entry_id}: output_dir should be an ignored outputs/ relative path")

    return (
        {
            "id": entry_id,
            "status": status,
            "provider": entry.get("provider"),
            "subject": entry.get("subject"),
            "topics": summary.get("topics"),
            "pending_concepts": pending_concepts,
            "pending_images": pending_images,
            "must_not_present_as_final": must_not_present,
        },
        failures,
    )


def verify_sample(
    sample_dir: Path,
    sample: str,
    expected: dict[str, int | str],
    allow_pending: bool,
) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    validation_path = sample_dir / "validation.json"
    run_options_path = sample_dir / "run-options.json"
    manifest_path = sample_dir / "images" / "visual_manifest.json"
    html_path = sample_dir / "guide.html"
    pdf_path = sample_dir / "guide.pdf"
    final_review_path = sample_dir / "final-review-packet.json"
    delivery_contract_path = sample_dir / "delivery-contract.json"
    product_review_path = sample_dir / "agent-product-review.json"

    required_files = [validation_path, run_options_path, manifest_path, html_path]
    if not allow_pending:
        required_files.extend(
            [pdf_path, final_review_path, delivery_contract_path, product_review_path]
        )
    for path in required_files:
        if not path.exists():
            failures.append(f"{sample}: missing {path.name}")

    validation = read_json(validation_path, {})
    raw_run_options = read_json(run_options_path, {})
    run_options = raw_run_options if isinstance(raw_run_options, dict) else {}
    final_review = read_json(final_review_path, {})
    delivery_contract = read_json(delivery_contract_path, {})
    product_review = read_json(product_review_path, {})
    raw_manifest = read_json(manifest_path, [])
    manifest = manifest_entries_from_payload(raw_manifest)
    if manifest is None:
        failures.append(
            f"{sample}: visual_manifest.json is not a legacy list or schema_version 2 object"
        )
        manifest = []
    html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
    raw_review = validation.get("review_summary", {}) if isinstance(validation, dict) else {}
    review = raw_review if isinstance(raw_review, dict) else {}
    issues = validation.get("issues", []) if isinstance(validation, dict) else []
    issue_errors = [issue for issue in issues if issue.get("severity") == "error"]
    if issue_errors:
        failures.append(f"{sample}: validation has {len(issue_errors)} error issue(s)")
    if not allow_pending:
        final_failures = final_delivery_failures(
            sample,
            validation,
            final_review,
            delivery_contract,
            product_review,
            hashlib.sha256(html.encode("utf-8")).hexdigest(),
        )
        failures.extend(final_failures)

    if review.get("topics") != expected["topics"]:
        failures.append(
            f"{sample}: expected {expected['topics']} topics, got {review.get('topics')}"
        )
    if review.get("practice_cards") != expected["practice_cards"]:
        failures.append(
            f"{sample}: expected {expected['practice_cards']} practice cards, got {review.get('practice_cards')}"
        )
    if run_options.get("output_language") != expected["language"]:
        failures.append(
            f"{sample}: expected language {expected['language']}, got {run_options.get('output_language')}"
        )
    duplicate_topics = count_duplicate_practice_topics(validation)
    if duplicate_topics:
        failures.append(f"{sample}: {duplicate_topics} topic(s) have duplicate practice questions")

    generated, pending, missing_files = count_infographics(sample_dir / "images", manifest)
    if pending and not allow_pending:
        failures.append(f"{sample}: {pending} infographic asset(s) still pending")
    if generated != expected["infographics"] and not allow_pending:
        failures.append(
            f"{sample}: expected {expected['infographics']} generated infographics, got {generated}"
        )
    if missing_files:
        failures.append(f"{sample}: {missing_files} manifest image file(s) are missing")

    broken_images = count_broken_html_images(sample_dir, html)
    if broken_images:
        failures.append(f"{sample}: {broken_images} HTML image(s) reference missing files")
    if not allow_pending and "Infographic Queue" in html:
        failures.append(f"{sample}: HTML still contains pending Infographic Queue blocks")
    if expected["language"] == "en" and re.search(r"[\u4e00-\u9fff]", html):
        failures.append(f"{sample}: English HTML contains Chinese characters")
    for label in mixed_language_label_matches(html):
        failures.append(f"{sample}: mixed-language label remains: {label}")

    row = {
        "sample": sample,
        "topics": review.get("topics"),
        "practice_cards": review.get("practice_cards"),
        "language": run_options.get("output_language"),
        "generated_infographics": generated,
        "pending_infographics": pending,
        "missing_manifest_files": missing_files,
        "broken_html_images": broken_images,
        "has_html": html_path.exists(),
        "has_pdf": pdf_path.exists(),
        "has_final_review": final_review_path.exists(),
        "has_delivery_contract": delivery_contract_path.exists(),
        "has_product_review": product_review_path.exists(),
        "delivery_status": validation.get("delivery_status")
        if isinstance(validation, dict)
        else None,
        "delivery_state": validation.get("delivery_state")
        if isinstance(validation, dict)
        else None,
        "validation_errors": len(issue_errors),
    }
    return row, failures


def read_json(path: Path, fallback: object) -> object:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def manifest_entries_from_payload(payload: object) -> list[dict[str, object]] | None:
    if isinstance(payload, dict) and payload.get("schema_version") == 2:
        visuals = payload.get("visuals")
        if isinstance(visuals, list):
            return [entry for entry in visuals if isinstance(entry, dict)]
        return None
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    return None


def count_infographics(images_dir: Path, manifest: object) -> tuple[int, int, int]:
    if not isinstance(manifest, list):
        return 0, 0, 0
    generated = 0
    pending = 0
    missing = 0
    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("complexity") != "infographic":
            continue
        status = str(entry.get("asset_status") or "")
        filename = str(entry.get("file") or "")
        is_raster = Path(filename).suffix.lower() in RASTER_EXTENSIONS
        exists = bool(filename) and (images_dir / filename).exists()
        if status in GENERATED_STATUSES and is_raster and exists:
            generated += 1
        elif status in PENDING_STATUSES or not exists:
            pending += 1
        if filename and not exists:
            missing += 1
    return generated, pending, missing


def final_delivery_failures(
    sample: str,
    validation: object,
    final_review: object,
    delivery_contract: object,
    product_review: object,
    html_sha256: str,
) -> list[str]:
    failures: list[str] = []
    if not isinstance(validation, dict):
        return [f"{sample}: validation.json is not an object"]
    if validation.get("delivery_status") != "ready":
        failures.append(f"{sample}: delivery_status is not ready")
    if validation.get("delivery_state") != "final-ready":
        failures.append(f"{sample}: delivery_state is not final-ready")

    if not isinstance(delivery_contract, dict):
        failures.append(f"{sample}: delivery-contract.json is not an object")
    elif delivery_contract.get("delivery_state") != "final-ready":
        failures.append(f"{sample}: delivery contract is not final-ready")

    if not isinstance(final_review, dict):
        failures.append(f"{sample}: final-review-packet.json is not an object")
        return failures
    machine = final_review.get("machine_validation")
    agent_review = final_review.get("agent_self_review")
    if not isinstance(machine, dict) or machine.get("delivery_status") != "ready":
        failures.append(f"{sample}: final review delivery_status is not ready")
    if (
        not isinstance(agent_review, dict)
        or agent_review.get("must_not_present_as_final") is not False
    ):
        failures.append(f"{sample}: final review does not allow final presentation")
    product_review_evidence = final_review.get("product_review_evidence")
    if (
        not isinstance(product_review_evidence, dict)
        or product_review_evidence.get("complete") is not True
    ):
        failures.append(f"{sample}: final review is missing complete product-review evidence")
    if not isinstance(product_review, dict):
        failures.append(f"{sample}: agent-product-review.json is not an object")
    elif product_review.get("schema_version") != "v0.6-llm-html-review":
        failures.append(f"{sample}: agent-product-review.json has the wrong schema_version")
    else:
        if product_review.get("reviewer_type") != "llm":
            failures.append(f"{sample}: HTML approval was not authored by an LLM reviewer")
        if product_review.get("html_opened_and_visually_inspected") is not True:
            failures.append(f"{sample}: current HTML was not visibly inspected by the LLM")
        if product_review.get("html_review_passed") is not True:
            failures.append(f"{sample}: current HTML review did not pass")
        for field in (
            "all_topics_reviewed",
            "subject_factual_accuracy_checked",
            "worked_examples_and_answers_checked",
            "all_rendered_visuals_reviewed",
            "visual_semantics_checked",
            "layout_checked",
        ):
            if product_review.get(field) is not True:
                failures.append(f"{sample}: {field} is not true")
        for count_field, ids_field in (
            ("topic_review_count", "reviewed_topic_titles"),
            ("rendered_visual_review_count", "reviewed_visual_ids"),
        ):
            reviewed_ids = product_review.get(ids_field)
            if not isinstance(reviewed_ids, list):
                failures.append(f"{sample}: {ids_field} is not a list")
            elif product_review.get(count_field) != len(reviewed_ids):
                failures.append(f"{sample}: {count_field} does not match {ids_field}")
        if product_review.get("decision") != "approved":
            failures.append(f"{sample}: agent-product-review.json decision is not approved")
        if product_review.get("reviewed_html_sha256") != html_sha256:
            failures.append(f"{sample}: LLM review hash does not match the release HTML")
        if product_review.get("unresolved_fixable_issues") not in (None, []):
            failures.append(f"{sample}: LLM review still has unresolved fixable issues")
    return failures


def count_broken_html_images(sample_dir: Path, html: str) -> int:
    broken = 0
    for match in re.finditer(r'<img[^>]+src="([^"]+)"', html):
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not (sample_dir / src).exists():
            broken += 1
    return broken


def count_duplicate_practice_topics(validation: object) -> int:
    if not isinstance(validation, dict):
        return 0
    # validation.json stores summary only, so inspect guide-plan.json next to it when available.
    html_value = validation.get("html")
    if not isinstance(html_value, str):
        return 0
    plan_path = Path(html_value).with_name("guide-plan.json")
    plan = read_json(plan_path, {})
    if not isinstance(plan, dict):
        return 0
    practice_items = plan.get("practice_items", [])
    if not isinstance(practice_items, list):
        return 0
    by_topic: dict[str, set[str]] = {}
    counts: dict[str, int] = {}
    for item in practice_items:
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic_title") or "")
        question = normalize_question(str(item.get("question") or ""))
        if not topic or not question:
            continue
        by_topic.setdefault(topic, set()).add(question)
        counts[topic] = counts.get(topic, 0) + 1
    return sum(1 for topic, count in counts.items() if len(by_topic.get(topic, set())) < count)


def normalize_question(question: str) -> str:
    question = re.sub(
        r"^(Case file: |Real-life prompt: |Warm-up prompt: |Exam-style prompt: |Story prompt: |Checkpoint challenge: )",
        "",
        question,
    )
    return re.sub(r"\s+", " ", question).strip().lower()


def mixed_language_label_matches(html: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html)
    matches: list[str] = []
    for label in BAD_MIXED_LABELS:
        if label in html:
            matches.append(label)
    for match in MIXED_LANGUAGE_SLASH_PATTERN.finditer(text):
        label = " ".join(match.group(0).split())
        if label not in matches:
            matches.append(label)
    return matches


if __name__ == "__main__":
    raise SystemExit(main())
