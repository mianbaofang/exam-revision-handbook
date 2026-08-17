# Project Operations Guide / 项目维护说明

Last updated: 2026-08-17 for `v0.7.2`.

This file defines how to maintain and release the single public project. Read
[`PROJECT.md`](../PROJECT.md) first.

## 1. Canonical Project

- Repository: `mianbaofang/exam-revision-handbook`
- Default branch: `main`
- Skill name: `exam-revision-handbook`
- Canonical Skill entry: root `SKILL.md`
- Full workflow: `references/workflow-contract.md`
- Artifact contract: `references/revision_guide_spec.md`
- Skill version: `manifest.json`
- Engine source: `src/intl_exam_guide/`
- Engine runtime lock: `assets/runtime/runtime-lock.json`
- Release record: `CHANGELOG.md` and GitHub Releases

There is no second public repository and no nested authoritative Skill. A clean
clone, temporary extraction directory, or release staging directory is only an
operational copy of this same project. Never describe it as a new product.

GitHub `main`, its matching tag, and the GitHub Release ZIP are one current
standard Skill release. The ZIP is its downloadable form. Do not call them two
versions, two editions, or two structures.

## 2. Release Download Boundary

The Git repository itself is the standard Skill source. It also contains the
open-source maintenance material needed to verify and update its Python engine;
those files do not form a separate edition.

The Release ZIP is generated from the same tagged commit by
`scripts/build_skill_store_package.py` and contains one top-level
`exam-revision-handbook/` directory. Its root contains the authoritative
`SKILL.md`; there is no second `SKILL.md` below it and no separate workflow.

Maintenance-only content excluded from the Release download includes:

- `.git/`, `.github/`, `docs/`, `src/`, and `tests/`;
- public README and community files;
- release builder, animation, audit, and sample-maintenance scripts;
- generated `dist/`, caches, official PDFs, outputs, and local evidence.

Required Skill content in the Release download includes:

- `SKILL.md`, `agents/`, `references/`, and `manifest.json`;
- pinned runtime Wheel and `runtime-lock.json`;
- `doctor.py`, runtime bootstrap/adapter scripts, and both import helpers;
- governed eval, report, security, and Skill Atlas evidence selected for the
  package.

Package and install reports that depend on the final ZIP hash remain outside
the ZIP to avoid self-referential checksums.

## 3. Workflow Ownership

The host LLM owns:

- official-syllabus meaning and atomic teaching-point decomposition;
- teaching explanations, worked examples, and mastery summaries;
- one visual decision for every final teaching point;
- semantic review of every visual;
- complete visible HTML review, repair decisions, and final approval.

Python owns:

- source retrieval and page-level evidence extraction;
- structural validation, rendering, hashing, and state recording;
- runtime isolation and integrity checks;
- mechanical blocking of stale, incomplete, pending, or mismatched state.

Python diagnostics cannot approve a handbook. PDF generation is blocked until
the current HTML has a complete LLM review bound to its exact HTML, render, and
review-ledger hashes.

## 4. Mandatory Update Matrix

For workflow or Agent-behavior changes, inspect and synchronize:

- `SKILL.md`
- `references/workflow-contract.md`
- `references/revision_guide_spec.md`
- `agents/interface.yaml` and `agents/openai.yaml`
- `evals/`
- `README.md` and `README.zh-CN.md`
- `CHANGELOG.md`

For Python engine changes, also update:

- `src/`
- relevant tests
- package version when applicable
- embedded Wheel and runtime lock
- CLI, output-tree, Wheel-payload, and regression evidence

For package or release changes, also update:

- `scripts/build_skill_store_package.py`
- this document and `docs/RELEASE_CHECKLIST.md`
- conformance, trust, registry, package, and install reports

Every completed iteration is appended to `CHANGELOG.md`. Historical entries are
not rewritten as if a later change existed in an earlier release.

## 5. Versioning

The public Skill release version lives in `manifest.json` and drives the Python
package version, embedded Wheel, runtime lock, Git tag, Release name, ZIP name,
and checksum name. They must share one canonical name and version.

The v0.7.0 migration retained the validated `0.6.2` engine behavior as its
compatibility baseline. Starting with v0.7.1, `tests/test_release_identity.py`
blocks a release when the manifest, package, code, Wheel, runtime lock, or hash
is stale.

When engine source behavior changes, do not leave the old Wheel in place.
Rebuild it, update its SHA-256 lock, rerun the entire regression suite, and
refresh migration/runtime evidence.

## 6. Local Validation

Run from repository root:

