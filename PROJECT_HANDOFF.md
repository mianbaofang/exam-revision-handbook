# 项目交接文档

> **当前收尾更新（2026-09-09）**：本文件下方保留了早期交接快照和历史阻塞
> 记录，不能代表当前手册状态。当前正式 OxfordAQA International AS Physics
> 2027 手册已经完成 94 个按实际考点拆分的 Topic、94 个 4:3 横向外部信息图，
> 当前 HTML 已完成完整可见审查并批准，PDF 与桌面交付副本已通过哈希绑定。
> 当前权威状态文件是
> `artifacts/as-physics-2027-review/agent-product-review.json`、
> `current-render.json`、`current-pdf.json`、`current-delivery.json`；当前
> 交付审计为 `delivery_eligible: true`，无 blocker、无 warning。旧的 33-topic、
> 中文旁路和 pre-repair accuracy/layout 报告均仅作历史证据。

**项目：** Exam Revision Handbook
**仓库：** `mianbaofang/exam-revision-handbook`
**工作目录：** `(仓库工作目录)`
**交接快照日期：** 2026-09-06
**当前分支与提交：** `main` / 待打 `v0.8.0` 标签的发布提交
**当前正式 Release：** `v0.8.0`（2026-11-13）。

本文件面向接手维护、验证或发布此项目的人员。它说明当前事实、不可绕过的产品约束、关键文件、运行方式、发布要求和已知未闭环事项。它不是 Skill 入口，也不替代 `skills/exam-revision-handbook/SKILL.md`。

## 1. 当前状态

### 1.1 已发布状态

- 当前公开 Release 为 `v0.8.0`（2026-11-13）。历史基线 `v0.7.4`（2026-08-17）
  与 `v0.7.1`（2026-07-27）均不再是当前发布；`manifest.json` 与
  `skills/exam-revision-handbook/manifest.json` 当前均为 `0.8.0`。
- `v0.8.0` 的核心变更：OxfordAQA International AS Physics 2027 手册交付收尾
  （94 个考点主题、94 张横向外部信息图、HTML/PDF/桌面副本哈希绑定）、视觉策略
  进入引擎并重建运行时 Wheel、旧 `choice` 时代之后的治理证据入库。
- 历史发布验证与 ZIP SHA-256 保留下文旧快照中；它们只代表当时版本，不代表
  当前 `v0.8.0` 工作树、运行时或未来版本的校验值。

### 1.2 当前 `main` 状态

当前 `main` 待打 `v0.8.0` 标签（发布说明见 CHANGELOG 的 0.8.0 小节与 GitHub Release）。
此前 `4d0fa4b`（`v0.7.4`）及其更早的 `22f6b1d` 等提交均为历史；下文带日期的
快照小节（2026-09-06 / 09-07 / 09-09）记录的是各自时点的事实，不构成当前状态。

### 1.3 本地健康检查

历史交接快照中曾执行以下本地检查：

```text
python skills/exam-revision-handbook/scripts/doctor.py
```

结果为通过：Python `3.13.0` 可用，内嵌 `exam_revision_handbook-0.7.1-py3-none-any.whl` 的锁定 SHA-256 与当时的 `skills/exam-revision-handbook/assets/runtime/runtime-lock.json` 一致，隔离运行时可用。该记录属于历史快照，不代表当前 `v0.8.0` 运行时的最新探针结果。

本次当前快照另有：`513 passed, 163 skipped`（使用独立 `--basetemp`，避免 Windows 临时目录权限问题）、变更脚本 Ruff 通过、Python 编译通过、`git diff --check` 通过，以及独立桌面中文 HTML 的桌面/移动 Playwright 检查通过。这些结果不解除本次 canonical 运行链的阻塞；任何功能、运行时、包结构或发布相关改动后，都必须重新执行第 10 节中的相应验证。

## 2. 项目定位和范围

这是一个单一的开源 Agent Skill 项目，不是多个平行仓库、多个版本线或“源码版/安装版”两套产品。

- 产品名称：`Exam Revision Handbook`
- 唯一 Skill 名称：`exam-revision-handbook`
- 唯一权威 Agent 入口：`skills/exam-revision-handbook/SKILL.md`
- GitHub 自动发现与安装边界：`skills/exam-revision-handbook/`
- 默认分支：`main`
- 公开远端：`https://github.com/mianbaofang/exam-revision-handbook.git`

在已发布提交中，GitHub `main`、与其匹配的 Git 标签、以及该标签对应的 Release ZIP，是同一个标准 Skill 的不同交付形式。ZIP 只是可安装下载包，不是精简版、第二套架构或第二条开发线。未发布的本地候选不能据此称为已发现或已建立索引。

项目的目标是生成可追溯到官方课程文件、可打印的复习手册。自动官方来源支持范围如下：

- AQA 与 Pearson Edexcel 的英国 GCSE 和 A-Level 路线；
- OxfordAQA、Pearson Edexcel、Cambridge International / CAIE 的国际 GCSE/IGCSE 与 A-Level 路线；
- College Board AP。

AS 和 A2 是 A-Level 的阶段，而不是独立课程体系。CAIE 是 Cambridge International；`uk-domestic` 只记录英国考试中心语境，不会创造一个独立的“CAIE 英国 GCSE”来源。

未支持的课程体系或考试局没有自动官方来源 Provider。用户手工导入 PDF 的路径是实验性能力，可能在 Provider、解析、提取、元数据或渲染环节失败，不能描述为正式支持。

## 3. 接手前必须阅读的文件

先阅读 `PROJECT.md`，再按以下顺序阅读。不要只看 README 后直接修改运行逻辑。

