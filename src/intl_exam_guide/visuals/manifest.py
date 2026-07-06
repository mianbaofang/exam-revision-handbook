from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from intl_exam_guide.visuals.spec import VisualSpec

# Keep the outer file format v2-compatible for existing import/render tooling while
# adding the v0.5 split contract inside each entry.  In v0.5, ``complexity`` remains
# a legacy route hint; the actual rendered handbook asset lives under
# ``rendered_asset``.
SCHEMA_VERSION = 2
VISUAL_CONTRACT = "v0.5-visual-route-asset-split"

PENDING_WORKFLOW_STATUSES = {
    "external-generation-required",
    "infographic-provider-required",
    "provider-selected-pending-generation",
    "llm-svg-required",
    "svg-fallback-needs-review",
    "professional-diagram-required",
}
GENERATED_WORKFLOW_STATUSES = {
    "generated",
    "reviewed",
    "reviewed-generated",
    "provider-selected-generated",
    "sensenova-generated",
}
REVIEWED_STATUSES = {"reviewed", "approved"}
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def build_visual_manifest_v2(
    specs: Sequence[VisualSpec],
    *,
    assets: Mapping[str, str | Path | None] | None = None,
    review_status: str | Mapping[str, str] = "pending",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "visual_contract": VISUAL_CONTRACT,
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
    entry: dict[str, Any] = {
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
        # Legacy route fields kept for existing scripts.  These are not proof that
        # the PDF contains an image.
        "complexity": spec.complexity,
        "image_provider": spec.renderer_id,
        "prompt": spec.prompt,
        "svg_fit": spec.svg_fit,
        "source_points": list(spec.source_points),
        "source_pages": list(spec.source_pages),
        "visual_need": build_visual_need(spec),
        "recommended_route": build_recommended_route(spec),
    }
    return sync_visual_manifest_entry(entry)


def build_visual_need(spec: VisualSpec) -> dict[str, Any]:
    return {
        "learning_claim": spec.trigger
        or f"Help students see the structure behind {spec.focus_point}.",
        "visual_teaching_value": "student-preview",
        "source_points": list(spec.source_points),
        "source_pages": list(spec.source_pages),
        "reviewer_visual_decision": "pending",
        "no_visual_reason": "",
    }


def build_recommended_route(spec: VisualSpec) -> dict[str, Any]:
    route = recommended_route_name(spec.complexity, spec.renderer_id)
    return {
        "route": route,
        "legacy_complexity": spec.complexity,
        "renderer_id": spec.renderer_id,
        "svg_fit": spec.svg_fit,
        "route_status": "recommended",
        "reason": spec.trigger,
    }


def sync_visual_manifest_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Populate v0.5 nested visual fields from the legacy flat manifest fields."""

    route = entry.get("recommended_route") if isinstance(entry.get("recommended_route"), dict) else {}
    legacy_complexity = str(route.get("legacy_complexity") or entry.get("complexity") or "")
    renderer_id = str(route.get("renderer_id") or entry.get("renderer_id") or entry.get("image_provider") or "")
    route_name = str(route.get("route") or recommended_route_name(legacy_complexity, renderer_id))
    route = {
        **route,
        "route": route_name,
        "legacy_complexity": legacy_complexity,
        "renderer_id": renderer_id,
        "svg_fit": str(route.get("svg_fit") or entry.get("svg_fit") or ""),
        "route_status": str(route.get("route_status") or "recommended"),
        "reason": str(route.get("reason") or entry.get("trigger") or ""),
    }
    entry["recommended_route"] = route

    asset = entry.get("asset") if isinstance(entry.get("asset"), dict) else {}
    file_name = str(entry.get("file") or asset.get("file") or "") or None
    workflow_asset_status = str(entry.get("asset_status") or "").lower()
    review_status = str(entry.get("review_status") or "pending").lower()
    rendered_asset = (
        entry.get("rendered_asset") if isinstance(entry.get("rendered_asset"), dict) else {}
    )
    rendered_asset = {
        **rendered_asset,
        "file": file_name,
        "media_type": asset.get("media_type"),
        "byte_size": asset.get("byte_size"),
        "sha256": asset.get("sha256"),
        "width": asset.get("width"),
        "height": asset.get("height"),
        "asset_route": rendered_asset_route(file_name, route_name, workflow_asset_status),
        "asset_status": actual_asset_status(file_name, workflow_asset_status, review_status),
        "review_status": review_status,
        "renders_in_html": renders_in_html(file_name, workflow_asset_status),
        "rendered_as": rendered_as(file_name, workflow_asset_status),
    }
    entry["rendered_asset"] = rendered_asset

    visual_need = entry.get("visual_need") if isinstance(entry.get("visual_need"), dict) else {}
    entry["visual_need"] = {
        "learning_claim": str(
            visual_need.get("learning_claim")
            or entry.get("trigger")
            or f"Help students understand {entry.get('focus_point') or entry.get('topic_title') or 'this topic'}."
        ),
        "visual_teaching_value": str(visual_need.get("visual_teaching_value") or "student-preview"),
        "source_points": list_or_empty(visual_need.get("source_points") or entry.get("source_points")),
        "source_pages": list_or_empty(visual_need.get("source_pages") or entry.get("source_pages")),
        "reviewer_visual_decision": str(
            visual_need.get("reviewer_visual_decision") or "pending"
        ),
        "no_visual_reason": str(visual_need.get("no_visual_reason") or ""),
    }

    entry["workflow_state"] = {
        "generation_state": generation_state(workflow_asset_status, file_name),
        "review_state": review_status,
        "delivery_blocker": delivery_blocker(workflow_asset_status, rendered_asset, review_status),
    }
    return entry


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


def recommended_route_name(complexity: str, renderer_id: str) -> str:
    complexity_norm = complexity.strip().lower()
    renderer_norm = renderer_id.strip().lower()
    if complexity_norm == "svg-basic":
        if renderer_norm == "kroki":
            return "kroki-diagram"
        return "exact-svg"
    if complexity_norm in {"text-ok", "none"}:
        return "text-ok"
    return "external-infographic"


def rendered_asset_route(
    file_name: str | None,
    recommended_route: str,
    workflow_asset_status: str,
) -> str:
    if not file_name:
        return "none"
    suffix = Path(file_name).suffix.lower()
    if suffix == ".svg":
        if recommended_route == "kroki-diagram" or workflow_asset_status == "svg-fallback-needs-review":
            return "kroki-svg"
        return "llm-svg"
    if suffix in RASTER_EXTENSIONS:
        return "imported-raster"
    return "external-image"


def actual_asset_status(
    file_name: str | None,
    workflow_asset_status: str,
    review_status: str,
) -> str:
    if not file_name:
        return "missing"
    if review_status in REVIEWED_STATUSES:
        return review_status
    if workflow_asset_status in PENDING_WORKFLOW_STATUSES or workflow_asset_status.endswith("-draft"):
        return "draft"
    if workflow_asset_status in GENERATED_WORKFLOW_STATUSES:
        return "generated"
    return workflow_asset_status or "unknown"


def renders_in_html(file_name: str | None, workflow_asset_status: str) -> bool:
    if not file_name:
        return False
    return workflow_asset_status in GENERATED_WORKFLOW_STATUSES or workflow_asset_status == "svg-fallback-needs-review"


def rendered_as(file_name: str | None, workflow_asset_status: str) -> str:
    if not renders_in_html(file_name, workflow_asset_status):
        return "placeholder" if workflow_asset_status in PENDING_WORKFLOW_STATUSES else "none"
    return "img"


def generation_state(workflow_asset_status: str, file_name: str | None) -> str:
    if workflow_asset_status in GENERATED_WORKFLOW_STATUSES:
        return "generated"
    if workflow_asset_status == "svg-fallback-needs-review":
        return "needs_review"
    if workflow_asset_status in PENDING_WORKFLOW_STATUSES:
        return "queued"
    if file_name:
        return "generated"
    return "unknown"


def delivery_blocker(
    workflow_asset_status: str,
    rendered_asset: dict[str, Any],
    review_status: str,
) -> bool:
    if workflow_asset_status in PENDING_WORKFLOW_STATUSES:
        return True
    if str(rendered_asset.get("asset_route") or "").endswith("svg"):
        return review_status not in REVIEWED_STATUSES
    return False


def list_or_empty(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _status_for(review_status: str | Mapping[str, str], visual_id: str) -> str:
    if isinstance(review_status, Mapping):
        return review_status.get(visual_id, "pending")
    return review_status


def _asset_status(spec: VisualSpec, filename: str | None, review_status: str) -> str:
    if not filename:
        if spec.complexity == "svg-basic":
            return "llm-svg-required"
        return "external-generation-required"
    if review_status in REVIEWED_STATUSES:
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
