# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `6`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: complete-runtime-package

Prompt: Package the existing exam handbook Skill without losing its Python-backed generation capability.

Rubric:
- `has-entrypoint` (1.0): Keeps the standard Skill entrypoint.
- `has-engine` (1.0): Includes the executable legacy engine.
- `has-integrity` (1.0): Reports byte-level engine parity.

### Variant A

The rule-only package contains SKILL.md, agents/, and references/, but no executable engine or runtime integrity contract.

### Variant B

The standard package contains SKILL.md, agents/interface.yaml, the versioned engine wheel, runtime-lock.json, doctor.py, bootstrap_runtime.py, and run_runtime.py. The wheel payload matches 77/77 legacy source files.

## Case: cli-command-contract

Prompt: Prove that the standard Skill keeps the existing command surface.

Rubric:
- `has-count` (1.0): Names complete command comparison.
- `has-commands` (1.0): Includes retrieval, review, and delivery commands.
- `preserves-exit` (1.0): Preserves the exit contract.

### Variant A

The rule-only package cannot run the legacy CLI, so command names, flags, help text, and exit codes are unavailable.

### Variant B

The packaged adapter preserves 10/10 CLI help contracts: root plus discover, generate, extract-evidence, demo, review, export-pdf, audit-delivery, index-review-ledger, and inspect; arguments and exit codes pass through unchanged.

## Case: artifact-tree-parity

Prompt: Show that a packaged run produces the same controlled artifacts as the legacy engine.

Rubric:
- `has-tree-count` (1.0): Reports the complete output-tree count.
- `has-no-drift` (1.0): Confirms no artifact drift.
- `keeps-blocker` (1.0): Preserves incomplete-content blocking.

### Variant A

No packaged runtime is available, so artifact compatibility is unknown and cannot be executed from the Skill archive.

### Variant B

A same-input dual run produced 25/25 matching normalized artifacts, with no missing, extra, or changed files. Both runs returned the same blocked state until LLM-owned teaching content is supplied.

## Case: html-before-pdf-gate

Prompt: Prevent PDF export before the current handbook HTML has passed complete LLM review.

Rubric:
- `has-review-chain` (1.0): Names the complete review chain.
- `has-hash-binding` (1.0): Requires current hash-bound approval.
- `has-blocking-exit` (1.0): Preserves failure behavior.

### Variant A

The prose says to review HTML first, but the rule-only archive has no final-review, render-snapshot, ledger, or export implementation.

### Variant B

The packaged engine keeps review, index-review-ledger, audit-delivery, and export-pdf. PDF export requires the exact current HTML, render snapshot, visual approvals, and review-ledger hashes; stale or pending state returns a blocking exit code.

## Case: repository-maintenance-neighbor

Prompt: Update the README and release assets for the exam handbook repository.

Rubric:
- `declines-run` (1.0): Does not start handbook generation.
- `names-neighbor` (1.0): Names the route boundary.
- `no-preflight` (1.0): Avoids irrelevant preflight.

### Variant A

Start the student-handbook preflight and ask which exam board and subject the user wants.

### Variant B

Do not trigger a handbook generation run. This is repository maintenance, a near-neighbor outside the student-handbook workflow; use repository tools and do not ask the external-image preflight.

## Case: governed-file-backed-migration

Prompt: Use the current project as evidence and produce a governed standard Skill with zero known capability loss.

Rubric:
- `uses-file-evidence` (1.0): Names governed file-backed evidence.
- `has-governance` (1.0): Keeps owner and lifecycle review.
- `has-boundaries` (1.0): Defines delivery and rollback boundaries.
- `has-reports` (1.0): Requires trust and quality evidence.
- `does-not-invent` (1.0): Marks unavailable telemetry honestly.

### Variant A

Create a small ZIP from the rule layer and describe it as complete without checking the runtime, installation, permissions, or output parity.

### Variant B

Use each file-backed fixture as input_files evidence. Preserve owner and review cadence, define the output contract and rollback boundary, publish a trust report and reports/output_quality_scorecard.md, and mark unavailable adoption telemetry as missing evidence. Replacement remains blocked until known capability loss is 0.
