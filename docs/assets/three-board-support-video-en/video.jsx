const { Stage, Sprite, useTime, Easing, clamp } = window;

const TOTAL_DURATION = 48;

const boards = [
  { name: "AQA", accent: "#1666b1" },
  { name: "Edexcel", accent: "#007d86" },
  { name: "CAIE", accent: "#c8323f" },
  { name: "College Board AP", accent: "#2255a4" },
];

const sampleBooks = [
  {
    title: "OxfordAQA IGCSE Biology",
    note: "Photosynthesis · carbon cycle · thermoregulation",
    accent: "#1666b1",
    pages: ["../v060-oxfordaqa-biology-p12.jpg", "../v060-oxfordaqa-biology-p21.jpg", "../v060-oxfordaqa-biology-p28.jpg"],
  },
  {
    title: "CAIE AS Physics",
    note: "Projectiles · stationary waves · internal resistance",
    accent: "#c8323f",
    pages: ["../v060-caie-physics-p10.jpg", "../v060-caie-physics-p25.jpg", "../v060-caie-physics-p30.jpg"],
  },
  {
    title: "College Board AP Chemistry",
    note: "PES · titration · galvanic cells",
    accent: "#2255a4",
    pages: ["../v060-ap-chemistry-p11.jpg", "../v060-ap-chemistry-p43.jpg", "../v060-ap-chemistry-p91.jpg"],
  },
  {
    title: "Edexcel IAL Mathematics",
    note: "Exponential models · mechanics · probability",
    accent: "#007d86",
    pages: ["../v060-edexcel-mathematics-p52.jpg", "../v060-edexcel-mathematics-p74.jpg", "../v060-edexcel-mathematics-p99.jpg"],
  },
];

function useSceneMotion(start, end, lift = 30) {
  const time = useTime();
  const enter = clamp((time - start) / 0.68, 0, 1);
  const exit = clamp((end - time) / 0.5, 0, 1);
  const opacity = Math.min(Easing.easeOutCubic(enter), Easing.easeOutCubic(exit));
  const y = (1 - Easing.easeOutCubic(enter)) * lift - (1 - Easing.easeOutCubic(exit)) * 14;
  return { opacity, transform: `translateY(${y}px)` };
}

function Scene({ start, end, className = "", children }) {
  return <Sprite start={start} end={end} keepMounted={true}><section className={`scene ${className}`} style={useSceneMotion(start, end)}>{children}</section></Sprite>;
}