1. `AGENTS.md`：当前工作区的协作、变更和验证要求。
2. `skills/exam-revision-handbook/SKILL.md`：简明执行入口、硬性门禁与停止条件。
3. `skills/exam-revision-handbook/references/workflow-contract.md`：完整工作流合同。
4. `skills/exam-revision-handbook/references/revision_guide_spec.md`：产物、审查、渲染和交付合同。
5. `skills/exam-revision-handbook/references/runtime-contract.md`：打包运行时与命令适配边界。
6. `docs/ARCHITECTURE_DECISION_SKILL_WORKFLOW.md`：LLM 与 Python 的职责划分。
7. `docs/PROJECT_OPERATIONS.md`：维护、打包、反向安装和发布流程。
8. `docs/RELEASE_CHECKLIST.md`：发布前逐项检查清单。

以下文件也常需要一并查看：

- `skills/exam-revision-handbook/manifest.json`：唯一 Skill 版本与生命周期元数据。
- `skills/exam-revision-handbook/assets/runtime/runtime-lock.json`：内嵌 Wheel 的版本、文件名、哈希和最小 Python 版本。
- `skills/exam-revision-handbook/agents/interface.yaml` 与 `skills/exam-revision-handbook/agents/openai.yaml`：平台入口提示和兼容性元数据。
- `tests/fixtures/delivery_matrix.json`：路线交付状态的事实矩阵。
- `docs/ACCURACY_POLICY.md`：教学准确性、人工审查与高风险使用边界。
- `CHANGELOG.md`：已完成迭代及其当时的验证证据。

## 4. 目录与职责

```text
skills/exam-revision-handbook/
  SKILL.md                唯一权威、可发现 Skill 入口
  agents/                 OpenAI、通用 Agent 等入口元数据
  references/             工作流、产物、Provider、运行时合同
  assets/                 锁定运行时与 Skill 资源
  evals/                  路由、工作流、迁移和一致性评估夹具
  reports/                已选入安装包的治理、包和质量证据
  security/               网络和权限策略
  skill_atlas/            路由和维护元数据
  scripts/                运行时、导入助手和 Skill 内工具
repository root:          开发、测试、文档和发布工具
PROJECT.md                项目身份、版本模型、更新矩阵和交接要求
PROJECT_HANDOFF.md        本交接文档
AGENTS.md                 当前工作区协作与变更规则
skills/exam-revision-handbook/manifest.json
                          发布身份和版本
skills/exam-revision-handbook/agents/
                          OpenAI、通用 Agent 等入口元数据
skills/exam-revision-handbook/references/
                          工作流、产物、Provider、运行时合同
skills/exam-revision-handbook/assets/runtime/
                          锁定的 Python Wheel 与 runtime lock
skills/exam-revision-handbook/scripts/
                          运行时启动、导入和 Skill 内助手
src/intl_exam_guide/      可维护的 Python 引擎源码
tests/                    引擎、工作流、打包和回归测试
skills/exam-revision-handbook/evals/
                          路由、工作流、迁移和一致性评估夹具
skills/exam-revision-handbook/reports/
                          已生成的治理、包、安装和质量证据
skills/exam-revision-handbook/security/
                          网络和权限策略
skills/exam-revision-handbook/skill_atlas/
                          路由和维护元数据
docs/                     公共文档、GitHub Pages 和发布操作说明
README.md                 英文用户入口
README.zh-CN.md           中文用户入口
CHANGELOG.md              版本和迭代记录
```

`src/`、`tests/`、`docs/`、README 和开发工具属于同一项目的维护材料。它们保留在 Git 中，但不应被打入面向 Skill Host 的 Release ZIP。不要重新创建根 `SKILL.md`、`skill/` 目录、第二个嵌套入口或发现器包装层。安装所需文件必须全部位于 `skills/exam-revision-handbook/` 内，不能依赖 `../..`。

## 5. 核心架构和职责边界

### 5.1 LLM 负责的内容

LLM 必须负责下列不可机械替代的决策：

- 解读官方课程文件，拆分为可独立考查的原子教学点；
- 编写教学解释、类比、例题、解题步骤、答案、易错点和学习目标摘要；
- 对每个最终主题逐一判断是否需要视觉材料，并定义其教学语义；
- 检查每个实际渲染视觉的标签、箭头、比例、关系、单位和学科语义；
- 打开或截图检查完整当前 HTML，并在修复后重新完整审查；
- 只有在完整审查通过时，写入与当前 HTML、渲染快照和审查账本哈希绑定的批准记录。

### 5.2 Python 负责的内容

Python 只能做确定性和机械性工作：

- 发现、下载和提取官方来源；
- 生成页级证据、Markdown 辅助文件、结构校验和哈希；
- 导入 LLM 编写的 JSON 产物；
- 渲染 HTML，生成不可变渲染快照；
- 验证结构、状态、文件、哈希与交付门禁；
- 在所有前置条件成立后导出候选 PDF，并维护当前/历史交付指针；
- 验证内嵌运行时的 Wheel 与隔离环境。

Python 不得拆课程主题、写教学正文、编造 `mastery_summary`、决定视觉是否有教学价值，或替代 LLM 批准最终手册。机械检查通过不等于手册正确，更不等于 PDF 可正式交付。

### 5.3 打包运行时

正式运行时是 `skills/exam-revision-handbook/assets/runtime/` 下锁定的 Wheel。运行命令必须经由：

```powershell
python skills/exam-revision-handbook/scripts/doctor.py
python skills/exam-revision-handbook/scripts/run_runtime.py -- <command>
```

当前运行时约束：

- 发行版：`exam-revision-handbook`
- 版本：`0.7.1`
- Wheel：`exam_revision_handbook-0.7.1-py3-none-any.whl`
- 最低 Python：`3.11`
- 官方来源获取需要网络；PDF 导出还需要兼容的 Playwright 浏览器。

