# Project Guide / 项目总说明

## 1. Project Identity / 项目身份

This is one open-source project, not a family of parallel repositories.

- Public repository: `mianbaofang/exam-revision-handbook`
- Product name: **Exam Revision Handbook**
- Canonical Skill name: `exam-revision-handbook`
- Current Skill release: `v0.7.1`
- Canonical branch: `main`

本项目只有一个公开仓库和一条持续迭代线。`v0.7.0` 将原有项目迁移为标准
Skill 结构，`v0.7.1` 统一仓库、Skill、运行引擎和发布文件的名称与版本；以后直接在
当前结构上更新，不再维护旧的嵌套 `skill/` 工作流，也不再建立
第二个公开项目。

迁移前的旧结构已单独归档作为回滚证据，但它不是当前开发来源，不得从归档中复制旧
`SKILL.md` 覆盖当前版本。

GitHub `main`, its matching tag, and the Release download are one current
standard Skill release. The ZIP is simply the downloadable form of that same
release; it is not another edition, structure, or source of truth. `src/` and
`tests/` are maintenance directories inside the same current version. The
legacy structure exists only in the external rollback archive.

换句话说，GitHub `main`、对应 tag 和 Release ZIP 就是同一个 `v0.7.1`；ZIP 只是
它的下载形式，不是“精简版”、第二套结构或另一条开发线。

## 2. Product Scope / 产品范围

The Skill creates source-backed, printable revision handbooks for:

- UK GCSE and A-Level routes from AQA and Pearson Edexcel;
- International GCSE (IGCSE) and A-Level routes from OxfordAQA, Pearson
  Edexcel, and Cambridge International / CAIE;
- College Board Advanced Placement (AP).

AS and A2 are stages inside A-Level. They are not separate curriculum systems.
CAIE is Cambridge International; a `uk-domestic` selection records UK-centre
context but does not invent a separate CAIE UK GCSE product.

Other curricula and exam boards have no automatic official-source Provider.
Manual imports are experimental and may fail with unknown compatibility errors.

## 3. One Source Of Truth / 唯一权威入口

The root [SKILL.md](SKILL.md) is the only authoritative Agent entry.

Read these files in order before changing behavior:

1. `SKILL.md`: compact mandatory workflow and stop conditions.
2. `references/workflow-contract.md`: complete workflow rule surface.
3. `references/revision_guide_spec.md`: artifact, review, rendering, and
   delivery contracts.
4. `references/runtime-contract.md`: packaged engine boundary.
5. `docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`: LLM/Python ownership.
6. `docs/PROJECT_OPERATIONS.md`: maintenance and release procedure.

There must never be another authoritative `SKILL.md` below the repository root.
In particular, do not recreate `skill/SKILL.md` or turn the root file back into
a discovery wrapper.

## 4. One Current Version / 唯一当前版本

The repository root is the complete current standard Skill project. Every file
committed at the tag belongs to that one release. The Release ZIP is generated
from the same tagged commit as its ready-to-use download; it does not define a
second project, version, workflow, or structure.

```text
SKILL.md         canonical Agent entry
agents/          OpenAI and portable interface metadata
references/      workflow, artifact, provider, and runtime contracts
assets/runtime/  pinned Python engine Wheel and SHA-256 lock
evals/           trigger, workflow, migration, and parity fixtures
reports/         governed Skill evidence
security/        permission and network policies
skill_atlas/     generated routing and maintenance metadata
scripts/         runtime adapters, import helpers, and developer tooling
src/             maintainable Python engine source
tests/           engine and workflow regression suite
docs/            public documentation and GitHub Pages
```

`src/`, `tests/`, public README files, Pages assets, and maintenance tools are
part of this one open-source version. They remain in Git so the Skill can be
maintained and verified. Building the download only removes files a Skill host
does not run; it never creates another Skill structure or version.

The v0.7.1 download contains one top-level `exam-revision-handbook/` folder with
its root `SKILL.md`, required metadata, references, runtime assets, governed
evidence, and user-facing runtime/import scripts. It must contain no nested
`SKILL.md`, no `src/`, no `tests/`, no `docs/`, no cache, and no local path.

## 5. Runtime And Version Model / 运行时与版本

