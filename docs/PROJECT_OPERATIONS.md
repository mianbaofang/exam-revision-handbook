# Project Operations Guide / 项目维护说明

Last updated: 2026-07-24

This file is the operational memory for future sessions and agents. Update it
whenever release flow, validation rules, animation assets, repository hygiene, or
Skill usage changes.

## 1. Project Positioning

This repository publishes an AI Skill and Python support package for generating
source-backed IGCSE, AS, A-Level, and College Board AP revision handbooks.

Current public scope:

- AQA, Edexcel, CAIE, and College Board AP are the supported source families.
- Automatic acquisition covers the International and UK-domestic
  AQA/Edexcel/CAIE IGCSE, AS, and A-Level routes plus College Board AP. The
  first preflight must explicitly distinguish `international` from
  `uk-domestic` for those three boards, then route discovery through the
  selected official Provider and retain the choice in source metadata. Other
  systems have no automatic provider; manual imports are unverified and may
  fail with unknown compatibility errors.
- AQA uses OxfordAQA / Oxford International AQA for International routes and
  the AQA official subject catalogue for UK-domestic routes.
- Edexcel and CAIE use market-specific official candidate matching plus
  official URL/PDF fallback. If the route is ambiguous, return candidates and
  wait for the user.
- Do not claim support for OCR, WJEC/Eduqas, CCEA, or every UK exam board.
- Do not commit official PDFs, past papers, mark schemes, copied exam questions,
  API keys, local absolute paths, private local notes, or generated output
  folders.

User-facing promise:

1. User gives the Skill link to OpenClaw, Hermes, or another Skill-compatible
   Agent.
2. User asks for a subject revision/study handbook.
3. Agent first asks the blocking visual-capability question: whether the user can
   provide or enable a callable external image-generation Skill or tool for this
   run. It must wait for the answer and must not silently default to local image
   generation. Agent then confirms exam board, level, course market
   (`international` or `uk-domestic` for AQA/Edexcel/CAIE IGCSE, AS, and
   A-Level), subject, required exam year, term-support language, explanation
   style, and workflow mode. The workflow-mode prompt must
   explicitly offer default single-host Analyst/Writer/Reviewer role passes or
   optional multi-agent delegation when the user wants separate agents and the
   runtime supports them.
4. Agent fetches official public syllabus/specification sources and official PDF runs produce dual-track evidence: `syllabus-evidence.json`, `source/specification.md`, and `source/markdown-extraction.json`.
5. Analyst reads Markdown for document structure and page-level evidence for
   source truth, then writes independently assessable, source-backed syllabus
   units. Python must not split topics from Markdown or promote directory
   headings into final topics.
6. Agent builds topic guides, concept-writing jobs, worked examples, visual
   briefs, and HTML. PDF is not generated yet.
7. Agent writes/imports reviewed concept explanations from
   `concepts/concept_jobs.json` before treating the handbook as final.
8. Agent keeps the lightweight operating roles clear: Analyst writes the outline,
   Writer writes content and per-topic visual decisions, and Reviewer inspects the
   visible handbook. These roles may be separate agents when explicitly requested,
   but the default Skill contract does not require a project-manager or release
   certification workflow. Review completion is not the same as final-ready
   approval.
9. The user's active LLM/Agent personally opens the current rendered HTML before
   handoff and reviews every final topic, worked example, answer, source anchor,
   and rendered visual. It checks topic sequence, concept explanations, visual
   semantics, glossary support, cross-page repetition, notation, and responsive
   layout against the syllabus outline. Every fixable problem returns to the
   Writer; after repair, the Agent rerenders and repeats the complete visible
   review. Python gates and Skill output are diagnostics, not approval. The pass
   must be recorded in per-item `review-ledger/` shards with visible evidence
   locations and summarized in `agent-product-review.json` with
   `reviewer_type: llm`, the ledger hash, render snapshot, and exact current
   HTML SHA-256. Only then may `export-pdf` create and technically validate a
   candidate before promoting it through `current-pdf.json`.

Verified delivery entries are only the routes recorded in the delivery matrix
with current evidence. Candidate routes must not be described as verified
delivery or release-ready until a fresh output passes validation and concept/
visual status checks, its current HTML receives complete hash-bound LLM review,
`current-pdf.json` points to a technically valid hash-bound export, and the release claim is recorded in
`docs/release-evidence/`. `review --out` and `final-review-packet.json` prepare
supporting diagnostics only.

v0.6 release-evidence status vocabulary:

