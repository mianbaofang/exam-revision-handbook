---
name: igcse-a-level-revision-guide
description: Framework and LLM operations guide for International GCSE and A-Level revision handbooks. Provides evidence extraction, artifact contracts, board visual themes, and HTML/PDF rendering. The host LLM owns syllabus analysis, writing, visual judgement, and review.
---

# IGCSE & A-Level Revision Handbook Skill

## Core Rule

This Skill is a framework plus LLM operations guide. It is not an automatic content generator.

Python may discover sources, download PDFs, extract page-level evidence, validate JSON, import LLM-written artifacts, render HTML/PDF, and write mechanical manifests. Python must not decide topic splits, choose syllabus points, write teaching content, invent `mastery_summary`, decide visual need, or approve final quality.

The host LLM owns all interpretation, writing, visual judgement, and review.

Before changing workflow scope, read `../docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`.

## What The Skill Provides

- Three board visual themes: OxfordAQA blue/red, Pearson Edexcel teal/blue, Cambridge red/navy.
- An 8-module handbook framework: Cover, How to Use, Study Roadmap, optional Term Glossary, Topic Guides, Practice Workbook, Exam Structure, Revision Checklist.
- Artifact contracts for `qualification.json`, `syllabus-evidence.json`, `syllabus-outline.json`, and `concepts/concept_explanations.json`.
- A Python rendering engine that turns approved artifacts into named HTML and optional PDF outputs.

## Preflight

Confirm the minimum run inputs before downloading or writing. Ask the user directly when any of these are missing or ambiguous; do not silently choose defaults for content-bearing decisions:

- board, level, subject, and code when known;
- official page URL or PDF URL if discovery is ambiguous;
- exam year or syllabus range when the provider lists several versions;
- support language: `en`, `zh-CN`, `zh-TW`, or `ja`;
- writing style: `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`;
- visual route: prompt queue, reviewed assets, installed image Skill, project script, or custom API;
- output directory.

If discovery returns several official candidates, show the candidates and wait for the user to choose. Do not guess. If no callable image route exists, continue with pending visual jobs and describe the result as a draft when visuals are still required.

## Workflow

### 1. Extract Evidence

Use evidence extraction first:

```bash
python -m intl_exam_guide extract-evidence --provider <oxfordaqa|pearson|cambridge> --query "<subject or official URL>" --level <level> --exam-year <year> --out <output-dir>
```

This writes only `qualification.json`, `syllabus-evidence.json`, and `source/`. It must not be treated as a generated handbook.

### 2. Analyst Writes The Outline

The host LLM reads `syllabus-evidence.json` and writes `syllabus-outline.json`.

The outline must include:

- `schema_version: "v0.5-llm-syllabus-outline"`;
- `structure_analysis` for this exact PDF;
- `official_structure` when the PDF exposes containers;
- `source_coverage[]` with stable IDs, page references, and source snippets;
- `topics[]` as final teachable knowledge units;
- `granularity_audit[]` showing how each `source_coverage` item is taught: independent topic, merged into a topic, prerequisite, or sub-skill;
- merge rationale whenever official bullets are combined, plus the visible handbook treatment that will teach each bullet;
- each topic mapped to `source_coverage_ids`, `exam_points`, and `source_snippets`.

The Analyst must not use provider templates, subject templates, topic-count targets, candidate hints, or Python fallback topics as the final split.

### 3. Writer Writes Concepts And Visual Decisions

The host LLM writes `concepts/concept_explanations.json` from the current topic jobs and source evidence.

For each topic, provide:

- `topic_title`;
- `essence`;
- `analogy`;
- `explanations`: 2-4 source-bound teaching bullets or short paragraphs;
- a worked example or complete `mini_worked_example`;
- `pitfall`;
- `mastery_summary`: one concrete student-facing sentence for the Study Roadmap `What to master` column;
- optional `visual_spec` when a visual materially improves understanding.

Use proper student-facing mathematical notation where the subject needs it: `²`, `³`, `√`, `≤`, `≥`, `≠`, `θ`, `μ`, and similar stable Unicode symbols are preferred over plain-text fallbacks such as `^2`, `sqrt()`, `<=`, or `>=`. Do not rely on MathJax or a formula engine for final PDF readability.

`mastery_summary` is Writer-owned content. Python must not fill it from a checklist template.

Visual decisions belong to the Writer:

- omit `visual_spec` when text is enough;
- use `complexity: "svg-basic"` only after the topic explanation and worked example exist, and only for exact-fit diagrams with `svg_fit: "exact"`;
- generate or import an LLM-authored exact SVG first and mark it reviewed only after LLM visual review passes;
- if LLM SVG review fails, try a Kroki professional diagram and review that output;
- if Kroki review fails or the visual needs realism, rich annotation, apparatus, scenes, or modelling nuance, route it to `complexity: "infographic"`;
- do not request board logos or course-cover packaging;
- do not claim an infographic exists until a reviewed image is saved under `images/`.

If support language is not `en`, add a professional term glossary. Keep the handbook body in English.

### 4. Render And Review

Render HTML after the Analyst and Writer artifacts are present. Mechanical validation can catch missing files and contract errors, but it does not prove teaching quality.

The Reviewer must open or screenshot the named HTML output and inspect the visible handbook. If PDF is exported, sample pages from it too. Validation, quality inspection, and review packets are supporting evidence only; they are not approval.

At minimum, check the cover, roadmap, topic order, concept explanations, examples, visuals, glossary policy, source traceability, and the Analyst `granularity_audit`. Confirm official bullets can be traced from the handbook directory/table of contents to visible teaching treatment, not only to JSON coverage IDs.

Do not present the handbook as final until the rendered HTML has actually been inspected and any pending visual or concept blockers are reported honestly. Student-facing HTML/PDF must not expose internal review/check panels such as `Review Check`, `Needs visible review`, delivery states, validation reminders, or coordinator-only handoff text.

## Board Themes

OxfordAQA: blue/red identity, direct modern cover, clear subject title and course-code badge.

Pearson Edexcel: teal/blue identity, Pearson Edexcel course identity, cleaned title and code. A URL year such as `2017` is not a course code.

Cambridge International: red/navy identity, academic cover, syllabus range and selected exam year only when known.

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

`demo` is only an offline framework preview. Production handbooks require an LLM Analyst outline, Writer-reviewed concepts/visual decisions, and Reviewer inspection of the rendered output.

## Reference Files

- `references/revision_guide_spec.md`
- `references/scientific_vector_fallback.md`

## Stop Conditions

Stop or downgrade the handoff when:

- official syllabus evidence is missing;
- the topic split came from Python fallback instead of the LLM Analyst;
- Pearson or Cambridge metadata is visibly wrong;
- source page furniture leaks into topic points;
- generated HTML has not been opened or screenshot-inspected;
- topic explanations are template filler or subject-mismatched;
- roadmap mastery summaries are missing, duplicated, or Python-generated;
- complex visuals are pending but described as reviewed assets.
