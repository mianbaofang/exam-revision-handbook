from __future__ import annotations

import json
import sys
import zipfile
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = spec_from_file_location("doctor_under_test", SCRIPTS / "doctor.py")
assert SPEC and SPEC.loader
DOCTOR = module_from_spec(SPEC)
SPEC.loader.exec_module(DOCTOR)


def write_installed_root(root: Path, *, version: str = "0.8.0", include_version: bool = True) -> None:
    (root / "SKILL.md").write_text("---\nname: exam-revision-handbook\n---\n", encoding="utf-8")
    (root / "manifest.json").write_text(
        json.dumps({"name": "exam-revision-handbook", "version": version}),
        encoding="utf-8",
    )
    if include_version:
        (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")


def test_doctor_installed_root_requires_version_file(tmp_path):
    write_installed_root(tmp_path, include_version=False)

    missing = DOCTOR._version_file_checks(tmp_path, "exam-revision-handbook", "0.8.0")
    assert missing["status"] == "fail"
    assert "VERSION=missing" in missing["mismatches"]

    (tmp_path / "VERSION").write_text("0.8.0\n", encoding="utf-8")
    present = DOCTOR._version_file_checks(tmp_path, "exam-revision-handbook", "0.8.0")
    assert present["status"] == "pass"
    assert present["layout"] == "installed"


def test_doctor_version_file_checks_do_not_swallow_invalid_manifest(tmp_path):
    write_installed_root(tmp_path)
    (tmp_path / "manifest.json").write_text("{", encoding="utf-8")

    result = DOCTOR._version_file_checks(tmp_path, "exam-revision-handbook", "0.8.0")

    assert result["status"] == "fail"
    assert any("invalid JSON" in item for item in result["mismatches"])


def test_doctor_catalog_checks_reject_stale_or_missing_catalog(tmp_path):
    write_installed_root(tmp_path)

    missing = DOCTOR._catalog_checks(tmp_path, "exam-revision-handbook", "0.8.0")
    assert missing["status"] == "fail"
    assert "no Skill Atlas catalog" in missing["mismatches"][0]

    catalog_dir = tmp_path / "skill_atlas"
    catalog_dir.mkdir()
    (catalog_dir / "catalog.json").write_text(
        json.dumps(
            {
                "skills": [
                    {"name": "exam-revision-handbook", "version": "0.7.4"},
                ]
            }
        ),
        encoding="utf-8",
    )
    stale = DOCTOR._catalog_checks(tmp_path, "exam-revision-handbook", "0.8.0")
    assert stale["status"] == "fail"
    assert "catalog.json=0.7.4" in stale["mismatches"]

    (catalog_dir / "catalog.json").write_text(
        json.dumps(
            {
                "skills": [
                    {"name": "exam-revision-handbook", "version": "0.8.0"},
                ]
            }
        ),
        encoding="utf-8",
    )
    current = DOCTOR._catalog_checks(tmp_path, "exam-revision-handbook", "0.8.0")
    assert current["status"] == "pass"


def test_doctor_source_wheel_payload_parity_detects_stale_source_fix(tmp_path):
    source_root = tmp_path / "src" / "intl_exam_guide"
    source_root.mkdir(parents=True)
    init_path = source_root / "__init__.py"
    init_path.write_text('__version__ = "0.8.0"\n', encoding="utf-8")
    wheel_path = tmp_path / "engine.whl"
    with zipfile.ZipFile(wheel_path, "w") as archive:
        archive.write(init_path, "intl_exam_guide/__init__.py")

    current = DOCTOR._source_wheel_payload_checks(tmp_path, wheel_path, "intl_exam_guide")
    assert current["status"] == "pass"

    init_path.write_text('__version__ = "0.8.0"\n# later fix\n', encoding="utf-8")
    stale = DOCTOR._source_wheel_payload_checks(tmp_path, wheel_path, "intl_exam_guide")
    assert stale["status"] == "fail"
    assert stale["changed"] == ["intl_exam_guide/__init__.py"]


def test_doctor_wheel_metadata_and_payload_version_match_lock(tmp_path):
    wheel_path = tmp_path / "engine.whl"
    with zipfile.ZipFile(wheel_path, "w") as archive:
        archive.writestr(
            "exam_revision_handbook-0.8.0.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: exam-revision-handbook\nVersion: 0.8.0\n",
        )
        archive.writestr("intl_exam_guide/__init__.py", '__version__ = "0.8.0"\n')

    metadata = DOCTOR._wheel_metadata(wheel_path)
    assert metadata == {"Name": "exam-revision-handbook", "Version": "0.8.0"}
    assert DOCTOR._wheel_payload_version(wheel_path, "intl_exam_guide") == "0.8.0"
    assert DOCTOR._wheel_payload_version(wheel_path, "missing.module") == ""
