# Revision Guide Handbook Spec

This repository is an open-source version of the original IGCSE revision-guide Skill. Its job is to provide a student-facing revision handbook framework and the operations needed for a host LLM to fill it correctly. It is not a project report generator, release-certification system, or Python content writer.

This reference implements the workflow boundary declared in `../SKILL.md`; it
must not define a competing workflow.

## Output Package

A generated handbook package may include:

- `<board>-<level>-<subject>-<time>.html`: one print-friendly UTF-8 HTML handbook, for example `oxfordaqa-igcse-mathematics-20260706-1430.html`.
- `<board>-<level>-<subject>-<time>.pdf`: portrait A4 PDF promoted from a technically valid candidate only after the host LLM approves the exact current HTML hash.
- `sections/`: source fragments used to assemble the handbook.
- `images/`: reviewed SVG assets, reviewed infographic assets, and pending visual jobs.
- `concepts/`: concept-writing jobs and LLM-written concept explanations, including per-topic `visual_decision` records.
- `guide-plan.json`: structured topic guides, worked examples, practice items, and visual briefs.
- `render-snapshots/<snapshot-id>.json` and `current-render.json`: immutable render-input binding and the explicit current HTML pointer used by formal review/export. The pointer is not an approval record.
- `qualification.json`: provider metadata, updated after the LLM Analyst outline pass.
- `syllabus-evidence.json`: page-level evidence extracted from the official source.
- `syllabus-outline.json`: the LLM Analyst's source split contract.
- `validation.json`: mechanical contract and consistency checks.
- `quality-inspection.json`: optional Python diagnostic output for obvious package gaps; never an approval artifact.
- `final-review-packet.json`: optional context packet from the `review` command; never a substitute for the LLM opening the rendered HTML.
- `agent-product-review.json`: LLM-authored approval bound to the SHA-256 of the exact visibly inspected HTML.
- `review-ledger/`: LLM-authored Topic and Visual review shards plus a separate
  holistic HTML review; `index.json` is a mechanical hash index, not an approval
  decision.
- `pdf-exports/<export-id>.json` and `current-pdf.json`: immutable approved-PDF
  provenance and the only formal current-PDF pointer. Historical PDF files may
  remain readable without being current.
- `delivery-copies/<copy-id>.json` and `current-delivery.json`: optional
  hash-verified delivery-copy provenance.
- `handbook-package.json`: mechanical manifest for sections and image assets.

Downloaded specification PDFs and extracted text belong under `source/` and must not be committed to the repository.

An evidence-only package from `extract-evidence` is intentionally smaller. It contains `qualification.json`, `syllabus-evidence.json`, and `source/`. It is not a generated handbook and should not include handbook HTML/PDF, `guide-plan.json`, `validation.json`, or delivery status.

## Required Preflight

Do not start syllabus download or handbook writing until the user has confirmed the following. Ask clarifying questions when any item is missing or ambiguous; do not silently choose defaults for content-bearing decisions. In the first preflight exchange, explicitly offer the workflow-mode choice: default single-host role passes, or optional multi-agent delegation when the user wants separate agents and the runtime supports them.

1. board, qualification level, A-Level stage when applicable, subject, and code
   when known. AS and A2 are A-Level stages, not parallel qualification levels;
2. for AQA, Edexcel, and CAIE GCSE/IGCSE/A-Level, the explicit course market:
   `international` or `uk-domestic`. Never infer this from a course title,
   code, URL, provider, or prior run. AP uses `not-applicable`. For AQA and
   Edexcel, the market selects the matching official route. For CAIE, it
   records the request context while using the same official Cambridge
   International catalogue;
3. official page URL or direct PDF URL when discovery is ambiguous;
4. exam year or syllabus range when the provider lists multiple versions;
5. support language: `en` for no glossary, or `zh-CN`, `zh-TW`, or `ja` for a professional term glossary;
6. writing style: `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`;
7. workflow mode: default single-host Analyst/Writer/Reviewer role passes, or optional multi-agent delegation when explicitly requested;
8. visual route: prompt queue, reviewed asset directory, installed image Skill, project script, or custom API;
9. output directory.