function Stagger({ start, index, children }) {
  const time = useTime();
  const p = clamp((time - start - index * 0.12) / 0.55, 0, 1);
  return <div style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 34}px)` }}>{children}</div>;
}

function Background() {
  return <div className="stage-bg"><div className="color-rail">{Array.from({ length: 8 }, (_, index) => <i key={index}></i>)}</div></div>;
}

function IntroScene() {
  return <Scene start={0} end={5.6}><div className="kicker">Open-source revision handbook Skill</div><h1 className="headline infographic-headline">Turn official course requirements into handbooks students can really learn from.</h1><p className="lead">IGCSE, AS, A-Level, and AP with explicit boundaries for sources, writing, visuals, review, and PDF delivery.</p><div className="imagegen-visual provider-art"><img src="../intro-providers-infographic.png" alt="" /><div className="visual-legend provider-legend">{boards.map((board, index) => <Stagger start={0.9} index={index} key={board.name}><span style={{ "--accent": board.accent }}>{board.name}</span></Stagger>)}</div></div></Scene>;
}

function PreflightScene() {
  const rows = [["01", "External image capability", "Confirm a callable route; never default to local generation"], ["02", "Board and level", "IGCSE / AS / A-Level / AP"], ["03", "Course market", "AQA, Edexcel, and CAIE require International or UK"], ["04", "Subject, year, and language", "Stop for user choice when sources are ambiguous"], ["05", "Workflow and output", "Single-host role passes or user-requested multi-agent mode"]];
  return <Scene start={5.3} end={11.0}><div className="kicker">Hard first-turn preflight</div><h2 className="headline compact">The first turn collects every choice. Until then, nothing downstream may run.</h2><div className="preflight-layout"><div className="preflight-form">{rows.map((row, index) => <Stagger start={5.9} index={index} key={row[0]}><div className="form-row"><b>{row[0]}</b><strong>{row[1]}</strong><span>{row[2]}</span></div></Stagger>)}</div><div className="gate-panel"><div className="gate-number">01</div><h3>Lock the visual route first</h3><p>Text inside teaching visuals is allowed. What is blocked is incorrect, unreadable, unsourced, or unnecessary text and any image route that has not actually been verified.</p><div className="lock-state">PRECHECK INCOMPLETE → DOWNLOAD / WRITING / RENDER BLOCKED</div></div></div></Scene>;
}

function ProviderScene() {
  const data = [["AQA", "OxfordAQA / AQA", "International uses OxfordAQA; UK domestic uses the official AQA catalogue.", ["IGCSE / GCSE", "AS as a distinct level", "A-Level"], "#1666b1"], ["Edexcel", "Pearson", "Preflight selects Pearson International or Pearson UK, without source mixing.", ["International", "UK domestic", "Ask when candidates differ"], "#007d86"], ["CAIE", "Cambridge", "Match the official subject catalogue and retain the selected market in metadata.", ["IGCSE", "AS", "A-Level"], "#c8323f"], ["College Board AP", "AP Courses", "Discover official AP courses, select the core CED, and record its effective version.", ["42 official subjects", "Core CED only", "Target exam year"], "#2255a4"]];
  return <Scene start={10.7} end={16.4}><div className="kicker">Official Providers</div><h2 className="headline compact">Use the exact market the user selected and only its official source route.</h2><div className="provider-grid">{data.map((item, index) => <Stagger start={11.3} index={index} key={item[0]}><article className="provider-card" style={{ "--accent": item[4] }}><div className="code">{item[0]}</div><h3>{item[1]}</h3><p>{item[2]}</p><div className="market-list">{item[3].map((point) => <span key={point}>{point}</span>)}</div></article></Stagger>)}</div></Scene>;
}

function AtomicScene() {
  const steps = [["01", "Official evidence", "#1666b1"], ["02", "Independently assessable", "#c8323f"], ["03", "Teaching topic", "#007d86"], ["04", "Handbook location", "#2255a4"]];
  return <Scene start={16.1} end={21.8}><div className="kicker">Atomic syllabus analysis</div><h2 className="headline compact">No board- or subject-specific hard coding: split by independent assessability.</h2><div className="imagegen-visual atomic-art"><img src="../intro-atomic-infographic.png" alt="" /><div className="visual-legend">{steps.map((step, index) => <Stagger start={16.7} index={index} key={step[0]}><span style={{ "--accent": step[2] }}><b>{step[0]}</b>{step[1]}</span></Stagger>)}</div></div></Scene>;
}

function DecisionScene() {
  const decisions = [["text-ok", "Text", "#36536d"], ["exact-svg", "Exact diagram", "#1666b1"], ["kroki", "Relationship", "#007d86"], ["external-infographic", "Rich infographic", "#c8323f"]];
  return <Scene start={21.5} end={27.2}><div className="kicker">Per-topic teaching and visual decisions</div><h2 className="headline compact">Visual count is the outcome of judgment, never a subject quota.</h2><div className="imagegen-visual decision-art"><img src="../intro-visual-routing-infographic.png" alt="" /><div className="visual-legend">{decisions.map((item, index) => <Stagger start={22.1} index={index} key={item[0]}><span style={{ "--accent": item[2] }}><b>{item[0]}</b>{item[1]}</span></Stagger>)}</div></div></Scene>;
}

function SamplesScene() {
  const time = useTime();
  return <Scene start={26.9} end={35.7} className="samples-scene"><div className="kicker">Four current handbooks</div><h2 className="headline">Each one has its own outline, writing, visuals, review, and export.</h2><div className="sample-grid">{sampleBooks.map((book, index) => <Stagger start={27.5} index={index} key={book.title}><article className="sample-set" style={{ "--accent": book.accent }}><h3>{book.title}</h3><p>{book.note}</p><div className="sample-pages">{book.pages.map((page, pageIndex) => <img src={page} alt="" key={page} style={{ opacity: clamp((time - 28.0 - index * 0.12 - pageIndex * 0.12) / 0.45, 0, 1) }} />)}</div></article></Stagger>)}</div></Scene>;
}

function ReviewScene() {
  const steps = [["01", "Open the current HTML", "No PDF exists yet", "#1666b1"], ["02", "LLM reviews every topic and visual", "Machine checks cannot approve", "#c8323f"], ["03", "Repair source artifacts and rerender", "HTML changes invalidate old approval", "#007d86"], ["04", "Bind approval to the current HTML hash", "Only then unlock PDF", "#157347"]];
  return <Scene start={35.4} end={41.2}><div className="kicker">Complete HTML-first review</div><h2 className="headline compact">Inspect, repair, and inspect again. Do not generate PDF until HTML passes.</h2><div className="review-layout"><div className="review-proof"><img src="../v060-caie-physics-p30.jpg" alt="" /><div className="proof-copy"><strong>FULL HTML REVIEW</strong><h3>A polished page is not proof of correct teaching.</h3><p>Review facts, notation, visual meaning, labels, arrows, sources, learning value, and cross-page repetition. Any pending item or stale hash blocks approval.</p></div></div><div className="review-loop">{steps.map((step, index) => <Stagger start={36.1} index={index} key={step[0]}><div className="loop-step" style={{ "--accent": step[3] }}><b>{step[0]}</b><strong>{step[1]}</strong><span>{step[2]}</span></div></Stagger>)}</div></div></Scene>;
}

function TraceabilityScene() {
  return <Scene start={40.9} end={45.7}><div className="kicker">Traceable delivery</div><h2 className="headline compact">Every final page can be traced back to the current official requirement.</h2><div className="package-layout"><div className="zip-panel"><div className="zip-header"><strong>HANDBOOK EVIDENCE</strong><span>CURRENT VERSION</span></div><div className="tree"><div className="tree-row root"><i></i>Official source page</div><div className="tree-row"><i></i>Atomic syllabus point</div><div className="tree-row"><i></i>Teaching and worked example</div><div className="tree-row"><i></i>Reviewed visual</div><div className="tree-row"><i></i>HTML and PDF hashes</div></div></div><div className="package-notes" style={{ "--accent": "#2255a4" }}><h3>Each step stays bound to the current version.</h3><ul><li>Every final topic maps to an official requirement and handbook location.</li><li>Visual approval and HTML review bind to current asset hashes.</li><li>PDF is exported only from approved HTML, with source and delivery hashes recorded.</li></ul></div></div></Scene>;
}

function ClosingScene() {
  return <Scene start={45.4} end={TOTAL_DURATION} className="closing-scene"><div className="closing-copy"><div className="kicker">Source-backed · LLM-reviewed</div><h2 className="headline">One handbook, one complete and non-bypassable delivery chain.</h2><p className="lead">Official source → atomic requirements → teaching and visuals → HTML review → controlled PDF</p><div className="closing-badges"><span>IGCSE</span><span>AS</span><span>A-Level</span><span>AP</span><span>Open Source Skill</span></div></div><div className="closing-pages"><img src="../v060-oxfordaqa-biology-p28.jpg" alt="" /><img src="../v060-ap-chemistry-p91.jpg" alt="" /><img src="../v060-edexcel-mathematics-p52.jpg" alt="" /></div></Scene>;
}

function Footer() {
  return <div className="footer-mark"><span>IGCSE · AS · A-LEVEL · AP REVISION HANDBOOK SKILL</span><span>OFFICIAL SOURCE → REVIEWED HANDBOOK</span></div>;
}

function App() {
  return <Stage width={1920} height={1080} duration={TOTAL_DURATION} background="#eef2f5"><Background /><IntroScene /><PreflightScene /><ProviderScene /><AtomicScene /><DecisionScene /><SamplesScene /><ReviewScene /><TraceabilityScene /><ClosingScene /><Footer /></Stage>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
