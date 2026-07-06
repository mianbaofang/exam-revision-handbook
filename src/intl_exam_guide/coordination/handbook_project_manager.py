"""Coordinator prompt and project-state contracts for handbook generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from intl_exam_guide.rendering.output_names import find_handbook_html, find_handbook_pdf

COORDINATOR_FILE = "handbook-project-manager.json"
COORDINATOR_PROMPT_FILE = "handbook-project-manager-prompt.md"
COORDINATOR_SCHEMA_VERSION = "v0.5-handbook-project-manager"

REQUIRED_SEQUENCE = [
    "handbook_project_manager",
    "syllabus_outline_analyst",
    "handbook_writer",
    "quality_inspector",
    "final_reviewer",
]


@dataclass(frozen=True)
class HandbookProjectParameters:
    """User-facing inputs the coordinator must confirm before generation."""

    exam_board: str | None = None
    level: str | None = None
    subject: str | None = None
    subject_code: str | None = None
    exam_year: str | None = None
    term_support_language: str | None = None
    explanation_style: str | None = None
    infographic_capability: str | None = None
    image_method: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def missing_required(self) -> list[str]:
        missing = []
        for field_name in [
            "exam_board",
            "level",
            "subject",
            "term_support_language",
            "explanation_style",
            "infographic_capability",
        ]:
            if not getattr(self, field_name):
                missing.append(field_name)
        return missing


@dataclass(frozen=True)
class ExpertHandoff:
    """A single coordinator-controlled handoff between specialist roles."""

    from_role: str
    to_role: str
    required_input: list[str]
    expected_output: list[str]
    validation_gate: list[str]
    on_failure: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class HandbookProjectState:
    """Machine-readable coordinator state for Skill hosts and delivery artifacts."""

    schema_version: str
    project_status: str
    current_phase: str
    parameters: HandbookProjectParameters
    required_sequence: list[str]
    handoffs: list[ExpertHandoff] = field(default_factory=list)
    quality_gates_passed: list[str] = field(default_factory=list)
    deliverables: dict[str, str | None] = field(default_factory=dict)
    missing_preflight: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["parameters"] = self.parameters.to_dict()
        payload["handoffs"] = [handoff.to_dict() for handoff in self.handoffs]
        return payload


def default_handoffs() -> list[ExpertHandoff]:
    """Return the standard Coordinator -> Analyst -> Writer -> Inspector -> Reviewer handoffs."""

    return [
        ExpertHandoff(
            from_role="handbook_project_manager",
            to_role="syllabus_outline_analyst",
            required_input=["syllabus-evidence.json", "official specification PDF text"],
            expected_output=["syllabus-outline.json"],
            validation_gate=[
                "schema_version == v0.5-llm-syllabus-outline",
                "topics are non-empty",
                "topic titles are teachable, not placeholders",
                "each topic has exam_points and source_snippets",
            ],
            on_failure="Return to syllabus_outline_analyst with exact schema or placeholder issues.",
        ),
        ExpertHandoff(
            from_role="handbook_project_manager",
            to_role="handbook_writer",
            required_input=["concepts/concept_jobs.json", "syllabus-outline.json"],
            expected_output=[
                "concepts/concept_explanations.json",
                "visual specs or pending visual jobs",
            ],
            validation_gate=[
                "all concept jobs have matching topic entries",
                "student-facing explanations are original and source-bound",
                "visual specs are created only where they materially help",
            ],
            on_failure="Return to handbook_writer with missing topic IDs or content defects.",
        ),
        ExpertHandoff(
            from_role="handbook_project_manager",
            to_role="quality_inspector",
            required_input=[
                "named handbook HTML",
                "qualification.json",
                "concepts/concept_explanations.json",
            ],
            expected_output=["quality-inspection.json"],
            validation_gate=[
                "inspection_status == pass",
                "module and file completeness checks pass",
                "no placeholder, null, undefined, or repeated visual spec problems are reported",
            ],
            on_failure="Repair through handbook_writer or renderer before dispatching final_reviewer.",
        ),
        ExpertHandoff(
            from_role="handbook_project_manager",
            to_role="final_reviewer",
            required_input=[
                "named handbook HTML",
                "syllabus-evidence.json",
                "validation.json",
                "quality-inspection.json",
                "images/visual_manifest.json",
            ],
            expected_output=[
                "final-review-packet.json",
                "agent-product-review.json when final-ready",
            ],
            validation_gate=[
                "final reviewer is independent from analyst and writer",
                "agent_self_review.must_not_present_as_final == false before final handoff",
                "agent-product-review.json is complete for final-ready delivery",
            ],
            on_failure="Return fixable content, visual, glossary, or rendering issues to the responsible phase.",
        ),
    ]


def build_project_state(
    *,
    parameters: HandbookProjectParameters | None = None,
    current_phase: str = "preflight",
    project_status: str | None = None,
    output_dir: Path | None = None,
    quality_gates_passed: list[str] | None = None,
    notes: list[str] | None = None,
) -> HandbookProjectState:
    params = parameters or HandbookProjectParameters()
    missing = params.missing_required()
    status = project_status or ("blocked" if missing else "in_progress")
    return HandbookProjectState(
        schema_version=COORDINATOR_SCHEMA_VERSION,
        project_status=status,
        current_phase=current_phase,
        parameters=params,
        required_sequence=REQUIRED_SEQUENCE,
        handoffs=default_handoffs(),
        quality_gates_passed=quality_gates_passed or [],
        deliverables=deliverable_paths(output_dir) if output_dir else {},
        missing_preflight=missing,
        notes=notes or [],
    )


def deliverable_paths(output_dir: Path) -> dict[str, str | None]:
    handbook_html = find_handbook_html(output_dir)
    handbook_pdf = find_handbook_pdf(output_dir)
    files = {
        "guide_html": handbook_html,
        "guide_pdf": handbook_pdf,
        "qualification": output_dir / "qualification.json",
        "syllabus_evidence": output_dir / "syllabus-evidence.json",
        "syllabus_outline": output_dir / "syllabus-outline.json",
        "concept_jobs": output_dir / "concepts" / "concept_jobs.json",
        "concept_explanations": output_dir / "concepts" / "concept_explanations.json",
        "quality_inspection": output_dir / "quality-inspection.json",
        "final_review_packet": output_dir / "final-review-packet.json",
        "product_review": output_dir / "agent-product-review.json",
        "validation": output_dir / "validation.json",
        "agent_orchestration": output_dir / "agent-orchestration.json",
        "delivery_contract": output_dir / "delivery-contract.json",
    }
    return {key: str(path) if path.exists() else None for key, path in files.items()}


def build_coordinator_prompt(
    parameters: HandbookProjectParameters | None = None,
    *,
    output_dir: Path | None = None,
) -> str:
    """Build the Handbook Project Manager prompt for an Agent runtime."""

    state = build_project_state(parameters=parameters, output_dir=output_dir)
    state_payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "# Handbook Project Manager",
            "",
            "## 1. Identity",
            "",
            "You are the handbook_project_manager, the coordinator for IGCSE and International AS/A-Level handbook generation.",
            "You do not write syllabus analysis, topic explanations, or final approval yourself.",
            "You route work to specialist roles, validate their artifacts, and control handoffs.",
            "",
            "## 2. Mission",
            "",
            "Orchestrate a five-role expert team so the final handbook is source-bound, rendered, inspected, and independently reviewed.",
            "Keep the project moving through Analyst -> Writer -> Quality Inspector -> Final Reviewer without skipping gates.",
            "",
            "## 3. Core Principles",
            "",
            "1. Preflight first: confirm board, level, subject, support language, explanation style, and infographic capability before generation.",
            "2. Sequential handoff: dispatch one expert phase at a time and record what each phase produced.",
            "3. No domain override: ask the responsible expert to repair their own artifact instead of silently rewriting it.",
            "4. Evidence before delivery: final-ready requires validation, quality inspection, independent final review, and product-review evidence.",
            "5. Transparent status: tell the user the current phase, blocker, and next action in concise terms.",
            "",
            "## 4. Workflow",
            "",
            "1. Preflight: collect missing required parameters from missing_preflight.",
            "2. Analyst: provide syllabus-evidence.json and require syllabus-outline.json.",
            "3. Writer: provide concept_jobs.json and require concept_explanations.json plus visual decisions.",
            "4. Inspector: run fast structure/completeness checks and write quality-inspection.json.",
            "5. Reviewer: use a fresh independent context to audit rendered output and final-review-packet.json.",
            "6. Delivery: only present final-ready when all final handoff gates pass; otherwise label draft/review-ready/blocked accurately.",
            "",
            "## 5. Failure Handling",
            "",
            "- If an expert output fails schema or completeness checks, return it to that expert with exact issues.",
            "- If the same phase fails twice, summarize the failure pattern and continue with a draft or blocked state instead of hiding the risk.",
            "- If no independent reviewer context exists, stop at review-ready or draft; do not call it final-ready.",
            "",
            "## 6. Current Project State JSON",
            "",
            "```json",
            state_payload,
            "```",
            "",
            "## 7. Required Output",
            "",
            "Maintain an updated handbook-project-manager.json with project_status, current_phase, missing_preflight, deliverables, quality_gates_passed, and handoff notes.",
            "When handing off, state exactly which files the next expert must read and what file they must produce.",
        ]
    )


def write_coordinator_artifacts(
    output_dir: Path,
    parameters: HandbookProjectParameters | None = None,
    *,
    current_phase: str = "preflight",
    project_status: str | None = None,
    quality_gates_passed: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, object]:
    """Write coordinator state and prompt artifacts to an output directory."""

    output_dir.mkdir(parents=True, exist_ok=True)
    state = build_project_state(
        parameters=parameters,
        current_phase=current_phase,
        project_status=project_status,
        output_dir=output_dir,
        quality_gates_passed=quality_gates_passed,
        notes=notes,
    )
    payload = state.to_dict()
    (output_dir / COORDINATOR_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / COORDINATOR_PROMPT_FILE).write_text(
        build_coordinator_prompt(parameters, output_dir=output_dir),
        encoding="utf-8",
    )
    return payload


def parameters_from_generation_args(
    *,
    provider: str | None,
    level: str | None,
    subject: str | None,
    exam_year: str | None,
    term_support_language: str | None,
    explanation_style: str | None,
    image_provider: str | None,
) -> HandbookProjectParameters:
    capability = None
    if image_provider:
        capability = "yes" if image_provider == "custom" else "no-or-prompt-queue"
    return HandbookProjectParameters(
        exam_board=provider,
        level=level,
        subject=subject,
        exam_year=exam_year,
        term_support_language=term_support_language,
        explanation_style=explanation_style,
        infographic_capability=capability,
        image_method=image_provider,
    )