若修改 `src/intl_exam_guide/` 的行为，必须重建 Wheel、更新 `runtime-lock.json` 中的哈希，并重跑源码与安装包的全部相应验证。只提交源码而没有同步运行时资产版本是不完整变更。

## 6. 手册生成工作流

### 6.1 第一轮必须是完整预检

每次为用户生成手册的第一轮响应只能是完整的结构化预检，不能提前搜索课程、写教学内容、设计视觉、渲染 HTML 或导出 PDF。

第一项必须逐字询问：

```text
Can you provide or enable an external image-generation Skill or tool for this run?
```

然后一次性收集并确认：

```text
external_visual_capability=<yes|no|uncertain>; image_method=<route or none>
board=<AQA|Edexcel|CAIE|College Board AP>; level=<IGCSE|A-Level|AP>
a_level_stage=<AS|A2|full|not-applicable>
course_market=<international|uk-domestic|not-applicable>
subject=<name and optional code>; exam_year_or_syllabus_range=<value|unknown>
term_support_language=<en|zh-CN|zh-TW|ja>
explanation_style=<formal|friendly|life|story|detective|adventure>
workflow_mode=<single-host|multi-agent>; batch_scope=<value>
output_dir=<absolute path>
```

要点：

- `course_market` 必须由用户明确选择，不能从课程名称、代码、URL、考试局或历史项目推断。
- 已配置图像模型、已安装工具、以往运行记录，都不等于用户确认了外部视觉能力。
- 若用户称有外部图片路线，必须实际调用成功并记录为已验证后，才能用于 `external-infographic`。
- 若路线不可用、用户选择 `no` 或 `uncertain`，不得悄悄退回本地图像生成。根据主题可用 `text-ok`、精确 SVG 或 Kroki；需要复杂信息图的项目保持待处理并如实标记。
- 只有用户明确选择 `multi-agent` 时才使用 Analyst、Writer、Reviewer 的多 Agent 编排；默认可以由一个 Host LLM 分角色顺序完成。

### 6.2 正确的状态顺序

```text
完整预检
-> 官方来源证据提取
-> LLM Analyst 编写 syllabus-outline.json
-> LLM Writer 编写 concepts/concept_explanations.json 和逐主题 visual_decision
-> 明确刷新视觉清单
-> 生成或导入视觉资产
-> LLM 逐视觉批准
-> 只读当前清单渲染 HTML 和不可变快照
-> LLM 完整可见 HTML 审查
-> 写入 review-ledger 和 agent-product-review.json
-> 通过交付审计
-> 导出候选 PDF、技术检查和更新 current-pdf.json
```

任何输入、概念、视觉计划、资产或 HTML 的改变都会使下游批准失效。不得通过直接调用渲染函数、凭文件修改时间，或复用另一本手册的审查，绕过这条状态链。

### 6.3 关键产物链

一个正式路径通常包含：

```text
qualification.json
syllabus-evidence.json
source/specification.md
source/markdown-extraction.json
syllabus-outline.json
concepts/concept_jobs.json
concepts/concept_explanations.json
guide-plan.json
visual_manifest.json
images/
render-snapshots/
current-render.json
review-ledger/
agent-product-review.json
validation.json
pdf-exports/
current-pdf.json
current-delivery.json  # 仅在导出到 delivery-dir 时存在
```

`current-render.json`、`agent-product-review.json`、`current-pdf.json` 和 `current-delivery.json` 是当前指针，不是可随意手改的缓存。历史 PDF 和资产应保留为历史记录，除非用户明确批准清理。

### 6.4 HTML 与 PDF 的严格门禁

PDF 只能由当前 HTML 导出，且当前 HTML 必须已经获得完整、LLM 编写、哈希绑定的批准。审查必须覆盖每个主题、例题、答案、来源锚点、视觉语义、版面、重复视觉、响应式布局和数学符号残留。

抽样页面、读取 JSON、查看代码 diff、解析 HTML、运行质量诊断或查看 `final-review-packet.json` 都不能替代完整可见审查。发现问题后必须回写源产物、重新渲染，并从头完整检查新 HTML。

## 7. 交付状态的准确用词

`tests/fixtures/delivery_matrix.json` 定义当前路线证据的用词。不要夸大路线或样例状态：

- `candidate`：存在来源或路由证据，但尚未完成交付。
- `draft`：有当前手册产物，但剩余阻塞项已明确说明。
- `final-ready`：该确切手册完成当前 LLM HTML 审查、视觉与概念状态、PDF 门禁和交付证据。
- `certified`：在 `final-ready` 基础上，另有明确记录的发布所有者或学科审查批准。

当前交付矩阵中的路线是 `candidate`，不应被描述为已认证或对任意课程都已可交付。本次桌面交付 manifest 的状态是
`generated_not_canonical_final`，其 `canonical_skill_boundary.canonical_status` 为
`blocked`；它也不等于 `final-ready`。单条路线的通过、样例 PDF 或另一本手册的审查，不能批准新的手册或一批中的其他项目。

## 8. 常用命令

所有命令从仓库根目录执行。首先确认运行时：

```powershell
python skills/exam-revision-handbook/scripts/doctor.py
```

使用打包运行时：

```powershell
python skills/exam-revision-handbook/scripts/run_runtime.py -- --help
python skills/exam-revision-handbook/scripts/run_runtime.py -- generate --query chemistry --level igcse --out .\outputs\chemistry-9202
python skills/exam-revision-handbook/scripts/run_runtime.py -- review --out <output-dir>
python skills/exam-revision-handbook/scripts/run_runtime.py -- index-review-ledger --out <output-dir>
python skills/exam-revision-handbook/scripts/run_runtime.py -- export-pdf --out <output-dir>
python skills/exam-revision-handbook/scripts/run_runtime.py -- export-pdf --out <output-dir> --delivery-dir <absolute-delivery-dir>
```