- `candidate`: route evidence exists, but it is not delivery-grade.
- `draft`: a fresh output exists, but concepts, visuals, PDF/export,
  validation, or Agent self-review still blocks final handoff.
- `final-ready`: current evidence passes validation, concept status, visual
  status, complete current-HTML LLM review, gated PDF export, and package checks.
- `certified`: final-ready evidence has also been approved by the release owner
  or a subject-aware reviewer and recorded in a release-evidence manifest.

Do not call any route certified unless the manifest explicitly says so. A v0.3
ready packet is historical evidence, not a standing v0.6 certification.

## 2. Source Of Truth

- GitHub repository: `https://github.com/mianbaofang/igcse-a-level-revision-guide`
- GitHub Pages: `https://mianbaofang.github.io/igcse-a-level-revision-guide/`
- Skill entry: `https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill`
- Repository wrapper: `SKILL.md` (discovery only; it points to `skill/SKILL.md`)
- Agent maintenance rules: `AGENTS.md`
- Package version: `pyproject.toml` and `src/intl_exam_guide/__init__.py`
- Release history: `CHANGELOG.md` and GitHub Releases
- Public home page: `docs/index.html`
- English/Chinese README: `README.md`, `README.zh-CN.md`
- Delivery matrix: `tests/fixtures/delivery_matrix.json`
- Release evidence manifest docs: `docs/release-evidence/`
- Workflow boundary: `docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`
- Optional multi-agent design notes: `docs/MULTI_AGENT_ORCHESTRATION.md`, `docs/multi-agent-optimization-plan.md`

Do not use old local clones or generated outputs as proof of current behavior.
When verifying user experience, start from the GitHub repository or the clean
current working copy.

## 3. Mandatory Update Rule

Every project update must decide whether these files need changes:

- `CHANGELOG.md`
- `README.md`
- `README.zh-CN.md`
- `docs/index.html`
- `docs/PROJECT_OPERATIONS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/MULTI_AGENT_ORCHESTRATION.md`
- `skill/SKILL.md`
- `skill/references/revision_guide_spec.md`

If the change affects actual generation behavior, validation, provider support,
CLI options, image routing, release flow, or animation assets, update this file.

Documentation-only wording fixes do not require a package version bump. Any
functional change to Skill behavior, validation, CLI, providers, rendering, or
release assets should bump the patch version.

v0.2.17 added the anti-template language gate. Future wording/tone changes that
affect generated handbook text or validation warnings are functional changes and
should bump the patch version.

v0.2.18 raised the CI coverage gate to 70% and split infographic rendering out
of `rendering/html.py`. Keep parser, renderer, and practice-generator guard
tests updated whenever those areas change.

v0.2.19 fixed a real product-labeling regression: unknown, synthetic, or demo
sources must not fall back to AQA branding. Future provider-label changes need
tests for both explicit AQA detection and neutral unknown-provider output.

v0.2.20 closed the sixth-round audit loop around stale local artifacts and
generator coverage. Release evidence must come from fresh outputs produced by
the current code; ignored `outputs/` folders and old `validation.json` files are
not valid proof. Keep `rendering/icons.py` tracked whenever renderer icon usage
changes.

The seventh-round audit follow-up raised coverage evidence past 80% and added a
fresh offline demo evidence requirement. When preparing the next release, record
the fresh demo/generate command plus the `validation.json` summary in
`CHANGELOG.md` or the GitHub Release notes, but keep the generated `outputs/`
folder ignored and untracked.

v0.2.21 closed the eighth-round testing-coverage gap by adding direct renderer
contract tests for cover identity, stylesheet/print layout, visual manifests,
generated raster reuse, legacy SVG replacement counters, modular handbook packaging, and the
Playwright Chrome-to-Edge PDF fallback route. Future rendering changes should
update these contract tests instead of relying only on end-to-end demo coverage.

v0.2.22 closed the ninth-round rendering coverage gap by adding direct
`rendering/html.py` contract tests for the full HTML entry point, topic-section
renderer, guide cards, diagrams, story-mode blocks, practice cards, visual
example routing, source appendix, assessment fallback, navigation, and topic
title localization. Keep this module covered with direct unit tests whenever
handbook structure changes.

v0.2.23 closed the tenth-round P3 audit items: weak truthy assertions were
converted to exact-value assertions, `zh-CN` rendering branches received direct
contract coverage, `rendering/svg_templates.py` and `rendering/text.py` gained
dedicated tests, and fresh offline demo evidence was restored in the release
notes. Future test-only releases still need fresh demo evidence unless this
operations document and `docs/RELEASE_CHECKLIST.md` explicitly define an
exemption.

