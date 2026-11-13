"""Fast quality inspection between handbook writing and final review."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from intl_exam_guide.planning.concept_integration import (
    FALLBACK_VISUAL_DECISION_STATE,
    VISUAL_DECISION_ROUTES,
)
from intl_exam_guide.rendering.output_names import find_handbook_html
from intl_exam_guide.validation.checks import ascii_math_residue_issues
from intl_exam_guide.visuals.manifest import PENDING_WORKFLOW_STATUSES, sync_visual_manifest_entry

QUALITY_INSPECTION_FILE = "quality-inspection.json"
QUALITY_INSPECTION_PROMPT_FILE = "quality-inspection-prompt.md"
QUALITY_INSPECTION_SCHEMA_VERSION = "v0.5-quality-inspection"

PLACEHOLDER_PATTERNS = [
    r"\[\s*(?:insert|llm fills?|todo|placeholder)[^\]]*\]",
    r"(?<!is )\bundefined\b",
    r"(?:value|field|result)\s*[:=]\s*null\b",
    r"TODO:",
]

REQUIRED_VISIBLE_MARKERS = {
    "cover": ["Revision Guide", "Specification"],
    "how_to_use": ["How to Study"],
    "topic_map": ["Study Roadmap", "Topic Map"],
    "topic_guides": ["One-Sentence Essence", "Worked Example"],
    "practice": ["Practice"],
    "exam_structure": ["Assessment", "Paper"],
    "revision_checklist": ["Checklist", "Revision"],
}


@dataclass(frozen=True)
class InspectionIssue:
    severity: str
    category: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class QualityInspectionResult:
    schema_version: str
    inspection_status: str
    recommendation: str
    summary: str
    checks: dict[str, object] = field(default_factory=dict)
    issues: list[InspectionIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.inspection_status == "pass"

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["issues"] = [issue.to_dict() for issue in self.issues]
        return payload


def inspect_handbook_output(output_dir: Path) -> QualityInspectionResult:
    """Run fast format and completeness checks for a rendered handbook directory."""

    issues: list[InspectionIssue] = []
    checks: dict[str, object] = {}
    html_path = find_handbook_html(output_dir)
    html = read_text(html_path)
    visible_text = student_visible_text_from_html(html)

    file_checks = check_required_files(output_dir)
    checks["files"] = file_checks
    for label, present in file_checks.items():
        if not present:
            issues.append(InspectionIssue("error", "files", f"Required file missing: {label}."))

    qualification = read_json(output_dir / "qualification.json")
    topic_count = count_topics(qualification)
    checks["topic_count"] = topic_count
    if topic_count == 0:
        issues.append(InspectionIssue("error", "topics", "qualification.json has no topics."))

    if not visible_text:
        issues.append(
            InspectionIssue(
                "error", "formatting", "Named handbook HTML has no readable student-facing text."
            )
        )
    else:
        module_checks = check_visible_modules(visible_text)
        checks["modules"] = module_checks
        for module_name, present in module_checks.items():
            if not present:
                issues.append(
                    InspectionIssue(
                        "warning"
                        if module_name in {"exam_structure", "revision_checklist"}
                        else "error",
                        "modules",
                        f"Visible handbook marker missing for module: {module_name}.",
                    )
                )

    notation_hits = ascii_math_residue_issues(visible_text)
    checks["ascii_math_residue"] = notation_hits[:20]
    for hit in notation_hits[:10]:
        issues.append(InspectionIssue("error", "notation", hit))

    placeholder_hits = find_placeholder_hits(visible_text)
    checks["placeholder_hits"] = placeholder_hits[:20]
    for hit in placeholder_hits[:10]:
        issues.append(
            InspectionIssue(
                "error", "formatting", f"Placeholder or raw value appears in visible text: {hit}"
            )
        )

    concept_checks = check_concept_explanations(output_dir, topic_count)
    checks["concept_explanations"] = concept_checks
    if concept_checks["present"] and concept_checks["entry_count"] < topic_count:
        issues.append(
            InspectionIssue(
                "error",
                "concepts",
                f"concept_explanations.json covers {concept_checks['entry_count']} of {topic_count} topic(s).",
            )
        )
    missing_visual_decisions = concept_checks.get("missing_visual_decisions", [])
    if missing_visual_decisions:
        sample = ", ".join(str(item) for item in missing_visual_decisions[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "concept_explanations.json must record visual_decision for every topic; "
                f"missing: {sample}.",
            )
        )
    invalid_visual_routes = concept_checks.get("invalid_visual_routes", [])
    if invalid_visual_routes:
        sample = ", ".join(str(item) for item in invalid_visual_routes[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "visual_decision.recommended_route must be one of "
                f"{sorted(VISUAL_DECISION_ROUTES)}; invalid: {sample}.",
            )
        )
    fallback_visual_decisions = concept_checks.get("fallback_visual_decisions", [])
    if fallback_visual_decisions:
        sample = ", ".join(str(item) for item in fallback_visual_decisions[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "visual_decision must be written by the Writer, not inserted by Python as a draft fallback; "
                f"fallback: {sample}.",
            )
        )
    missing_no_visual_reasons = concept_checks.get("missing_no_visual_reasons", [])
    if missing_no_visual_reasons:
        sample = ", ".join(str(item) for item in missing_no_visual_reasons[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "text-ok visual_decision entries must explain why no visual helps learning; "
                f"missing reason: {sample}.",
            )
        )
    text_ok_with_visual_specs = concept_checks.get("text_ok_with_visual_specs", [])
    if text_ok_with_visual_specs:
        sample = ", ".join(str(item) for item in text_ok_with_visual_specs[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "text-ok visual_decision entries must not include visual_spec; "
                f"contradictory entries: {sample}.",
            )
        )
    missing_visual_specs = concept_checks.get("missing_visual_specs", [])
    if missing_visual_specs:
        sample = ", ".join(str(item) for item in missing_visual_specs[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "non-text visual_decision routes must include visual_spec; "
                f"missing visual_spec: {sample}.",
            )
        )
    missing_visual_guidance = concept_checks.get("missing_visual_guidance", [])
    if missing_visual_guidance:
        sample = ", ".join(str(item) for item in missing_visual_guidance[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "Every Writer topic must include topic-specific visual_guidance; "
                f"missing: {sample}.",
            )
        )
    incomplete_visual_guidance = concept_checks.get("incomplete_visual_guidance", [])
    if incomplete_visual_guidance:
        sample = ", ".join(str(item) for item in incomplete_visual_guidance[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "visual_guidance is incomplete for these topics; "
                f"required composition, reading_order, required_elements, and student_inference: {sample}.",
            )
        )
    text_ok_visual_guidance_errors = concept_checks.get("text_ok_visual_guidance_errors", [])
    if text_ok_visual_guidance_errors:
        sample = ", ".join(str(item) for item in text_ok_visual_guidance_errors[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "text-ok topics must use visual_kind='none' and a concrete rationale matching "
                f"no_visual_reason; invalid: {sample}.",
            )
        )
    external_route_svg_downgrades = concept_checks.get("external_route_svg_downgrades", [])
    if external_route_svg_downgrades:
        sample = ", ".join(str(item) for item in external_route_svg_downgrades[:5])
        issues.append(
            InspectionIssue(
                "error",
                "visuals",
                "A verified external image route is available; exact SVG/Kroki requires a "
                f"topic-specific exclusion reason, and must not be a silent downgrade: {sample}.",
            )
        )

    visual_checks = check_visual_manifest(output_dir)
    checks["visuals"] = visual_checks
    for message in visual_checks.get("issues", []):
        issues.append(InspectionIssue("error", "visuals", str(message)))

    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    status = "fail" if error_count else "pass"
    recommendation = "return_to_writer" if error_count else "pass_to_reviewer"
    summary = (
        f"Checked handbook package: {topic_count} topic(s), {error_count} error(s), "
        f"{warning_count} warning(s)."
    )
    return QualityInspectionResult(
        schema_version=QUALITY_INSPECTION_SCHEMA_VERSION,
        inspection_status=status,
        recommendation=recommendation,
        summary=summary,
        checks=checks,
        issues=issues,
    )


def write_quality_inspection(output_dir: Path) -> Path:
    result = inspect_handbook_output(output_dir)
    path = output_dir / QUALITY_INSPECTION_FILE
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / QUALITY_INSPECTION_PROMPT_FILE).write_text(
        build_quality_inspector_prompt(output_dir),
        encoding="utf-8",
    )
    return path


def build_quality_inspector_prompt(output_dir: Path) -> str:
    """Build the checklist prompt for a fast package check."""

    context = {
        "guide_html": str(find_handbook_html(output_dir)),
        "qualification": str(output_dir / "qualification.json"),
        "syllabus_outline": str(output_dir / "syllabus-outline.json"),
        "concept_explanations": str(output_dir / "concepts" / "concept_explanations.json"),
        "visual_manifest": str(output_dir / "images" / "visual_manifest.json"),
        "output": str(output_dir / QUALITY_INSPECTION_FILE),
    }
    return "\n".join(
        [
            "# Fast Package Check",
            "",
            "## 1. Purpose",
            "",
            "This is a fast format and completeness check for the rendered handbook package.",
            "It does not judge deep teaching quality; the host LLM Reviewer owns that visible-handbook audit.",
            "",
            "## 2. Mission",
            "",
            "Catch obvious structural, schema, placeholder, file, glossary, and visual-manifest problems before handoff.",
            "",
            "## 3. Checklist",
            "",
            "A. Files: named handbook HTML, qualification.json, syllabus-outline.json, guide-plan.json, validation.json, concept_jobs.json.",
            "B. Module structure: cover, how-to-use, topic map, glossary when applicable, topic guides, practice, exam structure, revision checklist.",
            "C. Topic completeness: topic count matches qualification.json and each topic has visible teaching content.",
            "D. Concept import: concept_explanations.json exists when the package is being considered complete; every Writer topic records visual_decision and topic-specific visual_guidance, and text-ok decisions include a concrete matching rationale.",
            "E. Reviewer semantic gate: the host LLM Reviewer must independently reopen every text-ok topic and decide whether any diagram, annotated example, process, apparatus, graph, spatial model, comparison, or richer image would improve learning. A specific-sounding rationale is not proof. If a useful visual is optional, use it and return the topic to the Writer for a non-text route.",
            "F. Formatting: no visible [insert ...], [LLM fills ...], undefined, null, or TODO text.",
            "G. Visuals: manifest exists, visual prompts are not repeated five or more times, pending complex assets are explicit, and the recommended route is distinct from the rendered asset state.",
            "",
            "## 4. Decision",
            "",
            "Output pass only when there are no error-level issues. Warnings may pass to the host LLM Reviewer if they are explicit and non-blocking.",
            "Return fail with specific issues when a required artifact or visible module is missing.",
            "",
            "## 5. Runtime Context",
            "",
            "```json",
            json.dumps(context, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 6. Required JSON Output",
            "",
            "```json",
            json.dumps(
                {
                    "schema_version": QUALITY_INSPECTION_SCHEMA_VERSION,
                    "inspection_status": "pass | fail",
                    "issues": [
                        {
                            "severity": "error | warning",
                            "category": "files | modules | topics | concepts | visuals | formatting",
                            "message": "Specific issue and affected file/topic.",
                        }
                    ],
                    "summary": "Checked X items, found Y issues.",
                    "recommendation": "pass_to_reviewer | return_to_writer",
                },
                ensure_ascii=False,
                indent=2,
            ),
            "```",
        ]
    )


def check_required_files(output_dir: Path) -> dict[str, bool]:
    files = {
        "handbook_html": find_handbook_html(output_dir),
        "qualification.json": output_dir / "qualification.json",
        "syllabus-outline.json": output_dir / "syllabus-outline.json",
        "guide-plan.json": output_dir / "guide-plan.json",
        "validation.json": output_dir / "validation.json",
        "concepts/concept_jobs.json": output_dir / "concepts" / "concept_jobs.json",
        "concepts/concept_explanations.json": output_dir / "concepts" / "concept_explanations.json",
        "images/visual_manifest.json": output_dir / "images" / "visual_manifest.json",
    }
    return {label: path.exists() for label, path in files.items()}


def check_visible_modules(visible_text: str) -> dict[str, bool]:
    lowered = visible_text.lower()
    return {
        module_name: any(marker.lower() in lowered for marker in markers)
        for module_name, markers in REQUIRED_VISIBLE_MARKERS.items()
    }


def check_concept_explanations(output_dir: Path, topic_count: int) -> dict[str, Any]:
    path = output_dir / "concepts" / "concept_explanations.json"
    data = read_json(path)
    if isinstance(data, dict):
        entries = data.get("concept_explanations") or data.get("concepts") or data
    else:
        entries = data
    if isinstance(entries, dict):
        concept_entries = [entry for entry in entries.values() if isinstance(entry, dict)]
        entry_count = len(entries)
    elif isinstance(entries, list):
        concept_entries = [entry for entry in entries if isinstance(entry, dict)]
        entry_count = len(concept_entries)
    else:
        concept_entries = []
        entry_count = 0
    missing_visual_decisions = []
    invalid_visual_routes = []
    fallback_visual_decisions = []
    missing_no_visual_reasons = []
    text_ok_with_visual_specs = []
    missing_visual_specs = []
    missing_visual_guidance = []
    incomplete_visual_guidance = []
    text_ok_visual_guidance_errors = []
    external_route_svg_downgrades = []
    visual_decision_count = 0
    external_route_available = _external_visual_route_available_from_output(output_dir)
    for index, entry in enumerate(concept_entries, start=1):
        title = str(entry.get("topic_title") or entry.get("concept_term") or f"entry {index}")
        visual_decision = entry.get("visual_decision")
        if not isinstance(visual_decision, dict):
            missing_visual_decisions.append(title)
            continue
        visual_decision_count += 1
        route = str(visual_decision.get("recommended_route") or "").strip().lower()
        if route not in VISUAL_DECISION_ROUTES:
            invalid_visual_routes.append(f"{title} ({route or 'missing route'})")
            continue
        workflow_state = str(visual_decision.get("workflow_state") or "").strip()
        source = str(visual_decision.get("source") or "").strip()
        if workflow_state == FALLBACK_VISUAL_DECISION_STATE or source == "python-draft-fallback":
            fallback_visual_decisions.append(title)
        is_fallback = title in fallback_visual_decisions
        has_visual_spec = isinstance(entry.get("visual_spec"), dict)
        reason = str(visual_decision.get("no_visual_reason") or "").strip()
        if route == "text-ok":
            if len(reason) < 12:
                missing_no_visual_reasons.append(title)
            if has_visual_spec:
                text_ok_with_visual_specs.append(title)
        elif not has_visual_spec:
            missing_visual_specs.append(f"{title} ({route})")
        guidance = entry.get("visual_guidance")
        # Python fallbacks are retained for migration/recovery diagnostics and
        # are already blocked by fallback_visual_decisions. Formal Writer
        # entries must carry a separate, topic-specific guidance object.
        if is_fallback:
            continue
        if not isinstance(guidance, dict):
            missing_visual_guidance.append(title)
            continue
        visual_kind = str(guidance.get("visual_kind") or "").strip()
        if route == "text-ok":
            rationale = str(guidance.get("no_visual_rationale") or "").strip()
            if (
                visual_kind.lower() != "none"
                or len(rationale) < 12
                or " ".join(rationale.split()) != " ".join(reason.split())
            ):
                text_ok_visual_guidance_errors.append(title)
            continue
        required_guidance = {
            "composition": guidance.get("composition"),
            "reading_order": guidance.get("reading_order"),
            "required_elements": guidance.get("required_elements"),
            "student_inference": guidance.get("student_inference"),
        }
        missing_labels = [
            label
            for label, value in required_guidance.items()
            if not (
                isinstance(value, str)
                and value.strip()
                or isinstance(value, list)
                and any(str(item).strip() for item in value)
            )
        ]
        if not visual_kind or missing_labels:
            incomplete_visual_guidance.append(
                f"{title} ({', '.join(missing_labels) or 'visual_kind'})"
            )
        if route in {"exact-svg", "kroki-diagram"}:
            exactness_exception = str(guidance.get("exactness_exception") or "").strip()
            external_exclusion = str(
                guidance.get("external_route_exclusion_reason") or ""
            ).strip()
            if len(exactness_exception) < 12:
                incomplete_visual_guidance.append(f"{title} (exactness_exception)")
            if external_route_available and len(external_exclusion) < 12:
                external_route_svg_downgrades.append(f"{title} ({route})")
    return {
        "present": path.exists(),
        "entry_count": entry_count,
        "expected_topics": topic_count,
        "visual_decision_count": visual_decision_count,
        "missing_visual_decisions": missing_visual_decisions,
        "invalid_visual_routes": invalid_visual_routes,
        "fallback_visual_decisions": fallback_visual_decisions,
        "missing_visual_specs": missing_visual_specs,
        "missing_no_visual_reasons": missing_no_visual_reasons,
        "text_ok_with_visual_specs": text_ok_with_visual_specs,
        "missing_visual_guidance": missing_visual_guidance,
        "incomplete_visual_guidance": incomplete_visual_guidance,
        "text_ok_visual_guidance_errors": text_ok_visual_guidance_errors,
        "external_route_svg_downgrades": external_route_svg_downgrades,
        "external_route_available": external_route_available,
    }


def _external_visual_route_available_from_output(output_dir: Path) -> bool:
    """Read the recorded run options without making a new provider decision."""

    candidates = [output_dir / "guide-plan.json", output_dir / "run-options.json"]
    for path in candidates:
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        options = data.get("run_options") if isinstance(data.get("run_options"), dict) else data
        if not isinstance(options, dict):
            continue
        capability = str(options.get("external_visual_capability") or "").strip().lower()
        method = str(options.get("image_method") or "").strip()
        if capability == "yes" and bool(options.get("image_route_verified")) and method:
            return True
    return False


def check_visual_manifest(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "images" / "visual_manifest.json"
    issues: list[str] = []
    entries: list[dict[str, Any]] = []
    manifest_kind = "missing"
    expected_visual_count = _expected_visual_count(output_dir, issues)
    if path.exists():
        try:
            data: Any = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            # A damaged manifest must block, never be treated as an empty one.
            issues.append(f"visual_manifest.json is not readable JSON: {exc}")
            manifest_kind = "invalid"
        else:
            visuals: Any
            if isinstance(data, list):
                manifest_kind = "legacy-list"
                visuals = data
            elif (
                isinstance(data, dict)
                and data.get("schema_version") == 2
                and isinstance(data.get("visuals"), list)
            ):
                manifest_kind = "v2"
                visuals = data["visuals"]
            else:
                manifest_kind = "unsupported"
                issues.append(
                    "visual_manifest.json must be a legacy visual list or a "
                    "schema_version 2 object with a visuals list."
                )
                visuals = []
            invalid_entries = [
                index
                for index, entry in enumerate(visuals, start=1)
                if not isinstance(entry, dict)
            ]
            if invalid_entries:
                issues.append(
                    "visual_manifest.json contains non-object visual entries at positions: "
                    + ", ".join(str(index) for index in invalid_entries[:10])
                    + "."
                )
            entries = [entry for entry in visuals if isinstance(entry, dict)]
            if not entries and expected_visual_count > 0:
                issues.append(
                    "guide-plan.json declares "
                    f"{expected_visual_count} visual brief(s) but visual_manifest.json "
                    "contains no usable visual entries."
                )
    prompts: dict[str, int] = {}
    pending_complex = []
    for raw_entry in entries:
        entry = sync_visual_manifest_entry(raw_entry)
        prompt = str(entry.get("prompt") or "").strip()
        if prompt:
            prompts[prompt] = prompts.get(prompt, 0) + 1
        legacy_status = str(entry.get("asset_status") or "").lower()
        route_value = entry.get("recommended_route")
        route = route_value if isinstance(route_value, dict) else {}
        asset_value = entry.get("rendered_asset")
        asset = asset_value if isinstance(asset_value, dict) else {}
        review_status = str(asset.get("review_status") or entry.get("review_status") or "").lower()
        complexity = str(route.get("legacy_complexity") or entry.get("complexity") or "").lower()
        route_name = str(route.get("route") or "").lower()
        provider = str(route.get("renderer_id") or entry.get("image_provider") or entry.get("renderer_id") or "").lower()
        visual_id = entry.get("id") or entry.get("visual_id") or "unknown"
        if provider == "deterministic-svg":
            issues.append(
                f"{visual_id} uses local deterministic SVG instead of an LLM-approved exact SVG or external infographic asset."
            )
        if complexity == "svg-basic" or route_name in {"exact-svg", "kroki-diagram"}:
            if str(route.get("svg_fit") or entry.get("svg_fit") or "").lower() != "exact":
                issues.append(f"{visual_id} recommended_route is SVG but is not marked svg_fit=exact.")
            if (
                legacy_status == "svg-draft" or str(asset.get("asset_route") or "").endswith("svg")
            ) and review_status not in {"reviewed", "approved"}:
                issues.append(f"{visual_id} rendered SVG asset has not been reviewed or approved.")
        if legacy_status in PENDING_WORKFLOW_STATUSES:
            pending_complex.append(entry.get("id"))
    repeated = [prompt for prompt, count in prompts.items() if count >= 5]
    if repeated:
        issues.append("Five or more visual entries reuse the same prompt.")
    return {
        "present": path.exists(),
        "manifest_kind": manifest_kind,
        "expected_visual_count": expected_visual_count,
        "visual_count": len(entries),
        "pending_complex": [item for item in pending_complex if item],
        "repeated_prompt_count": len(repeated),
        "issues": issues,
    }


def _expected_visual_count(output_dir: Path, issues: list[str]) -> int:
    """Read the plan's visual-brief count without silently accepting bad JSON."""

    path = output_dir / "guide-plan.json"
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(f"guide-plan.json is not readable JSON: {exc}")
        return 0
    if not isinstance(data, dict):
        issues.append("guide-plan.json must contain a JSON object.")
        return 0
    briefs = data.get("visual_briefs")
    if briefs is None:
        return 0
    if not isinstance(briefs, list):
        issues.append("guide-plan.json visual_briefs must be a list when present.")
        return 0
    return len(briefs)


def find_placeholder_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.I):
            hits.append(match.group(0)[:120])
    return hits


def student_visible_text_from_html(html: str) -> str:
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def count_topics(qualification: object) -> int:
    if not isinstance(qualification, dict):
        return 0
    topics = qualification.get("topics")
    return len(topics) if isinstance(topics, list) else 0


def read_json(path: Path, default: object | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {} if default is None else default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")
