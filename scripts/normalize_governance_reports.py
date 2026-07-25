"""Make generated governance reports portable without changing their findings."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOTS = ("reports", "skill_atlas")
TEXT_SUFFIXES = {".csv", ".html", ".json", ".md", ".txt", ".xml"}
LOCAL_ABSOLUTE_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|/(?:Users|home)/)"
)
LOCAL_PATH_TOKEN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|/(?:Users|home)/)[^\s\"'<>]+"
)


def root_variants(path: Path) -> tuple[str, ...]:
    resolved = path.resolve()
    return tuple(dict.fromkeys((str(resolved), resolved.as_posix())))


def replace_source_root(text: str, source_root: Path) -> str:
    for value in root_variants(source_root):
        text = text.replace(value, "<SKILL_ROOT>")
    return text


def redact_external_local_paths(text: str) -> str:
    """Keep report evidence portable when a generator links its own files."""

    def replacement(match: re.Match[str]) -> str:
        token = match.group(0).rstrip(".,;)")
        normalized = token.replace("\\", "/")
        for marker in ("/docs/", "/reports/", "/references/", "/scripts/"):
            index = normalized.lower().find(marker)
            if index >= 0:
                return "LOCAL_PATH" + normalized[index:]
        return "LOCAL_PATH"

    return LOCAL_PATH_TOKEN.sub(replacement, text)


def resolve_resource(project_root: Path, value: str) -> str:
    relative = value.replace("\\", "/")
    if (project_root / relative).is_file():
        return relative
    parts = Path(relative).parts
    if len(parts) < 2:
        return relative
    resource_root = project_root / parts[0]
    if not resource_root.is_dir():
        return relative
    matches = [path for path in resource_root.rglob(parts[-1]) if path.is_file()]
    if len(matches) == 1:
        return matches[0].relative_to(project_root).as_posix()
    return relative


def normalize_json(value: Any, project_root: Path, source_root: Path) -> Any:
    if isinstance(value, str):
        return redact_external_local_paths(replace_source_root(value, source_root))
    if isinstance(value, list):
        return [normalize_json(item, project_root, source_root) for item in value]
    if not isinstance(value, dict):
        return value
    normalized = {
        key: normalize_json(item, project_root, source_root)
        for key, item in value.items()
    }
    resources = normalized.get("resources")
    if isinstance(resources, list) and all(isinstance(item, str) for item in resources):
        normalized["resources"] = [
            resolve_resource(project_root, item) for item in resources
        ]
    return normalized


def iter_report_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for name in REPORT_ROOTS:
        root = project_root / name
        if not root.is_dir():
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
        )
    return sorted(files)


def unresolved_resources(project_root: Path, value: Any) -> list[str]:
    missing: list[str] = []
    if isinstance(value, list):
        for item in value:
            missing.extend(unresolved_resources(project_root, item))
    elif isinstance(value, dict):
        resources = value.get("resources")
        if isinstance(resources, list):
            for item in resources:
                if isinstance(item, str) and not (project_root / item).is_file():
                    missing.append(item)
        for item in value.values():
            missing.extend(unresolved_resources(project_root, item))
    return missing


def normalize_reports(
    project_root: Path,
    source_root: Path,
    *,
    check: bool,
) -> dict[str, object]:
    project_root = project_root.resolve()
    changed: list[str] = []
    failures: list[str] = []
    report_files = iter_report_files(project_root)
    for path in report_files:
        original = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            payload = json.loads(original)
            payload = normalize_json(payload, project_root, source_root)
            missing = sorted(set(unresolved_resources(project_root, payload)))
            if missing:
                failures.append(f"{path.name}: unresolved resources: {missing}")
            normalized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        else:
            normalized = redact_external_local_paths(replace_source_root(original, source_root))
        if LOCAL_ABSOLUTE_PATH.search(normalized):
            failures.append(f"{path.name}: local absolute path remains")
        if normalized != original:
            changed.append(path.relative_to(project_root).as_posix())
            if not check:
                path.write_text(normalized, encoding="utf-8", newline="\n")
    if check and changed:
        failures.append(f"reports require normalization: {changed}")
    if failures:
        raise ValueError("; ".join(failures))
    return {"ok": True, "changed": changed, "checked_files": len(report_files)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize generated report paths without altering conclusions."
    )
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    source_root = (args.source_root or project_root).resolve()
    print(
        json.dumps(
            normalize_reports(project_root, source_root, check=args.check),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
