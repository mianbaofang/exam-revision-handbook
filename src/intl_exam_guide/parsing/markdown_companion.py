from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

MARKDOWN_EXTRACTION_FILE = "markdown-extraction.json"
MARKDOWN_SPECIFICATION_FILE = "specification.md"
MARKDOWN_EXTRACTION_SCHEMA_VERSION = "v0.5-markdown-extraction"


@dataclass(frozen=True)
class MarkdownExtractionReport:
    schema_version: str
    tool: str
    tool_version: str | None
    source_pdf: str
    source_pdf_sha256: str
    markdown_path: str
    command: list[str]
    created_at: str
    status: str
    markdown_char_count: int
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MarkItDownCommand:
    command: list[str]
    label: str


def write_markdown_companion(
    pdf_path: Path,
    *,
    source_pdf_sha256: str | None = None,
    output_dir: Path | None = None,
) -> MarkdownExtractionReport:
    """Convert an official PDF to Markdown via external MarkItDown CLI and record a report."""

    source_dir = output_dir or pdf_path.parent
    source_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = source_dir / MARKDOWN_SPECIFICATION_FILE
    report_path = source_dir / MARKDOWN_EXTRACTION_FILE
    digest = source_pdf_sha256 or sha256_file(pdf_path)
    command = find_markitdown_command(source_dir)
    warnings: list[str] = []
    status = "success"
    markdown_char_count = 0
    used_command: list[str] = []
    tool_label = "markitdown"
    tool_version: str | None = None

    if command is None:
        status = "missing-tool"
        warnings.append(
            "MarkItDown CLI was not found. Set MARKITDOWN_CMD, create .venv-markitdown, or install markitdown on PATH."
        )
    else:
        tool_label = command.label
        tool_version = markitdown_version(command.command)
        used_command = [*command.command, str(pdf_path), "-o", str(markdown_path)]
        try:
            result = subprocess.run(
                used_command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            status = "failed"
            warnings.append(f"MarkItDown CLI could not run: {exc}")
        else:
            if result.returncode != 0:
                status = "failed"
                stderr = result.stderr.strip()
                stdout = result.stdout.strip()
                detail = stderr or stdout or f"exit code {result.returncode}"
                warnings.append(f"MarkItDown CLI failed: {detail[:1000]}")
            elif not markdown_path.exists():
                stdout = result.stdout.strip()
                if stdout:
                    markdown_path.write_text(stdout, encoding="utf-8")
                else:
                    status = "failed"
                    warnings.append("MarkItDown CLI succeeded but did not write Markdown output.")
            if status == "success" and markdown_path.exists():
                markdown_text = markdown_path.read_text(encoding="utf-8", errors="replace")
                markdown_char_count = len(markdown_text)
                if not markdown_text.strip():
                    status = "failed"
                    warnings.append("MarkItDown CLI produced an empty Markdown file.")
                    markdown_char_count = 0

    report = MarkdownExtractionReport(
        schema_version=MARKDOWN_EXTRACTION_SCHEMA_VERSION,
        tool=tool_label,
        tool_version=tool_version,
        source_pdf=str(pdf_path),
        source_pdf_sha256=digest,
        markdown_path=str(markdown_path),
        command=used_command,
        created_at=datetime.now(UTC).isoformat(),
        status=status,
        markdown_char_count=markdown_char_count,
        warnings=warnings,
    )
    report_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def find_markitdown_command(start_dir: Path | None = None) -> MarkItDownCommand | None:
    env_command = os.environ.get("MARKITDOWN_CMD")
    if env_command and env_command.strip():
        return MarkItDownCommand(command=split_command(env_command), label="MARKITDOWN_CMD")

    for root in candidate_project_roots(start_dir):
        for relative in (
            Path(".venv-markitdown") / "Scripts" / "markitdown",
            Path(".venv-markitdown") / "Scripts" / "markitdown.exe",
            Path(".venv-markitdown") / "bin" / "markitdown",
        ):
            candidate = root / relative
            if candidate.exists():
                return MarkItDownCommand(command=[str(candidate)], label="project .venv-markitdown")

    path_command = shutil.which("markitdown")
    if path_command:
        return MarkItDownCommand(command=[path_command], label="PATH")
    return None


def candidate_project_roots(start_dir: Path | None = None) -> list[Path]:
    roots: list[Path] = []
    candidates: list[Path] = []
    if start_dir:
        resolved = start_dir.resolve()
        candidates.extend([resolved, *resolved.parents])
    candidates.append(Path.cwd())
    for root in candidates:
        if root not in roots:
            roots.append(root)
    return roots


def split_command(value: str) -> list[str]:
    import shlex

    return shlex.split(value, posix=os.name != "nt") or [value]


def markitdown_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(
            [*command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (result.stdout or result.stderr).strip()
    return text[:200] or None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
