---
name: igcse-a-level-revision-guide
description: Framework and LLM operations guide for International GCSE, A-Level, and College Board AP revision handbooks. Provides official-source evidence extraction, artifact contracts, curriculum visual themes, and HTML/PDF rendering. The host LLM owns syllabus analysis, writing, visual judgement, and review.
---

# IGCSE, A-Level & AP Revision Handbook Skill

## Boundary Compliance Gate

The rules in this Skill are binding execution constraints, not suggestions or
style preferences. Follow the stated sequence and artifact contracts exactly.
Do not invent shortcuts, replace an explicit LLM decision with a Python
fallback, compress official syllabus requirements for speed, merge topics only
because they share a directory heading, or allocate visuals by subject-level
quota. The handbook quality is uncontrolled if these boundaries are skipped.

Before each handoff, check that the current artifact still satisfies the Skill:
the Analyst reached independently assessable source requirements, the Writer
made a separate visual decision for every final topic, the LLM Reviewer opened
the current HTML and repaired/reviewed it until approval, and PDF export is
blocked until that approval is hash-bound to the current HTML. If a requirement
cannot be satisfied, stop at the relevant draft/review-ready state and report
the blocker. Never silently reinterpret the rule or claim completion.

## Core Rule

This Skill is a framework plus LLM operations guide. It is not an automatic content generator.

Python may discover sources, download PDFs, extract page-level evidence, validate JSON, import LLM-written artifacts, render HTML/PDF, and write mechanical manifests. Python must not decide topic splits, choose syllabus points, write teaching content, invent `mastery_summary`, decide visual need, or approve final quality.

The host LLM owns all interpretation, writing, visual judgement, and review.

Automatic official-syllabus acquisition supports the International and
UK-domestic AQA, Edexcel, and CAIE IGCSE/AS/A-Level routes, plus College Board
AP. The user must explicitly select the course market before retrieval. That
choice selects the official provider route and becomes source metadata; it must
never be inferred from a title, code, URL, provider, or prior run. Other
curriculum systems or exam boards cannot use automatic acquisition. Manual PDF
import outside the supported routes is experimental and may fail with unknown
provider, parser, extraction, or rendering compatibility errors; never describe
it as supported.

The complete runtime boundary is defined here and in
`references/revision_guide_spec.md`. Repository maintainers must also consult
the architecture decision record in the source checkout before changing scope.

## What The Skill Provides

- Four fixed source themes: OxfordAQA blue/red, Pearson Edexcel teal/blue, Cambridge red/navy, and College Board AP blue/yellow/aqua.
- An 8-module handbook framework: Cover, How to Use, Study Roadmap, optional Term Glossary, Topic Guides, Practice Workbook, Exam Structure, Revision Checklist.
- Artifact contracts for `qualification.json`, `syllabus-evidence.json`, `syllabus-outline.json`, and `concepts/concept_explanations.json`, including per-topic `visual_decision` records.
- A Python rendering engine that turns approved artifacts into named HTML and optional PDF outputs, with visual manifests that separate the Writer's recommended route from the asset actually rendered.
- A read-only delivery audit and immutable render-snapshot contract. Formal delivery uses `current-render.json` to bind one exact HTML render to its input hashes; historical files remain readable but cannot be selected by modification time for approval.

## Preflight

Confirm the minimum run inputs before downloading or writing. Ask the user directly when any of these are missing or ambiguous; do not silently choose defaults for content-bearing decisions.

### Hard First-Turn Contract

The first assistant response of every run is a **preflight form only**. It must
not contain syllabus analysis, topic suggestions, generated teaching text,
visual plans, HTML/PDF work, or a promise that generation has started. Do not
ask one open-ended question that bundles several missing values. Show every
required field and its allowed choices in the same response.

Use this fixed order:

1. `external_visual_capability`: choose `yes` (name a callable route), `no`, or
   `uncertain`. Ask exactly: **"Can you provide or enable an external image-generation Skill or tool for this run?"**
