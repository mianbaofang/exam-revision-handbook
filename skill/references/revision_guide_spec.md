# Revision Guide Handbook Spec

This repository is an open-source version of the original IGCSE revision-guide
Skill. Its first job is to generate a student-facing study and revision
handbook, not a project report.

## Output Package

Each generated handbook must include:

- `guide.html`: one print-friendly UTF-8 HTML file.
- `guide.pdf`: A4 PDF export when a browser runtime is available.
- `sections/`: modular source fragments used to assemble the handbook.
- `images/`: deterministic SVG drafts and reviewed infographic assets.
- `concepts/`: source-bound concept-writing jobs and reviewed concept
  explanations imported before final delivery.
- `guide-plan.json`: structured topic guides, worked examples, and visual briefs.
- `qualification.json`: source metadata extracted from the official provider.
- `validation.json`: machine-readable quality checks.
- `final-review-packet.json`: Agent/LLM self-review packet written by the
  `review` command before final presentation.
- `handbook-package.json`: manifest for sections and image assets.

Downloaded specification PDFs and extracted text belong under `source/` and must
not be committed to the repository.

Release evidence is separate from the generated handbook package. For v0.4+
maintenance or release work, use these status words:

- `candidate`: route evidence exists, but it is not delivery-grade.
- `draft`: a fresh output exists, but concepts, visuals, PDF/export,
  validation, or Agent self-review still blocks final handoff.
- `final-ready`: current evidence passes validation, final review, concept
  status, visual status, and package checks.
- `certified`: final-ready evidence has reviewer approval and a manifest entry
  under `docs/release-evidence/`.

Do not present candidate evidence as a final or certified handbook. A generated
output directory is not itself release evidence unless the concise manifest
records the command, git revision, validation summary, final review, asset
status, and reviewer decision when applicable.

## Required Preflight

Do not start syllabus download or handbook writing until the user has confirmed:

1. subject selection: board, qualification level, subject, and code if known.
   If the user only gives an exam board and subject, resolve official
   candidates first. If several official candidates match, return those choices
   and wait for the user to choose one instead of guessing;
2. exam year when the provider needs it, especially Cambridge pages with
   multiple syllabus year ranges;
3. term-support language: `en` for no glossary, or a support language such as
   `zh-CN`, `zh-TW`, or `ja` for a 30-50 item professional term glossary;
4. writing style: `formal`, `friendly`, `life`, `story`, `detective`, or
   `adventure`;
5. infographic capability: ask whether the user has a callable infographic or
   image-generation route available for this run. If yes, ask whether it is an
   installed image-generation Skill, a custom API with model name + base
   URL/endpoint + API-key environment variable name, an existing asset
   directory, or a project script. If no, explain that built-in deterministic
   SVG/scientific-vector visuals may be incomplete for complex infographics and
   ask whether to continue with a draft that marks complex visuals as pending.

Do not force the user to choose a specific image model during preflight. The
preflight question is whether a callable route exists and whether the user wants
to continue without one. The base handbook should run first, then the visual
pass should count how many complex infographic briefs are needed. Tell the user
that count after generation and use the confirmed route, if any. The user may
then provide final parameters or generated assets for the chosen route.
If a callable route exists, run it after the base handbook is generated and
import or attach the reviewed outputs automatically. Do not make the user move
files by hand. If they provide none, leave complex infographics as pending
visual jobs, show the `visual_###` IDs that need generation, and do not present
those slots as final reviewed visuals.

The same "base first, review before final" rule applies to concept
explanations. The base generator writes `concepts/concept_jobs.json` and
`concepts/concept_jobs.md` from the current topic title and official source
points. The Agent/LLM must then write the final student-facing concept
explanations for each job, save them as `concepts/concept_explanations.json`,
import them with `scripts/import_concept_explanations.py`, and rerun validation
before presenting the handbook as final.

Recommended external models for complex text+diagram infographics include GPT
Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast. They are recommendations,
not guaranteed built-in capabilities. For custom image providers, record the
model name, endpoint URL, and the API-key environment variable name. Do not
collect or store the raw API key.

Before any real image provider is used after the base guide run, verify at least
one concrete capability:
a named image-generation Skill installed for this run, an existing generation or
import script path, an asset directory with files matching visual IDs, or a
`custom` provider with model name, endpoint URL, API-key environment variable
name, and the environment variable actually set. If this gate is not satisfied,
do not ask the user to pick from model names and do not pass recommended model
labels to the base generator. Use `prompt-queue`, write pending visual jobs for
complex visuals, and leave the final result marked as needing image review.

## Handbook Structure

The final handbook should read like a revision book for a student. Use this
order unless the subject requires a reviewed alternative:

1. Cover.
2. How to use this handbook.
3. Study roadmap / topic map.
4. Topic guide blocks.
5. Worked examples and practice.
6. Visual explanations.
7. Exam structure and source appendix.

Each topic or knowledge unit should include:

- one-sentence essence;
- student-friendly analogy or life-scene explanation;
- 2-3 source-bound concept explanations that say what the concept is, what
  relationship or boundary it describes, and why it matters for this syllabus
  point;
- key syllabus points kept in structured review data, not as a substitute for
  concept explanation;
- at least one worked example;
- public solution steps;
- answer checkpoints;
- exam pitfall;
- source anchor back to the specification PDF.

