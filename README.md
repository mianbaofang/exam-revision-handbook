# IGCSE & A-Level AI Revision Guide Skill

<p align="center">
  <img src="docs/assets/hero.svg" alt="IGCSE and A-Level AI Revision Guide Skill hero" width="100%">
</p>

## Why This Skill Exists

This project began at home. My son is taking his International GCSE exams this
year after moving from a Chinese public-school path into an international
curriculum. In less than a year, the classroom language shifted from Chinese to
English, while the exam clock kept moving.

I used AI to build a study and revision Skill: take the course requirements,
break knowledge into understandable structures, worked examples, diagrams, and
checkpoints. The goal is not to let AI learn for a child. The goal is to lower
the noise around learning so students can face schoolwork with more calm and
control.

<p align="center">
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation-en.html">
    <img src="docs/assets/intro-animation-preview-en.gif" alt="Three-board revision handbook Skill HTML intro preview" width="100%">
  </a>
</p>

<p align="center">
  <a href="README.zh-CN.md">中文 README</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/">Project site</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation-en.html">HTML intro</a>
  ·
  <a href="docs/PROJECT_DETAILS.md">Project details</a>
  ·
  <a href="docs/PROJECT_OPERATIONS.md">Operations guide</a>
  ·
  <a href="docs/IMAGE_MODEL_GUIDE.md">Image guidance</a>
</p>

An AI Skill for generating image-rich, printable International GCSE and
International AS-A-level revision handbooks from official exam-board sources.

This version is built around the three exam boards most relevant to mainland
China international-school usage:

| Exam board | Current support |
|---|---|
| AQA | Discovers qualifications from OxfordAQA / Oxford International AQA public pages and reads the public specification PDF. |
| Edexcel | Tries official Pearson Edexcel subject-page candidates from the subject name; falls back to a supplied official subject page or direct specification PDF URL. |
| CAIE | Searches official Cambridge International subject indexes for candidates; falls back to a supplied official subject page or direct syllabus PDF URL; asks for the exam year when several ranges are listed. |

It uses one shared handbook workflow across the three boards: read the official
syllabus, expand it into teachable topic units, write reviewed concept
explanations from the current topic/source points, create worked examples,
decide which points need visuals, and deliver HTML/PDF output.

The workflow is a minimum three-role agent process. In Agent runtimes with
subagent support, the Skill must dispatch the syllabus/outline analyst,
handbook writer, and independent final reviewer as separate roles. The final
reviewer cannot be the same writing context approving its own output; if no
independent Agent/LLM context is available, the handbook stays review-ready or
draft, not final-ready. The evidence and dispatch briefs are written to
`agent-orchestration.json`, `delivery-contract.json`, and
`final-review-packet.json`.

Delivery quality claims are tracked in the delivery matrix at
`tests/fixtures/delivery_matrix.json`. Each route has an explicit claim status
and a v0.4 release-evidence status. Candidate routes must not be described as
release-ready until a fresh output passes validation, final review, and
visual-status checks. The shared workflow is three-board, but the matrix
evidence defines what is currently deliverable.
The candid rebuild plan for 95%+ student-usable delivery quality is recorded in
[`docs/DELIVERY_QUALITY_REBUILD_PLAN.md`](docs/DELIVERY_QUALITY_REBUILD_PLAN.md).

v0.4 status words are intentionally conservative:

- `candidate`: route evidence exists, but it is not delivery-grade.
- `draft`: a fresh output exists, but concepts, visuals, PDF, validation, or
  self-review still block final handoff.
- `final-ready`: current evidence says the output can be handed off after
  validation, final review, and asset/status checks.
- `certified`: final-ready evidence has also been reviewed and approved for a
  release. No current route should be called certified unless the
  release-evidence manifest says so.

## Quick Start

Most users do not need to install Python or run commands. Give this Skill link
to your OpenClaw, Hermes, or other Skill-compatible Agent:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

Then ask:

```text
Install this Skill, then generate an AQA Chemistry International GCSE revision handbook with a Simplified Chinese term glossary and export it as PDF.
```

