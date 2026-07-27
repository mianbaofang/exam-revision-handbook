# Exam Revision Handbook

**An open-source AI Agent Skill for source-backed GCSE, IGCSE, A-Level, and AP
revision guides. It retrieves official AQA, Edexcel, CAIE, and College Board
requirements, turns them into teachable handbooks, reviews the complete HTML,
and exports PDF only after approval.**

[![Latest release](https://img.shields.io/github/v/release/mianbaofang/exam-revision-handbook?style=flat-square&label=release)](https://github.com/mianbaofang/exam-revision-handbook/releases/latest) [![CI status](https://img.shields.io/github/actions/workflow/status/mianbaofang/exam-revision-handbook/ci.yml?branch=main&style=flat-square&label=tests)](https://github.com/mianbaofang/exam-revision-handbook/actions/workflows/ci.yml) [![MIT license](https://img.shields.io/github/license/mianbaofang/exam-revision-handbook?style=flat-square)](LICENSE) [![GitHub stars](https://img.shields.io/github/stars/mianbaofang/exam-revision-handbook?style=flat-square)](https://github.com/mianbaofang/exam-revision-handbook/stargazers)

<p align="center">
  <a href="https://mianbaofang.github.io/exam-revision-handbook/project-intro-animation-en.html">
    <img src="docs/assets/intro-animation-preview-en.gif" alt="GCSE, IGCSE, A-Level, and AP revision handbook Skill intro preview" width="100%">
  </a>
</p>

<p align="center">
  <a href="README.zh-CN.md">中文 README</a>
  ·
  <a href="https://mianbaofang.github.io/exam-revision-handbook/">Project site</a>
  ·
  <a href="https://mianbaofang.github.io/exam-revision-handbook/project-intro-animation-en.html">HTML intro</a>
  ·
  <a href="docs/index.html">Project details</a>
  ·
  <a href="docs/release-evidence/README.md">Release evidence</a>
  ·
  <a href="DISCLAIMER.md">Disclaimer</a>
  ·
  <a href="ACKNOWLEDGEMENTS.md">Acknowledgements</a>
  ·
  <a href="references/revision_guide_spec.md">Handbook spec</a>
</p>

## Start In One Minute

Download the official
[v0.7.1 Skill ZIP](https://github.com/mianbaofang/exam-revision-handbook/releases/download/v0.7.1/exam-revision-handbook-v0.7.1.zip),
or give this repository URL directly to a Skill-compatible Agent:

```text
https://github.com/mianbaofang/exam-revision-handbook
```

Then ask:

```text
Install this Skill, then create an AQA International GCSE Chemistry revision handbook with a Simplified Chinese term glossary and export it as PDF.
```

| Curriculum | Official sources currently supported |
|---|---|
| GCSE and A-Level | AQA and Pearson Edexcel UK routes |
| IGCSE and International A-Level | OxfordAQA, Pearson Edexcel, and Cambridge International / CAIE |
| Advanced Placement (AP) | College Board Course and Exam Descriptions |

AS and A2 are stages within A-Level. Other curricula and exam boards do not
have automatic source acquisition; manual imports remain experimental.

## Why This Skill Exists

This project did not start as "a tool." It started with a real child moving through a difficult transition.

My son is preparing for his International GCSE exams this year. Less than a year ago, he moved from a Chinese public-school path into an international curriculum. Almost overnight, the classroom language changed from Chinese to English. The knowledge itself can be learned step by step, but a new language, a new exam style, and the pressure of an approaching exam season can easily make a child feel pushed along by the system.

I built this study and revision Skill with AI so it can take the relevant course requirements and break them into understandable structures, worked examples, diagrams, and checkpoints. The purpose is simple: not to let AI study for a child, but to reduce the noise around learning and help students face schoolwork with more calm and control.

An open-source AI Skill for generating image-rich, printable handbooks for the British secondary curriculum (GCSE, IGCSE, and A-Level) and the US Advanced Placement (AP) system from official sources, with Analyst, Writer, and Reviewer roles kept visible from source evidence to final HTML/PDF output.

> Read [Disclaimer](DISCLAIMER.md) before use. This project is not affiliated with or endorsed by any exam board, and generated study materials must be reviewed against official sources.

## At A Glance

| Question | Answer |
|---|---|
| Who is it for? | Families, tutors, and agent users preparing GCSE, IGCSE, A-Level, or AP revision handbooks. |
| What does it generate? | A source-backed handbook package with HTML/PDF output, topic plans, worked examples, visual decisions, and review evidence. |
| What does the Python package do? | Fetch official source evidence, render outputs, manage assets, and run mechanical validation. |
| What must the host LLM do? | Write the syllabus outline, teaching explanations, examples, visual decisions, and final product review. |
| Current source scope | AQA, Edexcel, CAIE, and College Board AP. |

Automatic syllabus acquisition covers the supported British source families:
AQA, Edexcel, and CAIE. It includes UK GCSE, International GCSE (IGCSE),
and A-Level routes from the supported British source families, plus the US
College Board AP system. AS and A2 are stages within A-Level, not parallel
curriculum systems. AQA and Edexcel provide separate UK-domestic and
International source routes. CAIE is Cambridge International: it provides
International GCSE and Cambridge International A-Level routes rather than a
separate UK GCSE product. A `uk-domestic` CAIE selection records a UK-centre
request but still uses the official Cambridge International catalogue. Other
curriculum systems or exam boards cannot use automatic acquisition. Manual PDF
import outside the supported routes is an unverified compatibility path and
may fail with unknown parsing, extraction, metadata, or rendering errors.

## What This Project Is

**This is a framework, not an unattended content generator.** The root
`SKILL.md` and its contracts provide the
scaffolding — syllabus parsing, HTML/PDF rendering, visual asset management,
multi-role orchestration contracts — but the actual concept explanations and
worked-example wording are produced by **the LLM that runs this Skill**:

- When the Agent host (OpenClaw / Hermes / Claude / etc.) loads this Skill,
  the host's LLM plays the **Writer** role: it writes original concept
  explanations for each topic from its own knowledge, in the requested style.
- The host's LLM also plays the **Analyst** role: it reads both the official
  Markdown companion (`source/specification.md`) and page-level evidence
  (`syllabus-evidence.json`), decides the real topic boundaries and exam
  points, and writes the authoritative `syllabus-outline.json`. Python only
  collects page evidence and invokes external MarkItDown for structure-readable
  Markdown; it does **not** decide topics or exam points on its own.
- The host's LLM then performs the **Reviewer** role as a separate review pass:
  the Reviewer personally opens the rendered HTML and source evidence without
  treating Python validation or inspection as approval, then checks for teaching
  effectiveness, blank pages, duplicate mastery text, misused visuals, or
  gap-to-source issues. Any problem returns to the Writer for repair, HTML
  rerendering, and another visible LLM review. PDF export is blocked until the
  current HTML passes. This may be a separate Agent if the user requests
  multi-agent delegation, but it is not mandatory.

The Python package under `src/intl_exam_guide/` provides:

- Provider adapters that fetch official OxfordAQA / Pearson Edexcel /
  Cambridge International qualification pages and PDFs plus College Board AP
  Course and Exam Descriptions, extract page-level evidence,
  and create a mandatory MarkItDown Markdown companion for official PDF workflows
  without adding MarkItDown to the main package dependencies.
- HTML rendering plus candidate-PDF export gated by LLM approval of the current HTML hash, followed by technical validation and an immutable current-PDF record.
- Validation and quality gates (`scripts/import_concept_explanations.py`,
  `scripts/import_infographic_assets.py`).
- A **CLI-only fallback** (`python scripts/run_runtime.py -- generate ...`) that
  produces an evidence package without the LLM Analyst outline pass. The
  CLI fallback is for testing or for environments where no Skill host is
  available. The output stays at `draft/evidence-ready` and cannot be
  presented as `final-ready`. **Run the Skill through an LLM agent to get a
  teaching-grade handbook.**

This version automatically supports the International and UK-domestic routes of
three British-curriculum exam boards plus the College Board AP course system:

| Exam board | Current support |
|---|---|
| AQA | Uses OxfordAQA / Oxford International AQA for International GCSE and A-Level routes, and AQA's official subject catalogue for UK GCSE and A-Level routes. |
| Edexcel | Uses the corresponding official Pearson Edexcel International or UK GCSE/A-Level candidate route selected during preflight. |
| CAIE | Uses Cambridge International's official subject index for International GCSE and Cambridge International A-Level. A UK-centre selection remains auditable market metadata; it does not imply a separate CAIE UK GCSE product. |
| College Board AP | Discovers all 42 official AP subjects, selects the core Course and Exam Description, verifies its official source, and records the CED effective version and target exam year. |

It uses one shared handbook workflow across the four source systems: read the official
syllabus, expand it into teachable topic units, write reviewed concept
explanations from the current topic/source points, create worked examples,
decide which points need visuals, visibly review and repair HTML until it passes,
and only then export the final PDF.

The workflow is a lightweight three-role process: Analyst, Writer, and Reviewer.
Those names are operating roles, not mandatory separate agents; one host LLM can
run them step by step unless the user explicitly chooses multi-agent delegation.
The Reviewer still has to open the visible HTML and cannot treat machine
validation as approval. Final approval covers every final topic, worked example,
answer, source anchor, and rendered visual, including notation, visual semantics,
and cross-page repetition. Supporting diagnostics are written to
`delivery-contract.json` and `final-review-packet.json`; they are not approval.

Delivery quality claims are tracked in the delivery matrix at
`tests/fixtures/delivery_matrix.json`. Each route has an explicit claim status
and a v0.7 release-evidence status. Candidate routes must not be described as
release-ready until a fresh output passes validation, final review, product
review, and visual-status checks. The shared workflow covers four source systems, but the
matrix evidence defines what is currently deliverable.

v0.7 status words are intentionally conservative:

- `candidate`: route evidence exists, but it is not delivery-grade.
- `draft`: a fresh output exists, but concepts, visuals, PDF, validation, or
  self-review still block final handoff.
- `final-ready`: this handbook has complete hash-bound LLM HTML review, gated
  PDF export, validation, concept, visual, and package evidence from the current
  artifacts.
- `certified`: final-ready evidence has also been reviewed and approved for a
  release. No current route should be called certified unless the
  release-evidence manifest says so.

## Detailed Usage

Most users do not need to install Python or run commands. Give this Skill link
to your OpenClaw, Hermes, or other Skill-compatible Agent:

```text
https://github.com/mianbaofang/exam-revision-handbook
```

Download the ready-to-use
[v0.7.1 standard Skill ZIP](https://github.com/mianbaofang/exam-revision-handbook/releases/download/v0.7.1/exam-revision-handbook-v0.7.1.zip).

Then ask:

```text
Install this Skill, then generate an AQA Chemistry International GCSE revision handbook with a Simplified Chinese term glossary and export it as PDF.
```

Typical requests:

```text
Generate an Edexcel Accounting International GCSE revision guide.
Generate a Cambridge IGCSE Economics guide for the 2027 exam year with a Japanese term glossary.
Generate an AQA Mathematics 9260 revision handbook with visual worked examples and final review questions.
Generate an AP Cybersecurity revision handbook for the 2027 exam year.
```

Before generation starts, the Agent should confirm:

1. Exam board, qualification level, subject, code, and official URL when needed.
2. Exam year when the official page lists multiple syllabus ranges or the AP CED has a future effective version.
3. Term-support language: `en` for no glossary, or a support language such as
   `zh-CN`, `zh-TW`, or `ja` for a 30-50 item professional term glossary. The
   handbook body, examples, labels, and visual prompts stay in English.
4. Explanation style: formal, friendly, life-scene, story-based, detective, or
   adventure-style.
5. Workflow mode: explicitly offer default single-host Analyst/Writer/Reviewer
   role passes, or optional multi-agent delegation if the user wants separate
   agents and the host runtime supports them. If the user stays with the default,
   record that choice in the handoff summary.
6. Infographic capability: ask whether the user has a callable image or
   infographic route for this run. If yes, collect the route type, such as an
   installed image-generation Skill, a custom API endpoint plus environment
   variable name, a project script, or an existing generated-asset directory.
   If no, explain that exact SVG/Kroki assets still require an LLM exact-fit
   decision and review, while dense infographics will remain pending; then ask
   whether to continue as a draft-with-pending-images run.

The user should not be forced through a generic image-model menu. The required
early question is whether a callable image route exists at all. After the base
handbook is generated, the Agent reports how many complex infographics are
needed, runs or imports the confirmed route when available, and clearly marks
any unresolved complex visuals as not yet reviewed.

## What It Produces

```text
outputs/chemistry-9202/
  <board>-<level>-<subject>-<time>.html  printable student handbook
  <board>-<level>-<subject>-<time>.pdf   post-approval PDF export
  sections/                  modular guide sections for review
  images/                    visual manifest, reviewed assets, and pending jobs
  concepts/                  concept-writing jobs and reviewed explanations
  run-options.json           confirmed subject, language, and explanation style
  guide-plan.json            topic, example, and revision-task plan
  qualification.json         qualification and source metadata
  validation.json            quality-check report
  final-review-packet.json   Agent/LLM final review evidence
  agent-product-review.json  active Agent product-review and repair evidence
  current-render.json        explicit current HTML/render snapshot pointer
  review-ledger/             hash-bound per-Topic, per-Visual, and holistic LLM review
  current-pdf.json           explicit current approved-PDF pointer
  pdf-exports/               immutable PDF provenance records
  current-delivery.json      optional hash-verified delivery-copy pointer
  handbook-package.json      final delivery manifest
```

The handbook package includes:

- syllabus-based topic structure;
- student-friendly explanations reviewed from per-topic source jobs;
- original worked examples with steps and answer checkpoints;
- per-topic `visual_decision` records, including `text-ok` reasons when a separate visual would not add learning value;
- reviewed exact-SVG/Kroki/image assets where they fit, plus pending complex-infographic briefs;
- final revision questions;
- printable HTML plus a PDF exported only after current-HTML LLM approval.

Before presenting an output as final, run
`python scripts/run_runtime.py -- review --out <output-dir>`. This rerenders HTML and
prepares `final-review-packet.json`, but it does not inspect or approve the
handbook and it does not generate PDF. Validation is not enough by itself: the
LLM must personally open the complete current HTML and review what a student
will see. A route with only candidate evidence is not delivery-grade.
A base run with pending `concepts/concept_jobs.json` entries is a draft until
reviewed concept explanations are imported.

The user's LLM/Agent must perform a visible HTML review-and-repair loop before
handoff: compare the topic sequence and concept explanations with the syllabus
outline, inspect visuals and responsive layout, and repair every fixable issue.
After each repair it must rerender and personally inspect the new HTML again.
The project must not present "the Skill generated it", Python inspection, or a
passing gate as a substitute. Record approval and the exact HTML SHA-256 in
`agent-product-review.json`. Then run
`python scripts/run_runtime.py -- export-pdf --out <output-dir>`. The export command
rejects missing, non-LLM, stale, incomplete, or revisions-required approval.
It exports to a temporary candidate, blocks promotion on hard PDF defects, and
only then updates `current-pdf.json`; older PDFs remain historical rather than
being deleted or selected by modification time. To create a controlled final
copy, add `--delivery-dir <directory>`. A differing destination is never
overwritten unless `--supersede-existing` is explicitly supplied to archive it
first.

The first response of a handbook run is a blocking preflight form, not a
generation prompt. It must show fixed choices for external visual capability,
supported board/level, support language, explanation style, workflow mode, batch
scope, and output directory in one message. The user replies with `key=value`
fields; incomplete or invalid fields keep the run blocked. The Agent must not
download sources, discover providers, split the syllabus, write content, choose
visuals, render HTML, or generate PDF until the form is complete. A configured
image provider is not proof that the user supplied an external visual route.

## Preview

### OxfordAQA IGCSE Biology

<p align="center">
  <img src="docs/assets/v060-oxfordaqa-biology-p12.jpg" alt="OxfordAQA IGCSE Biology photosynthesis page" width="31%">
  <img src="docs/assets/v060-oxfordaqa-biology-p21.jpg" alt="OxfordAQA IGCSE Biology carbon cycle page" width="31%">
  <img src="docs/assets/v060-oxfordaqa-biology-p28.jpg" alt="OxfordAQA IGCSE Biology thermoregulation page" width="31%">
</p>

### CAIE AS Physics

<p align="center">
  <img src="docs/assets/v060-caie-physics-p10.jpg" alt="CAIE AS Physics projectile motion page" width="31%">
  <img src="docs/assets/v060-caie-physics-p25.jpg" alt="CAIE AS Physics stationary wave apparatus page" width="31%">
  <img src="docs/assets/v060-caie-physics-p30.jpg" alt="CAIE AS Physics internal resistance circuit page" width="31%">
</p>

### College Board AP Chemistry

<p align="center">
  <img src="docs/assets/v060-ap-chemistry-p11.jpg" alt="AP Chemistry photoelectron spectrum page" width="31%">
  <img src="docs/assets/v060-ap-chemistry-p43.jpg" alt="AP Chemistry titration page" width="31%">
  <img src="docs/assets/v060-ap-chemistry-p91.jpg" alt="AP Chemistry galvanic cell page" width="31%">
</p>

### Pearson Edexcel International A Level Mathematics

<p align="center">
  <img src="docs/assets/v060-edexcel-mathematics-p52.jpg" alt="Edexcel IAL Mathematics exponential model page" width="31%">
  <img src="docs/assets/v060-edexcel-mathematics-p74.jpg" alt="Edexcel IAL Mathematics mechanics model page" width="31%">
  <img src="docs/assets/v060-edexcel-mathematics-p99.jpg" alt="Edexcel IAL Mathematics conditional probability page" width="31%">
</p>

These are pages from four independently reviewed, current handbooks. They
demonstrate layout and visual teaching quality; they do not limit the supported
subjects or certify every subject in the source catalogues.

## Supported Curriculum Sources

| Curriculum route | AQA | Edexcel | CAIE | College Board |
|---|---:|---:|---:|---:|
| UK GCSE | yes | yes | no | no |
| International GCSE | yes | yes | yes | no |
| A-Level | UK / International | UK / International | Cambridge International | no |
| AP | no | no | no | yes |
| OCR, WJEC/Eduqas, CCEA, and other UK boards | no | no | no | no |

The current release supports automatic source acquisition for the routes shown
above. Before discovery, the Agent must explicitly record the course market.
For AQA and Edexcel that selection chooses the matching official source route.
For CAIE it records whether the request is for an International or UK-centre
context while using the same official Cambridge International catalogue. This
is a source-workflow support claim, not a claim that every subject already has
a final-ready handbook sample. Other systems have no automatic acquisition
support; manual imports remain unverified and may encounter unknown
compatibility errors.

## Visuals And Writing Styles

A useful handbook cannot be text-only. The workflow has two passes:

1. Build topic explanations and worked examples from the official syllabus.
2. Decide which topics or examples need visual explanation.

The host LLM/Agent decides whether each topic or worked example needs text only,
an exact SVG candidate, or a richer infographic. SVG is allowed only when the
visual meaning is fully carried by exact geometry, axes, labels, simple tables,
or simple flows; the Writer must mark `svg_fit: "exact"`, and the asset must be
reviewed or approved before final delivery. Richer items become visual briefs:
lab apparatus, complex geometry, circuits, economics scenes, or text-heavy
educational infographics.

When no callable image model is available, complex visuals remain queued in
`images/infographic_jobs.json` and `images/infographic_jobs.md`. The Python
framework does not create local deterministic SVG stand-ins for those briefs.
Kroki or SVG outputs are treated as reviewed exact-fit assets, not substitutes
for dense infographics.

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

Design inspiration: the anti-template wording check is adapted from
`qiaomu-novel-generator`. The SVG review contract follows the general idea of a
figure contract: define the claim, labels, source evidence, and review risk
before approving an asset. This is documentation guidance, not a runtime
dependency.

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

## Release Notes

Version-by-version update notes live in
[GitHub Releases](https://github.com/mianbaofang/exam-revision-handbook/releases)
and [CHANGELOG.md](CHANGELOG.md). The README stays focused on what the Skill
does and how users run it.

## Developer Quick Start

Two operating modes exist. Pick the one that matches your environment.

### Mode 1: Skill host (preferred, for production handbooks)

Point your Agent runtime (OpenClaw, Hermes, Claude with subagents, etc.) at
the repository root. The root `SKILL.md` is the only authoritative entry:

```text
https://github.com/mianbaofang/exam-revision-handbook
```

The Agent runtime follows the lightweight Skill workflow:

- **Analyst role**: reads the official syllabus evidence and writes the
  authoritative `syllabus-outline.json` (topic titles, exam points, source
  snippets). Python evidence extraction is a hint, not a substitute.
- **Writer role**: writes concept explanations, worked examples,
  study-roadmap text, and per-topic `visual_decision` records.
- **Reviewer role**: personally opens the rendered HTML, compares it with the
  source evidence and outline, sends problems back for rewriting and rerendering,
  and writes hash-bound `agent-product-review.json` only when the current HTML passes.

These are role labels. They may be separate agents in a runtime that supports
that, but the Skill does not require a project-manager agent, a mandatory
quality-inspector agent, or a release-certification workflow.

Re-runs within the same session are idempotent: re-generated topics overwrite
existing handbook-package.json, validation.json, and visual-manifest.json so the
Skill can keep iterating until the Reviewer has inspected the visible handbook.

### Mode 2: Packaged CLI (no Skill host, evidence package only)

The official CLI run prepares source evidence for the host LLM workflow. It does not split topics, write teaching content, or render the handbook:

```bash
python scripts/doctor.py
python scripts/run_runtime.py -- generate \
  --query chemistry \
  --level igcse \
  --out ./outputs/chemistry-9202
```

Windows PowerShell:

```powershell
python scripts\doctor.py
python scripts\run_runtime.py -- generate --query chemistry --level igcse --out .\outputs\chemistry-9202
```

The CLI is for fetching official source material and writing `qualification.json`, `syllabus-evidence.json`, and `source/`. A real teaching handbook still requires Mode 1: an LLM Analyst outline, Writer-authored concepts/visual decisions, rendered HTML, repeated visible LLM review until approval, and gated PDF export afterward.

GitHub `main`, its `v0.7.1` tag, and the attached Skill ZIP are the same current
standard Skill release. There is no separate source edition or install
edition. Contributors changing its Python engine can use
`pip install -e ".[dev]"`; the ZIP runs the pinned engine from
`assets/runtime/` in an isolated user cache.

Checks:

```bash
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
```

## Mechanical Quality Metrics

Version 0.4+ includes a quality metrics system for repeatable diagnostics such
as clarity, example relevance, visual helpfulness, and usability signals. These
scores can identify material that needs attention, but they cannot certify
subject accuracy or replace the complete visible review by the active LLM.

### Measuring Quality

```python
from intl_exam_guide.quality import QualityGate

gate = QualityGate()

# Check handbook quality
report = gate.check(
    concepts=[{"topic": "Photosynthesis", "text": "...", "keywords": [...]}],
    examples=[{"topic": "Photosynthesis", "text": "Step 1: ..."}],
    visuals=[{"topic": "Photosynthesis", "type": "flowchart", "prompt": "..."}],
    practice_items=[{"question": "..."}],
    subject="biology",
)

print(report.summary())

if report.passed:
    print("Mechanical quality thresholds met; LLM review is still required")
else:
    print("Mechanical quality thresholds not met")
    for issue in report.issues:
        print(f"  - {issue}")
```

### Quality Metrics Measured

| Metric | Threshold | What It Measures |
|--------|-----------|------------------|
| Concept Clarity | 0.85 | Are concepts explained clearly with examples? |
| Example Relevance | 0.90 | Do examples actually demonstrate the concepts? |
| Visual Helpfulness | 0.80 | Do visuals aid understanding (not decoration)? |
| Overall Usability | 0.85 | Can students actually use this to learn? |

See [docs/ACCURACY_POLICY.md](docs/ACCURACY_POLICY.md) for the boundary between
mechanical diagnostics and handbook approval.

## Repository Layout

```text
SKILL.md         the single authoritative Agent entry
agents/          platform-facing Skill metadata
references/      complete workflow, artifact, provider, and runtime contracts
assets/runtime/  pinned Python engine Wheel and integrity lock
evals/           trigger, workflow, migration, and output parity fixtures
reports/         governed Skill and migration evidence
security/        runtime permission and network policy
skill_atlas/     generated routing and maintenance metadata
scripts/         runtime adapters, import helpers, and repository tooling
src/intl_exam_guide/
  providers/      exam-board source access and parsing
  parsing/        PDF text extraction
  planning/       topic, example, and visual-brief planning
  rendering/      HTML and PDF rendering
  validation/     completeness checks
  quality/        teaching effectiveness metrics
docs/             project details, policies, examples, and preview pages
tests/            tests and regression samples
```

See [PROJECT.md](PROJECT.md) before maintaining or handing off the repository.

## Safety And Source Policy

Do not commit downloaded official PDFs, past papers, mark schemes, or copied exam
questions. Public samples should use original explanations, original practice
cards, and the minimum source information needed for review.

Families should have subject teachers or syllabus-aware adults review deeper
worked examples before using generated guides as final exam preparation.

## Acknowledgements

This project builds on public exam-board materials, open-source tooling, and agent workflow patterns:

- Official public syllabus pages and PDFs from OxfordAQA / Oxford International AQA, Pearson Edexcel, and Cambridge International.
- PDF and document processing: `pypdf` and Microsoft [`markitdown`](https://github.com/microsoft/markitdown) when available in the host workflow.
- Rendering and validation tooling: Playwright, pytest, pytest-cov, Ruff, and mypy.
- Demo and visual workflow: HyperFrames, generated preview assets, and image-generation routes supplied by the user or host runtime.
- Writing-quality guidance: anti-template wording checks inspired by `qiaomu-novel-generator` style rules.

Exam-board names are used for source identification only. This project is not endorsed by, affiliated with, or certified by those exam boards.

See [DISCLAIMER.md](DISCLAIMER.md) and [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for the full non-affiliation, copyright, and attribution notes.

## Status

Current Skill version: `v0.7.1`. The Skill is public-ready as a framework for
source-backed handbook generation. An individual handbook is final-ready only
after its own complete LLM HTML review is recorded in
`agent-product-review.json` and `review-ledger/`, the exact HTML passes the hash
gate, `current-pdf.json` points to a technically valid hash-bound export, and
any release claim is supported by the delivery matrix and release evidence.

## Author

Ethan <ethan.zl@hotmail.com>

## License

MIT.
