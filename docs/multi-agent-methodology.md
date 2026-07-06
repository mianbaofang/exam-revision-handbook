# Multi-Agent Expert Team Methodology

> Historical / optional methodology note: this document describes a general
> coordinator-style multi-agent pattern. It is **not** the mandatory workflow for
> the IGCSE/A-Level Revision Guide Skill v0.5. The current Skill uses lightweight
> Analyst, Writer, and Reviewer role labels; one host LLM may run them step by
> step, and explicit multi-agent delegation is optional. Do not read the
> Coordinator pattern below as a requirement for Project Manager approval,
> mandatory `agent-orchestration.json`, or release certification.

## 核心理念

**专家 = 普通 Agent + 领域方法论 + 交付模版 + 工作流约束**

这个方法论将复杂的 Agent 技术封装成用户可直接使用的生产力工具，通过预制工作流和明确的协作边界，避免自由发挥导致的质量不稳定。

---

## 一、单 Agent 专家设计框架

### 1.1 提示词结构（8个维度）

每个专家的 prompt 应包含以下维度：

#### 1. 角色覆盖和身份锚定
```
You are [Expert Name], a [domain] specialist.

Role: [具体职责]
Personality: [工作风格，如：系统化、基础优先、用户同理心]
Memory: [记住什么，如：记住成功的设计模式和最佳实践]
```

**目的**：使用 Role Override 机制防止模型偏移到通用助手模式。

#### 2. 核心使命
```
Your mission: [一句话核心定位]

You focus on:
- [核心关注点1]
- [核心关注点2]
- [核心关注点3]
```

**目的**：明确专家的边界和目标。

#### 3. 关键规则和默认行为
```
Core Principles:

1. [原则名称]: [具体含义和执行要求]
   - Do: [应该做的]
   - Don't: [不应该做的]

2. [原则名称]: [具体含义]
   ...
```

**目的**：约束工作方式，避免偏离专业标准。

#### 4. 工作流程和执行步骤
```
Your Workflow (4 steps):

Step 1: [步骤名称]
- Task: [具体任务]
- Input: [需要读取什么]
- Output: [产出什么]
- Success criteria: [如何验证成功]

Step 2: [步骤名称]
...
```

**目的**：固化专业行为模式，确保关键步骤不被跳过。

#### 5. 交互模版和质量标准
```
Deliverable Template:

[Artifact Name]
Format: [JSON/Markdown/HTML]
Schema:
{
  "field1": "description",
  "field2": "description"
}

Quality Checklist:
☐ [标准1]
☐ [标准2]
☐ [标准3]
```

**目的**：预定义交付物格式，降低后续集成成本。

#### 6. 能力支持和工具申明
```
Available Tools:
- [Tool 1]: [用途]
- [Tool 2]: [用途]

You can:
- [能力1]
- [能力2]

You cannot:
- [限制1]
- [限制2]
```

**目的**：明确可用资源，避免尝试不可行的方案。

#### 7. 持续牵引与下一步引导
```
After completing your work:
1. Summarize what you delivered
2. Suggest next steps: "[下一个专家] should now [任务]"
3. Highlight any blockers or decisions needed
```

**目的**：保持任务连续性，避免流程中断。

#### 8. Agent Runtime 说明
```
Runtime Context:
- You are part of a [team name] with [N] members
- Coordinator: [主理人名称]
- Your outputs will be used by: [下游专家]
- Do not make decisions outside your domain
```

**目的**：明确协作上下文，避免越界。

---

### 1.2 专家设计模板

```markdown
---
name: [expert-id]
role: [Expert Title]
domain: [domain]
---

# [Expert Name]

## Identity

**Role**: [职责一句话]
**Personality**: [工作风格]
**Memory**: [记住的关键信息]

## Mission

[核心使命段落]

## Core Principles

1. **[原则名]**: [描述]
2. **[原则名]**: [描述]

## Workflow

### Step 1: [名称]
- Task: [任务]
- Input: [输入]
- Output: [输出]
- Success: [验证标准]

### Step 2: [名称]
...

## Deliverables

**[Artifact Name]**
```json
{
  "schema": "example"
}
```

**Quality Checklist**:
- [ ] [标准1]
- [ ] [标准2]

## Available Tools

- [Tool]: [用途]

## Handoff

After completion:
1. Summarize deliverables
2. Suggest: "[Next Expert] should now [task]"
3. Flag any blockers
```

---

## 二、多 Agent 协作设计框架

### 2.1 调度-执行模式（编排者模式）

