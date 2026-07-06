# Skill Workflow Boundary

This repository version of the Skill is a framework and LLM operations guide. It is not an automatic content generator and not a heavy release-certification system.

The workflow is a lightweight three-role LLM workflow:

1. Analyst: the host LLM reads `syllabus-evidence.json` and writes `syllabus-outline.json`.
2. Writer: the host LLM writes `concepts/concept_explanations.json`, `mastery_summary`, and visual decisions.
3. Reviewer: the host LLM opens the rendered handbook, compares it with evidence and outline files, and records the real issues found.

Python may only:

- discover and download official sources;
- extract page-level syllabus evidence;
- validate JSON contract consistency;
- import LLM-written JSON artifacts;
- render HTML/PDF from approved artifacts;
- write mechanical manifests and review packets.

Python must not:

- decide topic boundaries or syllabus splits;
- upgrade old outputs into current-contract outlines;
- write teaching content;
- invent `mastery_summary` text;
- decide whether a topic needs a visual;
- approve final handbook quality.

Do not add project-manager roles, quality-inspector roles, multi-agent orchestration requirements, release-state certification, or extra delivery states unless the user explicitly asks for release infrastructure. The normal Skill flow should stay small enough to read and run in one sitting.
