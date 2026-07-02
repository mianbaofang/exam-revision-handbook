---
name: igcse-a-level-revision-guide
description: Use when generating image-rich International GCSE or International AS-A-level revision handbooks from official syllabus/specification sources, with AQA, Edexcel, and CAIE support.
---

# IGCSE & A-Level AI Revision Guide Skill

Use this skill when the user asks for an International GCSE or International
AS-A-level subject study/revision guide. Treat IGCSE as a user-facing alias for
International GCSE, but use the full qualification names in generated
documentation.

Before generating a guide, read `references/revision_guide_spec.md`. That file
defines the handbook contract inherited from the original IGCSE revision-guide
Skill: the output must be a student study/revision handbook with HTML, PDF,
modular sections, visual assets, worked examples, and validation. Do not turn
the output into project documentation.

Current exam-board support:

- AQA: implemented through OxfordAQA / Oxford International AQA public pages,
  including catalogue discovery. In Chinese user requests, treat "AQA" as this
  international AQA route unless the user explicitly gives a UK AQA page.
- Edexcel: subject-name candidate discovery for common official Pearson Edexcel
  International GCSE / International AS-A-level page patterns, plus official
  subject-page URL or direct specification PDF URL fallback.
- CAIE: official Cambridge International subject-index candidate discovery,
  plus official subject-page URL or direct syllabus PDF URL fallback. If a CAIE
  page lists multiple syllabus year ranges, ask for `exam_year` and use the
  range containing that year.

Do not run the AQA/OxfordAQA provider against Edexcel, CAIE, or generic UK AQA
pages. If the user says only "AQA" with no UK AQA URL, treat it as the
China-facing International GCSE / International AS-A-level AQA route. Do not
claim full subject-catalogue crawling for Edexcel. When Edexcel or CAIE cannot
uniquely identify a subject from exam board, level, subject, and code, return the
matching official candidates and ask the user to choose one. Do not silently pick
a likely route.

## Operational Gates

- STOP: preflight incomplete. If subject/provider, required exam year, output
  language, explanation style, or infographic capability choice is missing, ask
  only for the missing items and do not download or write the handbook yet.
- CHECKPOINT: official candidate selected. Continue only when discovery returns
  one official subject route or the user has chosen from the candidate list.
- STOP: no official candidate. Ask for an official subject-page URL, direct
  specification/syllabus PDF URL, or subject code. Do not switch boards, use an
  AQA syllabus, or guess a likely URL.
- CHECKPOINT: base handbook generated. After `guide-plan.json` and
  `validation.json` exist, inspect `concepts/concept_jobs.json` and report the
  pending concept-explanation count before starting image-generation or import
  workflow.
- STOP: concept explanations unreviewed. If
  `validation.json.review_summary.pending_concept_explanations` is nonzero,
  write source-bound explanations from `concepts/concept_jobs.json`, import them
  with `scripts/import_concept_explanations.py`, and rerun validation/review
  before presenting the handbook as final.
- STOP: no callable image route. If the user names GPT Image, Qwen, SenseNova,
  or another image model but there is no installed Skill, script, custom
  provider configuration, or matching asset directory, keep `prompt-queue`,
  write pending visual jobs, and do not create complex SVG stand-ins.
- CHECKPOINT: quality passed. Present the guide as usable only after validation
  has no `error` issues and the output includes detailed units, worked examples,
  source snippets, visual briefs, `sections/`, and `images/`.
- STOP: multi-agent workflow not separated. When the Agent runtime supports
  subagents or fresh child contexts, dispatch the run as three roles:
  syllabus/outline analyst, handbook writer, and independent final reviewer.
  Use `agent-orchestration.json` as the required role contract. If no
  independent Agent/LLM context is available for the final reviewer, keep the
  output at review-ready or draft and do not present it as final-ready.
