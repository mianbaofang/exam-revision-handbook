# Optional Multi-Agent Orchestration Note

This note is historical/optional design guidance. It is not the default Skill contract.

The binding workflow boundary is `docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`: this Skill is a framework plus LLM operations guide. Python may fetch sources, extract evidence, validate JSON, render HTML/PDF, and write mechanical manifests. Python must not decide syllabus splits, write teaching content, decide visual need, or approve final quality.

The shipped workflow uses three lightweight roles:

1. **Analyst** reads `syllabus-evidence.json` and writes `syllabus-outline.json`.
2. **Writer** writes `concepts/concept_explanations.json`, `mastery_summary`, and per-topic `visual_decision` records.
3. **Reviewer** opens the rendered handbook/PDF, compares it with the source evidence and outline, and records real issues found.

These names are operating roles, not mandatory separate agents. The same host LLM can perform them sequentially. A runtime may delegate them to separate agents only when the user explicitly asks for that orchestration.

Do not require a project-manager role, mandatory quality-inspector role, `agent-orchestration.json`, release-state certification, or extra delivery gates unless there is a fresh product decision. Mechanical quality inspection can still exist as a supporting package check, but it is not an independent approval role.

Visual judgment is all-subject and Writer-owned. Every topic must record `visual_decision`; `recommended_route: "text-ok"` is valid only with `no_visual_reason`, and non-text routes are not complete until the visual manifest shows a reviewed rendered asset.
