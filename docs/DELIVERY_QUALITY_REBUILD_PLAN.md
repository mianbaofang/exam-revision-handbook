# Delivery Quality Rebuild Plan / 交付质量重造计划

Date: 2026-07-01

## Verdict

The current project is safer than the earlier flat generator because it marks
unfinished outputs as `draft` and blocks obvious final-delivery claims. It is
not yet a product that can honestly promise 95%+ student-usable accuracy across
three exam boards and many subjects.

The main failure is architectural: validation currently proves that a package
has the expected files, manifests, status flags, and some anti-regression rules.
It does not prove that the handbook is a good revision guide for a child.

For this project to be considered successful, a generated handbook must pass
both machine checks and content checks:

- the official syllabus was parsed into the right teachable units;
- each unit has a specific, source-bound explanation, not a repeated checklist;
- examples match the current subject and topic;
- visuals are either deterministic and correct, or generated/imported and
  reviewed;
- HTML/PDF can be opened and sampled without blank pages or broken sections;
- the final status is based on evidence, not on optimistic wording.

## Critical Findings

### 1. Safety gates are not the same as quality proof

Current `draft / final-ready / certified` status handling prevents incomplete
work from being called final, but it does not certify subject accuracy. A route
can have zero validation errors while still containing weak explanations,
low-value examples, or too many pending concept jobs.

Required v0.5 change: introduce a `StudentUsabilityReview` layer with sampled
unit review, explanation specificity checks, practice relevance checks, visual
correctness checks, and PDF readability checks. This must produce a score and
human-readable evidence, not only pass/fail gates.

### 2. Concept writing is still outside the core closed loop

The project writes `concepts/concept_jobs.json`, but the base generator does not
automatically complete the second writing/review pass. That is why a handbook
can be structurally complete while the visible "what to master" or concept
text is still weak.

Required v0.5 change: the default product flow must be:

1. generate base guide;
2. create concept jobs;
3. run the source-bound LLM writing pass;
4. run a review pass against the same job;
5. import accepted explanations;
6. re-render and re-review.

If step 3 or 4 is unavailable, the output must stay draft and show the exact
pending concept count on the first screen.

### 3. Subject coverage is too shallow for the market promise

The six priority subjects are Mathematics, Physics, Chemistry, Economics,
Biology, and Accounting. Business and History also need real sampling because
students do use them. The current subject packs are useful contracts, but they
are still thin. They do not yet contain enough per-subject rubric knowledge to
judge whether examples and explanations are genuinely good.

Required v0.5 change: create priority subject packs with explicit rubrics:

- Mathematics: definitions, symbolic methods, graph/geometry correctness,
  worked calculation checks.
- Physics: quantities, units, laws, diagrams, data interpretation.
- Chemistry: particles, bonding, reactions, observations, quantitative
  chemistry boundaries.
- Biology: structure/function, processes, experimental evidence, diagrams.
- Economics: agents, incentives, diagrams, calculation and evaluation.
- Accounting: ledgers, statements, adjustments, reconciliation, ratio use.
- Business: business context, stakeholder/customer/operation/finance examples.
- History: chronology, cause/consequence, source evidence, change/continuity.

Generic subjects may use the generic source-bound pack, but they must not borrow
templates from the wrong subject.

### 4. Visual routing is still keyword-driven

The current visual decision layer mostly uses subject profiles and keyword
rules. This is acceptable for MVP triage, but it is not enough for high-stakes
student material. Keyword routing caused repeated SVGs and topic/image mismatch
before, and it can do so again when a new board words the syllabus differently.

Required v0.5 change: replace "keyword chooses renderer" with a typed visual
contract:

```text
VisualNeed
  claim_to_explain
  required_labels
  required_data_or_values
  visual_kind
  renderer_capability
  unsupported_claims
  review_risk
```

The renderer should accept the typed contract, not just a free-text visual
type.

### 5. SVG must be exact and reviewed

SVG is suitable only for simple, source-bound figures whose meaning is fully
carried by exact geometry, axes, labels, simple tables, or simple flows. It is
not a replacement for complex teaching infographics. The current framework must
block non-exact SVG and unreviewed SVG from final delivery.

Required v0.5 change: keep SVG only for `svg_fit: "exact"` cases with reviewed
or approved assets, and move complex cases to pending infographic jobs or
reviewed raster assets.

### 6. External image generation is a queue/import flow, not a product loop

The current open-source project can write `images/infographic_jobs.json` and
import generated images with `scripts/import_infographic_assets.py`. It does
not yet provide a single user-facing flow that says:

"These 7 images are required. I will generate them with the approved route,
review them, import them, re-render the guide, and run final review."

Required v0.5 change: add a visual orchestration command that reads pending
jobs, calls the selected external image workflow when available, stores
metadata, imports assets, and re-runs final review.

## Reviewed Visual Candidates

The framework may accept these categories as exact-SVG candidates only when the
LLM writes `svg_fit: "exact"` and the asset is reviewed or approved. They are not
local deterministic fallbacks for complex visuals.

