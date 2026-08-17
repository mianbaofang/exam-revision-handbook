# Exact SVG Review Policy

Use this reference when the LLM Writer marks a visual as `complexity: "svg-basic"` with `svg_fit: "exact"`.

This is not a user-facing image-model choice. It is the review contract for simple diagrams whose meaning is fully carried by geometry, axes, labels, tables, trees, timelines, or simple flows.

## Use It For

- number lines, fraction bars, ratio blocks;
- function graphs, equation-balance visuals, distance-time graphs;
- statistics charts, scatter plots, probability trees, simple data tables;
- pH scales, reaction-rate curves, energy profiles;
- simple labelled geometry where the shape and labels are unambiguous.

## Route

- The LLM Writer decides whether the visual is needed.
- The LLM Writer may choose `svg-basic` only when the diagram is an exact fit and must include `svg_fit: "exact"`.
- The framework routes exact SVG work to the professional SVG path and records it in `images/visual_manifest.json`.
- The visual is not final until the SVG asset is reviewed or approved.

## Review Contract

Before approving an SVG asset, check:

1. the one sentence the visual must clarify;
2. the exact syllabus point or worked example step it supports;
3. the labels, units, symbols, and axes that must appear;
4. the risk that would make the visual misleading.

Approve only what can be supported by those items. Do not invent values, mechanisms, formulas, or exam claims that are not in the guide plan.

## SVG Rules

- Keep text as SVG `<text>` nodes where possible.
- Prefer clear axes, labels, and line weights over decorative style.
- Use restrained semantic color: one main color, one contrast color, and neutral annotation colors.
- Record reviewed SVG assets with `review_status: "reviewed"` or `review_status: "approved"`.
- Use `complexity: "infographic"` for rich composition, realistic scenes, multiple linked states, dense annotation, or anything that could become misleading as simple shapes.
