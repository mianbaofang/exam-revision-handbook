const { Stage, Sprite, useTime, Easing, interpolate, clamp } = window;

const boardData = [
  {
    name: "AQA",
    note: "自动读取官方目录与公开 specification",
    status: "官方大纲",
    accent: "#d89b33",
  },
  {
    name: "Edexcel",
    note: "按科目候选匹配官方页面或 PDF",
    status: "候选确认",
    accent: "#be4750",
  },
  {
    name: "CAIE",
    note: "从科目索引匹配并确认考试年份",
    status: "年份确认",
    accent: "#4fa394",
  },
];

const providerData = [
  {
    tag: "01",
    title: "AQA",
    accent: "#d89b33",
    points: ["从官网目录发现课程", "读取公开 specification PDF", "把大纲转成 CourseSpec"],
  },
  {
    tag: "02",
    title: "Edexcel",
    accent: "#be4750",
    points: ["按科目名匹配官方候选", "支持官方科目页或 PDF 输入", "不唯一时先让用户选择"],
  },
  {
    tag: "03",
    title: "CAIE",
    accent: "#4fa394",
    points: ["从官方科目索引匹配候选", "多年大纲先确认考试年份", "年份不清楚就停下确认"],
  },
];

const TOTAL_DURATION = 48;

function useSceneMotion(start, end, inY = 36) {
  const time = useTime();
  const enter = clamp((time - start) / 0.8, 0, 1);
  const exit = clamp((end - time) / 0.55, 0, 1);
  const opacity = Math.min(Easing.easeOutCubic(enter), Easing.easeOutCubic(exit));
  const y = (1 - Easing.easeOutCubic(enter)) * inY + (1 - Easing.easeOutCubic(exit)) * -18;
  return { opacity, transform: `translateY(${y}px)` };
}

function VideoLabel() {
  const time = useTime();
  React.useEffect(() => {
    const label = `${Math.floor(time).toString().padStart(2, "0")}s`;
    document.documentElement.setAttribute("data-screen-label", label);
  }, [Math.floor(time)]);
  return null;
}

function Background() {
  const time = useTime();
  const drift = interpolate([0, TOTAL_DURATION], [0, -150], Easing.linear)(time);
  return (
    <div className="stage">
      <div className="grid-lines" style={{ transform: `translate3d(${drift}px, ${drift * 0.35}px, 0)` }}></div>
      <div className="noise"></div>
    </div>
  );
}

function SceneFrame({ start, end, children }) {
  const motion = useSceneMotion(start, end);
  return (
    <Sprite start={start} end={end} keepMounted={true}>
      <section className="scene" style={motion}>
        {children}
      </section>
    </Sprite>
  );
}

function IntroScene() {
  const time = useTime();
  const cardLift = (index) => {
    const p = clamp((time - 1.2 - index * 0.22) / 0.75, 0, 1);
    return {
      opacity: Easing.easeOutCubic(p),
      transform: `translateY(${(1 - Easing.easeOutBack(p)) * 72}px)`,
      "--accent": boardData[index].accent,
    };
  };
  const orbit = interpolate([0, 5.0], [0, 38], Easing.easeInOutSine)(time);
  return (
    <SceneFrame start={0} end={5.2}>
      <div className="orbit" style={{ transform: `rotate(${orbit}deg) scale(${1 + Math.sin(time * 0.7) * 0.025})` }}></div>
      <div className="kicker">v0.4.4 · 复习手册生成 Skill</div>
      <h1 className="headline">把官方大纲，变成孩子看得下去的复习手册。</h1>
      <p className="lead">
        面向 AQA、Edexcel、CAIE：先抓取官方大纲，再由多个 Agent 分工写作、配图和验收。
      </p>
      <div className="hero-board-row">
        {boardData.map((board, index) => (
          <article className="board-card" key={board.name} style={cardLift(index)}>
            <strong>{board.name}</strong>
            <span>{board.note}</span>
            <div className="status">{board.status}</div>
          </article>
        ))}
      </div>
    </SceneFrame>
  );
}

