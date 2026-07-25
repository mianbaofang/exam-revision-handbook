"""Build a skill-store ZIP with the authoritative SKILL.md at archive root."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "skill"
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}
UPWARD_REFERENCE_CHAIN = re.compile(rb"(?<![A-Za-z0-9_.-])(?:\.\.[/\\])+")


def package_version() -> str:
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def default_output_path() -> Path:
    return REPO_ROOT / "dist" / f"exam-revision-handbook-v{package_version()}.zip"


def skill_files(source_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.relative_to(source_dir).parts)
        and path.suffix != ".pyc"
    )


def package_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def inspect_package(archive_path: Path, expected_skill: bytes | None = None) -> dict[str, object]:
    with zipfile.ZipFile(archive_path) as archive:
        names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
        if "SKILL.md" not in names:
            raise ValueError("Package root does not contain SKILL.md.")
        if any(PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts for name in names):
            raise ValueError("Package contains an unsafe archive path.")
        escaped_references = []
        for name in names:
            path = PurePosixPath(name)
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            parent_depth = len(path.parent.parts) if path.parent != PurePosixPath(".") else 0
            upward_chains = UPWARD_REFERENCE_CHAIN.findall(archive.read(name))
            if any(chain.count(b"..") > parent_depth for chain in upward_chains):
                escaped_references.append(name)
        if escaped_references:
            raise ValueError(
                "Package text references paths outside the package root: "
                f"{escaped_references}"
            )
        nested_entries = [name for name in names if name.lower().endswith("/skill.md")]
        if nested_entries:
            raise ValueError(f"Package contains nested Skill entries: {nested_entries}")
        skill_bytes = archive.read("SKILL.md")
        if expected_skill is not None and skill_bytes != expected_skill:
            raise ValueError("Packaged SKILL.md does not match skill/SKILL.md.")
        if not skill_bytes.startswith(b"---\n") or b"\nname:" not in skill_bytes:
            raise ValueError("Packaged SKILL.md is missing standard YAML frontmatter.")

    return {
        "archive": str(archive_path.resolve()),
        "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "file_count": len(names),
        "skill_entry": "SKILL.md",
    }


def build_package(source_dir: Path, output_path: Path) -> dict[str, object]:
    source_dir = source_dir.resolve()
    output_path = output_path.resolve()
    skill_path = source_dir / "SKILL.md"
    if not skill_path.is_file():
        raise ValueError(f"Authoritative Skill entry not found: {skill_path}")
    if output_path.suffix.lower() != ".zip":
        raise ValueError("Skill-store package output must use the .zip extension.")
    if output_path.is_relative_to(source_dir):
        raise ValueError("Package output must be outside the source Skill directory.")

    files = skill_files(source_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".zip.tmp")
    temporary_path.unlink(missing_ok=True)

    try:
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path in files:
                relative = path.relative_to(source_dir).as_posix()
                entry = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, package_bytes(path))
        inspect_package(temporary_path, expected_skill=package_bytes(skill_path))
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return inspect_package(output_path, expected_skill=package_bytes(skill_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a skill-store ZIP whose root contains the authoritative SKILL.md."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=default_output_path())
    args = parser.parse_args()

    print(json.dumps(build_package(args.source, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
