from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re

from intl_exam_guide.models import Qualification


def default_handbook_stem(
    qualification: Qualification,
    timestamp: datetime | str | None = None,
) -> str:
    """Return the default board-level-subject-time file stem for rendered handbooks."""

    return "-".join(
        part
        for part in [
            board_slug(qualification),
            level_slug(qualification),
            subject_slug(qualification),
            timestamp_slug(timestamp),
        ]
        if part
    )


def default_handbook_paths(
    output_dir: Path,
    qualification: Qualification,
    timestamp: datetime | str | None = None,
) -> tuple[Path, Path]:
    stem = default_handbook_stem(qualification, timestamp)
    return output_dir / f"{stem}.html", output_dir / f"{stem}.pdf"


def find_handbook_html(output_dir: Path, qualification: Qualification | None = None) -> Path:
    path = path_from_validation(output_dir, "html")
    if path:
        return path
    legacy = output_dir / "guide.html"
    if legacy.exists():
        return legacy
    candidates = sorted(output_dir.glob("*.html"), key=lambda item: item.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    if qualification:
        return default_handbook_paths(output_dir, qualification)[0]
    return legacy


def find_handbook_pdf(output_dir: Path, qualification: Qualification | None = None) -> Path:
    path = path_from_validation(output_dir, "pdf")
    if path:
        return path
    legacy = output_dir / "guide.pdf"
    if legacy.exists():
        return legacy
    candidates = sorted(output_dir.glob("*.pdf"), key=lambda item: item.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    if qualification:
        return default_handbook_paths(output_dir, qualification)[1]
    return legacy


def path_from_validation(output_dir: Path, key: str) -> Path | None:
    validation_path = output_dir / "validation.json"
    if not validation_path.exists():
        return None
    try:
        payload = json.loads(validation_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    value = payload.get(key) if isinstance(payload, dict) else None
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = output_dir / path
    return path if path.exists() else None


def board_slug(qualification: Qualification) -> str:
    provider = " ".join(
        value
        for value in [
            qualification.provider,
            qualification.source.provider,
            qualification.qualification_family,
        ]
        if value
    )
    lowered = provider.lower()
    if "oxford" in lowered or "aqa" in lowered:
        return "oxfordaqa"
    if "pearson" in lowered or "edexcel" in lowered:
        return "pearson-edexcel"
    if "cambridge" in lowered or "caie" in lowered:
        return "cambridge"
    return slugify(provider) or "exam-board"


def level_slug(qualification: Qualification) -> str:
    value = qualification.qualification_type or qualification.qualification_family or "level"
    replacements = {
        "international_gcse": "igcse",
        "gcse": "gcse",
        "igcse": "igcse",
        "international_as_a_level": "as-a-level",
        "as_a_level": "as-a-level",
        "as-level": "as-level",
        "a-level": "a-level",
        "alevel": "a-level",
    }
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    return replacements.get(normalized, slugify(value) or "level")


def subject_slug(qualification: Qualification) -> str:
    return slugify(qualification.subject_area or qualification.title or "subject") or "subject"


def timestamp_slug(timestamp: datetime | str | None = None) -> str:
    if timestamp is None:
        return datetime.now().strftime("%Y%m%d-%H%M")
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y%m%d-%H%M")
    return slugify(timestamp) or datetime.now().strftime("%Y%m%d-%H%M")


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
