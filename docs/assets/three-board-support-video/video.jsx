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
    note: "光合作用 · 碳循环 · 体温调节",
    accent: "#1666b1",
    pages: ["../v060-oxfordaqa-biology-p12.jpg", "../v060-oxfordaqa-biology-p21.jpg", "../v060-oxfordaqa-biology-p28.jpg"],
  },
  {
    title: "CAIE AS Physics",
    note: "抛体运动 · 驻波 · 内阻",
    accent: "#c8323f",
    pages: ["../v060-caie-physics-p10.jpg", "../v060-caie-physics-p25.jpg", "../v060-caie-physics-p30.jpg"],
  },
  {
    title: "College Board AP Chemistry",
    note: "PES · 滴定 · 原电池",
    accent: "#2255a4",
    pages: ["../v060-ap-chemistry-p11.jpg", "../v060-ap-chemistry-p43.jpg", "../v060-ap-chemistry-p91.jpg"],
  },
  {
    title: "Edexcel IAL Mathematics",
    note: "指数模型 · 力学模型 · 条件概率",
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
  return (
    <Sprite start={start} end={end} keepMounted={true}>
      <section className={`scene ${className}`} style={useSceneMotion(start, end)}>{children}</section>
    </Sprite>
  );
}

function Stagger({ start, index, children }) {
  const time = useTime();
  const p = clamp((time - start - index * 0.12) / 0.55, 0, 1);
  return <div style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 34}px)` }}>{children}</div>;
}

function Background() {
  return (
    <div className="stage-bg">
      <div className="color-rail">{Array.from({ length: 8 }, (_, index) => <i key={index}></i>)}</div>
    </div>
  );
}

function IntroScene() {
  return (
    <Scene start={0} end={5.6}>
      <div className="kicker">开源复习手册 Skill</div>
      <h1 className="headline infographic-headline">把官方课程要求，做成真正能学的图文手册。</h1>
      <p className="lead">覆盖 GCSE、IGCSE、A-Level 与 AP；来源、写作、配图、审查和 PDF 交付都有明确边界。</p>
      <div className="imagegen-visual provider-art">
        <img src="../intro-providers-infographic.png" alt="" />
        <div className="visual-legend provider-legend">{boards.map((board, index) => <Stagger start={0.9} index={index} key={board.name}><span style={{ "--accent": board.accent }}>{board.name}</span></Stagger>)}</div>
      </div>
    </Scene>
  );
}

function PreflightScene() {
  const rows = [
    ["01", "外部生图能力", "先确认可调用路线，不得默认本地生图"],
    ["02", "考试局与课程阶段", "GCSE / IGCSE / A-Level / AP；A-Level 标明 AS、A2 或完整范围"],
    ["03", "课程市场", "AQA、Edexcel、CAIE 必选 International 或 UK"],
    ["04", "科目、年份与语言", "来源不唯一时停下让用户选择"],
    ["05", "工作模式与输出目录", "单宿主角色分离或用户明确要求多 Agent"],
  ];
  return (
    <Scene start={5.3} end={11.0}>
      <div className="kicker">首轮强制预检</div>
      <h2 className="headline compact">第一轮只收齐选择；没收齐，后面一步都不能跑。</h2>
      <div className="preflight-layout">
        <div className="preflight-form">
          {rows.map((row, index) => <Stagger start={5.9} index={index} key={row[0]}><div className="form-row"><b>{row[0]}</b><strong>{row[1]}</strong><span>{row[2]}</span></div></Stagger>)}
        </div>
        <div className="gate-panel">
          <div className="gate-number">01</div>
          <h3>外部视觉能力先锁定</h3>
          <p>图中文字默认允许。真正受限的是错误、不可读、没有来源或不必要的文字，以及未经验证的生图通道。</p>
          <div className="lock-state">PRECHECK INCOMPLETE → DOWNLOAD / WRITING / RENDER BLOCKED</div>
        </div>
      </div>
    </Scene>
  );
}

function ProviderScene() {
  const data = [
    ["AQA", "OxfordAQA / AQA", "International 走 OxfordAQA；英国本土走 AQA 官方目录。", ["英国 GCSE", "国际 IGCSE", "A-Level（AS/A2）"], "#1666b1"],
    ["Edexcel", "Pearson", "根据预检选 Pearson International 或 Pearson UK，不混用。", ["英国 GCSE", "国际 IGCSE", "A-Level（AS/A2）"], "#007d86"],
    ["CAIE", "Cambridge", "使用 Cambridge International 官方目录，并保留用户选择的市场元数据。", ["国际 IGCSE", "Cambridge A-Level", "市场元数据"], "#c8323f"],
    ["College Board AP", "AP Courses", "自动发现官方 AP 课程，只选择核心 CED 并记录生效版本。", ["42 门官方科目", "核心 CED", "目标考试年份"], "#2255a4"],
  ];
  return (
    <Scene start={10.7} end={16.4}>
      <div className="kicker">官方 Provider</div>
      <h2 className="headline compact">确认用户要哪个版本，就只走那个官方来源。</h2>
      <div className="provider-grid">
        {data.map((item, index) => <Stagger start={11.3} index={index} key={item[0]}><article className="provider-card" style={{ "--accent": item[4] }}><div className="code">{item[0]}</div><h3>{item[1]}</h3><p>{item[2]}</p><div className="market-list">{item[3].map((point) => <span key={point}>{point}</span>)}</div></article></Stagger>)}
      </div>
    </Scene>
  );
}

function AtomicScene() {
  const steps = [
    ["01", "官方来源证据", "#1666b1"],
    ["02", "独立可考要求", "#c8323f"],
    ["03", "最终教学 Topic", "#007d86"],
    ["04", "可追溯位置", "#2255a4"],
  ];
  return (
    <Scene start={16.1} end={21.8}>
      <div className="kicker">原子级大纲拆解</div>
      <h2 className="headline compact">不按考试局或学科硬编码，只按“能否独立考查”继续拆。</h2>
      <div className="imagegen-visual atomic-art">
        <img src="../intro-atomic-infographic.png" alt="" />
        <div className="visual-legend">{steps.map((step, index) => <Stagger start={16.7} index={index} key={step[0]}><span style={{ "--accent": step[2] }}><b>{step[0]}</b>{step[1]}</span></Stagger>)}</div>
      </div>
    </Scene>
  );
}

function DecisionScene() {
  const decisions = [
    ["text-ok", "文字足够", "#36536d"],
    ["exact-svg", "精确图解", "#1666b1"],
    ["kroki", "结构关系", "#007d86"],
    ["external-infographic", "复杂信息图", "#c8323f"],
  ];
  return (
    <Scene start={21.5} end={27.2}>
      <div className="kicker">逐主题教学与视觉决策</div>
      <h2 className="headline compact">视觉数量是判断结果，不是先分配给每科的配额。</h2>
      <div className="imagegen-visual decision-art">
        <img src="../intro-visual-routing-infographic.png" alt="" />
        <div className="visual-legend">{decisions.map((item, index) => <Stagger start={22.1} index={index} key={item[0]}><span style={{ "--accent": item[2] }}><b>{item[0]}</b>{item[1]}</span></Stagger>)}</div>
      </div>
    </Scene>
  );
}

function SamplesScene() {
  const time = useTime();
  return (
    <Scene start={26.9} end={35.7} className="samples-scene">
      <div className="kicker">四份当前成品</div>
      <h2 className="headline">每一本独立拆纲、写作、配图、审查和导出。</h2>
      <div className="sample-grid">
        {sampleBooks.map((book, index) => <Stagger start={27.5} index={index} key={book.title}><article className="sample-set" style={{ "--accent": book.accent }}><h3>{book.title}</h3><p>{book.note}</p><div className="sample-pages">{book.pages.map((page, pageIndex) => <img src={page} alt="" key={page} style={{ opacity: clamp((time - 28.0 - index * 0.12 - pageIndex * 0.12) / 0.45, 0, 1) }} />)}</div></article></Stagger>)}
      </div>
    </Scene>
  );
}

function ReviewScene() {
  const steps = [
    ["01", "打开当前 HTML", "PDF 尚未生成", "#1666b1"],
    ["02", "LLM 亲自审每个 topic 与视觉", "机器检查不能批准", "#c8323f"],
    ["03", "发现问题就重写并重新渲染", "HTML 变更使旧批准失效", "#007d86"],
    ["04", "当前 HTML 哈希绑定批准后", "才解锁 PDF", "#157347"],
  ];
  return (
    <Scene start={35.4} end={41.2}>
      <div className="kicker">HTML 优先的完整审查</div>
      <h2 className="headline compact">先看、再修、再从头看；通过前不生成 PDF。</h2>
      <div className="review-layout">
        <div className="review-proof"><img src="../v060-caie-physics-p30.jpg" alt="" /><div className="proof-copy"><strong>FULL HTML REVIEW</strong><h3>页面漂亮不等于教学正确。</h3><p>审查事实、公式、图义、标签、箭头、来源、学习价值和跨页重复；只要有 pending 或旧哈希，就不能批准。</p></div></div>
        <div className="review-loop">{steps.map((step, index) => <Stagger start={36.1} index={index} key={step[0]}><div className="loop-step" style={{ "--accent": step[3] }}><b>{step[0]}</b><strong>{step[1]}</strong><span>{step[2]}</span></div></Stagger>)}</div>
      </div>
    </Scene>
  );
}

function TraceabilityScene() {
  return (
    <Scene start={40.9} end={45.7}>
      <div className="kicker">可追溯交付</div>
      <h2 className="headline compact">从官方要求到最终 PDF，每一步都能查证。</h2>
      <div className="package-layout">
        <div className="zip-panel"><div className="zip-header"><strong>HANDBOOK EVIDENCE</strong><span>CURRENT VERSION</span></div><div className="tree"><div className="tree-row root"><i></i>官方来源页码</div><div className="tree-row"><i></i>原子考点</div><div className="tree-row"><i></i>教学讲解与例题</div><div className="tree-row"><i></i>已审查视觉</div><div className="tree-row"><i></i>HTML 与 PDF 哈希</div></div></div>
        <div className="package-notes" style={{ "--accent": "#2255a4" }}><h3>每一步都绑定当前版本。</h3><ul><li>每个最终主题对应官方要求和手册位置。</li><li>视觉批准与 HTML 审查绑定当前资产哈希。</li><li>PDF 只从已批准 HTML 导出，并记录来源与交付哈希。</li></ul></div>
      </div>
    </Scene>
  );
}

function ClosingScene() {
  return (
    <Scene start={45.4} end={TOTAL_DURATION} className="closing-scene">
      <div className="closing-copy"><div className="kicker">Source-backed · LLM-reviewed</div><h2 className="headline">一份手册，一条完整、真实、不可绕过的交付链。</h2><p className="lead">官方来源 → 原子考点 → 教学与视觉 → HTML 审查 → 受控 PDF</p><div className="closing-badges"><span>GCSE</span><span>IGCSE</span><span>A-Level</span><span>AP</span><span>Open Source Skill</span></div></div>
      <div className="closing-pages"><img src="../v060-oxfordaqa-biology-p28.jpg" alt="" /><img src="../v060-ap-chemistry-p91.jpg" alt="" /><img src="../v060-edexcel-mathematics-p52.jpg" alt="" /></div>
    </Scene>
  );
}

function Footer() {
  return <div className="footer-mark"><span>GCSE · IGCSE · A-LEVEL · AP REVISION HANDBOOK SKILL</span><span>OFFICIAL SOURCE → REVIEWED HANDBOOK</span></div>;
}

function App() {
  return <Stage width={1920} height={1080} duration={TOTAL_DURATION} background="#eef2f5"><Background /><IntroScene /><PreflightScene /><ProviderScene /><AtomicScene /><DecisionScene /><SamplesScene /><ReviewScene /><TraceabilityScene /><ClosingScene /><Footer /></Stage>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