v0.2.24 closed the eleventh-round P3 follow-up: dedicated tests now cover
explanation-style branches, localization helpers, `zh-CN` HTML helpers, the
`render_html()` Chinese entry path, SVG slash wrapping, and long-text truncation.
The concept fallback SVG is English-only because Chinese visuals already use
`render_zh_visual_svg()`. Raw-key release scans must use the same command as
`docs/RELEASE_CHECKLIST.md`: `python scripts/scan_for_raw_keys.py . ./outputs`.

v0.2.25 closed the twelfth-round precision pass: Chinese localization and
explanation-style tests use exact input-to-output assertions, `zh_visual_type()`
has dedicated route coverage, and public animation source/export HTML is guarded
so visible version labels match the package version.

v0.2.26 closed the thirteenth-round audit follow-up: dedicated tests now cover
subject profile routing and validation checks directly, `zh_topic_reference()`
and `zh_visual_type()` assertions are more precise, and the animation version
guard rejects any stale `v0.2.x` label rather than only one historical version.

Concept-explanation quality is a cross-subject pipeline rule, not a per-subject
patch area. The shared generator may create source-bound draft prompts and
`concepts/concept_jobs.json`; final student-facing concept text must be written
from those jobs and imported with `scripts/import_concept_explanations.py`.
Release evidence is not ready while
`validation.json.review_summary.pending_concept_explanations` is nonzero.

v0.3 introduced the student-facing usefulness checks. They remain historical
release context, not a substitute for the current per-handbook LLM HTML review.
For every release sample or user-facing final guide, the active LLM must inspect
the complete HTML and the exact rendered visuals; `final-review-packet.json`
remains supporting evidence only. Complex infographic assets must be
reviewed/imported or clearly left as non-final image jobs. SVG is appropriate
only for reviewed `svg_fit: "exact"` cases; it must not be used as a blanket
substitute for complex instructional infographics.

v0.6 keeps the release-evidence layer conservative rather than changing the v0.3 facts.
For any route promoted above `candidate`, create or update a concise
`docs/release-evidence/<version>/manifest.json` entry with the command,
git revision, validation summary, final-review summary, concept/image status,
PDF status, and reviewer decision if certified. Do not commit the generated
output directory used to collect that evidence.

Final-round maintenance updates that touch `skill/`, validation behavior,
release-facing docs, or public audit claims must record the exact validation
evidence and update `CHANGELOG.md`. Synchronizing an installed Skill copy,
committing, pushing, or creating a GitHub Release is a separate publication
step and requires the user's explicit request. For a local-only iteration,
report that publication is pending rather than attempting an outward change.

## 4. Version And Release Rules

Use GitHub Releases, not tags alone.

Standard flow for a functional release:

```powershell
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
python scripts/sync_intro_animation_sources.py --check
python scripts/build_skill_store_package.py
git diff --check
git status --short
```

Then:

1. Update `pyproject.toml`.
2. Update `src/intl_exam_guide/__init__.py`.
3. Update `CHANGELOG.md`.
4. Update README/project docs if the public promise changed.
5. Build the store package and verify that `SKILL.md` is at archive root and
   byte-identical to `skill/SKILL.md`.
6. If `skill/` changed, synchronize the installed local Skill copy and verify it
   matches the repository copy.
7. Commit intentionally.
8. Create an annotated tag, for example `vX.Y.Z`.
9. Push `main`.
10. Push the tag.
11. Create or update the GitHub Release for that tag.

The Release should contain:

- version title;
- what changed;
- validation commands and results;
- release-evidence manifest path and status summary when any route is claimed
  as `draft`, `final-ready`, or `certified`;
- usage reminder with the Skill link;
- the versioned Skill-store ZIP whose archive root contains `SKILL.md`;
- optional Chinese/English MP4 files only when the release intentionally offers
  downloadable intro videos;
- Source code assets generated by GitHub.

