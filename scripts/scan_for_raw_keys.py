from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


RAW_KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_-]{20,}")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", ".uv-python", ".uv-cache", ".venv", "venv", ".tox", ".mypy_cache"}
SKIP_SUFFIXES = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".webp",
    ".zip",
}
WINDOWS_DEVICE_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan text files for raw API-key-looking values.")
    parser.add_argument("roots", nargs="*", default=["."], help="Directories or files to scan.")
    parser.add_argument("--max-bytes", type=int, default=5_000_000)
    args = parser.parse_args()

    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    matches = []
    errors = []
    for root_value in args.roots:
        root = Path(root_value).resolve()
        if not root.exists():
            errors.append({"file": str(root), "error": "missing-root"})
            continue
        def onerror(exc):
            errors.append({"file": str(exc.filename), "error": "unreadable-directory"})
        for path in iter_scan_files(root, args.max_bytes, onerror=onerror):
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                errors.append({"file": str(path), "error": "unreadable-file"})
                continue
            for line_number, line in enumerate(lines, 1):
                if RAW_KEY_PATTERN.search(line):
                    matches.append({"file": str(path), "line": line_number})

    print(
        json.dumps(
            {"raw_key_matches": len(matches), "matches": matches, "scan_errors": errors,
             "excluded_directory_names": sorted(SKIP_DIRS)}, ensure_ascii=False, indent=2
        )
    )
    if matches:
        print(
            "Raw API-key-like value(s) found. Values are redacted; inspect listed files locally.",
            file=sys.stderr,
        )
        return 1
    return 2 if errors else 0


def iter_scan_files(root: Path, max_bytes: int, onerror=None):
    """Prune tool dependencies before traversal; explicit files are still scanned.

    Do not skip .env/config/source files or every ignored file: they may contain keys.
    No symlink traversal into unrelated directories.
    """
    if root.is_file():
        if should_scan(root, max_bytes):
            yield root
        return
    if not root.exists():
        return
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        parent = Path(directory)
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS
                         and not (parent / name / "pyvenv.cfg").is_file()
                         and not (parent / name).is_symlink())
        for name in sorted(files):
            path = parent / name
            if should_scan(path, max_bytes):
                yield path


def should_scan(path: Path, max_bytes: int) -> bool:
    if path.name.upper() in WINDOWS_DEVICE_NAMES:
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    try:
        return path.stat().st_size <= max_bytes
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