If official discovery returns several candidates, show the candidates and wait for selection. Do not guess. If no callable image route exists, continue with prompt-queue visual jobs and report pending visuals honestly.

For custom image providers, record the model name, endpoint URL, and API-key environment variable name. Do not collect or store the raw API key.

## Analyst Source Split Contract

The syllabus outline is an LLM-owned interpretation of the current official specification. Python may download, extract, store, convert the official PDF to Markdown, and validate evidence, but it must not decide the syllabus structure, require a fixed number of layers, or require provider-specific labels.

Official PDF production uses dual-track source input. Python must generate `syllabus-evidence.json`, `source/specification.md`, and `source/markdown-extraction.json`. The Analyst reads Markdown for document structure and page-level evidence for source truth. If Markdown and page evidence disagree, page evidence wins. Python must not split topics from Markdown headings, tables, or bullets.

The Analyst writes `syllabus-outline.json` in this order:

1. Read `source/specification.md`, `source/markdown-extraction.json`, and `syllabus-evidence.json`; record `source_inputs` and `cross_check` with Markdown structure use, page evidence use, mismatches, Markdown omissions, and unresolved source gaps.
2. Write `structure_analysis`, explaining how this exact syllabus organizes examinable content. The structure may be flat, nested, mixed, route-based, table-based, code-based, objective-based, or another form visible in the PDF.
3. Record `official_structure` when the PDF exposes structural containers such as parts, units, components, routes, sections, options, papers, or sub-sections. If the source is genuinely flat, say so; Python must not invent missing layers.
4. Treat every official Topic, Unit, Section, chapter, table heading, and similar label as a structural container by default. Record `coverage_granularity.container_audit` for every lowest official container and classify it as `single_examinable_point`, `multiple_examinable_points`, or `no_examinable_content`, with page evidence. A genuine single-point container must explain from the source why no deeper independently assessable split exists.
5. Record `source_coverage`: the lowest complete source-bound requirements that can be taught or assessed independently. These may be knowledge statements, conceptual relationships, coded points, rows, bullets, skills, calculations, practical work, source/data analysis, extended responses, language performance, portfolio evidence, restrictions, or other subject-appropriate demands. Every item must have a stable ID, `source_kind`, independently assessable `exam_action`, `atomicity: "atomic"`, source content, and page evidence. Paired columns should remain linked when one clarifies the other.
6. Write `granularity_audit`: for every `source_coverage` item, decide whether it is an independent topic, merged into a topic, prerequisite, or sub-skill. Any merged or sub-skill item must name the target topic, explain the teaching reason, and state the visible handbook treatment.
7. Split `topics[]` using a split-first rule. Every final topic maps one or more independently assessable source items. Combine closely related items only when `cluster_justification` names the relationship, explains why separate teaching topics would be misleading, and identifies the visible treatment for every mapped item. Do not force artificial one-item micro-topics. A shared heading alone is not a merge reason.
8. Map every final topic back to `source_coverage_ids`, source snippets, and page numbers so the Writer and Reviewer can audit the split.

A valid split is source-relative and teaching-relative, not provider-, qualification-, or subject-specific. Do not use a fixed command-verb vocabulary, fixed hierarchy, or fixed item count. The failure case to block is an outline that lets the Analyst define one broad container as one coverage item and then pass its own consistency checks, collapses detailed source coverage into headings, maps requirements only in JSON, or cannot show where each requirement receives visible teaching treatment in the handbook.

## Handbook Structure

The final handbook should read like a revision book for a student. Use this 8-module order unless the subject requires a reviewed alternative:

