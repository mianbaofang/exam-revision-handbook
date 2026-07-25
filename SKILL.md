---
name: exam-revision-handbook
description: Create source-backed GCSE, IGCSE, A-Level, and College Board AP revision handbooks from official AQA, Edexcel, CAIE, and College Board sources. Use when acquiring a syllabus, decomposing requirements into atomic teaching points, writing worked examples, planning or reviewing educational visuals, rendering a handbook, reviewing HTML, or exporting an approved PDF. Do not use for unsupported curricula unless the user accepts the experimental manual-import boundary.
---

# Exam Revision Handbook

Follow every gate and linked contract.

## Load The Contracts

1. Read [workflow-contract.md](references/workflow-contract.md) in full before responding.
2. Read [revision_guide_spec.md](references/revision_guide_spec.md) before changing artifacts.
3. Read the applicable College Board AP or OxfordAQA provider note.
4. Run `python scripts/doctor.py` before execution. Use `python scripts/run_runtime.py -- <command>` for every runtime command.
5. Use `evals/` only for validation and release readiness.

## Workflow

1. First respond with the complete structured preflight, including the explicit external-image-capability question. Infer nothing and block all later work until every field is valid.
2. Acquire official evidence only for the confirmed board, qualification, A-Level stage, market, subject, and year.
3. The LLM maps every official requirement to atomic teaching points before writing. Python may extract, validate, record, render, and block; it may not own meaning, content, visual judgment, or approval.
4. Decide visuals per final teaching point. Decorative text boxes are not explanatory diagrams.
5. Use this order: rebuild manifest, import assets, record per-visual LLM approval, then render only. Rebuilds invalidate approvals.
6. Render HTML first. The LLM inspects all of it, records item evidence, repairs, rerenders, and repeats until the exact HTML/render/ledger hashes are approved. Machines cannot approve.
7. Export PDF only from approved HTML and verify all HTML, review, PDF, and delivery hashes.
8. Review every batch subject independently; never share or sample conclusions.

## Output Contract

- The LLM owns syllabus meaning, teaching content, visual judgment, and approval; Python owns extraction, validation, rendering, recording, and blocking only.
- Every official requirement, visual, review item, and delivery file remains traceable to current source and artifact hashes.
- Hand back the approved PDF plus controlled HTML, evidence, review, and delivery artifacts.

## Stop Conditions

Stop instead of guessing when preflight is incomplete, an official source is ambiguous, an LLM-owned artifact is missing, any topic or visual is pending/rejected/stale, hashes disagree, HTML review is incomplete, or the packaged runtime is unavailable. Report the exact blocker and next valid action.

Do not publish or claim parity unless every requirement in [migration-acceptance.md](references/migration-acceptance.md) is passed with current evidence.
