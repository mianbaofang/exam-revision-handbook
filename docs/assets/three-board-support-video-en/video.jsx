const { Stage, Sprite, useTime, Easing, interpolate, clamp } = window;

const boardData = [
  {
    name: "AQA",
    note: "Reads the official catalogue and public specification",
    status: "Official source",
    accent: "#d89b33",
  },
  {
    name: "Edexcel",
    note: "Matches official subject pages or specification PDFs",
    status: "Candidate check",
    accent: "#be4750",
  },
  {
    name: "CAIE",
    note: "Matches the subject index and confirms the exam year",
    status: "Year check",
    accent: "#4fa394",
  },
];

const providerData = [
  {
    tag: "01",
    title: "AQA",
    accent: "#d89b33",
    points: ["Discover courses from the official catalogue", "Read public specification PDFs", "Turn syllabus detail into CourseSpec"],
  },
  {
    tag: "02",
    title: "Edexcel",
    accent: "#be4750",
    points: ["Match official candidates by subject name", "Accept official pages or PDFs", "Ask the user when candidates are not unique"],
  },
  {
    tag: "03",
    title: "CAIE",
    accent: "#4fa394",
    points: ["Match candidates from the official subject index", "Confirm exam year on multi-year pages", "Stop when the year is unclear"],
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
      <div className="kicker">v0.4.2 · Revision Handbook Skill</div>
      <h1 className="headline">Turn official syllabuses into revision handbooks students can actually use.</h1>
      <p className="lead">
        For AQA, Edexcel, and CAIE: fetch the official syllabus first, then let agents split writing, visuals, and final review.
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
    ["Real origin", "A student moved from Chinese-medium classes into English-medium international courses before the exam year."],
    ["What AI helps with", "It does not study for the child; it turns topics, examples, visuals, and checkpoints into readable pages."],
    ["Open-source goal", "Package the method as a Skill so other families and agents can generate subject handbooks too."],
  ];
  return (
    <SceneFrame start={4.8} end={9.7}>
      <div className="kicker">Why This Skill Exists</div>
      <h2 className="headline provider-headline">It started by making exam revision feel smaller for one real student.</h2>
      <div className="origin-layout">
        <div className="quote-panel">
          <strong>Not replacing study,</strong>
          <span>but reducing the noise around it.</span>
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
    ["01", "Syllabus analyst agent", "Fetch official pages/PDFs and split CourseSpec into LearningUnits."],
    ["02", "Handbook writer agent", "Write explanations, examples, glossary support, and visual needs."],
    ["03", "Visual routing agent", "Use local SVG for simple cases, Kroki for structured diagrams, and external jobs for rich infographics."],
    ["04", "Independent review agent", "Read final pages and sampled PDFs against the outline; fix what can be fixed before handoff."],
  ];
  return (
    <SceneFrame start={9.4} end={14.4}>
      <div className="kicker">Multi-Agent Collaboration</div>
      <h2 className="headline route-headline">Not one model writing straight through: separate roles write, route, and review.</h2>
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
    ["Board and subject", "AQA / Edexcel / CAIE, or an official page/PDF"],
    ["Exam year", "Cambridge multi-year pages must be confirmed first"],
    ["Term-support language", "Chinese, Traditional Chinese, Japanese, or another glossary language"],
    ["Explanation style", "formal, friendly, life, story, detective, or adventure"],
    ["Infographic capability", "Ask whether a Skill/API/asset folder exists; continue as draft if not"],
  ];
  return (
    <SceneFrame start={14.1} end={19.1}>
      <div className="kicker">Confirm first, then generate</div>
      <h2 className="headline">Ask the first-run questions before the handbook starts.</h2>
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
            <h3>Official subject page</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 124, top: 44, transform: `rotate(${4 - sourceT * 2}deg) translateY(${(1 - sourceT) * 42}px)` }}>
            <h3>Specification PDF</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 214, top: 146, transform: `rotate(${-1 + sourceT * 1.5}deg) translateY(${(1 - sourceT) * 90}px)` }}>
            <h3>Source checks and exam metadata</h3>
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
      <div className="kicker">How The Three Boards Are Supported</div>
      <h2 className="headline provider-headline">Automatically fetch three-board syllabuses without mixing sources.</h2>
      <p className="lead provider-lead">AQA, Edexcel, and CAIE publish syllabuses in different shapes, so the workflow parses each official source first, then normalizes it into a reviewable course structure.</p>
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
    ["Official page", "Find the exam-board subject page or use the URL supplied by the user"],
    ["Syllabus PDF", "Download the public specification or syllabus"],
    ["Topic extraction", "Extract topics, assessment structure, page numbers, and source snippets"],
    ["Handbook plan", "Generate explanations, examples, revision checks, and visual briefs"],
    ["Quality checks", "Missing topics, examples, sources, or visual blocks are surfaced"],
  ];
  return (
    <SceneFrame start={23.5} end={28.3}>
      <div className="kicker">From Syllabus To Handbook</div>
      <h2 className="headline route-headline">Protect the official source first, then make it usable for preview and revision.</h2>
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
    ["English body", "Support languages add a 30-50 term glossary instead of translating the whole handbook."],
    ["Style modes", "formal, friendly, life, story, detective, or adventure, so the prose is not painfully stiff."],
    ["Worked examples", "Each topic gets original questions, steps, answer frames, and common pitfalls."],
    ["Visual judgment", "Only concepts that genuinely need visuals get diagrams or infographics."],
  ];
  return (
    <SceneFrame start={28.0} end={32.8}>
      <div className="kicker">Language, Style, Examples</div>
      <h2 className="headline provider-headline">The exam is in English; support languages belong in the glossary.</h2>
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
    ["7", "local regression samples pass with clean quality checks"],
    ["357", "knowledge explanations generated across the three boards"],
    ["318", "worked-example cards with steps and checkpoints"],
    ["0", "complex infographics are no longer pretended as generated"],
  ];
  return (
    <SceneFrame start={38.0} end={43.1}>
      <div className="sample-scene">
        <div className="sample-copy">
          <div className="kicker">Real Handbook Samples</div>
          <h2 className="headline sample-headline">The samples are deliverable revision handbooks.</h2>
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
            <img src="../three-board-support-video/sample-math-guide.png" alt="Mathematics handbook screenshot" />
          </figure>
          <figure className="shot" style={{ left: 250, top: 250, transform: "rotate(3deg)" }}>
            <img src="../three-board-support-video/sample-economics-guide.png" alt="Economics handbook screenshot" />
          </figure>
          <figure className="shot" style={{ left: 0, top: 455, transform: "rotate(-1deg)" }}>
            <img src="../three-board-support-video/sample-chemistry-guide.png" alt="Chemistry handbook screenshot" />
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
      title: "Simple exact visuals: local SVG",
      body: "Number lines, axes, simple geometry, and compact tables stay local and deterministic.",
      visual: <div className="svg-diagram"><span></span><span></span><span></span></div>,
    },
    {
      title: "Structured diagrams: Kroki",
      body: "Flows, hierarchies, timelines, relationship maps, and concept maps use professional diagram rendering.",
      visual: <div className="queue-lines"><i></i><i></i><i></i><i></i></div>,
    },
    {
      title: "Rich infographics: external generation",
      body: "Labs, economics scenes, and dense text-plus-diagram explanations become worksheet-style image jobs and auto-imported assets.",
      visual: <div className="model-grid"><span>GPT Image 2.0</span><span>Qwen Image 2.0 Pro</span><span>SenseNova U1 Fast</span></div>,
    },
  ];
  return (
    <SceneFrame start={32.5} end={38.2}>
      <div className="kicker">Professional Visual Handling</div>
      <h2 className="headline route-headline">SVG, Kroki, and external infographics each have their own job.</h2>
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
    ["outline", "syllabus comparison"],
    ["glossary", "term table check"],
    ["visuals", "image/diagram check"],
    ["pdf", "sampled PDF pages"],
  ];
  return (
    <SceneFrame start={42.8} end={46.2}>
      <div className="kicker">Independent Agent Review</div>
      <h2 className="headline provider-headline">Generation is not the finish line; the final handbook must be read and repaired.</h2>
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
  const boxes = ["Official syllabus", "English body + glossary", "Worked examples", "Review evidence"];
  return (
    <SceneFrame start={45.8} end={TOTAL_DURATION}>
      <div className="final-lockup">
        <div>
          <div className="kicker">Final Delivery Standard</div>
          <h2 className="headline">The final file should feel like material a student can really use.</h2>
          <p className="lead">Syllabus, explanations, glossary, visuals, examples, and PDF pages must pass the final product review before final-ready.</p>
        </div>
        <div className="deliverable" style={{ opacity: p, transform: `rotate(${-1.5 + (1 - p) * -7}deg) translateY(${(1 - p) * 100}px)` }}>
          <h3>International GCSE / AS-A-level Revision Handbook</h3>
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
      <span>IGCSE & A-Level AI Revision Handbook Skill · v0.4.2</span>
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
