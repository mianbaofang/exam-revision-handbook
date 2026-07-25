# Security Trust Report

- OK: `True`
- Scanned files: `68`
- Scripts: `15`
- Internal script modules: `1`
- Secret findings: `0`
- Network-capable scripts: `1`
- Network policy covered scripts: `1`
- Network policy missing scripts: `0`
- File-write scripts: `9`
- Permission approvals: `3 / 3`
- Permission approval gaps: `0`
- CLI help smoke checked: `14`
- CLI help smoke failures: `0`
- Interactive scripts: `0`
- Package hash scope: `source-contract-without-generated-reports`
- Package hash files: `68`
- Package SHA256: `67efdf7a3ec8b11598cf963406a50252ff43485977c284ccae96add9b61e45f6`

## Failures

- None

## Warnings

- None

## Dependency Evidence

- Files: `requirements-ci.txt, pyproject.toml`
- Pinned entries: `4`
- Unpinned entries: `0`

## Network Policy

- Policy file: `security/network_policy.json`
- Present: `True`
- Covered scripts: `1`
- Missing scripts: `none`
- Mismatches: `0`

## Permission Governance

- Policy file: `security/permission_policy.json`
- Present: `True`
- Required capabilities: `file_write, network, subprocess`
- Approved capabilities: `file_write, network, subprocess`
- Missing approvals: `none`
- Invalid approvals: `none`
- Expired approvals: `none`

## CLI Help Smoke

- Enabled: `True`
- Timeout seconds: `5.0`
- Checked scripts: `14`
- Passed scripts: `14`
- Failed scripts: `none`

## Script Surface

| Script | Interface | Declared | Argparse | Main Guard | Input | Network | File Write | Subprocess | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripts\_runtime.py | internal-module | True | False | False | False | False | True | True | Shared packaged-runtime integrity and cache helpers for runtime and import CLIs. |
| scripts\audit_ap_courses.py | cli | False | True | True | False | True | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\bootstrap_runtime.py | cli | True | True | True | False | False | True | True | Create a versioned isolated Python environment for the packaged engine. |
| scripts\build_skill_store_package.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\capture_release_assets.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\doctor.py | cli | True | True | True | False | False | False | True | Read-only packaged runtime integrity and readiness check. |
| scripts\finalize_release_samples.py | cli | False | True | True | False | False | False | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\import_concept_explanations.py | cli | True | True | True | False | False | True | False | Import LLM-reviewed concept content through the isolated packaged engine. |
| scripts\import_infographic_assets.py | cli | True | True | True | False | False | True | False | Import reviewed visual assets through the isolated packaged engine. |
| scripts\render_intro_animation.py | cli | False | True | True | False | False | True | True | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\run_runtime.py | cli | True | True | True | False | False | False | True | Pass commands and exit codes through to the isolated packaged engine. |
| scripts\scan_for_raw_keys.py | cli | False | True | True | False | False | False | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\sync_intro_animation_sources.py | cli | False | True | True | False | False | True | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\verify_release_samples.py | cli | False | True | True | False | False | False | False | Default CLI classification; add SCRIPT_INTERFACE for internal modules. |
| scripts\write_concept_explanations_from_jobs.py | cli | True | True | True | False | False | False | False | Preserve the refusal-only legacy command without writing teaching content. |