1. Cover.
2. How to use this handbook.
3. Study roadmap / topic map.
4. Term glossary when requested.
5. Topic guide blocks.
6. Practice workbook.
7. Exam structure and source appendix.
8. Revision checklist.

Each topic or knowledge unit should include:

- one-sentence essence;
- student-friendly analogy or life-scene explanation;
- 2-4 source-bound concept explanations that say what the concept is, what relationship or boundary it describes, and why it matters for this syllabus point;
- key syllabus points kept in structured review data, not as a substitute for concept explanation;
- at least one worked example;
- public solution steps;
- answer checkpoints;
- exam pitfall;
- source anchor back to the specification PDF;
- Writer-authored `mastery_summary` for the Study Roadmap.

## Writing Style

Use English for handbook labels, explanations, image prompts, topic framing, worked examples, and diagram text because the exam is in English. If the user selects a support language, add a professional term glossary with 30-50 user-language-to-English entries. Do not translate the whole handbook body and do not render every label as a bilingual pair.

The tone should help teenagers stay awake and oriented:

- use life-scene explanations for abstract ideas;
- use detective-style reasoning for solution steps when useful;
- use original adventure or story framing only when it helps motivation;
- avoid copying protected characters, stories, or exam-paper artwork;
- avoid long academic paragraphs and unsupported syllabus claims;
- write formulas and inequalities with stable student-facing symbols such as `b²`, `t³`, `x<sup>−1/2</sup>`, `√(...)`, `≤`, `≥`, `≠`, `θ`, and `μ` instead of programmer-style fallbacks such as `b^2`, `t^3`, `x^(-1/2)`, `sqrt(...)`, `<=`, `>=`, or `!=`;
- remove formulaic transitions such as `In conclusion`, `Overall`, `总之`, and `值得注意的是` from student-facing text.

## Visual Workflow

Do not make the handbook text-only by default. The Writer decides visual need after the source-bound topic guide and examples are drafted. This judgment applies to every subject: any topic can deserve a visual when it improves learning, and any topic can be `text-ok` when a separate image would add noise.

Every topic in `concepts/concept_explanations.json` must include `visual_decision`:

- make the decision independently after the topic explanation and worked example exist. There is no one-image-per-subject quota, no minimum image count, and no limit of one external-generation job per subject;
- `recommended_route: "text-ok"`: no image needed; include `no_visual_reason` explaining why text, example, and source anchor are the better learning route.
- `recommended_route: "exact-svg"`: an exact SVG is appropriate because labels and geometry fully carry the teaching meaning. Include `svg_fit: "exact"`; create/import the LLM-authored SVG first and mark it reviewed only after LLM visual review passes.
- `recommended_route: "kroki-diagram"`: a professional formal diagram is more suitable than an exact LLM SVG; review the generated SVG before final delivery.
- `recommended_route: "external-infographic"`: this topic needs a richer reviewed raster asset, including a source-bound explanatory visual, realistic/reference/example image, apparatus, scene, material appearance, process detail, or rich annotation; create a topic-specific visual brief and prompt queue entry until an asset exists.
- text is allowed inside visuals when labels, callouts, legends, axes, captions, or short example annotations are accurate, legible, source-bound, and consistent with the handbook. The Skill does not require text-free images.
- never generate a generic subject poster or reuse one visual plan across unrelated topics. The Writer must state the topic-specific learning claim and source points for every non-text route.

Only routes other than `text-ok` should include `visual_spec`. The v0.5 visual manifest keeps the Writer's `recommended_route` separate from the actual `rendered_asset`, so `exact-svg`, `kroki-diagram`, or `external-infographic` is not complete until the corresponding reviewed file exists and renders in the handbook. Review must also catch cross-page visual repetition: repeated SVG structures, reused raster assets, duplicate visual titles, or decorative page layouts that make unrelated topics look copied.

Every non-text visual spec includes a `v1-visual-semantic-contract` with the
learning claim, intended inference, visual kind, required elements,
relationships and labels, plus forbidden misconceptions. Python validates that
shape but does not invent its contents or approve semantic accuracy.

