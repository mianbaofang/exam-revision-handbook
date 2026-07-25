---
name: exam-revision-handbook
description: Repository discovery entry for the Exam Revision Handbook Skill, which creates source-backed GCSE, IGCSE, A-Level, and College Board AP revision handbooks. The authoritative workflow is maintained in skill/SKILL.md.
---

# Exam Revision Handbook

The installable and authoritative Skill is [skill/SKILL.md](skill/SKILL.md).
Read that file in full before starting a handbook run, then follow its linked
reference contracts. This root file is only a repository-level discovery
wrapper; it does not define a second workflow.

Automatic official-syllabus acquisition covers the supported British source
families: AQA, Edexcel, and CAIE. It includes AQA and Edexcel UK GCSE,
International GCSE, and A-Level routes; Cambridge International / CAIE
International GCSE and A-Level routes; and College Board AP. A CAIE
`uk-domestic` selection records a UK-centre request but uses the same
Cambridge International catalogue; it does not imply a separate CAIE UK GCSE
product. AS and A2 are stages within A-Level, not separate curriculum systems.
The canonical Skill requires an explicit market selection before retrieval.
Other curriculum systems and exam boards cannot use automatic acquisition;
manual imports are experimental and may fail with unknown compatibility errors.

Do not infer behavior from an older generated output or from this wrapper. In
particular, the canonical Skill controls the mandatory visual-capability
preflight, LLM-owned syllabus analysis and writing, complete visible HTML
review, repair loop, and hash-gated PDF export.
