from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
import zipfile


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Shared packaged-runtime integrity and cache helpers for runtime and import CLIs."

SKILL_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = SKILL_ROOT / "assets" / "runtime" / "runtime-lock.json"


def load_lock() -> dict[str, Any]:
    data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    engine = data.get("engine")
    if not isinstance(engine, dict):
        raise RuntimeError("runtime-lock.json has no engine contract")
    return data


def engine_wheel(lock: dict[str, Any]) -> Path:
    file_name = str(lock["engine"].get("file") or "")
    candidate = (LOCK_PATH.parent / file_name).resolve()
    try:
        candidate.relative_to(LOCK_PATH.parent.resolve())
    except ValueError as exc:
        raise RuntimeError("engine wheel path escapes assets/runtime") from exc
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_engine(lock: dict[str, Any]) -> tuple[Path, str]:
    wheel = engine_wheel(lock)
    if not wheel.is_file():
        raise RuntimeError(f"packaged engine wheel is missing: {wheel.name}")
    actual_hash = sha256(wheel)
    expected_hash = str(lock["engine"].get("sha256") or "").lower()
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"packaged engine hash mismatch: expected {expected_hash}, got {actual_hash}"
        )
    module = str(lock["engine"].get("module") or "").replace(".", "/")
    with zipfile.ZipFile(wheel) as archive:
        required = {f"{module}/__init__.py", f"{module}/__main__.py", f"{module}/cli.py"}
        missing = sorted(required.difference(archive.namelist()))
    if missing:
        raise RuntimeError(f"packaged engine is incomplete: missing {', '.join(missing)}")
    return wheel, actual_hash


def require_python(lock: dict[str, Any]) -> None:
    raw = str(lock.get("python", {}).get("minimum") or "3.11")
    parts = tuple(int(part) for part in raw.split(".")[:2])
    if sys.version_info[:2] < parts:
        raise RuntimeError(f"Python {raw}+ is required")


def runtime_root(lock: dict[str, Any]) -> Path:
    override = os.environ.get("EXAM_REVISION_HANDBOOK_RUNTIME_CACHE")
    if override:
        base = Path(override).expanduser()
    elif os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        base = Path(os.environ["LOCALAPPDATA"]) / "exam-revision-handbook" / "runtimes"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "exam-revision-handbook" / "runtimes"
    engine = lock["engine"]
    identity = f"{engine['version']}-{str(engine['sha256'])[:12]}"
    return base / identity


def runtime_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def marker_path(root: Path) -> Path:
    return root / "runtime-ready.json"


def runtime_ready(lock: dict[str, Any], root: Path) -> bool:
    marker = marker_path(root)
    python = runtime_python(root)
    if not marker.is_file() or not python.is_file():
        return False
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("engine_sha256") == lock["engine"].get("sha256")
        and data.get("engine_version") == lock["engine"].get("version")
    )


def ensure_runtime() -> tuple[dict[str, Any], Path]:
    """Return a verified runtime, bootstrapping its isolated environment if needed."""
    lock = load_lock()
    require_python(lock)
    verify_engine(lock)
    root = runtime_root(lock)
    if runtime_ready(lock, root):
        return lock, root

    bootstrap = Path(__file__).with_name("bootstrap_runtime.py")
    result = subprocess.run([sys.executable, str(bootstrap)], check=False)
    if result.returncode != 0 or not runtime_ready(lock, root):
        raise RuntimeError(
            f"runtime bootstrap failed with exit code {result.returncode}"
        )
    return lock, root


def activate_runtime_imports() -> Path:
    """Expose the isolated engine to packaged helper scripts without global install."""
    lock, root = ensure_runtime()
    probe = subprocess.run(
        [
            str(runtime_python(root)),
            "-c",
            "import json, sys; print(json.dumps(sys.path))",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        raise RuntimeError(probe.stderr.strip() or "runtime import-path probe failed")
    try:
        paths = json.loads(probe.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("runtime import-path probe returned invalid JSON") from exc
    for raw_path in paths:
        if raw_path and raw_path not in sys.path:
            sys.path.insert(0, raw_path)
    module = str(lock["engine"].get("module") or "")
    if not module or importlib.util.find_spec(module) is None:
        raise RuntimeError(f"packaged engine module is unavailable after bootstrap: {module}")
    return root


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
