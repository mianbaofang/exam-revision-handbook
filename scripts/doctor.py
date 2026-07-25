from __future__ import annotations

import argparse
import json
import subprocess
import sys

from _runtime import (
    load_lock,
    print_json,
    require_python,
    runtime_python,
    runtime_ready,
    runtime_root,
    verify_engine,
)


SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Read-only packaged runtime integrity and readiness check."


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the packaged handbook runtime.")
    parser.add_argument("--deep", action="store_true", help="Also run the packaged CLI help command.")
    args = parser.parse_args()
    checks: list[dict[str, object]] = []
    try:
        lock = load_lock()
        require_python(lock)
        wheel, engine_hash = verify_engine(lock)
        root = runtime_root(lock)
        ready = runtime_ready(lock, root)
        checks.extend(
            [
                {"check": "python", "status": "pass", "version": sys.version.split()[0]},
                {"check": "engine-wheel", "status": "pass", "file": wheel.name, "sha256": engine_hash},
                {"check": "isolated-runtime", "status": "pass" if ready else "bootstrap-required"},
            ]
        )
        if args.deep:
            if not ready:
                raise RuntimeError("isolated runtime is not bootstrapped; run scripts/bootstrap_runtime.py")
            result = subprocess.run(
                [str(runtime_python(root)), "-m", str(lock["engine"]["module"]), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            checks.append(
                {
                    "check": "cli-help",
                    "status": "pass" if result.returncode == 0 else "fail",
                    "exit_code": result.returncode,
                }
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "packaged CLI help failed")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print_json({"ok": False, "checks": checks, "error": str(exc)})
        return 2
    print_json({"ok": True, "checks": checks})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
