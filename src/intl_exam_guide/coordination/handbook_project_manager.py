"""Optional coordination prompt and project-state contracts for handbook generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from intl_exam_guide.rendering.output_names import find_handbook_html, find_handbook_pdf

COORDINATOR_FILE = "handbook-project-manager.json"
COORDINATOR_PROMPT_FILE = "handbook-project-manager-prompt.md"
COORDINATOR_SCHEMA_VERSION = "v0.5-handbook-project-manager"

REQUIRED_SEQUENCE = [
    "syllabus_outline_analyst",
    "handbook_writer",
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
    """Return the lightweight Analyst -> Writer -> Reviewer handoffs."""

    return [
        ExpertHandoff(
            from_role="host_llm",
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
            from_role="syllabus_outline_analyst",
            to_role="handbook_writer",
            required_input=["concepts/concept_jobs.json", "syllabus-outline.json"],
            expected_output=[
                "concepts/concept_explanations.json",
                "per-topic visual_decision records",
                "visual specs or pending visual jobs when non-text visuals are needed",
            ],
            validation_gate=[
                "all concept jobs have matching topic entries",
                "student-facing explanations are original and source-bound",
                "every topic records visual_decision",
                "text-ok decisions include no_visual_reason",
                "visual specs are created only where they materially help",
            ],
            on_failure="Return to handbook_writer with missing topic IDs or content defects.",
        ),
        ExpertHandoff(
            from_role="handbook_writer",
            to_role="final_reviewer",
            required_input=[
                "named handbook HTML",
                "syllabus-evidence.json",
                "validation.json",
                "images/visual_manifest.json",
            ],
            expected_output=[
                "final-review-packet.json",
                "agent-product-review.json when final-ready",
            ],
            validation_gate=[
                "reviewer opens the rendered HTML/PDF instead of relying on machine validation alone",
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
        "delivery_contract": output_dir / "delivery-contract.json",
    }
    return {key: str(path) if path.exists() else None for key, path in files.items()}


def build_coordinator_prompt(
    parameters: HandbookProjectParameters | None = None,
    *,
    output_dir: Path | None = None,
) -> str:
    """Build the optional coordination prompt for a host LLM runtime."""

    state = build_project_state(parameters=parameters, output_dir=output_dir)
    state_payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "# Lightweight Handbook Workflow Coordinator",
            "",
            "## 1. Identity",
            "",
            "You are the host LLM coordinating a lightweight IGCSE and International AS/A-Level handbook run.",
            "Analyst, Writer, and Reviewer are operating roles you keep explicit; they are not mandatory separate agents.",
            "Do not add project-manager, mandatory quality-inspector, or release-certification roles unless the user explicitly asks for that infrastructure.",
            "",
            "## 2. Mission",
            "",
            "Keep the project moving through Analyst -> Writer -> Reviewer while respecting the Python boundary.",
            "Python fetches evidence, validates contracts, renders HTML/PDF, and writes mechanical manifests; the host LLM owns analysis, writing, visual judgment, and review.",
            "",
            "## 3. Core Principles",
            "",
            "1. Preflight first: confirm board, level, subject, support language, explanation style, and infographic capability before generation.",
            "2. Sequential handoff: complete Analyst artifacts before Writer artifacts, then inspect the visible handbook as Reviewer.",
            "3. No Python content generation: do not let Python decide topic boundaries, write teaching text, choose visual need, or approve final quality.",
            "4. Evidence before delivery: final-ready requires visible handbook inspection and product-review evidence, not just validation.",
            "5. Transparent status: tell the user the current phase, blocker, and next action in concise terms.",
            "",
            "## 4. Workflow",
            "",
            "1. Preflight: collect missing required parameters from missing_preflight.",
            "2. Analyst: read syllabus-evidence.json and write syllabus-outline.json.",
            "3. Writer: read concept_jobs.json and write concept_explanations.json with mastery_summary and visual_decision for every topic.",
            "4. Render/check: let Python validate and render approved artifacts; use quality-inspection.json only as supporting evidence when present.",
            "5. Reviewer: open the rendered HTML/PDF, compare it with evidence and outline files, and record real issues in final-review-packet.json / agent-product-review.json.",
            "6. Delivery: only present final-ready when the visible-handbook review and final handoff gates pass; otherwise label draft/review-ready/blocked accurately.",
            "",
            "## 5. Failure Handling",
            "",
            "- If an artifact fails schema or completeness checks, repair the responsible role output with exact issues.",
            "- If the same phase fails twice, summarize the failure pattern and continue with a draft or blocked state instead of hiding the risk.",
            "- If the rendered handbook was not opened or screenshot-inspected, stop at review-ready or draft; do not call it final-ready.",
            "",
            "## 6. Current Project State JSON",
            "",
            "```json",
            state_payload,
            "```",
            "",
            "## 7. Required Output",
            "",
            "Maintain an updated handbook-project-manager.json with project_status, current_phase, missing_preflight, deliverables, quality_gates_passed, and handoff notes when this optional coordinator artifact is used.",
            "When handing off between roles, state exactly which files the next role must read and what file it must produce.",
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
