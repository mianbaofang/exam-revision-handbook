from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


STAMP = re.compile(r"-\d{8}-\d{4}(?=\.[A-Za-z0-9]+(?:$|[\"']))")


def normalize_string(value: str, root: Path) -> str:
    variants = {
        str(root),
        root.as_posix(),
        str(root).replace("\\", "/"),
        str(root).replace("\\", "\\\\"),
    }
    normalized = value
    for variant in sorted(variants, key=len, reverse=True):
        normalized = normalized.replace(variant, "<ROOT>")
    return STAMP.sub("-<STAMP>", normalized.replace("\r\n", "\n"))


def normalize_json(value: Any, root: Path) -> Any:
    if isinstance(value, dict):
        return {key: normalize_json(item, root) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [normalize_json(item, root) for item in value]
    if isinstance(value, str):
        return normalize_string(value, root)
    return value


def logical_name(path: Path) -> str:
    return STAMP.sub("-<STAMP>", path.as_posix())


def tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = logical_name(path.relative_to(root))
        if path.suffix.lower() == ".json":
            content = json.dumps(
                normalize_json(json.loads(path.read_text(encoding="utf-8")), root),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        elif path.suffix.lower() in {".html", ".txt", ".md", ".svg"}:
            content = normalize_string(path.read_text(encoding="utf-8"), root).encode("utf-8")
        else:
            content = path.read_bytes()
        result[name] = hashlib.sha256(content).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare normalized legacy and candidate output trees.")
    parser.add_argument("--legacy", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    legacy = tree(args.legacy.resolve())
    candidate = tree(args.candidate.resolve())
    missing = sorted(set(legacy).difference(candidate))
    extra = sorted(set(candidate).difference(legacy))
    changed = sorted(path for path in set(legacy).intersection(candidate) if legacy[path] != candidate[path])
    payload = {
        "ok": not missing and not extra and not changed,
        "schema_version": "v1-normalized-output-parity",
        "legacy_file_count": len(legacy),
        "candidate_file_count": len(candidate),
        "missing": missing,
        "extra": extra,
        "changed": changed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
