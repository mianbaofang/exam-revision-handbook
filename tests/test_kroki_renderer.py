from __future__ import annotations

from pathlib import Path
from typing import Any

from intl_exam_guide.models import VisualBrief
from intl_exam_guide.rendering.kroki import (
    kroki_graphviz_source,
    normalize_kroki_svg_title,
    render_kroki_svg_asset,
)


def brief(visual_type: str, focus: str = "source evidence") -> VisualBrief:
    return VisualBrief(
        topic_title="Topic title",
        focus_point=focus,
        trigger="Writer selected a professional diagram route.",
        visual_type=visual_type,
        complexity="svg-basic",
        image_provider="kroki",
        prompt="",
        source_points=[focus],
    )


def test_render_kroki_svg_asset_posts_graphviz_source(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    calls: dict[str, object] = {}

    class FakeResponse:
        headers = {"Content-Type": "image/svg+xml"}

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'<?xml version="1.0"?><svg><text>Reviewed Flow</text></svg>'

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        calls["url"] = request.full_url
        calls["method"] = request.get_method()
        calls["data"] = request.data
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "intl_exam_guide.rendering.kroki.urllib.request.urlopen",
        fake_urlopen,
    )
    visual = brief("source evidence to reviewed conclusion flow", "source point and check")

    output_path = tmp_path / "visual.svg"
    render_kroki_svg_asset(visual, output_path, base_url="https://kroki.test", timeout=3)

    assert calls["url"] == "https://kroki.test/graphviz/svg"
    assert calls["method"] == "POST"
    assert b"Source Evidence To Review" in calls["data"]
    assert b"digraph G" not in calls["data"]
    assert b"digraph Source_Evidence_To_Review" in calls["data"]
    assert b"Source Evidence To Review" in calls["data"]
    assert calls["timeout"] == 3
    assert output_path.read_text(encoding="utf-8").startswith("<?xml")


def test_kroki_graphviz_uses_hierarchy_layout_for_structure_keyword() -> None:
    source = kroki_graphviz_source(brief("topic structure hierarchy", "reporting lines"))

    assert "rankdir=TB" in source
    assert "n1 -> n2" in source
    assert "n2 -> n3" in source
    assert "n2 -> n4" in source


def test_kroki_graphviz_uses_star_map_for_influence_map_keyword() -> None:
    source = kroki_graphviz_source(brief("influence map", "decision and groups"))

    assert "Influence" in source
    assert "n1 -> n2 [dir=both]" in source
    assert "n1 -> n5 [dir=both]" in source


def test_kroki_graphviz_uses_checkpoint_loop() -> None:
    source = kroki_graphviz_source(brief("checkpoint loop", "standard check improve process"))

    assert "Checkpoint Loop" in source
    assert "n4 -> n2" in source
    assert 'label="improve"' in source


def test_kroki_graphviz_uses_comparison_clusters() -> None:
    source = kroki_graphviz_source(brief("comparison", "option A option B evidence"))

    assert "subgraph cluster_left" in source
    assert "subgraph cluster_right" in source
    assert 'label="compare"' in source


def test_kroki_graphviz_uses_reconciliation_shape_for_verify_keyword() -> None:
    source = kroki_graphviz_source(brief("verify and match evidence", "source one source two difference"))

    assert "n1 -> n3" in source
    assert "n2 -> n3" in source
    assert "n3 -> n4" in source


def test_normalize_kroki_svg_title_replaces_graphviz_id_title() -> None:
    payload = b'<svg><title>G</title><g id="node1"></g></svg>'

    normalized = normalize_kroki_svg_title(payload, "Reviewed Flow - Topic")

    assert b"<title>Reviewed Flow - Topic</title>" in normalized
    assert b"<title>G</title>" not in normalized