- CHECKPOINT: final Agent review passed. Before presenting a generated handbook
  as final, run `python -m intl_exam_guide review --out <output-dir>`, read
  `final-review-packet.json`, and perform an Agent/LLM review over the rendered
  excerpt, validation issues, source/topic summary, and visual status.
  Validation is not enough by itself. Obey the packet's
  `agent_self_review.must_not_present_as_final` flag. If the Agent cannot
  honestly answer the review questions, present the output as a draft or blocked
  run, not as final.
- STOP: final review is only a gate report. The user's active LLM/Agent must
  read the generated handbook as a final product, compare it against the
  official syllabus outline, inspect visible HTML/PDF pages and visuals, and
  repair fixable issues before handoff. Do not treat "the Skill generated it"
  or "validation returned ready" as proof that the result is student-usable.
  If the review finds mismatched topic explanations, duplicated mastery text,
  unsuitable/repeated visuals, missing glossary support, PDF layout issues, or
  pending concept/image work, fix the content/assets, rerender, and rerun final
  review before giving the user the file.
- STOP: product-review evidence missing. After the active LLM/Agent performs
  that final product review, write `agent-product-review.json` with the
  inspected PDF pages, syllabus-outline comparison, visual/glossary checks,
  fixable issues, repairs made, and final decision. Without complete
  `agent-product-review.json` evidence, the output remains review-ready or
  draft even when validation and `final-review-packet.json` look clean.
- STOP: reviewer is not independent. The final reviewer role in
  `agent-orchestration.json` must be separate from the syllabus/outline analyst
  and handbook writer roles. A writer self-check can help, but it does not
  satisfy final review by itself.
- STOP: self-review found fixable problems. If the Agent/LLM review notices
  duplicated mastery text, a worked example that answers a different topic,
  repeated or unsuitable visuals, blank PDF pages, unresolved image jobs, or
  student-facing language/style mismatch, fix the generation logic or imported
  assets first, regenerate or rerender the handbook, and run the final review
  again. Do not hand off a guide merely because validation or a delivery gate
  says `ready`.
- CHECKPOINT: release evidence classified. For project maintenance or release
  tasks, classify claims as `candidate`, `draft`, `final-ready`, or
  `certified`. Candidate routes are not delivery-grade. Do not call a route
  certified unless a `docs/release-evidence/` manifest records current evidence
  and reviewer approval.

When Edexcel or CAIE discovery returns more than one official match, show the
choices in this shape and wait:

```text
Official candidates found:
1. board:
   level:
   subject:
   code:
   official_url:
   spec_pdf_url:
   why_matched:

Please choose a number, or provide the official subject page / syllabus PDF URL.
```

Provider resolution commands from a full repository checkout:

```bash
# AQA has catalogue discovery.
python -m intl_exam_guide discover --provider oxfordaqa

# Edexcel and CAIE are URL-first / subject-candidate routes, not full crawlers.
# Use a scratch output directory to verify whether the provider resolves one
# official route or returns an ambiguity/error message to show the user.
python -m intl_exam_guide generate --provider pearson --query "Accounting" --level igcse --language en --explanation-style friendly --out ./outputs/_candidate-check-edexcel --skip-pdf
python -m intl_exam_guide generate --provider cambridge --query "Accounting 0452" --level igcse --exam-year 2027 --language en --explanation-style friendly --out ./outputs/_candidate-check-caie --skip-pdf
```

If those checks create a scratch guide only for route confirmation, do not
present it as the final handbook. Re-run with the user's confirmed language,
style, output directory, and PDF setting after the official route is selected.

## User-Facing Use

The end user should not need to run Python commands. They can install the skill
by giving this link to OpenClaw, Hermes, or another Skill-compatible Agent:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

After installation, plain-language requests are enough, for example:

```text
帮我生成 AQA Chemistry International GCSE 复习手册，并导出 PDF。
帮我生成 Edexcel Accounting International GCSE 复习手册，附中文专业词对照表。
帮我生成 CAIE IGCSE Economics 2027 考试用复习手册，附日语专业词对照表。
```

Do not start generation immediately after a broad request. Run the preflight
choice step first.

## Required Preflight Choices

Before downloading a specification or generating content, ask for and confirm
these choices if the user did not already provide them:

