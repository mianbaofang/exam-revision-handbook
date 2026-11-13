from __future__ import annotations

import argparse
import json
import re
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
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _manifest_identity(base: Path) -> dict[str, str]:
    """Read the root manifest when the doctor runs from an installed Skill."""

    path = base / "manifest.json"
    if not path.is_file():
        return {}
    try:
        data = _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        "name": str(data.get("name") or "").strip(),
        "version": str(data.get("version") or "").strip(),
    }


def _wheel_metadata(wheel: Path) -> dict[str, str]:
    """Read Name and Version from the wheel's dist-info METADATA."""

    metadata: dict[str, str] = {}
    try:
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if not name.endswith(".dist-info/METADATA"):
                    continue
                for line in archive.read(name).decode("utf-8", "replace").splitlines():
                    key, separator, value = line.partition(":")
                    if separator and key in {"Name", "Version"}:
                        metadata[key] = value.strip()
    except (OSError, zipfile.BadZipFile):
        return {}
    return metadata


def _wheel_payload_version(wheel: Path, module: str) -> str:
    """Read the actual module __version__ shipped inside the wheel payload."""

    init_name = f"{module.replace('.', '/')}/__init__.py"
    try:
        with zipfile.ZipFile(wheel) as archive:
            text = archive.read(init_name).decode("utf-8", "replace")
    except (KeyError, OSError, zipfile.BadZipFile):
        return ""
    match = re.search(r"(?m)^__version__\s*=\s*[\"']([^\"']+)[\"']", text)
    return match.group(1).strip() if match else ""


def _installed_layout(base: Path) -> bool:
    return (
        (base / "SKILL.md").is_file()
        and (base / "manifest.json").is_file()
        and not (base / "skills").is_dir()
    )


def _version_file_checks(
    base: Path,
    expected_name: str,
    expected_version: str,
) -> dict[str, object]:
    """Check every present VERSION/manifest copy, including the installed root."""

    installed = _installed_layout(base)
    skill_root = base / "skills" / "exam-revision-handbook"
    candidates = [
        base / "VERSION",
        base / "manifest.json",
        skill_root / "VERSION",
        skill_root / "manifest.json",
    ]
    required = (
        [base / "VERSION", base / "manifest.json"]
        if installed
        else [skill_root / "VERSION", skill_root / "manifest.json"]
    )
    mismatches: list[str] = []
    checked: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        checked.append(candidate.relative_to(base).as_posix())
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            mismatches.append(f"{candidate.name}=unreadable ({exc})")
            continue
        if candidate.suffix == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                mismatches.append(f"{candidate.name}=invalid JSON ({exc.msg})")
                continue
            if not isinstance(data, dict):
                mismatches.append(f"{candidate.name}=not a JSON object")
                continue
            found = str(data.get("version") or "").strip()
            found_name = str(data.get("name") or "").strip()
            if found_name and found_name != expected_name:
                mismatches.append(f"{candidate.name}.name={found_name}")
        else:
            found = text.strip()
        if not found:
            mismatches.append(f"{candidate.name}=missing version")
        elif found != expected_version:
            mismatches.append(f"{candidate.name}={found}")
    missing_required = [
        candidate.relative_to(base).as_posix()
        for candidate in required
        if not candidate.is_file()
    ]
    for missing in missing_required:
        mismatches.append(f"{missing}=missing")
    if not checked and not missing_required:
        mismatches.append("no VERSION or manifest file was found")
    return {
        "check": "version-files",
        "status": "pass" if not mismatches else "fail",
        "layout": "installed" if installed else "source-checkout",
        "checked": checked,
        "mismatches": mismatches,
    }


