import hashlib
import json

from intl_exam_guide.rendering.visual_assets import load_visual_manifest
from intl_exam_guide.visuals import VisualSpec
from intl_exam_guide.visuals.manifest import build_visual_manifest_v2


def sample_visual_spec() -> VisualSpec:
    return VisualSpec(
        visual_id="visual_001",
        topic_title="Statistics chart",
        focus_point="draw a bar chart",
        trigger="simple chart",
        visual_type="statistics chart",
        complexity="svg-basic",
        renderer_id="kroki",
        prompt="Draw a simple chart.",
        source_points=("draw a bar chart",),
        source_pages=(8,),
        source_terms=("bar chart",),
    )


def test_build_visual_manifest_v2_generates_contract_and_asset_metadata(tmp_path):
    spec = sample_visual_spec()
    asset_path = tmp_path / "visual_001.svg"
    asset_bytes = b'<svg width="640" height="360"></svg>'
    asset_path.write_bytes(asset_bytes)

    manifest = build_visual_manifest_v2(
        [spec],
        assets={spec.visual_id: asset_path},
        review_status={spec.visual_id: "draft"},
    )

    assert manifest["schema_version"] == 2
    assert len(manifest["visuals"]) == 1

    entry = manifest["visuals"][0]
    assert entry["visual_id"] == "visual_001"
    assert entry["id"] == "visual_001"
    assert entry["spec_hash"] == spec.spec_hash()
    assert entry["renderer_id"] == "kroki"
    assert entry["review_status"] == "draft"
    assert entry["asset_status"] == "svg-draft"
    assert entry["file"] == "visual_001.svg"
    assert entry["topic_title"] == "Statistics chart"
    assert entry["source_pages"] == [8]
    assert entry["asset"] == {
        "file": "visual_001.svg",
        "media_type": "image/svg+xml",
        "byte_size": len(asset_bytes),
        "sha256": hashlib.sha256(asset_bytes).hexdigest(),
        "width": 640,
        "height": 360,
    }


def test_load_visual_manifest_accepts_v2_and_legacy_list(tmp_path):
    spec = sample_visual_spec()
    manifest = build_visual_manifest_v2([spec])
    manifest_path = tmp_path / "visual_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert load_visual_manifest(manifest_path) == manifest["visuals"]

    legacy_entries = [{"id": "visual_legacy", "file": "legacy.svg"}]
    manifest_path.write_text(json.dumps(legacy_entries), encoding="utf-8")

    assert load_visual_manifest(manifest_path) == legacy_entries
