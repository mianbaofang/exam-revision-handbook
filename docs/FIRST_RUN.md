# First use and recovery / 首次使用与故障恢复

Install the canonical Skill using the README command, then ask the Agent to start a handbook. Installation is quick; authoring a complete syllabus is not a one-minute task. Existing source, writing, visual and approval contracts still apply.

## 1. Check the environment

Run from the installed Skill root (the directory with `SKILL.md`), using a Python version allowed by `references/runtime-contract.md`:

```bash
python scripts/doctor.py --static
python scripts/bootstrap_runtime.py
python scripts/doctor.py --deep
python scripts/run_runtime.py -- --help
```

`--static` checks shipped files, metadata and wheel integrity without installing anything. `bootstrap_runtime.py` prepares the isolated runtime and can download dependencies. `--deep` additionally executes that runtime. A `bootstrap-required` result needs the bootstrap command, not a new handbook or a different provider key.

静态检查失败时先查看 `checks` / `error`，修复或重新取得缺失、哈希不符的安装文件；不要通过修改 runtime lock 来绕过。失败输出的 `next_actions` 只是恢复建议，不会自动联网或安装。

## 2. Confirm the run

The first response is the complete preflight defined in the canonical Skill. Answer the external-image-capability question explicitly even if an image tool is already installed. Unknown capability stays blocked. The Agent preserves answered fields and asks only for the missing ones. A batch needs independent review and delivery for every handbook.

## 3. Understand what is ready

| What you have | Meaning |
|---|---|
| `qualification.json` + `syllabus-evidence.json` + `source/` | Evidence only; no handbook yet |
| HTML + pending concepts or images | Draft; identify and finish the missing authoring / visuals |
| `current-render.json` | Exact current render binding, not approval |
| Full current Topic / Visual / holistic LLM review | May proceed only if all required gates also pass |
| `current-pdf.json` | Current approved-PDF provenance; check hashes before delivery |

```bash
python scripts/run_runtime.py -- audit-delivery --out YOUR_OUTPUT_DIRECTORY
```

This audit is read-only. Use its blocker codes to locate the relevant artifact. Do not edit generated review hashes, reuse another subject's approval, infer the current PDF from file modification time, or treat a passing machine check as LLM approval. Open the actual HTML, repair source artifacts, rerender and review again whenever the content changes.

## 4. Maintainer key scan

`python scripts/scan_for_raw_keys.py .` prunes dependency/cache directories such as `.uv-python` and `.venv` before traversal. It still checks source, `.env`, config and other user files, including ignored files. An explicitly named file inside a pruned directory is scanned. Missing/unreadable roots fail rather than reporting a clean scan. Potential key values are never printed. This is a pattern scan, not proof that no secret exists.