- `manifest.json` is the Skill release version and currently records `0.7.1`.
- Git tags and GitHub Releases follow the Skill version: `v0.7.1`.
- `assets/runtime/runtime-lock.json` pins the embedded Python engine and its
  exact Wheel hash.
- The v0.7.0 migration preserved the validated `0.6.2` engine behavior as its
  compatibility baseline. Starting with v0.7.1, the Skill manifest, Python
  package, embedded Wheel, runtime lock, Git tag, and Release share one version.
- Every future release must update source, tests, Wheel, runtime lock, parity
  evidence, and release notes together. The release identity test blocks stale
  names, versions, Wheel paths, or hashes.

Run the packaged engine only through:

```text
python scripts/doctor.py
python scripts/run_runtime.py -- <command>
```

The import helpers are also part of the installable Skill:

```text
python scripts/import_concept_explanations.py ...
python scripts/import_infographic_assets.py ...
```

They activate the same isolated, hash-checked runtime. They must not depend on a
global installation or on the repository `src/` tree being present.

## 6. Non-Negotiable Workflow Gates / 不可绕过的流程门禁

1. The first handbook response is the complete blocking preflight. It asks
   whether the user can provide or enable an external image-generation Skill or
   tool and collects every required field before any downstream work.
2. The LLM owns syllabus interpretation, atomic teaching points, teaching text,
   worked examples, visual judgment, semantic review, and final approval.
3. Python may retrieve, extract, validate, record, render, hash, and block. It
   may not invent LLM-owned decisions.
4. Visual state order is: rebuild manifest, import assets, record per-visual LLM
   approval, then render only. Rebuilding later invalidates approvals.
5. HTML is rendered and completely reviewed by the LLM before any PDF export.
   Every fix returns to writing, rerendering, and complete review.
6. PDF export is allowed only for the approved current HTML/render/ledger hash
   set, followed by PDF and delivery-copy hash verification.
7. Every handbook in a batch receives its own outline, visual decisions, HTML
   review, approval, PDF record, and conclusion. Sampling is forbidden.

## 7. Change Matrix / 修改同步矩阵

When changing workflow rules, review and update:

- `SKILL.md`
- `references/workflow-contract.md`
- `references/revision_guide_spec.md`
- `agents/interface.yaml` and `agents/openai.yaml`
- `evals/`
- English and Chinese README files
- `CHANGELOG.md`

When changing engine behavior, also update:

- `src/`
- focused and regression tests in `tests/`
- the embedded Wheel and `assets/runtime/runtime-lock.json`
- CLI, output-tree, and Wheel parity evidence

When changing packaging or release behavior, also update:

- `scripts/build_skill_store_package.py`
- `docs/PROJECT_OPERATIONS.md`
- `docs/RELEASE_CHECKLIST.md`
- package, installation, conformance, and trust reports

Every completed iteration is appended to `CHANGELOG.md`. Do not rewrite
historical release entries to make new work look older.

## 8. Validation And Release / 验证与发布

Minimum local validation:

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
```

For a governed release, also run the Yao validation, Skill IR, target compiler,
conformance, trust, registry, package verification, reverse-install simulation,
runtime permission probes, and installed-package CLI/helper checks. Reports must
be regenerated from the final version, not copied from an earlier candidate.

For migration acceptance, every P01-P19 row and every blocker-class governed
gate must pass. Optional human review, adoption telemetry, provider-backed
comparison, and world-class evidence must stay visibly `missing evidence` or
`no-data` when unavailable; never fabricate them merely to remove a warning.

Release attachments are limited to:

- `exam-revision-handbook-v<version>.zip`
- `exam-revision-handbook-v<version>.sha256`

Promotional MP4 files, generated handbooks, screenshots, test outputs, caches,
official PDFs, private notes, and machine-specific paths are not Release assets.

## 9. Agent Handoff Checklist / Agent 交接检查

Before editing:

1. Confirm this repository and `main` are the intended target.
2. Read this file and the six sources of truth in section 3.
3. Inspect `git status`; preserve unrelated changes.
4. State the exact success criteria and rollback boundary.

Before handoff:

1. Confirm only one `SKILL.md` exists in the current repository.
2. Show the changed-file scope and deletion scope.
3. Run the applicable validation and report exact results.
4. Verify the release ZIP by extracting it into a clean temporary location and
   running its doctor, CLI probes, and helper probes.
5. Push, tag, or create a GitHub Release only when explicitly authorized.