Typical requests:

```text
Generate an Edexcel Accounting International GCSE revision guide.
Generate a Cambridge IGCSE Economics guide for the 2027 exam year with a Japanese term glossary.
Generate an AQA Mathematics 9260 revision handbook with visual worked examples and final review questions.
```

Before generation starts, the Agent should confirm:

1. Exam board, qualification level, subject, code, and official URL when needed.
2. Exam year when the official page lists multiple syllabus ranges.
3. Term-support language: `en` for no glossary, or a support language such as
   `zh-CN`, `zh-TW`, or `ja` for a 30-50 item professional term glossary. The
   handbook body, examples, labels, and visual prompts stay in English.
4. Explanation style: formal, friendly, life-scene, story-based, detective, or
   adventure-style.
5. Infographic capability: ask whether the user has a callable image or
   infographic route for this run. If yes, collect the route type, such as an
   installed image-generation Skill, a custom API endpoint plus environment
   variable name, a project script, or an existing generated-asset directory.
   If no, explain that simple SVG and Kroki diagrams can still be rendered but
   dense infographics will remain pending, then ask whether to continue as a
   draft-with-pending-images run.

The user should not be forced through a generic image-model menu. The required
early question is whether a callable image route exists at all. After the base
handbook is generated, the Agent reports how many complex infographics are
needed, runs or imports the confirmed route when available, and clearly marks
any unresolved complex visuals as not yet reviewed.

## What It Produces

```text
outputs/chemistry-9202/
  guide.html                 printable student handbook
  guide.pdf                  PDF export
  sections/                  modular guide sections for review
  images/                    SVG drafts, infographic assets, and visual manifest
  concepts/                  concept-writing jobs and reviewed explanations
  run-options.json           confirmed subject, language, and explanation style
  guide-plan.json            topic, example, and revision-task plan
  qualification.json         qualification and source metadata
  validation.json            quality-check report
  agent-orchestration.json   syllabus/writer/reviewer role evidence
  final-review-packet.json   Agent/LLM final self-review evidence
  agent-product-review.json  active Agent product-review and repair evidence
  handbook-package.json      final delivery manifest
```

The handbook package includes:

- syllabus-based topic structure;
- student-friendly explanations reviewed from per-topic source jobs;
- original worked examples with steps and answer checkpoints;
- visual-learning decisions for topics and examples;
- simple SVG diagrams and pending complex-infographic briefs;
- final revision questions;
- printable HTML/PDF output.

Before presenting an output as final, run
`python -m intl_exam_guide review --out <output-dir>` and read
`final-review-packet.json`. Validation is not enough by itself: the Agent must
inspect the rendered excerpt, topic/source summary, worked-example evidence, and
concept/image job status, then label the output as draft or final-ready for
release evidence. A route with only candidate evidence is not delivery-grade.
A base run with pending `concepts/concept_jobs.json` entries is a draft until
reviewed concept explanations are imported.

The user's LLM/Agent must also perform a final product review before handoff:
read the generated handbook as the student will see it, compare the topic
sequence and concept explanations with the syllabus outline, inspect sampled
PDF pages and visuals, and repair fixable problems before giving the file to
the user. The project must not present "the Skill generated it" or "the gate
returned ready" as a substitute for this review-and-repair loop. Record that
pass in `agent-product-review.json`; without complete product-review evidence,
the package remains review-ready or draft even if validation has no errors.

## Preview

| Mathematics | Economics | Chemistry |
|---|---|---|
| <img src="docs/assets/sample-math-guide.png" alt="Mathematics sample guide with a visual worked example" width="100%"> | <img src="docs/assets/sample-economics-guide.png" alt="Economics sample guide with infographic" width="100%"> | <img src="docs/assets/sample-chemistry-guide.png" alt="Chemistry sample guide with infographic" width="100%"> |

These screenshots demonstrate handbook quality. They are not the subject limit.

## Supported Exam Boards