2. `board`: choose `AQA`, `Edexcel`, `CAIE`, or `College Board AP`.
3. `level`: choose `IGCSE`, `AS`, `A-Level`, or `AP`.
4. `course_market`: for AQA, Edexcel, or CAIE IGCSE/AS/A-Level, choose
   `international` or `uk-domestic`; for AP, enter `not-applicable`.
   This is a required explicit user choice. Do not infer it from a course title,
   code, URL, provider, or prior run.
5. `subject`: provide the subject name and code when known.
6. `exam_year_or_syllabus_range`: provide the exact year/range, or explicitly
   write `unknown` until the supported provider presents official candidates.
7. `term_support_language`: choose `en`, `zh-CN`, `zh-TW`, or `ja`.
8. `explanation_style`: choose exactly one of the following fixed values:
   - `formal`: exam-oriented and concise;
   - `friendly`: clear and approachable while precise;
   - `life`: everyday-life analogies while retaining exam accuracy;
   - `story`: narrative structure for connected ideas;
   - `detective`: questions, clues, and inference;
   - `adventure`: tasks and challenges that organize the explanation.
9. `workflow_mode`: choose `single-host` or `multi-agent`.
10. `batch_scope`: choose `one-handbook` or list every handbook in the batch.
11. `output_dir`: provide the exact output directory.

The first response must end with this machine-readable reply shape, not
“please tell me anything else”:

```text
external_visual_capability=<yes|no|uncertain>; image_method=<route or none>
board=<AQA|Edexcel|CAIE|College Board AP>; level=<IGCSE|AS|A-Level|AP>
course_market=<international|uk-domestic|not-applicable>
subject=<name and optional code>; exam_year_or_syllabus_range=<value|unknown>
term_support_language=<en|zh-CN|zh-TW|ja>
explanation_style=<formal|friendly|life|story|detective|adventure>
workflow_mode=<single-host|multi-agent>; batch_scope=<value>
output_dir=<absolute path>
```

The Agent must preserve answered fields and ask only for missing or invalid
fields on later turns. It must keep the run blocked until every required field
is valid. For AQA, Edexcel, and CAIE IGCSE/AS/A-Level, a missing or invalid
`course_market` blocks the run. Use the selected route only: `international`
maps to the International Provider, and `uk-domestic` maps to the UK Provider.
CAIE uses its official Cambridge International catalogue for the qualification
family selected by either market, but the chosen market remains recorded in the
source artifact. Never substitute a different market's source. A configured
`image_provider`, installed tool, prior run, or host
capability is never an answer to `external_visual_capability`. If capability is
`yes`, the named route must be invoked successfully and recorded as verified
before external visuals are planned. If it is `no` or `uncertain`, no local
image route may be silently substituted. No source download, provider
discovery, syllabus split, writing, local image generation, HTML render, or PDF
export may begin while this form is incomplete.

### Mandatory Visual Capability Gate

In the first preflight exchange, ask this question explicitly: **"Can you provide or enable an external image-generation Skill or tool for this run?"** Do this before downloading sources, writing artifacts, generating local images, or choosing a handbook visual plan.

This is a blocking question. Wait for the user's answer; do not infer it from installed tools, prior runs, model names, or the host's own capabilities. Do not silently select local generation, `prompt-queue`, or a preferred image model. Record the answer as one of: callable image Skill/tool, project script, reviewed asset directory, configured custom API, or no callable external route.

After the answer:

- callable external route: verify the named route can actually be invoked, then reserve it for source-bound `external-infographic` jobs;
- no external route: use `text-ok`, exact SVG, or Kroki only when the topic itself justifies that route, and leave `external-infographic` jobs pending;
- route claimed but not callable: treat it as unavailable until verified and ask whether to continue with pending complex visuals.

Never turn the entire handbook into locally generated images merely because the external route is absent. Visual availability does not decide learning value; the Writer's topic-specific `visual_decision` does. A missing or unconfirmed answer keeps the run at preflight.

