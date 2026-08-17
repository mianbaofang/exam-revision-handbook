# Changelog

## 0.7.2 - 2026-08-17

- Published the four post-v0.7.1 README presentation commits as one current release.
- Kept status badges and landscape preview pages in stable horizontal rows on GitHub.
- Bumped the canonical Skill and embedded Python runtime package to 0.7.2 without changing handbook-generation behavior.

## 0.7.1 - 2026-07-27

### Unified Product Identity And Public Discovery

#### Changed

- Unified the public repository, Skill ID, Python distribution metadata,
  runtime Wheel, release tag, download filename, documentation links, and
  provider User-Agent under `exam-revision-handbook` version `0.7.1`.
- Reworked the English and Chinese README entry points around one supported
  curriculum model: UK GCSE, International GCSE (IGCSE), A-Level with AS/A2
  stages, and College Board AP, using AQA, Edexcel, CAIE, and College Board
  official sources where supported.
- Added a bilingual GitHub Pages entry, canonical and `hreflang` metadata,
  Open Graph and structured-data metadata, `robots.txt`, `sitemap.xml`, and
  `llms.txt` so search engines and AI discovery systems can identify the
  repository by its GCSE, IGCSE, A-Level, AP, AQA, Edexcel, and CAIE scope.
- Rebuilt the embedded runtime as
  `exam_revision_handbook-0.7.1-py3-none-any.whl` and updated its locked
  checksum. The handbook workflow and generation contracts are unchanged in
  this release.
- Kept the release download as one complete standard Skill package with the
  root `SKILL.md`, runtime, providers, references, agents, assets, evaluation
  fixtures, security policy, and governed reports. Repository-only source,
  tests, documentation pages, caches, and post-package verification records
  remain outside the install archive.

#### Verified

- Full regression suite: `502 passed, 163 skipped`. Ruff, compileall, mypy for
  all 76 source files, governance-path normalization, raw-key scanning, and
  runtime integrity checks passed.
- Yao Governed validation passed with `0` blocker-class findings. Review Studio
  keeps `6` non-blocking warnings for unavailable human blind review, real
  adoption telemetry, waiver, promotion, and world-class evidence; none of
  those signals was fabricated.
- Built `dist/exam-revision-handbook-v0.7.1.zip` twice with the same SHA-256:
  `59bb417788fc95a11cb5eeca9c63f6c1e1ecf0f920643a68d18cd048be33b437`.
  The archive contains 102 files beneath one `exam-revision-handbook/` root,
  exactly one `SKILL.md`, and no unsafe path, machine-specific absolute path,
  raw key, replacement character, or stale current-version field.
- Reverse installation from the final ZIP passed the standard and deep runtime
  doctors, the root CLI and all nine subcommand help probes, and both import
  helper probes. The isolated demo produced the expected 25-file blocked draft;
  an unapproved PDF export failed and left the PDF count at zero.

## 0.7.0 - 2026-07-25

### Standard Skill Migration

#### Changed

- Replaced the former repository discovery wrapper plus nested `skill/`
  workflow with one canonical standard Skill at the repository root. The root
  `SKILL.md` is now the only Skill entry and directly links the workflow,
  artifact, Provider, migration, and runtime contracts in `references/`.
- Added standard Skill metadata, runtime assets, governed evaluation evidence,
  and explicit permission boundaries under `agents/`, `assets/`, `evals/`,
  `reports/`, `security/`, and `skill_atlas/`.
- Preserved the open-source Python engine in `src/` and its regression suite in
  `tests/` as parts of the same current Skill release. The Release ZIP is the
  strict-allowlist download generated from that same tagged commit.
- Added `PROJECT.md`, updated `AGENTS.md`, and rebuilt the operations guide so a
  later Agent has one current explanation of the canonical entry, ownership
  boundaries, package layout, version model, release procedure, and rollback
  policy.
- Defined GitHub `main`, its matching tag, and the versioned ZIP as one current
  standard Skill release, with no separate source edition, install edition,
  structure, workflow, or development line.
- Added deterministic governance-report normalization for generated path
  metadata and nested Atlas resources. CI and the package builder now reject
  machine-specific absolute paths and Atlas resources that do not exist in the
  install archive; report scores and conclusions are never rewritten.
- Replaced legacy architecture copy that still referenced `skill/SKILL.md` and
  incorrectly assigned teaching and visual decisions to Python. The current
  diagram separates root Skill instructions, LLM ownership, and deterministic
  runtime gates.

#### Preserved

- Preserved all current AQA, Edexcel, CAIE, and College Board AP Provider,
  cover, course-market, A-Level stage, atomic syllabus, teaching, visual,
  HTML-review, PDF, and batch-isolation contracts.
- Preserved the validated `0.6.2` engine command and artifact behavior inside a
  pinned Wheel. The wheel was rebuilt only to replace the deleted
  `skill/SKILL.md` help path with the canonical root `SKILL.md`; all 77 current
  source files still match the packaged payload. The standard package exposes
  the root CLI plus nine subcommands and both concept and visual import helpers
  without depending on repository `src/` files.
- Archived the complete pre-migration project outside the repository as
  `igcse-a-level-revision-guide-pre-v0.7.0-20260725.zip`. Its 452 files match
  the archived source tree and its SHA-256 is
  `bde77a6253bf3c18392737817804db8dcd96d3cc45c6b99b39b1eafc90541e4c`.

#### Verified

- Migration acceptance: `P01-P19` passed, `77/77` packaged engine source files
  are byte-identical, CLI contract parity is `10/10`, normalized demo artifact
  parity is `25/25`, known capability loss is `0`, and every blocker-class Yao
  Governed gate passed.
- Review Studio reports `0` blockers and retains `6` honest warnings for
  unavailable optional telemetry, provider, human-review, waiver, and
  world-class evidence; no evidence was fabricated to remove them.
- Full regression suite: `497 passed, 163 skipped`. Ruff, compileall, mypy for
  all 76 source files, raw-key scanning, animation-source synchronization,
  Skill Creator validation, and the packaged runtime doctor passed.
- Built `dist/exam-revision-handbook-v0.7.0.zip` deterministically: 102 files,
  515169 bytes, one top-level `exam-revision-handbook/` directory, exactly one
  `SKILL.md`, no maintenance-only source or promotional media, and SHA-256
  `b5a44dece732aa7f18abba595d97553ec6cd110c489239b9c008a6411db77acc`.
- Reverse installation from that ZIP passed the runtime doctor, root and
  subcommand help probes, both import-helper probes, concept import, visual
  import, pending-review preservation, and HTML-before-PDF blocking behavior.

## 0.6.2 - 2026-07-25

### Standard Skill Identity

#### Changed

- Renamed the installable Skill identity to `exam-revision-handbook` while
  retaining the keyword-rich public repository name
  `gcse-igcse-alevel-ap-revision-guide`.
- Kept the established `skill/` source directory and its workflow references
  intact. The install ZIP still exposes the standard root layout: `SKILL.md`,
  `agents/`, and `references/`.
- Shortened the Skill display name and release asset name while retaining GCSE,
  IGCSE, A-Level, AP, AQA, Edexcel, CAIE, and College Board in searchable
  metadata and documentation.

#### Verified

- Full test suite: `491 passed, 165 skipped`.
- `skill-creator` structural validation passed for `skill/` under UTF-8.
- Built and inspected `exam-revision-handbook-v0.6.2.zip`: seven required
  files, root `SKILL.md`, no nested Skill entry, no unsafe archive path, and
  SHA-256 `e0c482de0a86672acbd2eaaaed37ee042d7e744cb5450be523d959714f48a034`.

## 0.6.1 - 2026-07-25

### Public Repository Rename And Curriculum Terminology

#### Changed

- Renamed the public repository and Skill identifier to
  `gcse-igcse-alevel-ap-revision-guide`, preserving the `intl_exam_guide`
  Python import and CLI compatibility.
- Updated GitHub Pages, README installation links, site metadata, Skill-store
  package naming, provider user-agent metadata, and operations documentation
  to the new public address.
- Expanded the public display names, site titles, SEO metadata, and animation
  copy to include GCSE, IGCSE, A-Level, and AP. The animation now treats AS and
  A2 as A-Level stages rather than standalone curriculum systems.

#### Verified

- Full test suite: `491 passed, 165 skipped`.
- Ruff, compileall, mypy for six changed source files, and the raw-key scan
  passed with zero raw-key matches.
- Built and inspected
  `gcse-igcse-alevel-ap-revision-guide-skill-v0.6.1.zip`: the archive has
  seven files, `SKILL.md` at its root, no nested Skill entry, no unsafe archive
  paths, and SHA-256
  `ff7e3e71cb050372c4d294d6f2b27ff51b12758f12b02174ab64442b3b5c3053`.

### Iteration 2026-07-25 - Curriculum Terminology And A-Level Stage Model

#### Changed

- Reframed the public scope as UK GCSE, International GCSE (IGCSE), A-Level,
  and College Board AP. AS and A2 are now consistently described as A-Level
  stages rather than parallel curriculum systems.
- Corrected the AQA, Edexcel, and CAIE source-route matrix: AQA and Edexcel
  have UK-domestic and International routes, while CAIE uses the Cambridge
  International catalogue and does not claim a separate UK GCSE product.
- Added the `a_level_stage` coordinator field. New A-Level requests require
  `AS`, `A2`, or `full`; legacy `--level as` remains supported and maps to
  `level=a-level` with `a_level_stage=AS`.
- Updated generic handbook labels to use `A-Level`, while retaining official
  source titles and the `international_as_a_level` compatibility identifier.

#### Verified

- Focused provider, coordinator, cover, rendering, validation, and release
  contract tests: `145 passed, 29 skipped`.
- Ruff, compileall, mypy for six changed source files, and the raw-key scan
  passed with zero raw-key matches.
- The full suite reached `490 passed, 165 skipped`; its sole failure is the
  pre-existing repository-state check that calls `git check-ignore` while this
  workspace has no functional `.git` repository. No Git metadata was created
  or altered for this documentation and coordinator iteration.

## 0.6.0 - 2026-07-24

### Iteration 2026-07-24 - Public Copy And Infographic Correction

#### Changed

- Replaced the introduction animation's text-card visuals with three real
  ImageGen illustrations using distinct radial, linear-process, and teaching-
  instrument compositions. Chinese and English captions remain accurate HTML
  overlays rather than generated text.
- Replaced the archive-layout animation scene with a product-facing
  traceability scene covering official evidence, atomic requirements, reviewed
  teaching visuals, HTML approval, and controlled PDF delivery.
- Simplified both READMEs to link directly to the installable Skill package and
  removed author-facing archive guidance from public copy. The release notes
  now describe functional changes and independent handbook evidence only.
- Updated the public project page so its animation and capability descriptions
  reflect the current four-source workflow without release-production details.
- Constrained Ruff to the verified pre-0.16 rule semantics after Ruff 0.16
  changed its default rule set and made the unchanged repository fail CI.
- Completed the clean CI development dependency set and made the Skill-package
  byte assertion honor the builder's cross-platform LF normalization contract.

#### Verified

- Reviewed every scene in both 1920x1080 HTML animations through Playwright
  captures. The three illustration compositions are visibly distinct; images,
  localized captions, headings, and fixed footers do not overlap or clip.
- Rendered and inspected both final MP4 files at 1920x1080, 47.375 seconds,
  and 379 frames, plus both README GIFs at 960x540, 47.4 seconds, and 237
  frames. Representative frames extracted from the encoded MP4 files match the
  approved HTML scenes.
- A clean Python 3.11 environment installed successfully from `.[dev]`. Its
  final suite reported `489 passed, 165 skipped` with 70.41% coverage; Ruff,
  mypy for 76 source files, compileall, animation-source synchronization,
  raw-key scanning, and Git diff checks passed with zero raw-key matches.

### Iteration 2026-07-24 - Store Package, Public Showcase, And Release Evidence

#### Added

- Added a deterministic Skill-store package builder that promotes the contents
  of `skill/` to archive root, verifies the root `SKILL.md` byte-for-byte, rejects
  unsafe or nested Skill paths, canonicalizes text line endings across LF/CRLF
  checkouts, and prints the final SHA-256.
- Added 12 full-A4 preview pages from four independently reviewed handbooks:
  OxfordAQA IGCSE Biology, CAIE AS Physics, College Board AP Chemistry, and
  Pearson Edexcel International A Level Mathematics.
- Added a `v0.6.0` release-evidence manifest that records each handbook's own
  topic, practice, visual-review, HTML-review, ledger, PDF-page, and hash evidence
  without committing generated handbooks, PDFs, source PDFs, or local paths.
- Added an animation-source synchronizer so the shared primitives and each
  language's `video.jsx` cannot drift from the standalone HTML pages.

#### Changed

- Rebuilt both 48-second introduction animations around the four current source
  systems, hard first-turn preflight, market-specific Providers, atomic syllabus
  analysis, per-topic visual decisions, four current handbook samples,
  HTML-before-PDF review, and the store-ready archive layout.
- Replaced the old three-image README gallery with three visual teaching pages
  from each of the four current handbooks, and synchronized the English and
  Chinese installation, scope, version, and release wording.
- Bumped the package version from `0.5.3` to `0.6.0` and updated the public site,
  operations guide, and release checklist.

#### Fixed

- Fixed the Skill-store upload layout that caused stores to report a missing
  `SKILL.md` when users uploaded a repository folder or GitHub source archive.
- Updated the release-evidence verifier to default to `v0.6.0` and accept real
  semantic release versions at or above `v0.5.0`, instead of contradicting its
  own `v0.5+` contract by accepting only `v0.5` prefixes.

#### Verified

- Rendered and visually inspected the final Chinese and English introduction
  videos. Each MP4 is 1920x1080, 47.33 seconds, and 284 frames; representative
  frames from the actual videos were nonblank, sample assets loaded, and no
  text or controls overlapped or clipped. The two README GIFs are 960x540 and
  47.40 seconds.
- Verified four independent `final-ready` release-evidence entries with zero
  pending concepts or images. The repository raw-key scan reported zero
  matches, and the animation source synchronization check passed.