def _catalog_checks(
    base: Path,
    expected_name: str,
    expected_version: str,
) -> dict[str, object]:
    """Check both source and installed Skill Atlas catalogs when present."""

    skill_root = base / "skills" / "exam-revision-handbook"
    candidates = [
        base / "skill_atlas" / "catalog.json",
        skill_root / "skill_atlas" / "catalog.json",
    ]
    checked: list[str] = []
    mismatches: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        checked.append(candidate.relative_to(base).as_posix())
        try:
            data = _read_json(candidate)
        except (OSError, json.JSONDecodeError) as exc:
            mismatches.append(f"{candidate.name}=unreadable ({exc})")
            continue
        if not isinstance(data, dict):
            mismatches.append(f"{candidate.name}=not a JSON object")
            continue
        skills = data.get("skills")
        if not isinstance(skills, list):
            mismatches.append(f"{candidate.name}=missing skills list")
            continue
        entry = next(
            (
                item
                for item in skills
                if isinstance(item, dict) and item.get("name") == expected_name
            ),
            None,
        )
        if entry is None:
            mismatches.append(f"{candidate.name}=no {expected_name} entry")
            continue
        found = str(entry.get("version") or "").strip()
        if found != expected_version:
            mismatches.append(f"{candidate.name}={found}")
    if not checked:
        mismatches.append("no Skill Atlas catalog was found")
    return {
        "check": "catalog-version",
        "status": "pass" if not mismatches else "fail",
        "checked": checked,
        "mismatches": mismatches,
    }


def _skill_runtime_copy_checks(base: Path, lock: dict[str, object]) -> dict[str, object]:
    """Prove the Skill copy of runtime-lock and Wheel is byte-identical."""

    skill_runtime = base / "skills" / "exam-revision-handbook" / "assets" / "runtime"
    if not skill_runtime.is_dir():
        return {
            "check": "skill-runtime-copy",
            "status": "skipped",
            "reason": "no nested skills/exam-revision-handbook copy",
        }
    engine = lock.get("engine")
    engine = engine if isinstance(engine, dict) else {}
    wheel_name = str(engine.get("file") or "")
    mismatches: list[str] = []
    for relative in ["runtime-lock.json", wheel_name]:
        if not relative:
            mismatches.append("runtime-lock.json=missing engine file name")
            continue
        source = base / "assets" / "runtime" / relative
        copy = skill_runtime / relative
        if not source.is_file() or not copy.is_file():
            mismatches.append(f"{relative}=missing copy")
            continue
        if source.read_bytes() != copy.read_bytes():
            mismatches.append(f"{relative}=bytes differ")
    return {
        "check": "skill-runtime-copy",
        "status": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
    }


def _source_wheel_payload_checks(
    base: Path,
    wheel: Path,
    module: str,
) -> dict[str, object]:
    """Compare the checkout source tree with the embedded Wheel payload."""

    source_root = base / "src" / Path(*module.split("."))
    if not source_root.is_dir():
        return {
            "check": "source-wheel-payload-parity",
            "status": "skipped",
            "reason": "no src tree in this installation",
        }
    source_files = {
        path.relative_to(source_root.parent).as_posix(): path
        for path in source_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }
    missing: list[str] = []
    changed: list[str] = []
    try:
        with zipfile.ZipFile(wheel) as archive:
            wheel_names = {
                name
                for name in archive.namelist()
                if name.startswith(f"{module.replace('.', '/')}/") and not name.endswith("/")
            }
            for name, path in sorted(source_files.items()):
                if name not in wheel_names:
                    missing.append(name)
                    continue
                if archive.read(name) != path.read_bytes():
                    changed.append(name)
            extra = sorted(wheel_names - set(source_files))
    except (OSError, zipfile.BadZipFile) as exc:
        return {
            "check": "source-wheel-payload-parity",
            "status": "fail",
            "error": str(exc),
        }
    mismatches = [*missing, *changed, *extra]
    return {
        "check": "source-wheel-payload-parity",
        "status": "pass" if not mismatches else "fail",
        "source_file_count": len(source_files),
        "wheel_file_count": len(wheel_names),
        "missing": missing[:20],
        "changed": changed[:20],
        "extra": extra[:20],
    }


