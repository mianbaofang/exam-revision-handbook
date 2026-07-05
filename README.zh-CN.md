# IGCSE & A-Level AI Revision Guide Skill

<p align="center">
  <img src="docs/assets/hero.svg" alt="IGCSE 与 A-Level AI 复习手册 Skill 封面" width="100%">
</p>

## 为什么要做这个 Skill

这个项目最早不是为了做一个“工具”，而是为了帮一个真实的孩子轻一点地走过转轨期。
我的儿子今年要参加 International GCSE 大考；他从公办体系转到国际课程还不到一年，
课堂语言几乎一下从全中文切换到全英文。知识点本身可以慢慢学，但新的语言、新的考试方式
和临近大考的时间压力叠在一起，很容易让孩子觉得自己被推着走。

我用 AI 做了一个学习、复习用的 Skill：让它围绕对应课程要求，把知识点拆成能理解的结构、
例题、图解和检查点。这个项目的初衷很简单：不是替孩子学习，而是把学习路上的噪音降下来，
利用人工智能帮助孩子更轻松、更有掌控感地面对学业。

<p align="center">
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">
    <img src="docs/assets/intro-animation-preview.gif" alt="三大考试局复习手册 Skill 介绍动画预览" width="100%">
  </a>
</p>

<p align="center">
  <a href="README.md">English</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/">项目主页</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">介绍动画</a>
  ·
  <a href="docs/index.html">项目详情</a>
  ·
  <a href="docs/release-evidence/README.md">发布证据</a>
  ·
  <a href="skill/references/revision_guide_spec.md">手册规范</a>
</p>

**这个项目是框架，不是离线内容生成器。** `skill/` 里的 Skill 说明会让
OpenClaw、Hermes 或其它 Agent 的宿主 LLM 扮演 Writer：根据当前官方大纲和
`concepts/concept_jobs.json` 即时写概念解释、例题和学习路线；宿主还必须开启独立
Reviewer 子 Agent 复查渲染后的手册。Python 包只负责抓取官方来源、规划结构、导出
HTML/PDF、登记图片资产、写入 concept/image jobs 和执行验证门槛。

CLI 只是框架调试和草稿 fallback。直接运行 `python -m intl_exam_guide generate ...`
会得到结构完整但教学内容偏骨架化的 draft，不能当成已经可交给学生的最终手册。

一个给 AI Agent 使用的复习手册 Skill：输入国内常用三大国际考试局的科目要求，
生成图文并茂、可打印的 International GCSE / International AS-A-level 学习复习手册。

当前版本以三大考试局为基础设计：

| 考试局 | 当前支持方式 |
|---|---|
| AQA | 支持从官网科目目录发现课程，并读取公开大纲 PDF。 |
| Edexcel | 会先根据科目名尝试匹配官方候选页面；无法唯一确认时列出候选，也支持用户直接提供官方科目页或大纲 PDF。 |
| CAIE | 会从官方科目索引匹配候选；无法唯一确认时列出候选，也支持官方科目页或大纲 PDF；遇到多个考试年份时会先确认年份。 |

说明：文档和用户提示里优先使用国内更常见的简称 AQA、Edexcel、CAIE；对应全称分别是 OxfordAQA / Oxford International AQA、Pearson Edexcel、Cambridge International / CAIE。

这套流程面向三大考试局统一设计：先读取官方大纲，再围绕当前 topic/source points 写出已复查的概念解释，生成例题、图文学习单元、复习题和 PDF。

## 快速使用

普通用户不需要安装 Python，也不需要看懂代码。把下面这个 Skill 链接发给你的
OpenClaw、Hermes 或其他支持 Skill 的 Agent：

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

然后直接说：

```text
请安装这个 Skill，然后帮我生成 AQA Chemistry International GCSE 复习手册，附中文专业词对照表，并导出 PDF。
```

也可以这样说：

```text
帮我生成 Edexcel Accounting International GCSE 复习手册。
帮我生成 Cambridge IGCSE Economics 2027 考试用复习手册，附日语专业词对照表。
帮我生成 AQA Mathematics 9260 复习手册，需要图文例题和最终复习题。
```

开始生成前，Agent 应先确认五件事：

1. 考试局、课程阶段、科目和代码，必要时确认官方链接。
2. 考试年份，尤其是 Cambridge 页面同时列出多个年份范围时。
3. 术语辅助语言：`en` 表示不加对照表；`zh-CN`、`zh-TW`、`ja` 等表示在英文正文基础上增加 30-50 个“用户语言 → English exam term”专业词对照表。手册正文、标签、例题和配图提示仍使用英文。
4. 讲解风格：严谨、轻松、生活化、故事性、侦探推理、闯关式等。
5. 是否存在本次可调用的信息图/生图路线：已安装 Skill、自定义 API + 环境变量、项目脚本，或已有图片目录。没有可调用路线时，Agent 只能继续生成 draft，并把复杂信息图标记为 pending。