1. **Subject choice**: exam board, qualification level, subject, and code if
   known. The user may only know the exam board and subject. First resolve an
   official candidate yourself. If the provider finds several matching official
   routes, show the choices and wait for the user to pick one. Official
   subject-page URLs and direct specification/syllabus PDF URLs are accepted as
   precise overrides.
2. **Exam year when needed**: Cambridge subject pages often expose multiple
   syllabus ranges. If more than one range is available, ask for the student's
   exam year before selecting a syllabus.
3. **Term-support language**: the handbook body, worked examples, labels, and
   diagram text stay in English because the exam is in English. If the user asks
   for Chinese, Traditional Chinese, Japanese, or another support language, add
   a 30-50 item professional glossary mapping that language to the official
   English terms. Do not generate a fully translated handbook body, and do not
   render mixed `Chinese / English` labels throughout the guide; the bilingual
   content belongs in the glossary table.
4. **Explanation style**: ask how the knowledge points and examples should read:
   `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`.
5. **Infographic capability**: ask whether the user has a callable infographic
   or image-generation route available for this run. This is a required
   yes/no preflight question, not an image-model menu. If the user says yes,
   ask which route they want to use: installed image-generation Skill, custom
   API with model name + base URL/endpoint + API-key environment variable name,
   existing asset directory, or a project script. If the user says no, explain
   that built-in deterministic SVG/scientific-vector visuals may be incomplete
   for complex infographics, then ask whether to continue with a draft that
   marks complex visuals as pending.
Do not force the user to choose a specific image model before the base guide is
generated. Do not show an image-model choice menu that mixes SVG, prompt queue,
and recommended model names. The required preflight choices are
subject/provider, required exam year, term-support language, explanation style, and
infographic capability availability.
Do not ask the user to choose an image model before the base guide is generated.

The recommended complex-image models are GPT Image 2.0, Qwen Image 2.0 Pro, and
SenseNova U1 Fast because they tend to handle text+diagram educational
infographics better than generic art models. These are recommendations only.
Do not imply every user can call them by default.

When no callable image model is available, do not treat every visual as a rough
generic SVG. The visual stack is automatic: exact simple diagrams use local
SVG/scientific-vector output; medium-complexity professional diagrams such as
flows, hierarchies, timelines, concept maps, and relationship diagrams use the
built-in Kroki professional diagram renderer; high-density text+diagram
infographics remain external-image jobs. For chart-like or rule-driven visuals, use the internal
scientific-vector fallback described in
`references/scientific_vector_fallback.md`: number lines, axes, probability
trees, function graphs, statistics charts, rate curves, pH scales, energy
profiles, and simple labelled geometry should be rendered as source-bound,
editable SVG where possible. This is not a user-facing image model choice.
Complex infographics still require an external model, script, imported asset, or
reviewed designer workflow.

After the guide plan is built, inspect `validation.json.review_summary` or
`images/visual_manifest.json` and tell the user how many complex infographic
briefs were found. Then the user may provide or confirm their own
image-generation model, API, Skill, script, designer workflow, or generated
image directory. If a callable route exists, the Agent should run it and then
import or attach the reviewed outputs automatically; do not make the user move
files by hand. If they do not provide a callable route or assets, leave complex
items as pending visual jobs, show the `visual_###` IDs that need generation,
and present the handbook as draft-with-pending-images rather than final.

## Callable Image Capability Gate

Before using any real image model name after the base guide run, verify one of
these concrete capabilities:

- a named image-generation Skill is installed and the user explicitly asked to
  use it for this run; the Agent may call that Skill and then import/attach the
  generated files;
- a script path exists and is designed to generate or import the pending
  `visual_manifest.json` entries;
- an asset directory exists with generated image files matching the visual IDs;
- `--image-provider custom` has model name, endpoint URL, and API-key
  environment variable name, and the environment variable is set.

If none of those checks passes, do not choose a model. Keep the base guide on
`prompt-queue`, write `images/infographic_jobs.json` and
`images/infographic_jobs.md`, and leave complex infographic slots pending until
reviewed raster assets are imported.
Never ask the user to paste a raw API key into chat or commit one to the
repository.