- Built `dist/igcse-a-level-revision-guide-skill-v0.6.0.zip` with seven files,
  one root `SKILL.md`, no nested Skill entry, and SHA-256
  `6b553f0ba834e80c7e64f24895834724afa5df78afa34abbd15c1153a626a688`.
- Final regression suite: `489 passed, 165 skipped`. Ruff, compileall, and mypy
  for all 80 source files and the changed release scripts passed.

### Iteration 2026-07-24 - Pearson Edexcel International A Level Mathematics Controlled Delivery

#### Fixed

- Completed the 2027 Pearson Edexcel International A Level Mathematics
  handbook for `YMA01`, covering P1-P4, M1-M2, D1, S1, and S2.
- Recovered the LLM-authored plan and completed a fresh 103-topic / 74-visual
  render review. The delivery record is bound to the current render snapshot,
  review ledger, and all reviewed visual assets.
- Corrected the binomial-approximation visual from programmer-style
  `sqrt(1 + x)` notation to a rendered square-root symbol, then reimported the
  asset, rerendered the HTML, and repeated desktop/mobile evidence capture.

#### Verified

- Controlled delivery audit: eligible with zero blockers; all 74 rendered
  visuals are reviewed and the final HTML has no broken images.
- Exported a 131-page A4 PDF to the Desktop Handbook folder. The delivered
  file is `pearson-edexcel-as-a-level-mathematics-20260724-0431.pdf` with
  SHA-256 `2d379b02a13fb033a6efc733cc5ce072bdbab15673f437ffa7ace8edde55fd0a`.
  The controlled source and Desktop copy have matching hashes; PDF text
  extraction found no `sqrt(` residue.
- Ruff, compileall, and mypy for the changed SVG asset helper passed. The full
  suite reported `482 passed, 165 skipped, 1 failed`; the single failure is the
  pre-existing architecture test assumption that this checkout has a working
  Git repository, while its `.git` directory is not a usable worktree. The
  raw-key scan reports one untouched temporary-page match at
  `tmp/caie-physics-9702-page-full.html:944`.

### Iteration 2026-07-24 - Course Market Preflight Gate

#### Fixed

- Added the required `course_market` preflight field for AQA, Edexcel, and
  CAIE IGCSE, AS, and A-Level requests. The user must explicitly choose
  `international` or `uk-domestic`; the Agent must never infer it from a title,
  code, URL, provider, or previous run.
- Added `AS` as a distinct preflight level and persisted the course-market
  choice in the coordinator state. Missing, invalid, or route-inappropriate
  market values now keep that state blocked.
- Added market-specific official Provider routing: OxfordAQA/AQA for the two
  AQA routes, Pearson International/Pearson UK for Edexcel, and Cambridge
  International for the selected CAIE qualification family. The market is now
  retained in source metadata and UK qualification labels no longer render as
  International labels.
- Aligned the Skill, coordinator prompt, reference contract, operations guide,
  and public English/Chinese scope statements around the two supported markets.

#### Verified

- Focused tests cover missing market values, UK route selection, invalid AP
  market selection, domestic AQA/Edexcel metadata, AS PDF selection, and prompt
  wording that prohibits market inference.
- Live official-provider checks retrieved and selected the expected source
  records for AQA UK GCSE Mathematics, Edexcel UK AS Mathematics, and CAIE UK
  Accounting. The AQA and Edexcel routes use their respective UK catalogues;
  CAIE retains the selected market while using the official Cambridge
  International qualification catalogue for that qualification family.
- Focused regression suite: `17 passed, 31 skipped`; Ruff, compileall, and
  mypy for the changed modules passed. The full suite reported `482 passed,
  165 skipped, 1 failed`; the remaining failure is the pre-existing
  architecture guard expectation of a functional Git worktree while this
  checkout has an empty `.git` directory. The raw-key scan completed and
  reported one untouched temporary-file match at
  `tmp/caie-physics-9702-page-full.html:944`.

### Iteration 2026-07-24 - AP Chemistry Controlled Delivery

#### Fixed

- Corrected scientific-notation handling in the AP Chemistry authoring helper
  so thermodynamic notation is not mistaken for a negative exponent.
- Repaired the reviewed AP Chemistry explanations and visuals covering
  mass-spectra qualification, ammonia geometry, phase-diagram slope,
  calorimetry conditions, reaction-energy semantics, equilibrium particle
  conservation, and electrolytic-cell electron paths.
- Rebound the LLM review ledger only after byte-for-byte comparison confirmed
  that all 132 required review screenshots were identical between the prior
  review evidence and the final visual-approval snapshot.

#### Verified

- Completed snapshot-bound LLM review of all 91 AP Chemistry topic guides,
  worked examples, 38 rendered visuals, and desktop/mobile HTML evidence.
- The controlled-delivery audit passed with zero blockers. Its 100 warnings
  are non-blocking checklist-length and formulaic-wording diagnostics, reviewed
  as non-factual defects.
- Exported a 94-page, 13.23 MiB A4 PDF with zero blank pages, zero blank-text
  pages, zero raw ASCII maths residues, and a hash-verified desktop copy:
  `2f319fb6400ee0142002daf2428b08976d3996f23f735bb7de09a65e0f2d441e`.
- Full tests: `476 passed, 165 skipped`; one architecture-guard test cannot
  run because the workspace has an empty/non-worktree `.git` directory. Ruff
  and compileall passed. Mypy reports nine untyped-JSON issues in the
  standalone AP authoring helper. The raw-key scan reports one untouched
  temporary source-page match at `tmp/caie-physics-9702-page-full.html:944`.

### Iteration 2026-07-23 - Visual Manifest Lifecycle And Approval Invalidation

#### Fixed

- Existing visual manifests now default to render-only behavior. Rebuilding a
  manifest is an explicit new visual-plan cycle, so importing assets or writing
  visual approvals cannot accidentally recreate the list and reset decisions.
- Reviewed/generated assets are reused only when the source-bound visual
  `spec_hash` is unchanged. A changed visual specification starts with no
  current asset and pending asset/visual-review state; legacy manifests without
  a hash remain readable for compatibility but still require a fresh visual
  decision.
- Importing or replacing an infographic resets
  `visual_need.reviewer_visual_decision` to `pending` while retaining the
  separate imported asset `review_status`. Unreferenced image files are no
  longer deleted during manifest rebuilds.
- Manifest/plan matching now rejects duplicate visual keys and count-mismatched
  manifests instead of allowing dictionary folding to hide inconsistent state.
- Maintenance scripts that replace SVGs, revise routes, or change visual prompts
  now reset the affected visual decision to `pending` instead of carrying an
  approval across changed visual semantics.
- Concept imports now start a new manifest cycle when an imported
  `visual_spec` changes; import commands fail instead of reporting success when
  the required rerender cannot complete. Asset imports likewise fail on a real
  rerender error rather than leaving a silently stale handbook.
- Rebuild reuse compares the recorded asset SHA-256 with the current file. A
  changed file under the same name is treated as a new unreviewed asset.
- The read-only delivery gate now verifies that the current visual manifest is
  the exact visual-spec set for the current `guide-plan.json`, including count,
  derived key, and source-bound `spec_hash`; direct `render_html()` calls cannot
  bypass this binding check.
- Manifest entries with a declared key that disagrees with their own topic,
  focus, visual type, or complexity are blocked instead of being treated as a
  valid lookup entry.
- The CCAPI asset-versioning maintenance path now resets the affected visual
  decision to `pending`, matching the normal asset-import contract.
- PDF raster derivatives marked as already optimized are not optimized again
  during a later explicit manifest refresh, preventing needless `-print-2` file
  churn and avoidable review invalidation.
- A review packet no longer continues silently after a current render exists
  but HTML rerender fails. Draft directories without a current render pointer
  retain the legacy packet behavior so incomplete fixtures remain reviewable as
  drafts.
- Raw-key scanning skips Windows reserved device-name files such as `NUL`, so
  the scan reports actual matches instead of failing while reading a device.

#### Workflow Contract

- Documented the enforced order: Writer visual specs -> explicit manifest
  refresh -> asset generation/import -> visual-level LLM approval -> render-only
  HTML -> complete LLM HTML review -> product approval -> PDF.
- Clarified that any plan, concept, manifest, or asset mutation requires a new
  render snapshot and complete LLM review; machine hashes block stale delivery
  but do not replace visual approval.
- Bumped the package patch version to `0.5.2`; publication and GitHub Release
  creation remain pending explicit user request.

#### Verified

- Added regression coverage for changed visual specifications not reusing old
  reviewed assets or approvals, render-only reuse, duplicate manifest keys, and
  asset import resetting visual approval.
- Targeted lifecycle tests: `86 passed, 1 skipped`.
- Full test suite: `476 passed, 165 skipped`; one existing environment failure
  remains because the workspace contains an empty `.git` directory rather than
  a Git worktree, so the architecture guard's `git check-ignore` call exits
  with code 128.
- Ruff, compileall, and mypy passed for the changed modules. The raw-key scan
  runs successfully and reports one pre-existing temporary-file match at
  `tmp/caie-physics-9702-page-full.html:944`; that local file was not changed
  or deleted.

### Iteration 2026-07-23 - CAIE AS Physics Controlled Delivery

#### Fixed

- Corrected the Topic 1 worked-example equation to `P = Fv` and repaired the
  I-V-characteristic visual caption so every explanation is visible in the
  rendered handbook.
- Rebuilt the external-image and exact-SVG manifest in the correct order so
  13 approved visual assets remain bound to the final render snapshot.

#### Verified

- Completed a snapshot-bound LLM review of all 35 CAIE AS Physics topics,
  35 worked examples, 13 rendered visuals, and desktop/mobile HTML evidence.
- The controlled-delivery audit passed with zero blockers and zero warnings.
  The 39-page PDF was exported and copied to the selected delivery directory
  with matching SHA-256 `548b2d99d6f584d91ac28205d4a2538fa613756aea7b0094ca52ebf3019eeefd`.

### Iteration 2026-07-23 - A4 Cover Responsive Isolation

#### Fixed

- Scoped the single-column cover breakpoint to screen rendering. A4 PDF export
  can no longer inherit the narrow-screen grid that stacked the title, course
  identity card, syllabus metadata, and feature cells inside a fixed-height
  print page and caused them to overlap.
- Let genuinely narrow screen covers grow with their content instead of
  constraining stacked cover blocks to a viewport-derived grid row.

#### Compatibility

- Preserved the shared cover structure and the fixed AQA, Edexcel, CAIE, and AP
  palettes. The change only separates screen responsiveness from A4 print
  geometry; course-derived cover text and Provider behavior are unchanged.

#### Verified

- Added a regression proving that narrow-cover rules are screen-only and that
  mobile cover rows expand with content.
- Exported and visually inspected a four-page A4 PDF containing AQA, Edexcel,
  CAIE, and AP covers. All four pages fill the printable A4 area; the course
  identity card, syllabus metadata, and feature cells remain separated, and
  each board keeps its fixed palette.
- Inspected the cover at a 390px screen width. The mast, main identity area,
  and footer flowed in order without intersecting bounding boxes.
- Cover and rendering regressions passed (`39 passed, 1 skipped`). The full
  suite reached `468 passed, 165 skipped`; its only failure is the existing
  architecture guard invoking Git against the workspace's empty/non-worktree
  `.git` directory. Ruff, Compileall, and targeted Mypy passed.
- Raw-key scanning passed across source, tests, scripts, Skill files, docs, and
  release Markdown. The whole-workspace scan remains blocked by a separately
  generated, unreferenced `tmp/caie-physics-9702-page-full.html` file reported
  at line 944; it was not altered or deleted by this iteration.

### Iteration 2026-07-23 - OxfordAQA Biology Responsive Review And Controlled Delivery

#### Fixed

- Contained the mobile cover decoration within the viewport and made narrow
  tables and long links wrap safely, preventing horizontal scrolling in the
  rendered handbook.

#### Verified

- Re-rendered OxfordAQA International GCSE Biology (9201) for 2027 and
  completed a snapshot-bound LLM review: 32 topics, 32 worked examples, 21
  rendered visuals, desktop/mobile evidence, source anchors, navigation,
  encoding, and responsive layout were reviewed.
- The controlled-delivery audit passed with zero blockers and zero warnings.
  The 43-page, 5.51 MiB PDF was exported and copied to the selected delivery
  directory with matching SHA-256 `4f5955bee1decc8629ba05b9450ca2521d34f6aab937c0c5c790d4dd81e66a69`.
- Ruff, Compileall, targeted Mypy, and raw-key scanning passed. Full pytest
  execution is blocked by an empty/non-worktree `.git` directory: the first
  failure is the architecture guard that invokes `git check-ignore`, after 10
  tests passed. `git diff --check` is not applicable for the same reason.

### Iteration 2026-07-22 - Hard Structured First-Turn Preflight

#### Added

- Added a mandatory first-turn preflight contract to `skill/SKILL.md` and the
  default OpenAI Skill prompt. The first response must be a fixed-choice form
  covering external visual capability, board, level, subject, year/range,
  support language, explanation style, workflow mode, batch scope, and output
  directory.
- Added the required `key=value` response shape and explicit stop conditions:
  answered values are preserved, only missing/invalid fields are asked again,
  and no source discovery, syllabus analysis, writing, visual planning,
  rendering, or PDF work can begin before the form is complete.
- Added coordinator validation for supported languages, six explanation styles,
  workflow mode, image capability state, route verification, and output
  directory. A configured `image_provider` remains separate from the user's
  external-route answer.

#### Fixed

- Closed the entry-point gap where the Agent asked the external-image question,
  then merged remaining preflight decisions into an open-ended prompt or asked
  for a style only after other work had begun.
- Added plain-language descriptions for each accepted style so the user chooses
  from the Skill's actual options rather than inventing a new label.

#### Compatibility

- Existing coordinator fields remain readable; new verification fields default
  conservatively and only block incomplete new runs. No provider, subject,
  qualification, or batch-specific rule was added.

#### Verified

- Added regressions for invalid styles, missing workflow mode, unverified named
  image routes, non-inference from `image_provider`, and the complete first-form
  coordinator prompt. Skill, JSON, and YAML validation remain passing.
