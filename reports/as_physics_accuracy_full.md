# OxfordAQA International AS Physics 2027 — Historical Superseded Audit

> **Status update (2026-09-09):** This audit describes an earlier pre-repair
> candidate and is **superseded**. Do not use its `draft-review-required` or
> unresolved-issue conclusions for the current handbook. The current 94-topic
> content and delivery status are recorded in the final review ledger and
> current delivery pointers under `artifacts/as-physics-2027-review/`.

## Full Accuracy and Delivery Audit

**Audit date:** 2026-09-09  
**Draft reviewed:** `LOCAL_PATH  
**Route:** OxfordAQA International Advanced Subsidiary Physics, code 9631, International market, 2027  
**Scope:** current 94-topic raster-routing draft, 128 atomic source points

## Executive conclusion

At the time of this historical audit, the draft was a substantial source-aligned
content candidate, but it was not approved for HTML or PDF delivery. This
statement is superseded by the current approved 94-topic delivery record.

- 94 final topics are present.
- 128/128 atomic source points are mapped.
- No duplicate, missing, or unknown source IDs were found in the current mapping.
- 94/94 concept entries contain an explanation, worked example, at least four
  solution steps, `visual_decision`, `visual_spec`, and `visual_guidance`.
- 94/94 topics currently route to `external-infographic` using APIMart GPT Image
  2 with a 4:3 landscape brief.
- 0/94 visual assets have been generated or semantically reviewed.
- The current topic split is based on atomic examinable points and teachable
  groupings, not a one-to-one rename of official section headings.
- The draft remains `draft-review-required` and `delivery_eligible: false`.

The content audit found eight bounded Writer revisions and two source-traceability
clarifications. All ten items must be resolved before content approval. After
that, the actual visual assets, rendered HTML, and the complete LLM review ledger
remain separate mandatory gates.

## Evidence reviewed

- `reports/as_physics_accuracy_001_047.md`
- `reports/as_physics_accuracy_048_094.md`
- Current `syllabus-outline.json`
- Current `concepts/concept_explanations.json`
- Current OxfordAQA specification extraction and qualification metadata

The review recalculated all 94 numerical worked examples and checked topic title,
source alignment, definitions, equations, units, scope boundaries, practical
requirements, and required visual fields. The audit covers the current 94-topic
raster-routing draft only; it does not reuse conclusions from the earlier
82-topic draft or the retired Chinese bypass output.

## Content revisions required

### Topic 010 — Equilibrium and resultant force

The worked calculation `T sin 35° = 50 N` is valid only when the cable angle is
35 degrees **above the horizontal**. Add that reference explicitly, or change the
component equation if the intended angle is measured from the vertical.

### Topic 041 — Alpha, beta and gamma properties and applications

The paper-thickness example can mis-teach the standard thickness-gauge mapping.
State the intended applications explicitly:

- alpha: very thin paper;
- beta: aluminium foil;
- gamma: thicker steel or another denser/thicker material.

Retain the explanation that the selected radiation must produce a measurable
count change while passing through the material.

### Topic 064 — Resonance applications

Do not state that all stationary waves are resonance phenomena. Explain that a
stationary-wave situation **may involve resonance when a periodic driver excites
a natural mode**. Keep the separate definitions of superposition, boundary
conditions, and resonance.

### Topic 065 — Wave quantities and phase

Define phase and phase difference explicitly in this topic, not only as a
reference to Topic 067. Add a short identification example such as in-phase,
antiphase, or quarter-cycle separation. Topic 067 may retain the numerical
degree/radian/cycle conversions.

### Topic 071 — Superposition and stationary-wave formation

The specification requires a graphical explanation. Add a real sequence or
annotated diagram showing two equal-frequency, opposite-travelling waves at
successive phases, their resultant, fixed nodes, and oscillating antinodes.
Prose saying that a diagram “should show” these features is insufficient.

### Topic 073 — Stationary-wave applications and harmonics

Add an explicit sound or microwave application checkpoint in addition to the
string example. Revise the terminology note to say that the exam uses “first
harmonic” and does not require “fundamental” or “overtone” as examination
terminology; do not present those words as universally forbidden teaching terms.

### Topic 078 — Young’s slits and diffraction practical

The practical requirement covers both Young’s-slit interference and diffraction
gratings. Keep the current Young’s-slit example, and add a separate grating data
or evaluation example using line density, measured angle/order, wavelength,
repeat readings, uncertainty, or comparison with an expected value.

### Topic 079 — Single-slit diffraction

Remove the unqualified claim that central brightness “may decrease”. The assessed
core is the central-maximum width: increasing wavelength or reducing slit width
increases the width. Any intensity statement must be conditional on a stated
experimental comparison and is optional rather than a core requirement.

## Source-traceability clarifications

### Topic 027 — Density

The official source statement combines density with Hooke’s law and the elastic
limit. The density-only teaching split is acceptable, but the outline and
provenance must explicitly record that the Hooke/elastic-limit clauses are
cross-covered by Topic 028. Do not imply that Topic 027 alone covers all of the
combined source statement.

### Topic 029 — Stress, strain and breaking stress

The official source statement also names elastic strain energy, which is taught in
Topic 030. Record that cross-topic treatment explicitly in the outline and
provenance.

These are traceability repairs, not numerical or conceptual failures in the
current topic explanations.

## Visual and layout gate

The current visual plan is directionally correct but not yet evidence of delivery.
The external route is available, so richer diagram-led visuals should be used for
topics that benefit from apparatus, processes, wave formation, radiation paths,
graphs, or modelled systems. SVG must remain an explicit exception for exact
geometry, notation, scale, or machine-readable structure; it must not be used as
a silent fallback for a richer visual.

Visual prompts must be landscape-first: 4:3 by default, with 3:2 acceptable.
Portrait 3:4 is not the default. Image text must be limited to short labels,
symbols, units, callouts, and at most one brief caption. Text-heavy posters or
miniature handbook pages do not satisfy the visual purpose.

Every generated visual still requires individual semantic review. The current
state is pending for all 94 visuals, so the visual gate is open and blocks
delivery.

## HTML, PDF, and delivery gates

The current draft has not passed the required complete LLM HTML review. No PDF
may be exported or presented as final until all of the following are true:

1. The ten content/source issues above are repaired in the authored artifacts.
2. The visual manifest is rebuilt for the repaired briefs.
3. All required external visuals are generated/imported and individually reviewed.
4. HTML is rendered from the current artifact and visually inspected in full.
5. Topic, visual, and holistic review-ledger entries bind the same current render
   snapshot and HTML hash.
6. The read-only delivery audit passes, after which PDF export and delivery-copy
   hashes are recorded.

Machine validation, file presence, image count, or an older PDF cannot substitute
for the LLM-owned content, visual, or HTML decisions.

## Recommended next action

Apply only the eight bounded Writer revisions and the two traceability updates,
then rerun the full 94-topic audit. Do not generate the 94-image batch or export
PDF before that re-audit passes. The next content review should also confirm that
the final split still groups atomic points by actual teachable/examinable skill
rather than by official section headings.

**Historical status at time of review:** `draft-review-required` /
`delivery_eligible: false` (superseded)
