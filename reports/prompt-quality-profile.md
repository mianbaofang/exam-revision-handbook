# Prompt Quality Profile

Skill: `exam-revision-handbook`
Relevance: `prompt-aware`
Overall quality score: `80.0/100`

## Primary Task Family

**Teaching guidance**
- Matched keywords: teach, guide, course

## Complexity

- Band: `complex`
- Score: `6`
- Reason: multiple inputs, constraints, or task families require tradeoff handling

## Need Model

- Explicit Need: Create source-backed GCSE, IGCSE, A-Level, and College Board AP revision handbooks from official AQA, Edexcel, CAIE, and College Board sources. Use when acquiring a syllabus, decomposing requirements into atomic teaching points, writing worked examples, planning or reviewing educational visuals, rendering a handbook, reviewing HTML, or exporting an approved PDF. Do not use for unsupported curricula unless the user accepts the experimental manual-import boundary.
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: not yet explicit
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: usable output with clear validation cues

## RTF To Skill Mapping

- Role: Use a teacher role that adapts to learner level and avoids overloading the first pass.
- Task: Explain through progressive steps, examples, and visible success checks.
- Format: Return learner-facing sections, worked examples, checkpoints, and common mistakes.

## Quality Matrix

### Completeness — 70/100
- Matched signals: example
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 80/100
- Matched signals: none
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 85/100
- Matched signals: boundary
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 95/100
- Matched signals: action, use, workflow
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 70/100
- Matched signals: none
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Teaching guidance
- Score: `3`
- Keywords: teach, guide, course
- Role: Use a teacher role that adapts to learner level and avoids overloading the first pass.
- Task: Explain through progressive steps, examples, and visible success checks.
- Format: Return learner-facing sections, worked examples, checkpoints, and common mistakes.

### Creative generation
- Score: `1`
- Keywords: copy
- Role: Use a taste-aware creator role with clear audience, tone, and originality boundaries.
- Task: Generate variants, explain selection logic, and preserve the user's distinctive constraints.
- Format: Return options with rationale, selection criteria, and refinement paths.

### Analytical reasoning
- Score: `1`
- Keywords: analysis
- Role: Use an analyst role that separates evidence, inference, uncertainty, and recommendation.
- Task: State assumptions, compare alternatives, and make the decision path inspectable.
- Format: Return findings, evidence, tradeoffs, recommendation, and residual risks.

### Execution operation
- Score: `1`
- Keywords: workflow
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
