# Project Hot Review - 2026-07-03

## Executive Verdict

The project can produce useful handbook packages, but it is not yet a
reliably autonomous, 95%+ student-ready generator across AQA, Pearson Edexcel,
and CAIE subjects.

The main failure is not one AQA AS Mathematics bug. The main failure is that
the product promise is ahead of the production chain. The repository now has
contracts for source-bound writing, product review evidence, visual routing,
and multi-agent roles, but those contracts are not yet a fully enforced
runtime that can consistently generate, inspect, repair, and certify a random
board/subject request without the active user Agent doing manual rescue work.

## What Happened In The Latest AQA AS Mathematics Run

The route had already been exercised several times, but the visible handbook
still exposed delivery-grade problems:

- roadmap mastery text repeated across independent topics;
- topic explanations fell back to generic mathematical wording instead of the
  specific syllabus point;
- trigonometry, differentiation, circle geometry, kinematics, and fixed-plane
  impact routing crossed concepts or reused nearby language;
- adjacent SVG visuals could still look duplicated or teach the wrong emphasis;
- the final PDF looked ready only after manual inspection, targeted repair,
  rerendering, and a second product review pass.

One important nuance: mechanics topics such as constant acceleration, Newton's
laws, forces, momentum, and collisions are valid AS Mathematics mechanics
content. The bug is not that mechanics appeared in Mathematics; the bug is that
the handbook must present them as mathematical modelling topics, not as loose
physics-topic spillover.

## Root Causes

### 1. Validation Passed The Wrong Level Of Quality

The existing checks are good at confirming that files exist, counts look
reasonable, obvious pending items are tracked, and known bad strings are absent.
They are not enough to prove that a child can use the handbook.

A guide can pass structural checks while still having:

- repeated topic explanations;
- concept text that is locally grammatical but pedagogically empty;
- a visual that exists but is the wrong visual;
- source-bound but poorly selected source points;
- PDF pages that are technically nonblank but visually weak.

### 2. Multi-Agent Is Mostly A Contract, Not A Runtime

The Skill and output metadata describe roles such as syllabus analyst,
handbook writer, and independent final reviewer. That is necessary, but not
sufficient.

Today the Python pipeline does not truly spawn independent agents, isolate
contexts, compare their outputs, or force a repair loop before final handoff.
The active user Agent still has to notice problems, patch code, rerender, and
rerun review. That is why the workflow still feels like manual debugging rather
than automatic multi-agent production.

### 3. Concept Writing Still Has Too Much Programmatic Fallback

The system says final explanations should come from source-bound writing jobs.
In practice, deterministic fallback and topic-family routing still shape too
much student-facing text. That creates repeated "what to master" phrasing and
near-identical explanations when the topic title changes but the family route
does not.

For a cross-subject project, this is dangerous. A fallback that sounds safe in
Mathematics can become wrong in Economics, Accounting, History, Biology, or
Chemistry.

### 4. Source Extraction Is Not Normalized Enough Across Boards

AQA/OxfordAQA, Pearson Edexcel, and CAIE specifications use different layouts,
labels, bullet styles, tables, options, and boilerplate. The current pipeline
has filters and subject profiles, but it does not yet have a strong enough
normalization layer that converts every source into the same trusted unit
model before writing begins.

This leads to downstream bugs:

- shell text becomes student-facing content;
- broad headings masquerade as independent knowledge points;
- option codes are mistaken for subject codes;
- unrelated examples leak through a generic subject profile;
- source points are technically official but not the right teaching unit.

### 5. Visual Routing Is Under-Specified

The intended visual stack is correct in principle:

- local deterministic SVG for exact simple diagrams;
- Kroki/professional diagrams for flows, hierarchies, timelines, relationship
  maps, and concept maps;
- external image models for dense text+diagram educational infographics.

The implementation still does not consistently decide which layer is required.
It can overuse local SVG, underuse external infographics, or mark too many
medium visuals as "good enough" because an asset exists.

For STEM, exact diagrams matter. For humanities and social-science subjects,
high-density infographics may be more useful. The routing decision must be
made from the teaching need, not from renderer availability.

### 6. PDF/HTML Review Is Too Late

Layout issues such as cramped visual interiors, poor scaling, blank pages,
student-facing implementation labels, and weak final status pages were found
after generation. The pipeline needs rendered-output review before handoff, not
only after a user complains.