- Exhaustive non-overlapping regression groups passed with a combined
  `466 passed, 165 skipped`. Ruff, Compileall, targeted Mypy, Skill validation,
  JSON/YAML parsing, and raw-key scanning passed; raw-key scanning returned
  `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Controlled PDF Lifecycle And Delivery Copy

#### Added

- Added candidate-PDF export. `export-pdf` now writes to a temporary candidate,
  runs hard technical checks, promotes only a passing file, and then writes an
  immutable record under `pdf-exports/` plus the explicit `current-pdf.json`
  pointer.
- PDF export records bind the render snapshot ID, parent HTML SHA-256, PDF
  SHA-256, byte size and page count, review-ledger index hash, product-review
  hash, and technical-validation result.
- Added `export-pdf --delivery-dir <directory>` for a hash-verified controlled
  copy, with immutable `delivery-copies/` evidence and
  `current-delivery.json`. A differing destination blocks by default;
  `--supersede-existing` explicitly archives it before replacement.
- Added deterministic `next_actions` to the read-only delivery audit. It now
  distinguishes repair/rerender, Writer repair, Visual repair, LLM review, PDF
  export, stale configured delivery copy, and complete states instead of
  treating every clean HTML audit as an instruction to export again. An
  unconfigured optional delivery copy is not a completion blocker.

#### Fixed

- Replaced destructive PDF invalidation. Rerendering or review now marks the
  former current pointer stale while preserving historical PDF bytes and
  immutable records.
- Removed remaining same-name PDF deletion from the CLI draft renderer and both
  Skill-interface render paths. Rendering HTML can no longer erase a historical
  delivery artifact merely because it shares the default stem.
- Removed the same destructive deletion from retained one-off handbook rebuild
  scripts. They may still rerender their explicitly named local handbooks, but
  now rely on snapshot invalidation and leave former PDFs available as history.
- Formal PDF lookup now uses the explicit current pointer and full hash/review
  binding. Legacy lookup still reads historical files, but those files cannot
  become formal delivery sources through modification time.
- Hard PDF delivery checks now cover unreadable/zero-page files, genuinely
  blank pages, portrait A4 geometry, and local-file header/footer leakage.
  Recommended page/size limits and lossy text-extraction notation findings are
  warnings rather than universal cross-subject blockers.
- A new render snapshot automatically makes a PDF pointer from another snapshot
  stale, closing rerender paths outside the main review command.

#### Compatibility

- Existing AQA, Edexcel, CAIE, College Board AP, HTML rendering, and legacy PDF
  discovery paths remain unchanged. Historical PDFs are retained and readable.
- No delivery directory is touched unless `--delivery-dir` is explicitly used;
  no differing destination is moved unless `--supersede-existing` is also
  explicitly supplied.
- PDF technical checks are provider-, qualification-, subject-, language-, and
  batch-size independent and do not make teaching or visual-semantic decisions.

#### Verified

- Added regressions for failed-candidate isolation, immutable current-PDF
  records, non-destructive invalidation, legacy/history lookup separation,
  controlled-copy conflicts and explicit superseding, state-specific next
  actions, automatic stale marking after rerender, and non-A4 rejection.
- Full regression coverage was executed in exhaustive non-overlapping groups:
  `463 passed, 165 skipped`. Ruff, Compileall, targeted Mypy for every changed
  source file, and raw-key scanning passed; raw-key scanning returned
  `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Cross-Subject Governance Safety Corrections

#### Added

- Topic, Visual, and holistic LLM review records now require non-empty
  `evidence_locations` pointing to the screenshot or browser viewport positions
  actually inspected. Python validates presence and binding but does not create
  or approve those decisions.
- Added explicit regression coverage proving that a configured image renderer
  never supplies the user's preflight answer. `image_provider` and confirmed
  external-image capability are separate facts.

#### Fixed

- Removed the universal one-primary-item-per-topic rule. A final teaching topic
  must map at least one independently assessable source item and may combine
  tightly linked items only with a source-based cluster reason and visible
  teaching treatment for every mapped item. This prevents both broad heading
  passthrough and artificial micro-topic fragmentation.
- Narrowed exact-SVG structural rejection so legitimate rectangular tables,
  matrices, timelines, heatmaps, histograms, and bar/data charts are not rejected
  merely because SVG element types resemble cards. Declared text/summary cards
  remain ineligible, and process/feedback visuals still require direction.
- Updated the Skill, handbook specification, architecture decision, accuracy
  policy, operations guide, release checklist, README, Reviewer prompt, default
  Skill prompt, and explanatory docs to one current review/PDF contract.

#### Compatibility

- The granularity rule remains independent of provider, qualification, subject,
  and batch size. It does not introduce subject vocabularies, topic-count
  targets, or provider-specific split templates.
- Legacy v0.6 product-review files and ad-hoc historical scripts remain readable
  evidence but cannot satisfy the v0.7 ledger-based formal delivery gate.

#### Verified

- Added regressions for justified multi-item teaching topics, rejection of a
  topic with no independent source item, review evidence locations, rectangular
  quantitative SVGs, declared text cards, and preflight non-inference.
- These checks are included in the same complete `463 passed, 165 skipped`
  regression result above. Ruff, Compileall, targeted Mypy, and raw-key scanning
  passed.

### Iteration 2026-07-22 - Shadow Delivery Audit And PDF P0 Gate

#### Added

- Added the read-only `audit-delivery --out <output-dir>` command and a shared
  delivery-gate evaluator. It reports current HTML and review hashes, refreshed
  HTML-only validation, product-review completeness, per-visual review state,
  rendered asset presence, and asset SHA-256 consistency without modifying any
  handbook artifact.
- Added stable blocker codes for missing or invalid plans and HTML, current-HTML
  review gaps, validation errors, pending or rejected visual decisions,
  unreviewed rendered assets, invalid asset paths, and missing or stale hashes.

#### Fixed

- Closed the P0 path where `export-pdf` accepted an approved
  `agent-product-review.json` even when current validation failed, a visual
  decision remained pending or rejected, a rendered SVG was unreviewed, or an
  asset hash no longer matched. PDF export now consumes the same gate result as
  the shadow audit and rechecks the current HTML hash immediately before export.
- Removed literal student-facing heading checks such as `Method` and `Check`
  from language validation. Those checks produced false delivery blockers when
  valid templates expressed the same teaching structure under different copy;
  language-mixing, guide-content, practice, visual, and package validation remain
  active.

#### Compatibility

- The audit accepts both legacy-list and schema-version 2 visual manifests.
  Legacy manifests remain readable and are reported explicitly; rendered assets
  without review/hash evidence are blocked rather than silently approved.
- No provider, qualification, subject, or batch-size condition was added. AQA,
  Edexcel, CAIE, and College Board AP use the same artifact-state gate.
- Existing handbook files are not moved, deleted, renamed, or rewritten by the
  audit. Blocked PDF export returns before changing existing PDF or JSON files.

#### Verified

- Shadow-audited the four retained handbook directories. Refreshed machine
  validation produced zero errors for AP Chemistry, CAIE AS Physics 9702,
  Edexcel A-level Mathematics 9MA0, and OxfordAQA IGCSE Biology; the only
  blockers were the 19, 18, 21, and 8 pending per-visual decisions respectively.
- Attempted `export-pdf` for all four directories. Every run returned exit code
  `2`, and all pre-existing PDF and JSON hashes remained unchanged.
- Added regression coverage for read-only auditing, CLI blocked reporting,
  validation-error blocking, pending and rejected visual decisions, unreviewed
  rendered SVGs, stale asset hashes, and a clean reviewed export.
- Full regression result: `436 passed, 165 skipped`. Ruff, Compileall, targeted
  Mypy for all changed Python files, and raw-key scanning passed; raw-key
  scanning returned `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Immutable Render Snapshot And Current Pointer

#### Added

- Added immutable render snapshots under `render-snapshots/`. Each snapshot
  binds the exact HTML bytes, the rendered `GuidePlan`, the guide plan,
  qualification, run options, syllabus evidence/outline, concept explanations,
  visual manifest, and every rendered visual asset through canonical JSON or
  byte-level SHA-256 records.
- Added Unicode-NFC, sorted-key canonical JSON hashing and atomic snapshot and
  pointer writes. The snapshot ID is derived from the payload without including
  its own ID, so the hash graph has no self-reference.
- Added `current-render.json`, a mutable pointer to one immutable snapshot, and
  made handbook HTML selection prefer that pointer over validation metadata or
  modification-time guesses.

#### Fixed

- Delivery auditing now rejects missing, invalid, stale, or hash-inconsistent
  current render snapshots, while retaining historical output files for
  inspection and migration.
- JSON formatting-only changes do not create a new semantic snapshot; changes
  to actual render inputs do. Older snapshots remain untouched when a new
  render becomes current.

#### Compatibility

- Direct rendering tests and legacy output readers continue to work without a
  pre-existing guide-plan file; such outputs can render and be inspected, but a
  formal delivery export requires a current pointer and a complete snapshot.
- Snapshot records are provider-, qualification-, subject-, and batch-size
  independent. No existing handbook directory was modified during this
  iteration.

#### Verified

- Added regressions for canonical Unicode/JSON hashing, immutable snapshot
  history, pointer precedence over newer unrelated HTML, and detection of later
  input changes.
- Full regression result: `438 passed, 165 skipped`. Ruff, Compileall, targeted
  Mypy for the snapshot, renderer, output-selection, and delivery-gate modules,
  and raw-key scanning passed; raw-key scanning returned `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Draft-Only Python Fallbacks And Stable Topic Identity

#### Added

- Added `GuidePlan.content_provenance`. Plans created by Python remain
  `python-draft`; formal delivery requires the host LLM to finish all teaching
  content and explicitly record `llm-authored` provenance.
- Added deterministic `requirement-<sha256>` topic IDs derived from normalized
  topic titles, source points, and source snippets. Concept jobs and Writer
  entries now carry that stable ID instead of process-random Python `hash()`
  values.
- Added concept-entry provenance and `delivery_eligible` fields. Python visual
  fallback decisions remain available for demo/legacy workflows but are marked
  `python-fallback` and cannot pass the delivery gate.

#### Fixed

- Removed substring-based concept-to-topic routing. LLM content now applies by
  exact stable ID, exact topic title for legacy entries, or exact normalized
  source point; near-match topic text is left unmatched for explicit repair.
- Closed two additional PDF bypasses in the concept and infographic import
  scripts. After either import changes HTML, the scripts retain any old PDF as
  historical output, clear its validation pointer, and return
  `blocked_pending_current_html_review` instead of calling the low-level PDF
  renderer.
- Updated the authoritative Skill, handbook spec, architecture decision, and
  coordinator prompt with stable IDs, LLM provenance, immutable snapshots, the
  read-only audit, and the draft-only Python boundary.

#### Compatibility

- Existing exact-title concept imports remain supported. Lightweight legacy
  test objects without qualification metadata still use exact title matching;
  they do not regain fuzzy matching.
- Python demo and legacy rendering behavior remains available, but its output
  is intentionally not formal-delivery eligible until LLM-owned artifacts
  replace every fallback and provenance is updated.
- The rules are independent of provider, qualification, subject, language, and
  batch size.

#### Verified

- Added regressions for deterministic IDs, Unicode-stable identity input,
  rejection of substring matches, fallback provenance blocking, and the absence
  of low-level PDF export calls from both import scripts.
- Full regression result: `441 passed, 165 skipped`. Ruff, Compileall, targeted
  Mypy for all changed runtime/scripts, and raw-key scanning passed; raw-key
  scanning returned `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Generic Visual Semantics And Exact-SVG Rejection

#### Added

- Added the provider- and subject-independent
  `v1-visual-semantic-contract`. Every non-text visual declares its learning
  claim, intended inference, visual kind, required elements, relationships and
  labels, and forbidden misconceptions.
- Carried Writer-authored semantic contracts through `VisualBrief`,
  `VisualSpec`, spec hashing, and visual-manifest rendering without Python
  inventing domain content.
- Added exact-SVG structural diagnostics for text-card layouts and missing
  directional connectors in process/feedback visuals.

#### Fixed

- Exact-SVG files made only from text and decorative rectangles can no longer
  satisfy the delivery gate as explanatory visuals.
- Legitimate table, matrix, and comparison-table SVGs remain supported when
  their semantic contract declares the relationship they encode.
- Tightened the existing visual-manifest JSON typing without changing its
  runtime compatibility behavior, eliminating its previously reported Mypy
  errors in the touched path.

#### Compatibility

- Existing manifests remain readable, but missing semantic contracts are an
  explicit formal-delivery blocker rather than being silently inferred.
- The gate validates visual grammar and contract completeness only. The LLM
  Reviewer remains responsible for factual meaning and teaching value.

#### Verified

- Added regressions for decorative SVG rejection, table/matrix allowance,
  directional process connectors, missing semantic-contract fields, and
  manifest propagation.
- Full regression result: `445 passed, 165 skipped`. Ruff, Compileall, targeted
  Mypy for every changed visual/runtime module, and raw-key scanning passed;
  raw-key scanning returned `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Chunked Review Ledger And Holistic HTML Approval

#### Added

- Added LLM-authored Topic and Visual review shards under `review-ledger/`,
  capped at 25 items per shard and bound to the current render snapshot and HTML
  SHA-256.
- Added a separate `review-ledger/holistic.json` contract for direct inspection
  of the complete assembled HTML, including cover/navigation, cross-page
  consistency, responsive layout, notation, encoding, findings, and repair
  iteration.
- Added `index-review-ledger --out <output-dir>`. Python hashes existing
  LLM-authored shards and writes `review-ledger/index.json`; it does not create
  review items or approval decisions.
- Added the compact `v0.7-llm-html-review-ledger` product-review schema, which
  references the current snapshot, HTML, and ledger-index hashes instead of
  duplicating full Topic and Visual lists in one large JSON file.

#### Fixed

