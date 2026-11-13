# Image Model Guide / 生图模型建议

## English

The handbook's factual content must not depend on image generation. In the
current framework, Python performs mechanical execution only: it downloads the
official source, extracts page text, receives LLM-authored JSON, renders HTML,
exports PDF, and validates artifacts. The host LLM/Agent decides what the visual
should explain.

For many subjects, richer illustrations are still useful:

- science lab apparatus and safety layouts;
- maths geometry diagrams and step-by-step annotated figures;
- biology structures and process diagrams;
- chemistry particle or reaction sketches;
- physics force, circuit, wave, and energy-transfer diagrams;
- economics curves, flow diagrams, and scenario posters;
- text-heavy infographics in English, with official formulae and syllabus terms
  preserved when needed.

Use image generation as an optional illustration adapter, not as the source of
truth. The LLM/Agent should first write source-bound knowledge points and
practice examples, then record both `visual_decision` and topic-specific
`visual_guidance` for every topic. A useful visual is the default whenever a
diagram, comparison, process, apparatus, field, graph, spatial relationship,
data pattern, or annotated example can make the source-bound claim easier to
see. The outcome is one of four recommended routes:

- `text-ok`: a separate visual is genuinely unnecessary; include a specific
  `no_visual_reason` and matching `visual_guidance`. Text being able to explain
  the idea is not enough to omit a useful visual.
- `exact-svg`: an SVG is a last-resort exception. It is acceptable only when no
  callable external image route exists, or a separately recorded exactness
  exception proves that an external image would create an unacceptable semantic
  risk. The fact that a graph, equation, circuit, or label can be drawn with
  lines is not enough. The Writer must mark `svg_fit: "exact"`, name the exact
  structure that must be preserved, and the asset must be reviewed or approved
  before delivery.
- `kroki-diagram`: a professional formal diagram is appropriate and must be
  reviewed before delivery.
- `external-infographic`: use a verified external route for richer explanation,
  realistic/reference appearance, apparatus, scenes, modelling nuance, material
  appearance, or dense annotation. The visual becomes a source-bound external
  infographic job until a callable route or reviewed imported asset exists.

The base handbook pipeline does not require an image model, but the first
preflight exchange must ask whether the user can provide or enable an external image-generation Skill or tool that is callable. This is a capability gate, not a model
menu: do not choose a provider or silently default to local image generation.
After the guide has a visual manifest, report the complex visual IDs and use
only the route the user confirmed:

- installed image-generation Skill;
- project script;
- reviewed generated-asset directory;
- `custom` provider configuration with model name, endpoint URL, and API-key
  environment variable name.

Never collect the raw key in chat, docs, screenshots, or committed files.
When a callable `image-gen-flow` GPT or SenseNova channel is supplied, it counts
as an external route only after the current run verifies that the channel can be
invoked. A verified route with an unjustified simple-SVG downgrade is a delivery
blocker.

## Exact SVG Review Policy

Exact SVG is a reviewed last-resort exception, not a local fallback for
unfinished images. If a callable external route exists and the user asks to
avoid SVG, use the external route for graphs, circuits, waves, and relationship
diagrams, then review the imported raster for exact axes, geometry, labels,
units, arrows, and topology. Use SVG only when the exact structure cannot be
reliably represented any other way and that reason is recorded.

Good candidates include number lines, probability trees, statistics charts,
distance-time graphs, rate curves, pH scales, energy profiles, and simple
labelled geometry. Do not use SVG for rich educational posters, dense lab
apparatus, complex economics scenarios, or text-heavy infographics; those remain
external jobs until a reviewed raster asset is supplied.

Before approving an SVG asset, record the learning claim, required labels,
source-bound symbols or values, and review risk. The manifest entry must include
`svg_fit: "exact"` and `review_status: "reviewed"` or `"approved"` before the
asset can be treated as deliverable. Review SVGs across pages, not one by one only:
repeated structures, repeated titles, or reused decorative diagrams across unrelated
topics are a handbook-quality failure even when each individual SVG renders.

## Recommended Providers

| Provider | Best use | Notes |
|---|---|---|
| GPT Image 2.0 | High-quality option for OpenAI-compatible workflows, visual explanations, edits, and polished guide illustrations. | Treat it as an external capability unless the user has a callable route. Check cost, moderation, and organization requirements. |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | Chinese or English text-heavy infographics, poster-like layouts, PPT-style visual explanations, and China-market experiments. | Treat API availability, provider endpoint, license, and deployment constraints as configurable. |
| SenseNova U1 Fast | Fast infographic drafts, local/provider experiments, dense visual communication, and interleaved image-text tests. | Use as an experimental provider until this project has its own visual benchmark set. |

Do not hard-code one provider and do not imply these providers are available to
every user. Use a provider interface so schools, tutors, or agents can choose
based on availability, cost, privacy, and language quality.

## Suggested Architecture

Use this as the integration flow:

```text
official specification
  -> Python extracts page evidence and external MarkItDown creates source/specification.md
  -> LLM reads Markdown + page evidence and writes syllabus outline and concept/practice content
  -> LLM records visual_decision + visual_guidance for every topic
  -> verified external route is preferred for visuals with learning value
  -> exact-svg is reserved for explicit exactness exceptions
  -> Python records visual manifest and pending jobs
  -> reviewed exact SVG or reviewed raster asset is imported
  -> Python renders HTML only
  -> LLM personally reviews and repairs the current HTML until it passes
  -> PDF export runs only after hash-bound LLM HTML approval
```

Recommended interface:

```text
generate_illustration(
  provider_config,
  topic_id,
  topic_title,
  source_snippet_ids,
  visual_type,
  required_labels,
  forbidden_claims,
  language_policy,
  output_size
)
```

Each generated image should store:

- model/provider name;
- prompt;
- source topic and source snippets;
- generation time;
- caption and alt text;
- review status;
- whether it is safe for student-facing use.

## Importing External Assets

The open-source repository does not hard-code private image APIs. If an agent or
teacher generates infographic files with GPT Image, Qwen Image, SenseNova U1
Fast, or a custom provider, name each file with the manifest ID, for example:

```text
visual_001.png
visual_002_market-equilibrium.png
visual_003.webp
```

When the base handbook package is written, the `images/` directory includes:

- `visual_manifest.json`: every visual entry and its current file/status
- `infographic_jobs.json`: pending external infographic replacement jobs
- `infographic_jobs.md`: the same pending jobs in a review-friendly checklist

Each pending job records the visual ID, prompt, replacement target, source
pages, and the import hint. Pending handbook blocks show the visual job ID so
the reviewed raster file can replace that slot by name.

Generate complex images with whatever callable workflow the user actually has:
an image Skill, API, script, design tool, or designer review process. If the
workflow is callable, the Agent can run it automatically after the base guide is
generated. Then import the reviewed files into the guide package when they are
written outside `images/`:

```bash
python scripts/import_infographic_assets.py ./outputs/chemistry-9202 \
  --asset-dir ./generated-infographics/chemistry-9202 \
  --provider "gpt-image-2"
```

The script copies matching raster images into `images/`, updates
`images/visual_manifest.json`, replaces pending infographic slots that share the
same visual ID, and marks imported entries as generated. Importing or replacing
an asset resets that entry's visual-level LLM decision to `pending`; the file's
asset `review_status` is separate. The import rerender uses the existing
manifest only and never rebuilds it. After a successful import it prints the
exact handbook review command to run:

```bash
python scripts/run_runtime.py -- review --out ./outputs/chemistry-9202
```

## Routing Rules

- Let the LLM/Agent decide whether a visual is needed; Python must not infer the
  teaching need from keywords.
- Use exact SVG only for `svg_fit: "exact"` cases with reviewed or approved
  status.
- Use GPT Image 2.0 when the user wants polished guide illustrations and a
  callable OpenAI-compatible image route is available.
- Use Qwen-Image-2.0 or Qwen Image 2.0 Pro when text-heavy infographic layout is
  the main evaluation point.
- Use SenseNova U1 Fast for fast infographic drafts, local experiments, or
  low-latency provider tests.
- Do not recreate official exam paper diagrams, mark scheme diagrams, or
  copyrighted textbook illustrations.
- Do not add labels, mechanisms, equations, or facts that are absent from the
  extracted specification unless a subject expert reviews them.

## Prompt Template

```text
Create a diagram-led educational visual for an International GCSE
or International A-Level revision guide.

Exam board: {exam_board}
Qualification: {qualification_title}
Topic: {topic_title}
Source-bound learning point: {source_point}
Visual type: {visual_type}
Required labels: {required_labels}
Language policy: use English labels for the handbook body and visual text;
preserve official formulae, symbols, and reviewed syllabus terms when needed.

Art direction: use a landscape 4:3 aspect ratio by default; landscape 3:2 is
also acceptable. Do not use a portrait 3:4 image unless the current run
explicitly requests it. Make the diagram, apparatus, process, graph, field,
structure, or relationship the dominant teaching content. Keep text minimal:
short labels, callouts, symbols, units, and at most one brief caption. Do not
turn the image into a text-heavy poster, worksheet, paragraph panel, slide of
copied notes, or a second copy of the handbook explanation. Use a clean visual
hierarchy, pastel subject colors, and readable labels. Do not add institutional
logos, exam board branding, course-cover headers, watermarks, new syllabus
facts, named examples, equations, or exam claims beyond the source point.

Visual text is allowed: labels, callouts, legends, axes, captions, and short
example annotations may be included when they are accurate, legible, and
source-bound. The Skill does not require text-free images. Visual selection is
made independently for each final topic; there is no one-image-per-subject
quota. An external image may be a realistic/reference/example image when that
improves the topic's learning claim, not only a formal diagram.
```

## 中文

复习手册的核心事实不应该依赖生图模型。当前框架中，Python 只负责机械执行：下载官方来源、抽取页面文本、接收 LLM 写好的 JSON、渲染 HTML、导出 PDF 和校验产物。视觉内容要解释什么，由宿主 LLM/Agent 判断。