Handle repository setup, CLI execution, validation checks, and PDF export as the
Agent. Do not ask the user to install dependencies unless the local environment
is genuinely missing the required runtime and cannot proceed.

## Core Contract

This skill is a cross-subject framework, not a Mathematics, Chemistry, or
Economics template. Do not hard-code one subject's examples, diagrams, topic
counts, tone, or revision structure into another subject.
Within a supported board, do not maintain a per-subject allowlist. If the
official qualification page and specification PDF can be discovered or supplied,
run the same source-bound generation pipeline. Specialist subject profiles may
improve examples and visual decisions; subjects without a specialist profile
must fall back to generic source-bound examples instead of borrowing another
subject's template.
Do not maintain per-subject hard-coded concept-explanation libraries. The base
generator may write source-bound draft prompts, but final student-facing concept
explanations must be written in a second LLM/Agent pass from the current
`topic_title`, `student_title`, and `source_points` in `concepts/concept_jobs.json`.

The end product is a study/revision handbook package. A valid run writes:

- `guide.html`;
- `guide.pdf` when PDF export is available;
- `sections/` with modular handbook source fragments;
- `images/` with deterministic SVG drafts or reviewed infographic assets;
- `concepts/` with concept-writing jobs and reviewed concept explanations;
- `guide-plan.json`;
- `qualification.json`;
- `validation.json`;
- `final-review-packet.json` after the review command has run;
- `handbook-package.json`.

The required generation logic is:

1. Find the public qualification page and course specification PDF.
2. Use the web page only as discovery metadata; use the downloaded PDF as the
   source of truth for detailed syllabus content.
3. Parse the detailed subject content into teachable knowledge units. If the PDF
   has specification references such as `N1`, `A13`, `G20`, `S18`, or equivalent
   subject codes, use those references as the unit level. If a subject has no
   codes, use the lowest reliable section/subsection level available in the PDF.
4. Generate source-bound study-note drafts and original worked examples for each unit.
   Each worked example must include a real question prompt, a solve-it-first
   frame, public solution steps, final answer/checkpoints, and source anchors.
5. Write one concept-explanation job per topic under `concepts/`. The job must
   include the current topic title, student-facing title, draft text, source
   points, source pages, and a constrained task.
6. Run the LLM/Agent concept-writing pass before finalizing student-facing
   topic guides. Each topic needs 2-3 direct concept explanations that say what
   the concept is, what relationship or boundary it describes, and why it is
   central to this syllabus point. Do not write procedural mastery checklists
   such as "be able to identify / operate / check".
7. Run the anti-template language pass before finalizing student-facing
   explanation and practice text. Remove safe formulaic transitions such as
   `In conclusion`, `Overall`, `总之`, and `值得注意的是`; if a phrase still reads
   like generic AI prose, keep it as a validation warning for review instead of
   hiding it.
8. Run a second visual-needs pass over each knowledge unit and worked example.
   Decide whether text is enough, local deterministic SVG is enough, built-in
   Kroki professional rendering is appropriate, or a richer external
   infographic/image model is needed. Do not create a visual merely because a
   topic could be illustrated; create one only when the concept, graph, flow, or
   worked example becomes materially clearer with that visual.
9. Render the guide to HTML/PDF only after the content, examples, concept
   explanations, visual briefs, and source checks are present.

For student-facing guides, do not produce a text-only template. During visual
planning:

- `prompt-queue` is the default route for complex visuals when no callable image
  capability exists;
- `deterministic-svg` for exact editable diagrams such as axes, curves, charts,
  pH scales, particle layouts, motion graphs, force arrows, and simple geometry;
- built-in Kroki professional diagrams for medium-complexity flows, hierarchies,
  timelines, source-to-ledger routes, relationship maps, and concept maps;
- GPT Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are recommended
  external options for text+diagram educational infographics;
- `custom` if the user has another provider, URL, model name, and key env var.

