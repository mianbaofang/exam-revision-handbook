from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from intl_exam_guide.visuals.manifest import build_asset_metadata  # noqa: E402


VISUAL_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
REPLACEABLE_STATUSES = {
    "external-generation-required",
    "infographic-provider-required",
    "provider-selected-pending-generation",
    "svg-fallback-needs-review",
    "professional-diagram-required",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import reviewed visual assets into visual_manifest.json."
    )
    parser.add_argument("output_dir", help="A generated guide output directory.")
    parser.add_argument(
        "--asset-dir",
        required=True,
        help="Directory containing generated/reviewed assets named with manifest IDs, e.g. visual_001.png or visual_001.svg.",
    )
    parser.add_argument("--provider", default="external-provider")
    parser.add_argument("--status", default="reviewed-generated")
    parser.add_argument("--force", action="store_true", help="Replace existing generated files.")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Do not fail when some pending infographic IDs have no matching image.",
    )
    parser.add_argument(
        "--print-finalize-command",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Print the handbook review command after a successful import.",
    )
    parser.add_argument(
        "--rerender",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Re-render guide.html and section files after importing assets.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    asset_dir = Path(args.asset_dir).resolve()
    images_dir = output_dir / "images"
    manifest_path = images_dir / "visual_manifest.json"
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}", file=sys.stderr)
        return 1
    if not asset_dir.is_dir():
        print(f"asset directory not found: {asset_dir}", file=sys.stderr)
        return 1

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = manifest_entries_from_payload(manifest_payload)
    if manifest is None:
        print(
            "visual_manifest.json must contain a list or schema_version 2 object", file=sys.stderr
        )
        return 1

    source_assets_by_key = load_source_assets_by_key(asset_dir)
    imported = 0
    missing: list[str] = []
    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("complexity") not in {
            "infographic",
            "svg-basic",
        }:
            continue
        visual_id = str(entry.get("id") or "")
        if not visual_id:
            continue
        existing_file = str(entry.get("file") or "")
        status = str(entry.get("asset_status") or "").lower()
        if (
            existing_file
            and (images_dir / existing_file).exists()
            and status not in REPLACEABLE_STATUSES
            and not args.force
        ):
            continue
        source = find_asset(asset_dir, visual_id, str(entry.get("key") or ""), source_assets_by_key)
        if not source:
            missing.append(visual_id)
            continue
        target_name = (
            source.name
            if source.stem.startswith(visual_id)
            else f"{visual_id}{source.suffix.lower()}"
        )
        target = images_dir / target_name
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        if source.name != target_name:
            entry["source_asset_file"] = source.name
        entry["file"] = target_name
        entry["asset_status"] = args.status
        entry["review_status"] = "reviewed" if "reviewed" in args.status else "generated"
        entry["asset"] = build_asset_metadata(target)
        entry["generated_by"] = args.provider
        imported += 1

    if missing and not args.allow_partial:
        print(
            json.dumps(
                {
                    "ok": False,
                    "imported": imported,
                    "missing": missing,
                    "hint": "Use --allow-partial to import only matching assets.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    write_manifest_payload(manifest_path, manifest_payload, manifest)
    rerender_result = (
        rerender_handbook(output_dir) if imported and args.rerender else {"rerendered": False}
    )
    print(
        json.dumps(
            {
                "ok": True,
                "imported": imported,
                "missing": missing,
                "manifest": str(manifest_path),
                "rerender": rerender_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.print_finalize_command:
        print(f"Imported {imported} visual asset(s).")
        if rerender_result.get("rerendered"):
            print(f"Re-rendered handbook HTML: {rerender_result.get('html')}")
        elif args.rerender:
            print(f"Re-render skipped: {rerender_result.get('reason', 'nothing imported')}")
        print("Review the updated handbook with:")
        print(f"python -m intl_exam_guide review --out {output_dir}")
    return 0


def load_source_assets_by_key(asset_dir: Path) -> dict[str, Path]:
    manifest_path = asset_dir / "visual_manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    entries = manifest_entries_from_payload(payload)
    if not isinstance(entries, list):
        return {}
    assets: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key") or "")
        filename = str(entry.get("file") or "")
        if not key or not filename:
            continue
        source = asset_dir / filename
        if source.is_file() and source.suffix.lower() in VISUAL_ASSET_EXTENSIONS:
            assets.setdefault(key, source)
    return assets


def manifest_entries_from_payload(payload: object) -> list[dict[str, object]] | None:
    if isinstance(payload, dict) and payload.get("schema_version") == 2:
        visuals = payload.get("visuals")
        if isinstance(visuals, list):
            return [entry for entry in visuals if isinstance(entry, dict)]
        return None
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    return None


def write_manifest_payload(
    manifest_path: Path,
    original_payload: object,
    entries: list[dict[str, object]],
) -> None:
    if isinstance(original_payload, dict) and original_payload.get("schema_version") == 2:
        payload = dict(original_payload)
        payload["visuals"] = entries
    else:
        payload = entries
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def find_asset(
    asset_dir: Path,
    visual_id: str,
    visual_key: str = "",
    source_assets_by_key: dict[str, Path] | None = None,
) -> Path | None:
    candidates = [
        path
        for path in asset_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in VISUAL_ASSET_EXTENSIONS
        and (path.stem == visual_id or path.stem.startswith(f"{visual_id}_"))
    ]
    if candidates:
        return sorted(candidates)[0]
    if visual_key and source_assets_by_key:
        return source_assets_by_key.get(visual_key)
    return None


def rerender_handbook(output_dir: Path) -> dict[str, object]:
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        return {"rerendered": False, "reason": "missing guide-plan.json"}
    try:
        from intl_exam_guide.models import GuidePlan
        from intl_exam_guide.rendering.handbook_package import write_handbook_package
        from intl_exam_guide.rendering.html import render_html
        from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf

        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))
        write_handbook_package(plan, output_dir)
        html_path = render_html(
            plan,
            output_dir / "guide.html",
            output_dir / "images" / "visual_manifest.json",
        )
        result: dict[str, object] = {
            "rerendered": True,
            "html": str(html_path),
            "sections": str(output_dir / "sections"),
        }
        pdf_path = output_dir / "guide.pdf"
        if pdf_path.exists():
            try:
                export_pdf(html_path, pdf_path)
                result["pdf"] = str(pdf_path)
            except PdfExportError as exc:
                result["pdf_error"] = str(exc)
        return result
    except Exception as exc:  # pragma: no cover - defensive script boundary
        return {"rerendered": False, "reason": str(exc)}


if __name__ == "__main__":
    raise SystemExit(main())
