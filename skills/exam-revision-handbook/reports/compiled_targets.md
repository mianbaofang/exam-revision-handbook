# Compiled Targets

- OK: `True`
- Targets: `4`
- Pass: `4`
- Warn: `0`
- Block: `0`

## Target Transforms

| Target | Status | Native Surface | Adapter Mode | Permissions | Degradation | Generated Files |
| --- | --- | --- | --- | --- | --- | --- |
| `openai` | `pass` | OpenAI-style interface metadata plus neutral Agent Skills source | `metadata-adapter` | `file_write, subprocess` | `Use the canonical Skill plus the packaged Python runtime adapter.` | targets/openai/adapter.json, targets/openai/agents/openai.yaml |
| `claude` | `pass` | Claude-compatible neutral source folder with adapter notes | `neutral-source-plus-adapter` | `file_write, subprocess` | `Use Agent Skills metadata and the same packaged Python runtime adapter.` | targets/claude/adapter.json, targets/claude/README.md |
| `agent-skills` | `pass` | Agent Skills standard source tree | `neutral-agent-skills-source` | `file_write, subprocess` | `Use the canonical folder directly; Python 3.11+ remains required.` | SKILL.md, agents/interface.yaml |
| `vscode` | `pass` | VS Code/Copilot Agent Skills project or user scope | `vscode-agent-skills-adapter` | `file_write, subprocess` | `Use the canonical Agent Skills metadata; invoke scripts through the integrated terminal.` | targets/vscode/adapter.json, targets/vscode/README.md |

## Native Behavior Contracts

### openai

- Native surface: OpenAI-style interface metadata plus neutral Agent Skills source
- Activation: Use frontmatter description for catalog routing and targets/openai/agents/openai.yaml for display name, default prompt, and compatibility metadata.
- Resources: Ship the neutral source tree and expose OpenAI-facing interface metadata as a generated companion file.
- Scripts: Keep scripts as local package resources; expose help-smoke and permission metadata for reviewer approval before execution.
- Permission enforcement: `metadata-only`; native enforcement `False`
- Review artifacts: targets/openai/agents/openai.yaml, targets/openai/adapter.json, reports/review-studio.html

### claude

- Native surface: Claude-compatible neutral source folder with adapter notes
- Activation: Use SKILL.md frontmatter description as the primary activation contract and adapter.json for review metadata.
- Resources: Preserve the source tree directly; write target notes in targets/claude/README.md.
- Scripts: Scripts remain local package resources and must be reviewed through trust and permission reports before use.
- Permission enforcement: `metadata-fallback`; native enforcement `False`
- Review artifacts: targets/claude/README.md, targets/claude/adapter.json, reports/review-studio.html

### agent-skills

- Native surface: Agent Skills standard source tree
- Activation: Use SKILL.md frontmatter name and description for progressive disclosure.
- Resources: Keep optional directories as relative resources next to SKILL.md.
- Scripts: Scripts remain local optional resources and should advertise --help when executable.
- Permission enforcement: `consumer-enforced-or-metadata-only`; native enforcement `False`
- Review artifacts: SKILL.md, agents/interface.yaml, reports/review-studio.html

### vscode

- Native surface: VS Code/Copilot Agent Skills project or user scope
- Activation: Use folder name plus SKILL.md name/description; keep description under platform limits.
- Resources: Install as project or user scoped skill source, preserving relative references and scripts.
- Scripts: Scripts require workspace trust and operator/client approval outside this compiler.
- Permission enforcement: `client-or-workspace-trust`; native enforcement `False`
- Review artifacts: SKILL.md, agents/interface.yaml, reports/review-studio.html


## Failures

- None

## Warnings

- None