- Formal delivery now rejects sampled or incomplete review coverage, duplicate
  or unknown Topic/Visual IDs, stale shard hashes, mismatched visual asset
  hashes, unapproved per-item decisions, oversized shards, and missing or
  failed holistic HTML review.
- The generated Reviewer prompt no longer pre-populates all approval booleans
  as `true`. It supplies placeholders and instructs the LLM to set each field
  only after the exact check is completed.
- Legacy v0.6 product-review records remain readable but cannot satisfy the new
  formal ledger gate by themselves.

#### Compatibility

- Handbooks with zero rendered visuals use no Visual shard and remain valid
  when Topic coverage and holistic review are complete.
- Every handbook has an independent ledger and snapshot binding; batch outputs
  cannot reuse another handbook's review conclusion.
- Review rules remain independent of provider, qualification, subject, and
  batch size.

#### Verified

- Added regressions for complete clean export, missing Topic coverage, stale
  shard hashes, unapproved Visual review, the 25-item shard cap, compact product
  review binding, holistic review, and CLI index generation.
- Full regression result: `450 passed, 165 skipped`. Ruff, Compileall, targeted
  Mypy for all changed review/gate modules, and raw-key scanning passed; raw-key
  scanning returned `raw_key_matches: 0`.
- This workspace has no Git worktree, so `git diff --check` was not applicable.

### Iteration 2026-07-22 - Four Handbook Full Review And Delivery Refresh

#### Fixed

- Completed the repair, current-HTML rerender, and full visible-review loop for
  OxfordAQA International GCSE Biology 9201, Cambridge International AS Level
  Physics 9702, AP Chemistry, and Pearson Edexcel A-level Mathematics 9MA0.
- Replaced generic or cross-topic student-facing teaching remnants, repeated
  solution layers, stale mathematics practice content, and repeated generic
  visual prompts. The current topic records and rendered pages now carry
  topic-specific mastery statements, worked content, and visual decisions.
- Refreshed the four root-level delivery PDFs so they exactly match the
  approved subject-folder exports, rather than retaining earlier PDF copies.
- Updated `C:\\Users\\Ethan\\Desktop\\Handbook\\delivery-record.json` to bind
  the delivery list to the current approved HTML hashes, root PDF hashes, file
  sizes, and final page counts.

#### Verified

- The LLM review record for every handbook uses
  `v0.6-llm-html-review`, approves the exact current HTML hash, lists every
  final topic and every rendered visual, and has no unresolved fixable issue.
- Reviewed the current rendered HTML at topic level: 31 Biology topics and 8
  visuals; 32 Physics topics and 18 visuals; 91 Chemistry topics and 19
  visuals; 89 Mathematics topics and 21 visuals.
- Rendered and checked all 204 final PDF pages. The four root delivery PDFs
  have 28, 36, 72, and 68 pages respectively, with no blank-page or zero-byte
  render finding.
- Full regression result: `427 passed, 165 skipped`. Ruff, Compileall, and
  raw-key scanning passed; raw-key scanning returned `raw_key_matches: 0`.
- Delivery-record verification passed for all four HTML approval hashes and
  all four root PDF hashes/page counts.
- Targeted Mypy on `src/intl_exam_guide/auditing/quality_inspector.py` still
  reports 18 existing broad-JSON type errors. No Python source was changed in
  this delivery-refresh closeout. This workspace has no Git worktree, so
  `git diff --check` was not applicable.

### Iteration 2026-07-22 - Knowledge And Governance Closeout

#### Fixed

- Replaced the stale root `SKILL.md`, which required a second PDF-review handoff
  and linked to three missing reference files, with a discovery wrapper that
  points to the authoritative `skill/SKILL.md` and repeats only the supported
  automatic-acquisition boundary.
- Reconciled the English and Chinese READMEs, Skill explanation, accuracy
  policy, project operations guide, image-model guide, examples, release
  checklist, release-evidence guide, project details, and public homepage with
  the current workflow: blocking image-capability preflight, LLM-owned atomic
  syllabus analysis, per-topic visual decisions, complete visible HTML review,
  repair and rerender loops, and hash-gated PDF export.
- Removed the broken `docs/QUALITY_METRICS.md` link and stopped presenting
  Python quality scores or review packets as student-ready approval.
- Updated the OpenAI Skill metadata to include College Board AP and to require
  the visual-capability question before any other run action or local-generation
  assumption.

#### Added

- Added a trackable `AGENTS.md` as a concise maintenance entry for
  source-of-truth files, change boundaries, changelog discipline, validation
  commands, publication authorization, and non-destructive workspace handling;
  removed its stale `.gitignore` exclusion so it will survive the next GitHub
  import.
- Added ignore coverage for retained local review approvals, visual prompts,
  visual-review captures, MP4 exports, and the zero-byte `NUL` residue so a
  future Git import does not accidentally publish them. No retained artifact
  was deleted.
- Synchronized public entry titles to name the supported College Board AP
  curriculum alongside IGCSE and A-Level.
- Marked `docs/DELIVERY_QUALITY_REBUILD_PLAN.md` as historical planning. Its
  sampling matrix is release-portfolio evidence and cannot replace full review
  of each handbook.

#### Compatibility

- No Python runtime, schema, provider, or rendering behavior changed in this
  closeout. The package remains `v0.5.1`; publication and versioning are pending
  a separate release request.
- The canonical install target remains `skill/`; the root `SKILL.md` is a
  repository discovery wrapper, not a second contract.

#### Verified

- Full regression result: `426 passed, 165 skipped`.
- Ruff and Compileall passed.
- Targeted Mypy passed for the current HTML/PDF gate, coordinator prompt, and
  release verifier modules.
- Raw-key scanning returned `raw_key_matches: 0`.
- Markdown local-link validation, stale-contract scanning, Skill/OpenAI YAML
  parsing, and public-homepage HTML parsing passed.
- Full-project Mypy still reports 38 pre-existing errors in
  `visuals/manifest.py` and `auditing/quality_inspector.py`; those modules were
  not changed by this documentation/governance iteration.

### Iteration 2026-07-21 - Complete Subject And Visual Semantic Review

#### Fixed

- Closed the final-review loophole where an LLM could approve a handbook after
  checking only file presence, layout, or a sample of pages and visuals.
- Final approval now requires the LLM to review every final topic for subject
  facts, definitions, relationships, teaching claims, worked questions,
  solution steps, final answers, units, and source anchors.
- Final approval now requires the LLM to review every visual that actually
  renders in HTML for semantic accuracy, including labels, arrows, positions,
  structures, relationships, scales, units, captions, and correspondence with
  the associated topic. Loading successfully or looking polished is not enough.

#### Added

- Added exact review-coverage fields to `v0.6-llm-html-review`:
  `reviewed_topic_titles`, `topic_review_count`, `reviewed_visual_ids`,
  `rendered_visual_review_count`, and explicit subject-fact, worked-answer,
  visual-semantic, and layout confirmations.
- The PDF export gate now compares the recorded topic titles and rendered
  visual IDs with the current handbook artifacts. Missing, duplicate, or unknown
  entries invalidate approval and block export.
- The LLM review prompt now enumerates every required Topic and rendered visual
  ID and explicitly prohibits sampled final approval.

#### Compatibility

- This is a general per-handbook review rule. It does not encode any particular
  subject, exam board, output batch, or number of handbooks.
- Handbooks with zero rendered visuals remain valid when every topic is reviewed
  and the recorded rendered-visual count and ID list are both empty.

#### Verified

- Added regressions proving that omitting one required Topic or one rendered
  visual invalidates the LLM review and blocks PDF export.
- Full regression result: `426 passed, 165 skipped`.
- Full Ruff, Compileall, targeted Mypy, and raw-key checks passed.

### Iteration 2026-07-21 - Skill Boundary Compliance And Per-Topic Visual Decisions

#### Fixed

- Added a mandatory Boundary Compliance Gate at the beginning of the Skill and
  coordinator prompt. Agents must follow artifact contracts and workflow order
  exactly, may not invent speed shortcuts, and must stop/report when a boundary
  cannot be satisfied.
- Strengthened the Analyst contract against promoting directory-level syllabus
  headings into final topics or compressing a full course into a few broad
  themes. Non-flat structure models now require declared official containers,
  and the prompt includes an explicit pre-delivery depth check.
- Prevented visual workflow drift in the Writer instructions: visual decisions
  are independent for every final topic, with no one-image-per-subject quota,
  no minimum image count, and no generic subject poster or reused visual plan.

#### Changed

- Clarified that visual assets may contain accurate, legible, source-bound text
  such as labels, callouts, legends, axes, captions, and short example
  annotations. The Skill does not require text-free images.
- Clarified that `external-infographic` may be used for a topic-specific
  explanatory visual, realistic/reference/example image, apparatus, scene,
  material appearance, process detail, or rich annotation; it is not limited to
  formal diagrams.
- Updated Writer, concept-job, coordinator, Skill, specification, image-guide,
  and multi-agent instructions with the same per-topic visual boundary.

#### Verified

- Added regression assertions for the boundary-compliance prompt, no subject
  visual quota, text-bearing visuals, generic-poster rejection, and non-flat
  outlines without official container declarations.
- Full regression result after this iteration: `424 passed, 165 skipped`.
- Full Ruff, Compileall, targeted Mypy, and raw-key checks remained green.

### Iteration 2026-07-20 - LLM HTML Review Before PDF Export

#### Changed

- Replaced the previous render-and-review order with a mandatory two-stage
  delivery workflow. All handbook generation paths now stop at HTML; PDF is no
  longer created during Writer rendering or by the `review` command.
- The active LLM Reviewer must personally open and visually inspect the current
  HTML. Python validation, quality inspection, parsed text, and review packets
  are supporting diagnostics only and cannot provide approval.
- Any content, source, teaching, worked-example, visual, layout, overflow,
  notation, or language issue must return to the Writer. After repair, HTML must
  be rerendered and visibly reviewed by the LLM again until no fixable issue
  remains.
- Added the `v0.6-llm-html-review` product-review contract. Approval records
  `reviewer_type: "llm"`, the exact inspected HTML SHA-256, review iteration,
  issue/repair history, `html_review_passed: true`, an empty unresolved-issue
  list, and `decision: "approved"`.

#### Added

- Added `python -m intl_exam_guide export-pdf --out <output-dir>` as the only
  production workflow entry that exports a handbook PDF after review.
- Added a hard export gate that rejects missing review evidence, non-LLM
  approval, revisions-required decisions, unresolved fixable issues, malformed
  review records, and HTML hashes that no longer match the reviewed file.
- HTML rerendering now removes or invalidates an earlier PDF. Any HTML change
  makes the old review evidence stale and requires another visible LLM review
  before PDF can be exported again.
- Updated release-sample verification to require LLM HTML approval and confirm
  that the recorded review hash matches the released HTML.

#### Compatibility

- Existing `v0.5-visible-handbook-review` artifacts cannot authorize new PDF
  exports because they were not bound to the current HTML and required PDF
  sampling before approval. They must be replaced by a fresh visible LLM review
  using `v0.6-llm-html-review`.
- Existing generator method signatures retain `skip_pdf` for host compatibility,
  but handbook rendering now always stops at HTML. Hosts must use the new gated
  `export-pdf` step after LLM approval.
- Python quality-inspection files remain available as optional diagnostics, but
  their presence, absence, pass, or failure cannot substitute for the LLM's
  visible HTML decision.

#### Verified

- Added regressions proving that `review` never exports PDF, unreviewed HTML is
  rejected, stale review hashes are rejected, and a matching current-HTML LLM
  approval permits PDF export.
- Added prompt assertions requiring the LLM to view HTML, prohibiting PDF during
  review, and binding the approval template to the current HTML SHA-256.
- Full regression result: `423 passed, 165 skipped`.
- Full Ruff and Compileall checks passed. Mypy passed for all seven changed
  Python workflow/review modules, and the raw-key scan returned zero matches.

### Iteration 2026-07-20 - Source-Relative Syllabus Granularity Contract

#### Fixed

- Closed the outline-validation loophole where an Analyst could define one
  broad official Topic, Unit, Section, chapter, or table heading as a single
  `source_coverage` item and then pass all later self-consistency checks.
- Added a mandatory `coverage_granularity` contract. Every lowest official
  container must now be classified as one independently assessable requirement,
  several requirements, or no examinable content, with page evidence and a
  source-based rationale when no deeper split exists.
- Every `source_coverage` item must now carry a stable source kind, an
  independently assessable demand, `atomicity: "atomic"`, source content, and a
  valid page reference. Structural headings are rejected as coverage unless a
  single-point container audit supports them.
- Added split-first topic validation: every final teaching topic must have
  exactly one primary `independent_topic` source item. Topics that also map
  prerequisites or sub-skills require a valid `cluster_justification` explaining
  the relationship and why separate teaching topics would be misleading.

#### Compatibility

- The contract is provider-, qualification-, and subject-independent. It does
  not encode CAIE-specific behavior, a fixed hierarchy, a command-verb list, or
  a fixed number of points per Topic.
- Source requirements may be knowledge statements, conceptual relationships,
  calculations, practical work, source/data analysis, extended responses,
  language performance, portfolio evidence, or other source-bound demands.
- Genuine one-requirement official Topics remain valid when the Analyst cites
  evidence and explains why the requirement cannot be split further.
- Existing AQA, Edexcel, CAIE, and College Board AP Provider discovery and
  acquisition logic is unchanged; the stricter contract applies after evidence
  extraction to all supported routes.

#### Changed

- Updated the Skill and handbook specification so Analyst instructions,
  mechanical validation, and Reviewer checks enforce the same source-relative
  granularity model.
- Reviewer packets now explicitly check container-detail audits, primary source
  items, and source-justified prerequisite/sub-skill clustering before handoff.

#### Verified

- Added regression coverage for a multi-requirement container incorrectly
  mapped to one item, a correctly split multi-requirement container, a genuine
  single-requirement container, an invalid two-primary-item merge, and a valid
  primary-plus-sub-skill cluster.
- Full regression result: `418 passed, 165 skipped`.
- Full Ruff and Compileall checks passed. Mypy passed for both changed source
  modules: syllabus-outline planning and final review.

