# OxfordAQA International AS Physics 2027 Content Audit — Historical Superseded

> **Status update (2026-09-09):** This report records the earlier 33-topic
> candidate and is **superseded**. The current handbook uses the repaired
> 94-topic, atomic-exam-point split. Current approval evidence is in
> `artifacts/as-physics-2027-review/agent-product-review.json` and the current
> delivery pointers in the same directory.

Date: 2026-09-08

## Scope

- Official source: `source/oxfordaqa-2022-specification.pdf`, Version 5.1.
- Reviewed scope: International AS Physics 9631, Unit 1 and Unit 2, sections
  `3.1.1` through `3.5.11`.
- Handbook under review:
  `LOCAL_PATH
- Reviewed artifacts: `syllabus-outline.json`, `qualification.json`,
  `guide-plan.json`, `concepts/concept_explanations.json`,
  `images/visual_manifest.json`, and the rendered HTML.

## Topic Split

- The official AS specification contains 33 numbered subject-content sections.
  These sections are structural containers, not automatic final topics.
- The current handbook contains 33 topics and maps them one-to-one to those
  sections. This matches the official section count but does not yet satisfy the
  updated split rule in `SKILL.md` and `workflow-contract.md`.
- The current Analyst outline contains 128 atomic exam points grouped into
  those 33 section-level topics. On average, each topic collapses about four
  separately assessable source points.
- No AS section from `3.1.1` to `3.5.11` is omitted, but the topic boundaries
  need a new Analyst pass before this handbook can be treated as a final
  exam-point-based split.
- International A-level-only sections `3.6` to `3.13` are not treated as AS
  requirements.

## Accuracy Review

- Checked every topic against its official section title, source points and
  AS-only restrictions.
- Checked equations, symbols, units, definitions and qualitative claims for
  physics correctness.
- Checked all 33 worked examples and practice answers numerically.
- Checked the terminology and exclusions explicitly named by the
  specification, including candela, dimensional analysis, Malus's law,
  critical field, spectrometer operation, potentiometer operation, atomic mass
  unit, exponential decay and `E = mc^2`.

## Fixes Applied

- T27 `Superposition and stationary-wave patterns`: replaced the terms
  `fundamental` and `overtone` with `first harmonic`, as required by section
  `3.5.5`, and regenerated the T27 visual with the corrected terminology.
- T16 `Decay, half-life and radiation`: added the complete thickness-measurement
  application: alpha for very thin material such as paper, beta for thin metal
  foil such as aluminium, and gamma for thicker or denser material such as
  steel.

## Verification

- Quality inspection after repair: `pass`.
- Topic count: `33`.
- Reviewed concept explanations: `33`.
- Reviewed visuals: `33`; pending complex visuals: `0`.
- ASCII maths residue: none.
- Placeholder hits: none.
- Missing visual guidance: none.

## Non-Blocking Notes

- The structural validator still prefers four or more public solution steps
  for every worked example. Several examples use three correct, sufficient
  steps. This is a formatting preference, not a physics or syllabus error.
- This audit checks the handbook against the official specification. It does
  not claim access to unpublished exam questions, mark schemes or examiner
  reports.
- The current handbook content can be reused as source material, but its
  33-topic table of contents must be re-split by atomic exam point before the
  next final delivery.
