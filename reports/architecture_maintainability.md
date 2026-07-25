# Architecture Maintainability

Generated at: `2026-07-25T00:00:00Z`

## Summary

- decision: `pass`
- python files: `4`
- scripts: `0`
- tests: `0`
- internal modules: `1`
- CLI scripts: `3`
- Yao CLI command handlers: `0`
- entrypoint command handlers: `0`
- command modules: `0`
- largest file lines: `108`
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
| `scripts\_runtime.py` | `108` | `internal-module` | `pass` |
| `scripts\bootstrap_runtime.py` | `82` | `cli-script` | `pass` |
| `scripts\doctor.py` | `67` | `cli-script` | `pass` |
| `scripts\run_runtime.py` | `54` | `cli-script` | `pass` |

## Release Rule

- `block` hotspots should be split before governed release.
- `warn` hotspots can ship only when Review Studio keeps them visible and a reviewer accepts the modularization plan.
- Do not split a file only for line count; split when a stable responsibility boundary is clear.