def _runtime_lock_identity(lock: dict[str, object], manifest: dict[str, str]) -> dict[str, object]:
    engine = lock.get("engine")
    engine = engine if isinstance(engine, dict) else {}
    mismatches: list[str] = []
    distribution = str(engine.get("distribution") or "").strip()
    version = str(engine.get("version") or "").strip()
    file_name = str(engine.get("file") or "").strip()
    sha256 = str(engine.get("sha256") or "").strip().lower()
    if manifest.get("name") and distribution != manifest["name"]:
        mismatches.append(f"distribution={distribution or 'missing'}")
    if manifest.get("version") and version != manifest["version"]:
        mismatches.append(f"version={version or 'missing'}")
    if not file_name or Path(file_name).name != file_name:
        mismatches.append(f"file={file_name or 'missing'}")
    if not SHA256_PATTERN.fullmatch(sha256):
        mismatches.append("sha256=invalid")
    return {
        "check": "runtime-lock-identity",
        "status": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the packaged handbook runtime.")
    parser.add_argument("--deep", action="store_true", help="Also run the packaged CLI help command.")
    parser.add_argument(
        "--static",
        action="store_true",
        help="Verify package files and metadata without requiring a bootstrapped runtime.",
    )
    args = parser.parse_args()
    checks: list[dict[str, object]] = []
    try:
        if args.deep and args.static:
            raise RuntimeError("--deep cannot be combined with --static")
        lock = load_lock()
        require_python(lock)
        wheel, engine_hash = verify_engine(lock)
        root = runtime_root(lock)
        ready = runtime_ready(lock, root)
        base = Path(__file__).resolve().parents[1]
        manifest = _manifest_identity(base)
        checks.extend(
            [
                {"check": "python", "status": "pass", "version": sys.version.split()[0]},
                {"check": "engine-wheel", "status": "pass", "file": wheel.name, "sha256": engine_hash},
                {
                    "check": "isolated-runtime",
                    "status": (
                        "skipped"
                        if args.static
                        else ("pass" if ready else "bootstrap-required")
                    ),
                },
            ]
        )
        metadata = _wheel_metadata(wheel)
        engine = lock["engine"]
        metadata_mismatches: list[str] = []
        if metadata.get("Name") != engine["distribution"]:
            metadata_mismatches.append(f"Name={metadata.get('Name', 'missing')}")
        if metadata.get("Version") != engine["version"]:
            metadata_mismatches.append(f"Version={metadata.get('Version', 'missing')}")
        checks.append(
            {
                "check": "wheel-metadata",
                "status": "pass" if not metadata_mismatches else "fail",
                "name": metadata.get("Name", ""),
                "wheel": metadata.get("Version", ""),
                "lock": engine["version"],
                "mismatches": metadata_mismatches,
            }
        )
        payload_version = _wheel_payload_version(wheel, str(engine.get("module") or ""))
        checks.append(
            {
                "check": "wheel-payload-version",
                "status": "pass" if payload_version == engine["version"] else "fail",
                "payload": payload_version,
                "lock": engine["version"],
            }
        )
        checks.append(_runtime_lock_identity(lock, manifest))
        checks.append(
            _version_file_checks(base, str(engine["distribution"]), str(engine["version"]))
        )
        checks.append(
            _catalog_checks(base, str(engine["distribution"]), str(engine["version"]))
        )
        checks.append(_skill_runtime_copy_checks(base, lock))
        checks.append(
            _source_wheel_payload_checks(base, wheel, str(engine.get("module") or ""))
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
    except (
        OSError,
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        json.JSONDecodeError,
    ) as exc:
        print_json({"ok": False, "checks": checks, "error": str(exc)})
        return 2
    ok = all(check["status"] in {"pass", "skipped"} for check in checks)
    print_json(
        {
            "ok": ok,
            "mode": "static" if args.static else ("deep" if args.deep else "integrity"),
            "checks": checks,
        }
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
