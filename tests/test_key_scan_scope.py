import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts/scan_for_raw_keys.py"


def run(*args):
    result = subprocess.run([sys.executable, str(SCRIPT), *map(str,args)], capture_output=True, text=True)
    return result, json.loads(result.stdout)


def test_dependency_pruning_does_not_hide_user_config_or_explicit_file(tmp_path):
    dependency = tmp_path / ".uv-python" / "library.py"
    dependency.parent.mkdir()
    dependency.write_text("sk-" + "a" * 24, encoding="utf-8")
    result, data = run(tmp_path)
    assert result.returncode == 0 and data["raw_key_matches"] == 0
    result, data = run(dependency)
    assert result.returncode == 1 and data["raw_key_matches"] == 1
    assert "a" * 24 not in result.stdout + result.stderr
    (tmp_path / ".env").write_text("KEY=sk-" + "b" * 24, encoding="utf-8")
    result, data = run(tmp_path)
    assert result.returncode == 1 and data["matches"][0]["file"].endswith(".env")


def test_missing_scan_root_is_not_reported_clean(tmp_path):
    result, data = run(tmp_path / "missing")
    assert result.returncode == 2 and data["scan_errors"][0]["error"] == "missing-root"