During the first preflight exchange, explicitly offer the workflow-mode choice:

- default single-host mode: one host LLM performs Analyst, Writer, and Reviewer as separated role passes;
- optional multi-agent mode: use separate agents for those roles only if the user asks for that orchestration and the host runtime supports it.

If the user does not choose multi-agent mode, continue with default single-host mode, but record that choice in the handoff summary so the user is not surprised later.

Confirm:

- board, level, and the explicit course market (`international` or
  `uk-domestic`) before any source discovery for AQA, Edexcel, or CAIE;
- subject and code when known;
- official page URL or PDF URL if discovery is ambiguous;
- exam year or syllabus range when the provider lists several versions;
- support language: `en`, `zh-CN`, `zh-TW`, or `ja`;
- writing style: `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`;
- workflow mode: default single-host role passes, or optional multi-agent delegation when explicitly requested;
- batch scope and the requirement that every handbook receives its own outline,
  visual decisions, HTML review, and PDF record;
- confirmed visual capability and route from the mandatory gate above;
- output directory.

If the requested curriculum system or exam board is outside the supported
automatic-acquisition scope, stop automatic discovery and explain the boundary.
For a valid selected market, use its Provider route and retain
`course_market` in the source artifact. Only continue with a manually supplied
PDF outside the supported routes after explicitly warning that it is unverified
and may fail with unknown compatibility errors.

If discovery returns several official candidates, show the candidates and wait for the user to choose. Do not guess. If the user confirms that no callable image route exists, continue only after that explicit choice, keep complex visuals as pending jobs, and describe the result as a draft when visuals are still required.

## Workflow

The Analyst, Writer, and Reviewer names below are lightweight role labels. They can be the same host LLM working step by step, or separate agents if the user explicitly asks for that orchestration. They are not mandatory project-manager or release-certification roles.

### 1. Extract Evidence

Use evidence extraction first:

```bash
python -m intl_exam_guide extract-evidence --provider <aqa|edexcel|caie|collegeboard> --course-market <international|uk-domestic|not-applicable> --query "<subject or official URL>" --level <igcse|as|a-level|ap> --exam-year <year> --out <output-dir>
```

This writes only `qualification.json`, `syllabus-evidence.json`, and `source/`. For official PDF runs, `source/` must include the original PDF, page-text extraction, `specification.md`, and `markdown-extraction.json`. It must not be treated as a generated handbook.

### 2. Analyst Writes The Outline

The host LLM reads all three source inputs and writes `syllabus-outline.json`: `source/specification.md` for document structure, `source/markdown-extraction.json` for conversion status/warnings, and `syllabus-evidence.json` for page-level source truth. Markdown helps identify headings, tables, bullets, and content/assessment/appendix boundaries; page-level evidence controls page numbers, snippets, and source coverage when the two disagree. Python must not split topics from Markdown.

The outline must include:

- `schema_version: "v0.5-llm-syllabus-outline"`;
- `source_inputs` confirming `markdown_companion_read`, `page_evidence_read`, and `markdown_extraction_status`;
- `cross_check` recording `markdown_structure_used`, `page_evidence_used`, `mismatches`, `markdown_omissions`, and `unresolved_source_gaps`;
- `structure_analysis` for this exact PDF, including the lowest source unit found below structural headings;
- `official_structure` when the PDF exposes containers;
- `coverage_granularity` using `atomic-examinable-point-v1`, with one evidence-backed audit for every lowest official container;
- `source_coverage[]` with stable IDs, page references, source kinds, independently assessable demands, and `atomicity: "atomic"`;
- `topics[]` as final teachable knowledge units;
- `granularity_audit[]` showing how each `source_coverage` item is taught: independent topic, merged into a topic, prerequisite, or sub-skill;
- one or more independently assessable source items per final topic, without forcing artificial one-item micro-topics;
- `cluster_justification` whenever a topic maps multiple source items, plus the visible handbook treatment that will teach each item;
- each topic mapped to `source_coverage_ids`, `exam_points`, and `source_snippets`.