These recommended model names are not CLI providers. Do not pass them as
`--image-provider` values to the base generator. Use `prompt-queue` for the
guide, then run or import external images only after the callable gate above
passes.

If the user has not chosen the subject, required exam year, term-support
language, and explanation style, stop and ask. Ask whether a callable external
infographic route exists before generation, but do not ask the user to choose
between local SVG and Kroki; that routing is automatic. Do not claim that complex infographics have been finalized until a
callable image route has produced reviewed image assets; new outputs must not
use generic SVG as a substitute for complex infographics.

The public repository does not include a fixed built-in image-generation router.
That does not mean image work must be manual. If the user has a callable model,
API, Skill, script, or designer workflow, the Agent should run that capability
after the base handbook is generated, save the reviewed files, and use
`scripts/import_infographic_assets.py` when the files need to be copied into the
guide package before finalizing HTML/PDF.

## Repository Access

This skill may be installed from the repository's `skill/` directory, which
contains the Agent instructions but not the Python engine. Before running the
generator, check whether the current workspace has `pyproject.toml` and
`src/intl_exam_guide`.

If the full repository is not available, clone or otherwise fetch this public
repository into a workspace directory, then run commands from that checkout:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide.git
```

## Maintenance And Audit Closure

Use this section only when the user asks to update, audit, or release the
generator/Skill itself. Do not run maintenance steps during an ordinary handbook
generation request.

Final-round P3 closure requires these checks before calling the project ready:

- `visual_routing.py` has a dedicated test file and direct coverage for
  `build_visual_brief`, provider selection, subject-specific infographic routes,
  SVG routes, and text-only fallbacks.
- `validation/checks.py` branch coverage is above 90% in its dedicated test run,
  with direct tests for `validate_plan`, custom image-provider success/failure,
  Chinese placeholder checks, image manifest edge cases, review-summary asset
  counts, `is_contents_or_index_snippet`, and all localized topic marker groups.
- `subject_profiles.py` dedicated coverage reaches 100%, including declared
  subject routing, ambiguous science routing, Mathematics prefix routing, and
  Economics/Accounting source-text fallbacks. Accounting source-text must be
  checked before broader Economics text so `bank reconciliation` does not route
  as Economics.
- Chinese visual OR aliases are tested as standalone triggers, including
  `accounting process` and `neutralisation`; weak assertions pin full messages
  or exact return values, not only severity/truthiness.
- Public release copy, especially `docs/index.html` detail cards, reflects the
  actual release changes instead of stale prior-round text.

Run at least these focused checks after such maintenance:

```bash
python -m pytest tests/test_visual_routing.py tests/test_visual_routing_benchmark.py -q
python -m pytest tests/test_subject_profiles.py tests/test_localization.py tests/test_validation_checks.py -q
python -m pytest tests/test_visual_routing.py tests/test_visual_routing_benchmark.py --cov=intl_exam_guide.planning.visual_routing --cov-report=term-missing -q
python -m pytest tests/test_subject_profiles.py --cov=intl_exam_guide.planning.subject_profiles --cov-report=term-missing -q
python -m pytest tests/test_validation_checks.py --cov=intl_exam_guide.validation.checks --cov-report=term-missing -q
```

Before release or handoff, also run the full project checks from
`docs/PROJECT_OPERATIONS.md`: `python -m pytest --cov
--cov-report=term-missing -q`, `python -m ruff check .`, `python -m mypy`,
`python -m compileall -q src tests scripts`, `python scripts/scan_for_raw_keys.py
. ./outputs`, and `git diff --check`. For functional releases, record fresh demo
evidence in `CHANGELOG.md` or the GitHub Release notes before publishing. For
v0.4+ release claims above `candidate`, also record the concise manifest under
`docs/release-evidence/`; do not commit generated output folders as evidence.

## Workflow

1. Confirm the required preflight choices: subject/provider, required exam
   year, term-support language, and explanation style. Do not ask for an image model
   at this stage.
2. Read `references/revision_guide_spec.md`.
3. For AQA, read `references/oxfordaqa.md` because the implemented AQA route is
   based on OxfordAQA / Oxford International AQA pages.
4. For Edexcel or CAIE, first try official
   candidate discovery from the user's subject request. If more than one
   official candidate matches, return the choices and wait. If none matches,
   ask for an official subject-page URL, direct specification/syllabus PDF URL,
   or subject code. Do not silently switch to another board or reuse an AQA
   syllabus.
5. Run the generator CLI from the repository root with the confirmed
   `--language`, `--explanation-style`, optional `--exam-year`, and optional
   `--image-provider`. Confirm that detailed PDF
   syllabus units were extracted; do not accept broad web summary topics as the
   final guide structure when the PDF contains finer subject content.
6. Check `validation.json` before presenting the guide. A usable student guide
   needs detailed units, worked examples, source snippets, visual briefs,
   `sections/`, and `images/`; a guide with only broad topic headings is a
   failed draft.
7. If `pending_concept_explanations` is nonzero, use
   `concepts/concept_jobs.json` as the source-bound brief for the LLM/Agent
   concept-writing pass, save the reviewed output as
   `concepts/concept_explanations.json`, import it with
   `scripts/import_concept_explanations.py`, and rerun validation.
8. Report how many complex infographic briefs were found. If the user provides
   a generation/import method, use it after the callable gate passes. If not,
   report the pending `visual_###` jobs and present the handbook as draft with
   pending visual assets.