### 7. Release Evidence Has Been Too Optimistic

Previous sample matrices showed that routes could run. That is not the same as
being student-ready. A validation-clean sample should be called candidate or
review-ready unless a visible product review has inspected the rendered
handbook, visuals, PDF pages, glossary policy, and syllabus alignment.

## What Is Actually Fixed In v0.4.3

v0.4.3 is a corrective release for the latest AQA AS Mathematics failures:

- topic-specific mathematics concept routing was tightened;
- repeated mastery/explanation phrasing was reduced and regression-tested;
- practice examples were improved for the affected mathematics families;
- SVG routing was corrected for nearby circle and mechanics visuals;
- rendering contracts were repaired;
- the local AQA AS Mathematics sample was rerendered and product-reviewed.

This does not certify the whole project.

## What Remains Unfixed

- No real Python-level multi-agent orchestrator yet.
- No independent reviewer context enforced by runtime.
- No automatic repair loop that can rewrite, rerender, and re-review without
  the active user Agent intervening.
- No broad hand-inspected matrix across AQA, Pearson Edexcel, and CAIE for the
  priority subjects.
- No reliable subject-pack certification for Mathematics, Physics, Chemistry,
  Economics, Biology, Accounting, Business, or History.
- No visual quality scoring that distinguishes "asset exists" from "visual is
  pedagogically correct and readable".
- No guarantee that a random course request can finish in ordinary user time
  rather than hours of repair.

## Recommended Rebuild Direction For Fable

### Product Contract

The product should be reframed as:

1. generate a candidate handbook;
2. run independent review agents;
3. repair until final-ready or clearly stop as draft;
4. only then present the user-facing PDF.

Do not market a guide as final just because files exist or validation is clean.

### Runtime Architecture

Use a real orchestrated pipeline:

1. `SourceAgent`: discover official page/PDF and extract raw syllabus evidence.
2. `CourseSpecAgent`: normalize source evidence into `CourseSpec` and
   `LearningUnit` records.
3. `WriterAgent`: write source-bound `PedagogicalUnit` content and practice.
4. `VisualAgent`: decide text-only, local SVG, Kroki/professional diagram, or
   external infographic from teaching need.
5. `LayoutAgent`: render HTML/PDF and capture page samples.
6. `ReviewAgent`: independently inspect syllabus coverage, topic content,
   visuals, glossary policy, and rendered pages.
7. `RepairAgent`: patch content/assets/layout, then rerun rendering and review.

The writer must not approve its own output.

### Evidence Model

Each run should produce a compact, inspectable packet:

- official source URL and PDF hash;
- normalized unit list;
- concept-writing jobs and reviewed explanations;
- visual decision table with renderer choice and reason;
- rendered PDF page count and sampled screenshots;
- duplicate text/visual checks;
- reviewer findings and repairs;
- final state: `draft`, `review-ready`, `final-ready`, or `certified`.

### Subject Coverage Strategy

Prioritize a certification matrix instead of one-off fixes:

- AQA/OxfordAQA, Pearson Edexcel, and CAIE;
- Mathematics, Physics, Chemistry, Biology, Economics, Accounting;
- plus Business and History as cross-domain checks.

Each priority subject should have at least one small golden syllabus fixture and
one full visible handbook audit before claims are made.

### Visual Stack

Keep local SVG only for exact, simple, deterministic diagrams. Use professional
diagram renderers for structured diagrams. Use external image models only when
the concept needs dense, student-friendly infographic layout.

Recommended built-in/free diagram layer:

- Kroki for Mermaid, Graphviz, PlantUML, BlockDiag, SeqDiag, ActDiag, BPMN, and
  related structured diagrams;
- local SVG/matplotlib-style scientific vectors for axes, curves, geometry,
  probability trees, distributions, pH scales, energy profiles, and charts.

External image models should remain a reviewed asset-import step, not a silent
fallback.

## Release Recommendation

Ship v0.4.3 only as a corrective release with honest status wording. Do not use
it to claim all-board/all-subject readiness.

The next meaningful milestone should be a rebuild of the generation runtime
around real multi-agent orchestration and automatic repair, followed by a small
but hand-inspected board/subject certification matrix.
