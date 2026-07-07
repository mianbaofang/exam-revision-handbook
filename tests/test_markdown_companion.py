import hashlib
import json
import os

from intl_exam_guide.parsing.markdown_companion import (
    find_markitdown_command,
    write_markdown_companion,
)


def test_markitdown_missing_tool_writes_report(monkeypatch, tmp_path):
    monkeypatch.delenv("MARKITDOWN_CMD", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.chdir(tmp_path)
    pdf_path = tmp_path / "source" / "spec.pdf"
    pdf_path.parent.mkdir()
    pdf_path.write_bytes(b"%PDF-1.4\n")

    report = write_markdown_companion(pdf_path)

    data = json.loads((pdf_path.parent / "markdown-extraction.json").read_text(encoding="utf-8"))
    assert report.status == "missing-tool"
    assert data["status"] == "missing-tool"
    assert data["schema_version"] == "v0.5-markdown-extraction"
    assert data["source_pdf_sha256"] == hashlib.sha256(b"%PDF-1.4\n").hexdigest()
    assert data["markdown_path"].endswith("specification.md")
    assert not (pdf_path.parent / "specification.md").exists()


def test_markitdown_env_command_generates_markdown_and_report(monkeypatch, tmp_path):
    script = tmp_path / "fake_markitdown.py"
    script.write_text(
        """
import pathlib
import sys
if '--version' in sys.argv:
    print('fake-markitdown 1.0')
    raise SystemExit(0)
out = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
out.write_text('# Specification\\n\\n## Topic table', encoding='utf-8')
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("MARKITDOWN_CMD", f"{os.sys.executable} {script}")
    pdf_path = tmp_path / "source" / "spec.pdf"
    pdf_path.parent.mkdir()
    pdf_path.write_bytes(b"%PDF-1.4\n")

    report = write_markdown_companion(pdf_path)

    markdown_path = pdf_path.parent / "specification.md"
    data = json.loads((pdf_path.parent / "markdown-extraction.json").read_text(encoding="utf-8"))
    assert report.status == "success"
    assert markdown_path.read_text(encoding="utf-8").startswith("# Specification")
    assert data["status"] == "success"
    assert data["tool"] == "MARKITDOWN_CMD"
    assert data["tool_version"] == "fake-markitdown 1.0"
    assert data["markdown_char_count"] > 0


def test_markitdown_discovery_prefers_project_isolated_venv(monkeypatch, tmp_path):
    monkeypatch.delenv("MARKITDOWN_CMD", raising=False)
    monkeypatch.setenv("PATH", "")
    command_path = tmp_path / ".venv-markitdown" / "bin" / "markitdown"
    command_path.parent.mkdir(parents=True)
    command_path.write_text("#!/bin/sh\n", encoding="utf-8")

    command = find_markitdown_command(tmp_path / "source")

    assert command is not None
    assert command.label == "project .venv-markitdown"
    assert command.command == [str(command_path)]
