# Migration Acceptance Contract

This contract records replacement of the former nested project layout by the
standard root Skill in the same repository. The pre-migration structure remains
available only as a verified rollback archive.

## Required Result

```text
capability_parity = 100%
rule_coverage = 100%
command_contract_parity = 100%
artifact_contract_parity = 100%
legacy_regression_pass = 100%
yao_governed_gates = 100%
known_capability_loss = 0
```

These measures cover migration of the current project. They do not promise that external websites, models, or platforms never change.

## Coverage Matrix

| ID | Legacy capability or contract | Candidate evidence | Status |
| --- | --- | --- | --- |
| P01 | AQA, Edexcel, CAIE, and College Board AP Providers | Provider contract tests and dual-run evidence | pass |
| P02 | GCSE, IGCSE, A-Level AS/A2/full, and AP routing | Qualification matrix | pass |
| P03 | International and UK-domestic preflight routing | Market-route evals | pass |
| P04 | Blocking external-image capability question | Trigger and workflow evals | pass |
| P05 | Official syllabus discovery, download, and evidence extraction | Provider fixture dual-run | pass |
| P06 | Atomic syllabus-point decomposition owned by the LLM | Artifact schema and output eval | pass |
| P07 | LLM/Python ownership boundary | Architecture and adversarial evals | pass |
| P08 | AQA, Edexcel, CAIE, and AP cover templates | Golden render comparison | pass |
| P09 | Manifest rebuild, asset import, approval, render sequencing | State-transition tests | pass |
| P10 | Per-topic visual routing and semantic review | Visual contract evals | pass |
| P11 | HTML-first generation and complete LLM review | Review-gate dual-run | pass |
| P12 | HTML, render, ledger, and approval hash consistency | Tamper and stale-state tests | pass |
| P13 | PDF export and delivery-copy hash gates | PDF gate tests | pass |
| P14 | Independent full review for every batch subject | Batch isolation tests | pass |
| P15 | CLI commands, flags, outputs, paths, and exit codes | Command contract snapshot | pass |
| P16 | JSON schemas, filenames, and status fields | Artifact contract snapshot | pass |
| P17 | Unicode, formula, SVG, and encoding gates | Corruption fixtures | pass |
| P18 | All current automated tests | Frozen-suite run | pass |
| P19 | Concept and visual import helper entry points remain usable from the install ZIP | Package-content regression plus reverse-install helper probes | pass |

## Replacement Gate

Every P01-P19 row and every blocker-class governed gate must pass. Any pending
migration row, failed test, waived migration requirement, stale hash, or missing
fixture named by those rows blocks replacement and release. Optional telemetry,
provider-backed output comparison, human blind review, and world-class evidence
remain honestly marked `missing evidence` or `no-data`; they do not block this
structure migration because this release makes no adoption, superiority, or
world-class claim.

The source project may be replaced only after the user reviews the final parity
report and explicitly approves replacement.

Replacement was explicitly approved for `v0.7.0` after every migration row
passed. Publication still requires a final clean-clone regression, standard
package validation, reverse installation, trust scan, and Git diff review.

The original v0.6.2 local source baseline had one environment-only failure: an
empty `.git` directory caused `test_outputs_are_ignored_and_not_tracked` to
invoke Git outside a valid repository. The clean same-repository checkout used
for v0.7.0 removes that environment defect without changing the frozen baseline
evidence.