Treat official Topic, Unit, Section, chapter, and table headings as structural containers by default. For every lowest container, determine from source evidence whether it holds one independently assessable requirement, several, or no examinable content. Continue below the heading when the source exposes separate rows, bullets, clauses, codes, conditions, applications, objectives, or other demands that can be taught or assessed independently. A genuine one-requirement container is valid only with a source-based explanation of why no deeper split exists.

This rule is independent of provider, qualification, and subject. The lowest requirement may be knowledge, a conceptual relationship, calculation, practical work, source or data analysis, extended writing, language performance, portfolio evidence, or another source-bound demand. The Analyst must not use provider templates, subject templates, command-verb lists, topic-count targets, candidate hints, or Python fallback topics as the final split.

### 3. Writer Writes Concepts And Visual Decisions

The host LLM writes `concepts/concept_explanations.json` from the current topic jobs and source evidence.

For each topic, provide:

- `topic_id` copied from the stable ID in `concepts/concept_jobs.json`;
- `topic_title`;
- `essence`;
- `analogy`;
- `explanations`: 2-4 source-bound teaching bullets or short paragraphs;
- a worked example or complete `mini_worked_example`;
- `pitfall`;
- `mastery_summary`: one concrete student-facing sentence for the Study Roadmap `What to master` column;
- `visual_decision`: the Writer's learning-value judgment for the topic;
- optional `visual_spec` only when `visual_decision.recommended_route` asks for an exact SVG, Kroki diagram, or external infographic.

Each completed Writer entry must also set `content_provenance: "llm-authored"`
and `delivery_eligible: true`. A missing visual decision, a
`python-draft-fallback` decision, or any entry with `delivery_eligible: false`
is a draft condition. Python may retain that fallback for demos and legacy
reading, but it cannot promote it into a formal handbook.

Use proper student-facing mathematical/scientific notation where the subject needs it: `b²`, `t³`, `x<sup>−1/2</sup>`, `√(...)`, `≤`, `≥`, `≠`, `θ`, `μ`, and similar stable expressions are preferred over programmer-style fallbacks such as `b^2`, `t^3`, `x^(-1/2)`, `sqrt(...)`, `<=`, `>=`, or `!=`. Do not rely on PDF→Markdown, MathJax, or a formula engine to fix notation after writing.

`mastery_summary` is Writer-owned content. Python must not fill it from a checklist template.

Visual decisions belong to the Writer and must be recorded for every topic:

- always include `visual_decision` after the topic explanation and worked example exist;
- make the decision independently for each final topic. There is no one-visual-per-subject quota, no requirement that every topic has an image, and no rule limiting external generation to one topic;
- use `recommended_route: "text-ok"` only when a clear `no_visual_reason` explains why a separate visual would not improve learning;
- use `recommended_route: "exact-svg"` only for label/geometry-first diagrams that can be reviewed as exact SVG with `svg_fit: "exact"`;
- use `recommended_route: "kroki-diagram"` when a professional formal diagram is more suitable than an LLM-authored SVG;
- use `recommended_route: "external-infographic"` when this topic needs a source-bound explanatory infographic, realistic/reference/example image, apparatus, scene, material appearance, process detail, rich annotation, or modelling nuance;
- add `visual_spec` only for `exact-svg`, `kroki-diagram`, or `external-infographic` decisions, not for `text-ok`;
- every non-text `visual_spec` must contain `semantic_contract` with
  `schema_version: "v1-visual-semantic-contract"`, a topic-specific
  `learning_claim`, `intended_inference`, `visual_kind`, non-empty
  `required_elements`, `required_relationships`, `required_labels`, and
  `forbidden_misconceptions`;
- visual assets may contain accurate, legible text labels, callouts, legends, axes, captions, and short example annotations. The Skill does not require text-free images. It requires that visible text be source-bound and consistent with the handbook;
- never create a generic subject poster or reuse one visual plan across unrelated topics. Each visual decision and visual spec must state the topic-specific learning claim and source points;
- do not request board logos or course-cover packaging;
- do not claim an infographic exists until a reviewed image is saved under `images/`.