| Area | Exact-SVG candidate categories |
|---|---|
| Mathematics | number line, fraction bar, ratio blocks, function/algebra graph, equation balance, statistics chart, probability tree, simple right triangle, Venn diagram |
| Mechanics / Physics-like math | distance-time graph, force arrows |
| Chemistry | particle states, pH scale, reaction rate curve, energy profile, gas test chart, bonding sketch, organic/reaction sketch, chemical analysis sketch |
| Economics | demand/supply market diagram, simple economic flow |
| Accounting | source-document to ledger flow, reconciliation flow, trial balance table, control account diagram, suspense/error correction flow, incomplete-records flow, basic financial-statement layout |
| Business | stakeholder map, ownership comparison, cash-flow timeline, break-even chart, marketing mix quadrant, segmentation map, organisation structure, quality checkpoint, operations flow |
| History | timeline, cause/consequence chain, source evidence organizer, change/continuity comparison |

These are not enough for "professional image-rich handbook" quality. They cover
simple reproducible figures only after exact-fit review. Complex diagrams should
not be squeezed into these categories.

## Visuals That Should Require External Generation Or Reviewed Assets

Use external image generation, a designer workflow, or a subject-specific
scripted renderer for:

- complex geometry transformations, constructions, bearings, vectors, and
  multi-step graph annotations;
- chemistry bonding structures, organic pathways, electrolysis, reactivity, and
  apparatus-heavy diagrams;
- physics circuits, waves, energy transfer, and context-specific mechanics
  scenes;
- biology cell/organ/process diagrams and experimental setups;
- dense economics/business/accounting infographics with several labelled
  relationships;
- any visual where wrong labels would mis-teach the topic.

If no callable route exists, these must stay as pending jobs. They should not be
silently replaced by generic SVG.

## Free Built-In Renderer Candidates Before External AI

The open-source project can improve quality without private image APIs by adding
free deterministic renderers:

| Renderer | Good for | Why |
|---|---|---|
| Matplotlib | function graphs, statistics charts, motion graphs, reaction curves, economics curves | precise axes, ticks, labels, numerical control |
| Graphviz or Mermaid rendered through browser | process flows, dependency maps, cause/consequence chains, accounting flows | structured diagrams with less hand-coded SVG repetition |
| Pillow | final raster composition, labels, print-safe image cards, imported asset normalization | consistent size, compression, and PDF-safe output |
| SymPy plus Matplotlib | algebra/function plots and symbolic labels | safer math plots than hand-shaped curves |
| NetworkX plus Matplotlib | relation maps and simple networks | useful for stakeholder/source/cause maps |

These should be optional dependencies grouped as `visual` extras. The base
package should still run without them, but the final-ready visual route should
prefer them when installed.

## External Image Flow

External image generation must be a post-base-guide step. The user should not
be asked to choose an image model before we know which visuals are needed.

Required flow:

1. Generate the base handbook with `prompt-queue`.
2. Inspect `images/visual_manifest.json` and `images/infographic_jobs.json`.
3. Show the count and IDs of required complex infographics.
4. Confirm the callable route:
   - installed `image-gen-flow` skill, such as GPT Image 2 or Qwen Image;
   - custom script;
   - custom provider config using environment variables;
   - existing reviewed asset directory.
5. For each pending job, submit only the content prompt: topic, concept,
   required labels, language, and forbidden additions. Do not include logos,
   exam-board branding, textbook names, badges, or watermarks.
6. Save each result as `visual_001.png`, `visual_002.png`, etc.
7. Import with:

```bash
python scripts/import_infographic_assets.py <output-dir> --asset-dir <asset-dir> --provider <provider-name>
```

8. Re-render HTML/PDF.
9. Run final review.
10. Keep the output as draft unless all pending concepts, images, validation,
    PDF, and sampled content checks pass.

## Required Sampling Matrix

The next release cannot be judged by one AQA Mathematics sample. Minimum v0.5
evidence should include:

- AQA/OxfordAQA: Mathematics plus one science or humanities/business subject.
- Pearson Edexcel: Accounting or Business plus one science/humanities subject.
- Cambridge/CAIE: Economics or Accounting plus one science/humanities subject.
- Priority matrix: at least one current sample for each of Mathematics,
  Physics, Chemistry, Economics, Biology, Accounting.
- Supporting matrix: at least one current sample for Business and History.

Each sample must be opened and manually inspected at the rendered HTML/PDF
level. Machine validation alone is not enough.

## Definition Of 95% Student-Usable

"95% correct" cannot mean "all tests pass." It needs a review rubric.

For a handbook to be called student-usable:

- no critical board/subject/topic mismatch;
- no repeated generic concept explanations in sampled units;
- no cross-subject example leakage;
- no unsupported exam claims;
- no broken or blank major sections;
- no complex visual presented as final without reviewed asset status;
- at least 95% of sampled units must be rated usable for a student to revise
  from without extra explanation.

Certification requires a recorded reviewer, sample size, sampled unit IDs,
issues found, and final status.

## v0.5 Implementation Order

1. Add `StudentUsabilityReview` and sample-evidence files.
2. Close the concept-writing loop so final-ready cannot happen with pending
   concept jobs.
3. Add typed visual contracts and renderer capability checks.
4. Add optional free deterministic renderers under a `visual` extra.
5. Add the external image orchestration command.
6. Build the required three-board subject sampling matrix.
7. Only then update public release claims.