注意：不需要在一开始选择生图模型。基础手册先生成，之后 Agent 会告诉你有多少张复杂信息图需要生成或复核。
如果你有可调用的生图 API、Skill、脚本或已经生成好的图片目录，Agent 应该自动调用该路线生成图片，并自动导入或挂接到手册；如果没有，复杂信息图应保留为待生成/待复核任务。SVG 只允许用于 `svg_fit="exact"` 且已复核的精确图。

## 会生成什么

每次生成会输出一个完整手册包：

```text
outputs/chemistry-9202/
  guide.html                 可预览、可打印的学习手册
  guide.pdf                  PDF 文件
  sections/                  分章节手册内容，便于 Agent 复查
  images/                    配图清单、已复核资产和待生成任务
  concepts/                  概念解释任务和已复查概念解释
  run-options.json           本次确认的科目、语言和讲解风格
  guide-plan.json            知识点、例题和复习任务规划
  qualification.json         课程与来源信息
  validation.json            完整性检查结果
  handbook-package.json      最终交付清单
  final-review-packet.json   独立 reviewer 最终复查证据
  agent-product-review.json  当前 Agent 读成品、修复并兜底后的产品复查证据
```

手册内容包括：

- 官方大纲整理出的知识点结构；
- 从每个 topic/source job 复查后的学生友好概念解释；
- 原创例题、步骤和答案检查点；
- 适合图文讲解的知识点与例题；
- 已复核的 exact-SVG 资产和复杂信息图需求清单；
- 最终备考复习题；
- 可打印 HTML/PDF。

在把输出当成最终成品交给学生前，必须运行
`python -m intl_exam_guide review --out <output-dir>` 并阅读
`final-review-packet.json`。Validation 不是充分条件；独立 reviewer 要看渲染摘录、
topic/source 摘要、例题证据、概念解释任务和视觉任务状态。当前 Agent 还必须像学生一样
打开手册成品，检查 PDF 页面、图像、术语策略和大纲对应关系，修复能修的问题，并写入
`agent-product-review.json`。没有这个产品复查证据，即使 validation 没有 error，也只能是
review-ready 或 draft，不能标 final-ready。

只有 candidate 证据的路线不能说成交付级。如果 `concepts/concept_jobs.json` 里还有未导入的概念解释，或复杂信息图还 pending，这份手册只能算 draft。

## 效果预览

| Mathematics | Economics | Chemistry |
|---|---|---|
| <img src="docs/assets/sample-math-guide.png" alt="数学复习手册图文例题截图" width="100%"> | <img src="docs/assets/sample-economics-guide.png" alt="经济学复习手册信息图截图" width="100%"> | <img src="docs/assets/sample-chemistry-guide.png" alt="化学复习手册信息图截图" width="100%"> |

这些截图只是展示最终手册长什么样，不代表项目只支持这三门课。

## 三大考试局支持范围

| 考试局 | International GCSE | International AS-A-level | 当前说明 |
|---|---:|---:|---|
| AQA | 支持 | 支持 | 可从官网科目目录发现课程。 |
| Edexcel | 支持 | 支持 | 根据科目名匹配官方候选；多个候选时让用户选择；官方 URL/PDF 可作为精确输入。 |
| CAIE | 支持 | 支持 | 从官方科目索引匹配候选；多个候选时让用户选择；官方 URL/PDF 可作为精确输入；多年份页面会先确认考试年份。 |
| OCR、WJEC/Eduqas、CCEA 等其他英国考试局 | 暂不支持 | 暂不支持 | 不在当前版本范围内。 |

项目当前聚焦国内常用的 AQA、Edexcel 和 CAIE。
以后可以继续扩展，但不会把未支持的考试局写成已经支持。

交付质量以 `tests/fixtures/delivery_matrix.json` 里的交付矩阵为准。每条路线都有明确的
claim status 和 v0.4 release-evidence status；三大考试局共享同一套生成流程，但不等于所有科目、
所有级别都已经验证。候选路线不能说成交付级，只有在新的输出同时通过 validation、
最终 Agent 复查和视觉状态检查，并写入 release-evidence manifest 后，才能升级为可交付样例。

v0.4 使用四个状态词：

