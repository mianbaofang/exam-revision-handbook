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
        assert archive.read("SKILL.md") == (REPO_ROOT / "skill" / "SKILL.md").read_bytes()
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
