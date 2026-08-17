from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INCLUDE_PATHS = (
    "src",
    "skill",
    "scripts",
    "tests",
    "pyproject.toml",
    "SKILL.md",
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
)
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in INCLUDE_PATHS:
        path = root / relative
        if path.is_file():
            files.append(path)
            continue
        if not path.is_dir():
            raise FileNotFoundError(f"baseline input is missing: {relative}")
        for candidate in path.rglob("*"):
            if not candidate.is_file() or candidate.suffix == ".pyc":
                continue
            if EXCLUDED_PARTS.intersection(candidate.relative_to(root).parts):
                continue
            files.append(candidate)
    return sorted(set(files), key=lambda item: item.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture the immutable legacy source baseline.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source.resolve()
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": file_hash(path),
        }
        for path in iter_files(root)
    ]
    payload = {
        "schema_version": "v1-legacy-source-baseline",
        "source_identity": "gcse-igcse-alevel-ap-revision-guide@0.6.2",
        "file_count": len(entries),
        "byte_count": sum(int(entry["bytes"]) for entry in entries),
        "files": entries,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(json.dumps({"ok": True, "file_count": len(entries), "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
