from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

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


def _wheel_metadata_version(wheel) -> str:
    """从 wheel 的 dist-info METADATA 读取 Version（读取失败返回空串）。"""
    try:
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if name.endswith(".dist-info/METADATA"):
                    for line in archive.read(name).decode("utf-8", "replace").splitlines():
                        if line.startswith("Version:"):
                            return line.split(":", 1)[1].strip()
    except (OSError, zipfile.BadZipFile):
        return ""
    return ""


def _version_file_mismatches(expected_version: str) -> list[str]:
    """检查各处 VERSION/manifest 版本与 runtime lock 是否一致（存在才查）。"""
    base = Path(__file__).resolve().parents[1]
    candidates = [
        base / "skills" / "exam-revision-handbook" / "VERSION",
        base / "VERSION",
        base / "skills" / "exam-revision-handbook" / "manifest.json",
        base / "manifest.json",
    ]
    mismatches: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if candidate.suffix == ".json":
            import json as _json

            try:
                found = str(_json.loads(text).get("version", ""))
            except json.JSONDecodeError:
                continue
        else:
            found = text.strip()
        if found and found != expected_version:
            mismatches.append(f"{candidate.name}={found}")
    return mismatches


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
        wheel_version = _wheel_metadata_version(wheel)
        checks.append(
            {
                "check": "wheel-metadata-version",
                "status": "pass" if wheel_version == lock["engine"]["version"] else "fail",
                "wheel": wheel_version,
                "lock": lock["engine"]["version"],
            }
        )
        mismatches = _version_file_mismatches(lock["engine"]["version"])
        checks.append(
            {
                "check": "version-files",
                "status": "pass" if not mismatches else "fail",
                "mismatches": mismatches,
            }
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
    ok = all(check["status"] == "pass" for check in checks)
    print_json({"ok": ok, "checks": checks})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