function OriginScene() {
  const time = useTime();
  const notes = [
    ["真实起点", "孩子从中文课堂切换到全英文课堂，不到一年就面对 International GCSE 大考。"],
    ["AI 的任务", "不是替孩子学习，而是把知识点、例题、图解和检查点整理成能读下去的手册。"],
    ["开源目标", "把这套方法做成 Skill，让其他家庭和 Agent 也能按科目生成复习手册。"],
  ];
  return (
    <SceneFrame start={4.8} end={9.7}>
      <div className="kicker">为什么做这个 Skill</div>
      <h2 className="headline provider-headline">先帮一个真实的孩子，把复习压力拆小。</h2>
      <div className="origin-layout">
        <div className="quote-panel">
          <strong>不是替孩子学习，</strong>
          <span>而是把学习路上的噪音降下来。</span>
        </div>
        <div className="story-points">
          {notes.map((note, index) => {
            const p = clamp((time - 5.4 - index * 0.22) / 0.65, 0, 1);
            return (
              <article key={note[0]} style={{ opacity: p, transform: `translateY(${(1 - p) * 34}px)` }}>
                <b>{note[0]}</b>
                <p>{note[1]}</p>
              </article>
            );
          })}
        </div>
      </div>
    </SceneFrame>
  );
}

function UsageScene() {
  const time = useTime();
  const steps = [
    ["01", "大纲分析 Agent", "抓取官方页面/PDF，拆出 CourseSpec 和 LearningUnit。"],
    ["02", "主编写 Agent", "写讲解、例题、术语表和视觉需求，不直接冒充最终审核。"],
    ["03", "视觉处理 Agent", "判定 exact SVG、Kroki 或外部信息图任务；复杂图不能用草图冒充完成。"],
    ["04", "独立验收 Agent", "读最终页面和抽样 PDF，对照大纲，能修就修，不能修就标 draft。"],
  ];
  return (
    <SceneFrame start={9.4} end={14.4}>
      <div className="kicker">多 Agent 协同</div>
      <h2 className="headline route-headline">不是一个模型一路写到底，而是分工协作再独立复查。</h2>
      <div className="usage-steps">
        {steps.map((step, index) => {
          const p = clamp((time - 10.0 - index * 0.16) / 0.58, 0, 1);
          return (
            <article key={step[0]} style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 48}px)` }}>
              <div>{step[0]}</div>
              <h3>{step[1]}</h3>
              <p>{step[2]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function PreflightScene() {
  const time = useTime();
  const sourceT = clamp((time - 14.9) / 3.2, 0, 1);
  const rows = [
    ["考试局与科目", "AQA / Edexcel / CAIE，或官方页面/PDF"],
    ["考试年份", "Cambridge 多年份页面必须先确认"],
    ["术语支持语言", "中文、繁中、日语等只生成术语对照表"],
    ["讲解风格", "formal、friendly、life、story、detective、adventure"],
    ["信息图能力", "先问有无 Skill/API/图片目录；没有也可继续 draft"],
  ];
  return (
    <SceneFrame start={14.1} end={19.1}>
      <div className="kicker">先确认，再生成</div>
      <h2 className="headline">第一次使用先问清楚，不跑完才补问。</h2>
      <div className="choice-grid">
        <div className="control-panel">
          {rows.map((row, index) => {
            const p = clamp((time - 14.7 - index * 0.18) / 0.55, 0, 1);
            return (
                <div className="choice-row" key={row[0]} style={{ opacity: p, transform: `translateX(${(1 - p) * -34}px)` }}>
                <b>{row[0]}</b>
                <span>{row[1]}</span>
              </div>
            );
          })}
        </div>
        <div className="source-stack">
          <div className="source-card" style={{ left: 34, top: 90, transform: `rotate(${-6 + sourceT * 3}deg) translateY(${(1 - sourceT) * 70}px)` }}>
            <h3>官方科目页</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 124, top: 44, transform: `rotate(${4 - sourceT * 2}deg) translateY(${(1 - sourceT) * 42}px)` }}>
            <h3>考试大纲 PDF</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 214, top: 146, transform: `rotate(${-1 + sourceT * 1.5}deg) translateY(${(1 - sourceT) * 90}px)` }}>
            <h3>来源校验和考试信息</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
        </div>
      </div>
    </SceneFrame>
  );
}

function ProviderScene() {
  const time = useTime();
  return (
    <SceneFrame start={18.8} end={23.8}>
      <div className="kicker">三大考试局怎么支持</div>
      <h2 className="headline provider-headline">自动抓取三大考试局大纲，但不混用来源。</h2>
      <p className="lead provider-lead">AQA、Edexcel、CAIE 的大纲格式不同，所以先解析官方来源，再统一成可写作、可复查的课程结构。</p>
      <div className="provider-system">
        {providerData.map((provider, index) => {
          const p = clamp((time - 19.2 - index * 0.28) / 0.75, 0, 1);
          return (
            <article className="provider-column" key={provider.title} style={{ "--accent": provider.accent, opacity: p, transform: `translateY(${(1 - Easing.easeOutBack(p)) * 86}px)` }}>
              <div className="tag">{provider.tag}</div>
              <h3>{provider.title}</h3>
              <ul>
                {provider.points.map((point) => <li key={point}>{point}</li>)}
              </ul>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function SyllabusScene() {
  const time = useTime();
  const steps = [
    ["官方页面", "找到考试局科目页或用户指定 URL"],
    ["大纲 PDF", "下载公开 specification / syllabus"],
    ["主题拆解", "抽取 topic、assessment、页码和来源片段"],
    ["手册骨架", "生成知识点、例题、复习检查点"],
    ["质量验证", "topic、例题、来源、图文块缺失都会暴露"],
  ];
  return (
    <SceneFrame start={23.5} end={28.3}>
      <div className="kicker">从大纲到手册</div>
      <h2 className="headline route-headline">先守住官方来源，再写成学生能预习复习的内容。</h2>
      <div className="pipeline-board">
        {steps.map((step, index) => {
          const p = clamp((time - 24.0 - index * 0.14) / 0.6, 0, 1);
          return (
            <article className="pipeline-step" key={step[0]} style={{ opacity: p, transform: `translateY(${(1 - p) * 42}px)` }}>
              <b>{String(index + 1).padStart(2, "0")}</b>
              <h3>{step[0]}</h3>
              <p>{step[1]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function LanguageStyleScene() {
  const time = useTime();
  const cards = [
    ["正文保持英文", "中文、繁中、日语等需求会变成 30-50 个专业词对照表，而不是整本翻译。"],
    ["多种语言风格", "formal、friendly、life、story、detective、adventure，避免死板教辅腔。"],
    ["配套例题讲解", "每个 topic 有原创例题、步骤、答案框架和常见失分点。"],
    ["图文判断", "只给必须靠图说清楚的知识点配图，不把每个 topic 都硬画一张。"],
  ];
  return (
    <SceneFrame start={28.0} end={32.8}>
      <div className="kicker">语言、风格和例题</div>
      <h2 className="headline provider-headline">考试是英文，辅助语言应该放在术语表，而不是整本翻译。</h2>
      <div className="style-grid">
        {cards.map((card, index) => {
          const p = clamp((time - 28.6 - index * 0.16) / 0.58, 0, 1);
          return (
            <article className="style-card" key={card[0]} style={{ opacity: p, transform: `translateX(${(1 - p) * 42}px)` }}>
              <h3>{card[0]}</h3>
              <p>{card[1]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function SamplesScene() {
  const time = useTime();
  const wallPan = interpolate([38.5, 43.0], [0, -36], Easing.easeInOutSine)(time);
  const stats = [
    ["7", "本地回归样例通过，质量检查无错误"],
    ["357", "跨三大考试局样例生成的知识点讲解"],
    ["318", "带步骤和检查点的例题卡"],
    ["0", "复杂信息图不再假装已生成"],
  ];
  return (
    <SceneFrame start={38.0} end={43.1}>
      <div className="sample-scene">
        <div className="sample-copy">
          <div className="kicker">真实手册样例</div>
          <h2 className="headline sample-headline">展示的是能交付的复习手册。</h2>
          <div className="stat-list">
            {stats.map((stat, index) => {
              const p = clamp((time - 38.7 - index * 0.18) / 0.55, 0, 1);
              return (
                <div className="stat" key={stat[1]} style={{ opacity: p, transform: `translateX(${(1 - p) * -32}px)` }}>
                  <b>{stat[0]}</b>
                  <span>{stat[1]}</span>
                </div>
              );
            })}
          </div>
        </div>
        <div className="screenshot-wall" style={{ transform: `translateX(${wallPan}px)` }}>
          <figure className="shot" style={{ left: 80, top: 20, transform: "rotate(-5deg)" }}>
            <img src="sample-math-guide.png" alt="数学手册截图" />
          </figure>
          <figure className="shot" style={{ left: 250, top: 250, transform: "rotate(3deg)" }}>
            <img src="sample-economics-guide.png" alt="经济学手册截图" />
          </figure>
          <figure className="shot" style={{ left: 0, top: 455, transform: "rotate(-1deg)" }}>
            <img src="sample-chemistry-guide.png" alt="化学手册截图" />
          </figure>
        </div>
      </div>
    </SceneFrame>
  );
}

function VisualRouteScene() {
  const time = useTime();
  const cards = [
    {
      title: "精确复核图：Exact SVG",
      body: "数轴、坐标轴、简单几何、基础表格必须标记 svg_fit=exact，并复核通过。",
      visual: <div className="svg-diagram"><span></span><span></span><span></span></div>,
    },
    {
      title: "专业结构图：Kroki",
      body: "流程、层级、时间线、关系图、概念图等结构图，需要 LLM 判断并复核。",
      visual: (
        <svg className="kroki-preview" viewBox="0 0 360 190" aria-label="Kroki 结构图示意">
          <defs>
            <marker id="arrow-cn" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" />
            </marker>
          </defs>
          <path d="M180 48 L96 86" />
          <path d="M180 48 L264 86" />
          <path d="M96 124 L180 150" />
          <path d="M264 124 L180 150" />
          <rect x="126" y="14" width="108" height="42" rx="8" />
          <rect x="34" y="84" width="124" height="42" rx="8" />
          <rect x="202" y="84" width="124" height="42" rx="8" />
          <rect x="120" y="140" width="120" height="42" rx="8" className="output" />
          <text x="180" y="41">来源</text>
          <text x="96" y="111">流程</text>
          <text x="264" y="111">层级</text>
          <text x="180" y="167">复查图</text>
        </svg>
      ),
    },
    {
      title: "复杂信息图：外部生成",
      body: "实验、经济场景、密集图文解释生成 worksheet 风格信息图，导入后自动替换。",
      visual: <div className="model-grid"><span>GPT Image 2.0</span><span>Qwen Image 2.0 Pro</span><span>SenseNova U1 Fast</span></div>,
    },
  ];
  return (
    <SceneFrame start={32.5} end={38.2}>
      <div className="kicker">专业图形生成处理</div>
      <h2 className="headline route-headline">Exact SVG、Kroki、外部信息图各有自己的审核边界。</h2>
      <div className="visual-routing">
        {cards.map((card, index) => {
          const p = clamp((time - 33.0 - index * 0.18) / 0.7, 0, 1);
          return (
            <article className="route-card" key={card.title} style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 58}px)` }}>
              <h3>{card.title}</h3>
              <div className="route-visual">{card.visual}</div>
              <p>{card.body}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function QualityScene() {
  const time = useTime();
  const metrics = [
    ["outline", "大纲逐项对照"],
    ["glossary", "术语表检查"],
    ["visuals", "图片/图形检查"],
    ["pdf", "PDF 抽页检查"],
  ];
  return (
    <SceneFrame start={42.8} end={46.2}>
      <div className="kicker">独立 Agent 验收</div>
      <h2 className="headline provider-headline">不是生成完就算，最终手册要自己读一遍、修一遍。</h2>
      <div className="quality-grid">
        {metrics.map((metric, index) => {
          const p = clamp((time - 43.3 - index * 0.12) / 0.5, 0, 1);
          return (
            <article className="quality-card" key={metric[0]} style={{ opacity: p, transform: `scale(${0.92 + p * 0.08})` }}>
              <b>{metric[0]}</b>
              <span>{metric[1]}</span>
              <i></i>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function ClosingScene() {
  const time = useTime();
  const p = clamp((time - 46.0) / 1.0, 0, 1);
  const boxes = ["官方大纲", "英文正文+术语表", "例题讲解", "复查证据"];
  return (
    <SceneFrame start={45.8} end={TOTAL_DURATION}>
      <div className="final-lockup">
        <div>
          <div className="kicker">最终交付标准</div>
          <h2 className="headline">最终交付必须像一份能给孩子用的资料。</h2>
          <p className="lead">大纲、讲解、术语表、图形、例题和 PDF 都通过最终复查，才允许进入 final-ready。</p>
        </div>
        <div className="deliverable" style={{ opacity: p, transform: `rotate(${-1.5 + (1 - p) * -7}deg) translateY(${(1 - p) * 100}px)` }}>
          <h3>International GCSE / AS-A-level 复习手册</h3>
          <div className="bar"></div>
          <div className="paper-grid">
            {boxes.map((box) => (
              <div className="paper-box" key={box}>
                <b>{box}</b>
                <i></i><i></i><i></i>
              </div>
            ))}
          </div>
        </div>
      </div>
    </SceneFrame>
  );
}

function Footer() {
  return (
    <div className="footer-mark">
      <span>IGCSE & A-Level AI 复习手册 Skill · v0.4.4</span>
      <span>official syllabus → reviewed handbook</span>
    </div>
  );
}

function App() {
  return (
    <Stage width={1920} height={1080} duration={TOTAL_DURATION} background="#080b10">
      <VideoLabel />
      <Background />
      <IntroScene />
      <OriginScene />
      <UsageScene />
      <PreflightScene />
      <ProviderScene />
      <SyllabusScene />
      <LanguageStyleScene />
      <VisualRouteScene />
      <SamplesScene />
      <QualityScene />
      <ClosingScene />
      <Footer />
    </Stage>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
