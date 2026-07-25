# System Model

Skill: `exam-revision-handbook`

- Stability score: `95/100`
- Stability band: `governed`
- Doctrine: A handbook is deliverable only when its source, teaching, visual, review, and delivery states form one current evidence chain.

## System Boundary Map

- Owned job: Acquire official curriculum evidence, decompose it into atomic teaching points, write subject-specific teaching and practice, select and review educational visuals, render and personally review HTML, and export a hash-bound PDF only after approval.
- Output boundary: For each subject, one controlled handbook bundle containing current source evidence, atomic outline, teaching content, visual manifest and assets, approved HTML, review ledger, PDF, delivery copy, and matching hashes.
- Maturity assumption: `governed`
- Input boundary:
  - A complete preflight covering board or provider, qualification, A-Level stage when applicable, market, subject, exam year, language, work mode, batch scope, and output directory.
  - An explicit user answer about external image-generation capability plus a verified callable route when one is selected.
  - Official source evidence, or a user-accepted experimental manual import for unsupported curricula.
- Non-goals:
  - Automatic official-source acquisition for curricula outside the declared AQA, Edexcel, CAIE, and College Board AP routes.
  - Using Python, keyword rules, templates, or machine diagnostics to decide syllabus meaning, teaching content, visual semantics, or approval.
  - Exporting a PDF before complete LLM review and approval of the exact current HTML.
  - Sharing sampled review conclusions, outlines, approvals, or artifact state between batch subjects.
- Human judgment boundary:
  - Confirm the complete preflight and verify the selected image route before starting any downstream work.
  - Resolve official provider, market, qualification, stage, course, and year ambiguity instead of guessing or substituting.
  - Let the LLM decide syllabus meaning, atomic teaching points, teaching content, visual route, semantic correctness, and approval.
  - Require complete review of the exact current HTML and matching evidence hashes before authorizing PDF export.
  - Review every batch subject independently and never approve from a sample or another subject's state.

## Feedback Loops

### Preflight gate loop

- Signal: A required field is missing, ambiguous, inferred, or the selected image route has not been called successfully.
- Response: Stop, ask only for the missing decision, verify the route, and invalidate any prematurely created downstream artifacts.
- Evidence: workflow state and preflight record.

### Syllabus granularity loop

- Signal: A final topic maps only to a broad Topic or Unit container, lacks an independently assessable source requirement, or merges requirements without a teaching reason.
- Response: Return to official evidence, rebuild the atomic mapping, and re-audit source coverage before writing.
- Evidence: official requirement -> atomic point -> final topic -> visible handbook location mapping.

### Visual semantics loop

- Signal: A planned or rendered visual does not express a topic-specific structure, relationship, quantity, process, or spatial meaning, or contains incorrect labels, arrows, units, or relationships.
- Response: Reject the visual, revise its medium and source-bound specification, regenerate or replace it, and perform LLM semantic review again.
- Evidence: visual manifest, visual specification, rendered asset, and per-visual review decision.

### State invalidation loop

- Signal: A manifest rebuild, imported asset, outline, teaching input, visual decision, HTML, render snapshot, ledger, PDF, or delivery hash changes.
- Response: Invalidate every dependent approval and rebuild the chain from the earliest changed input using rebuild -> import -> approve -> render-only order.
- Evidence: artifact hashes and approval state ledger.

### HTML repair loop

- Signal: Complete visible LLM review finds a factual, teaching, visual, layout, encoding, or traceability defect in the current HTML.
- Response: Rewrite or repair the defect, rerender, inspect the complete new HTML, and repeat until the exact current hashes are approved.
- Evidence: HTML hash, render snapshot hash, item-level review ledger, screenshot locations, and repair round.

### Delivery and batch loop

- Signal: Any subject has pending, rejected, stale, missing, shared, or mismatched state before export or delivery.
- Response: Block PDF and batch completion for that subject, repair its own chain, then verify the approved PDF and delivery-copy hashes.
- Evidence: per-subject approval, PDF provenance, delivery audit, and batch completion matrix.

## Delay And Drift Watch

### Preflight bypass

- Watch signal: An agent starts retrieval, analysis, writing, or visuals before the structured preflight and image-route decision are complete.
- Countermeasure: Make preflight state the first blocking transition and invalidate all artifacts created before it.
- Cadence: every handbook run.

### Broad-topic decomposition

- Watch signal: The outline stops at Topic or Unit headings instead of independently assessable atomic teaching points.
- Countermeasure: Require the source-to-atomic-to-topic-to-location table and a coverage audit before writing.
- Cadence: every outline revision.

### Manifest and approval order drift

- Watch signal: Approval is recorded before a manifest rebuild or asset import, causing assets or decisions to disappear or reset.
- Countermeasure: Enforce rebuild -> import -> approve -> render-only and reject out-of-order transitions.
- Cadence: every visual state transition.

### Stale artifact hashes

- Watch signal: HTML, render evidence, approvals, PDF, or delivery copies refer to different input versions.
- Countermeasure: Invalidate downstream state on every upstream hash change and audit the complete chain before export.
- Cadence: every render and export.

### Semantic visual regression

- Watch signal: Decorative text cards, repeated SVG templates, or polished but incorrect images are accepted as explanatory visuals.
- Countermeasure: Require topic-specific graphical objects and item-level LLM semantic review of the rendered asset.
- Cadence: every planned and rendered visual.

### Sampled batch review

- Watch signal: One subject's outline, visual decision, HTML approval, or sampled result is reused to approve another subject.
- Countermeasure: Maintain independent subject state and block batch completion until every subject has its own current evidence chain.
- Cadence: every batch phase transition.

## Failure Pattern Map

1. Preflight bypass: return to preflight, verify the selected route, and invalidate premature work.
2. Syllabus under-decomposition: rebuild the atomic evidence map and repeat the coverage audit before writing.
3. Semantic ownership violation: move semantic decisions back to the LLM and retain Python only for deterministic support and gates.
4. Visual format substitution: judge the rendered meaning and reject semantically weak visuals.
5. State and hash divergence: invalidate from the earliest changed input and rebuild one current evidence chain.
6. False approval: perform full visible review and repair of the current HTML, then record hash-bound item-level evidence.
7. Batch conclusion sharing: invalidate the shared conclusion and complete each subject independently.

## Highest Leverage Moves

1. Block incomplete preflight.
2. Make atomic mapping an approved artifact.
3. Enforce rebuild -> import -> approve -> render-only and propagate invalidation.
4. Approve visual meaning, not file format.
5. Bind delivery to complete HTML review and current hashes.

## Reviewer Use

Approve only when one current, per-subject evidence chain proves complete preflight, atomic source coverage, LLM-owned semantics, reviewed visuals, fully repaired HTML, and hash-bound PDF delivery.