Pure text and decorative rectangles are a layout card, not an explanatory
exact-SVG. Tables and matrices are valid exceptions when the declared visual
kind and relationship make the comparison inspectable. Process and feedback
visuals require directional connectors; the LLM Reviewer must still verify
that the direction, loop, target state, labels, and subject meaning are correct.

Each concept entry must carry the stable `topic_id` from
`concepts/concept_jobs.json`, `content_provenance: "llm-authored"`, and
`delivery_eligible: true`. Python-generated entries and visual fallbacks remain
available for framework previews but must be marked as draft and are not
eligible for formal delivery. Topic application uses exact stable IDs or exact
source-point matches; substring matching is prohibited.

Good exact-SVG cases include number lines, simple graphs, pH scales, particle models, energy profiles, basic geometry, flows, hierarchies, timelines, and relationship maps when the geometry and labels fully carry the concept.

Good external-infographic cases include lab apparatus, complex geometry, circuits, dense multi-factor scenes, realistic process scenes, and high-design text+diagram charts.

External infographic prompts should use the default revision-worksheet visual style: landscape educational infographic, clear topic banner, separated teaching panels, pastel subject colors, readable black English labels, accurate diagrams/icons, and a small Quick Q&A or practice box. Do not request board logos, school branding, course-cover packaging, decorative watermarks, or unsupported facts.

For SVG-safe chart, axis, curve, table, and simple geometry cases, use the exact SVG review policy in `references/scientific_vector_fallback.md`. Keep SVG text editable and require review before final delivery. Do not use SVG for dense educational posters or rich infographics that need a real image model or reviewed imported asset.

Do not claim that an infographic has been generated until a callable route has produced or imported an image and the asset is saved under `images/`.

## Source And Accuracy Rules

- Use the public qualification page for discovery metadata.
- Use the downloaded course specification PDF as the source of truth for detailed syllabus content.
- Prefer detailed reference codes such as `N1`, `A13`, `G20`, or `S18` when the PDF exposes them.
- Do not copy past-paper questions, mark schemes, or large passages from the PDF.
- Generate original worked examples that stay inside the extracted syllabus points.
- Do not maintain per-subject hard-coded concept-explanation libraries. The final concept text must be generated from the current topic title and source points for that run, not copied from a Mathematics, Chemistry, Economics, or Physics template.
- Treat a guide as incomplete if detailed topic extraction, source snippets, examples, visuals, HTML, or validation output are missing.

## HTML Review Before PDF

Before presenting a handbook as complete, confirm:

- `syllabus-outline.json` exists and was written by the LLM Analyst from current evidence;
- every lowest official container is present in `coverage_granularity.container_audit`, and every `source_coverage` item is an atomic source-bound requirement;
- every final topic maps one or more independent source items, with source-justified clustering and visible treatment for every mapped item;
- every topic has a guide block and worked example;
- every topic has reviewed concept explanation content imported from `concepts/concept_explanations.json`;
- every topic has a Writer-authored `mastery_summary`;
- every topic has a source snippet or a manual-review warning;
- every topic has `visual_decision`, with `no_visual_reason` whenever the route is `text-ok`;
- visual briefs or reviewed assets exist for visual topics;
- `visual_manifest.json` distinguishes the recommended route from the rendered asset state;
- `visual_manifest.json` is stateful approval evidence, not a disposable build
  cache. An existing manifest is render-only by default. A new visual plan must
  explicitly start a refresh cycle before asset generation/import and visual
  approval. Never rebuild after importing an asset or after recording approval.
  Reuse requires an unchanged source-bound `spec_hash`; changed specifications
  reset the asset and visual decision to `pending`. Importing/replacing an
  asset resets `visual_need.reviewer_visual_decision` to `pending` even when
  the separate asset `review_status` is `reviewed`. Unreferenced image files
  remain historical unless explicit cleanup is approved.