导入 LLM 已完成内容或已审阅视觉时使用：

```powershell
python skills/exam-revision-handbook/scripts/import_concept_explanations.py ...
python skills/exam-revision-handbook/scripts/import_infographic_assets.py ...
```

不要把 `generate`、`review` 或通过 `validation.json` 的结果描述为成品手册或 PDF 批准。它们分别是证据准备或机械诊断。

## 9. 维护变更矩阵

### 9.1 修改工作流、Agent 行为或交付规则

必须检查并在共享合同变化时同步：

```text
skills/exam-revision-handbook/SKILL.md
skills/exam-revision-handbook/references/workflow-contract.md
skills/exam-revision-handbook/references/revision_guide_spec.md
skills/exam-revision-handbook/agents/interface.yaml
skills/exam-revision-handbook/agents/openai.yaml
skills/exam-revision-handbook/evals/
README.md
README.zh-CN.md
CHANGELOG.md
```

### 9.2 修改 Python 引擎

除源码和相关测试外，还必须同步内嵌 Wheel、`skills/exam-revision-handbook/assets/runtime/runtime-lock.json`、CLI/输出树/Wheel 载荷证据和回归测试。

### 9.3 修改打包或发布机制

还必须检查 `scripts/build_skill_store_package.py`、`docs/PROJECT_OPERATIONS.md`、`docs/RELEASE_CHECKLIST.md` 以及 conformance、trust、registry、package、install 报告。

任何完成的迭代都应追加到 `CHANGELOG.md`，不要修改历史条目来伪造较早的完成时间。

## 10. 验证和发布流程

### 10.1 常规变更后的最低验证

按改动范围运行，发布前必须完整运行：

```powershell
python -m pytest -q
python -m ruff check .
python -m compileall -q src tests scripts skills/exam-revision-handbook
python -m mypy src/intl_exam_guide
python scripts/scan_for_raw_keys.py .
python skills/exam-revision-handbook/scripts/doctor.py
python scripts/normalize_governance_reports.py --project-root skills/exam-revision-handbook --check
python scripts/build_skill_store_package.py
git diff --check
git status --short
```

仅 Markdown 文档修改时，至少运行 `git diff --check`、检查改动范围和 `python skills/exam-revision-handbook/scripts/doctor.py`；不要为了文档改动重写或伪造生成报告。

### 10.2 发行前额外验证

发布是显式授权操作。没有用户明确授权，不要推送、打 tag、创建 GitHub Release 或上传资产。

发行前需要：确定性构建 ZIP 两次；确认一个顶层目录和一个根 `SKILL.md`；排除维护目录、缓存、官方 PDF、用户输出、私有笔记和本地路径；在干净临时目录反向安装；运行 doctor、全部 CLI help、两个导入 helper 和合成 demo；重新生成治理证据；完整审查 Git diff；最后才提交、推送、打 tag、创建 Release，并回查资产与 CI/Pages。

Release 只允许附加版本化 Skill ZIP 与 `.sha256` 文件。GitHub 源码归档、宣传视频、截图、样例 PDF、官方大纲和生成的手册不能替代安装包或作为 Release 附件。

## 11. 当前治理状态与待办

`skills/exam-revision-handbook/reports/review-studio.json` 是仓库级治理汇总，已生成状态记录了 `0` 个 blocker 和 `6` 个 warning。warning 代表证据缺口，不是应直接编辑报告消掉的文字；它不能覆盖本次 OxfordAQA 手册运行目录中 `validation.json` 的 `35` 个 error、`33` 个 warning 和 `delivery_state=blocked`：

- output eval 的人工盲审和 adjudication 尚未完成；
- Skill Atlas 有一个 drift 信号；
- 没有真实采用、误触发或坏输出的运营事件数据；
- 三个 warning 门禁尚无审查豁免或人工决定；
- world-class evidence ledger 尚缺失，不能声称具备 world-class 证据；
- promotion decisions / release notes 的审查确认尚缺失。

后续只能收集真实、可审计的人工或外部证据，或明确记录审查决定；不得填充虚假遥测，也不得把 `no-data` 改为 `pass`。

## 12. 安全、版权和数据边界

不得提交 API 密钥、Provider 凭证、学生个人信息、学生专属手册、下载的官方 PDF、past paper、mark scheme、教材页、无再分发权资源、含私人数据的 trace/截图、生成输出、缓存或本地绝对路径。

项目不隶属于、也不受 AQA、Edexcel、CAIE 或 College Board 背书。高风险考试准备、地区入学建议、等效资格判断和复杂或有争议的学科内容仍需要合格教师或学科专家复核。

## 13. 常见错误和恢复原则

- **把安装包、源码和临时目录当成不同项目：** 以 `skills/exam-revision-handbook/SKILL.md`、其 `manifest.json`、远端 URL 和 `main` 为准；临时目录只是操作副本。
- **绕过第一轮视觉能力问题：** 停止下游工作，回到完整预检；不可因主机有图像模型而推断用户授权。
- **把机械诊断当最终批准：** 检查当前 HTML 是否由 LLM 完整可见审查，并且批准、审查账本、渲染快照哈希一致；缺失则保持 draft，不导出 PDF。
- **修改源码后忘记 Wheel/lock：** 重建 Wheel、更新锁定哈希并重跑相关验证；源码与运行时不一致时不能发布。
- **使用历史输出证明当前状态：** 重新生成临时输出并保留当前命令、哈希和审查记录。
- **直接修改治理报告消警：** 修复源合同并重新生成，或保留真实 warning/no-data。
- **删除历史 PDF 或视觉资产：** 默认保留；只有用户明确批准才按准确绝对路径清理。

