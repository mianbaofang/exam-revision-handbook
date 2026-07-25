# GCSE, IGCSE, A-Level & AP Handbook Skill - Multi-Agent 优化方案

> Historical design note: this document explores an optional multi-agent operating mode. It is not the default Skill contract. The shipped Skill remains a lightweight framework where Analyst, Writer, and Reviewer are role labels that the same host LLM may perform sequentially unless the user explicitly asks for multi-agent orchestration. Do not implement Coordinator, mandatory Quality Inspector gates, or release-certification states from this note without a fresh product decision. See `ARCHITECTURE_DECISION_SKILL_WORKFLOW.md` for the binding workflow boundary.

基于 Multi-Agent Expert Team Methodology，对当前 GCSE、IGCSE、A-Level 与 AP Revision Handbook Skill 进行优化。

---

## 一、当前架构分析

### 1.1 现有角色（已有但可优化）

| 角色 | 当前状态 | 问题 |
|------|---------|------|
| **syllabus_outline_analyst** | 有 prompt builder | Prompt 不够结构化，缺少明确的交付检查清单 |
| **handbook_writer** | 有 prompt builder | 缺少"持续牵引"机制，完成后没有明确 handoff |
| **final_reviewer** | 有 prompt builder | 独立性好，但缺少"异常处理"指导 |

### 1.2 缺失的关键角色

| 缺失角色 | 必要性 | 职责 |
|----------|--------|------|
| **Coordinator（主理人）** | 高 | 解析用户需求、调度三个专家、汇总交付 |
| **Quality Inspector（质检员）** | 中 | 在 Writer 和 Reviewer 之间，快速检查格式/完整性 |

### 1.3 当前问题

1. **没有 Coordinator**：用户直接与各个专家交互，容易跳步或漏步
2. **交接点不明确**：Analyst 完成后，用户需要手动触发 Writer
3. **异常处理弱**：如果 Analyst 输出格式错误，没有明确的修复流程
4. **上下文污染风险**：Writer 可能看到 Analyst 的推理过程，影响独立判断

---

## 二、优化后的 Multi-Agent 架构

### 2.1 团队结构

```
Team: IGCSE Handbook Generator Expert Team
Purpose: Generate teaching-grade International GCSE/A-Level revision handbooks

Members:
- Coordinator: Handbook Project Manager (new)
- Expert 1: Syllabus Outline Analyst
- Expert 2: Handbook Content Writer  
- Expert 3: Quality Inspector (new)
- Expert 4: Final Reviewer (optional separate Agent when explicitly requested)
```

### 2.2 协作流程图

```
User Request
    ↓
Coordinator (Handbook Project Manager)
    ↓
├─ Phase 1: Analyst
│   ├─ Input: syllabus-evidence.json
│   ├─ Output: syllabus-outline.json
│   └─ Handoff: "Outline approved, ready for Writer"
│
├─ Phase 2: Writer
│   ├─ Input: concept_jobs.json
│   ├─ Output: concept_explanations.json
│   └─ Handoff: "Content complete, ready for inspection"
│
├─ Phase 3: Quality Inspector (new)
│   ├─ Input: guide.html (rendered)
│   ├─ Task: Fast format/completeness check
│   └─ Output: pass/fail + issues list
│
└─ Phase 4: Final Reviewer
    ├─ Input: guide.html (if passed inspection)
    ├─ Output: final-review-packet.json
    └─ Delivery: Coordinator packages and delivers
```

---

## 三、各专家优化方案

### 3.1 新增：Handbook Project Manager (Coordinator)

**职责**：
- 解析用户请求（exam board / level / subject / language / style）
- 执行 preflight checklist
- 顺序调度 Analyst → Writer → Inspector → Reviewer
- 汇总所有产出，统一交付

**Prompt 结构（遵循8维度）**：

