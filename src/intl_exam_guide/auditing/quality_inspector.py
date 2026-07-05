"""Fast quality inspection between handbook writing and final review."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

QUALITY_INSPECTION_FILE = "quality-inspection.json"
QUALITY_INSPECTION_PROMPT_FILE = "quality-inspection-prompt.md"
QUALITY_INSPECTION_SCHEMA_VERSION = "v0.5-quality-inspection"

PLACEHOLDER_PATTERNS = [
    r"\[\s*(?:insert|llm fills?|todo|placeholder)[^\]]*\]",
    r"\bundefined\b",
    r"\bnull\b",
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
    html_path = output_dir / "guide.html"
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
                "error", "formatting", "guide.html has no readable student-facing text."
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
    """Build the checklist prompt for an LLM quality_inspector role."""

    context = {
        "guide_html": str(output_dir / "guide.html"),
        "qualification": str(output_dir / "qualification.json"),
        "syllabus_outline": str(output_dir / "syllabus-outline.json"),
        "concept_explanations": str(output_dir / "concepts" / "concept_explanations.json"),
        "visual_manifest": str(output_dir / "images" / "visual_manifest.json"),
        "output": str(output_dir / QUALITY_INSPECTION_FILE),
    }
    return "\n".join(
        [
            "# Quality Inspector",
            "",
            "## 1. Identity",
            "",
            "You are the quality_inspector, the fast format and completeness checker between handbook_writer and final_reviewer.",
            "You do not judge deep teaching quality; the final_reviewer owns that audit.",
            "",
            "## 2. Mission",
            "",
            "Catch obvious structural, schema, placeholder, file, glossary, and visual-manifest problems before the independent final reviewer spends time on the package.",
            "",
            "## 3. Checklist",
            "",
            "A. Files: guide.html, qualification.json, syllabus-outline.json, guide-plan.json, validation.json, concept_jobs.json.",
            "B. Module structure: cover, how-to-use, topic map, glossary when applicable, topic guides, practice, exam structure, revision checklist.",
            "C. Topic completeness: topic count matches qualification.json and each topic has visible teaching content.",
            "D. Concept import: concept_explanations.json exists when the package is being considered for review-ready/final-ready delivery.",
            "E. Formatting: no visible [insert ...], [LLM fills ...], undefined, null, or TODO text.",
            "F. Visuals: manifest exists, visual prompts are not repeated five or more times, pending complex assets are explicit.",
            "",
            "## 4. Decision",
            "",
            "Output pass only when there are no error-level issues. Warnings may pass to final_reviewer if they are explicit and non-blocking.",
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
        "guide.html": output_dir / "guide.html",
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


def check_concept_explanations(output_dir: Path, topic_count: int) -> dict[str, object]:
    path = output_dir / "concepts" / "concept_explanations.json"
    data = read_json(path)
    if isinstance(data, dict):
        entries = data.get("concept_explanations") or data.get("concepts") or data
    else:
        entries = data
    if isinstance(entries, dict):
        entry_count = len(entries)
    elif isinstance(entries, list):
        entry_count = len([entry for entry in entries if isinstance(entry, dict)])
    else:
        entry_count = 0
    return {
        "present": path.exists(),
        "entry_count": entry_count,
        "expected_topics": topic_count,
    }


def check_visual_manifest(output_dir: Path) -> dict[str, object]:
    path = output_dir / "images" / "visual_manifest.json"
    data = read_json(path)
    visuals = data.get("visuals", data) if isinstance(data, dict) else data
    entries = (
        [entry for entry in visuals if isinstance(entry, dict)] if isinstance(visuals, list) else []
    )
    prompts: dict[str, int] = {}
    pending_complex = []
    issues = []
    for entry in entries:
        prompt = str(entry.get("prompt") or "").strip()
        if prompt:
            prompts[prompt] = prompts.get(prompt, 0) + 1
        status = str(entry.get("asset_status") or "").lower()
        review_status = str(entry.get("review_status") or "").lower()
        complexity = str(entry.get("complexity") or "").lower()
        provider = str(entry.get("image_provider") or entry.get("renderer_id") or "").lower()
        visual_id = entry.get("id") or entry.get("visual_id") or "unknown"
        if provider == "deterministic-svg":
            issues.append(
                f"{visual_id} uses local deterministic SVG instead of an LLM-approved exact SVG or external infographic asset."
            )
        if complexity == "svg-basic":
            if str(entry.get("svg_fit") or "").lower() != "exact":
                issues.append(f"{visual_id} is SVG but is not marked svg_fit=exact.")
            if status == "svg-draft" or review_status not in {"reviewed", "approved"}:
                issues.append(f"{visual_id} SVG asset has not been reviewed or approved.")
        if complexity == "infographic" and status in {
            "external-generation-required",
            "infographic-provider-required",
            "provider-selected-pending-generation",
            "svg-fallback-needs-review",
        }:
            pending_complex.append(entry.get("id"))
    repeated = [prompt for prompt, count in prompts.items() if count >= 5]
    if repeated:
        issues.append("Five or more visual entries reuse the same prompt.")
    return {
        "present": path.exists(),
        "visual_count": len(entries),
        "pending_complex": [item for item in pending_complex if item],
        "repeated_prompt_count": len(repeated),
        "issues": issues,
    }


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
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {} if default is None else default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")
