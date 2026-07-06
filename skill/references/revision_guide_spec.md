# Revision Guide Handbook Spec

This repository is an open-source version of the original IGCSE revision-guide Skill. Its job is to provide a student-facing revision handbook framework and the operations needed for a host LLM to fill it correctly. It is not a project report generator, release-certification system, or Python content writer.

The workflow boundary is recorded in `../../docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`.

## Output Package

A generated handbook package may include:

- `guide.html`: one print-friendly UTF-8 HTML handbook.
- `guide.pdf`: A4 PDF export when requested and a browser runtime is available.
- `sections/`: source fragments used to assemble the handbook.
- `images/`: reviewed SVG assets, reviewed infographic assets, and pending visual jobs.
- `concepts/`: concept-writing jobs and LLM-written concept explanations.
- `guide-plan.json`: structured topic guides, worked examples, practice items, and visual briefs.
- `qualification.json`: provider metadata, updated after the LLM Analyst outline pass.
- `syllabus-evidence.json`: page-level evidence extracted from the official source.
- `syllabus-outline.json`: the LLM Analyst's source split contract.
- `validation.json`: mechanical contract and consistency checks.
- `quality-inspection.json`: optional fast inspection output for obvious package gaps.
- `final-review-packet.json`: optional packet from the `review` command to help the host LLM review the rendered handbook.
- `handbook-package.json`: mechanical manifest for sections and image assets.

Downloaded specification PDFs and extracted text belong under `source/` and must not be committed to the repository.

An evidence-only package from `extract-evidence` is intentionally smaller. It contains `qualification.json`, `syllabus-evidence.json`, and `source/`. It is not a generated handbook and should not include `guide.html`, `guide-plan.json`, `validation.json`, or delivery status.

## Required Preflight

Do not start syllabus download or handbook writing until the user has confirmed:

1. board, qualification level, subject, and code when known;
2. official page URL or direct PDF URL when discovery is ambiguous;
3. exam year or syllabus range when the provider lists multiple versions;
4. support language: `en` for no glossary, or `zh-CN`, `zh-TW`, or `ja` for a professional term glossary;
5. writing style: `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`;
6. visual route: prompt queue, reviewed asset directory, installed image Skill, project script, or custom API;
7. output directory.

If official discovery returns several candidates, show the candidates and wait for selection. Do not guess. If no callable image route exists, continue with prompt-queue visual jobs and report pending visuals honestly.

For custom image providers, record the model name, endpoint URL, and API-key environment variable name. Do not collect or store the raw API key.

## Analyst Source Split Contract

The syllabus outline is an LLM-owned interpretation of the current official specification. Python may download, extract, store, and validate evidence, but it must not decide the syllabus structure, require a fixed number of layers, require provider-specific labels, or require a minimum topic count.

The Analyst writes `syllabus-outline.json` in this order:

1. Read the current PDF evidence and write `structure_analysis`, explaining how this exact syllabus organizes examinable content. The structure may be flat, nested, mixed, route-based, table-based, code-based, objective-based, or another form visible in the PDF.
2. Record `official_structure` when the PDF exposes structural containers such as parts, units, components, routes, sections, options, papers, or sub-sections. If the source is genuinely flat, say so; Python must not invent missing layers.
3. Record `source_coverage`: the actual examinable rows, bullets, coded points, skill statements, formula requirements, restrictions, examples, or table cells that need coverage. Paired columns such as Content and Additional information should stay linked when the second column clarifies the first.
4. Split `topics[]` into final teachable knowledge units or tight clusters justified by the current source evidence. A topic title should name what the student learns, not merely repeat where it appears in the PDF.
5. Map every final topic back to `source_coverage_ids`, source snippets, and page numbers so the Writer and Reviewer can audit the split.

A valid split is source-relative, not count-relative. A short flat syllabus may produce a short flat outline. A dense table may produce many knowledge units. The failure case to block is not "too few topics" by itself; it is an outline that collapses detailed source coverage into container headings or cannot show how its teaching units cover the source evidence.

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
- remove formulaic transitions such as `In conclusion`, `Overall`, `总之`, and `值得注意的是` from student-facing text.

## Visual Workflow

Do not make the handbook text-only by default. The Writer decides visual need after the source-bound topic guide and examples are drafted.

Allowed visual decisions:

- `text-ok`: no image needed.
- `svg-basic`: exact SVG is appropriate because labels and geometry fully carry the teaching meaning. Include `svg_fit: "exact"`.
- `infographic`: a richer reviewed raster asset is needed; create a source-bound visual brief and prompt queue entry until an asset exists.

Good SVG cases include number lines, simple graphs, pH scales, particle models, energy profiles, basic geometry, flows, hierarchies, timelines, and relationship maps when the geometry and labels fully carry the concept.

Good infographic cases include lab apparatus, complex geometry, circuits, dense economics scenes, realistic process scenes, and high-design text+diagram charts.

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

## Review Before Handoff

Before presenting a handbook as complete, confirm:

- `syllabus-outline.json` exists and was written by the LLM Analyst from current evidence;
- every topic has a guide block and worked example;
- every topic has reviewed concept explanation content imported from `concepts/concept_explanations.json`;
- every topic has a Writer-authored `mastery_summary`;
- every topic has a source snippet or a manual-review warning;
- visual briefs or reviewed assets exist for visual topics;
- `validation.json` has no `error` issues;
- PDF export succeeded when requested, or the user is told why it was skipped.

Then the host LLM must open or screenshot `guide.html` and review the visible handbook. It should compare topic sequence and concept explanations with the syllabus outline, inspect diagrams/images, check glossary policy, sample PDF pages when exported, and fix repairable issues before handoff.

Validation is not enough by itself. A handbook is not complete merely because the Skill generated files or validation passed. If the rendered HTML was not opened or screenshot-inspected, say so and do not present the handbook as complete.
