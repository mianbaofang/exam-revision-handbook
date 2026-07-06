from __future__ import annotations

import base64
import html
import os
import re
import urllib.error
import urllib.request
import zlib
from pathlib import Path

from intl_exam_guide.models import VisualBrief

DEFAULT_KROKI_BASE_URL = "https://kroki.io"


class KrokiRenderError(RuntimeError):
    pass


def render_kroki_svg_asset(
    brief: VisualBrief,
    output_path: Path,
    *,
    base_url: str | None = None,
    timeout: float | None = None,
) -> None:
    source = kroki_graphviz_source(brief)
    url = kroki_post_url(
        diagram_type="graphviz",
        output_format="svg",
        base_url=base_url or os.environ.get("KROKI_BASE_URL") or DEFAULT_KROKI_BASE_URL,
    )
    request = urllib.request.Request(
        url,
        data=source.encode("utf-8"),
        method="POST",
        headers={
            "Accept": "image/svg+xml",
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": "intl-exam-guide/0.4",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout or kroki_timeout()) as response:
            content_type = response.headers.get("Content-Type", "")
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise KrokiRenderError(str(exc)) from exc
    if b"<svg" not in payload[:500].lower() and "svg" not in content_type.lower():
        raise KrokiRenderError(f"Kroki returned non-SVG response: {content_type or 'unknown'}")
    payload = normalize_kroki_svg_title(payload, topic_specific_diagram_title(brief))
    output_path.write_bytes(payload)


def normalize_kroki_svg_title(payload: bytes, title: str) -> bytes:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload
    replacement = f"<title>{html.escape(short_label(title, 90))}</title>"
    if re.search(r"<title\b[^>]*>.*?</title>", text, flags=re.I | re.S):
        text = re.sub(r"<title\b[^>]*>.*?</title>", replacement, text, count=1, flags=re.I | re.S)
    else:
        text = re.sub(r"(<svg\b[^>]*>)", rf"\1{replacement}", text, count=1, flags=re.I | re.S)
    return text.encode("utf-8")


def kroki_url(
    source: str,
    *,
    diagram_type: str,
    output_format: str,
    base_url: str = DEFAULT_KROKI_BASE_URL,
) -> str:
    return f"{base_url.rstrip('/')}/{diagram_type}/{output_format}/{encode_kroki_source(source)}"


def kroki_post_url(
    *,
    diagram_type: str,
    output_format: str,
    base_url: str = DEFAULT_KROKI_BASE_URL,
) -> str:
    return f"{base_url.rstrip('/')}/{diagram_type}/{output_format}"


def encode_kroki_source(source: str) -> str:
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(source.encode("utf-8")) + compressor.flush()
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def kroki_timeout() -> float:
    try:
        return max(1.0, float(os.environ.get("KROKI_TIMEOUT_SECONDS", "12")))
    except ValueError:
        return 12.0


def kroki_graphviz_source(brief: VisualBrief) -> str:
    labels = professional_diagram_labels(brief)
    title = short_label(topic_specific_diagram_title(brief), 64)
    family = kroki_diagram_family(brief)
    if family == "hierarchy":
        return hierarchy_graphviz_source(title, labels)
    if family == "stakeholder":
        return stakeholder_graphviz_source(title, labels)
    if family == "segmentation":
        return segmentation_graphviz_source(title, labels)
    if family == "checkpoint":
        return checkpoint_graphviz_source(title, labels)
    if family == "timeline":
        return timeline_graphviz_source(title, labels)
    if family == "comparison":
        return comparison_graphviz_source(title, labels)
    if family == "reconciliation":
        return reconciliation_graphviz_source(title, labels)
    if family == "cause":
        return cause_graphviz_source(title, labels)
    return flow_graphviz_source(title, labels)


def base_graph_header(title: str, *, rankdir: str = "LR") -> str:
    return (
        f"digraph {graphviz_identifier(title)} {{\n"
        f'  graph [rankdir={rankdir}, bgcolor="transparent", pad="0.25", nodesep="0.45", '
        f'ranksep="0.55", label="{escape_dot_label(title)}", labelloc=t, fontsize=22, fontname="Arial Bold"];\n'
        '  node [shape=box, style="rounded,filled", fillcolor="#F7FBFF", color="#1354A5", '
        'penwidth=2.4, fontname="Arial", fontsize=18, margin="0.14,0.09"];\n'
        '  edge [color="#172033", penwidth=2.2, arrowsize=0.8, fontname="Arial", fontsize=12];\n'
    )


def graphviz_identifier(title: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]+", "_", title).strip("_")
    if not identifier or identifier[0].isdigit():
        identifier = f"Guide_{identifier}"
    return identifier[:48]


def flow_graphviz_source(title: str, labels: list[str]) -> str:
    nodes = "\n".join(
        f'  n{index} [label="{escape_dot_label(label)}"];'
        for index, label in enumerate(labels, start=1)
    )
    edges = "\n".join(f"  n{index} -> n{index + 1};" for index in range(1, len(labels)))
    return f"{base_graph_header(title)}{nodes}\n{edges}\n}}"


def hierarchy_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title, rankdir="TB")}  n1 [label="{escape_dot_label(labels[0])}", fillcolor="#EAF3FF"];
  n2 [label="{escape_dot_label(labels[1])}"];
  n3 [label="{escape_dot_label(labels[2])}"];
  n4 [label="{escape_dot_label(labels[3])}"];
  n1 -> n2;
  n2 -> n3;
  n2 -> n4;
}}"""


def stakeholder_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 5)
    node_lines = []
    for index, label in enumerate(labels, start=1):
        extra = ', shape=ellipse, fillcolor="#FFF8EA"' if index == 1 else ""
        node_lines.append(f'  n{index} [label="{escape_dot_label(label)}"{extra}];')
    nodes = "\n".join(node_lines)
    edges = "\n".join(f"  n1 -> n{index} [dir=both];" for index in range(2, len(labels) + 1))
    return f"{base_graph_header(title)}{nodes}\n{edges}\n}}"


def segmentation_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title, rankdir="TB")}  n1 [label="{escape_dot_label(labels[0])}", shape=ellipse, fillcolor="#FFF8EA"];
  n2 [label="{escape_dot_label(labels[1])}", fillcolor="#EAF3FF"];
  n3 [label="{escape_dot_label(labels[2])}", fillcolor="#EAF8F1"];
  n4 [label="{escape_dot_label(labels[3])}", fillcolor="#FFF1F3"];
  n1 -> n2 [label="needs"];
  n1 -> n3 [label="segments"];
  n2 -> n4 [style=dashed, label="target"];
  n3 -> n4 [style=dashed, label="message"];
}}"""


