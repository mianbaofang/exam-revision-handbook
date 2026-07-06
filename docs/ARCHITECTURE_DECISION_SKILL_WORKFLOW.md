# Skill Workflow Boundary

This repository version of the Skill is a framework and LLM operations guide. It is not an automatic content generator and not a heavy release-certification system.

The workflow is a lightweight three-role LLM framing, not mandatory multi-agent orchestration. The same host LLM may perform the steps sequentially, or the user may choose to delegate them to separate agents:

1. Analyst: reads `syllabus-evidence.json` and writes `syllabus-outline.json`.
2. Writer: writes `concepts/concept_explanations.json`, `mastery_summary`, and per-topic `visual_decision` records.
3. Reviewer: opens the rendered handbook, compares it with evidence and outline files, and records the real issues found.

The Writer's visual judgment applies to all subjects. Every topic needs a recorded `visual_decision`; `text-ok` is allowed only when `no_visual_reason` explains why a separate visual would not add learning value.

Python may only:

- discover and download official sources;
- extract page-level syllabus evidence;
- validate JSON contract consistency;
- import LLM-written JSON artifacts;
- render HTML/PDF from approved artifacts;
- write mechanical manifests and review packets, including the v0.5 visual route/asset split.

Python must not:

- decide topic boundaries or syllabus splits;
- upgrade old outputs into current-contract outlines;
- write teaching content;
- invent `mastery_summary` text;
- decide whether a topic needs a visual;
- approve final handbook quality.

Do not add project-manager roles, quality-inspector roles, multi-agent orchestration requirements, release-state certification, or extra delivery states unless the user explicitly asks for release infrastructure. The normal Skill flow should stay small enough to read and run in one sitting.