很多知识点确实需要更好的视觉解释，例如：

- Science 实验装置和安全布局；
- Biology 结构图和过程图；
- Chemistry 粒子模型、反应过程示意图；
- Physics 力、电路、波、能量转移图；
- Economics 曲线图、流程图、场景信息图；
- 英文文字信息图，必要时保留公式、符号和经复核的官方术语；用户语言支持放在专业词对照表中。

生图应该是可选插图层，不是事实来源。LLM/Agent 应先写出 source-bound 知识点和例题，再为每个 topic 记录 `visual_decision` 和 topic-specific `visual_guidance`。只要图形、比较、过程、装置、字段、图像、空间关系、数据模式或带标注的例题能帮助学生看懂，就应使用视觉：

- `text-ok`：确实不需要单独图片，必须写具体 `no_visual_reason` 和匹配的 `visual_guidance`；“文字也能解释”不等于可以省略有学习价值的图。
- `exact-svg`：SVG 是最后例外。只有没有可调用外部生图路线，或有单独记录的不可接受外部生图语义风险时才允许；“图表、公式或电路可以用线画出来”本身不构成例外。Writer 必须写明 `svg_fit="exact"`、必须保持精确的结构和外部路线风险，且资产 reviewed/approved 后才能交付。
- `kroki-diagram`：适合专业正式图表，生成后也必须复核。
- `external-infographic`：有可调用外部路线时，装置、复杂几何、电路、真实场景、材质、建模细节和多面板标注等应优先走该路线，直到有已复核导入资产。

外部生图默认使用横版 `4:3`，也允许横版 `3:2`；除非用户在当前任务中明确要求，否则不要使用竖版 `3:4`。画面必须以图形、装置、过程、图像、场、结构或关系为主，文字只保留短标签、标注、符号、单位和至多一句简短说明。不要把图片做成密集文字海报、练习卷、段落面板或手册解释的复制版。

第一次预检必须先询问用户是否能提供或启用本次可调用的外部生图 Skill 或工具；在得到明确回答前，不得下载来源、写手册或默认使用本地生图。不要把模型列表做成生成前菜单。完成每个 topic 的 `visual_decision` 和 `visual_guidance` 后，再报告复杂视觉 ID，并只使用用户确认且实际可调用的路线：已安装生图 Skill、项目脚本、已复核图片目录，或带模型名、接口 URL、API key 环境变量名的 `custom` 配置。用户提供的 `image-gen-flow` GPT 或 SenseNova 通道也必须先验证可调用。不要在聊天、文档、截图或仓库里暴露真实 key。

## Exact SVG 复核规则

Exact SVG 是经过复核的最后例外，不是未完成图片的本地 fallback。用户有可调用外部路线且要求避免 SVG 时，图表、电路、波形和关系图默认走外部生图；只有记录了不可接受的语义风险、且外部图无法可靠表达时，才可以使用 SVG。

适合场景包括 number line、probability tree、statistics chart、distance-time graph、rate curve、pH scale、energy profile 和简单 labelled geometry。复杂实验装置、经济学场景、密集文字信息图或教学海报必须保持为外部任务，直到有已复核 raster 资产。

批准 SVG 前，要记录学习 claim、必要标签、来源绑定的符号或数值，以及误导风险。manifest 条目必须包含 `svg_fit="exact"`，并且 `review_status` 为 `reviewed` 或 `approved`，才能作为可交付资产。

## 推荐模型

| Provider | 适合场景 | 备注 |
|---|---|---|
| GPT Image 2.0 | OpenAI-compatible 工作流里的高质量选项，适合复习手册插图、视觉解释和编辑。 | 只有用户有可调用路线时才使用；注意成本、内容审核和组织要求。 |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | 英文文字较多的信息图、海报式解释、PPT 风格知识图、国内场景实验。 | API、服务商、许可和部署限制应做成配置，不要写死。 |
| SenseNova U1 Fast | 快速信息图草稿、本地或自定义 provider 实验、密集图文表达测试。 | 在本项目建立自己的视觉基准前，建议作为实验性 provider。 |

不要把项目绑定到单一 provider。更好的做法是设计 provider interface，让学校、老师、家长或 agent 按可用性、成本、隐私和所选语言的排版质量来选择。

## 生成边界

- 由 LLM/Agent 判断是否需要图，Python 不根据关键词自动决定教学视觉需求。
- SVG 只用于 `svg_fit="exact"` 且 reviewed/approved 的场景。
- 需要精美插图且用户有可调用 OpenAI-compatible 图像路线时，可以评估 GPT Image 2.0。
- 需要文字密集型信息图时，可以评估 Qwen-Image-2.0 / Qwen Image 2.0 Pro。
- 需要快速信息图草稿、本地实验或低延迟 provider 测试时，可以评估 SenseNova U1 Fast。
- 不要复刻官方真题图、mark scheme 图或教材版权插图。
- 不要让图片添加 specification 中没有的标签、机制、公式或考试结论，除非经过学科老师复核。
