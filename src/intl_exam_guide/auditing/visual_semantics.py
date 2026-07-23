from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any


SEMANTIC_CONTRACT_SCHEMA_VERSION = "v1-visual-semantic-contract"
TEXT_ONLY_ROUTES = {"text-ok", "none"}
RECT_TEXT_KINDS = {
    "bar-chart",
    "chart",
    "comparison-table",
    "data-visualization",
    "heatmap",
    "histogram",
    "matrix",
    "table",
    "timeline",
}
NON_EXPLANATORY_KINDS = {"flashcard", "summary-card", "text-card"}
GEOMETRY_TAGS = {"circle", "ellipse", "line", "path", "polygon", "polyline"}
CONNECTOR_TAGS = {"line", "path", "polygon", "polyline"}


def visual_semantic_issues(
    entry: dict[str, Any], images_dir: Path | None = None
) -> list[dict[str, str]]:
    route = _route(entry)
    if route in TEXT_ONLY_ROUTES:
        return []
    visual_id = str(entry.get("visual_id") or entry.get("id") or "unknown visual")
    contract = entry.get("semantic_contract")
    if not isinstance(contract, dict):
        return [
            _issue(
                "visual.semantic_contract_missing",
                f"{visual_id} has no Writer-authored visual semantic contract.",
            )
        ]
    issues = _contract_issues(visual_id, contract)
    if route == "exact-svg" and images_dir is not None:
        filename = str(entry.get("file") or "").strip()
        if filename.lower().endswith(".svg"):
            path = images_dir / filename
            if path.is_file():
                issues.extend(_exact_svg_issues(visual_id, path, contract))
    return issues


def _contract_issues(visual_id: str, contract: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if contract.get("schema_version") != SEMANTIC_CONTRACT_SCHEMA_VERSION:
        issues.append(
            _issue(
                "visual.semantic_contract_schema",
                f"{visual_id} semantic contract has an unsupported schema_version.",
            )
        )
    for field in ["learning_claim", "intended_inference"]:
        if len(str(contract.get(field) or "").strip()) < 8:
            issues.append(
                _issue(
                    "visual.semantic_contract_incomplete",
                    f"{visual_id} semantic contract requires {field}.",
                )
            )
    if not str(contract.get("visual_kind") or "").strip():
        issues.append(
            _issue(
                "visual.semantic_contract_incomplete",
                f"{visual_id} semantic contract requires visual_kind.",
            )
        )
    for field in [
        "required_elements",
        "required_relationships",
        "required_labels",
        "forbidden_misconceptions",
    ]:
        values = contract.get(field)
        if not isinstance(values, list) or not any(str(value).strip() for value in values):
            issues.append(
                _issue(
                    "visual.semantic_contract_incomplete",
                    f"{visual_id} semantic contract requires non-empty {field}.",
                )
            )
    return issues


def _exact_svg_issues(
    visual_id: str, path: Path, contract: dict[str, Any]
) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ET.ParseError):
        return [
            _issue("visual.svg_invalid", f"{visual_id} exact-SVG asset is not valid XML.")
        ]
    elements = list(root.iter())
    tags = {_local_name(element.tag) for element in elements}
    visual_kind = str(contract.get("visual_kind") or "").strip().lower()
    issues: list[dict[str, str]] = []
    if visual_kind in NON_EXPLANATORY_KINDS or (
        not tags.intersection(GEOMETRY_TAGS) and visual_kind not in RECT_TEXT_KINDS
    ):
        issues.append(
            _issue(
                "visual.svg_text_card",
                f"{visual_id} exact-SVG contains only text/rectangular layout and is not an explanatory diagram.",
            )
        )
    if visual_kind in {"process", "feedback-loop"}:
        connectors = [
            element
            for element in elements
            if _local_name(element.tag) in CONNECTOR_TAGS
        ]
        directional = any(
            element.get("marker-start") or element.get("marker-end") for element in connectors
        ) or "marker" in tags
        if not connectors or not directional:
            issues.append(
                _issue(
                    "visual.svg_direction_missing",
                    f"{visual_id} process/feedback SVG has no explicit directional connector.",
                )
            )
    return issues


def _route(entry: dict[str, Any]) -> str:
    recommended = entry.get("recommended_route")
    if not isinstance(recommended, dict):
        return ""
    return str(recommended.get("route") or "").strip().lower()


def _local_name(tag: object) -> str:
    return str(tag).rsplit("}", 1)[-1].lower()


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}