- `validation.json` has no `error` issues;
- official PDF runs have successful `source/markdown-extraction.json` and readable `source/specification.md`;
- no PDF has been generated for the current HTML before LLM approval.
- `current-render.json` points to an immutable snapshot whose input and asset hashes still match the current files.
- The delivery gate also compares the current manifest with `guide-plan.json`
  visual briefs by count, derived key, and source-bound `spec_hash`; a stale or
  legacy manifest cannot be approved through a direct HTML render.

The host LLM must open or screenshot the named HTML output and personally review the complete visible handbook. Final approval cannot be based on sampled pages, topics, examples, or visuals. Review every final topic for subject facts, definitions, relationships, explanations, worked questions, solution steps, final answers, units, and source anchors. Confirm official requirements are visibly taught rather than only mapped in JSON.

Review every visual that actually renders in HTML for semantic and factual accuracy, not only loading or appearance. Check labels, arrows, positions, structures, relationships, scales, units, captions, and correspondence with the associated topic. Also check topic sequence, `granularity_audit`, cross-page repetition, glossary policy, responsive layout, and notation throughout the HTML for `b^2`, `sqrt(...)`, `x^(-1/2)`, `<=`, `>=`, and similar ASCII residue. Python validation, quality inspection, packet generation, HTML parsing, and source-code review are diagnostics only and cannot approve the handbook.

If any fixable issue is found, the LLM returns the handbook to the Writer, rewrites the responsible source artifact, rerenders HTML, and visually reviews the new HTML again. Repeat until the current HTML contains no unresolved fixable issue. The Reviewer must not approve a repair from code or a diff without looking at the rerendered result.

Detailed approval evidence is stored in `review-ledger/topics-NNN.json` and
`visuals-NNN.json` shards with no more than 25 reviews per file, plus
`review-ledger/holistic.json` for the complete assembled HTML. Every shard binds
the same current render snapshot and HTML SHA-256. Topic coverage uses stable
topic IDs; Visual coverage uses visual IDs and current asset hashes. Python may
write `review-ledger/index.json` from those existing files, but it cannot create
or approve their conclusions. Every Topic/Visual entry and the holistic review
must record the screenshot or browser viewport positions actually inspected in
`evidence_locations`.

The compact `agent-product-review.json` uses
`v0.7-llm-html-review-ledger` and references the current snapshot, HTML SHA-256,
and ledger-index SHA-256. Any input, asset, HTML, shard, or index change makes
the approval stale.

The visual-to-delivery sequence is Writer visual specs -> explicit manifest
refresh for a new plan -> asset generation/import -> visual-level LLM decision
-> render-only HTML -> complete HTML review -> product approval -> PDF. A
manifest or asset mutation without a subsequent current HTML render leaves the
current snapshot and downstream approval evidence stale and must block delivery.

Only after that approval and a passing read-only delivery audit may the host run
`python -m intl_exam_guide export-pdf --out <output-dir>`. The command must
refuse export when content provenance, snapshot, input/asset hashes, visual
states, validation, or approval evidence is incomplete or stale. It renders to
a temporary candidate, blocks promotion on hard PDF defects, and writes an
immutable `pdf-exports/` record before updating `current-pdf.json`. Failed
candidates never become current. Historical PDFs remain on disk but are not
formal delivery sources. `--delivery-dir` creates a hash-verified copy; a
differing destination requires the explicit `--supersede-existing` archival
option.

The student edition must be exported only after internal review/check panels have been removed. `final-review-packet.json`, `quality-inspection.json`, and validation notes are supporting diagnostics, not student handbook sections or approval evidence.

Validation is not enough by itself. A handbook is not complete merely because the Skill generated files or Python checks passed. If the current rendered HTML was not personally opened or screenshot-inspected by the LLM, do not create the PDF and do not present the handbook as complete.
