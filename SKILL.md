---
name: igcse-a-level-revision-guide
description: Repository entry for the source-backed IGCSE, A-Level, and College Board AP revision-handbook Skill. The authoritative workflow is maintained in skill/SKILL.md.
---

# Repository Skill Entry

The installable and authoritative Skill is [skill/SKILL.md](skill/SKILL.md).
Read that file in full before starting a handbook run, then follow its linked
reference contracts. This root file is only a repository-level discovery
wrapper; it does not define a second workflow.

Automatic official-syllabus acquisition covers the International and
UK-domestic AQA, Edexcel, and CAIE IGCSE/AS/A-Level routes plus College Board
AP. The canonical Skill requires an explicit market selection before retrieval.
Other curriculum systems and exam boards cannot use automatic acquisition;
manual imports are experimental and may fail with unknown compatibility errors.

Do not infer behavior from an older generated output or from this wrapper. In
particular, the canonical Skill controls the mandatory visual-capability
preflight, LLM-owned syllabus analysis and writing, complete visible HTML
review, repair loop, and hash-gated PDF export.
