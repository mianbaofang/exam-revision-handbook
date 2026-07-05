from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from intl_exam_guide.visuals.spec import VisualSpec

SCHEMA_VERSION = 2


def build_visual_manifest_v2(
    specs: Sequence[VisualSpec],
    *,
    assets: Mapping[str, str | Path | None] | None = None,
    review_status: str | Mapping[str, str] = "pending",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "visuals": [
            build_visual_manifest_entry_v2(
                spec,
                asset_path=(assets or {}).get(spec.visual_id),
                review_status=_status_for(review_status, spec.visual_id),
            )
            for spec in specs
        ],
    }


def build_visual_manifest_entry_v2(
    spec: VisualSpec,
    *,
    asset_path: str | Path | None = None,
    review_status: str = "pending",
) -> dict[str, Any]:
    asset = build_asset_metadata(asset_path)
    asset_status = _asset_status(spec, asset["file"], review_status)
    return {
        "visual_id": spec.visual_id,
        "id": spec.visual_id,
        "spec_hash": spec.spec_hash(),
        "renderer_id": spec.renderer_id,
        "review_status": review_status,
        "asset": asset,
        "key": _legacy_key(spec),
        "file": asset["file"],
        "asset_status": asset_status,
        "topic_title": spec.topic_title,
        "focus_point": spec.focus_point,
        "trigger": spec.trigger,
        "visual_type": spec.visual_type,
        "complexity": spec.complexity,
        "image_provider": spec.renderer_id,
        "prompt": spec.prompt,
        "svg_fit": spec.svg_fit,
        "source_points": list(spec.source_points),
        "source_pages": list(spec.source_pages),
    }


def build_asset_metadata(asset_path: str | Path | None) -> dict[str, Any]:
    if asset_path is None:
        return {
            "file": None,
            "media_type": None,
            "byte_size": None,
            "sha256": None,
            "width": None,
            "height": None,
        }

    path = Path(asset_path)
    metadata: dict[str, Any] = {
        "file": path.name,
        "media_type": _media_type(path),
        "byte_size": None,
        "sha256": None,
        "width": None,
        "height": None,
    }
    if not path.exists():
        return metadata

    content = path.read_bytes()
    metadata["byte_size"] = len(content)
    metadata["sha256"] = hashlib.sha256(content).hexdigest()
    width, height = _image_dimensions(path, content)
    metadata["width"] = width
    metadata["height"] = height
    return metadata


def _status_for(review_status: str | Mapping[str, str], visual_id: str) -> str:
    if isinstance(review_status, Mapping):
        return review_status.get(visual_id, "pending")
    return review_status


def _asset_status(spec: VisualSpec, filename: str | None, review_status: str) -> str:
    if not filename:
        return "external-generation-required"
    if review_status in {"approved", "reviewed"}:
        return "reviewed-generated"
    if spec.complexity == "svg-basic" and Path(filename).suffix.lower() == ".svg":
        return "svg-draft"
    return "generated"


def _legacy_key(spec: VisualSpec) -> str:
    return "||".join(
        _normalize(value)
        for value in [
            spec.topic_title,
            spec.focus_point,
            spec.visual_type,
            spec.complexity,
        ]
    )


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _media_type(path: Path) -> str | None:
    if path.suffix.lower() == ".svg":
        return "image/svg+xml"
    media_type, _ = mimetypes.guess_type(path.name)
    return media_type


def _image_dimensions(path: Path, content: bytes) -> tuple[int | None, int | None]:
    if path.suffix.lower() == ".svg":
        text = content.decode("utf-8", errors="replace")
        return _svg_dimensions(text)
    try:
        from PIL import Image

        with Image.open(path) as image:
            return image.size
    except (ModuleNotFoundError, OSError, ValueError):
        return None, None


def _svg_dimensions(svg: str) -> tuple[int | None, int | None]:
    width = _svg_number_attr(svg, "width")
    height = _svg_number_attr(svg, "height")
    if width is not None and height is not None:
        return width, height
    viewbox = re.search(r'\bviewBox=["\']([^"\']+)["\']', svg, flags=re.I)
    if not viewbox:
        return width, height
    numbers = re.findall(r"-?\d+(?:\.\d+)?", viewbox.group(1))
    if len(numbers) < 4:
        return width, height
    return width or int(float(numbers[2])), height or int(float(numbers[3]))


def _svg_number_attr(svg: str, attr: str) -> int | None:
    match = re.search(rf'\b{attr}=["\']\s*(\d+(?:\.\d+)?)', svg, flags=re.I)
    return int(float(match.group(1))) if match else None
