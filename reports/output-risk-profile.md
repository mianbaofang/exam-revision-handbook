# Output Risk Profile

## Top Risks
- The agent bypasses the blocking external-image capability preflight.
- Syllabus analysis stops at broad Topic or Unit headings.
- Manifest rebuild, asset import, approval, and rendering occur in the wrong order.
- A text-card SVG or semantically wrong image is accepted as a teaching visual.
- PDF export proceeds without complete current LLM HTML approval and matching hashes.
- Batch subjects share sampled or stale review conclusions.

## Required Constraints
- Block all work until structured preflight is valid.
- Keep syllabus meaning, teaching writing, visual judgment, and approval LLM-owned.
- Use rebuild -> import -> approve -> render-only ordering.
- Require complete current HTML review before PDF export.
- Bind every approval and delivery decision to current hashes.
- Complete every batch subject independently.

## Self-Repair Checks
- Check preflight state before every phase transition.
- Verify every final topic maps to independently assessable source evidence.
- Reject pending, rejected, stale, or hash-mismatched visual and review state.
- Inspect the complete visible HTML after every repair.
- Re-run the delivery audit immediately before PDF export.

The report is migration- and provider-independent; it governs workflow truth and handbook quality.