| Exam board | International GCSE | International AS-A-level | Current behavior |
|---|---:|---:|---|
| AQA | yes | yes | Public catalogue discovery through OxfordAQA / Oxford International AQA pages. |
| Edexcel | yes | yes | Subject-name candidate discovery for common official Pearson Edexcel page patterns; official URL/PDF can override ambiguity. |
| CAIE | yes | yes | Official Cambridge International subject-index candidate discovery; official URL/PDF can override ambiguity; exam year is required for multi-range pages. |
| OCR, WJEC/Eduqas, CCEA, and other UK boards | no | no | Outside the current release scope. |

The current release focuses on AQA, Edexcel, and CAIE. Full official names are
OxfordAQA / Oxford International AQA, Pearson Edexcel, and Cambridge
International. It does not claim support for every UK A-level awarding
organisation.

## Visuals And Writing Styles

A useful handbook cannot be text-only. The workflow has two passes:

1. Build topic explanations and worked examples from the official syllabus.
2. Decide which topics or examples need visual explanation.

Simple reproducible diagrams use SVG. Medium-complexity professional diagrams
such as flows, hierarchies, timelines, source-to-ledger routes, and relationship
maps use the built-in Kroki renderer. Richer items become visual briefs: lab
apparatus, complex geometry, circuits, economics scenes, or text-heavy
educational infographics.

When no callable image model is available, chart-like visuals use a scripted
scientific-vector fallback inspired by `nature-figure`: editable SVG with clear
axes, labels, source-bound symbols, and review notes. Kroki covers professional
diagram structures that are more precise than hand-built generic SVG. Neither
route is a substitute for dense infographics; those remain queued until a
reviewed image asset is supplied.

Recommended external image models include:

- OpenAI GPT Image 2.0;
- Qwen Image 2.0 Pro;
- SenseNova U1 Fast.

These are recommendations, not guaranteed built-in capabilities. Users need to
provide their own callable API, Skill, script, or generated image assets. Images
explain selected syllabus points; they must not introduce unsupported exam
claims.

Writing styles include formal exam prep, friendly explanation, life-scene
analogy, story-based teaching, detective reasoning, and adventure-style study
missions. The default is original framing, not copied protected characters or
worlds.

The writing pass also includes a small anti-template-language gate adapted from
the anti-AI-language ideas in `qiaomu-novel-generator`: it removes safe
formulaic transitions and warns when a guide still sounds like generic AI prose.
This is a design inspiration, not a runtime dependency.