def checkpoint_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title)}  n1 [label="{escape_dot_label(labels[0])}"];
  n2 [label="{escape_dot_label(labels[1])}", fillcolor="#FFF8EA"];
  n3 [label="{escape_dot_label(labels[2])}", fillcolor="#EAF8F1"];
  n4 [label="{escape_dot_label(labels[3])}", fillcolor="#FFF1F3"];
  n1 -> n2 [label="standard"];
  n2 -> n3 [label="inspect"];
  n3 -> n4 [label="feedback"];
  n4 -> n2 [style=dashed, label="improve"];
}}"""


def timeline_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    nodes = "\n".join(
        f'  n{index} [label="{escape_dot_label(label)}", shape=box];'
        for index, label in enumerate(labels, start=1)
    )
    edges = "\n".join(
        f'  n{index} -> n{index + 1} [label="{label}"];'
        for index, label in enumerate(["then", "turning point", "leads to"], start=1)
    )
    return f"{base_graph_header(title)}{nodes}\n{edges}\n}}"


def comparison_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title)}  subgraph cluster_left {{
    label="Option A";
    color="#D7DEEA";
    n1 [label="{escape_dot_label(labels[0])}"];
    n2 [label="{escape_dot_label(labels[1])}"];
  }}
  subgraph cluster_right {{
    label="Option B";
    color="#D7DEEA";
    n3 [label="{escape_dot_label(labels[2])}"];
    n4 [label="{escape_dot_label(labels[3])}"];
  }}
  n2 -> n4 [style=dashed, label="compare"];
}}"""


def reconciliation_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title)}  n1 [label="{escape_dot_label(labels[0])}"];
  n2 [label="{escape_dot_label(labels[1])}"];
  n3 [label="{escape_dot_label(labels[2])}", fillcolor="#FFF8EA"];
  n4 [label="{escape_dot_label(labels[3])}", fillcolor="#EAF8F1"];
  n1 -> n3;
  n2 -> n3;
  n3 -> n4;
}}"""


def cause_graphviz_source(title: str, labels: list[str]) -> str:
    labels = pad_labels(labels, 4)
    return f"""{base_graph_header(title)}  n1 [label="{escape_dot_label(labels[0])}"];
  n2 [label="{escape_dot_label(labels[1])}"];
  n3 [label="{escape_dot_label(labels[2])}", fillcolor="#FFF8EA"];
  n4 [label="{escape_dot_label(labels[3])}"];
  n1 -> n3 [label="background"];
  n2 -> n3 [label="trigger"];
  n3 -> n4 [label="consequence"];
}}"""


def kroki_diagram_family(brief: VisualBrief) -> str:
    text = " ".join([brief.visual_type, brief.focus_point, *brief.source_points]).lower()
    if "hierarchy" in text or "structure" in text:
        return "hierarchy"
    if "star" in text or "influence map" in text:
        return "stakeholder"
    if "checkpoint" in text or "loop" in text:
        return "checkpoint"
    if "timeline" in text or "chronology" in text:
        return "timeline"
    if "comparison" in text or "compare" in text:
        return "comparison"
    if "reconciliation" in text or "match" in text or "verify" in text:
        return "reconciliation"
    if "cause and consequence" in text or ("cause" in text and "consequence" in text):
        return "cause"
    return "flow"


def pad_labels(labels: list[str], minimum: int) -> list[str]:
    fallback = ["Key idea", "Relationship", "Evidence", "Exam answer", "Check"]
    values = [label for label in labels if label]
    while len(values) < minimum:
        values.append(fallback[len(values) % len(fallback)])
    return values


def professional_diagram_title(brief: VisualBrief) -> str:
    title = split_visual_labels(brief.visual_type)
    if title:
        return title[0]
    return brief.focus_point or brief.topic_title or "Professional Diagram"


def topic_specific_diagram_title(brief: VisualBrief) -> str:
    base = professional_diagram_title(brief)
    topic = re.sub(r"^\s*\d+(?:\.\d+)*\s*[-:]\s*", "", brief.topic_title).strip()
    if not topic:
        return base
    return f"{base} - {topic}"


def professional_diagram_labels(brief: VisualBrief) -> list[str]:
    labels = split_visual_labels("; ".join([brief.visual_type, brief.focus_point, *brief.source_points]))
    return labels[:5] if len(labels) >= 3 else ["Key idea", "Relationship", "Evidence", "Exam answer"]


def split_visual_labels(value: str) -> list[str]:
    text = re.sub(r"\b(diagram|visual|flow|map|workflow|comparison)\b", " ", value, flags=re.I)
    chunks = [chunk.strip(" -_/") for chunk in re.split(r"\band\b|,|->|;", text) if chunk.strip()]
    labels = [short_label(chunk.title(), 28) for chunk in chunks]
    return [label for label in labels if label]


def short_label(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def escape_dot_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
