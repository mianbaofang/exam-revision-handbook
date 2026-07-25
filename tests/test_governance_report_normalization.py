from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "normalize_governance_reports.py"


def test_normalizer_redacts_source_root_and_resolves_atlas_resources(tmp_path: Path):
    project = tmp_path / "exam-revision-handbook"
    source_root = tmp_path / "generated-stage" / "exam-revision-handbook"
    reports = project / "reports"
    atlas = project / "skill_atlas"
    runtime = project / "assets" / "runtime"
    reports.mkdir(parents=True)
    atlas.mkdir()
    runtime.mkdir(parents=True)
    (runtime / "engine.whl").write_bytes(b"wheel")
    (reports / "compiled_targets.json").write_text(
        json.dumps({"skill_dir": str(source_root)}),
        encoding="utf-8",
    )
    (atlas / "catalog.json").write_text(
        json.dumps(
            {
                "skills": [
                    {
                        "name": "exam-revision-handbook",
                        "resources": ["assets/engine.whl"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(project),
            "--source-root",
            str(source_root),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    compiled = json.loads((reports / "compiled_targets.json").read_text(encoding="utf-8"))
    catalog = json.loads((atlas / "catalog.json").read_text(encoding="utf-8"))
    assert compiled["skill_dir"] == "<SKILL_ROOT>"
    assert catalog["skills"][0]["resources"] == ["assets/runtime/engine.whl"]

    check = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(project),
            "--source-root",
            str(source_root),
            "--check",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr


def test_normalizer_redacts_external_generator_paths(tmp_path: Path):
    project = tmp_path / "exam-revision-handbook"
    reports = project / "reports"
    reports.mkdir(parents=True)
    (reports / "review-studio.json").write_text(
        json.dumps(
            {
                "evidence_link": r"C:\Users\Example\.agents\skills\yao-meta-skill\docs\migration-v2.md",
                "decision": "review",
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(project)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((reports / "review-studio.json").read_text(encoding="utf-8"))
    assert payload["evidence_link"] == "LOCAL_PATH/docs/migration-v2.md"
    assert payload["decision"] == "review"