### Iteration 2026-07-20 - College Board AP Provider And Cover

#### Added

- Registered `collegeboard` as the fourth production source provider, with
  aliases for `ap` and `advanced-placement` and automatic inference from exact
  AP course names and official College Board URLs.
- Added full discovery for the official 42-subject AP directory, exact and
  ambiguity-safe subject selection, strict core Course and Exam Description
  matching, official-domain enforcement, shared-CED support, and supplemental
  clarification/correction exclusion.
- Added the `advanced_placement` qualification type, `--level ap`, CED effective
  Fall version extraction, target AP exam-year applicability checks, AP output
  naming, AP-specific revision language, and a College Board provider reference.
- Added an independent full-A4 AP `Textbook Grid` cover template using College
  Board blue, bright yellow, and pale aqua. It displays the AP course identity,
  verified CED version, and target exam year without inventing a course code.

#### Fixed

- Fixed official PDFs that are marked encrypted but are readable with an empty
  password. The extractor now checks the `pypdf` decrypt result instead of
  incorrectly treating the persistent `is_encrypted` metadata flag as a locked
  document; genuinely password-locked PDFs remain blocked.

#### Compatibility

- OxfordAQA, Pearson Edexcel, and Cambridge remain on their existing Provider
  paths and cover palettes. AP is added as an independent provider and template.
- AP source acquisition is supported, while subject handbook delivery remains
  `candidate` until the normal Analyst, Writer, visual, PDF, and final-review
  evidence chain is complete.
- Clarified the automatic-acquisition boundary: supported routes are
  AQA/Edexcel/CAIE IGCSE and A-Level plus College Board AP. Other curriculum
  systems or exam boards cannot use automatic acquisition; manual syllabus
  imports are unverified and may fail with unknown compatibility errors.

#### Verified

- Live provider discovery returned all 42 official AP subjects. An
  `extract-evidence` run for AP Cybersecurity 2027 selected the official core
  CED, recorded `CED effective Fall 2026`, produced 187 non-empty page-evidence
  records, generated a successful 274,382-character Markdown companion, and
  stored the official PDF SHA-256 hash.
- Rendered and visually inspected the independent AP cover as a one-page A4 PDF
  (`594.96 x 841.92pt`) and full-page PNG. The long `Cybersecurity` title, CED
  version, target year, and footer cards remained visible without overlap.
- Full regression result: `411 passed, 165 skipped`. Full Ruff, Compileall, and
  raw-key scanning passed; Mypy passed for all 15 source files touched by this
  iteration.
- Browser-checked the updated project homepage at `1440 x 900` and `390 x 844`.
  The four-source heading and scope table fit without horizontal overflow.

### Iteration 2026-07-20 - College Board AP CED Feasibility Audit

#### Added

- Added a reproducible, low-frequency College Board AP audit utility that
  enumerates the official course directory, excludes overview pages, extracts
  numbered course-page units, selects explicit Course and Exam Description
  cards, and verifies official PDF responses and file signatures.
- Added an isolated `audit` dependency extra for the research utility and a
  permanent AP provider feasibility report with production acceptance rules.

#### Verified

- The official directory declared and exposed 42 AP subjects. All 42 subject
  pages returned successfully and yielded a verified core CED, resolving to 39
  unique official College Board PDFs.
- Confirmed two shared-document groups: Calculus AB/BC share one CED, while
  2-D Art and Design, 3-D Art and Design, and Drawing share another.
- Confirmed that clarification/correction PDFs on Computer Science A and Latin
  are supplemental documents and do not make the core CED ambiguous.
- Downloaded and parsed six representative CEDs to confirm course identity,
  course framework, effective version, and exam or portfolio structure. The
  sample included the new AP Cybersecurity and AP Business with Personal
  Finance CEDs effective Fall 2026.
- The audit utility compiled and passed Ruff. Its JSON assertions confirmed 42
  courses, zero non-official or invalid PDF selections, and 39 unique CEDs.
- Full project regression remained green: `399 passed, 165 skipped`.

#### Compatibility

- This iteration establishes feasibility only. AP is not yet registered as a
  production provider, and the existing OxfordAQA, Pearson Edexcel, and
  Cambridge provider behavior is unchanged.

### Iteration 2026-07-20 - Textbook Grid Cover Selection

#### Changed

- Explored four A4 cover directions with the installed design Skills and selected
  the `Textbook Grid` direction for the production templates.
- Updated the shared cover geometry so the exam-board identity and revision-guide
  bands span the page width, the subject title and course code form the primary
  reading path, and the syllabus metadata and learning signals remain anchored
  at the bottom of the A4 page.
- Replaced the generic board-handbook label with a qualification- and
  subject-derived study title such as `AS Mathematics study guide` or
  `IGCSE Economics study guide`.
- Fixed distinct production palettes for all supported boards: OxfordAQA uses
  deep blue, red, and gold; Pearson Edexcel uses deep teal, blue, and pale aqua;
  Cambridge International uses deep burgundy, navy, red, and gold.

#### Verified

- Rendered the AQA, Edexcel, and CAIE production templates as three independent
  one-page A4 PDFs and inspected the corresponding full-page PNGs. All three
  retained the shared layout while preserving distinct board colors, readable
  study-title wrapping, and syllabus-derived metadata.

### Iteration 2026-07-20 - Board Covers And Visual Preflight

#### Changed

- Standardized OxfordAQA, Pearson Edexcel, and Cambridge International covers
  on one fixed information hierarchy and geometry. Each board keeps its own
  identity and palette, while subject, course code, qualification family,
  specification or syllabus version, and exam year continue to come from the
  selected qualification and official syllabus metadata.
- Preserved the existing OxfordAQA cover structure while replacing the former
  Edexcel- and CAIE-specific header/body arrangements with the shared cover
  mast, main panel, and footer contract.
- Added a mandatory first-exchange visual-capability gate to the published
  Skill, agent default prompt, image-model guide, and optional coordinator.
  The host must ask whether the user can provide or enable an external
  image-generation Skill or tool and wait for an explicit answer instead of
  inferring a route or defaulting the entire handbook to local generation.
- Defined route-aware behavior after that answer: verified external routes are
  reserved for source-bound external infographic jobs; runs without an external
  route may use text, reviewed exact SVG, or Kroki only when the topic justifies
  them, while complex infographic jobs remain pending.

#### Fixed

- Fixed PDF covers rendering as a partial page. The print cover previously used
  a `220mm` minimum height even though an A4 page with `3.5mm` top and bottom
  margins has a `290mm` content area. Print covers now use the full `290mm`
  height and are protected from internal page breaks.

#### Verified

- Added regression coverage for the shared three-board cover structure, fixed
  board palettes, syllabus-derived cover fields, mandatory external-image
  capability question, and coordinator preflight blocking behavior.
- Rendered OxfordAQA, Edexcel, and CAIE covers through Chromium and exported
  each as a one-page A4 PDF (`594.96 x 841.92pt`). Each cover occupied the full
  printable page without clipping, overlap, or bottom-page whitespace.
- Exported a five-page handbook through the project's normal PDF path and
  raster-inspected page 1 to confirm that the cover fills the complete A4 page.
- Full regression result after the iteration: `399 passed, 165 skipped`.
  Focused cover/PDF regression result: `49 passed, 1 skipped`. Ruff and Mypy
  passed for every source and test file changed by this iteration, and the
  packaged Skill plus `skill/test-prompts.json` passed format validation.

#### Release Notes

- This is an unreleased iteration record, not a new certification of every
  subject or visual route. The CLI framework demo remains intentionally blocked
  from final-ready status until LLM-authored syllabus, concept, visual, and
  review artifacts are supplied.

## 0.5.1 - 2026-07-06

### Changed

- Made official PDF evidence dual-track: provider downloads now create page-level
  `syllabus-evidence.json`, mandatory `source/specification.md`, and
  `source/markdown-extraction.json` via an external MarkItDown CLI or isolated
  `.venv-markitdown`, without adding MarkItDown to main package dependencies.
- Updated the Analyst contract so `syllabus-outline.json` must record
  `source_inputs` and `cross_check`, and the LLM Analyst must read Markdown plus
  page-level evidence while Python still never splits topics from Markdown.
- Added final-readiness gates for missing/failed Markdown extraction and stronger
  source-evidence mapping checks.
- Added a notation contract and mechanical lint for student-facing ASCII maths
  residue in guide plans, rendered HTML, and extracted PDF text.
- Expanded Reviewer duties to include notation spot-checks and cross-page visual
  repetition checks for repeated SVG/raster/layout patterns.

## 0.5 - 2026-07-06

### Changed

- Reframed Analyst, Writer, and Reviewer as lightweight operating roles rather
  than mandatory multi-agent orchestration. Explicit multi-agent delegation is
  optional; the Skill no longer requires a project-manager role,
  release-certification role, or `agent-orchestration.json` deliverable.
- Introduced the v0.5 visual-decision contract. Every topic in
  `concepts/concept_explanations.json` must carry a Writer-owned
  `visual_decision`; `text-ok` is valid only with a clear `no_visual_reason`,
  and visual routes are limited to `text-ok`, `exact-svg`, `kroki-diagram`, and
  `external-infographic`.
- Split visual intent from rendered output in the visual manifest: Writer route
  recommendations, learning-value claims, workflow state, and actual rendered
  assets are recorded separately so pending or unreviewed visuals cannot be
  mistaken for finished handbook images.
- Kept the Python boundary mechanical: Python downloads official PDFs, extracts
  text, receives LLM JSON, validates contracts, renders HTML/PDF, imports
  reviewed assets, and packages evidence; the host LLM owns syllabus judgment,
  teaching explanations, practice wording, visual need, and final review.

### Fixed

- Replaced the legacy concept-writing script with an explicit refusal so Python
  cannot silently generate teaching content from concept jobs.
- Removed subject-specific runtime template residue from the handbook-writing
  path and updated tests/docs toward source-bound, all-subject visual judgment.
- Added OxfordAQA direct-PDF/code handling and tightened provider blending so a
  qualification code must be an exact single four-digit code.

### Review Notes

- This is a framework release, not a blanket certification of every exam board,
  subject, level, or visual route. Release evidence remains conservative and
  must be read from the delivery matrix and release-evidence manifests.

## 0.4.4 - 2026-07-05

### Changed

- Reframed the Skill as a Python execution framework plus LLM-operated handbook
  workflow. Python now handles mechanical tasks such as official PDF download,
  page-text extraction, JSON receipt/validation, HTML rendering, PDF export, and
  packaging; the host LLM/Agent owns syllabus boundaries, exam-point selection,
  concept explanations, worked-example judgment, visual needs, and final review.
- Added the `syllabus-outline`, `visual_spec`, and reviewed concept-explanation
  handoff path so the LLM's source-bound decisions can populate the guide plan
  without Python inventing content.
- Tightened the visual contract around exact SVG. SVG can enter a deliverable
  only when the LLM marks `svg_fit: "exact"` and the asset is reviewed or
  approved; non-exact SVG, unreviewed SVG, and legacy `deterministic-svg`
  provider output are blocked from final delivery.

### Fixed

- Removed local deterministic/scientific-vector SVG generation from the
  deliverable path. Complex visual needs now remain external infographic jobs
  until a callable route or reviewed imported raster asset is available.
- Updated validation, quality inspection, manifest v2, rendering, import, and
  visual-routing tests so stale SVG fallback assets and unresolved visual jobs
  fail loudly instead of being presented as finished teaching diagrams.

### Review Notes

- This is a framework release. It is classified as `candidate` release evidence,
  not a new final-ready sample certification.

## 0.4.3 - 2026-07-03

### Fixed

- Repaired AQA AS Mathematics generation issues found during visible handbook
  review: repeated mastery explanations, generic exam-logic phrasing, weak
  topic routing for trigonometry, differentiation, circle geometry, kinematics,
  and fixed-plane impact, and repeated adjacent SVG visuals.
- Added focused regression coverage for mathematics concept-writing routes,
  practice generation, source-point selection, SVG routing, rendering contracts,
  and validation checks so the same AQA AS Mathematics failures are easier to
  catch before handoff.
- Re-rendered and reviewed the local AQA AS Mathematics sample after repairs:
  99 topic guides, 99 practice items, 24 visual assets, 46 professional glossary
  terms, 117 PDF pages, zero blank text pages, zero duplicate visual hashes, and
  `agent-product-review.json` marked `final-ready`.

### Review Notes

- This is a corrective release, not a certification of all exam boards and
  subjects.

## 0.4.2 - 2026-07-02

### Changed

- Added machine-readable multi-agent dispatch briefs to
  `agent-orchestration.json` so Skill-compatible Agents can separate syllabus
  analysis, handbook writing, and independent final review instead of allowing
  the writer to self-approve.
- Added `agent-product-review.json` as required final handoff evidence. A clean
  validation run and `final-review-packet.json` are no longer enough to mark an
  output final-ready; the active Agent/LLM must record visible-handbook review,
  syllabus-outline comparison, sampled PDF/visual/glossary checks, repair-loop
  status, unresolved fixable issues, and the final decision.
- Updated release evidence vocabulary so prior v0.4.1 validation-clean samples
  are treated as draft/review-ready until product-review evidence exists.

### Fixed

- Removed internal visual provider/review-status labels from student-facing
  generated and local visual blocks, and added validation coverage so those
  implementation labels cannot appear in final HTML/PDF output.

## 0.4.1 - 2026-07-02

### Fixed

- Locked term-support languages to the product rule: the handbook body, worked
  examples, labels, and visual prompts stay English; `zh-CN`, `zh-TW`, `ja`,
  and other reviewed support languages add only a 30-50 item professional
  glossary.
- Fixed cross-subject template leakage found in real samples so Business,
  Economics, Physics, Accounting, and History routes no longer borrow
  mathematics, momentum, ledger, or stakeholder examples from the wrong subject.
- Filtered Cambridge and Pearson boilerplate, footer text, feedback markers,
  and malformed formula extraction before those source points can reach
  roadmap mastery cells, explanations, practice, or visual prompts.