An SVG file is not automatically an explanatory visual. An exact-SVG made only
of text and decorative rectangles is a layout card and must be rejected. A
real table or matrix may legitimately use rectangles and text when its semantic
contract declares that visual kind and the comparison relationship. Process
and feedback visuals require explicit directional connectors; feedback review
must also confirm the return path and target state. These are generic visual
grammar rules, not subject-specific templates.

The visual manifest uses the v0.5 route/asset split: `recommended_route` records the Writer's intended learning route, while `rendered_asset` records whether a real SVG/Kroki/image asset is actually present in the HTML/PDF.

Treat `images/visual_manifest.json` as a stateful approval ledger, not a build
cache. The canonical order is: Writer finalizes visual specs -> explicitly
refresh the manifest for that new plan -> generate/import assets -> record the
asset review and LLM visual decision -> render HTML using the existing manifest
only -> complete the current-HTML LLM review -> write
`agent-product-review.json` -> export PDF. When a manifest already exists,
package and import paths must be render-only; never rebuild it after importing
an asset or after writing a visual approval. Reuse an asset only when its
source-bound `spec_hash` is unchanged; changed specifications reset the asset
and visual-review state to `pending`. Importing/replacing an asset resets
`visual_need.reviewer_visual_decision` to `pending` even when the file's
separate `review_status` is `reviewed`. Unreferenced files are retained as
historical assets unless explicit cleanup is approved. Any plan, concept,
manifest, or asset change requires a new render snapshot and a complete LLM
review; hashes block stale delivery but do not replace that review. Before the
delivery gate, the current manifest must match the current `guide-plan.json`
visual briefs by count, derived key, and source-bound `spec_hash`; a stale,
legacy, duplicate, or otherwise mismatched manifest blocks delivery even when
direct `render_html()` produced an HTML file.

If support language is not `en`, add a professional term glossary. Keep the handbook body in English.

### 4. Render HTML Only

Render HTML after the Analyst and Writer artifacts are present. Do not generate PDF in this step. Remove or invalidate any PDF from an earlier HTML version. Mechanical validation may report missing files and contract errors as supporting diagnostics, but it cannot approve the handbook.

The renderer must create an immutable file under `render-snapshots/` and update
`current-render.json`. The snapshot binds the exact HTML, `guide-plan.json`,
`syllabus-outline.json`, concept explanations, visual manifest, and every
rendered asset. Do not edit a snapshot in place. After rendering, run the
read-only audit before asking the Reviewer to approve the HTML:

```bash
python -m intl_exam_guide audit-delivery --out <output-dir>
```

Any `render.*`, `content.*`, validation, visual, or review blocker keeps the
handbook in draft/review-ready state.

### 5. LLM HTML Review And Repair Loop

The active LLM Reviewer must personally open or screenshot the named HTML output and visually inspect the complete student-facing handbook. Reading source code, diffs, extracted text, `validation.json`, `quality-inspection.json`, or `final-review-packet.json` is not a substitute for looking at the rendered HTML. Python must never supply the approval decision. Sampling a few pages, topics, examples, or visuals is not sufficient for final approval.

Review every final topic. For each topic, verify the subject facts, definitions, causal or mathematical relationships, teaching explanation, worked question, solution steps, final answer, units, and source anchor. Confirm every official requirement is visibly taught and traceable from the handbook directory/table of contents, not only mapped in JSON.

Review every visual that actually renders in HTML. Inspect its subject meaning, not only whether it loads or looks polished: labels, arrows, positions, structures, relationships, scales, units, captions, and correspondence with the associated topic must be accurate. A visual with a factual or semantic error must be regenerated or replaced and reviewed again.

Also check the cover, roadmap, topic order, mastery summaries, glossary policy, source traceability, and the Analyst `granularity_audit`; cross-page visual repetition; repeated SVG structures or raster assets; and notation throughout the HTML for code-style residues such as `b^2`, `t^3`, `x^(-1/2)`, `sqrt(...)`, `<=`, `>=`, and `!=`.