## 14. 接手检查清单

开始维护前：

- [ ] 确认工作目录和远端。
- [ ] 运行 `git status --short --branch` 并保留已有改动。
- [ ] 阅读第 3 节权威文件。
- [ ] 明确本次目标、成功标准、影响范围和回滚边界。
- [ ] 区分“修复 Skill/运行时”和“生成某本手册”。

交付给下一位维护者前：

- [ ] 确认只有 `skills/exam-revision-handbook/SKILL.md` 是权威入口，且包内无向上路径依赖。
- [ ] 说明变更/删除文件和未触及边界。
- [ ] 报告准确验证结果与未运行项目。
- [ ] 涉及发布时完成打包、反向安装、治理和 GitHub 复核。
- [ ] 涉及具体手册时使用 `candidate`、`draft`、`final-ready` 或 `certified` 的准确状态。

## 15. 快速定位

| 事项 | 首先查看 |
| --- | --- |
| 生成新手册 | `skills/exam-revision-handbook/SKILL.md`、`skills/exam-revision-handbook/references/workflow-contract.md` |
| 工作流/Agent 行为 | `PROJECT.md` 第 7 节、`skills/exam-revision-handbook/references/workflow-contract.md` |
| 产物、审查、PDF | `skills/exam-revision-handbook/references/revision_guide_spec.md`、`docs/ACCURACY_POLICY.md` |
| 运行时/Wheel/CLI | `skills/exam-revision-handbook/references/runtime-contract.md`、`skills/exam-revision-handbook/assets/runtime/runtime-lock.json` |
| 打包/Release | `docs/PROJECT_OPERATIONS.md`、`docs/RELEASE_CHECKLIST.md` |
| 路线可交付性 | `tests/fixtures/delivery_matrix.json` 和该手册自己的证据 |
| 治理 warning | `skills/exam-revision-handbook/reports/review-studio.json`，随后运行对应生成器 |
| 版本/历史 | `PROJECT.md`、`skills/exam-revision-handbook/manifest.json`、`CHANGELOG.md`、Git 标签和 Release |

---

本文件包含 2026-08-13 的历史交接快照和 2026-09-06 的当前任务快照。接手者在实际修改、发布或对外说明前，应重新核查 `git status`、当前提交、`skills/exam-revision-handbook/manifest.json`、运行时健康状态和 GitHub Release/CI 状态。

---

## 2026-09-06 本次任务快照

### A. 任务边界与当前课程身份

本次任务要求为 **AQA International AS Physics，2027，中文支持，formal，multi-agent**，并指定 `image-gen-flow` 的 SenseNova 路线。项目的 `AQA International` 口语请求按 Provider 路由解析为 **OxfordAQA International AS Physics**；它不是英国本土 AQA `7407`：

- 学科登记代码：`9631`（OxfordAQA International Advanced Subsidiary Physics）。
- 规格族编号：`9630`（OxfordAQA International AS and A-level Physics）。`9631` 与 `9630` 不应混为同一个登记代码。
- 课程市场：`international`；选择年份：`2027`；规格版本：`Version 5.1`。
- 官方课程页面：`https://www.oxfordaqa.com/qualifications/international-as-a-level-physics/`。
- 官方规格 PDF：`https://www.oxfordaqa.com/wp-content/uploads/2022/08/oxfordaqa-a-level-physics-specification.pdf`。

当前官方来源、资格代码和 2027 timetable 已核对。不要把该路线改写为英国本土 AQA `7407`，也不要把桌面中文文件误称为仓库 Skill 的正式交付。

### B. 官方规格证据

- 本地规格文件：`LOCAL_PATH\source\oxfordaqa-2022-specification.pdf`。
- SHA-256：`9e2ab37a44dfcad9f621642d1e28caf43721a8ca7723557f578d38ac2ae80aca`。
- 提取 Markdown：`LOCAL_PATH\source\specification.md`；其当前文件哈希为 `b28bb3162d82c279f3fc33ba4d09b8068ff9dc15137d29c3cc11d85a6565c022`。该值是提取文本文件哈希，不替代官方 PDF 哈希。

### C. 桌面输出与已有产物

当前输出目录为：`LOCAL_PATH`。

已存在的主要产物包括：

- `qualification.json`、`syllabus-evidence.json`、`syllabus-outline.json`、`guide-plan.json`、`run-options.json`。
- `concepts/concept_jobs.json`、`concepts/concept_explanations.json`、`concepts/concept_explanations-merged.json`，当前验证摘要记录 33 个主题概念条目已导入。
- 原 canonical run 的当前 HTML：`oxfordaqa-as-a-level-physics-20260906-2038.html`。
- 当前渲染指针：`current-render.json`，HTML SHA-256 为 `1299f2f0ebc6151ed924bdb3cdeeb382bfbe359f7713c018b25d3c5736f52cbe`。
- `validation.json`、`final-review-packet.json`、`delivery-contract.json`、`quality-inspection.json` 及渲染快照目录。
- `images/visual_manifest.json`、`images/infographic_jobs.json`、SenseNova 预检/队列文件、响应文件和视觉候选目录。
- 独立桌面交付 manifest：`LOCAL_PATH\desktop-delivery-manifest.json`；仓库副本为 `reports/as-physics-desktop-delivery-manifest.json`，记录文件、官方来源、视口检查和 SHA-256。

截至原 canonical run 的 21:13，尚无可作为 Skill 正式交付的 PDF、`current-pdf.json` 或 `current-delivery.json`。随后独立桌面中文链在 21:41–21:42 生成了 HTML/Markdown/PDF，但这些文件不属于 canonical current 指针，也未获完整 LLM HTML 审查批准。

