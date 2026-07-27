# Security Trust Report

- OK: `True`
- Scanned files: `35`
- Scripts: `7`
- Internal script modules: `1`
- Secret findings: `0`
- Network-capable scripts: `0`
- Network policy covered scripts: `0`
- Network policy missing scripts: `0`
- File-write scripts: `4`
- Permission approvals: `2 / 2`
- Permission approval gaps: `0`
- CLI help smoke checked: `6`
- CLI help smoke failures: `0`
- Interactive scripts: `0`
- Package hash scope: `source-contract-without-generated-reports`
- Package hash files: `35`
- Package SHA256: `37d886ff9fd5b7decc8e5e9d57c4100f2b04e0a68d8f601ca1c305276ff7968a`

## Failures

- None

## Warnings

- None

## Dependency Evidence

- Files: `requirements-ci.txt`
- Pinned entries: `4`
- Unpinned entries: `0`

## Network Policy

- Policy file: `security/network_policy.json`
- Present: `True`
- Covered scripts: `0`
- Missing scripts: `none`
- Mismatches: `0`

## Permission Governance

- Policy file: `security/permission_policy.json`
- Present: `True`
- Required capabilities: `file_write, subprocess`
- Approved capabilities: `file_write, subprocess`
- Missing approvals: `none`
- Invalid approvals: `none`
- Expired approvals: `none`

## CLI Help Smoke

- Enabled: `True`
- Timeout seconds: `5.0`
- Checked scripts: `6`
- Passed scripts: `6`
- Failed scripts: `none`

## Script Surface

| Script | Interface | Declared | Argparse | Main Guard | Input | Network | File Write | Subprocess | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripts\_runtime.py | internal-module | True | False | False | False | False | True | True | Shared packaged-runtime integrity and cache helpers for runtime and import CLIs. |
| scripts\bootstrap_runtime.py | cli | True | True | True | False | False | True | True | Create a versioned isolated Python environment for the packaged engine. |
| scripts\doctor.py | cli | True | True | True | False | False | False | True | Read-only packaged runtime integrity and readiness check. |
| scripts\import_concept_explanations.py | cli | True | True | True | False | False | True | False | Import LLM-reviewed concept content through the isolated packaged engine. |
| scripts\import_infographic_assets.py | cli | True | True | True | False | False | True | False | Import reviewed visual assets through the isolated packaged engine. |
| scripts\run_runtime.py | cli | True | True | True | False | False | False | True | Pass commands and exit codes through to the isolated packaged engine. |
| scripts\write_concept_explanations_from_jobs.py | cli | True | True | True | False | False | False | False | Preserve the refusal-only legacy command without writing teaching content. |
