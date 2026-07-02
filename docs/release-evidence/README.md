# Release Evidence Manifests

This directory documents the lightweight evidence manifest expected for v0.4+
release claims. It is documentation only; generated handbook outputs, PDFs,
screenshots, downloaded specifications, and local review scratch folders must
stay out of Git unless a separate release task explicitly promotes a small
asset.

## Status Vocabulary

- `candidate`: route or sample exercises the pipeline, but it is not
  delivery-grade evidence. Candidate routes must not be described as
  release-ready.
- `draft`: a fresh output exists, but review still found pending concepts,
  pending complex images, PDF/export gaps, validation errors, or an Agent
  self-review block.
- `final-ready`: fresh evidence from the current code shows validation success,
  `final-review-packet.json` reports ready, concepts and visuals are reviewed
  or explicitly nonblocking, `agent-product-review.json` records the active
  Agent's visible-handbook review and repair pass, and the manifest records the
  exact commands and summaries.
- `certified`: final-ready evidence has also been reviewed and approved by the
  release owner or a subject-aware reviewer, with no code or asset drift after
  the evidence was captured.

No route is certified by default. A v0.3 `delivery_status: ready` packet is a
historical fact, not a standing v0.4 certification.

## Manifest Shape

For each release that claims draft, final-ready, or certified evidence, add a
small manifest such as `docs/release-evidence/v0.4/manifest.json`.

```json
{
  "release": "v0.4",
  "generated_at": "YYYY-MM-DD",
  "git_revision": "<commit sha>",
  "overall_status": "candidate",
  "entries": [
    {
      "id": "provider-level-subject-language",
      "status": "candidate",
      "provider": "oxfordaqa",
      "level": "igcse",
      "subject": "Chemistry",
      "language": "en",
      "commands": [
        "python -m intl_exam_guide generate ...",
        "python -m intl_exam_guide review --out <output-dir>"
      ],
      "validation_summary": {
        "error_count": 0,
        "warning_count": 0,
        "topics": 0,
        "practice_cards": 0
      },
      "final_review": {
        "delivery_status": "ready",
        "must_not_present_as_final": false
      },
      "product_review": {
        "complete": true,
        "artifact": "agent-product-review.json",
        "decision": "final-ready"
      },
      "visual_summary": {
        "pending_infographic_assets": 0,
        "generated_infographic_assets": 0,
        "svg_fallback_assets": 0
      },
      "pdf_summary": {
        "has_pdf": false,
        "pdf_pages": 0
      },
      "evidence_files": [
        "validation.json",
        "final-review-packet.json",
        "handbook-package.json",
        "images/visual_manifest.json"
      ],
      "notes": "Do not commit the output directory; record only the evidence summary."
    }
  ]
}
```

Keep manifests concise. They should let a reviewer reproduce and classify the
release claim without turning this directory into a generated-output archive.