- Tightened visual routing so local SVG is used only for simple deterministic
  diagrams, Kroki professional diagrams are written and rendered from the visual
  manifest, and dense educational infographics remain pending until reviewed
  external image assets are imported.
- Fixed PDF export quality by disabling browser header/footer output and
  trimming trailing blank pages produced by the renderer.

### Verified

- Fresh validation-clean samples were generated and reviewed for AQA AS Mathematics,
  Cambridge IGCSE Economics 0455, OxfordAQA IGCSE Business, Pearson IGCSE
  Accounting, Pearson IGCSE Physics 2017, and Cambridge IGCSE History 0470.
  Each has zero validation errors, zero pending concept explanations, zero
  blank PDF text pages, and no local-file footer leakage. Under the v0.4.2
  handoff rule, these samples are review-ready/draft until
  `agent-product-review.json` evidence is recorded.

## 0.4 - 2026-07-02

### Changed

- Added the v0.4 core delivery pipeline contracts:
  `CourseSpec`, `LearningUnit`, `PedagogicalUnit`, `VisualSpec`,
  manifest v2, and `DeliveryState`, while preserving v0.3 CLI usage.
- Moved student-facing source-point selection behind a shared filter so
  syllabus shell text such as `Candidates should have an understanding of`,
  `Students will`, and split Pearson bullets like
  `a) Understand the significance of the following accounting` do not become
  the visible "what to master", practice focus, or image prompt.
- Added subject-aware practice generation for Business and History so these
  courses no longer fall through to generic or mathematics examples.
- Locked non-English user choices to term-support mode: the handbook body,
  examples, visual prompts, and cover stay in English, while `zh-CN`,
  `zh-TW`, `ja`, and other supported choices add only a 30-50 item
  professional glossary.
- Tightened Accounting visual routing so source-record lists, trial balance,
  control accounts, bank reconciliation, error correction, incomplete records,
  statements, and ratios do not collapse into one repeated SVG template.
- Added automatic Kroki routing for professional diagram briefs between local
  deterministic SVG and external image-generation queues.

### Fixed

- Fixed Pearson History option codes such as `A1` being mistaken for
  mathematics/algebra units.
- Fixed Cambridge Accounting content extraction so `Candidates should have an
  understanding of:` is filtered at the parser/source-point layer.
- Fixed Pearson History breadth/depth-study shell points so visual briefs and
  practice prompts fall back to the actual option title when no deeper point is
  present.
- Added English visible-text validation for syllabus-shell phrases in topic
  guides, practice cards, and visual briefs.
- Added plan-level validation that rejects non-English body text in topic
  guides, practice cards, and visual briefs when a term-support language is
  selected.
- Fixed OxfordAQA AS Mathematics SVG selection for motion graphs, connected
  particles, conservation of momentum, and fixed-plane impact so adjacent
  mechanics topics no longer reuse the same SVG layout.

### Documentation

- Added the v0.4 release-evidence status vocabulary:
  `candidate`, `draft`, `final-ready`, and `certified`.
- Clarified that candidate routes are not delivery-grade and must not be
  described as release-ready without fresh validation, final-review, concept,
  visual, package, and PDF/export evidence.
- Added lightweight `docs/release-evidence/` manifest guidance so release
  evidence records commands, git revision, validation summary, final-review
  status, visual/concept state, and reviewer approval when certified.
- Kept the v0.3 ready/draft evidence as historical facts only; this changelog
  entry does not certify any new route or generated output.
- Added a real-sample v0.4 audit covering OxfordAQA Business, OxfordAQA
  Accounting, Pearson Accounting, Pearson History, Cambridge History, and
  Cambridge Accounting. All six samples are `draft`, not final-ready, because
  concept explanations and some accounting infographic assets remain pending.

## 0.3 - 2026-06-30

### Changed

- Reset the delivery-quality contract around source-grounded handbook output:
  topic guides now require reviewed concept explanations before a guide can be
  presented as final, and `python -m intl_exam_guide review --out <output-dir>`
  writes a final review packet with machine validation, visual status, and
  agent self-review status.
- Reworked the study roadmap so each row shows one independent, topic-specific
  mastery target. Repeated roadmap titles or repeated "what to master" cells are
  now delivery errors instead of issues left for the user to spot manually.
- Tightened visual routing across subjects: simple SVG is reserved for
  SVG-safe diagrams, complex infographic briefs stay in the image job queue
  until reviewed raster assets are imported, and generated-image prompts are
  content-only rather than branded/course-packaged.
- Improved OxfordAQA AS Mathematics extraction and AS-only filtering so
  AS-focused guides exclude A-level-only units while still preserving source
  traceability for every teachable topic.
- Updated the Skill and release workflow so final presentation depends on
  concept review, image review, PDF inspection, output package manifests, and a
  fresh final-review packet rather than broad validation alone.

### Fixed

- Blocked repeated checklist/mastery text in topic guides and repeated roadmap
  cells in rendered HTML.
- Added PDF quality checks for excessive page counts, file size, and blank text
  pages so oversized or mostly blank outputs cannot pass as final.
- Added SVG repetition checks for repeated titles and repeated SVG structures.
- Added validation for encoding artifacts, mixed-language labels, stale visual
  prompt packaging, fragment-like syllabus titles, cross-subject borrowed
  examples, and AS-only/A-level scope leakage.

### Verified

- Fresh AQA AS Mathematics Chinese/friendly handbook package was regenerated
  with reviewed GPT Image 2 1k infographic assets at
  `outputs/aqa-as-mathematics-9660-zh-CN-friendly-20260630-full-gpt-image2-1k`.
  Final review reported `delivery_status: ready`, 99 handbook topics, 99
  reviewed concept explanations, 99 practice cards, 26 visual examples, 21
  generated raster infographics, 5 SVG assets, 0 pending concept explanations,
  0 pending infographic assets, 105 PDF pages, and 0 blank text pages. The
  rendered study roadmap had 99 rows, 0 duplicate titles, and 0 duplicate
  mastery cells. The generated output directory is ignored and is not committed.
- `python -m intl_exam_guide review --out outputs/aqa-as-mathematics-9660-zh-CN-friendly-20260630-full-gpt-image2-1k`
  wrote `final-review-packet.json` with `error_count: 0`,
  `warning_count: 0`, and `delivery_status: ready`.
- Fresh offline demo smoke:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v03-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  The package generated HTML, 3 topics, 3 practice cards, 3 concept jobs, 3 SVG
  visuals, 7 section files, and 3 image files. Review correctly reported
  `delivery_status: draft_needs_concept_review`, `warning_count: 1`, and
  `agent_self_review.must_not_present_as_final: true` because the synthetic demo
  intentionally had 3 pending concept explanations. The ignored demo output was
  removed after collecting evidence and is not committed.