If the LLM finds any content, source, teaching, worked-example, visual, layout, overflow, notation, or language problem, return to the Writer and rewrite the responsible source artifact. Rerender HTML and have the LLM inspect the new HTML from the beginning. Repeat this write-render-look loop until the current HTML has no unresolved fixable issue. Do not approve from a patch or assume a repair worked.

Write the detailed review as LLM-authored shards under `review-ledger/`:

- `topics-NNN.json`: at most 25 Topic reviews per shard, using the exact stable
  topic ID and recording factual accuracy, worked-example accuracy, source
  traceability, teaching value, findings, decision, review iteration, and the
  screenshot or browser viewport positions in `evidence_locations`;
- `visuals-NNN.json`: at most 25 rendered Visual reviews per shard, binding the
  current asset SHA-256 and recording semantic-contract review, factual
  semantics, teaching value, layout, findings, decision, review iteration, and
  `evidence_locations` for the inspected visible asset;
- `holistic.json`: a separate review of the complete assembled HTML, including
  cover/navigation, cross-page consistency, responsive layout, notation and
  encoding, issue history, decision, desktop/mobile `evidence_locations`, and
  current snapshot/HTML binding.

Sampling is forbidden. After the LLM has written those files, run:

```bash
python -m intl_exam_guide index-review-ledger --out <output-dir>
```

Python may hash and index the LLM-authored shards but cannot create their review
decisions. Then write the compact `agent-product-review.json` using
`schema_version: "v0.7-llm-html-review-ledger"`, `reviewer_type: "llm"`, the
exact `reviewed_html_sha256`, `render_snapshot_id`,
`review_ledger_index_sha256`, positive `review_iteration`,
`complete_html_reviewed: true`, `html_review_passed: true`, `decision:
"approved"`, issue/repair history, and no unresolved fixable issue. Do not put
the full Topic/Visual lists back into this summary file.

### 6. Export PDF After Approval

Only after the current HTML hash has valid LLM approval may the host run:

```bash
python -m intl_exam_guide export-pdf --out <output-dir>
```

The export command must reject missing approval, Python-authored approval,
`python-draft` or mixed content provenance, revisions-required decisions,
unresolved issues, pending/rejected visual decisions, missing or stale render
snapshots, asset hash mismatches, or a review hash that does not match the
current HTML. It first creates a temporary candidate PDF, runs technical checks
for readable pages, portrait A4 geometry, local-file footers, and other hard
export defects, and only then writes an immutable `pdf-exports/` record and
updates `current-pdf.json`. A failed candidate never becomes current. Any later
input or HTML change marks the former PDF historical without deleting it and
returns the workflow to Step 4/5.

For a controlled final copy, use `--delivery-dir <directory>`. The copied PDF
must match the approved source hash. A differing existing destination is never
silently overwritten; `--supersede-existing` is an explicit archival action.
Formal delivery uses `current-pdf.json` and `current-delivery.json`, never file
modification time.

Do not present the handbook as final until this sequence completes. Student-facing HTML/PDF must not expose internal review/check panels such as `Review Check`, `Needs visible review`, delivery states, validation reminders, or coordinator-only handoff text.

## Board Themes

All four supported source systems use the same fixed cover information hierarchy and geometry. Each has an independent template identity and palette. Cover text must come from the selected qualification and official syllabus metadata; do not invent a course code, specification version, syllabus range, or exam year.

OxfordAQA: blue/red identity, clear subject title and course-code badge.

Pearson Edexcel: teal/blue identity, Pearson Edexcel course identity, cleaned title and code. A URL year such as `2017` is not a course code.

Cambridge International: red/navy identity, academic cover, syllabus range and selected exam year only when known.

College Board AP: College Board blue/yellow/aqua identity, AP course title, CED effective version, and selected AP exam year only when verified. AP courses do not receive invented numeric course codes.

