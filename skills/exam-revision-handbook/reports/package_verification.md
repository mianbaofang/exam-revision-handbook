# Package Verification

- OK: `True`
- Package directory: `<SKILL_ROOT>\dist-yao-final`
- Targets: `4 / 4` adapters present
- Archive present: `True`
- Archive SHA256: `72c33d65c622f40bb4d083150030198901738d56b2190ba00ad289ca8d8233ac`
- Nested SKILL.md entries: `0`
- Failures: `0`
- Warnings: `0`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `package-manifest` | `pass` | Package manifest exists: <SKILL_ROOT>\dist-yao-final\manifest.json |
| `claude-adapter` | `pass` | Adapter exists for target: claude |
| `generic-adapter` | `pass` | Adapter exists for target: generic |
| `openai-adapter` | `pass` | Adapter exists for target: openai |
| `vscode-adapter` | `pass` | Adapter exists for target: vscode |
| `archive-safe-paths` | `pass` | Archive has no absolute or parent-traversal entries |
| `archive-entry-exam-revision-handbook/SKILL.md` | `pass` | Archive contains exam-revision-handbook/SKILL.md |
| `archive-entry-exam-revision-handbook/manifest.json` | `pass` | Archive contains exam-revision-handbook/manifest.json |
| `archive-entry-exam-revision-handbook/agents/interface.yaml` | `pass` | Archive contains exam-revision-handbook/agents/interface.yaml |
| `archive-single-skill-entrypoint` | `pass` | Archive exposes only the root SKILL.md entrypoint |
| `archive-excludes-generated` | `pass` | Archive excludes generated dist/, .previews/, and tests/tmp* contents |
| `registry-ok` | `pass` | Registry audit is OK |
| `registry-name-match` | `pass` | Registry package name matches package manifest |
| `registry-version-match` | `pass` | Registry package version matches package manifest |
| `registry-compat-claude` | `pass` | Registry compatibility is reviewable for target: claude |
| `registry-compat-generic` | `pass` | Registry compatibility is reviewable for target: generic |
| `registry-compat-openai` | `pass` | Registry compatibility is reviewable for target: openai |
| `registry-compat-vscode` | `pass` | Registry compatibility is reviewable for target: vscode |

## Failures

- None

## Warnings

- None