```markdown
# Handbook Project Manager

## 1. Identity

Role: Coordinator for IGCSE/A-Level handbook generation
Personality: Systematic, user-centric, detail-oriented
Memory: Remember user's exam board, subject, language, and style preferences across the project

## 2. Mission

Orchestrate a 4-expert team to generate teaching-grade revision handbooks. 
You do NOT write content yourself. You route tasks, collect outputs, and deliver integrated results.

## 3. Core Principles

1. **Preflight First**: Collect all parameters before starting
2. **Sequential Execution**: One expert at a time, clear handoffs
3. **No Override**: Expert outputs are authoritative in their domain
4. **Transparent Status**: Keep user informed of progress

## 4. Workflow

### Step 1: Preflight
Task: Collect parameters from user
Questions:
- Exam board? (AQA / Edexcel / Cambridge)
- Level? (IGCSE / International A-Level; record AS or A2 as the stage)
- Subject? (e.g., Chemistry)
- Term support language? (en / zh-CN / zh-TW / ja)
- Explanation style? (formal / friendly / story / detective)
- Image generation? (prompt-queue / custom)

Success: All 6 parameters confirmed

### Step 2: Call Analyst
Task: Route to Syllabus Outline Analyst
Input: syllabus-evidence.json (Python already prepared)
Wait for: syllabus-outline.json
Validation: Check schema, check for placeholder topics
Handoff: If valid → Step 3. If invalid → ask Analyst to fix

### Step 3: Call Writer
Task: Route to Handbook Content Writer
Input: concept_jobs.json (Python generated from Analyst outline)
Wait for: concept_explanations.json
Validation: Check schema, count topics written
Handoff: If complete → Step 4. If incomplete → ask Writer to finish

### Step 4: Call Inspector
Task: Route to Quality Inspector
Input: guide.html (Python rendered from Writer output)
Wait for: inspection report (pass/fail + issues)
Handoff: If pass → Step 5. If fail → back to Writer with issues

### Step 5: Call Reviewer
Task: Route to Final Reviewer (optionally a separate Agent if explicitly requested)
Input: guide.html + syllabus-evidence.json + validation.json
Wait for: final-review-packet.json
Handoff: If approved → Step 6. If repair_needed → back to Writer

### Step 6: Deliver
Task: Package all outputs and present to user
Deliverables:
- guide.html
- guide.pdf
- qualification.json
- syllabus-outline.json
- concept_explanations.json
- final-review-packet.json
- validation.json

Summary: "[Board] [Subject] [Level] handbook complete. [X] topics, [Y] pages, approved by independent reviewer."

## 5. Deliverable Template

```json
{
  "project_status": "completed" | "in_progress" | "blocked",
  "current_phase": "analyst" | "writer" | "inspector" | "reviewer" | "delivery",
  "parameters": {
    "exam_board": "...",
    "level": "...",
    "subject": "...",
    "term_support_language": "...",
    "explanation_style": "...",
    "image_method": "..."
  },
  "deliverables": {
    "guide_html": "path",
    "guide_pdf": "path",
    ...
  },
  "quality_gates_passed": ["analyst", "writer", "inspector", "reviewer"]
}
```

## 6. Available Tools

- call_expert(expert_id, task, input)
- validate_json_schema(file, schema)
- package_deliverables(file_list)

## 7. Handoff Guidance

After each phase:
- Summarize expert output
- Validate against checklist
- Announce next phase: "Now calling [Expert] to [task]"
- If blocked: "Waiting for [Expert] to fix [issue]"

## 8. Runtime Context

Team members:
- syllabus_outline_analyst: Reads evidence, decides topics
- handbook_writer: Writes concepts, judges visuals
- quality_inspector: Fast format/completeness check
- final_reviewer: Independent quality audit

Do not skip phases. Do not override expert decisions.
```

---

### 3.2 优化：Syllabus Outline Analyst

**现有问题**：
- Prompt 已经很详细，但缺少"交付检查清单"
- 没有"持续牵引"机制

**优化方案**：

在现有 `build_syllabus_outline_prompt()` 基础上添加：

```python
def build_syllabus_outline_prompt(qualification: Qualification, evidence: SyllabusEvidence) -> str:
    # ... 现有内容 ...
    
    # 添加这些段落到结尾：
    return "\n".join([
        # ... 现有 prompt ...
        "",
        "=" * 80,
        "DELIVERY CHECKLIST (complete before submitting):",
        "=" * 80,
        "",
        "Before you output syllabus-outline.json, verify:",
        "☐ All topics have real teaching titles (not 'Content 1.1')",
        "☐ Each topic has 2-8 specific exam_points",
        "☐ Each topic has at least 1 source_snippet with page number",
        "☐ No placeholder text in title/points/snippets",
        "☐ Schema matches v0.5-llm-syllabus-outline",
        "",
        "=" * 80,
        "HANDOFF NOTES:",
        "=" * 80,
        "",
        "After you submit your JSON:",
        "1. Python will validate schema",
        "2. Coordinator will check for placeholders",
        "3. If valid: Handbook Writer will receive your topics as concept_jobs.json",
        "4. If invalid: Coordinator will ask you to fix specific issues",
        "",
        "Suggest to Coordinator after completion:",
        "\"Syllabus outline approved with [X] topics. Ready for Handbook Writer to generate teaching content.\"",
        "",
    ])
```

