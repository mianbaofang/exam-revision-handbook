from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare legacy package bytes with the engine wheel.")
    parser.add_argument("--legacy-src", required=True, type=Path)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_root = args.legacy_src.resolve() / "intl_exam_guide"
    source = {
        path.relative_to(args.legacy_src.resolve()).as_posix(): digest(path.read_bytes())
        for path in source_root.rglob("*")
        if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts
    }
    with zipfile.ZipFile(args.wheel) as archive:
        packaged = {
            name: digest(archive.read(name))
            for name in archive.namelist()
            if name.startswith("intl_exam_guide/") and not name.endswith("/")
        }
    missing = sorted(set(source).difference(packaged))
    extra = sorted(set(packaged).difference(source))
    changed = sorted(path for path in set(source).intersection(packaged) if source[path] != packaged[path])
    payload = {
        "ok": not missing and not extra and not changed,
        "schema_version": "v1-wheel-payload-parity",
        "source_file_count": len(source),
        "wheel_file_count": len(packaged),
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
