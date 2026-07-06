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
  --cover-bg: #071a35;
  --cover-deep: #041020;
  --cover-panel: #f7fbff;
  --cover-primary: #1354a5;
  --cover-accent: #b83246;
  --cover-warm: #d99a24;
  --cover-soft: rgba(255, 255, 255, .12);
  position: relative;
  overflow: hidden;
  min-height: min(760px, 78vh);
  padding: 42px max(28px, 7vw) 48px;
  color: #ffffff;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, .055) 1px, transparent 1px),
    linear-gradient(0deg, rgba(255, 255, 255, .045) 1px, transparent 1px),
    linear-gradient(135deg, var(--cover-bg) 0 62%, var(--cover-deep) 62% 100%);
  background-size: 42px 42px, 42px 42px, auto;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  align-content: stretch;
  gap: 34px;
  border-bottom: 12px solid var(--cover-warm);
}
.cover.board-aqa {
  --cover-bg: #082551;
  --cover-deep: #04152e;
  --cover-panel: #f5f9ff;
  --cover-primary: #1354a5;
  --cover-accent: #b83246;
  --cover-warm: #d99a24;
}
.cover.board-edexcel {
  --cover-bg: #053237;
  --cover-deep: #061c2f;
  --cover-panel: #f1fbfb;
  --cover-primary: #007b83;
  --cover-accent: #2d5aa7;
  --cover-warm: #78c6be;
}
.cover.board-caie {
  --cover-bg: #231424;
  --cover-deep: #11233d;
  --cover-panel: #fff7f6;
  --cover-primary: #b42c35;
  --cover-accent: #173154;
  --cover-warm: #e7b64b;
}
.cover.board-neutral {
  --cover-bg: #263244;
  --cover-deep: #172033;
  --cover-panel: #f7f9fc;
  --cover-primary: #5b677a;
  --cover-accent: #172033;
  --cover-warm: #9aa6b8;
}
.cover::before,
.cover::after {
  content: "";
  position: absolute;
  pointer-events: none;
}
.cover::before {
  inset: 0;
  background:
    linear-gradient(118deg, transparent 0 56%, rgba(255, 255, 255, .10) 56% 66%, transparent 66%),
    linear-gradient(90deg, transparent 0 76%, rgba(255, 255, 255, .08) 76% 100%);
}
.cover::after {
  top: 12%;
  right: -8%;
  width: 36%;
  height: 64%;
  background: var(--cover-accent);
  clip-path: polygon(38% 0, 100% 0, 66% 100%, 0 100%);
  opacity: .96;
}
.cover.board-edexcel::before {
  background:
    linear-gradient(90deg, transparent 0 68%, rgba(120, 198, 190, .18) 68% 100%),
    repeating-linear-gradient(135deg, rgba(255, 255, 255, .07) 0 1px, transparent 1px 18px);
}
.cover.board-edexcel::after {
  top: 8%;
  right: -4%;
  width: 30%;
  height: 76%;
  background: var(--cover-primary);
  clip-path: polygon(0 0, 100% 0, 100% 82%, 26% 100%, 0 70%);
}
.cover.board-caie::before {
  background:
    linear-gradient(90deg, transparent 0 72%, rgba(180, 44, 53, .20) 72% 100%),
    linear-gradient(118deg, transparent 0 48%, rgba(255, 255, 255, .08) 48% 60%, transparent 60%);
}
.cover.board-caie::after {
  inset: 0 0 0 auto;
  width: 31%;
  height: 100%;
  background: var(--cover-primary);
  clip-path: polygon(28% 0, 100% 0, 100% 100%, 0 100%, 16% 42%);
}
.cover.board-edexcel .cover-main {
  grid-template-columns: minmax(260px, .38fr) minmax(0, .62fr);
}
.cover.board-edexcel .cover-spec-card {
  order: -1;
  min-height: 300px;
  clip-path: polygon(0 0, 100% 0, 92% 100%, 0 100%);
}
.cover.board-edexcel .cover-title-lockup {
  justify-items: start;
}
.cover.board-caie .cover-mast {
  grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
}
.cover.board-caie .exam-board-name {
  order: 2;
}
.cover.board-caie .cover-signature-card {
  order: 1;
  clip-path: polygon(0 0, 92% 0, 100% 100%, 0 100%);
}
.cover.board-caie .cover-main {
  grid-template-columns: minmax(0, .72fr) minmax(220px, .28fr);
}
.cover.board-caie .cover-spec-card {
  border-left: 8px solid var(--cover-primary);
  clip-path: polygon(0 0, 100% 0, 100% 88%, 82% 100%, 0 100%);
}
.cover > * {
  position: relative;
  z-index: 1;
}
.exam-board-theme-strip {
  position: absolute;
  inset: 0 auto 0 0;
  z-index: 1;
  width: 22px;
  min-height: 96px;
  background: var(--cover-primary);
  border-bottom: 0;
  box-shadow: inset -7px 0 0 var(--cover-accent);
}
.exam-board-theme-strip.board-edexcel {
  width: 28px;
  background: #007b83;
  box-shadow: inset -9px 0 0 #2d5aa7;
}
.exam-board-theme-strip.board-caie {
  width: 18px;
  background: #b42c35;
  box-shadow: inset -6px 0 0 #173154;
}
.exam-board-theme-strip.board-neutral {
  background: #5b677a;
  box-shadow: inset -7px 0 0 #172033;
}
.cover-mast {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 320px);
  gap: 18px;
  align-items: start;
  width: 100%;
  max-width: 1120px;
}
.exam-board-name {
  padding: 15px 18px;
  color: #ffffff;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .22);
}
.exam-board-name span,
.cover-signature-card span,
.cover-spec-card span,
.course-code span,
.cover-identity-grid span,
.cover-signal-grid span {
  display: block;
  color: rgba(255, 255, 255, .72);
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}
.exam-board-name strong {
  display: block;
  margin-top: 7px;
  font-size: 18px;
  line-height: 1.25;
}
.cover-signature-card,
.cover-spec-card {
  color: var(--ink);
  background: var(--cover-panel);
  border: 1px solid rgba(255, 255, 255, .5);
  box-shadow: 0 18px 44px rgba(0, 0, 0, .18);
}
.cover-signature-card {
  min-height: 116px;
  padding: 16px 18px;
  clip-path: polygon(0 0, 100% 0, 100% 78%, 84% 100%, 0 100%);
}
.cover-signature-card span,
.cover-spec-card span,
.course-code span,
.cover-identity-grid span,
.cover-signal-grid span {
  color: var(--cover-primary);
}
.cover-signature-card strong {
  display: block;
  margin-top: 16px;
  font-size: 24px;
  line-height: 1.05;
}
.cover-signature-card em {
  display: block;
  margin-top: 8px;
  color: var(--muted);
  font-size: 13px;
  font-style: normal;
  font-weight: 750;
}
.cover-main {
  display: grid;
  grid-template-columns: minmax(0, .64fr) minmax(240px, .36fr);
  gap: 36px;
  align-items: center;
  width: 100%;
  max-width: 1120px;
}
.cover-title-lockup {
  align-self: center;
  display: grid;
  gap: 18px;
  min-width: 0;
}
.qualification-pill {
  width: max-content;
  max-width: 100%;
  padding: 8px 11px;
  color: #ffffff;
  background: rgba(255, 255, 255, .10);
  border: 1px solid rgba(255, 255, 255, .25);
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}
h1 { max-width: 920px; font-size: 52px; line-height: 1.05; margin: 18px 0; letter-spacing: 0; }
.cover-title-lockup h1 {
  max-width: 760px;
  margin: 0;
  color: #ffffff;
  font-size: clamp(44px, 7vw, 86px);
  line-height: .92;
  text-wrap: pretty;
}
.course-code {
  display: inline-grid;
  grid-template-columns: auto auto;
  gap: 10px;
  align-items: center;
  width: max-content;
  max-width: 100%;
  padding: 10px 14px;
  color: var(--ink);
  background: var(--cover-warm);
  font-weight: 900;
  letter-spacing: 0;
}
.course-code strong {
  font-size: 24px;
  line-height: 1;
}
.cover-spec-card {
  min-height: 244px;
  padding: 22px;
  display: grid;
  align-content: end;
  position: relative;
}
.cover-spec-card::before {
  content: "";
  position: absolute;
  inset: 18px 18px auto auto;
  width: 96px;
  height: 96px;
  background:
    linear-gradient(var(--cover-primary), var(--cover-primary)) 0 28px / 100% 2px no-repeat,
    linear-gradient(var(--cover-primary), var(--cover-primary)) 0 60px / 100% 2px no-repeat,
    linear-gradient(90deg, var(--cover-primary), var(--cover-primary)) 32px 0 / 2px 100% no-repeat,
    linear-gradient(90deg, var(--cover-primary), var(--cover-primary)) 68px 0 / 2px 100% no-repeat;
  opacity: .24;
}
.cover-spec-card strong {
  display: block;
  margin-top: 11px;
  font-size: 30px;
  line-height: 1.08;
}
.cover-spec-card p {
  margin: 10px 0 0;
  color: var(--muted);
  font-weight: 750;
}
.cover-footer {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  width: 100%;
  max-width: 1120px;
}
.cover-identity-grid,
.cover-signal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
  gap: 12px;
}
.cover-identity-grid div,
.cover-signal-grid div {
  min-height: 76px;
  padding: 14px;
  color: var(--ink);
  background: rgba(255, 255, 255, .94);
  border-top: 4px solid var(--cover-primary);
}
.cover-signal-grid div {
  border-top-color: var(--cover-accent);
}
.cover-identity-grid strong,
.cover-signal-grid strong {
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
  background: #f7fbff;
  box-shadow: 0 8px 18px rgba(23, 32, 51, .08);
}
.topic-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
.topic-nav-group {
  background: #ffffff;
  border: 1px solid var(--line);
  padding: 10px;
}
.topic-nav-group h3 {
  margin: 0 0 8px;
  color: var(--blue);
  font-size: 13px;
  text-transform: uppercase;
}
.topic-nav-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
  gap: 6px;
}
.topic-nav a {
  display: flex;
  gap: 6px;
  align-items: center;
  min-width: 0;
  padding: 6px 8px;
  color: var(--ink);
  text-decoration: none;
  background: #f8fbff;
  border: 1px solid var(--line);
  font-size: 12px;
  line-height: 1.25;
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
.guide-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
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
.topic { scroll-margin-top: 18px; }
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
  .cover-mast, .cover-main, .cover-footer, .cover-identity-grid, .cover-signal-grid, .delivery-status-grid, .overview-grid, .assessment-grid, .topic-grid, .practice-block, .guide-grid, .visual-grid, .generated-infographic-grid, .story-modes, .concept-html-map, .concept-html-map ol { grid-template-columns: 1fr; }
  .cover { padding: 36px 24px; }
  .cover::after { right: -20%; width: 52%; opacity: .72; }
  .cover-signature-card { min-height: auto; }
  .cover-spec-card { min-height: 180px; }
  .cover-title-lockup h1 { font-size: 44px; }
  .course-code { grid-template-columns: 1fr; }
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
  .course-code strong { font-size: 18px; }
  .cover-spec-card { min-height: 54mm; }
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