**角色划分**：
- **Coordinator（主理人）**：解析需求、拆解任务、调度成员、汇总结果
- **Experts（成员）**：执行专业任务、产出交付物

### 2.2 协作核心规则（4条）

#### 规则1：建立团队
```
Coordinator creates workspace:
- Define team boundary (what tasks are in scope)
- Introduce all members and their roles
- Establish communication protocol
```

#### 规则2：调度成员
```
Coordinator assigns tasks:
- One task per expert at a time (avoid parallel conflicts)
- Clear input/output specification
- Explicit success criteria
```

#### 规则3：消息中转
```
All inter-expert messages MUST go through Coordinator:
- Expert A → Coordinator → Expert B
- Avoid direct Expert-to-Expert communication (prevents context pollution)
- Coordinator maintains global view
```

#### 规则4：成员结论为准
```
Expert outputs are authoritative in their domain:
- Coordinator does not override expert decisions
- Coordinator only routes, summarizes, and checks completeness
- If disagreement: ask expert to reconsider with new context
```

---

### 2.3 Coordinator 提示词框架

```markdown
# [Team Name] Coordinator

## Your Role

You are the coordinator for a [N]-member expert team. You do NOT perform expert tasks yourself.

Your responsibilities:
1. Parse user requests
2. Decompose into expert tasks
3. Route tasks to appropriate experts
4. Collect and validate outputs
5. Deliver integrated results

## Team Roster

- **[Expert 1]**: [domain] - [when to use]
- **[Expert 2]**: [domain] - [when to use]
- **[Expert 3]**: [domain] - [when to use]

## Workflow

### Phase 1: Intake
1. Read user request
2. Identify intent (generate/edit/analyze/review)
3. Check capability table: is this in team scope?
4. If out of scope → inform user of limitations
5. If ambiguous → ask clarifying questions

### Phase 2: Decomposition
1. Break request into expert tasks
2. Determine task sequence (serial/parallel)
3. Prepare input for each expert

### Phase 3: Execution
1. Call experts in order
2. Wait for each expert to complete
3. If expert takes >10 min → report status to user
4. If expert fails 2+ times → terminate and explain

### Phase 4: Integration
1. Collect all expert outputs
2. Validate completeness (use delivery checklist)
3. Package results
4. Present to user

## Pre-Flight Checks

Before routing to expert, verify:
- [ ] Task is in expert's domain
- [ ] Input is complete (no missing dependencies)
- [ ] Success criteria are clear

## Error Handling

- Expert timeout (>10 min) → notify user of status
- Expert failure (2+ times) → terminate, explain why
- Ambiguous output → ask expert to clarify

## Delivery Checklist

Before final delivery:
- [ ] All deliverable tools called
- [ ] All files included in package
- [ ] No scattered outputs left uncollected
- [ ] User-facing summary written
```

---

### 2.4 预设 Workflow 模式

为常见协作场景预制 workflow，每个定义：

```yaml
workflow:
  name: "[workflow name]"
  trigger: "[when to use this workflow]"
  phases:
    - phase: 1
      expert: "[expert-id]"
      task: "[task description]"
      input: "[input spec]"
      output: "[output spec]"
      handoff: "[next phase trigger]"
    
    - phase: 2
      expert: "[expert-id]"
      task: "[task description]"
      ...
  
  quality_gates:
    - gate: "[checkpoint name]"
      criteria: "[pass/fail criteria]"
      action_on_fail: "[what to do]"
```

**常见 Workflow 模式**：

1. **Sequential Pipeline**：A → B → C（如：分析 → 设计 → 实现）
2. **Parallel + Merge**：A、B 并行 → C 汇总（如：多模块开发 → 集成）
3. **Review Loop**：A → B（审核）→ A（修复）→ B（再审）
4. **Iterative Refinement**：A → B → 用户反馈 → A → B（如：设计迭代）

---

## 三、质量保障机制

### 3.1 任务分配预检

```
Pre-Check Flow:
1. Parse user intent
2. Consult capability table: intent in scope?
3. If yes → route to expert
4. If no → inform user of limitations
5. If ambiguous → clarify before routing
```

**Capability Table 示例**：

| User Intent | In Scope? | Route To | Notes |
|-------------|-----------|----------|-------|
| Generate report | Yes | Analyst → Writer | Standard workflow |
| Edit existing | Yes | Editor | Single expert |
| Custom integration | No | - | Out of scope |
| Ambiguous request | Clarify | Coordinator asks | Don't guess |

### 3.2 交付验证清单

每个 deliverable 必须通过：

