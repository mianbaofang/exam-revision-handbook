from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

from _runtime import (
    load_lock,
    marker_path,
    print_json,
    require_python,
    runtime_python,
    runtime_ready,
    runtime_root,
    verify_engine,
)


SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Create a versioned isolated Python environment for the packaged engine."
PACKAGE_INDEX_POLICY_HOSTS = (
    "https://pypi.org/simple",
    "https://files.pythonhosted.org",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install the packaged handbook engine and pinned dependencies into a user cache."
    )
    parser.parse_args(argv)
    try:
        lock = load_lock()
        require_python(lock)
        wheel, engine_hash = verify_engine(lock)
        root = runtime_root(lock)
        if runtime_ready(lock, root):
            print_json({"ok": True, "status": "already-ready", "runtime": str(root)})
            return 0
        root.parent.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True, clear=False, symlinks=False).create(root)
        python = runtime_python(root)
        requirements = [str(item) for item in lock.get("install_requirements", [])]
        result = subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel), *requirements],
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"runtime dependency installation failed with exit code {result.returncode}")
        probe = subprocess.run(
            [str(python), "-m", str(lock["engine"]["module"]), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            raise RuntimeError(probe.stderr.strip() or "packaged CLI probe failed")
        payload = {
            "schema_version": "v1-runtime-ready",
            "engine_version": lock["engine"]["version"],
            "engine_sha256": engine_hash,
            "python": sys.version.split()[0],
            "requirements": requirements,
        }
        marker = marker_path(root)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=root, prefix=".runtime-ready.", suffix=".tmp", delete=False
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = Path(handle.name)
        os.replace(temp_path, marker)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print_json({"ok": False, "error": str(exc)})
        return 2
    print_json({"ok": True, "status": "bootstrapped", "runtime": str(root)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
