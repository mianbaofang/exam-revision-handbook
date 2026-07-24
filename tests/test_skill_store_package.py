from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_skill_store_package.py"


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

    assert result["skill_entry"] == "SKILL.md"
    with zipfile.ZipFile(output) as archive:
        names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
        assert "SKILL.md" in names
        assert "skill/SKILL.md" not in names
        assert not any(name.startswith("igcse-a-level-revision-guide/") for name in names)
        source_skill = (REPO_ROOT / "skill" / "SKILL.md").read_bytes()
        assert archive.read("SKILL.md") == source_skill.replace(b"\r\n", b"\n").replace(
            b"\r", b"\n"
        )
        assert "agents/openai.yaml" in names
        assert "references/revision_guide_spec.md" in names


def test_skill_store_package_is_reproducible(tmp_path: Path):
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    first_result = build_package(first)
    second_result = build_package(second)

    assert first_result["sha256"] == second_result["sha256"]


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
    assert "outside the package root" in result.stderr


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
        assert archive.read("SKILL.md") == skill_lf
        assert archive.read("references/contract.md") == reference_lf