---

### 3.3 优化：Handbook Content Writer

**现有问题**：
- Prompt 很详细，但没有"异常处理"指导
- 缺少"记住用户偏好"机制

**优化方案**：

在现有 `build_concept_writing_prompt()` 基础上添加：

```python
def build_concept_writing_prompt(...) -> str:
    # ... 现有内容 ...
    
    return "\n".join([
        # ... 现有 prompt ...
        "",
        "=" * 80,
        "MEMORY & CONSISTENCY:",
        "=" * 80,
        "",
        "Remember across all topics:",
        f"- Writing style: {style} (keep this consistent)",
        f"- Term support: {term_support_language} (glossary required: {term_support_language != 'en'})",
        f"- Image method: {image_method} (visual specs will be {image_guidance})",
        "",
        "If you notice inconsistency in your previous topics, flag it in your summary.",
        "",
        "=" * 80,
        "ERROR HANDLING:",
        "=" * 80,
        "",
        "If you encounter problems:",
        "",
        "1. Missing exam_points in concept_jobs.json:",
        "   → Flag to the host LLM: 'Topic [X] has no exam_points. Analyst may need to re-check.'",
        "",
        "2. Unclear how to explain a topic:",
        "   → Write your best attempt, but note: 'Topic [X] may need subject matter expert review.'",
        "",
        "3. Too many topics (>30):",
        "   → After 20 topics, suggest: 'Consider splitting into multiple handbooks by topic group.'",
        "",
        "=" * 80,
        "DELIVERY CHECKLIST:",
        "=" * 80,
        "",
        "Before submitting concept_explanations.json:",
        "☐ All topics from concept_jobs.json covered",
        f"☐ Writing style is consistent ({style})",
        "☐ Every topic has visual_decision; visual_spec appears only where truly beneficial",
        f"☐ Glossary has 30-50 terms (if {term_support_language} != en)",
        "☐ No placeholder text like '[insert explanation here]'",
        "",
        "=" * 80,
        "HANDOFF NOTES:",
        "=" * 80,
        "",
        "After completion, suggest to Coordinator:",
        "\"Content complete for [X] topics. [Y] visual specs created and every topic has visual_decision. Ready for optional inspection or visible-handbook review.\"",
        "",
    ])
```

---

### 3.4 新增：Quality Inspector

**角色定位**：在 Writer 和 Final Reviewer 之间，做快速的格式/完整性检查。

**为什么需要**：
- Final Reviewer 是独立 subagent，成本高（重新读整个 HTML）
- 很多问题是格式错误（如：JSON schema 不对、缺少必填字段），可以快速检查
- 避免让 Final Reviewer 浪费时间在低级错误上

**Prompt 结构**：

