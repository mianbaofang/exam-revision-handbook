from __future__ import annotations


def stylesheet() -> str:
    return """
:root {
  --ink: #172033;
  --muted: #5b677a;
  --paper: #fffaf1;
  --blue: #1354a5;
  --red: #b83246;
  --green: #1f7a5b;
  --gold: #d99a24;
  --line: #d7deea;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background: #eef2f7;
  font: 15px/1.65 "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
a { color: var(--blue); }
.cover {
  min-height: 100vh;
  padding: 46px max(28px, 8vw);
  color: var(--ink);
  background:
    linear-gradient(90deg, var(--blue) 0 22px, transparent 22px),
    linear-gradient(180deg, #edf4ff 0 38%, transparent 38%),
    var(--paper);
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 30px;
  border-bottom: 10px solid var(--gold);
}
.cover-mast {
  display: grid;
  grid-template-columns: 118px minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
  max-width: 980px;
}
.exam-board-badge {
  display: grid;
  place-items: center;
  min-height: 96px;
  color: #ffffff;
  background: linear-gradient(135deg, var(--blue) 0 64%, var(--red) 64% 100%);
  font-size: 28px;
  font-weight: 900;
  letter-spacing: .02em;
}
.exam-board-badge.board-edexcel {
  background: linear-gradient(135deg, #007b83 0 64%, #2d5aa7 64% 100%);
}
.exam-board-badge.board-caie {
  background: linear-gradient(135deg, #b42c35 0 64%, #173154 64% 100%);
}
.exam-board-badge.board-neutral {
  background: linear-gradient(135deg, #5b677a 0 64%, #172033 64% 100%);
}
.exam-board-name {
  padding: 16px 18px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.exam-board-name span,
.cover-identity-grid span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.exam-board-name strong {
  display: block;
  margin-top: 8px;
  font-size: 18px;
  line-height: 1.25;
}
.cover-title-lockup {
  align-self: center;
  display: grid;
  gap: 16px;
  max-width: 980px;
}
.qualification-pill {
  width: max-content;
  max-width: 100%;
  padding: 7px 11px;
  color: var(--blue);
  background: #ffffff;
  border: 1px solid #b8cce6;
  font-size: 12px;
  font-weight: 850;
  letter-spacing: .05em;
  text-transform: uppercase;
}
h1 { max-width: 920px; font-size: 52px; line-height: 1.05; margin: 18px 0; letter-spacing: 0; }
.cover-title-lockup h1 {
  margin: 0;
  font-size: clamp(44px, 8vw, 82px);
  line-height: .94;
}
.course-code {
  width: max-content;
  max-width: 100%;
  padding: 10px 14px;
  color: #ffffff;
  background: var(--red);
  font-size: 24px;
  font-weight: 900;
  letter-spacing: .02em;
}
.course-scope-note {
  max-width: 760px;
  margin: 0;
  padding: 12px 14px;
  color: #172033;
  background: #ffffff;
  border-left: 6px solid var(--gold);
  box-shadow: 0 0 0 1px var(--line) inset;
  font-size: 15px;
  font-weight: 750;
  line-height: 1.45;
}
.cover-identity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  max-width: 980px;
}
.cover-identity-grid div {
  min-height: 76px;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.cover-identity-grid strong {
  display: block;
  margin-top: 8px;
  font-size: 17px;
  line-height: 1.25;
}
.band, .topic {
  margin: 0 auto;
  padding: 34px max(24px, calc((100vw - 1120px) / 2));
  background: white;
  border-bottom: 1px solid var(--line);
}
.band > *,
.topic > * {
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
}
.student-overview { background: #fffaf1; }
.delivery-panel { background: #f7fbff; }
.delivery-status-grid {
  display: grid;
  grid-template-columns: minmax(180px, .28fr) minmax(0, .72fr);
  gap: 16px;
}
.delivery-state-badge {
  padding: 16px;
  color: #ffffff;
  background: var(--blue);
}
.delivery-state-badge span {
  display: block;
  font-size: 12px;
  font-weight: 850;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.delivery-state-badge strong {
  display: block;
  margin-top: 8px;
  font-size: 24px;
  line-height: 1.1;
}
.delivery-state-draft { background: var(--red); }
.delivery-state-review-ready { background: var(--gold); }
.delivery-state-final-ready,
.delivery-state-certified { background: var(--green); }
.delivery-state-detail {
  padding: 16px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.delivery-state-detail p { margin: 0 0 8px; font-weight: 750; }
.overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.overview-grid article {
  border: 1px solid var(--line);
  border-left: 5px solid var(--green);
  padding: 16px;
  background: #ffffff;
}
.source { background: var(--paper); }
.listing-note { padding: 10px 12px; background: #ffffff; border-left: 4px solid var(--gold); }
.language-policy { background: #f7fbff; }
.language-note { margin: -8px 0 16px; color: var(--muted); font-size: 13px; }
h2 { margin: 0 0 16px; font-size: 28px; line-height: 1.15; color: var(--blue); letter-spacing: 0; }
h3 { margin: 0 0 10px; font-size: 17px; color: var(--red); letter-spacing: 0; }
h4 { margin: 12px 0 6px; font-size: 14px; color: var(--blue); letter-spacing: 0; }
.icon {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  vertical-align: -4px;
  margin-right: 6px;
}
.guide-grid h3,
.practice h3,
.practice h4,
.story-modes h3,
.visual-example figcaption {
  display: flex;
  align-items: center;
  gap: 6px;
}
ul, ol { padding-left: 22px; }
li { margin: 5px 0; }
code { overflow-wrap: anywhere; color: var(--red); }
table { width: 100%; border-collapse: collapse; margin-top: 14px; }
th { background: var(--blue); color: #fff; text-align: left; }
th, td { border: 1px solid var(--line); padding: 10px 12px; vertical-align: top; }
.topic-nav {
  position: sticky;
  top: 0;
  z-index: 3;
  background: #f7fbff;
  box-shadow: 0 8px 18px rgba(23, 32, 51, .08);
}
.topic-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}
.topic-nav a {
  display: flex;
  gap: 8px;
  align-items: center;
  min-width: 0;
  padding: 8px 10px;
  color: var(--ink);
  text-decoration: none;
  background: #ffffff;
  border: 1px solid var(--line);
}
.topic-nav span {
  flex: 0 0 auto;
  color: var(--red);
  font-weight: 800;
}
.assessment-grid, .topic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.assessment, .logic-card, .practice {
  border: 1px solid var(--line);
  border-left: 5px solid var(--gold);
  padding: 16px;
  background: #fbfcff;
}
.guide-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.guide-grid article {
  border: 1px solid var(--line);
  padding: 14px;
  background: white;
}
.essence { border-left: 5px solid var(--gold) !important; }
.analogy { border-left: 5px solid var(--green) !important; }
.worked { border-left: 5px solid var(--blue) !important; }
.pitfall { border-left: 5px solid var(--red) !important; }
.topic:nth-of-type(odd) { background: #fbfcff; }
.practice-block { margin-top: 16px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.practice-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }
.practice-meta span {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  background: #edf4ff;
  color: var(--blue);
  font-size: 12px;
  font-weight: 800;
}
.practice-question { font-weight: 700; }
.visual-example {
  margin: 18px 0 0;
  padding: 8px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--red);
}
.visual-example figcaption {
  margin-bottom: 8px;
  color: var(--red);
  font-weight: 800;
}
.visual-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  align-items: start;
}
.visual-svg {
  display: block;
  width: 100%;
  height: auto;
}
.visual-notes {
  border: 1px solid var(--line);
  padding: 16px;
  background: #fbfcff;
}
.infographic-required {
  border-left-color: var(--gold);
}
.generated-infographic {
  border-left-color: var(--green);
}
.generated-infographic-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  align-items: start;
}
.infographic-image {
  display: block;
  width: 100%;
  max-height: 560px;
  object-fit: contain;
  background: #ffffff;
  border: 1px solid var(--line);
}
.infographic-card {
  border: 1px solid var(--line);
  padding: 16px;
  background: #fffaf1;
}
.visual-model,
.visual-source {
  display: inline-block;
  margin: 0 6px 12px 0;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.visual-model { background: #edf4ff; color: var(--blue); }
.visual-source { background: #fff3d8; color: #8a5f11; }
.visual-question {
  margin: 0 0 10px;
  font-weight: 700;
}
.visual-prompt {
  margin-top: 12px;
  padding: 10px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
}
.visual-prompt summary {
  cursor: pointer;
  color: var(--red);
  font-weight: 800;
}
.visual-prompt p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.story-modes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.story-modes article {
  border: 1px solid var(--line);
  padding: 14px;
  background: #ffffff;
}
.story-modes article:nth-child(1) { border-left: 5px solid var(--green); }
.story-modes article:nth-child(2) { border-left: 5px solid var(--blue); }
.story-modes article:nth-child(3) { border-left: 5px solid var(--gold); }
.story-modes p { margin: 0; }
.topic-diagram {
  margin: 16px 0 0;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--green);
}
.topic-diagram figcaption {
  margin-bottom: 10px;
  color: var(--green);
  font-weight: 800;
}
.concept-html-map {
  display: grid;
  grid-template-columns: minmax(220px, .38fr) minmax(0, .62fr);
  gap: 14px;
}
.concept-core {
  padding: 18px;
  color: white;
  background: #124f9b;
}
.concept-core span {
  display: block;
  color: #ffe4a9;
  font-size: 12px;
  font-weight: 800;
}
.concept-core strong {
  display: block;
  margin: 12px 0;
  font-size: 22px;
  line-height: 1.2;
}
.concept-core small {
  display: block;
  color: #dceaff;
}
.concept-html-map ol {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.concept-html-map li {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--line);
  background: #fbfcff;
}
.concept-html-map li span {
  grid-row: span 2;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: white;
  background: var(--green);
  display: grid;
  place-items: center;
  font-weight: 800;
}
.concept-html-map li strong {
  min-width: 0;
}
.concept-html-map li em {
  color: var(--muted);
  font-size: 12px;
  font-style: normal;
}
.source-snippets { margin-top: 14px; padding: 12px 14px; background: #f8fafc; border: 1px solid var(--line); }
.source-snippets summary { cursor: pointer; font-weight: 800; color: var(--blue); }
.source-snippets blockquote { margin: 6px 0 8px; color: var(--muted); font-size: 13px; }
.source-snippets.compact { background: transparent; border: 0; padding: 0; }
.source-snippets.compact blockquote { display: none; }
.stage-list li { padding: 10px 12px; background: #f3f7fb; border-left: 4px solid var(--green); }
.warning { color: var(--red); font-weight: 700; }
.final { background: #f4fff9; }
@media (max-width: 760px) {
  h1 { font-size: 38px; }
  .cover-mast, .cover-identity-grid, .delivery-status-grid, .overview-grid, .assessment-grid, .topic-grid, .practice-block, .guide-grid, .visual-grid, .generated-infographic-grid, .story-modes, .concept-html-map, .concept-html-map ol { grid-template-columns: 1fr; }
  .cover { padding: 36px 24px; }
  .cover-title-lockup h1 { font-size: 44px; }
  .course-code { font-size: 19px; }
  .topic-nav { position: static; }
}
@media print {
  @page { size: A4; margin: 3.5mm; }
  body { background: white; }
  body { font-size: 10.5px; line-height: 1.38; }
  .cover {
    min-height: 220mm;
    padding: 18mm 14mm;
    break-after: page;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .cover-title-lockup h1 { font-size: 42px; line-height: 1; }
  .course-code { font-size: 18px; }
  .course-scope-note { font-size: 11px; line-height: 1.35; }
  .band, .topic {
    break-inside: auto;
    page-break-inside: auto;
    padding: 4mm 0;
    border-bottom: 1px solid var(--line);
  }
  body > section:last-of-type {
    padding-bottom: 0;
    border-bottom: 0;
  }
  .band > *,
  .topic > * {
    max-width: none;
  }
  .topic-nav,
  .story-modes,
  .topic-diagram,
  .source-snippets,
  .visual-prompt {
    display: none !important;
  }
  h1 { font-size: 30px; line-height: 1.05; margin: 0 0 5mm; }
  h2 { font-size: 18px; line-height: 1.15; margin: 0 0 3mm; }
  h3 { font-size: 11px; margin: 0 0 2mm; }
  h4 { font-size: 10px; margin: 2mm 0 1mm; }
  p { margin: 1.5mm 0; }
  ul, ol { margin: 1.5mm 0; padding-left: 16px; }
  li { margin: .5mm 0; }
  th, td { padding: 4px 5px; }
  .overview-grid,
  .delivery-status-grid,
  .assessment-grid,
  .topic-grid,
  .guide-grid,
  .practice-block,
  .visual-grid,
  .generated-infographic-grid {
    gap: 3mm;
  }
  .guide-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .guide-grid article,
  .assessment,
  .logic-card,
  .practice,
  .visual-notes,
  .infographic-card {
    padding: 3mm;
  }
  .practice-block { grid-template-columns: 1fr; }
  .practice-block .practice:nth-child(n+2) { display: none; }
  .visual-example { margin: 2mm 0 0; break-inside: avoid-page; }
  .visual-example figcaption { margin-bottom: 1.5mm; }
  .visual-grid,
  .generated-infographic-grid {
    grid-template-columns: 1fr;
    gap: 2mm;
    align-items: start;
  }
  .visual-svg { max-height: none; object-fit: contain; }
  .infographic-image { max-height: 92mm; object-fit: contain; }
  a { color: inherit; text-decoration: none; }
}
"""