Do not show fallback strings such as `Not specified` prominently on the cover.

## CLI Notes

Framework preview only:

```bash
python -m intl_exam_guide demo --out <output-dir> --explanation-style friendly --language en --skip-pdf
```

Evidence-only official run:

```bash
python -m intl_exam_guide generate --provider <provider> --query "<subject or URL>" --level <level> --out <output-dir>
```

`generate` prepares official evidence for the host LLM workflow. It must not split topics, write fallback outlines, or render HTML/PDF.

`demo` is only an offline framework preview and now stops at HTML. Production handbooks require an LLM Analyst outline, Writer-reviewed concepts/visual decisions, repeated visible HTML review by the LLM until approval, and gated PDF export afterward.

`audit-delivery --out <output-dir>` is read-only. It never refreshes validation,
changes review states, exports PDF, or rewrites historical artifacts.

## Reference Files

- `references/revision_guide_spec.md`
- `references/scientific_vector_fallback.md`

## Stop Conditions

Stop or downgrade the handoff when:

- official syllabus evidence is missing;
- the topic split came from Python fallback instead of the LLM Analyst;
- `guide-plan.json` is missing `content_provenance: "llm-authored"`, or any concept entry is marked `python-fallback`, `python-draft-fallback`, or `delivery_eligible: false`;
- a Writer/Reviewer handoff uses a missing or guessed topic ID, substring topic match, or a changed source/input artifact without a new render snapshot;
- Pearson, Cambridge, or College Board AP metadata is visibly wrong;
- source page furniture leaks into topic points;
- official PDF run lacks `source/specification.md` or `source/markdown-extraction.json`, or Markdown extraction status is not `success`;
- `coverage_granularity` does not audit every lowest official container, or a broad structural heading is passed through as one source item without source proof;
- a final teaching topic has no independent source item, or combines multiple source items without a source-based teaching justification and visible treatment for every mapped item;
- generated HTML has not been opened or screenshot-inspected;
- final approval was based on sampled pages/topics/visuals instead of every final topic and every rendered visual;
- review shards exceed 25 items, omit/duplicate a current Topic or Visual, omit visible `evidence_locations`, use a stale asset/snapshot hash, or replace the separate holistic HTML review;
- topic review did not verify subject facts, worked examples, solution steps, final answers, units, and source anchors;
- visual review checked only loading or appearance without checking labels, arrows, structures, relationships, scales, units, captions, and topic correspondence;
- Python validation, inspection, or packet generation was used as a substitute for the LLM personally viewing the rendered HTML;
- `agent-product-review.json` was not written by an LLM, does not reference the current review-ledger index/render snapshot/HTML SHA-256, or still lists unresolved fixable issues;
- PDF was generated before the current HTML passed LLM review, or HTML changed after approval without a new visible review;
- `current-render.json` or its immutable snapshot is missing, invalid, stale, or points to a different HTML/input hash;
- a PDF candidate fails technical validation, `current-pdf.json` is missing/stale, or a delivery copy does not match the approved PDF hash;
- topic explanations are template filler or subject-mismatched;
- roadmap mastery summaries are missing, duplicated, or Python-generated;
- a topic is missing `visual_decision`, or a `text-ok` decision lacks `no_visual_reason`;
- a non-text visual lacks the complete semantic contract, or an exact-SVG is a text card without independent structure, relationship, quantity, or spatial meaning;
- visual decisions were made by subject-level quota, one-image-per-subject batching, or a reused generic visual plan instead of independently for each topic;
- an image was rejected or omitted solely because it contains text, rather than because its text is inaccurate, illegible, unsupported, or unnecessary;
- complex visuals are pending but described as reviewed assets;
- the external image-generation capability question was skipped, inferred, or silently defaulted to local generation;
- cross-page visual repetition makes different topics look like reused templates;
- student-facing HTML/PDF still contains ASCII math residue such as `^2`, `sqrt(...)`, `<=`, `>=`, or `!=`.