```markdown
# Quality Inspector

## 1. Identity

Role: Format and completeness validator for revision handbooks
Personality: Meticulous, checklist-driven, fast feedback
Memory: Remember the project's topic count and module structure

## 2. Mission

Perform rapid quality checks on rendered handbooks BEFORE they go to Final Reviewer.
You focus on format, completeness, and obvious errors. You do NOT judge teaching quality (that's Final Reviewer's job).

## 3. Core Principles

1. **Fast Feedback**: Spend <3 minutes per handbook
2. **Checklist-Driven**: Use pre-defined checks, don't invent new ones
3. **Pass/Fail Only**: Either approve for Final Reviewer, or send back to Writer with specific issues
4. **No Content Judgment**: Don't judge if concepts are well-explained. Only check if they exist.

## 4. Workflow

### Step 1: Load Context
Input: 
- guide.html (rendered handbook)
- qualification.json (expected topic count)
- concept_explanations.json (Writer's output)

### Step 2: Run Checklist (6 categories)

**A. Module Structure**
☐ Module 1 (Cover) present
☐ Module 2 (How to Use) present
☐ Module 3 (Topic Map) present
☐ Module 4 (Glossary) present if term_support != en
☐ Module 5 (Topic Guides) present
☐ Module 6 (Practice) present
☐ Module 7 (Exam Structure) present
☐ Module 8 (Revision Checklist) present

**B. Topic Completeness**
☐ Number of topics in HTML matches qualification.json
☐ Each topic has: essence, analogy, concepts, worked_examples
☐ No placeholder text like "[LLM fills: ...]"

**C. Visual Specs**
☐ If visual_spec exists, it has: type, complexity, prompt, llm_visual_approved=true
☐ Visual specs are not repetitive (check for 5+ identical prompts)

**D. Glossary (if applicable)**
☐ Glossary has 30-50 entries
☐ Each entry has: term_english, term_target, target_language

**E. Formatting**
☐ No broken HTML tags
☐ Images (if any) have valid paths
☐ No "undefined" or "null" text in visible content

**F. Files**
☐ guide.html exists
☐ qualification.json exists
☐ syllabus-outline.json exists
☐ concept_explanations.json exists

### Step 3: Decide

If ALL checks pass:
→ Output: { "status": "pass", "notes": "[X] topics verified, ready for Final Reviewer" }

If ANY check fails:
→ Output: { "status": "fail", "issues": ["Module 4 missing glossary", "Topic 3 has no worked_examples"] }

## 5. Deliverable Template

```json
{
  "inspection_status": "pass" | "fail",
  "issues": [
    "Module 4 (Glossary) missing but term_support=zh-CN",
    "Topic 3.2 has placeholder text '[insert analogy]'",
    "Visual spec for topics 4.1, 4.2, 4.3 are identical"
  ],
  "summary": "Checked [X] items, found [Y] issues.",
  "recommendation": "pass_to_reviewer" | "return_to_writer"
}
```

## 6. Available Tools

- read_html(path) → extract text
- validate_json_schema(file, schema)
- count_placeholders(text) → int

## 7. Handoff

If pass:
"Quality inspection complete. [X] topics verified, all modules present. Ready for Final Reviewer (independent audit)."

If fail:
"Quality inspection failed: [issues]. Returning to Handbook Writer for fixes."

## 8. Runtime Context

- You work BETWEEN Writer and Final Reviewer
- Your job is to catch obvious errors FAST
- Final Reviewer will do deep content audit (you don't need to)
- If unsure about an issue, mark as "pass" and let Final Reviewer judge
```

---

### 3.5 优化：Final Reviewer

**现有问题**：
- Prompt 已经很好，但可以添加"异常升级"机制

**优化方案**：

在现有 `build_final_review_prompt()` 末尾添加：

```python
def build_final_review_prompt(...) -> str:
    # ... 现有内容 ...
    
    return "\n".join([
        # ... 现有 prompt ...
        "",
        "=" * 80,
        "EXCEPTION ESCALATION:",
        "=" * 80,
        "",
        "If you encounter severe issues:",
        "",
        "1. **Systemic problems** (5+ topics with same error):",
        "   → Mark status='repair_needed', instructions='[pattern description]. Suggest Writer review their approach.'",
        "",
        "2. **Out of scope content** (topics not in original syllabus):",
        "   → Flag to the host LLM: 'Topic [X] appears to be out of syllabus scope. Analyst may need to re-check.'",
        "",
        "3. **Unresolvable ambiguity** (can't judge quality without domain expertise):",
        "   → Mark status='approved_with_notes', notes='Topic [X] chemistry mechanism needs subject expert review.'",
        "",
        "DO NOT spend >15 minutes on review. If you're stuck, flag it and move on.",
        "",
    ])
```

---

## 四、工作流优化

### 4.1 标准流程（所有步骤都经过 Coordinator）

```
User: "Generate AQA Chemistry IGCSE handbook with Chinese glossary, friendly style"
    ↓
Coordinator: Preflight
    → Confirm: board=AQA, level=IGCSE, subject=Chemistry, 
               term_support=zh-CN, style=friendly, image=prompt-queue
    ↓
Coordinator → Python: fetch_qualification() + write_syllabus_evidence()
    ↓
Coordinator → Analyst: "Read syllabus-evidence.json, output topics"
    ↓
Analyst → Coordinator: syllabus-outline.json
    ↓
Coordinator: Validate (no placeholders? schema valid?)
    ↓
Coordinator → Python: build_guide_plan() + write_concept_jobs()
    ↓
Coordinator → Writer: "Write concepts for [X] topics"
    ↓
Writer → Coordinator: concept_explanations.json
    ↓
Coordinator → Python: render_html() + export_pdf()
    ↓
Coordinator → Inspector: "Check format and completeness"
    ↓
Inspector → Coordinator: pass/fail + issues
    ↓
If fail:
    Coordinator → Writer: "Fix these issues: [list]"
    (loop back to Writer step)
    ↓
If pass:
    Coordinator → Reviewer (independent): "Audit quality"
    ↓
Reviewer → Coordinator: final-review-packet.json
    ↓
If repair_needed:
    Coordinator → Writer: "Fix these issues: [list from Reviewer]"
    (loop back to Writer step)
    ↓
If approved:
    Coordinator → User: "Handbook complete! [summary + files]"
```

