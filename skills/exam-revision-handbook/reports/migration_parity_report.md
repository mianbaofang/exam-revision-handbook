# Migration Parity Report

## Scope

This report measures migration of `gcse-igcse-alevel-ap-revision-guide@0.6.2`
into the standard root Skill released as `exam-revision-handbook@0.7.0` in the
same repository. It does not claim that future websites,
models, or third-party platforms cannot change.

The verified pre-migration archive is the rollback boundary. The active project
now continues only from the standard root Skill structure.

## Current Result

- capability parity: `100%` for the current v0.6.2 engine and workflow
- rule coverage: `100%` of the authoritative workflow tail
- command contract parity: `10/10`
- artifact-tree parity: `25/25` normalized demo artifacts
- current clean-checkout regression: `494 passed, 163 skipped, 0 failed, 0 errors`
- frozen v0.6.2 baseline regression: `491 passed, 165 existing skips, 0 failed, 0 errors`
- packaged engine payload: `77/77` source files byte-identical
- known capability loss: `0`
- Yao Governed migration gates: `100%` for P01-P19 and blocker-class checks,
  with `0` Review Studio blockers
- Review Studio retains `6` non-blocking warnings for optional evidence that is
  unavailable or deliberately not claimed; no telemetry, provider result, human
  review, waiver, or world-class evidence was fabricated
- archive and install verification: `pass`; final checksum is recorded beside the archive
- replacement: `approved for same-repository v0.7.0 release`

## Coverage

| ID | Status | Current evidence |
| --- | --- | --- |
| P01 | pass | `test_course_market_providers.py`, `test_url_first_providers.py`, `test_collegeboard_ap_provider.py`, and 77/77 wheel payload parity preserve AQA, Edexcel, CAIE, and AP Providers. |
| P02 | pass | `test_handbook_project_manager.py` covers A-Level stage selection and legacy AS mapping; provider and AP tests cover GCSE, IGCSE, A-Level AS/A2/full, and AP routing. |
| P03 | pass | `test_course_market_providers.py` covers International and UK-domestic routing; the complete workflow contract requires explicit market selection. |
| P04 | pass | `test_handbook_project_manager.py` proves no image-route inference and blocks incomplete preflight; the compact entry repeats the mandatory external-image question. |
| P05 | pass | Provider parser, URL-first Provider, AP Provider, and market Provider tests cover official discovery, ambiguity, year selection, download, and evidence extraction. |
| P06 | pass | `test_syllabus_outline.py` covers source coverage, container audit, atomic splitting, justified merging, and rejection of broad collapsed topics. |
| P07 | pass | `test_architecture_guards.py`, `test_write_concept_explanations_from_jobs.py`, and the exact workflow contract preserve the LLM/Python ownership boundary. |
| P08 | pass | `test_cover_templates.py` and the AP cover test preserve fixed AQA, Edexcel, CAIE, and AP geometry, palettes, A4 print rules, and output identities. |
| P09 | pass | The compact entry fixes rebuild -> import -> approve -> render-only order; the exact workflow contract and release-script tests preserve approval invalidation and asset-import behavior. |
| P10 | pass | Visual job, visual semantic, visual manifest, delivery matrix, and validation tests preserve per-topic routing, text-card rejection, semantic contracts, and pending-state blocking. |
| P11 | pass | `test_final_review_packet.py` proves HTML-first review, LLM-owned approval, repair/rerender behavior, and refusal to export PDF from unreviewed HTML. |
| P12 | pass | Final-review and render-snapshot tests cover HTML, plan, visual asset, shard, render pointer, ledger, and approval hash invalidation. |
| P13 | pass | PDF export, final-review, delivery audit, and validation tests cover export blocking, candidate promotion, A4 geometry, blank pages, and current-delivery state. |
| P14 | pass | The compact entry requires every batch subject to have an independent outline, visual review, HTML approval, and conclusion; the exact workflow contract forbids sampled final approval. |
| P15 | pass | `reports/cli-contract-parity.json` records root plus nine subcommands with matching help and exit status: `10/10`. |
| P16 | pass | The engine is byte-identical, schema and delivery tests pass, and `reports/demo-output-parity.json` records no missing, extra, or changed normalized artifacts. |
| P17 | pass | Validation, rendering-text, PDF-text, SVG-template, and visual-semantic tests cover Unicode artifacts, formulas, SVG safety, A4 geometry, and blank-page blocking. |
| P18 | pass | `reports/legacy_regression.xml` records 656 collected tests, 491 passing, 165 pre-existing skips, 0 failures, and 0 errors. |
| P19 | pass | The install ZIP includes both concept and visual import helpers; reverse-install probes verify they activate the isolated packaged runtime without the repository source tree. |

## Evidence Boundaries

- `reports/workflow_contract_parity.json` proves the authoritative workflow from
  `## Boundary Compliance Gate` onward is exactly preserved.
- `reports/wheel-payload-parity.json` proves all 77 packaged Python source files
  match the current migrated source bytes. The only migration-specific engine
  adjustment is the canonical-root `SKILL.md` help-path correction; command and
  artifact behavior remain compatible with the v0.6.2 baseline.
- `reports/packaged_runtime_import.json` proves the isolated runtime imports the
  installed wheel from `site-packages`, not the legacy source directory.
- `reports/output_review_adjudication.json` deliberately keeps six blind-review
  decisions pending. No human or provider-backed superiority claim is made.
- `reports/adoption_drift_report.json` records `no-data`; adoption evidence is
  unavailable and is not invented.
- `reports/package_verification.json` and `reports/install_simulation.json`
  prove the archive structure, adapters, root entrypoint, and installed Skill.
- The archive checksum is external by design: embedding a ZIP's own SHA-256
  inside that ZIP would create a self-referential and therefore unstable hash.
