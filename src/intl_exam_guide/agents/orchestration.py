from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

AGENT_ORCHESTRATION_FILE = "agent-orchestration.json"


@dataclass(frozen=True)
class AgentRole:
    """A recorded role in the handbook production workflow."""

    role_id: str
    label: str
    responsibility: str
    status: str
    evidence: list[str] = field(default_factory=list)
    independent_from: list[str] = field(default_factory=list)
    dispatch_brief: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def default_agent_roles(
    final_review_complete: bool = False,
    quality_inspection_complete: bool = False,
) -> list[AgentRole]:
    inspector_status = "complete" if quality_inspection_complete else "pending"
    inspector_evidence = ["quality-inspection.json"] if quality_inspection_complete else []
    reviewer_status = "complete" if final_review_complete else "pending"
    reviewer_evidence = ["final-review-packet.json"] if final_review_complete else []
    return [
        AgentRole(
            role_id="handbook_project_manager",
            label="Handbook project manager",
            responsibility=(
                "Coordinate preflight, specialist dispatch, artifact validation, repair loops, and final handoff."
            ),
            status="complete",
            evidence=["handbook-project-manager.json", "agent-orchestration.json"],
            dispatch_brief=[
                "Confirm board, level, subject, term-support language, explanation style, and infographic capability before generation.",
                "Dispatch Analyst, Writer, Quality Inspector, and Final Reviewer in sequence.",
                "Record blocked, draft, review-ready, or final-ready state honestly instead of skipping gates.",
            ],
        ),
        AgentRole(
            role_id="syllabus_outline_analyst",
            label="Syllabus and outline analyst",
            responsibility=(
                "Parse provider syllabus evidence into CourseSpec and LearningUnit records."
            ),
            status="complete",
            evidence=["qualification.json", "syllabus-outline.json", "delivery-contract.json"],
            dispatch_brief=[
                "Read the official provider page and specification PDF evidence.",
                "Extract CourseSpec and LearningUnit records from the current source only.",
                "Flag ambiguous board, level, subject, or syllabus-year evidence instead of guessing.",
            ],
        ),
        AgentRole(
            role_id="handbook_writer",
            label="Handbook writer",
            responsibility=(
                "Create source-bound PedagogicalUnit content, practice, visuals, and HTML/PDF output."
            ),
            status="complete",
            evidence=["guide-plan.json", "handbook-package.json", "named handbook HTML"],
            dispatch_brief=[
                "Read CourseSpec, LearningUnit records, source snippets, and concept jobs.",
                "Write source-bound PedagogicalUnit content, practice, visual specs, HTML, and PDF.",
                "Do not approve the final output; hand it to the Quality Inspector and independent final reviewer.",
            ],
        ),
        AgentRole(
            role_id="quality_inspector",
            label="Quality inspector",
            responsibility=(
                "Run fast structure, completeness, placeholder, file, and visual-manifest checks before final review."
            ),
            status=inspector_status,
            evidence=inspector_evidence,
            independent_from=["handbook_writer"],
            dispatch_brief=[
                "Read the named handbook HTML, qualification.json, concept_explanations.json, and visual_manifest.json.",
                "Check module presence, topic completeness, placeholder text, missing files, and repeated visual specs.",
                "Return fail with exact issues to the writer/renderer, or pass the package to the final reviewer.",
            ],
        ),
        AgentRole(
            role_id="final_reviewer",
            label="Independent final reviewer",
            responsibility=(
                "Inspect rendered output and review evidence independently before final handoff."
            ),
            status=reviewer_status,
            evidence=reviewer_evidence,
            independent_from=["syllabus_outline_analyst", "handbook_writer", "quality_inspector"],
            dispatch_brief=[
                "Run in a fresh Agent/LLM context or subagent separate from outline analysis and writing.",
                "Read the rendered named HTML/PDF outputs, validation.json, quality-inspection.json, final-review-packet.json, and visual manifest.",
                "Treat machine validation as supporting evidence only; inspect the visible handbook before handoff.",
                "Compare the visible handbook with the syllabus outline and repair fixable content, visual, glossary, or PDF issues before handoff.",
            ],
        ),
    ]


def agent_orchestration_payload(
    final_review_complete: bool = False,
    quality_inspection_complete: bool = False,
) -> dict[str, object]:
    roles = default_agent_roles(
        final_review_complete=final_review_complete,
        quality_inspection_complete=quality_inspection_complete,
    )
    return {
        "schema_version": "v0.5-agent-orchestration",
        "mode": "role-separated",
        "multi_agent_required": True,
        "agent_runtime_contract": {
            "automatic_dispatch": (
                "Skill-compatible Agent runtimes with subagent support must dispatch "
                "the roles in required_sequence instead of letting the writer self-approve."
            ),
            "fallback_without_subagents": (
                "If no independent Agent/LLM context is available, keep the handbook "
                "at review-ready or draft and do not present it as final-ready."
            ),
            "final_handoff_requires": [
                "handbook_project_manager.status == complete",
                "quality_inspector.status == complete",
                "quality_inspection.inspection_status == pass",
                "final_reviewer.status == complete",
                "final_reviewer_independent == true",
                "agent_self_review.must_not_present_as_final == false",
                "the user's active Agent/LLM has inspected the rendered handbook and repaired fixable issues",
            ],
        },
        "roles": [role.to_dict() for role in roles],
        "final_reviewer_independent": final_reviewer_is_independent(roles),
        "required_sequence": [
            "handbook_project_manager",
            "syllabus_outline_analyst",
            "handbook_writer",
            "quality_inspector",
            "final_reviewer",
        ],
    }


def final_reviewer_is_independent(roles: list[AgentRole] | list[dict[str, Any]]) -> bool:
    reviewer = _role_by_id(roles, "final_reviewer")
    if not reviewer:
        return False
    independent_from = set(_role_value(reviewer, "independent_from", []))
    return {"syllabus_outline_analyst", "handbook_writer"}.issubset(independent_from)


def write_agent_orchestration(
    output_dir: Path,
    final_review_complete: bool = False,
    quality_inspection_complete: bool = False,
) -> Path:
    path = output_dir / AGENT_ORCHESTRATION_FILE
    path.write_text(
        json.dumps(
            agent_orchestration_payload(
                final_review_complete=final_review_complete,
                quality_inspection_complete=quality_inspection_complete,
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def _role_by_id(
    roles: list[AgentRole] | list[dict[str, Any]],
    role_id: str,
) -> AgentRole | dict[str, Any] | None:
    for role in roles:
        if _role_value(role, "role_id") == role_id:
            return role
    return None


def _role_value(role: AgentRole | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(role, AgentRole):
        return getattr(role, key, default)
    return role.get(key, default)
