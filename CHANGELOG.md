# Changelog

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
  subjects. The hot review in `docs/PROJECT_HOT_REVIEW_20260703.md` records the
  remaining product and architecture risks: real multi-agent orchestration is
  still not enforced by the Python runtime, final review is partly dependent on
  the active user Agent, subject coverage remains uneven, and the visual routing
  stack needs a cleaner rebuild before claiming 95%+ student-ready accuracy.

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
