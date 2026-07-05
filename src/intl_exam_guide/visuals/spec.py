from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from intl_exam_guide.models import VisualBrief


@dataclass(frozen=True)
class VisualSpec:
    visual_id: str
    topic_title: str
    focus_point: str
    trigger: str
    visual_type: str
    complexity: str
    renderer_id: str
    prompt: str
    source_points: tuple[str, ...] = field(default_factory=tuple)
    source_pages: tuple[int, ...] = field(default_factory=tuple)
    source_terms: tuple[str, ...] = field(default_factory=tuple)
    svg_fit: str = ""

    @classmethod
    def from_brief(cls, brief: VisualBrief, visual_id: str) -> "VisualSpec":
        snippets = tuple(brief.source_snippets)
        return cls(
            visual_id=visual_id,
            topic_title=brief.topic_title,
            focus_point=brief.focus_point,
            trigger=brief.trigger,
            visual_type=brief.visual_type,
            complexity=brief.complexity,
            renderer_id=brief.image_provider,
            prompt=brief.prompt,
            source_points=tuple(brief.source_points),
            source_pages=tuple(snippet.page for snippet in snippets),
            source_terms=tuple(snippet.matched_term for snippet in snippets),
            svg_fit=str(getattr(brief, "svg_fit", "") or ""),
        )

    def spec_hash(self) -> str:
        return spec_hash(self)

    def hash_payload(self) -> dict[str, Any]:
        return {
            "topic_title": self.topic_title,
            "focus_point": self.focus_point,
            "trigger": self.trigger,
            "visual_type": self.visual_type,
            "complexity": self.complexity,
            "prompt": self.prompt,
            "svg_fit": self.svg_fit,
            "source_points": list(self.source_points),
            "source_pages": list(self.source_pages),
            "source_terms": list(self.source_terms),
        }


def spec_hash(spec: VisualSpec) -> str:
    payload = json.dumps(
        spec.hash_payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
