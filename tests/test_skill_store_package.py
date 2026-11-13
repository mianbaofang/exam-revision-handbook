from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_skill_store_package.py"
LOCAL_ABSOLUTE_PATH = re.compile(
    rb"(?i)(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|/(?:Users|home)/)"
)


def build_package(output: Path, source: Path | None = None) -> dict[str, object]:
    command = [sys.executable, str(SCRIPT), "--output", str(output)]
    if source is not None:
        command.extend(["--source", str(source)])
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_skill_store_package_places_authoritative_skill_at_archive_root(tmp_path: Path):
    output = tmp_path / "revision-guide-skill.zip"

    result = build_package(output)

    prefix = "exam-revision-handbook/"
    assert result["top_level"] == "exam-revision-handbook"
    assert result["skill_entry"] == f"{prefix}SKILL.md"
    with zipfile.ZipFile(output) as archive:
        names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
        assert f"{prefix}SKILL.md" in names
        assert "skill/SKILL.md" not in names
        assert not any(name.startswith("gcse-igcse-alevel-ap-revision-guide/") for name in names)
        source_skill = (REPO_ROOT / "skills" / "exam-revision-handbook" / "SKILL.md").read_bytes()
        assert archive.read(f"{prefix}SKILL.md") == source_skill.replace(
            b"\r\n", b"\n"
        ).replace(b"\r", b"\n")
        manifest = json.loads(
            (REPO_ROOT / "skills" / "exam-revision-handbook" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        assert archive.read(f"{prefix}VERSION").decode("utf-8").strip() == manifest["version"]
        assert f"{prefix}agents/openai.yaml" in names
        assert f"{prefix}references/revision_guide_spec.md" in names
        assert f"{prefix}VERSION" in names
        assert f"{prefix}manifest.json" in names
        assert f"{prefix}scripts/doctor.py" in names
        assert f"{prefix}scripts/bootstrap_runtime.py" in names
        assert f"{prefix}scripts/import_concept_explanations.py" in names
        assert f"{prefix}scripts/import_infographic_assets.py" in names
        assert not any(name.startswith(f"{prefix}src/") for name in names)
        assert not any(name.startswith(f"{prefix}tests/") for name in names)
        assert not any(name.startswith(f"{prefix}docs/") for name in names)
        assert f"{prefix}requirements-ci.txt" not in names
        assert f"{prefix}reports/package_verification.json" not in names
        for name in names:
            if Path(name).suffix.lower() in {
                ".json",
                ".md",
                ".py",
                ".txt",
                ".yaml",
                ".yml",
            }:
                assert LOCAL_ABSOLUTE_PATH.search(archive.read(name)) is None
        catalog = json.loads(archive.read(f"{prefix}skill_atlas/catalog.json"))
        for skill in catalog["skills"]:
            for resource in skill["resources"]:
                resource_path = resource.replace("\\", "/")
                assert f"{prefix}{resource_path}" in names


def test_skill_store_package_is_reproducible(tmp_path: Path):
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    first_result = build_package(first)
    second_result = build_package(second)

    assert first_result["sha256"] == second_result["sha256"]


def test_runtime_block_message_points_to_canonical_skill_entry():
    cli_source = (REPO_ROOT / "src" / "intl_exam_guide" / "cli.py").read_text(
        encoding="utf-8"
    )

    assert "See SKILL.md for LLM workflow instructions." in cli_source
    assert "skill/SKILL.md" not in cli_source


def test_skill_store_package_rejects_references_above_archive_root(tmp_path: Path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text(
        "---\nname: broken-skill\n---\n\nRead `../docs/contract.md`.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source",
            str(source),
            "--output",
            str(tmp_path / "broken.zip"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "outside the Skill root" in result.stderr


def test_skill_store_package_normalizes_text_line_endings(tmp_path: Path):
    source = tmp_path / "skill"
    references = source / "references"
    references.mkdir(parents=True)
    skill_lf = b"---\nname: portable-skill\n---\n\nRead the reference.\n"
    reference_lf = b"# Contract\n\nPortable text.\n"
    (source / "SKILL.md").write_bytes(skill_lf.replace(b"\n", b"\r\n"))
    (references / "contract.md").write_bytes(reference_lf.replace(b"\n", b"\r\n"))

    first = build_package(tmp_path / "crlf.zip", source)
    (source / "SKILL.md").write_bytes(skill_lf)
    (references / "contract.md").write_bytes(reference_lf)
    second = build_package(tmp_path / "lf.zip", source)

    assert first["sha256"] == second["sha256"]
    with zipfile.ZipFile(tmp_path / "crlf.zip") as archive:
        assert archive.read("portable-skill/SKILL.md") == skill_lf
        assert archive.read("portable-skill/references/contract.md") == reference_lf


def test_skill_store_package_rejects_machine_specific_paths(tmp_path: Path):
    source = tmp_path / "skill"
    reports = source / "reports"
    reports.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: broken-skill\n---\n\nRun the workflow.\n",
        encoding="utf-8",
    )
    (reports / "report.json").write_text(
        json.dumps({"skill_dir": r"C:\Users\Example\broken-skill"}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source",
            str(source),
            "--output",
            str(tmp_path / "broken.zip"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "machine-specific absolute paths" in result.stderr


def test_extracted_skill_doctor_checks_installed_root_and_version(tmp_path: Path):
    output = tmp_path / "skill.zip"
    build_package(output)
    install_root = tmp_path / "install"
    with zipfile.ZipFile(output) as archive:
        archive.extractall(install_root)
    skill_root = install_root / "exam-revision-handbook"
    assert (skill_root / "VERSION").is_file()
    assert not (skill_root / "src").exists()

    result = subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "doctor.py"), "--static"],
        cwd=skill_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    checks = {check["check"]: check for check in payload["checks"]}
    assert payload["ok"] is True
    assert checks["version-files"]["layout"] == "installed"
    assert checks["version-files"]["status"] == "pass"
    assert checks["catalog-version"]["status"] == "pass"
    assert checks["wheel-payload-version"]["status"] == "pass"
    assert checks["isolated-runtime"]["status"] == "skipped"


def test_packaged_runtime_scripts_match_repository_scripts():
    packaged = REPO_ROOT / "skills" / "exam-revision-handbook" / "scripts"
    scripts = REPO_ROOT / "scripts"
    names = [
        "_runtime.py",
        "bootstrap_runtime.py",
        "doctor.py",
        "run_runtime.py",
        "import_concept_explanations.py",
        "import_infographic_assets.py",
        "write_concept_explanations_from_jobs.py",
    ]

    for name in names:
        assert (scripts / name).read_bytes() == (packaged / name).read_bytes(), name
