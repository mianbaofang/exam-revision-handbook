# Skill Workflow Boundary

This repository version of the Skill is a framework and LLM operations guide. It
is not an automatic content generator. It contains a narrow delivery gate
because an approved HTML/PDF pair must be bound to one immutable render and
cannot be inferred from file presence or modification time.

The workflow is a lightweight three-role LLM framing, not mandatory multi-agent orchestration. The same host LLM may perform the steps sequentially, or the user may choose to delegate them to separate agents:

1. Analyst: reads `source/specification.md`, `source/markdown-extraction.json`, and `syllabus-evidence.json`, then writes `syllabus-outline.json` with `source_inputs` and `cross_check` audit fields.
2. Writer: writes `concepts/concept_explanations.json`, `mastery_summary`, and per-topic `visual_decision` records.
3. Reviewer: the LLM personally opens the rendered HTML, compares it with evidence and outline files, returns every fixable issue to the Writer, and repeats the render-and-visible-review loop until the current HTML passes. The machine delivery audit checks artifact identity and completeness only; it never supplies the LLM decision.

The Reviewer records per-item evidence and visible screenshot/browser viewport
locations in Topic/Visual shards of at most 25 items and separately records a
holistic review of the complete assembled HTML.
Python may hash those LLM-authored files into `review-ledger/index.json`; it
cannot fill their decisions. The compact product-review summary references that
index and the current render snapshot.

Before source acquisition, the first preflight exchange must ask whether the
user can provide or enable a callable external image-generation Skill or tool.
The Agent waits for that answer and never silently defaults to local generation.
The entire first response is a structured fixed-choice form: board, level,
course market, subject, year/range, support language, one of the six supported explanation
styles, workflow mode, batch scope, and output directory are collected together
with the image-capability answer. Missing or invalid fields keep the project
blocked; the Agent preserves answered fields and may not begin discovery,
analysis, writing, visual planning, rendering, or PDF work until the form is
complete. A named image route also remains blocked until it is actually
callable and recorded as verified.

The Writer's visual judgment applies to all subjects. Every topic needs a recorded `visual_decision`; `text-ok` is allowed only when `no_visual_reason` explains why a separate visual would not add learning value. The Reviewer must check every final topic, worked example, answer, source anchor, and rendered visual for factual and semantic accuracy, as well as cross-page repetition and notation residue in HTML. Python diagnostics cannot approve the handbook. PDF export is a separate final step allowed only after `agent-product-review.json` records complete LLM coverage and approval for the exact current HTML SHA-256 and `current-render.json` verifies the immutable render-input snapshot. Export first creates a candidate, then runs technical checks, writes an immutable record under `pdf-exports/`, and finally updates `current-pdf.json`. Any later input or HTML change invalidates the approval and marks the former PDF historical without deleting it.

Visual assets have a separate state transition and must follow this order:

```text
Writer visual specs -> explicit manifest refresh for a new plan
-> generate/import assets -> LLM visual decision
-> render-only HTML -> complete HTML review -> product approval -> PDF
```

An existing `visual_manifest.json` is render-only by default. Rebuilding it
after asset import or after writing approval can reset decisions and detach
assets from the current review cycle. Reuse is allowed only for an unchanged
source-bound `spec_hash`; changed specs reset asset and visual-review state.
Asset import resets `visual_need.reviewer_visual_decision` to `pending` while
preserving the separate asset `review_status`. Old unreferenced files remain
historical unless explicit cleanup is approved. Any plan, concept, manifest, or
asset mutation requires a new HTML snapshot and complete LLM review; hashes are
mechanical blockers, not substitutes for that review. The delivery gate also
requires the current manifest to match the current plan's visual briefs by
count, derived key, and source-bound `spec_hash`; direct `render_html()` calls
cannot bypass that binding check.

Python may only:

- discover and download official sources;
- extract page-level syllabus evidence;
- invoke external MarkItDown / isolated environment to create `source/specification.md` and `source/markdown-extraction.json` for official PDF runs;
- validate JSON contract consistency;
- import LLM-written JSON artifacts;
- render HTML before review and promote a candidate PDF only after the read-only delivery gate, hash-bound LLM HTML approval, and technical PDF checks;
- write immutable PDF/copy records and explicit current pointers; never infer formal delivery from modification time;
- write mechanical manifests and review packets, including the v0.5 visual route/asset split.

Python must not:

- decide topic boundaries or syllabus splits, including from Markdown headings, tables, or bullets;
- upgrade old outputs into current-contract outlines;
- write teaching content;
- invent `mastery_summary` text;
- decide whether a topic needs a visual;
- approve final handbook quality.
- create, infer, or substitute the LLM HTML-review decision from validation, quality inspection, parsed HTML, screenshots, or review packets.
- treat a Python-generated plan, concept fallback, or visual fallback as formal student-ready content. Those artifacts may remain as clearly marked demo/legacy drafts only.

Do not add project-manager roles, quality-inspector roles, multi-agent orchestration requirements, release-state certification, or extra delivery states unless the user explicitly asks for release infrastructure. The normal Skill flow should stay small enough to read and run in one sitting.
