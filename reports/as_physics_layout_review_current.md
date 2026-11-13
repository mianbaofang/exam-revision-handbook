# AS Physics Layout Review — Historical Superseded Report

> **Status update (2026-09-09):** This report is retained as historical evidence
> from the pre-repair layout pass. It is **superseded** and must not be used as
> the current delivery decision. The current approved HTML is bound to
> render snapshot `309f262141e886027dfe8023cfce5977c833c0fc7a01121f757793fa8559a850`
> and HTML SHA-256
> `4264385f0bfc4f4ea8dd0714803823d0aac32a598fc66ffef4d98ad3033d3b94`.
> Use `artifacts/as-physics-2027-review/agent-product-review.json`,
> `current-render.json`, and `current-delivery.json` for the current status.

**Review date:** 2026-09-09  
**Reviewed HTML:** `artifacts/as-physics-2027-review/oxfordaqa-as-a-level-physics-topic-split-draft.html`  
**HTML SHA-256:** `a04686db51c0a3832f4fdc1342254e5dfd9ce4852355706158d152aedc9ba21f`  
**Historical status at time of review:** `ISSUE — superseded; not the current delivery decision`

## Evidence reviewed

- `artifacts/as-physics-2027-review/qa/desktop-top.png`
- `artifacts/as-physics-2027-review/qa/desktop-topic071.png`
- `artifacts/as-physics-2027-review/qa/mobile-topic071.png`
- `artifacts/as-physics-2027-review/qa/desktop-topic094.png`
- `artifacts/as-physics-2027-review/qa/desktop-full.png` (dimensions and file integrity checked; the very tall raster is not suitable for direct in-app preview)
- `artifacts/as-physics-2027-review/qa/full-review/topics-01.jpg` through `topics-08.jpg`
- `artifacts/as-physics-2027-review/qa/full-review/visuals-01.jpg` through `visuals-08.jpg`
- Current HTML, `sections/00_css.txt`, `sections/01_cover.txt`, and package metadata.

## PASS

### Document language and glossary

- The current HTML declares `lang="en"` and the handbook body is English.
- The HTML contains 94 topic sections and 94 generated infographic placements.
- The professional glossary is present with 50 rows and the headers `Simplified Chinese`, `English exam term`, and `Exam use`. This matches the intended English-first handbook with Chinese term support.

### Cover

- The cover renders without clipping or overlap in `desktop-top.png`.
- The source uses the project AQA template class `cover-template-aqa` and includes Oxford International AQA Examinations, AQA, AS entry code `9631`, target year `2027`, and specification version `5.1`.
- The cover hierarchy is readable at desktop size: board identity, qualification title, course identity, code, year, and version are visually separated.

### Visual assets

- The 149 raster assets in the current package are all `1448×1086`, i.e. 4:3 landscape. No standalone SVG visual assets are present.
- The contact sheets show raster infographics and diagrams rather than the earlier simple SVG fallback style. Sampled pages such as T71 and T94 use diagrams that directly support the topic concept.
- The reviewed contact sheets show no obvious image clipping, broken references, or image/text overlap.

### Desktop topic layout

- `desktop-topic071.png` and `desktop-topic094.png` show a stable topic structure: title, key ideas/exam logic, explanation cards, generated infographic, visual prompt/source anchor, and worked example.
- The infographic and visual-notes block are in the same screen-flow section on desktop, with no visible overlap or horizontal overflow.
- The generated diagrams are large enough to inspect on desktop and preserve the 4:3 aspect ratio.

### Mobile layout

- `mobile-topic071.png` shows the responsive grid collapsing to one column as intended.
- Headings and cards wrap without visible clipping, horizontal overflow, or overlapping blocks.
- The topic title, teaching explanation, visual prompt, and worked example remain in a coherent reading order.

## ISSUE

### 1. Print CSS still forces visual notes onto a new page — blocking

The current HTML and source CSS still contain:

```css
.generated-infographic .visual-notes {
  break-before: page;
  page-break-before: always;
}
```

at `sections/00_css.txt` lines 830–832 (the same rule is embedded in the current HTML). This contradicts the intended layout of keeping a short visual explanation with its 4:3 image when the page can fit it. The current screen screenshots cannot prove print pagination; a fresh HTML render followed by print/PDF inspection is required after changing this rule.

### 2. Mobile infographic text is too small — blocking for mobile study use

At 390 px wide, the 4:3 image in `mobile-topic071.png` is reduced to roughly the content width. The diagram remains visible, but labels, axis text, and equations inside the raster are difficult to read without zooming. The surrounding HTML text is readable; the issue is the text baked into the image. The mobile layout needs either a deliberate large-image treatment, a per-topic image page/zoom affordance, or a mobile-specific presentation rule. Do not solve this by shrinking the body text further.

### 3. Desktop card grid has avoidable empty space — polish issue

On `desktop-topic071.png` and `desktop-topic094.png`, the two-column top grid leaves a large blank area beside the shorter `Key Ideas` content while the `Exam Logic` card is taller. This does not cause overlap, but it makes the page feel loose and increases vertical scanning distance. It is a layout-polish issue rather than a correctness failure.

### 4. Cover is a project-generated AQA-style template, not a verified official OxfordAQA cover asset

The source uses the project class `cover-template-aqa`, but no official OxfordAQA Physics cover-template image or PDF asset was found in the package. The cover therefore passes as the project template implementation, but should not be described as an official reproduced cover until an official template reference is supplied and checked.

### 5. Review metadata is stale and inconsistent with the current HTML — release-evidence issue

- `current-render.json` matches the current HTML hash, but `final-review-packet.json` still records the older hash `0b683409...`.
- `validation.json` still points to the old desktop path and the old seven-section package, while `handbook-package.json` records the current `LOCAL_PATH package with eight sections including `02_professional_glossary.txt` and `output_language: zh-CN`.
- These metadata mismatches do not change the pixels in the reviewed HTML, but they prevent an auditable final approval record.

## Verdict

The current HTML is **structurally usable for continued review**: English-first body, Chinese glossary support, AQA-style cover, 94 topic sections, and 4:3 raster infographics are present, and the sampled desktop/mobile pages have no visible overlap or clipping. It is **not ready for PDF export or final delivery** because the print stylesheet still splits visual notes from their image, mobile infographic text is too small for comfortable study, and the review metadata is not bound to the current HTML.

## Required next actions

1. Remove the forced print page break from `.generated-infographic .visual-notes`, rerender the HTML, and inspect representative printed pages.
2. Add a deliberate mobile image-reading treatment without changing the English-first content model.
3. Refresh `validation.json`, `final-review-packet.json`, and the review evidence so they reference the current eight-section package and current HTML hash.
4. Re-run the full visual review and create `agent-product-review.json` only after the repaired HTML has been inspected.
