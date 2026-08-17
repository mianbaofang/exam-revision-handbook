from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

from intl_exam_guide import __version__


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAME = "exam-revision-handbook"


def test_release_identity_is_consistent() -> None:
    manifest = json.loads((REPO_ROOT / "manifest.json").read_text(encoding="utf-8"))
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    runtime = json.loads(
        (REPO_ROOT / "assets" / "runtime" / "runtime-lock.json").read_text(
            encoding="utf-8"
        )
    )["engine"]

    assert manifest["name"] == EXPECTED_NAME
    assert project["project"]["name"] == EXPECTED_NAME
    assert runtime["distribution"] == EXPECTED_NAME
    assert manifest["version"] == project["project"]["version"] == __version__
    assert runtime["version"] == manifest["version"]

    wheel = REPO_ROOT / "assets" / "runtime" / runtime["file"]
    assert wheel.is_file()
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == runtime["sha256"]


def test_skill_frontmatter_uses_canonical_name() -> None:
    skill = (REPO_ROOT / "skills" / EXPECTED_NAME / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: exam-revision-handbook\n")


def test_discoverable_package_is_the_only_repository_skill_entry() -> None:
    entries = list(REPO_ROOT.rglob("SKILL.md"))
    assert entries == [REPO_ROOT / "skills" / EXPECTED_NAME / "SKILL.md"]
