# Project Agent Guidance

## Start Here

Read `PROJECT.md` before making changes. Then read:

1. `skills/exam-revision-handbook/SKILL.md`
2. `references/workflow-contract.md`
3. `references/revision_guide_spec.md`
4. `docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`
5. `docs/PROJECT_OPERATIONS.md`

## Single Canonical Skill

- `skills/exam-revision-handbook/SKILL.md` is authoritative and is the GitHub
  CLI automatic-discovery entry.
- GitHub `main`, the matching tag, and its Release download are one current
  standard Skill release. The ZIP is the downloadable form of that release,
  never another edition, structure, or development line.
- Do not recreate the retired `skill/` workflow, a root-level wrapper
  `SKILL.md`, or another nested workflow.
- `src/` and `tests/` are development support for the same standard Skill, not
  a legacy product.
- The installable ZIP is built from an allowlist and must keep one top-level
  `exam-revision-handbook/` folder with exactly one `SKILL.md`.

## Product Boundaries

- Keep rules independent of provider, qualification, subject, and batch size.
- Python may acquire evidence, validate structure, render, hash, record, and
  block. It must not replace LLM syllabus analysis, teaching writing, visual
  judgment, semantic review, or approval.
- The first-turn visual-capability question is a blocking preflight field. Do
  not infer an answer or silently select local image generation.
- Render and fully review HTML before PDF export. Machine diagnostics cannot
  approve a handbook.
- Every handbook in a batch requires an independent full review and delivery
  record.

## Change Discipline

- Make the smallest change that satisfies the current request.
- Preserve unrelated user changes and public assets.
- Update `CHANGELOG.md` for every completed iteration.
- Keep the canonical Skill, references, Agent metadata, evals, README files, and tests in
  sync when their shared contract changes.
- If engine behavior changes, rebuild and re-lock the embedded Wheel. A source
  change without a matching runtime asset is incomplete.
- Do not include generated outputs, official PDFs, caches, local paths, private
  notes, promotional MP4 files, or review scratch data in commits or Releases.

## Validation

Run the applicable checks before handoff:

```text
python -m pytest -q
python -m ruff check .
python -m compileall -q src tests scripts evals
python -m mypy src/intl_exam_guide
python scripts/scan_for_raw_keys.py .
python scripts/doctor.py
python scripts/build_skill_store_package.py
git diff --check
```

For a release, also run the governed Yao gates, reverse-install the final ZIP,
run its doctor/CLI/helper probes, inspect the full Git diff, and re-query the
published GitHub Release assets.

## Publication

- The maintainer has explicitly requested routine GitHub source synchronization: follow the standing synchronization policy below after validating authorized work. Tags, Releases, release-asset replacement, and registry publication still require an explicit release request.
- Release attachments are only the versioned Skill ZIP and its
  checksum file unless the user explicitly changes that policy.
- GitHub source archives are not substitutes for the installable Skill ZIP.

## GitHub Synchronization

- Standing maintainer instruction: after completing and validating an authorized change, commit the task's source, documentation, and tests, then push to the canonical GitHub branch. Do not leave completed work only in the local working tree unless the user explicitly requests local-only work or a concrete blocker prevents synchronization.
- Fetch before committing; preserve unrelated edits and review remote divergence. Never discard work or force-push to make branches match.
- Keep generated outputs, private data, secrets, local review reports, and release scratch files out of commits. Stage explicit task paths rather than blindly adding the entire working tree.
- Verify the remote branch SHA matches the local commit after pushing. Report the branch, commit, and any remaining unpushed work or synchronization blocker.
- Source synchronization does not itself authorize a new tag, GitHub Release, overwritten release asset, or package-registry publication. Keep unreleased behavior labeled accurately and report release-channel status separately.
