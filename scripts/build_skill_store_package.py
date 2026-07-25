"""Build the deterministic, installable standard Skill archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
UPWARD_REFERENCE_CHAIN = re.compile(rb"(?<![A-Za-z0-9_.-])(?:\.\.[/\\])+")
LOCAL_ABSOLUTE_PATH = re.compile(
    rb"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|/(?:Users|home)/)"
)
STANDARD_ROOTS = (
    "SKILL.md",
    "LICENSE",
    "manifest.json",
    "requirements-ci.txt",
    "agents",
    "assets",
    "evals",
    "references",
    "reports",
    "security",
    "skill_atlas",
)
STANDARD_SCRIPTS = (
    "_runtime.py",
    "bootstrap_runtime.py",
    "doctor.py",
    "run_runtime.py",
    "import_concept_explanations.py",
    "import_infographic_assets.py",
    "write_concept_explanations_from_jobs.py",
)
POST_PACKAGE_REPORTS = {
    "install_simulation.json",
    "install_simulation.md",
    "package_verification.json",
    "package_verification.md",
    "registry_audit.json",
    "registry_audit.md",
}
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def load_manifest(source_dir: Path) -> dict[str, object]:
    path = source_dir / "manifest.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def skill_name(source_dir: Path) -> str:
    manifest_name = str(load_manifest(source_dir).get("name") or "").strip()
    if manifest_name:
        return manifest_name
    text = (source_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*['\"]?([a-z0-9-]+)", text)
    if not match:
        raise ValueError("SKILL.md frontmatter does not define a valid name.")
    return match.group(1)


def package_version(source_dir: Path = REPO_ROOT) -> str:
    version = str(load_manifest(source_dir).get("version") or "").strip()
    if not version:
        raise ValueError("manifest.json does not define a package version.")
    return version


def default_output_path() -> Path:
    return REPO_ROOT / "dist" / f"exam-revision-handbook-v{package_version()}.zip"


def selected_files(source_dir: Path) -> list[tuple[Path, Path]]:
    selected: dict[str, tuple[Path, Path]] = {}

    def include(path: Path) -> None:
        if path.is_symlink() or not path.is_file() or path.suffix == ".pyc":
            return
        relative = path.relative_to(source_dir)
        if any(part in IGNORED_PARTS for part in relative.parts):
            return
        if relative.parts[:1] == ("reports",) and relative.name in POST_PACKAGE_REPORTS:
            return
        selected[relative.as_posix()] = (path, relative)

    for name in STANDARD_ROOTS:
        candidate = source_dir / name
        if candidate.is_file():
            include(candidate)
        elif candidate.is_dir():
            for path in candidate.rglob("*"):
                include(path)
    scripts_dir = source_dir / "scripts"
    for name in STANDARD_SCRIPTS:
        candidate = scripts_dir / name
        if candidate.is_file():
            include(candidate)
    return [selected[key] for key in sorted(selected)]


def package_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def inspect_package(
    archive_path: Path,
    *,
    expected_name: str,
    expected_skill: bytes | None = None,
    canonical: bool = False,
) -> dict[str, object]:
    skill_entry = f"{expected_name}/SKILL.md"
    with zipfile.ZipFile(archive_path) as archive:
        names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
        if skill_entry not in names:
            raise ValueError(f"Package does not contain {skill_entry}.")
        if any(PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts for name in names):
            raise ValueError("Package contains an unsafe archive path.")
        top_levels = sorted({PurePosixPath(name).parts[0] for name in names})
        if top_levels != [expected_name]:
            raise ValueError(f"Package must contain one top-level Skill folder: {top_levels}")
        nested_entries = [
            name for name in names if name.lower().endswith("/skill.md") and name != skill_entry
        ]
        if nested_entries:
            raise ValueError(f"Package contains nested Skill entries: {nested_entries}")
        escaped_references = []
        local_path_entries = []
        for name in names:
            path = PurePosixPath(name)
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            payload = archive.read(name)
            parent_depth = max(0, len(path.parent.parts) - 1)
            upward_chains = UPWARD_REFERENCE_CHAIN.findall(payload)
            if any(chain.count(b"..") > parent_depth for chain in upward_chains):
                escaped_references.append(name)
            if LOCAL_ABSOLUTE_PATH.search(payload):
                local_path_entries.append(name)
        if escaped_references:
            raise ValueError(
                "Package text references paths outside the Skill root: "
                f"{escaped_references}"
            )
        if local_path_entries:
            raise ValueError(
                "Package contains machine-specific absolute paths: "
                f"{local_path_entries}"
            )
        skill_bytes = archive.read(skill_entry)
        if expected_skill is not None and skill_bytes != expected_skill:
            raise ValueError("Packaged SKILL.md does not match the canonical root SKILL.md.")
        if not skill_bytes.startswith(b"---\n") or b"\nname:" not in skill_bytes:
            raise ValueError("Packaged SKILL.md is missing standard YAML frontmatter.")
        if canonical:
            required = {
                skill_entry,
                f"{expected_name}/agents/openai.yaml",
                f"{expected_name}/references/workflow-contract.md",
                f"{expected_name}/assets/runtime/runtime-lock.json",
                f"{expected_name}/scripts/run_runtime.py",
                f"{expected_name}/scripts/import_concept_explanations.py",
                f"{expected_name}/scripts/import_infographic_assets.py",
            }
            missing = sorted(required.difference(names))
            if missing:
                raise ValueError(f"Package is missing required standard Skill files: {missing}")
            forbidden_prefixes = tuple(
                f"{expected_name}/{name}/"
                for name in (".git", ".github", "docs", "skill", "src", "tests")
            )
            forbidden = [name for name in names if name.startswith(forbidden_prefixes)]
            if forbidden:
                raise ValueError(f"Package contains repository-only files: {forbidden[:10]}")
            catalog_name = f"{expected_name}/skill_atlas/catalog.json"
            if catalog_name in names:
                catalog = json.loads(archive.read(catalog_name))
                missing_resources = set()
                for skill in catalog.get("skills", []):
                    for resource in skill.get("resources", []):
                        resource_path = str(resource).replace("\\", "/")
                        archive_name = f"{expected_name}/{resource_path}"
                        if archive_name not in names:
                            missing_resources.add(archive_name)
                if missing_resources:
                    raise ValueError(
                        "Skill Atlas references missing package resources: "
                        f"{sorted(missing_resources)}"
                    )

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    return {
        "archive": str(archive_path.resolve()),
        "sha256": digest,
        "bytes": archive_path.stat().st_size,
        "file_count": len(names),
        "top_level": expected_name,
        "skill_entry": skill_entry,
    }


def build_package(source_dir: Path, output_path: Path) -> dict[str, object]:
    source_dir = source_dir.resolve()
    output_path = output_path.resolve()
    skill_path = source_dir / "SKILL.md"
    if not skill_path.is_file():
        raise ValueError(f"Canonical Skill entry not found: {skill_path}")
    if output_path.suffix.lower() != ".zip":
        raise ValueError("Skill-store package output must use the .zip extension.")
    name = skill_name(source_dir)
    files = selected_files(source_dir)
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
            for path, relative in files:
                entry_name = PurePosixPath(name, *relative.parts).as_posix()
                entry = zipfile.ZipInfo(entry_name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, package_bytes(path))
        result = inspect_package(
            temporary_path,
            expected_name=name,
            expected_skill=package_bytes(skill_path),
            canonical=source_dir == REPO_ROOT,
        )
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    result = inspect_package(
        output_path,
        expected_name=name,
        expected_skill=package_bytes(skill_path),
        canonical=source_dir == REPO_ROOT,
    )
    checksum_path = output_path.with_suffix(".sha256")
    checksum_path.write_text(
        f"{result['sha256']}  {output_path.name}\n",
        encoding="ascii",
        newline="\n",
    )
    result["checksum"] = str(checksum_path.resolve())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the versioned standard Skill ZIP and SHA-256 file."
    )
    parser.add_argument("--source", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=default_output_path())
    args = parser.parse_args()
    print(json.dumps(build_package(args.source, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