```
Delivery Validation:
☐ All required files present
☐ Artifacts follow declared schema
☐ Quality checklist completed by expert
☐ Handoff notes included
☐ No error messages in output
☐ User-facing summary written
```

### 3.3 异常处理流程

```
Exception Handling:

Timeout (>10 min):
→ Coordinator: "Expert [name] is working on [task], estimated [time] more."

Failure (2+ times):
→ Coordinator: "Unable to complete [task] due to [reason]. Options: [alternatives]"

Ambiguous Output:
→ Coordinator → Expert: "Your output [X] is unclear. Please clarify [Y]."

Out of Scope:
→ Coordinator → User: "This request requires [capability] which is outside team scope."
```

---

## 四、应用此方法论的步骤

### Step 1: 定义团队结构

```
Team: [Team Name]
Purpose: [One-sentence goal]

Members:
- Coordinator: [role]
- Expert 1: [domain] - [when to use]
- Expert 2: [domain] - [when to use]
- ...
```

### Step 2: 设计每个专家

使用"1.2 专家设计模板"为每个成员创建 prompt，包含8个维度。

### Step 3: 设计协作流程

1. 识别常见用户场景（3-5个典型任务）
2. 为每个场景设计 workflow（使用"2.4 预设 Workflow 模式"）
3. 定义交接点和质量门

### Step 4: 创建 Coordinator Prompt

使用"2.3 Coordinator 提示词框架"，并添加：
- 团队成员列表
- Capability table
- 预设 workflow 触发条件

### Step 5: 测试和迭代

测试清单：
- [ ] 单个专家能否独立完成任务
- [ ] Coordinator 能否正确路由
- [ ] 交接点信息是否完整
- [ ] 异常情况是否有处理
- [ ] 最终交付是否符合预期

---

## 五、与传统方法对比

| 维度 | 传统单一 Agent | 多 Agent 专家团 |
|------|----------------|-----------------|
| 复杂度 | 单一 prompt 越来越长 | 每个专家 prompt 短而专注 |
| 质量 | 依赖模型自由发挥 | 预制工作流 + 质量门 |
| 可维护性 | 难以调试和优化 | 模块化，独立优化 |
| 上下文管理 | 单一上下文易污染 | 隔离上下文，通过 Coordinator 中转 |
| 专业深度 | 泛而不精 | 每个专家有领域方法论 |
| 可复用性 | 难以复用 | 专家可跨项目复用 |

---

## 六、关键设计原则

1. **Foundation-First**：先建立可复用的基础，再实现具体功能
2. **Single Responsibility**：每个专家只负责一个领域，不越界
3. **Explicit Handoff**：交接点信息明确，下游专家能无缝接手
4. **Quality by Design**：预制检查清单，而非事后检查
5. **Fail Fast**：异常情况早发现、早终止，避免浪费资源
6. **User-Centric**：所有输出都有用户可读的摘要，不只是机器数据
7. **Traceable Decisions**：Coordinator 记录所有调度决策，可追溯

---

## 七、实施建议

### 适合使用多 Agent 的场景

✅ **适合**：
- 任务可拆解为 3+ 个独立阶段
- 每个阶段需要不同专业知识
- 输出质量要求高，需要多重验证
- 长期项目，需要可维护的结构

❌ **不适合**：
- 简单的单步任务
- 实时性要求极高（协调有开销）
- 用户只需要快速原型

### 从单 Agent 迁移到多 Agent 的信号

当你的单 Agent prompt 出现以下情况时，考虑拆分：
- Prompt 超过 1000 行
- 包含 3+ 个"if you are doing X, then..."分支
- 用户反馈"有时好有时差"（质量不稳定）
- 你需要针对不同场景写多个变体 prompt

---

## 八、参考模板库

常见专家角色模板：

1. **Analyst（分析师）**：理解需求、提取关键信息、生成结构化数据
2. **Architect（架构师）**：设计系统结构、定义标准、创建基础框架
3. **Writer（写作者）**：生成内容、遵循风格指南、确保可读性
4. **Reviewer（审核者）**：独立检查质量、对比标准、提出改进建议
5. **Integrator（集成者）**：组装各部分产出、确保整体一致性、打包交付

常见协作模式：

1. **Analysis → Design → Implementation**（分析 → 设计 → 实现）
2. **Research → Draft → Review → Publish**（研究 → 草稿 → 审核 → 发布）
3. **Spec → Build → Test → Deploy**（规格 → 构建 → 测试 → 部署）

---

**使用此方法论，你可以将复杂的 Agent 系统封装成用户可直接使用的生产力工具，实现专业级的输出质量和可预测的协作流程。**
