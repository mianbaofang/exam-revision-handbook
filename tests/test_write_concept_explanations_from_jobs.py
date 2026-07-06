import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "write_concept_explanations_from_jobs.py"
)
SCRIPT_SPEC = spec_from_file_location("write_concept_explanations_from_jobs", SCRIPT_PATH)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
SCRIPT_MODULE = module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)


def test_legacy_python_concept_writer_refuses_to_generate_content(tmp_path, capsys):
    concepts = tmp_path / "concepts"
    concepts.mkdir()
    (concepts / "concept_jobs.json").write_text(
        json.dumps(
            [
                {
                    "topic_title": "Source-bound topic",
                    "source_points": ["Official source point."],
                }
            ]
        ),
        encoding="utf-8",
    )

    result = SCRIPT_MODULE.main([str(tmp_path)])

    stderr = json.loads(capsys.readouterr().err)
    assert result == 2
    assert stderr["ok"] is False
    assert stderr["concept_jobs_present"] is True
    assert "Python does not write teaching content" in stderr["reason"]
    assert not (concepts / "concept_explanations.json").exists()


def test_legacy_python_concept_writer_reports_missing_jobs_without_writing(tmp_path, capsys):
    result = SCRIPT_MODULE.main([str(tmp_path)])

    stderr = json.loads(capsys.readouterr().err)
    assert result == 2
    assert stderr["concept_jobs_present"] is False
    assert stderr["target"].endswith("concept_explanations.json")


def test_legacy_subject_template_entrypoint_is_removed():
    assert not hasattr(SCRIPT_MODULE, "write_entry")