9. If the guide will be used with children, require subject-specialist review for
   worked examples before treating it as final exam preparation material.
10. Preserve the visual and narrative learning layer: after the base topic guide
   and practice items are generated, analyze which knowledge points or examples
   need visual explanation. Use deterministic SVG for simple diagrams. For
   complex infographic needs, create source-bound briefs and pending visual jobs
   unless a callable route or reviewed raster asset is available.
   When the visual is an exact chart/axis/curve/simple geometry case, read
   `references/scientific_vector_fallback.md` and keep the SVG editable,
   source-bound, and recorded as a scientific-vector fallback in the manifest.

## Commands

From a full repository checkout, install the package first when possible:

```bash
python -m pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

If the package is not installed and the Agent only needs a local run, set
`PYTHONPATH` for the current shell:

```powershell
$env:PYTHONPATH='src'; python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

Use `--skip-pdf` only when no local browser or Playwright runtime is available.

## Anti-Patterns

- Do not ask for an image model during preflight.
- Do not show `gpt-image-2`, `qwen-image-pro`, `sensenova-u1-fast`,
  `deterministic-svg`, and `prompt-queue` as one user-facing model menu.
- Do not treat a recommended model name as a callable capability.
- Do not use AQA syllabus content when the user asked for Edexcel or CAIE.
- Do not accept a guide with only broad topic headings, missing worked examples,
  or missing visual briefs.
- Do not treat draft "what to master" prompts as final concept explanations.
- Do not add one subject's concept rules to the shared generator to fix another
  subject's output; fix the source-bound concept job and review flow instead.
- Do not present generic SVG stand-ins for complex infographics as reviewed
  teaching diagrams.
- Do not generate a translated Chinese/Japanese/etc. handbook body. Keep the
  handbook body English and put user-language support in the professional terms
  glossary.
- Do not leave obvious AI-template transitions in student-facing explanations
  or practice cards when a concrete sentence will do.

## Safety Rules

- Do not copy official past-paper questions, mark schemes, or large passages of
  specification/syllabus text into generated public examples.
- Keep the official page URL, specification URL, and PDF hash in every output.
- Treat the generated guide as incomplete if topic extraction, assessment
  extraction, source download, or HTML validation fails.
- Do not invent exam claims. If a topic needs deeper explanation, keep it inside
  the extracted syllabus text and mark it for review.
- Use AI image generation only as an optional illustration layer. Prefer
  deterministic SVG concept maps for simple structures. If an AI image model is
  used, record the model, prompt, source topic, caption, and review status; never
  let an illustration introduce unsupported exam claims.