### D. 当前阻塞与证据状态

1. **Canonical 旧验证仍阻塞：** 原 canonical `validation.json` 记录 `35` 个 error、`33` 个 warning，`delivery_status=blocked_errors`，`delivery_state=blocked`。工作树中的 Analyst 已修复官方结构容器与教学标题分离逻辑，但尚未重建桌面 JSON，因此该验证文件仍是旧状态；这些诊断不能靠手改报告消除。
2. **主题命名与颗粒度：** 旧验证中 33 个主题沿用官方结构标题并触发 “reuses a declared structure title while covering multiple source items”。可教学标题已落地；`source_container_title` 追溯字段仍属待办（Topic 模型与序列化尚未携带该字段），重建时应同步 `qualification.json`、`syllabus-outline.json`、`guide-plan.json`、概念解释和视觉 manifest。
3. **HTML 尚未完成 LLM 可见审查：** `final-review-packet.json` 的 `llm_review_complete=false`，`pdf_export_allowed=false`。必须打开并完整检查当前 HTML，必要时修复、重新渲染并重新审查。
4. **视觉审批未闭环：** manifest 有 17 个视觉条目，14 个 SVG、3 个栅格资产；资产层记录为 `reviewed-generated`，但 17 个条目的 `visual_need.reviewer_visual_decision` 仍为 `pending`，因此不能视为交付批准。视觉资产哈希、topic 绑定和当前 HTML 必须继续保持一致。
5. **SenseNova 证据不完整：** `pending-sensenova-visuals-preflight.json` 和 `pending-sensenova-visuals-queue.json` 记录 `provider_call_made=false`、`execution_state=not_started_no_provider_call`。已有响应文件仅提供 `ok=true` 级别信息，不能替代可审计的真实调用回执；不得据此宣称所有 SenseNova 视觉已生成并批准。
6. **中文正文存在合同冲突：** 当前 `run-options.json` 使用 `output_language=zh-CN`，但项目合同将其定义为中文术语表支持语言；标准路径仍生成英文考试正文，并要求 30–50 条中文专业术语表。`src/intl_exam_guide/planning/language_policy.py`、`src/intl_exam_guide/planning/guide_plan.py` 和 `src/intl_exam_guide/validation/checks.py` 会阻止未经合同变更的中文学生正文。若保持现有合同，应交付英文正文加中文术语表；若确需中文正文，必须同步语言策略、生成器、渲染器、校验器、Writer 合并器、合同、测试、README 和 CHANGELOG，不能只删除一条校验。

### E. 下一步建议

1. 重建 canonical `syllabus-outline.json`、`guide-plan.json` 和后续绑定，使 Analyst 的教学标题修复真正进入桌面运行目录。
2. 明确中文交付边界：现有桌面文件是独立中文正文；canonical Skill 仍是英文考试正文加中文术语表，不能把两条链混称。
3. 由 Analyst 重新完成最低官方容器审计、原子 `source_coverage` 和可教学主题命名；由 Writer 重新生成概念解释、`mastery_summary`、worked examples 和每主题 `visual_decision`。
4. 在视觉决策导入后刷新 manifest，再生成或导入 SenseNova/Kroki/SVG 资产；逐项绑定哈希并记录 LLM 视觉审批。不要把旧 manifest 中的 pending 决策直接提升为批准。
5. 重新渲染 HTML，完成 33 个主题（或新 AQA 主题数）的全量可见审查，写入 `review-ledger`、`agent-product-review.json`，然后运行只读交付审计。
6. 只有当前 HTML、视觉状态、审查账本和交付审计全部通过后，才允许导出 canonical PDF；桌面中文 PDF 的存在不解除这些门禁。

## 2026-09-06 本次任务快照：OxfordAQA International AS Physics 2027

### 任务身份与用户修正

- 用户最初提出 AS Physics 学习指南，随后明确要求：中文、formal、multi-agent、使用 `image-gen-flow` 的 SenseNova 通道；最终把路线修正为 **AQA International、2027**。
- 项目官方 Provider 解析将该请求落到 **OxfordAQA International AS and A-level Physics**，资格族代码 `9630`，AS 报名代码 `9631`，而不是英国本土 AQA 7407。当前 AS 两个考试单元为 `PH01` 和 `PH02`。
- 当前官方规格 PDF 位于 `LOCAL_PATH\source\oxfordaqa-2022-specification.pdf`，SHA-256 为 `9e2ab37a44dfcad9f621642d1e28caf43721a8ca7723557f578d38ac2ae80aca`，规格版本为 5.1，内容范围为 2027 适用的 AS 3.1-3.5。
- 桌面输出同时保留了 2027 timetable 证据文件：`source/oxfordaqa-january-2027-timetable.pdf`、`source/oxfordaqa-may-june-2027-timetable.pdf` 和 `source/exam-timetables-2027.json`。已核到 PH01 为 2027-04-26、PH02 为 2027-05-04；最终考试安排仍以考试局通知为准。

### 当前已生成的桌面交付物

- 中文正式版 HTML：`LOCAL_PATH\AS_Physics_学习指南_AQA_International_2027.html`
- 中文 Markdown：`LOCAL_PATH\AS_Physics_学习指南_AQA_International_2027.md`
- 中文 PDF：`LOCAL_PATH\AS_Physics_学习指南_AQA_International_2027.pdf`
- 桌面渲染快照：`render-snapshots/chinese-guide-desktop.png`、`render-snapshots/chinese-guide-mobile.png`
- 中文指南包含 33 个 AS 主题、Unit 1/Unit 2 考试地图、公式提示、例题思路、易错点、规格页码和考前检查清单。

### 交付验证事实