```text
python -m pytest -q
python -m ruff check .
python -m compileall -q src tests scripts evals
python -m mypy src/intl_exam_guide
python scripts/scan_for_raw_keys.py .
python scripts/doctor.py
python scripts/normalize_governance_reports.py --check
python scripts/build_skill_store_package.py
git diff --check
git status --short
```

The package builder must report:

- one top-level `exam-revision-handbook/` directory;
- one canonical Skill entry;
- no unsafe path or escaped reference;
- the required runtime and import helpers;
- no repository-only directories;
- a deterministic ZIP SHA-256 and matching `.sha256` file.

## 7. Governed Skill Gates

For a release, run Yao Meta Skill against a clean Skill-only staging copy made
from the same package allowlist. The staging copy is disposable and is never a
second project.

At minimum run:

```text
yao.py validate <stage> --require-manifest
yao.py skill-ir <stage>
yao.py compile-skill <stage>
yao.py conformance <stage>
yao.py trust <stage>
yao.py skill-atlas <stage>
yao.py package <stage> --platform openai --platform claude --platform generic --platform vscode --zip
yao.py registry-audit <stage>
yao.py package-verify <stage> --require-zip
yao.py install-simulate <stage>
yao.py runtime-permissions <stage>
```

After copying generated reports back from the disposable stage, normalize only
their path metadata and validate every Atlas resource against the canonical
tree:

```text
python scripts/normalize_governance_reports.py --source-root <stage>
python scripts/normalize_governance_reports.py --check
```

This step may replace the generated stage path with `<SKILL_ROOT>` and restore
a uniquely resolvable nested resource path. It must not change a score, status,
warning, failure, or review conclusion. The package builder rejects any
remaining local absolute path or unresolved Atlas resource.

Also refresh the governed intent, output-risk, artifact-design, prompt-quality,
system-model, output-eval, Review Studio, adoption-drift, Python compatibility,
and architecture evidence when their inputs changed.

Do not edit generated reports to manufacture a pass. Fix the source contract,
rerun the generator, and keep unavailable human/telemetry evidence explicitly
marked as missing or no-data.

## 8. Reverse Installation Check

Before release:

1. Extract the final versioned ZIP into a clean temporary directory.
2. Confirm exactly one root Skill folder and one `SKILL.md`.
3. Run `python scripts/doctor.py` from the extracted Skill.
4. Run all ten CLI help probes through `scripts/run_runtime.py`.
5. Run `--help` for the concept and infographic import helpers.
6. Execute an isolated synthetic demo and compare its normalized artifact tree
   with the frozen parity fixture.
7. Scan extracted text for secrets, unsafe archive paths, local absolute paths,
   replacement characters, and stale version strings.

File presence alone is not installation proof. The installed runtime and helper
entry points must actually execute.

## 9. Delivery Evidence Vocabulary

The delivery matrix is `tests/fixtures/delivery_matrix.json`. It describes
current evidence, not a blanket promise for every subject.

Candidate routes must not be described as final-ready or certified.

- `candidate`: source-route evidence exists but delivery is not complete.
- `draft`: a current handbook exists with a named blocker.
- `final-ready`: the exact handbook has complete LLM HTML review, current
  concept/visual state, gated PDF export, and delivery evidence.
- `certified`: final-ready plus explicit release-owner or subject-aware review
  recorded in release evidence.

`final-review-packet.json` is supporting diagnostics only. A route or another
handbook's review cannot approve the current handbook. Every batch item must be
reviewed independently.

## 10. GitHub Release

Only publish after explicit user authorization.

1. Inspect the full Git diff and deletion list.
2. Confirm README, Chinese README, `CHANGELOG.md`, Project Guide, and package
   metadata describe the final state.
3. Commit and push `main`.
4. Create the `v<version>` tag and GitHub Release from `main`.
5. Attach only:
   - `exam-revision-handbook-v<version>.zip`
   - `exam-revision-handbook-v<version>.sha256`
6. Re-query the Release and verify asset names, sizes, URLs, and checksum.
7. Wait for CI and GitHub Pages to pass.

Do not attach promotional MP4s, screenshots, generated manuals, official PDFs,
or GitHub's automatic source archive as the Skill installer. Animation or site
maintenance is not a functional Release-note item unless it changes product
behavior.

## 11. Cleanup And Rollback

- Keep the verified pre-migration archive outside the active repository.
- Do not keep another editable legacy checkout beside the canonical project
  after replacement is complete.
- Remove only disposable extraction/staging directories after their hashes and
  reports are recorded.
- Never delete user outputs, review evidence, or unrelated files without
  explicit approval.
- If release validation fails, do not push a partial migration. Restore from
  Git or the verified archive, fix the failing gate, and rerun from the start.
