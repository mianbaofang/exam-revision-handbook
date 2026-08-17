# Architecture Maintainability

Generated at: `2026-08-17`

## Summary

- decision: `pass`
- python files: `7`
- scripts: `0`
- tests: `0`
- internal modules: `1`
- CLI scripts: `6`
- Yao CLI command handlers: `0`
- entrypoint command handlers: `0`
- command modules: `0`
- largest file lines: `326`
- early watch threshold lines: `600`
- early watchlist: `0`
- watch threshold lines: `720`
- watchlist: `0`
- hotspots: `0`
- blockers: `0`

This report keeps maintainability risk visible before the Meta Skill grows more gates, renderers, and CLI commands.

## Hotspots

No file-size hotspots found.

## Watchlist

No near-threshold files found.

## Early Watchlist

No early watch files found.

## Largest Files

| File | Lines | Kind | Severity |
| --- | ---: | --- | --- |
| `scripts\import_infographic_assets.py` | `326` | `cli-script` | `pass` |
| `scripts\import_concept_explanations.py` | `197` | `cli-script` | `pass` |
| `scripts\_runtime.py` | `156` | `internal-module` | `pass` |
| `scripts\bootstrap_runtime.py` | `86` | `cli-script` | `pass` |
| `scripts\doctor.py` | `67` | `cli-script` | `pass` |
| `scripts\write_concept_explanations_from_jobs.py` | `50` | `cli-script` | `pass` |
| `scripts\run_runtime.py` | `48` | `cli-script` | `pass` |

## Release Rule

- `block` hotspots should be split before governed release.
- `warn` hotspots can ship only when Review Studio keeps them visible and a reviewer accepts the modularization plan.
- Do not split a file only for line count; split when a stable responsibility boundary is clear.
