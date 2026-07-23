from __future__ import annotations

import hashlib
import re
import unicodedata

from intl_exam_guide.models import Topic


def stable_requirement_id(topic: Topic) -> str:
    """Return a deterministic ID for a topic and its source-bound requirements."""

    parts = [topic.title.strip(), *[point.strip() for point in topic.points]]
    parts.extend(
        f"{snippet.page}:{snippet.text.strip()}" for snippet in topic.source_snippets
    )
    basis = unicodedata.normalize("NFC", "\n".join(parts))
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"requirement-{digest}"


def normalized_identifier_text(value: str) -> str:
    text = unicodedata.normalize("NFC", value).strip().casefold()
    return re.sub(r"\s+", " ", text)