## Writing Style

Use English for handbook labels, explanations, image prompts, topic framing,
worked examples, and diagram text because the exam is in English. If the user
selects a support language, add a professional term glossary with 30-50
user-language-to-English entries. Do not translate the whole handbook body and
do not render every label as a bilingual `Chinese / English` pair.

The tone should help teenagers stay awake and oriented:

- use life-scene explanations for abstract ideas;
- use detective-style reasoning for solution steps;
- use original adventure/anime-like framing for motivation when useful;
- avoid copying protected characters, stories, or exam-paper artwork;
- avoid long academic paragraphs and unsupported syllabus claims.
- run the anti-template language pass before finalizing student-facing text:
  remove safe formulaic transitions such as `In conclusion`, `Overall`, `总之`,
  and `值得注意的是`; leave remaining suspicious AI-style phrasing as validation
  warnings for review.

## Visual Workflow

Do not make the handbook text-only by default.

After the source-bound topic guide and examples are drafted, run a second pass
to decide which items need visuals:

- `text-ok`: no image needed;
- `svg-basic`: exact local SVG/scientific-vector output is enough, or a
  medium-complexity professional diagram can be rendered through built-in Kroki;
- `infographic`: create a source-bound visual brief and prompt queue entry;
  render it only after a reviewed raster asset exists.

Good SVG cases include number lines, simple graphs, pH scales, particle models,
energy profiles, and basic geometry. Good Kroki cases include flows,
hierarchies, timelines, relationship maps, concept maps, and source-to-ledger
routes. Good infographic cases include lab apparatus, complex geometry,
circuits, dense economics scenes, and high-design text+diagram charts.

For SVG-safe chart, axis, curve, table, and simple geometry cases, use the
scientific-vector fallback in `references/scientific_vector_fallback.md`. This
adapts the `nature-figure` idea of a figure contract to revision guides: state
the learning claim, evidence/label requirements, and review risk before drawing.
Keep SVG text editable and record `fallback_route:
scripted-scientific-vector` in `images/visual_manifest.json`. For Kroki output,
record `fallback_route: kroki-professional-diagram`. Do not use either route for
dense educational posters or rich infographics that need a real image model or
reviewed imported asset.

If a richer infographic is needed, keep a prompt queue with:

- topic title;
- focus point;
- source syllabus points;
- asset route/status: `deterministic-svg`, `external-generation-required`, or a
  reviewed generated/imported asset;
- prompt;
- review status.

Do not claim that an infographic has been generated until a callable route has
produced or imported an image and the asset is saved under `images/`.

## Source And Accuracy Rules

- Use the public qualification page for discovery metadata.
- Use the downloaded course specification PDF as the source of truth for
  detailed syllabus content.
- Prefer detailed reference codes such as `N1`, `A13`, `G20`, or `S18` when the
  PDF exposes them.
- Do not copy past-paper questions, mark schemes, or large passages from the PDF.
- Generate original worked examples that stay inside the extracted syllabus
  points.
- Do not maintain per-subject hard-coded concept-explanation libraries. The
  final concept text must be generated from the current topic title and source
  points for that run, not copied from a Mathematics, Chemistry, Economics, or
  Physics template.
- Treat a guide as incomplete if the detailed topic extraction, source snippets,
  examples, visuals, HTML, or validation report are missing.

## Validation Checklist

Before presenting a handbook, confirm:

- topic count is detailed enough for the source PDF;
- every topic has a guide block and worked example;
- every topic has a reviewed concept explanation imported from
  `concepts/concept_explanations.json`;
- `validation.json.review_summary.pending_concept_explanations` is `0`;
- every topic has a source snippet or a manual-review warning;
- visual briefs exist for visual topics;
- `sections/` and `images/` are present;
- `validation.json` has no `error` issues;
- PDF export succeeded or the user is told why it was skipped.

Then run `python -m intl_exam_guide review --out <output-dir>`, read
`final-review-packet.json`, and perform an Agent/LLM review over the rendered
excerpt, validation issues, source/topic summary, and visual status. Validation
is not enough by itself. The packet must include an `agent_self_review` verdict;
if `agent_self_review.must_not_present_as_final` is true, present the output as
a draft or blocked run, not as final. For release evidence, map a ready packet
to `final-ready` only when concepts, visuals, package files, and PDF/export
status are also current; map unresolved blockers to `draft`.

The user's active LLM/Agent must do this as a real product review, not as a
checkbox pass over machine gates. It should read the final visible handbook,
compare the topic sequence and concept explanations with the syllabus outline,
inspect diagrams/images and sampled PDF pages, and fix any repairable issue it
finds before handoff. A handbook is not final merely because the Skill
generated files or the validation summary says `ready`. Record the pass in
`agent-product-review.json`, including inspected PDF pages, syllabus-outline
comparison, visual/glossary checks, fixable issues, repairs made, unresolved
fixable issues, and final decision. Without this complete artifact, the package
must stay review-ready or draft.

The run must also preserve the multi-agent contract. When the user's Agent
runtime supports subagents or fresh child contexts, dispatch the syllabus/
outline analyst, handbook writer, and independent final reviewer as separate
roles using `agent-orchestration.json`. If that independent reviewer cannot run,
keep the output at review-ready or draft. The final reviewer must inspect the
rendered handbook and review packet, not just the writer's summary.