Design inspirations: the anti-template wording check is adapted from
`qiaomu-novel-generator`; the scientific SVG fallback is inspired by the
`nature-figure` figure-contract idea from
[`Yuan1z0825/nature-skills`](https://github.com/Yuan1z0825/nature-skills).
Both have been reshaped for revision handbooks.

## Language Policy

The handbook body is always English because the exams themselves are in
English. The preflight language choice is now a term-support language, not a
translated-body mode:

- `en` means English only, with no glossary.
- `zh-CN`, `zh-TW`, `ja`, or another supported language adds a 30-50 item
  professional glossary mapping the selected language to the official English
  exam terms.
- Student-facing explanations, worked examples, topic labels, diagram text, and
  image prompts remain English.
- The generator should not create a fully translated handbook or sprinkle
  bilingual `Chinese / English` labels through the body.

## Core Changes Since v0.1.0

README only summarizes changes that affect the Skill's actual generation flow.
See [CHANGELOG.md](CHANGELOG.md) for the complete history.

- **v0.4.2:** makes final-ready depend on real product-review evidence:
  generated outputs now require `agent-product-review.json` from the active
  Agent/LLM, plus machine-readable multi-agent dispatch briefs in
  `agent-orchestration.json`.
- **v0.4.1:** fixes the first real v0.4 sample-audit regressions: term-support
  languages now mean English body plus glossary only, cross-subject template
  leakage is blocked for Business/Economics/Physics samples, Cambridge/Pearson
  syllabus boilerplate is filtered before student-facing text, Kroki
  professional-diagram assets are rendered/importable, and PDF export strips
  browser footers plus trailing blank pages. Six fresh samples are
  validation-clean but are review-ready/draft under the v0.4.2
  product-review evidence rule.
- **v0.4:** adds the conservative delivery-state vocabulary (`candidate`,
  `draft`, `final-ready`, `certified`), the lightweight
  `docs/release-evidence/` manifest expectation, the English-body plus
  professional glossary language policy, and the three-tier visual route:
  exact SVG, built-in Kroki professional diagrams, and external reviewed
  infographics. This does not upgrade any candidate route to delivery-grade;
  v0.3 evidence remains historical unless a fresh manifest records it.
- **v0.3:** resets the final-delivery contract: topic concepts must be reviewed
  before final handoff, roadmap rows use independent mastery targets, repeated
  roadmap titles/mastery cells become validation errors, SVG is limited to
  SVG-safe diagrams, complex infographics stay in the reviewed image workflow,
  and final review packets now combine machine validation, concept status,
  image status, PDF inspection, and agent self-review.
- **v0.2.0:** expanded the project from an AQA-focused flow to a three-board
  framework for AQA, Edexcel, and CAIE; added language lock, post-handbook image
  routing, SVG fallback warnings, and cross-subject regression samples.
- **v0.2.1:** fixed real handbook regressions found during Accounting and
  Economics runs, including Chinese terminology, Accounting display names,
  generated raster assets, PDF export timeout, and validation coverage.
- **v0.2.2:** tightened Skill gates after review: confirm subject/year/language
  and style before generation, return Edexcel/CAIE candidates instead of
  guessing, and avoid presenting scratch candidate checks as final handbooks.
- **v0.2.7:** cleaned public docs so a GitHub clone has no private local paths,
  removed a duplicate CLI resolver, and tightened validation for Chinese
  placeholders plus duplicate practice questions.
- **v0.2.8:** hardened the generation engine: unified provider fetching, added
  Pearson Edexcel learning-table parsing, made PDF export prefer Playwright with
  Chrome/Edge fallback, added CLI `discover`/`generate` coverage, and added
  validation gates for generic `Content unit` topics or missing assessment
  extraction.
- **v0.2.9:** closes the remaining audit gaps: CI now runs an OS/Python matrix
  with coverage, visual routing has cross-subject benchmarks, Physics force and
  motion routes to infographic briefs, SVG substring collisions are fixed, and
  the HTML renderer is split into structure, SVG templates, and CSS modules.
- **v0.2.10:** fixes real second-round audit regressions: Edexcel no longer
  appends Pearson front matter into topics, CAIE skips content-overview and AO
  tables, Chinese handbook titles avoid generic numbered placeholders, generated
  HTML gains quick navigation and width constraints, and SVG fallbacks now use
  subject-specific accounting, economics, maths, physics, and chemistry
  templates.
- **v0.2.11:** clarifies validation output for visual assets: generated raster
  infographics, SVG fallback assets, and pending infographic briefs are now
  counted separately so prompt-queue runs are not mistaken for missing visuals.
- **v0.2.12:** cleans up Skill/project wording so image generation is presented
  as a post-handbook review step, not a required preflight model choice, and
  keeps the explanation diagrams aligned with the AQA, Edexcel, and CAIE flow.
- **v0.2.13:** redesigns the generated handbook's opening pages: the cover now
  focuses on exam-board/course identity, the setup page avoids internal
  engineering wording, and the roadmap table removes the extra study-route
  column.
- **v0.2.14:** completes the actionable third-round audit follow-up: splits the
  planning monolith, adds mypy and Codecov coverage upload to CI, strengthens
  Pearson/Cambridge parser tests, covers encrypted PDF handling, and makes
  narrative explanation cards topic-aware. Built-in image models remain out of
  scope by design.
- **v0.2.15:** finishes the third-round audit cleanup by removing the local
  image-router script from the public repo, documenting external reviewed asset
  import as the release path, and adding direct regression tests for guide-plan
  behavior, provider PDF selection, PDF export errors, and topic-aware story
  cards.
- **v0.2.16:** clarifies the image workflow after user testing: external image
  generation is not a manual file-moving step. If the user has a callable image
  Skill, API, script, or generated asset directory, the Agent should run or
  import that route automatically after the base handbook is generated.
- **v0.2.17:** adds the anti-template language gate to generated explanations
  and practice cards, plus validation warnings for remaining formulaic AI-style
  wording. The homepage and README now credit the anti-AI-language and
  nature-figure inspirations as design references, not runtime dependencies.
- **v0.2.18:** completes the fourth-round audit hardening: infographic rendering
  is split out of the main HTML renderer, practice generation reuses the shared
  subject matcher, assessment duration/weighting parsing is fixed, direct
  practice/parser tests are added, and CI now enforces 70% coverage.
- **v0.2.19:** fixes fifth-round audit regressions: unknown/demo sources no
  longer display AQA branding, anti-template wording detection covers more
  English and Chinese AI-style phrases, and direct tests now cover infographic
  rendering branches plus Mathematics/Biology/Economics practice examples.
- **v0.2.20:** closes the sixth-round audit loop by centralizing rendered icons,
  blocking stale ignored `outputs/` from being used as release evidence,
  tightening the practice-generator architecture guard, and expanding direct
  tests for multi-subject practice generation plus PDF export branches.
- **v0.2.21:** closes the eighth-round testing-coverage gap: direct renderer
  contract tests now cover handbook cover identity, stylesheet/print layout,
  visual manifest handling, generated raster reuse, SVG fallback assets, modular
  package output, and the Playwright Chrome-to-Edge PDF fallback path.
- **v0.2.22:** closes the ninth-round rendering coverage gap: `html.py`
  now has direct contract tests for the full HTML entry point, `render_topics()`,
  guide cards, concept diagrams, story-mode blocks, practice cards, visual
  example routing, source appendix, assessment fallback, navigation, and topic
  title localization.
- **v0.2.23:** closes the tenth-round P3 audit items: weak truthy assertions are
  now exact-value checks, `zh-CN` rendering paths have direct contracts, fresh
  demo evidence is restored for the release, and `svg_templates.py` plus
  `text.py` now have dedicated tests.
- **v0.2.24:** closes the eleventh-round P3 follow-up: explanation-style and
  localization helpers now have dedicated tests, `zh-CN` HTML helper branches
  and `render_html()` have direct coverage, SVG text edge cases are covered,
  raw-key release scans match the checklist, and the unused Chinese branch in
  the English concept fallback SVG was removed.
- **v0.2.25:** closes the twelfth-round precision pass: Chinese localization
  and explanation-style tests now assert exact input-to-output mappings,
  `zh_visual_type()` has dedicated route coverage, and the public intro
  animation labels are guarded against drifting behind the package version.
- **v0.2.26:** closes the thirteenth-round audit follow-up by adding dedicated
  `subject_profiles.py` and `validation/checks.py` tests, tightening
  `zh_topic_reference()` and `zh_visual_type()` route assertions, and making the
  animation version guard reject any stale `v0.2.x` label.
- **v0.2.27:** closes the final-round P3 follow-up with dedicated
  `visual_routing.py` coverage, 100% `subject_profiles.py` coverage,
  `validation/checks.py` branch coverage above 90%, exact Chinese route edge
  assertions, token-aware topic-marker matching, and a documented Skill release
  sync gate.

## Developer Quick Start

Normal Skill users can skip this section.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out .\outputs\chemistry-9202
```

Checks:

```bash
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
```

## Repository Layout

```text
src/intl_exam_guide/
  providers/      exam-board source access and parsing
  parsing/        PDF text extraction
  planning/       topic, example, and visual-brief planning
  rendering/      HTML and PDF rendering
  validation/     completeness checks
skill/            Agent-facing Skill instructions
docs/             project details, policies, examples, and preview pages
tests/            tests and regression samples
```

## Copyright And Source Policy

Do not commit downloaded official PDFs, past papers, mark schemes, or copied exam
questions. Public samples should use original explanations, original practice
cards, and the minimum source information needed for review.

Families should have subject teachers or syllabus-aware adults review deeper
worked examples before using generated guides as final exam preparation.

## License

MIT.