Do not leave a version visible only under `/tags`. The user-facing release page
should be under:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/releases
```

## 5. GitHub Release Creation

Preferred method when GitHub CLI is installed:

```powershell
gh release create vX.Y.Z --repo mianbaofang/igcse-a-level-revision-guide --title "vX.Y.Z · short title" --notes-file RELEASE_NOTES.md --latest
```

If GitHub CLI is unavailable, use the GitHub Releases REST API with the existing
Git credential manager token. Never print or commit the token.

Minimum release payload fields:

- `tag_name`
- `target_commitish`
- `name`
- `body`
- `draft: false`
- `prerelease: false`

If the release already exists, update it instead of creating a duplicate.

## 6. Animation Asset Rules

Animation files:

- Chinese wrapper: `docs/project-intro-animation.html`
- English wrapper: `docs/project-intro-animation-en.html`
- Chinese source: `docs/assets/three-board-support-video/`
- English source: `docs/assets/three-board-support-video-en/`
- shared theme: `docs/assets/intro-animation.css`
- embedded-source synchronizer: `scripts/sync_intro_animation_sources.py`
- current handbook page assets: `docs/assets/v060-*.jpg`
- README GIF previews:
  - `docs/assets/intro-animation-preview.gif`
  - `docs/assets/intro-animation-preview-en.gif`

Rules:

- Chinese README must show Chinese animation/GIF.
- English README must show English animation/GIF.
- Stage size is `1920x1080`.
- Stage duration is `48` seconds.
- README GIF preview should be 16:9, normally `960x540`.
- HTML animation must autoplay in page, not require opening raw code.
- Animation source must not hardcode a release version label. The README and
  Release carry the version; `tests/test_release_scripts.py` guards both source
  and embedded animation pages against stale labels.
- Run `python scripts/sync_intro_animation_sources.py` after changing shared
  animation primitives or either language's `video.jsx`, then run the same
  command with `--check` before release.
- If animation source text changes, regenerate the relevant preview GIF.
- MP4 export is optional and should not be committed unless a release explicitly
  needs a downloadable video file.

Render command:

```powershell
python scripts/render_intro_animation.py --html docs/project-intro-animation.html --mp4 outputs/project-intro-animation.mp4 --gif docs/assets/intro-animation-preview.gif
python scripts/render_intro_animation.py --html docs/project-intro-animation-en.html --mp4 outputs/project-intro-animation-en.mp4 --gif docs/assets/intro-animation-preview-en.gif
```

For quick README preview refresh, a shorter preview may be rendered, but the
HTML source must still represent the current project.

## 6A. Skill-Store Package

The repository root and the store upload are intentionally different layouts.
The repository root `SKILL.md` is a discovery wrapper; the store archive must
promote the contents of `skill/` so the authoritative `SKILL.md` is immediately
visible at archive root.

```powershell
python scripts/build_skill_store_package.py
```

The builder writes a deterministic versioned ZIP under `dist/`, rejects unsafe
or nested archive paths, verifies byte equality with `skill/SKILL.md`, and prints
its SHA-256. Do not upload GitHub's automatically generated source archive as a
substitute for this artifact.

## 7. Skill And Image Routing Rules

The Skill must not present GPT Image, Qwen Image, or SenseNova as built-in
callable providers.

Current public logic:

- recommended external models: GPT Image 2.0, Qwen Image 2.0 Pro, SenseNova U1
  Fast;
- base generator writes visual briefs and prompt queues;
- real image generation only happens if the user provides a callable route,
  API/script, image-generation Skill, designer workflow, or generated asset
  directory;
- the first preflight must confirm whether any such callable route exists before
  source acquisition or local image generation. After topic-specific visual
  decisions are written, a confirmed callable route should be run and its
  reviewed assets imported automatically;
- exact SVG is a reviewed exception for `svg_fit: "exact"` cases, not a
  fallback for complex visuals; unreviewed or non-exact SVG must block final
  delivery.

External complex-infographic prompts should preserve the revision-worksheet
look that has tested well: landscape layout, large topic banner, clear teaching
panels, pastel subject colors, readable black English labels, accurate diagrams
or icons, and a small Quick Q&A or practice box. If generated images drift into
generic icons, brand-logo posters, course covers, or low-density decorative art,
fix the prompt or regenerate before importing them as reviewed assets.

Do not show a user-facing menu that implies these models are always available.
Ask the capability question first, then confirm subject/language/style. Report
complex infographic needs after the per-topic handbook plan exists.

After changing `skill/`, synchronize any locally installed Skill copy from the
repository's `skill/` directory, verify the installed files match the repository
files, and publish the change through the normal GitHub Release flow unless the
user explicitly asks for a local-only draft.

## 8. Validation Rules

Validation must fail on student-facing output that is visibly incomplete.

Important error cases:

- downloaded specification yields too few syllabus topics;
- missing topic guides or practice coverage;
- Chinese placeholder text such as numbered generic syllabus points;
- repeated practice questions under the same topic;
- cross-subject borrowed practice templates;
- missing source URLs or missing specification metadata;
- pending or missing concept-explanation review jobs;
- Edexcel/CAIE ambiguity resolved by guessing instead of returning candidates;
- downloaded official PDFs that only produce generic `Content unit` topics;
- downloaded official PDFs that produce no assessment-paper structure;
- missing manifest files or broken image references.

Important warning cases:

- remaining formulaic AI-style wording in student-facing topic guides or
  practice cards after the anti-template language pass.

Approval rules:

- `review --out` prepares diagnostics and rerenders HTML; it does not approve
  the handbook or export PDF;
- the active LLM must visibly inspect every final topic and every rendered visual,
  record per-item decisions and evidence locations in `review-ledger/`, and bind
  the compact `agent-product-review.json` summary to that ledger;
- `export-pdf` is the only delivery export path and must remain blocked until the
  current HTML hash has valid LLM approval; it promotes only a technically valid
  candidate and writes `current-pdf.json`; any later HTML change marks that PDF
  historical without deleting it.
- The visual-manifest lifecycle is ordered: explicitly refresh a new manifest
  cycle, generate/import assets, write the LLM visual decision, render from the
  existing manifest only, complete HTML review, then export PDF. Import or
  rebuild operations after visual approval are ordering errors.
- Reuse requires an unchanged source-bound `spec_hash`; changed visual specs
  and replaced assets reset visual approval to `pending`. Unreferenced image
  files are historical unless cleanup is explicitly approved. Any manifest or
  asset mutation without a new render snapshot and complete LLM review blocks
  delivery. The delivery gate also checks that the manifest matches the current
  plan's visual briefs by count, derived key, and `spec_hash`, so direct HTML
  rendering cannot approve a stale visual list.

Use `export-pdf --delivery-dir <directory>` only when a controlled final copy is
needed. The copy must match the current PDF hash. A differing destination is a
hard conflict unless the operator explicitly adds `--supersede-existing`, which
archives the former file first.

PDF export should try Playwright first, then fall back to a local Chrome/Edge
browser. If both routes fail, record a clear PDF export error instead of
masking the rest of the generation run.

Do not treat `issues: []` as meaningful unless the run was generated from the
current code and not copied from old `outputs/` folders.

For concept-output audits, read these counters together:

- `concept_jobs`: concept-writing jobs emitted for the current guide;
- `reviewed_concept_explanations`: topics whose reviewed concept explanations
  were imported;
- `pending_concept_explanations`: topics still blocked from final delivery.

For visual-output audits, read the three counters together:

- `generated_infographic_assets`: reviewed/generated raster infographic files;
- `svg_fallback_assets`: legacy SVG fallback files detected for replacement or
  explicit review under the exact-SVG policy;
- `pending_infographic_assets`: complex briefs still waiting for external
  image generation or human review.

A prompt-queue run can legitimately have `generated_infographic_assets: 0` if
pending infographic jobs were written and the warning clearly states that final
complex infographics still need an external model, script, or imported raster
asset.

## 9. Repository Hygiene

Keep committed files focused on source, docs, Skill, tests, screenshots, and
animation assets.

Ignored or local-only artifacts:

- `outputs/`
- `review-approvals/`
- `visual-prompts/`
- `visual-review/`
- `MP4/`
- top-level `NUL` residue;
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`
- `*.egg-info/`
- downloaded official PDFs;
- generated release sample folders unless explicitly converted into tracked
  screenshots/assets.

Before committing:

```powershell
git clean -fdX -n
python scripts/scan_for_raw_keys.py . ./outputs
rg -n "local-private-path-pattern" . -S -g "!outputs/**" -g "!.git/**"
```

Run `git clean -fdX` only after reviewing the dry run. Never remove unrelated
user folders or subject-study materials.

Do not commit temporary review notes, subagent scratch files, local API outputs,
or one-off audit transcripts unless they are promoted into public documentation.

## 10. Local Folder Migration Notes

Local project paths may change. Do not write machine-specific absolute paths
into public docs.

When moving the repository:

1. confirm `git status --short` is clean or commit changes first;
2. copy or move the entire repository directory;
3. run `git status --short` in the new location;
4. run a smoke test or at least
   `python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q`;
5. synchronize the installed Skill copy if `skill/` changed;
6. remove old duplicate clones and ignored outputs after confirming the new
   location works.

The public docs should describe procedure, not a private workstation path.