- `python -m pytest -q` (`326 passed`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `git diff --check` (Windows line-ending notices only, no whitespace errors).

## 0.2.27 - 2026-06-21

### Tests

- Closed the final-round P3 follow-up by adding dedicated
  `visual_routing.py` tests for visual brief creation, provider selection,
  subject-specific infographic branches, SVG routes, and text-only fallbacks.
- Expanded `validation/checks.py` tests for aggregate validation,
  custom-provider success, Chinese placeholder branches, image manifest edges,
  review-summary asset counts, all localized topic marker groups, and isolated
  contents/index snippet branches.
- Completed `subject_profiles.py` dedicated coverage for Economics and
  Accounting source-text routing, and pinned standalone `zh_visual_type()`
  aliases for `accounting process` and `neutralisation`.

### Fixed

- Route ambiguous Accounting source text before broader Economics matching so
  `bank reconciliation` and related accounting phrases do not get claimed by
  generic Economics terms such as `bank`.
- Match localized topic marker keywords with token-aware logic so `statement`
  and `liquidity` no longer accidentally match `state` and `liquid`.
- Updated the public homepage v0.2.27 detail cards to describe the actual final
  audit closure work instead of stale earlier-round details.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v027-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  HTML guide generated at `outputs/_fresh-v027-demo/guide.html`; PDF skipped
  (`--skip-pdf`). The resulting validation output reported `issues: []`, 3
  topics, 6 practice cards, 3 topic guides, 3 visual briefs, 3 SVG-safe visuals,
  0 infographic visuals, 3 topic diagrams in HTML, 3 visual examples in HTML, 7
  section files, 3 image files, and both visual/package manifests. The ignored
  output folder was removed after collecting release evidence and is not
  committed.
- `python -m pytest tests/test_visual_routing.py tests/test_visual_routing_benchmark.py -q`
  (`17 passed`).
- `python -m pytest tests/test_subject_profiles.py tests/test_localization.py tests/test_validation_checks.py -q`
  (`23 passed`).
- `python -m pytest tests/test_visual_routing.py tests/test_visual_routing_benchmark.py tests/test_subject_profiles.py tests/test_localization.py tests/test_validation_checks.py -q`
  (`40 passed`).
- `python -m pytest tests/test_release_scripts.py tests/test_visual_routing.py tests/test_visual_routing_benchmark.py tests/test_subject_profiles.py tests/test_localization.py tests/test_validation_checks.py -q`
  (`52 passed`).
- `python -m pytest tests/test_visual_routing.py tests/test_visual_routing_benchmark.py --cov=intl_exam_guide.planning.visual_routing --cov-report=term-missing -q`
  (`17 passed`, `100%` for `visual_routing.py`).
- `python -m pytest tests/test_subject_profiles.py --cov=intl_exam_guide.planning.subject_profiles --cov-report=term-missing -q`
  (`4 passed`, `100%`).
- `python -m pytest tests/test_validation_checks.py --cov=intl_exam_guide.validation.checks --cov-report=term-missing -q`
  (`13 passed`, `91%` for `validation/checks.py`).
- `python -m pytest --cov --cov-report=term-missing -q` (`220 passed`, coverage
  `86%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py . ./outputs` (`raw_key_matches: 0`).
- `git diff --check`

## 0.2.26 - 2026-06-21

### Tests

- Closed the thirteenth-round audit follow-up by adding dedicated
  `subject_profiles.py` tests for declared subject routing, ambiguous science
  source-text routing, and the mathematics prefix heuristic.
- Added dedicated `validation/checks.py` tests for preflight/source checks,
  custom image-provider validation, guide/practice/visual validators,
  qualification notes, output package validation, HTML language checks, visual
  asset checks, review summaries, mixed-language labels, and small helper
  branches.
- Tightened `zh_topic_reference()` tests from loose containment checks to exact
  Chinese return values.
- Expanded `zh_visual_type()` tests so OR-condition aliases such as
  `prime-entry`, `reconciliation`, `financial-statement`, `venn`, and
  `probability` are tested as standalone triggers.
- Strengthened the intro-animation version guard so it rejects any stale
  `v0.2.x` label, not only the historical `v0.2.20` value.

### Changed

- Updated package version and public intro animation labels to `v0.2.26`.
- Updated README release histories, project operations notes, and the public
  homepage version card for the thirteenth-round audit closure.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v026-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  HTML guide generated; PDF skipped (--skip-pdf). The resulting validation
  output reported `issues: []`, 3 topics, 6 practice cards, 3 topic guides,
  3 visual briefs, 3 SVG-safe visuals, 3 topic diagrams in HTML, 3 visual
  examples in HTML, 7 section files, 3 image files, and both visual/package
  manifests. The ignored output folder was removed after collecting release
  evidence and is not committed.
- `python -m pytest tests/test_subject_profiles.py tests/test_validation_checks.py tests/test_localization.py tests/test_release_scripts.py::test_intro_animation_visible_version_labels_match_package_version -q`
  (`16 passed`).
- `python -m pytest tests/test_subject_profiles.py --cov=intl_exam_guide.planning.subject_profiles --cov-report=term-missing -q`
  (`3 passed`, `94%`).
- `python -m pytest tests/test_validation_checks.py --cov=intl_exam_guide.validation.checks --cov-report=term-missing -q`
  (`7 passed`, `79%`).
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`203 passed`, coverage `85.51%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py . ./outputs` (`raw_key_matches: 0`)
- `git diff --check` (only Windows line-ending notices, no whitespace errors)

## 0.2.25 - 2026-06-21

### Tests

- Closed the twelfth-round precision follow-up by replacing the remaining weak
  Chinese assertions with exact input-to-output checks for `style_display()`,
  `zh_point_labels()`, and `zh_visual_trigger()`.
- Added dedicated `zh_visual_type()` coverage for accounting, chemistry,
  economics, mathematics, and default visual routes so Chinese visual labels are
  no longer only covered through broader generation tests.
- Strengthened Chinese explanation-style tests with style-specific fragments for
  formal, life-scene, story, detective, adventure, and friendly/default modes.
- Added a release-asset guard that checks the Chinese and English intro
  animation `index.html` and `video.jsx` files contain the current package
  version and do not retain the old `v0.2.20` label.

### Changed

- Updated public intro animation labels in both Chinese and English assets to
  `v0.2.25`.
- Added the animation-version guard to the operations guide so future releases
  check visible animation labels alongside `pyproject.toml` and
  `src/intl_exam_guide/__init__.py`.
- Updated README release histories and the public homepage version card for the
  twelfth-round precision pass.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v025-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  HTML guide generated; PDF skipped (--skip-pdf). The resulting validation
  output reported `issues: []`, 3 topics, 6 practice cards, 3 topic guides,
  3 visual briefs, 3 SVG-safe visuals, 3 topic diagrams in HTML, 3 visual
  examples in HTML, 7 section files, 3 image files, and both visual/package
  manifests. The ignored output folder was removed after collecting release
  evidence and is not committed.
- `python -m pytest tests/test_localization.py tests/test_explanation_styles.py tests/test_rendering_contracts.py tests/test_release_scripts.py -q`
  (`37 passed`).
- `python -m pytest tests/test_localization.py --cov=intl_exam_guide.planning.localization --cov-report=term-missing -q`
  (`4 passed`, `100%`).
- `python -m pytest tests/test_explanation_styles.py --cov=intl_exam_guide.planning.explanation_styles --cov-report=term-missing -q`
  (`3 passed`, `100%`).
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`192 passed`, coverage `83.67%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py . ./outputs` (`raw_key_matches: 0`)
- `git diff --check` (only Windows line-ending notices, no whitespace errors)

## 0.2.24 - 2026-06-21

### Tests

- Closed the eleventh-round P3 follow-up by adding dedicated
  `explanation_styles.py` tests for formal, life-scene, story, detective,
  adventure, and friendly/default explanation branches.
- Added dedicated `localization.py` tests for `zh_topic_reference()`,
  `zh_point_labels()`, and `zh_visual_trigger()`.
- Added direct `zh-CN` rendering tests for HTML helpers that were previously
  covered only indirectly: style labels, image-provider labels, source notes,
  listing notes, revision stages, missing links, and the full `render_html()`
  Chinese entry path.
- Replaced the remaining weak `build_visual_asset_lookup()` truthy assertion
  with an exact lookup assertion.
- Added SVG text edge-case tests for slash token wrapping and three-line
  truncation in `svg_multiline_text()`.

### Changed

- Removed the unused `zh-CN` branch from `render_concept_fallback_svg()`. The
  production Chinese path already uses `render_zh_visual_svg()`, so the concept
  fallback is now an English-only fallback with a simpler signature.
- Added `uv.lock` to `.gitignore` so local package-manager lockfiles do not
  appear as stray release artifacts.
- Aligned raw-key scan examples in the README and operations guide with the
  release checklist command: `python scripts/scan_for_raw_keys.py . ./outputs`.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v024-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  HTML guide generated; PDF skipped (--skip-pdf). The resulting validation
  output reported `issues: []`, 3 topics, 6 practice cards, 3 topic guides,
  3 visual briefs, 3 SVG-safe visuals, 3 topic diagrams in HTML, 3 visual
  examples in HTML, 7 section files, 3 image files, and both visual/package
  manifests. The ignored output folder was removed after collecting release
  evidence and is not committed.
- `python -m pytest tests/test_explanation_styles.py tests/test_localization.py tests/test_rendering_contracts.py tests/test_svg_templates.py -q`
  (`28 passed`).
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`190 passed`, coverage `83.35%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py . ./outputs` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.23 - 2026-06-21

### Tests

- Closed the tenth-round P3 review items by replacing weak truthy assertions
  with exact-value assertions for Chinese topic-title and source-reference
  helpers.
- Added direct `zh-CN` rendering-contract coverage for handbook overview,
  summary, assessments, `render_topics()`, topic guide cards, concept diagrams,
  visual examples, practice cards, and the source appendix.
- Added dedicated tests for `rendering/svg_templates.py`, covering English and
  Chinese SVG routing, direct SVG helpers, fallback visuals, escaping, and
  deterministic word wrapping.
- Added dedicated tests for `rendering/text.py`, covering supported subject
  display names, generic fallback, and HTML escaping.
- Added direct checks for the small `render_listing_note()` and `topic_anchor()`
  helpers that were previously only indirectly covered.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v023-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  The resulting validation output reported `issues: []`, 3 topics, 6 practice
  cards, 3 topic guides, 3 visual briefs, 3 SVG-safe visuals, 3 topic diagrams
  in HTML, 3 visual examples in HTML, 7 section files, 3 image files, and both
  visual/package manifests. The ignored output folder was removed after
  collecting release evidence and is not committed.
- `python -m pytest tests/test_rendering_contracts.py tests/test_svg_templates.py tests/test_rendering_text.py -q`
  (`23 passed`).
- `python -m pytest tests/test_svg_templates.py --cov=intl_exam_guide.rendering.svg_templates --cov-report=term-missing -q`
  (`4 passed`, `svg_templates.py` dedicated coverage `100%`).
- `python -m pytest tests/test_rendering_text.py --cov=intl_exam_guide.rendering.text --cov-report=term-missing -q`
  (`3 passed`, `text.py` dedicated coverage `100%`).
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`182 passed`, coverage `82.97%`; `rendering/html.py` coverage `97%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.22 - 2026-06-21

### Tests

- Closed the ninth-round audit gap around `rendering/html.py` by adding direct
  rendering contract tests for the full HTML entry point, topic sections,
  guide cards, concept diagrams, story-mode blocks, practice cards, visual
  example routing, source appendix, assessment fallback, navigation, and topic
  title localization.
- Added direct coverage for the `render_topics()` function group instead of
  relying only on end-to-end guide generation to touch the topic renderer.

### Verified

- `python -m pytest tests/test_rendering_contracts.py --cov=intl_exam_guide.rendering.html --cov-report=term-missing -q`
  (`15 passed`; `rendering/html.py` direct coverage increased to `89%`).
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`174 passed`, coverage `81.70%`; `rendering/html.py` total coverage `96%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.21 - 2026-06-21

### Tests

- Added Playwright PDF export success and launch-failure tests so both the
  preferred browser path and fallback error reporting stay covered.
- Added a Playwright channel fallback test for the Chrome-fails / Edge-succeeds
  route.
- Added architecture guards for shared icon registration and unknown icon
  fallback behavior.
- Expanded practice-generator regression coverage for even/odd variants across
  major Mathematics, Chemistry, Accounting, and Economics example branches.
- Expanded visual-routing tests for additional Accounting, Economics,
  Chemistry, Mathematics, Physics, and generic SVG/infographic routes.
- Added common provider parser helper tests for URL normalization, candidate
  choice messages, qualification type inference, metadata extraction, overview
  topics, chunk fallback behavior, link deduplication, and topic deduplication.
- Added a PDF text extraction test for page separators and `max_pages`.
- Added direct rendering contract tests for the handbook stylesheet, course
  identity cover, source/setup copy, visual manifest loading, generated raster
  asset reuse, SVG fallback assets, and modular handbook package output.

### Verified

- Fresh offline demo evidence was regenerated from the current working copy:
  `python -m intl_exam_guide demo --out ./outputs/_fresh-v021-demo --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf`.
  The resulting `validation.json` reported `issues: []`, 3 topics, 6 practice
  cards, 3 visual briefs, 3 image files, 7 section files, and a generated HTML
  guide. The ignored output folder is validation evidence only and is not
  committed.
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`169 passed`, coverage `81.26%`).
- `python -m ruff check .`
- `python -m mypy`
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.20 - 2026-06-20

### Changed

- Centralized handbook SVG icon rendering in `rendering/icons.py` so normal HTML
  sections and infographic cards no longer carry duplicate icon definitions.
- Tightened the `practice_generator.py` architecture guard from 1000 lines to
  950 lines to keep the generator from drifting back toward a monolith.
- Added release and PR checklist guards requiring validation evidence to come
  from fresh outputs generated by the current code, not stale ignored `outputs/`
  or old `validation.json` files.

### Tests

- Expanded `practice_generator.py` regression coverage across Mathematics,
  Chemistry, Accounting, Economics, Biology, Chinese examples, command words,
  and difficulty rotation.
- Added PDF export branch tests for missing Playwright, browser timeout, and
  successful browser CLI command construction.
- Added an architecture guard ensuring `outputs/` remains ignored and is not
  tracked as release source.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`146 passed`, coverage `76.94%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)

## 0.2.19 - 2026-06-20

### Fixed

- Fixed generated handbook covers so unknown, synthetic, or demo sources no
  longer fall back to AQA/OxfordAQA branding. AQA is now shown only when the
  source metadata or URL explicitly identifies AQA/OxfordAQA.
- Added neutral cover styling for unspecified exam-board sources.
- Expanded the anti-template wording gate to catch and safely remove more
  formulaic English and Chinese AI-style transitions, including "It's important
  to note", "Let's dive into", "在当今社会", "让我们一起", and "深入探讨".

### Tests

- Added cover regression coverage for unknown-provider sources.
- Added direct unit tests for generated infographic, SVG fallback, and pending
  infographic rendering branches.
- Added Mathematics, Biology, Economics, and generic fallback practice-example
  regression tests.
- Added a small `python -m intl_exam_guide` entry-point smoke test.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`135 passed`, coverage `73.94%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)

## 0.2.18 - 2026-06-20

### Changed

- Split infographic HTML rendering out of `rendering/html.py` into
  `rendering/infographics.py`, keeping the generated handbook behavior the
  same while reducing the main renderer's responsibility.
- Reused the shared `subject_profiles.has_terms` matcher in
  `practice_generator.py` instead of carrying a duplicate local token/phrase
  matcher.
- Raised the CI coverage gate from 60% to 70% after the project consistently
  exceeded that level.

### Fixed

- Fixed common PDF assessment parsing so durations such as
  `1 hour 30 minutes` and standalone weighting lines such as `50%` are captured
  correctly.
- Added architecture guards for `practice_generator.py` and the new infographic
  renderer split.

### Tests

- Added direct `practice_generator` unit tests for styled practice cards,
  Accounting/Chemistry routing, and Chinese student-facing example text.
