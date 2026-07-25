"""Optional coordination prompt and project-state contracts for handbook generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from intl_exam_guide.auditing.pdf_delivery import inspect_current_pdf
from intl_exam_guide.rendering.output_names import find_handbook_html

COORDINATOR_FILE = "handbook-project-manager.json"
COORDINATOR_PROMPT_FILE = "handbook-project-manager-prompt.md"
COORDINATOR_SCHEMA_VERSION = "v0.6-handbook-project-manager"
SUPPORTED_SUPPORT_LANGUAGES = {"en", "zh-CN", "zh-TW", "ja"}
SUPPORTED_EXPLANATION_STYLES = {
    "formal",
    "friendly",
    "life",
    "story",
    "detective",
    "adventure",
}
SUPPORTED_WORKFLOW_MODES = {"single-host", "multi-agent"}
SUPPORTED_IMAGE_CAPABILITY_STATES = {"yes", "no", "uncertain"}
SUPPORTED_COURSE_MARKETS = {"international", "uk-domestic", "not-applicable"}
SUPPORTED_BOARD_ALIASES = {
    "aqa",
    "edexcel",
    "pearson",
    "caie",
    "cambridge",
    "college board ap",
    "collegeboard ap",
    "collegeboard",
}
SUPPORTED_LEVEL_ALIASES = {
    "igcse",
    "gcse",
    "a-level",
    "alevel",
    "as-level",
    "as",
    "as-a-level",
    "ap",
}
SUPPORTED_A_LEVEL_STAGES = {"AS", "A2", "full", "not-applicable"}
LEGACY_AS_LEVEL_ALIASES = {"as", "as-level"}
A_LEVEL_LEVEL_ALIASES = {
    "a-level",
    "alevel",
    "as-a-level",
    *LEGACY_AS_LEVEL_ALIASES,
}


def requires_course_market(exam_board: str | None, level: str | None) -> bool:
    """Return whether a board and level pair has international/UK routes."""

    if not exam_board or not level:
        return False
    return (
        exam_board.strip().lower() in {"aqa", "edexcel", "pearson", "caie", "cambridge"}
        and level.strip().lower() in SUPPORTED_LEVEL_ALIASES - {"ap"}
    )

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
    a_level_stage: str | None = None
    course_market: str | None = None
    subject: str | None = None
    subject_code: str | None = None
    exam_year: str | None = None
    term_support_language: str | None = None
    explanation_style: str | None = None
    infographic_capability: str | None = None
    image_method: str | None = None
    image_route_verified: bool = False
    workflow_mode: str | None = None
    batch_scope: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        if (
            payload["a_level_stage"] is None
            and self.level
            and self.level.strip().lower() in LEGACY_AS_LEVEL_ALIASES
        ):
            payload["a_level_stage"] = "AS"
        return payload

    def resolved_a_level_stage(self) -> str | None:
        """Return the declared stage, preserving the legacy AS selector."""

        if self.a_level_stage:
            return self.a_level_stage
        if self.level and self.level.strip().lower() in LEGACY_AS_LEVEL_ALIASES:
            return "AS"
        return None

    def missing_required(self) -> list[str]:
        missing = []
        for field_name in [
            "exam_board",
            "level",
            "course_market",
            "subject",
            "exam_year",
            "term_support_language",
            "explanation_style",
            "infographic_capability",
            "workflow_mode",
            "batch_scope",
        ]:
            if not getattr(self, field_name):
                missing.append(field_name)
        if (
            self.level
            and self.level.strip().lower() in A_LEVEL_LEVEL_ALIASES
            and not self.resolved_a_level_stage()
        ):
            missing.append("a_level_stage")
        if self.infographic_capability == "yes":
            if not self.image_method:
                missing.append("image_method")
            if not self.image_route_verified:
                missing.append("image_route_verified")
        return missing

    def invalid_required(self) -> list[str]:
        invalid: list[str] = []
        if self.exam_board and self.exam_board.strip().lower() not in SUPPORTED_BOARD_ALIASES:
            invalid.append("exam_board")
        if self.level and self.level.strip().lower() not in SUPPORTED_LEVEL_ALIASES:
            invalid.append("level")
        if self.a_level_stage and self.a_level_stage not in SUPPORTED_A_LEVEL_STAGES:
            invalid.append("a_level_stage")
        elif self.level and self.level.strip().lower() in A_LEVEL_LEVEL_ALIASES:
            if self.resolved_a_level_stage() == "not-applicable":
                invalid.append("a_level_stage")
        elif self.a_level_stage and self.a_level_stage != "not-applicable":
            invalid.append("a_level_stage")
        if self.course_market and self.course_market not in SUPPORTED_COURSE_MARKETS:
            invalid.append("course_market")
        elif self.course_market and requires_course_market(self.exam_board, self.level):
            if self.course_market not in {"international", "uk-domestic"}:
                invalid.append("course_market")
        elif self.course_market and self.course_market != "not-applicable":
            invalid.append("course_market")
        if self.term_support_language and self.term_support_language not in SUPPORTED_SUPPORT_LANGUAGES:
            invalid.append("term_support_language")
        if self.explanation_style and self.explanation_style not in SUPPORTED_EXPLANATION_STYLES:
            invalid.append("explanation_style")
        if self.infographic_capability and self.infographic_capability not in SUPPORTED_IMAGE_CAPABILITY_STATES:
            invalid.append("infographic_capability")
        if self.workflow_mode and self.workflow_mode not in SUPPORTED_WORKFLOW_MODES:
            invalid.append("workflow_mode")
        if self.batch_scope and not self.batch_scope.strip():
            invalid.append("batch_scope")
        return invalid


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
    invalid_preflight: list[str] = field(default_factory=list)
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
                "stable topic_id and llm-authored provenance for every topic",
                "per-topic visual_decision records",
                "visual specs or pending visual jobs when non-text visuals are needed",
            ],
            validation_gate=[
                "all concept jobs have matching topic entries",
                "topic IDs match exactly; substring topic matching is forbidden",
                "guide-plan content_provenance == llm-authored before formal review",
                "student-facing explanations are original and source-bound",
                "every topic records visual_decision",
                "text-ok decisions include no_visual_reason",
                "visual specs are created only where they materially help",
                "an existing visual_manifest.json is render-only unless a new manifest cycle is explicitly declared",
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
                "current-render.json and its immutable render snapshot",
            ],
            expected_output=[
                "final-review-packet.json",
                "review-ledger Topic/Visual shards and holistic HTML review",
                "agent-product-review.json when final-ready",
            ],
            validation_gate=[
                "LLM reviewer personally opens the current rendered HTML instead of relying on Python diagnostics",
                "Topic/Visual review shards contain at most 25 items and cover every current ID exactly once",
                "holistic review separately covers the complete assembled HTML",
                "every repair is followed by HTML rerender and another visible LLM review",
                "agent-product-review.json approves the exact current HTML SHA-256",
                "read-only audit-delivery has no current snapshot, content, validation, or visual blocker",
                "PDF export occurs only after current-HTML LLM approval",
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
    invalid = params.invalid_required()
    if output_dir is None:
        missing.append("output_dir")
    status = project_status or ("blocked" if missing or invalid else "in_progress")
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
        invalid_preflight=invalid,
        notes=notes or [],
    )


def deliverable_paths(output_dir: Path) -> dict[str, str | None]:
    handbook_html = find_handbook_html(output_dir)
    current_pdf = inspect_current_pdf(output_dir)
    handbook_pdf = (
        Path(str(current_pdf.get("pdf_path")))
        if current_pdf.get("complete") is True
        else None
    )
    files: dict[str, Path | None] = {
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
    return {
        key: str(path) if path is not None and path.exists() else None
        for key, path in files.items()
    }


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
            "## Boundary Compliance Gate",
            "",
            "Treat the Skill and its artifact contracts as binding execution constraints, not suggestions. Do not invent shortcuts, compress official syllabus requirements for speed, merge directory headings into final topics, allocate visuals by subject quota, use Python inspection as approval, or export PDF before current-HTML LLM approval. If a boundary cannot be satisfied, stop and report the blocker instead of silently changing the rule.",
            "",
            "## 1. Identity",
            "",
            "You are the host LLM coordinating a lightweight GCSE/IGCSE, A-Level, or College Board AP handbook run.",
            "Analyst, Writer, and Reviewer are operating roles you keep explicit; they are not mandatory separate agents.",
            "Do not add project-manager, mandatory quality-inspector, or release-certification roles unless the user explicitly asks for that infrastructure.",
            "",
            "## 2. Mission",
            "",
            "Keep the project moving through Analyst -> Writer -> Reviewer while respecting the Python boundary.",
            "Python fetches evidence, validates contracts, renders HTML, gates post-approval PDF export, and writes mechanical manifests; the host LLM owns analysis, writing, visual judgment, and review.",
            "",
            "## 3. Core Principles",
            "",
            "1. Preflight first: confirm board, level, A-Level stage when applicable, course market, subject, support language, explanation style, and external image-generation capability before generation.",
            "   The first response is a structured preflight form only. Ask every field below in one message, show the allowed choices, and wait; do not merge missing fields into an open-ended question.",
            "   Required first-response fields: external_visual_capability (yes/no/uncertain), image_method when yes, board (AQA/Edexcel/CAIE/College Board AP), level (IGCSE/A-Level/AP), a_level_stage (AS/A2/full for A-Level; not-applicable otherwise), course_market (international/uk-domestic for AQA, Edexcel, or CAIE GCSE/IGCSE/A-Level; not-applicable for AP), subject, exam_year_or_syllabus_range, term_support_language (en/zh-CN/zh-TW/ja), explanation_style (formal/friendly/life/story/detective/adventure), workflow_mode (single-host/multi-agent), batch_scope, and output_dir.",
            "   Never infer course_market from a course title, code, URL, provider, or prior run. AQA and Edexcel route automatic acquisition through the selected market's official Provider. CAIE records the selected market but uses the same official Cambridge International catalogue for either market; never substitute the recorded market.",
            "   Ask exactly: Can you provide or enable an external image-generation Skill or tool for this run? Offer the three capability choices. Do not infer a route or an answer from image_provider, installed tools, prior runs, or the host's own capabilities.",
            "   Reply format must be key=value lines. Preserve answered fields, list only missing/invalid fields on a follow-up, and keep the project blocked until every required field is valid. Do not download, discover, split, write, render, generate visuals, or export PDF while preflight is incomplete.",
            "   A yes capability is not verified until the named route is actually callable and image_route_verified=true is recorded. A no/uncertain answer never silently becomes local generation.",
            "   Explanation-style choices are fixed: formal=exam-oriented; friendly=clear and approachable; life=everyday analogies with exam accuracy; story=narrative structure; detective=questions, clues, inference; adventure=tasks and challenges. Do not accept a new style label or silently map it to a default.",
            "   Use this first-response form: external_visual_capability=<yes|no|uncertain>; image_method=<route or none>; board=<AQA|Edexcel|CAIE|College Board AP>; level=<IGCSE|A-Level|AP>; a_level_stage=<AS|A2|full|not-applicable>; course_market=<international|uk-domestic|not-applicable>; subject=<name/code>; exam_year_or_syllabus_range=<value|unknown>; term_support_language=<en|zh-CN|zh-TW|ja>; explanation_style=<fixed value>; workflow_mode=<single-host|multi-agent>; batch_scope=<value>; output_dir=<absolute path>.",
            "2. Sequential handoff: complete Analyst artifacts before Writer artifacts, then inspect the visible handbook as Reviewer.",
            "3. No Python content generation: do not let Python decide topic boundaries, write teaching text, choose visual need, or approve final quality.",
            "4. Evidence before delivery: final-ready requires visible handbook inspection and product-review evidence, not just validation.",
            "5. Transparent status: tell the user the current phase, blocker, and next action in concise terms.",
            "",
            "## 4. Workflow",
            "",
            "1. Preflight: collect missing_required, invalid_preflight, and output_dir from the structured form. An A-Level request requires an explicit AS, A2, or full stage. Any missing or invalid field keeps the project blocked; never replace it with an inferred default.",
            "2. Analyst: read syllabus-evidence.json and write syllabus-outline.json.",
            "3. Writer: read concept_jobs.json and write concept_explanations.json with the exact stable topic_id, llm-authored provenance, mastery_summary, and visual_decision for every topic. Do not accept Python fallback content or substring topic matching.",
            "4. Visual state: for a new Writer visual plan, explicitly refresh the manifest before asset generation/import; after import or visual approval, never rebuild it again. Reuse requires unchanged spec_hash; changed specs and replaced assets reset visual approval to pending. Keep old unreferenced files unless cleanup is explicitly approved.",
            "5. Render HTML: let Python render current Writer artifacts using the existing manifest only, without generating PDF, create the immutable render snapshot/current-render pointer, and run read-only audit-delivery; diagnostics remain supporting evidence only.",
            "6. LLM review loop: personally open the rendered HTML and review every final topic, worked example/answer, and rendered visual for subject and semantic accuracy; sampling or layout-only review is not approval. Compare with evidence and outline files, return every fixable issue to the Writer, rerender, and look again until the current HTML passes.",
            "7. Approval: write LLM-authored Topic/Visual review shards (at most 25 items each) and a separate holistic complete-HTML review, index their hashes mechanically, then write the compact agent-product-review.json bound to the exact snapshot, HTML, and ledger index. Python cannot author any review decision.",
            "8. PDF delivery: run export-pdf only after current-HTML approval and a clean delivery gate; any later input, asset, or HTML change requires a new snapshot and visible review. Otherwise label draft/review-ready/blocked accurately.",
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
    a_level_stage: str | None = None,
) -> HandbookProjectParameters:
    normalized_level = level
    resolved_stage = a_level_stage
    if level and level.strip().lower() in LEGACY_AS_LEVEL_ALIASES:
        normalized_level = "a-level"
        resolved_stage = resolved_stage or "AS"
    elif level and level.strip().lower() in {"a-level", "alevel", "as-a-level"}:
        normalized_level = "a-level"
        resolved_stage = resolved_stage or "full"
    return HandbookProjectParameters(
        exam_board=provider,
        level=normalized_level,
        a_level_stage=resolved_stage,
        subject=subject,
        exam_year=exam_year,
        term_support_language=term_support_language,
        explanation_style=explanation_style,
        # A configured renderer is not evidence of the user's explicit answer.
        infographic_capability=None,
        image_method=image_provider,
    )
