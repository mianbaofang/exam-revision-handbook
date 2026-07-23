from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


RAW_KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_-]{20,}")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
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

    matches = []
    for root_value in args.roots:
        root = Path(root_value).resolve()
        for path in iter_scan_files(root, args.max_bytes):
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if RAW_KEY_PATTERN.search(line):
                    matches.append({"file": str(path), "line": line_number})

    print(
        json.dumps(
            {"raw_key_matches": len(matches), "matches": matches}, ensure_ascii=False, indent=2
        )
    )
    if matches:
        print(
            "Raw API-key-like value(s) found. Values are redacted; inspect listed files locally.",
            file=sys.stderr,
        )
        return 1
    return 0


def iter_scan_files(root: Path, max_bytes: int):
    if root.is_file():
        if should_scan(root, max_bytes):
            yield root
        return
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
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
