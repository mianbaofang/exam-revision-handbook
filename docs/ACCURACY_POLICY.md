# Accuracy Policy / 准确性政策

## English

This project supports student revision. Accuracy and traceability take priority
over generation speed, visual polish, or fluent prose.

### Non-Negotiable Rules

1. Use official syllabus/specification evidence; do not invent syllabus requirements.
2. Do not copy past-paper questions, mark schemes, or copyrighted textbook material.
3. Do not commit downloaded official PDFs, private keys, or generated handbook outputs.
4. Treat official headings as containers until the LLM has checked whether lower-level rows, bullets, clauses, conditions, or objectives are independently assessable.
5. Keep analysis, teaching content, worked answers, and visual judgment under LLM ownership. Python may validate structure but cannot make those decisions.
6. Do not approve a handbook from machine diagnostics or from a sample of pages, topics, examples, or visuals.
7. Do not generate the delivery PDF until the exact current HTML has complete, hash-bound LLM approval.

### What The Mechanical Layer Can Do

- discover supported official AQA, Edexcel, CAIE, and College Board AP sources;
- download the selected public specification or CED at runtime;
- create `source/specification.md`, page-level evidence, source URLs, and PDF hashes;
- validate JSON shape, cross-artifact consistency, files, links, counts, and hashes;
- render LLM-authored artifacts to HTML;
- reject PDF export when current-HTML LLM approval is absent, stale, incomplete, or not LLM-authored.
- validate a temporary PDF candidate mechanically and promote it only after hard
  technical checks pass; keep older exports historical through explicit pointers.

These checks can identify missing evidence and broken contracts. They cannot
prove that a teaching explanation, worked answer, diagram, or final handbook is
correct.

### Required LLM Review

The active LLM Reviewer must open or screenshot the complete current HTML and
review every final topic. The review covers subject facts, definitions,
relationships, explanations, worked questions, solution steps, final answers,
units, source anchors, and visible syllabus coverage.

Every rendered visual must also be checked for semantic accuracy: labels,
arrows, positions, structures, relationships, scales, units, captions, and
correspondence with the associated topic. Appearance or successful loading is
not enough.

Any issue returns to the Writer. The responsible source artifact is rewritten,
HTML is rerendered, and the LLM repeats the complete visible review. Only then
may it write the per-item `review-ledger/`, bind the compact
`agent-product-review.json` summary to it, and run the gated candidate-PDF
export.

### High-Stakes Use

The required LLM review is a delivery gate, not a claim of professional
certification. Families and schools should still use a qualified teacher or
subject specialist for high-stakes exam preparation, regional entry advice,
equivalency decisions, and unusually deep or disputed content.

## 中文

本项目用于学生复习。准确性和可追溯性高于生成速度、视觉精美程度或文字流畅度。

### 不可妥协的规则

1. 只以官方课程大纲或 specification 证据为依据，不编造考点。
2. 不复制 past-paper questions、mark schemes 或受版权保护的教材内容。
3. 不把下载的官方 PDF、私密 key 或生成的完整手册提交到仓库。
4. 官方 Topic、Unit、Section 或章节标题默认只是结构容器；LLM 必须继续检查更低层的表格行、项目符号、条款、条件和目标是否可以独立考查。
5. 大纲分析、教学内容、例题答案和配图判断由 LLM 负责；Python 只能校验结构，不能替代这些决定。
6. 不得根据机器诊断或抽样查看少数页面、topic、例题、视觉后批准手册。
7. 当前 HTML 没有获得完整且与哈希绑定的 LLM 批准前，不得生成交付 PDF。

### 机械层可以做什么

- 自动发现受支持的 AQA、Edexcel、CAIE 和 College Board AP 官方来源；
- 在运行时下载选定的公开 specification 或 CED；
- 生成 `source/specification.md`、逐页证据、来源 URL 和 PDF 哈希；
- 校验 JSON 结构、跨产物一致性、文件、链接、数量和哈希；
- 把 LLM 编写的产物渲染成 HTML；
- 当当前 HTML 的 LLM 审查缺失、过期、不完整或并非 LLM 编写时，拒绝导出 PDF。

这些检查能发现证据缺失和合同错误，但不能证明教学解释、例题答案、图解或整本手册正确。

### 必须由 LLM 完成的审查

当前 LLM Reviewer 必须亲自打开或截图查看完整 HTML，逐一审查所有最终 topic，包括学科事实、定义、关系、教学解释、例题、解题步骤、最终答案、单位、来源锚点，以及官方要求是否在手册中真正得到讲解。

每个实际渲染视觉也必须检查语义准确性：标签、箭头、位置、结构、关系、比例、单位、说明文字和对应 topic。仅仅“加载成功”或“看起来好看”不算通过。

发现任何问题都要返回 Writer，重写对应源产物、重新渲染 HTML，并再次做完整可视审查。只有全部通过后，LLM 才能写入 `agent-product-review.json` 并运行受门禁保护的 PDF 导出。

### 高风险使用

LLM 审查是交付门禁，不等于专业认证。用于正式大考准备、地区报名建议、学历等效判断，或遇到深度和争议性内容时，家庭和学校仍应请合格教师或学科专家复核。