### 4.2 异常流程

**Timeout (expert >10 min)**:
```
Coordinator → User: 
"[Expert] is working on [task]. Estimated [time] more. 
Current status: [what they're doing]"
```

**Failure (2+ times)**:
```
Coordinator → User:
"Unable to complete [task] after 2 attempts due to [reason].
Options:
1. Try different approach: [suggestion]
2. Manual intervention needed: [what to do]
3. Skip this step (not recommended)"
```

---

## 五、实施路线图

### Phase 1: 添加 Coordinator（1-2天）

1. 创建 `coordination/handbook_project_manager.py`
2. 实现 `build_coordinator_prompt()` 函数
3. 修改 `skill_interface.py`，让它先调用 Coordinator
4. 测试：用户请求 → Coordinator preflight → 调度 Analyst

### Phase 2: 添加 Quality Inspector（1天）

1. 创建 `auditing/quality_inspector.py`
2. 实现 `build_inspector_prompt()` 和快速检查逻辑
3. 修改 workflow：Writer → Inspector → Reviewer
4. 测试：Inspector 能否捕获格式错误

### Phase 3: 优化现有专家 Prompt（1天）

1. 更新 `build_syllabus_outline_prompt()` 添加 delivery checklist + handoff
2. 更新 `build_concept_writing_prompt()` 添加 error handling + memory
3. 更新 `build_final_review_prompt()` 添加 exception escalation
4. 测试：专家交接是否更清晰

### Phase 4: 集成测试（1天）

1. 端到端测试：User request → Coordinator → 4 experts → Delivery
2. 异常测试：timeout、failure、format error
3. 质量测试：最终 handbook 是否符合预期

---

## 六、预期收益

### 6.1 用户体验

**Before**:
```
用户: "生成 AQA Chemistry handbook"
系统: "请提供 level"
用户: "IGCSE"
系统: "请提供 term support language"
用户: "zh-CN"
...
```
→ 多轮交互，容易漏参数

**After**:
```
用户: "生成 AQA Chemistry handbook"
Coordinator: "我需要确认6个参数:
- Exam board: AQA ✓
- Level: ? (IGCSE / A-Level; record AS or A2 as the A-Level stage)
- Subject: Chemistry ✓
- Term support: ? (en / zh-CN / zh-TW / ja)
- Style: ? (formal / friendly / story...)
- Image method: ? (prompt-queue / custom)

请补充缺失的4个参数。"
```
→ 一次性收集，清晰明确

### 6.2 质量稳定性

**Before**:
- Writer 可能跳过某些 topic
- 格式错误直接到 Final Reviewer（浪费审核时间）
- 没有明确的修复流程

**After**:
- Inspector 快速捕获格式错误（<3分钟）
- Final Reviewer 只看高质量候选
- 每个阶段都有 delivery checklist

### 6.3 可维护性

**Before**:
- 单一 prompt 越来越长
- 修改一个部分可能影响其他部分

**After**:
- 每个专家独立优化
- Coordinator 统一管理流程
- 新增专家不影响现有专家

---

## 七、后续扩展

### 7.1 可复用的专家

设计好的专家可以跨项目复用：

- **Syllabus Outline Analyst** → 可用于其他课程大纲分析
- **Quality Inspector** → 可用于任何需要格式检查的项目
- **Final Reviewer** → 可用于任何需要独立审核的项目

### 7.2 可插拔的 Workflow

预制多个 workflow 模板：

1. **快速草稿** (Fast Draft): Analyst → Writer → 交付（跳过 Inspector 和 Reviewer）
2. **标准流程** (Standard): Analyst → Writer → Inspector → Reviewer
3. **迭代优化** (Iterative): 标准流程 + 用户反馈 → Writer 修改 → Reviewer 重审

用户可选择：`--workflow standard` 或 `--workflow fast-draft`

---

**按照此方案实施，IGCSE Handbook Skill 将从"三个独立专家"升级为"协调有序的专家团队"，实现更高的质量稳定性和更好的用户体验。**
