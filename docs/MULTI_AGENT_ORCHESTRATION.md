# Multi-Agent Orchestration Contract

Every handbook run is a three-role workflow. In a Skill-compatible Agent runtime
with subagent support, the Agent must dispatch these roles in order instead of
letting one writing context approve its own output:

1. `syllabus_outline_analyst` parses official provider evidence into
   `CourseSpec` and `LearningUnit` records.
2. `handbook_writer` creates source-bound `PedagogicalUnit` content, practice,
   visuals, HTML, and PDF.
3. `final_reviewer` inspects rendered output and review evidence independently
   before handoff.

`final_reviewer` must run in a fresh Agent/LLM context or subagent and must list
both earlier roles in `independent_from`. A completed review is not the same as a
final-ready verdict: the reviewer can still mark the output draft or blocked.
If no independent reviewer context is available, the output must remain
`review-ready` or `draft`; it must not be presented as `final-ready`.
The reviewer must also produce `agent-product-review.json` after inspecting the
visible handbook, comparing it with the syllabus outline, checking visuals and
sampled PDF pages, and recording any repairs. Without that artifact, the
package remains review-ready even if local validation is clean.

The generated `agent-orchestration.json` is intentionally machine-readable. It
sets `multi_agent_required: true`, includes an `agent_runtime_contract`, and
adds a `dispatch_brief` for each role so a user Agent can automatically assign
the syllabus analyst, writer, and independent reviewer without inventing the
workflow.

Artifacts:

- `agent-orchestration.json`: role status and evidence.
- `delivery-contract.json`: public delivery contract, including role evidence.
- `final-review-packet.json`: final reviewer evidence and verdict.
- `agent-product-review.json`: active Agent product-review and repair evidence.

The Python CLI records and validates the contract without requiring a private
model API. The Skill layer is responsible for dispatching real subagents when
the user's Agent environment exposes them. If it cannot, the final reviewer must
still be a separate LLM/Agent pass over the rendered handbook and review packet
before handoff.