- 中文 HTML 已通过 UTF-8 读回检查，包含 33 个主题和 17 个图像引用。
- Playwright 渲染结果：桌面视口 `1440×900`，`scrollWidth=clientWidth=1440`；17 个图像全部加载，`broken_images=0`。
- 移动视口 `390×844` 已渲染并保存快照。此前记录的 `scrollWidth=459` 横向溢出已通过断词样式修复；本次复核再次得到 `document` 与 `body` 的 `scrollWidth=390`、`clientWidth=390`，17 个图像均加载成功（`broken_images=0`）。这不能替代 canonical 的完整 LLM HTML 审查。
- PDF 已生成，当前大小约 13.7 MB。尚未把该 PDF 写入 Skill 的 `current-pdf.json` 或正式 delivery 指针；它是用户桌面学习指南交付物，不应被描述为仓库 Skill 的 `final-ready`。

### 视觉资产状态

- 当前已有 17 个视觉资产，其中 SVG 与 PNG 均写入桌面 HTML；`visual_017_emf.png` 已通过 SenseNova 语义复核。
- `visual_015_circuits.png` 的 SenseNova 候选 v2 自检通过，但人工语义复核仍发现“cells in series”拓扑不清晰；没有将候选 v2 覆盖旧图，也没有把它宣称为最终教学图。最终指南中电路主题同时提供文字、公式和易错点，避免依赖有歧义的图。
- 不要根据模型自检 PASS 代替人工语义审查；若再次处理该图，必须保持 SenseNova 通道、`watermark:false` 和当前 visual semantic contract。

### 仓库 Skill 与桌面交付的边界

- 仓库当前正式 Skill 合同仍是：`zh-CN` 表示英文考试正文 + 中文专业术语表。该合同位于 `references/workflow-contract.md`、`references/revision_guide_spec.md`、语言策略、校验器和合并脚本中。
- 本次用户明确要求中文正文，因此新增了一个桌面交付脚本和独立中文 HTML/PDF/Markdown；没有局部删除仓库 CJK 校验器，也没有伪装成 canonical Skill 的中文模式。
- 若将中文正文正式纳入 canonical Skill，必须同步语言策略、guide plan、渲染器、校验器、Writer 合并器、测试、合同、README、CHANGELOG，并重建内嵌 Wheel 与 runtime lock；当前未做这项大范围契约变更。

### 当前仍未闭环的仓库级阻塞项

- 原 OxfordAQA canonical 运行链的 `validation.json` 仍有英文正文/CJK、Analyst 粒度、qualification-source mismatch 等阻塞；它不是本次独立中文桌面 PDF 的批准记录。
- 原有 17 个 visual manifest 条目的 `reviewer_visual_decision` 仍有 pending，当前不能生成 canonical Skill 的 `agent-product-review.json`、current-pdf 或 delivery 指针。
- `review-ledger/` 和完整的 LLM HTML 审查记录尚未完成；机器诊断、截图和 PDF 存在不等于 canonical Skill 的最终批准。
- 移动端中文桌面指南的横向溢出已修复；仍需保持最新截图与桌面交付 manifest 一致。

### 后续接手建议

1. 用仓库内脚本/流程重建 `syllabus-outline.json`、`guide-plan.json` 和后续绑定，使 Analyst 的教学标题真正进入桌面运行目录。
2. 对所有 17 个实际渲染视觉逐项写入明确的 LLM review ledger；对于电路图，不要把有歧义的 SenseNova 候选当作通过。
3. 完成当前 HTML 的桌面与移动全量可见审查后，才考虑 `agent-product-review.json`、PDF 门禁和 delivery 指针。
4. 若继续维护本次中文桌面指南，保持桌面/移动渲染检查与交付 manifest 一致；不要把该独立 PDF 升级为 canonical Skill current-pdf。
5. 不要 push、tag 或创建 Release，除非用户明确授权。

### F. 2026-09-06 23:10 后续刷新

本次继续任务只处理独立桌面中文指南的机械证据同步，没有推进 canonical Skill 的
视觉导入、LLM HTML 审查或 PDF 正式交付门禁。

- 已将桌面 manifest 与仓库副本 `reports/as-physics-desktop-delivery-manifest.json`
  的 5 个产物哈希和文件大小刷新为当前磁盘值，并确认两份 manifest 逐字段一致。
- 当前桌面产物证据为：HTML 54,167 bytes，SHA-256
  `8bddae8e81c0987597d40c4946cee5b26e9dda829e390143e0fdef6a4ac5cf8f`；Markdown
  26,574 bytes，SHA-256
  `9a64b56b100514e6fe03a479dd468f0b6e5516fe8808ebb7a26183cf72d736c4`；PDF
  13,618,932 bytes，SHA-256
  `bd7b78d90c44d73baf5780e896331cfa3790cf5f3503fae20201b04e493dd401`；桌面快照
  `e3f2fa4c447ab189dd159cb97844e30b44b9e79d16b24441480216d8bd3a6b94`；移动快照
  `06e1e48ed6f88fc8ec93f0eade2637e01a8e3419857279b968724a56fead15b1`。
- manifest 的 `canonical_skill_boundary.validation_errors` / `validation_warnings`
  现与桌面 `validation.json` 的实际 issue severity 对齐为 `35` / `33`；该文件的
  `delivery_status=blocked_errors`、`delivery_state=blocked`，PDF gate 仍为
  `pending_current_html_review`。这组数字不是“通过”计数。
- 另一次最新 `audit-delivery` 只读审计汇总为 `53 blockers`、`34 warnings`；它与
  桌面旧运行目录的 `validation.json`（35 errors、33 warnings）属于不同审计层，不能
  混写或互相替代。若继续推进 canonical 链，应重新生成当前运行目录证据后再更新任何
  交付摘要。
