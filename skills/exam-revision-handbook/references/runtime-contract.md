# Runtime Adapter Contract

## Canonical Invocation

Run all engine commands through:

```text
python scripts/run_runtime.py -- <legacy arguments>
```

The v0.7 standard Skill adapter preserves the validated v0.6.2 engine command
surface exactly:

```text
discover
generate
extract-evidence
demo
review
export-pdf
audit-delivery
index-review-ledger
inspect
```

It must pass arguments, standard input, standard output, standard error, working directory, and exit code through without reinterpretation. It must not weaken preflight, review, hash, or delivery gates.

## Packaged Engine

The authoritative engine is a versioned wheel under `assets/runtime/`. Do not reimplement Provider, planning, rendering, visual, auditing, or delivery logic in Skill scripts. `scripts/doctor.py` verifies the wheel and records its hash. `scripts/bootstrap_runtime.py` installs it into a versioned user cache without modifying the global Python environment.

The engine still requires network access for official source retrieval. PDF export additionally requires a compatible Playwright browser. These are existing runtime prerequisites, not migrated capability loss.

## Import Helpers

The installable Skill also preserves the two user-facing import entry points:

```text
python scripts/import_concept_explanations.py ...
python scripts/import_infographic_assets.py ...
```

Both helpers must run when the repository `src/` tree is absent. They activate
the same isolated, hash-checked runtime as `run_runtime.py`; they must not rely
on a global package installation. `write_concept_explanations_from_jobs.py`
remains a refusal-only compatibility command because Python is not allowed to
write teaching content.
