from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


COMMANDS = (
    None,
    "discover",
    "generate",
    "extract-evidence",
    "demo",
    "review",
    "export-pdf",
    "audit-delivery",
    "index-review-ledger",
    "inspect",
)


def normalized(value: str) -> str:
    return value.replace("\r\n", "\n").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare legacy and packaged CLI help contracts.")
    parser.add_argument("--legacy-root", required=True, type=Path)
    parser.add_argument("--runner", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    env = dict(os.environ)
    env["PYTHONPATH"] = str(args.legacy_root.resolve() / "src")
    results: list[dict[str, object]] = []
    for command in COMMANDS:
        suffix = [command, "--help"] if command else ["--help"]
        legacy = subprocess.run(
            [sys.executable, "-m", "intl_exam_guide", *suffix],
            cwd=args.legacy_root,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        candidate = subprocess.run(
            [sys.executable, str(args.runner.resolve()), "--", *suffix],
            cwd=args.runner.resolve().parents[1],
            check=False,
            capture_output=True,
            text=True,
        )
        passed = (
            legacy.returncode == candidate.returncode
            and normalized(legacy.stdout) == normalized(candidate.stdout)
            and normalized(legacy.stderr) == normalized(candidate.stderr)
        )
        results.append(
            {
                "command": command or "<root>",
                "pass": passed,
                "legacy_exit": legacy.returncode,
                "candidate_exit": candidate.returncode,
            }
        )
    payload = {
        "ok": all(bool(item["pass"]) for item in results),
        "schema_version": "v1-cli-contract-parity",
        "commands": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