- 桌面 manifest 仍明确保持 `generated_not_canonical_final`，canonical 状态为
  `blocked`；`full_llm_html_review=false`、`current_pdf_pointer=false`、
  `current_delivery_pointer=false`、`visual_review_pending=17`。`visual_015` 仍因
  串联/并联电池拓扑、极性和连接路径语义不清而阻塞。
- 当前 `current-render.json` 仍指向 canonical 英文 HTML，而不是桌面中文 HTML；桌面
  中文 PDF 不得写入 `current-pdf.json` 或 `current-delivery.json`。

本次刷新后应执行的定向检查：`python -m ruff check
scripts/create_chinese_as_physics_handbook.py`、`python -m compileall -q scripts`
和 `git diff --check`。不要运行会覆盖桌面 JSON 或渲染证据的 canonical 重建命令，除非明确重新启动 canonical 运行链。

执行结果：`skills/exam-revision-handbook/scripts/doctor.py` 通过；
`tests/test_concept_jobs.py` 与 `tests/test_import_concept_full_body.py` 在项目内隔离
临时目录下共 `7 passed`；两个相关脚本的 Ruff 检查、`python -m compileall -q scripts`
以及 `git diff --check` 均通过。系统默认 pytest 临时目录存在 Windows 权限错误，未将该
环境问题误判为测试失败；隔离运行已覆盖同一测试集合。

### G. 2026-09-07 响应式布局修复与桌面证据刷新

本次只维护独立桌面中文指南，不推进 canonical Skill 的视觉审批、LLM HTML 审查或正式 PDF 门禁。

- 将桌面中文 HTML 的响应式断点扩大到 `820px`：`390x844` 和 `768x1024` 使用单列元信息、主题内容和目录，`1440x900` 保持双列目录。
- Playwright 三视口复核均无横向溢出：`390x844`、`768x1024`、`1440x900` 的 `scrollWidth=clientWidth`，17 个图像引用全部加载，`broken_images=0`，主题数为 33；目录列数为 `1/1/2`。
- 当前 HTML 为 54,527 bytes，SHA-256 为 `27ab40d80038968ac51edf273aeb081cd2c5d1f7df504b1cb0cab80bc5205db9`。桌面、平板、手机全页快照分别为 `e3f2fa4c447ab189dd159cb97844e30b44b9e79d16b24441480216d8bd3a6b94`、`c763569aa16b53fde9d80b35e1fbd0f8587331df14583b19c8905e86b992338e`、`7ac6f9b41df9636d81c942e42741fe78d88837a2744f56c632b19aaa90e5e1c4`。
- 已同步桌面目录与仓库 `reports/as-physics-desktop-delivery-manifest.json`；两份 JSON 逐字段一致，实际文件 SHA-256 与大小逐项匹配。manifest 现在包含平板全页、三视口检查、顶部截图及渲染证据。
- 现有 PDF 仍为 2026-09-06 生成的 13,618,932-byte 文件，SHA-256 为 `bd7b78d90c44d73baf5780e896331cfa3790cf5f3503fae20201b04e493dd401`；它绑定的是布局修复前 HTML `8bddae8e81c0987597d40c4946cee5b26e9dda829e390143e0fdef6a4ac5cf8f`，因此 manifest 标为 `stale_unbound_to_current_html`，没有写入 `current-pdf.json` 或 `current-delivery.json`。

### H. 2026-09-07 视觉策略运行时封装与安装验证

本轮继续任务完成了视觉策略的运行时封装闭环。源码、两处嵌入 Wheel、运行时锁和安装包均以当前工作树为准；没有创建提交、推送、tag 或新的 GitHub Release。

- 两处 `assets/runtime/` 中的 `exam_revision_handbook-0.7.4-py3-none-any.whl` 完全一致，大小为 `273,393` bytes，SHA-256 为 `a86d205c8c194860e52045cf0270a30961d5fbd2d3ff6d630ccc039f3455773e`；两份 `runtime-lock.json` 均锁定该值。
- `reports/wheel-payload-parity.json` 当前为 `77/77`，没有缺失、额外或变更载荷；根目录与 Skill 包内 `doctor.py --deep` 均通过。
- `dist/exam-revision-handbook-v0.7.4.zip` 已按当前包重建，包含 `112` files，大小 `542,832` bytes，SHA-256 为 `6fc360535ecdcaec3da21e14cae4c361716f572037a31a5f9181591278d8cb30`；对应 `.sha256` 文件已同步。
- 反向安装到独立临时目录后，bootstrap、doctor、根 CLI、9 个子命令的 `help`、两个导入 helper 的 `help` 均以 exit code `0` 完成。第一次未 bootstrap 时出现预期的 `bootstrap-required`，随后 bootstrap 后验证通过。
- 视觉策略相关定向测试 `48 passed`、完整回归 `511 passed, 163 skipped`，以及 Ruff、compileall、mypy、raw-key scan、治理报告规范化、Wheel parity、打包和反向安装均已完成。默认 Windows pytest 临时目录仍有缓存写入权限 warning；测试使用项目外可写 `--basetemp`，不是断言失败。

本轮新增的运行时策略是强制每个 topic 记录 `visual_decision` 与 topic-specific `visual_guidance`；有已验证外部图像路线时，复杂信息图、装置、场景、建模和丰富标注优先走 `external-infographic`，`exact-svg`/`kroki-diagram` 只保留给精确几何、符号或正式结构例外。`visual_policy_enforced` 仍兼容旧序列化字段，但运行时会固定为 `true`，不能重新打开已废弃的旁路。桌面中文物理手册仍是独立历史/用户交付证据，不会被此运行时更新自动升级为 canonical `final-ready`。