- Added common provider parser tests for assessment papers, command words, and
  assessment objectives.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -q`
  (`125 passed`, coverage `73.30%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`
- `python -m intl_exam_guide demo --out outputs/_fourth-review-check --language en --explanation-style friendly --image-provider deterministic-svg --skip-pdf`
  completed with `issues: []`.

## 0.2.17 - 2026-06-20

### Changed

- Added a deterministic anti-template language gate to the generation flow.
  Topic explanations and practice items now remove safe formulaic transitions
  such as "In conclusion", "Overall", "总之", and "值得注意的是" before they are
  written into the guide plan.
- Added validation warnings for remaining formulaic AI-style wording in topic
  guides and practice cards, so suspicious phrasing can be reviewed without
  blocking otherwise valid handbooks.
- Documented the design inspirations clearly: the anti-template writing pass is
  adapted from the anti-AI-language gate idea in `qiaomu-novel-generator`, and
  the scientific SVG fallback is inspired by the `nature-figure` contract idea
  in `Yuan1z0825/nature-skills`. Both are adapted into this project and are not
  runtime dependencies.

### Verified

- `python -m pytest tests/test_anti_ai_language.py tests/test_guide_plan_units.py -q`
  (`9 passed`)
- `python -m ruff check src\intl_exam_guide\planning\anti_ai_language.py tests\test_anti_ai_language.py src\intl_exam_guide\planning\guide_plan.py src\intl_exam_guide\planning\practice_generator.py src\intl_exam_guide\validation\checks.py`
- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q`
  (`120 passed`, coverage `71.45%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`
- English and Chinese demo generation with `--skip-pdf` both completed with
  `issues: []`; the English output scan found no common formulaic AI phrases.

## 0.2.16 - 2026-06-20

### Changed

- Clarified the callable image workflow: "external" image generation does not
  mean the user must move files by hand. If a user has a callable image Skill,
  API, script, designer workflow, or matching generated asset directory, the
  Agent should run or import that route after the base handbook is generated
  and attach the reviewed assets automatically.
- Changed imported infographic assets to use the neutral
  `reviewed-generated` status by default, avoiding misleading manual-import
  wording in new manifests.
- Updated README, Skill, image-model guide, release checklist, homepage, and
  animation version labels to reflect the v0.2.16 behavior.

### Fixed

- Removed stale public validation/sample statuses that referenced a private
  local image router or implied manual file-moving as the normal image path.
- Added regression assertions that the public Skill explicitly says callable
  image routes can be run automatically and are not built-in providers.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q`
  (`115 passed`, coverage `71.23%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.15 - 2026-06-20

### Changed

- Removed the local image-generation router script from the public repository so
  GPT Image, Qwen, and SenseNova remain documented as external options instead
  of implied built-in providers.
- Updated image-model, example, release-checklist, and Skill documentation to
  use external reviewed asset import as the public release workflow.

### Fixed

- Added direct guide-plan tests for image-provider normalization, custom
  provider gating, readable Chinese revision stages, practice generation, and
  visual-brief routing.
- Added provider tests for Pearson specification PDF selection, Pearson helper
  boundaries, Cambridge direct-PDF exam-year validation, and generic PDF link
  selection.
- Added PDF export error-path tests for missing browser and failed browser CLI
  runs.
- Added topic-aware story-mode tests so narrative cards stay tied to the
  subject instead of only rotating generic copy.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest tests/test_guide_plan_units.py tests/test_url_first_providers.py tests/test_pdf_export.py tests/test_story_modes.py tests/test_release_scripts.py -q`
  (`49 passed`)
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q`
  (`115 passed`, coverage `71.23%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.14 - 2026-06-20

### Changed

- Completed the actionable third-round audit items except for embedding a built-in
  image model, which remains intentionally out of scope.
- Split the former monolithic `guide_plan.py` into smaller planning modules for
  localization, explanation styles, practice generation, and visual routing while
  preserving the old public import path for Agent compatibility.
- Split infographic rendering into separate generated-asset, SVG-fallback, and
  pending-queue renderers.
- Made narrative explanation cards more topic-aware for accounting, economics,
  chemistry, and mathematics instead of relying only on index-based rotation.
- Added CI type checking with mypy and coverage XML upload through Codecov.

### Fixed

- Tightened Pearson Edexcel specification PDF selection so welcome guides, past
  papers, and mark schemes are not accepted as specifications.
- Cleaned Pearson subject names so issue years such as `(2017)` do not leak into
  `subject_area`.
- Stopped Pearson learning-table parsing at appendix/administration sections.

### Verified

- `python -m ruff check .`
- `python -m mypy`
- `python -m pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q`
  (`101 passed`, coverage `70.68%`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`

## 0.2.13 - 2026-06-20

### Changed

- Redesigned the generated handbook cover so the first page is a clean course
  identity page: exam board, qualification, subject, course code, syllabus /
  specification version, and target exam year.
- Kept learning route and generation statistics off the cover and moved setup
  context into the following pages.
- Simplified the roadmap page by removing the extra study-route column and
  keeping the table focused on knowledge units and what students need to
  master.

### Fixed

- Removed student-facing internal wording such as source "boundaries",
  preflight image routes, and deterministic/SVG safety language from the guide
  setup copy.
- Improved Chinese fallback topic titles for demo material/change content so
  the guide does not fall back to generic labels like "第 3 节".

### Verified

- `python -m pytest tests/test_demo_cli.py -q` (`30 passed`)

## 0.2.12 - 2026-06-20

### Fixed

- Clarified the Skill and project documentation so image generation is no
  longer presented as a required preflight choice. Agents should first generate
  the source-bound base handbook, then report pending complex infographic
  briefs and only use external image generation after a callable route or
  reviewed assets are provided.
- Generalized Skill explanation diagrams, release checks, and image prompt
  templates from AQA/OxfordAQA-only wording to the supported AQA, Edexcel, and
  CAIE workflow.
- Updated release validation wording so all official specification/syllabus
  PDFs are treated consistently and no board-specific PDF language misleads
  future agents.

### Verified

- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`
- Documentation phrase scan for the removed AQA-only and preflight image-route
  wording.

## 0.2.11 - 2026-06-19

### Fixed

- Clarified visual-output validation so `validation.json` now separates
  reviewed/generated raster infographics from SVG fallback assets and pending
  infographic briefs. This prevents audit reports from treating a deliberate
  prompt-queue/SVG-fallback run as if the visual pipeline produced no files.
- Updated infographic warning messages to include how many SVG fallback assets
  were written for draft review while complex infographics wait for an external
  image model, script, or imported reviewed asset.

### Verified

- `python -m pytest -q` (`90 passed`)
- Real CLI checks in temporary directories:
  AQA Accounting, Pearson Edexcel Accounting by official URL, and CAIE
  Accounting by official URL with `--exam-year 2027`.

## 0.2.10 - 2026-06-19

### Fixed

- Hardened PDF text extraction so missing, damaged, encrypted, or page-level
  extraction failures are reported as controlled `PdfTextExtractionError`
  cases with tests.
- Added cross-platform browser discovery for PDF export fallbacks on Windows,
  Linux, and macOS.
- Removed duplicated provider helpers from the OxfordAQA provider and added
  coverage for the shared helper signatures.
- Fixed Pearson Edexcel parsing so trailing Pearson copyright/front-matter
  pages cannot be appended into the last learning-table topic.
- Fixed Cambridge / CAIE parsing so `Content overview` pages and AO1/AO2/AO3
  assessment-objective tables are not mixed into detailed subject topics.
- Added topic navigation anchors and max-width reading constraints to generated
  handbook HTML and section packages.
- Replaced Chinese topic-title placeholders such as numbered knowledge units
  with cleaner section labels or subject-aware localized titles.
- Added subject-specific SVG fallback templates for accounting records,
  reconciliation, financial statements, market diagrams, economic flows, Venn
  regions, forces, and gas tests.
- Kept Chinese visual routing subject-specific so accounting visuals no longer
  collapse into a generic "图文结合学习图" route.
- Split validation checks into smaller validation stages and moved story-mode
  sentence rotation into a small rendering helper module.

### Verified

- `python -m ruff check .`
- `python -m pytest -q` (`90 passed`)
- Real CLI checks in temporary directories:
  AQA Accounting, Pearson Edexcel Accounting by official URL, and CAIE
  Accounting by official URL with `--exam-year 2027`.

## 0.2.9 - 2026-06-19

### Fixed

- Added CI matrix coverage for Ubuntu and Windows on Python 3.11 and 3.12.
- Added a coverage gate with `pytest-cov` so CI now fails below the configured
  coverage floor instead of only running plain tests.
- Added visual routing benchmarks for Accounting, Economics, Chemistry,
  Mathematics, and Physics so complex teaching visuals cannot silently fall
  back to unrelated generic SVGs.
- Added a Physics subject profile so force and motion topics route to
  infographic briefs instead of plain text.
- Fixed SVG routing collisions where substring matches such as `preparation`
  containing `ratio`, or `graph` containing `ph`, could select the wrong
  diagram.
- Split the HTML renderer into page structure, SVG templates, and CSS modules,
  then added an architecture guard to stop the main HTML renderer from growing
  back into a monolith.

### Verified

- `python -m ruff check .`
- `python -m pytest --cov --cov-report=term-missing --cov-fail-under=60 -q`
  (`79 passed`, total coverage 65.60%)

## 0.2.8 - 2026-06-19

### Fixed

- Unified provider download/text-cleaning helpers so AQA, Edexcel, and CAIE use
  one source-traceable User-Agent and one safe URL/text path.
- Replaced broad provider and PDF `except Exception` handlers with narrower
  network, parser, and PDF-export errors so implementation bugs are no longer
  hidden as missing candidates.
- Added a Pearson Edexcel learning-table parser for `Topic ... / What students
  need to learn` specification pages, preventing Edexcel Accounting from falling
  back to generic `Content unit` blocks.
- Made PDF export match the declared optional dependency: Playwright is tried
  first, then local Chrome/Edge is used as a fallback, with a clear PDF export
  error if neither route works.
- Added validation hard gates for downloaded specifications that produce generic
  `Content unit` topics or no assessment papers.
- Added practice-question variant markers so repeated worked examples under the
  same topic are caught and avoided.
- Renamed the HTML escaping helper to avoid shadowing the standard-library
  module while keeping quoted attribute escaping enabled.
- Added CI linting with `ruff check .`.
- Added offline CLI coverage for `discover` and the full `generate` provider
  chain.

### Verified

- `python -m ruff check .`
- `python -m pytest -q` (`74 passed`)
- `python -m compileall -q src tests scripts`
- `python scripts/scan_for_raw_keys.py .` (`raw_key_matches: 0`)
- `git diff --check`
- Real CLI regressions with no validation errors except expected pending
  infographic warnings:
  AQA Accounting, AQA Economics, Pearson Edexcel Accounting, and CAIE
  Accounting.

## 0.2.7 - 2026-06-19

### Fixed

- Removed public local-machine notes and private paths from the repository
  entry points so a clean GitHub clone no longer points agents at private
  working folders.
- Removed a duplicate CLI provider resolver.
- Strengthened validation so Chinese placeholder text such as generic numbered
  syllabus points and duplicate practice questions are reported as errors.
- Split several Chinese point labels for demo science topics so repeated topic
  cards do not collapse into identical practice prompts.

## 0.2.6 - 2026-06-19

### Fixed

- Fixed the intro-animation export viewport and duration. The animation stage is
  1920x1080, so the render script now captures at 1920x1080 before scaling GIF
  previews, preventing README animation previews from being cropped into a
  960x667 frame. The export duration now covers the full 32-second animation.
- Tightened the intro-animation layout for the provider, handbook-sample, and
  visual-routing scenes so headings, cards, and statistics do not overlap.
- Reworded public setup text so it refers to AI and to OpenClaw, Hermes, or
  other Skill-compatible Agents instead of emphasizing a specific build tool.

## 0.2.5 - 2026-06-19

### Fixed

- Split the public intro animation into language-specific versions. The English
  README now links to an English-only HTML animation and GIF preview, while the
  Chinese README keeps the Chinese animation and Chinese GIF preview.
- Forwarded animation preview query parameters through the intro wrapper pages
  so rendered GIF previews can capture the intended timeline instead of a static
  initial frame.

## 0.2.4 - 2026-06-19

### Fixed

- Updated the intro-animation copy so Edexcel and CAIE are no longer described
  as future/URL-only work. The animation now reflects the current v0.2.x support
  model: AQA catalogue discovery, Edexcel official candidate matching, and CAIE
  official subject-index matching with exam-year confirmation.

## 0.2.3 - 2026-06-19

### Fixed

- Restored the clickable intro-animation preview directly under the project
  origin section in both English and Chinese READMEs, using the tracked GIF
  preview and linking to the full HTML animation.
- Made the full HTML intro animation standalone by inlining the local animation
  scripts, so opening `docs/project-intro-animation.html` from `file://` also
  auto-plays instead of being blocked by browser CORS rules.

## 0.2.2 - 2026-06-19

### Changed

- Darwin-optimized `skill/SKILL.md` and raised the independent judge score from
  about `81.1/100` to `91.1/100`.
- Added explicit `STOP` / `CHECKPOINT` gates for missing preflight choices,
  official candidate selection, missing official routes, base-handbook
  completion, non-callable image models, and final quality validation.
- Added a standard Edexcel/CAIE official-candidate response template so agents
  return choices to the user instead of guessing a subject route.
- Documented the real provider-resolution commands: AQA supports catalogue
  discovery, while Edexcel and CAIE use URL-first / subject-candidate checks
  rather than full-site crawling.
- Clarified that scratch candidate-check outputs are not final handbooks; agents
  must re-run with the user's confirmed language, style, output directory, and
  PDF settings after the official route is selected.

## 0.2.1 - 2026-06-19

### Changed

- Updated the public naming convention to use the familiar exam-board names
  AQA, Edexcel, and CAIE across the Skill, README, homepage copy, project docs,
  and hero artwork, while keeping the full official names as explanatory notes:
  OxfordAQA / Oxford International AQA, Pearson Edexcel, and Cambridge
  International / CAIE.
- Darwin-tuned `skill/SKILL.md` so the agent flow is clearer: confirm exam
  board, subject, required exam year, output language, and explanation style
  first; do not ask for an image model before the base handbook run.
- Added `skill/test-prompts.json` with regression prompts for AQA Accounting,
  ambiguous Edexcel subject selection, CAIE exam-year selection, and non-callable
  image-model requests.

### Fixed

- Fixed Chinese handbook content generated during real Accounting/Economics
  runs so visible focus labels no longer fall back to generic text such as
  `第 N 个官方大纲要求`.
- Translated student-facing Chinese Accounting examples that previously leaked
  raw English terms such as `purchase invoice`, `purchases journal`, and
  `ledger accounts`.
- Fixed the Chinese visual-type classifier so the word `infographic` no longer
  accidentally triggers the pH/acid label merely because it contains `ph`.
- Added Accounting as a Chinese subject display name (`会计学`) in rendered
  handbook covers and overview blocks.
- Treated `sensenova-generated` image assets as renderable generated raster
  infographics, so externally generated SenseNova assets can be preserved and
  rendered.
- Increased browser PDF export timeout for image-heavy handbooks.
- Added validation and regression tests for the Chinese placeholder, Accounting
  Chinese terminology, SenseNova asset status, Accounting display name, and the
  visual-type classifier.
- Removed remaining user-facing wording that made the project look like an
  OxfordAQA-only Skill after the v0.2.0 three-board upgrade.
- Tightened image-generation instructions so recommended models such as GPT
  Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are described as
  recommendations, not guaranteed built-in capabilities.
- Generalized source-safety wording from OxfordAQA-only PDFs to official PDFs
  from all supported exam boards.

## 0.2.0 - 2026-06-19

### Added

- Added URL-first MVP providers for Pearson Edexcel and Cambridge International / CAIE while keeping OxfordAQA generation working.
- Added `--exam-year` support so Cambridge subject pages with multiple syllabus year ranges can select the correct syllabus or fail with a clear request for the exam year.
- Added provider/source metadata fields for provider name, qualification family, specification URL, PDF hash, syllabus year range, selected exam year, route tags, command words, assessment objectives, and paper/unit/component details.
- Added live smoke coverage for OxfordAQA, Pearson International GCSE, Pearson International AS/A Level, Cambridge IGCSE, and Cambridge International AS/A Level.

### Changed

- Complex infographic routing now defaults to source-bound `visual_brief` / prompt queue output. GPT Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are documented as recommended external options, not guaranteed built-in capabilities for every user.
- `--image-provider` is optional and defaults to `prompt-queue`. Real image generation or import only happens when the user supplies a callable skill, API, script, asset directory, or custom provider configuration.
- Validation now treats missing complex infographic files as pending external-generation work instead of claiming provider-selected images were generated.

### Fixed

- Cambridge missing `exam_year` on multi-range syllabus pages now stops clearly instead of silently choosing a syllabus.
- Provider validation no longer applies OxfordAQA modular assumptions to Cambridge AS/A Level outputs.
- Topic-count sanity checks now catch obviously thin extraction from downloaded specification/syllabus PDFs.

## 0.1.1 - 2026-06-18

### Fixed

- Fixed OxfordAQA syllabus parsing so subjects such as Accounting no longer fall back to a few top-level table-of-contents headings.
- Expanded body-table syllabus sections into teachable knowledge units when the official PDF uses broad `3.x` sections instead of many leaf topic codes.
- Preserved PDF body source snippets from the parser and skipped contents/index pages during fallback source matching.
- Added Accounting/finance subject profiling so Accounting examples use source documents, books of prime entry, ledgers, reconciliation, statements, and ratios instead of borrowed Mathematics templates.
- Routed Accounting, Economics, Business, and other complex visual explanations to infographic prompts instead of unsafe or misleading SVG drafts.
- Strengthened validation to fail empty syllabus topics, contents-page-only source anchors, placeholder practice frames, and cross-subject borrowed practice questions.
- Added regression tests for Accounting-style body tables, source-snippet preservation, and non-math example generation.

### Added

- Added the first multi-provider foundation: a common `ExamBoardProvider` contract, provider registry, URL-based provider inference, and model fields for Cambridge syllabus year ranges and Edexcel modular/unit structures.
- Added explicit guardrails for Pearson Edexcel and Cambridge International / CAIE URLs. In this release they were recognised as roadmap providers and stopped with a clear roadmap message.

### Verified

- Accounting International GCSE: 68 topics, 136 practice cards, 68 infographic briefs.
- Mathematics International GCSE: 90 topics, 180 practice cards, 43 SVG-safe briefs, 39 infographic briefs.
- Chemistry International GCSE: 35 topics, 70 practice cards, 14 SVG-safe briefs, 18 infographic briefs.
- Economics International GCSE: 38 topics, 76 practice cards, 38 infographic briefs.
- Business International AS-A-level: 29 topics, 58 practice cards, 29 infographic briefs.

### Notes

- `prompt-queue` remains the safe no-API image route. Complex infographic briefs require a callable external skill/API/script, generated asset directory, or custom provider before final raster assets are added.
- Official specification PDFs and extracted official text are generated at runtime and are not committed to the repository.

## 0.1.0 - Initial public architecture draft

- Initial OxfordAQA-focused Skill architecture for generating International GCSE and International AS-A-level revision handbooks.
- Added language selection, explanation style selection, visual routing, source appendix, HTML/PDF packaging, and release-sample documentation.