- `candidate`：有路线或样例证据，但不是交付级。
- `draft`：有当前输出，但概念、图片、PDF、validation 或自查仍有阻塞。
- `final-ready`：当前证据显示可以交付复核/使用，validation、最终复查和资产状态都已通过。
- `certified`：在 final-ready 之上，又经过发布负责人或熟悉学科的人确认；除非证据 manifest 明确记录，否则不要称为 certified。

## 图文与讲解风格

孩子愿意看的手册不能只有文字。生成流程会做两次判断：

1. 先根据官方大纲生成知识点、讲解和例题。
2. 再判断哪些知识点或例题需要图文结合讲解。

宿主 LLM/Agent 判断每个 topic 或例题到底需要纯文字、exact-SVG 候选，还是更复杂的信息图。SVG 只允许用于几何、坐标轴、标签、简单表格或简单流程能完整表达含义的场景；Writer 必须写明 `svg_fit="exact"`，并且资产经过 reviewed 或 approved 后才能进入最终交付。

如果用户没有可调用的生图模型，复杂视觉内容会保留在 `images/infographic_jobs.json` 和 `images/infographic_jobs.md` 中。Python 框架不会用本地 deterministic SVG 冒充复杂信息图。Kroki 或 SVG 输出只能作为已复核的 exact-fit 资产，不能替代高密度信息图。

推荐的外部生图模型包括：

- OpenAI GPT Image 2.0；
- Qwen Image 2.0 Pro；
- SenseNova U1 Fast。

这些只是推荐选项，不代表每个用户都能直接调用。用户需要自己提供可用的 API、Skill、脚本或图片目录。
生图只负责解释已经选中的知识点，不能编造大纲里没有的考试结论。

讲解风格也可以选择：严谨备考、轻松愉快、生活场景、故事化、侦探推理、闯关式等。
默认使用原创表达，不复刻受保护角色或世界观。

生成链路里也加入了一个轻量“反模板腔”检查：会先清理“总之”“综上所述”“值得注意的是”
这类安全可删的 AI 腔过渡语；如果仍然出现明显模板化表达，验证报告会给出 warning，方便后续复核。

设计参考说明：讲解文字的反模板腔检查借鉴了 `qiaomu-novel-generator` 里的 anti-AI language gate 思路。SVG 复核规则采用 figure contract 的原则：先写清楚图要解释的 claim、标签、来源依据和误导风险，再决定是否批准资产。这只是文档约束，不是运行时依赖。

## 语言策略

手册正文始终使用英文，因为考试本身是英文。生成前选择的是“术语辅助语言”，不是“整本手册翻译语言”：

- `en` 表示纯英文手册，不加术语表。
- `zh-CN`、`zh-TW`、`ja` 或其它受支持语言，会在英文正文基础上增加 30-50 个“用户语言 → English exam term”专业词对照表。
- 讲解正文、例题、标题、图中文字和生图提示词仍然使用英文。
- 不生成整本中文/日语正文，也不在正文里到处插入 `中文 / English` 这类拼接标签。

## 版本更新说明

版本更新说明统一放在 [GitHub Releases](https://github.com/mianbaofang/igcse-a-level-revision-guide/releases)
和 [CHANGELOG.md](CHANGELOG.md)。中文 README 只保留项目定位、使用方式和核心生成流程。

## 开发者快速开始

普通用户可以跳过这一节。只有想修改 Python 引擎或本地调试时才需要看。
这条命令只运行 CLI-only fallback，没有运行 LLM syllabus_outline_analyst，只能产出 `draft/evidence-ready`；真正可教学的手册必须通过 Skill 宿主 LLM 完成大纲 outline、考点、概念写作和独立 reviewer 复查。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language zh-CN --explanation-style friendly --out ./outputs/chemistry-9202
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language zh-CN --explanation-style friendly --out .\outputs\chemistry-9202
```

常用检查：

```bash
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
```

## 目录结构

```text
src/intl_exam_guide/
  providers/      各考试局官方页面读取与解析
  parsing/        PDF 文本抽取
  planning/       知识点、例题和配图需求规划
  rendering/      HTML 与 PDF 渲染
  validation/     完整性检查
skill/            Agent 使用的 Skill 说明
docs/             项目详情、准确性政策、示例和展示页面
tests/            测试与回归样例
```

## 版权与来源

不要把下载的官方 PDF、past papers、mark schemes 或复制来的真题内容提交到仓库。
公开样例应使用原创讲解、原创练习卡和必要的来源信息。

给孩子正式备考使用前，建议由老师或熟悉大纲的人复核深度例题和答案。

## License

MIT.
