from __future__ import annotations

import re

from intl_exam_guide.models import Topic


SHELL_PATTERNS = [
    r"^candidates should have an understanding of:?$",
    r"^students should be able to:?$",
    r"^learners should be able to:?$",
    r"^[a-z]\)\s*understand the significance of the following accounting$",
    r"^[a-z]\)\s*(?:explain|describe|understand|state|identify|apply|prepare|calculate)\s+(?:the\s+)?(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)?(?:\s+of)?\s*:?$",
    r"^[a-z]\)\s*(?:explain|describe|understand|state|identify|apply|prepare|calculate)\s+(?:the\s+)?[a-z ]{0,25}:$",
]

BOILERPLATE_SUFFIX_PATTERNS = [
    r"\s*Cambridge\s+(?:IGCSE|International\s+AS\s*&\s*A\s+Level)\b.+?\bSubject content\b.*$",
    r"\s*\d+\s*www\.cambridgeinternational\.org/\S*Back to contents page.*$",
    r"\s+\d+\s+[A-Z][A-Za-z ,&()'-]+\s+This topic\b.*$",
    r"\s+This topic\s+(?:considers|covers|introduces|explores)\b.*$",
    r"\s*Specification\s+-\s+Issue\b.+?Pearson Education Limited\s+\d{4}.*$",
    r"\s*Faculty feedback:.+$",
    r"\s*Feedback from:.+$",
]

BOILERPLATE_FULL_PATTERNS = [
    r"^\d+\s*www\.cambridgeinternational\.org/\S*Back to contents page$",
    r"^Cambridge\s+IGCSE\b.+?\bSubject content$",
    r"^Specification\s+-\s+Issue\b.+?Pearson Education Limited\s+\d{4}$",
    r"^\([a-z]\)\s+[a-z][a-z ,/+-]{3,80}$",
    r"^Students should:?$",
    r"^The following sub-topics are covered in this section$",
    r"^Faculty feedback:.+$",
    r"^Feedback from:.+$",
]


def visible_source_points(topic: Topic, limit: int = 5) -> list[str]:
    """Return source points suitable for student-facing guide text."""

    cleaned = [clean_source_point(point) for point in topic.points]
    visible = merge_wrapped_source_points(
        [point for point in cleaned if point and not is_syllabus_shell(point)]
    )
    if visible:
        return visible[:limit]
    title = clean_topic_title(topic.title)
    return [title] if title else [topic.title]


def normalized_student_topic(topic: Topic) -> Topic:
    """Return a copy whose title is usable as a student-facing unit title."""

    title = complete_topic_title(topic)
    points = [clean_source_point(point) for point in topic.points]
    if title == topic.title and points == topic.points:
        return topic
    return Topic(
        title=title,
        points=points,
        level_tags=topic.level_tags,
        source_snippets=topic.source_snippets,
    )


def complete_topic_title(topic: Topic) -> str:
    """Complete parser-fragment titles using the same unit's visible source points."""

    title = clean_ocr_math_text(" ".join(topic.title.split()).strip())
    if not is_incomplete_topic_title(title):
        return clean_title_shell(title)
    points = visible_source_points(topic, limit=3)
    if not points:
        return clean_title_shell(title)
    focus = clean_topic_title(title)
    completed = title_focus_from_points(focus, points)
    if not completed or completed == focus:
        return clean_title_shell(title)
    prefix = topic_title_prefix(title)
    completed_title = f"{prefix}{completed}" if prefix else completed
    return clean_title_shell(completed_title)


def clean_title_shell(title: str) -> str:
    prefix = topic_title_prefix(title)
    focus = clean_topic_title(title)
    cleaned_focus = clean_source_point(focus).strip(" .;:")
    if cleaned_focus.lower().startswith("the notation "):
        cleaned_focus = "Notation " + cleaned_focus[len("the notation ") :]
    if cleaned_focus and cleaned_focus != focus:
        return f"{prefix}{cleaned_focus}" if prefix else cleaned_focus
    return title


def is_incomplete_topic_title(title: str) -> bool:
    focus = clean_topic_title(title)
    lower = focus.lower().strip()
    if not lower:
        return True
    if "..." in lower:
        return True
    if lower.endswith((",", ";", ":")):
        return True
    tail = lower.split()[-1]
    return tail in {
        "and",
        "or",
        "of",
        "the",
        "to",
        "with",
        "form",
        "convergent",
        "subst",
        "rem",
        "repres",
        "thei",
    }


def title_focus_from_points(focus: str, points: list[str]) -> str:
    if focus.lower().strip().endswith("remainder theorem and the"):
        return focus.rstrip(" ,;:.") + " Factor Theorem"
    candidates = merge_wrapped_source_points(
        [clean_source_point(point) for point in points if point]
    )
    if not candidates:
        return focus
    focus_clean = focus.strip(" ,;:.")
    lower_focus = focus_clean.lower()
    for candidate in candidates:
        cleaned = compact_title_candidate(candidate)
        if cleaned.lower().startswith(lower_focus):
            return cleaned
    return compact_title_candidate(candidates[0])


def compact_title_candidate(value: str) -> str:
    text = clean_math_title_text(value)
    text = re.split(
        r"\bTo include\b|\bQuestions will\b|\bStudents are expected\b", text, maxsplit=1
    )[0]
    text = re.split(r"\bwhere the equation\b", text, maxsplit=1)[0]
    text = text.strip(" .;:")
    return text or clean_source_point(value).strip(" .;:")


def clean_math_title_text(value: str) -> str:
    text = clean_ocr_math_text(" ".join(value.split()))
    text = text.replace("(1+ x)n", "(1 + x)^n")
    text = text.replace("(a + b) n", "(a + b)^n")
    text = text.replace("(x - a)2 + (y - b)2 = r 2 circle", "(x - a)^2 + (y - b)^2 = r^2")
    return text


def clean_ocr_math_text(value: str) -> str:
    text = value
    text = text.replace("/greaterthanorequalangled", ">=")
    text = re.sub(r"\beg\s+2\s+2xx\s*\+\s*>=\s*6\b", "eg 2x^2 + x >= 6", text)
    text = text.replace(
        "tan sin cosθ θ θ= ; and sinc os 122 +=θθ",
        "tan theta = sin theta / cos theta; and sin^2 theta + cos^2 theta = 1",
    )
    text = re.sub(r"\(1\s*\+\s*x\)\s*n\b", "(1 + x)^n", text)
    text = re.sub(r"\(a\s*\+\s*b\)\s*n\b", "(a + b)^n", text)
    text = text.replace("−± −bb ac a", "completing the square and the quadratic formula")
    text = text.replace("ab Csin2", "1/2 ab sin C")
    text = text.replace("d d y x", "dy/dx")
    text = text.replace("2t as vtt= 2", "s = ut + 1/2 at^2 and v = u + at")
    text = re.sub(r"\bxn\s*\+\s*1\s*=\s*f\s*\(\s*xn\s*\)", "x_(n+1) = f(x_n)", text)
    text = re.sub(r"\bx n\b", "x^n", text)
    text = re.sub(r"\bxn\b", "x^n", text)
    return text


def topic_title_prefix(title: str) -> str:
    if ":" not in title:
        return ""
    return title.rsplit(":", 1)[0].strip() + ": "


def choose_focus_point(topic: Topic, number: int = 0) -> str:
    points = visible_source_points(topic)
    return points[number % len(points)]


def clean_source_point(point: str) -> str:
    text = " ".join(point.split()).strip()
    text = (
        text.replace("脳", "x")
        .replace("¡Á", "x")
        .replace("鈭?", "-")
        .replace("鈭", "-")
        .replace("漏", "(c)")
    )
    text = clean_ocr_math_text(text)
    for pattern in BOILERPLATE_SUFFIX_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    if re.fullmatch(r"forcepressure\s+area=", text, flags=re.IGNORECASE):
        return "pressure = force / area"
    if "velocity in changeonaccelerati" in text.lower():
        return "acceleration = change in velocity / time"
    if text.lower().rstrip(" .").endswith("remainder theorem and the"):
        text = text.rstrip(" .") + " Factor Theorem"
    action_words = (
        r"(?:understand|identify|explain|describe|state|apply|prepare|calculate|distinguish)"
    )
    text = re.sub(r"^[a-z]\)\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+significance\s+of\s+the\s+following\s+accounting\s+concepts\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+following\s+accounting\s+concepts\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+following\s+accounting\s*$", "", text, flags=re.IGNORECASE
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+following\s+accounting\s*:?\s*$", "", text, flags=re.IGNORECASE
    ).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+the\s+terms\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+causes\s+of\s+(.+)$", r"causes of \1", text, flags=re.IGNORECASE
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of(?:\s+the)?\s*:?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"^{action_words}\s+the\s+(?:purpose|use|uses|characteristics|features|terms|benefits|significance|principles)\s+of\s+",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(rf"^{action_words}\s+between\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(rf"^{action_words}\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(
        rf"\bStudents should be able to\s+{action_words}\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r"\bStudents will be expected to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bStudents may be required to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        r"\bStudents should be familiar with\b[: ]*", "", text, flags=re.IGNORECASE
    ).strip()
    text = re.sub(r"\bStudents should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bLearners should be able to\b[: ]*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(
        r"\bCandidates should have an understanding of\b[: ]*", "", text, flags=re.IGNORECASE
    ).strip()
    return text.rstrip(".")


def merge_wrapped_source_points(points: list[str]) -> list[str]:
    merged: list[str] = []
    for raw in points:
        point = raw.strip()
        if not point:
            continue
        if merged and should_merge_with_next(merged[-1], point):
            merged[-1] = f"{merged[-1]} {point}".strip()
        else:
            merged.append(point)
    return merged


def should_merge_with_next(previous: str, current: str) -> bool:
    prev = previous.strip().lower()
    cur = current.strip()
    if not prev or not cur:
        return False
    if prev.endswith((",", ";", ":")):
        return True
    if prev.split()[-1] in {
        "and",
        "or",
        "for",
        "of",
        "the",
        "in",
        "to",
        "with",
        "form",
        "convergent",
        "subst",
        "rem",
        "repres",
        "thei",
        "capital",
        "raw",
        "provision",
    }:
        return True
    if cur and cur[0].islower() and prev.endswith((" other", "non-current", "books", "open")):
        return True
    return False


def clean_topic_title(title: str) -> str:
    text = title.rsplit(":", 1)[-1]
    text = re.sub(r"^\s*[A-Z]{0,3}\d+(?:\.\d+)*\s*[-–]\s*", "", text).strip()
    return text or title.strip()


def is_syllabus_shell(point: str) -> bool:
    text = clean_source_point(point).strip(" .")
    if not text:
        return True
    lower = text.lower()
    if any(re.fullmatch(pattern, lower) for pattern in SHELL_PATTERNS):
        return True
    if any(
        re.fullmatch(pattern, text, flags=re.IGNORECASE) for pattern in BOILERPLATE_FULL_PATTERNS
    ):
        return True
    if lower in {
        "concepts:",
        "the following accounting",
        "the following accounting:",
    }:
        return True
    return False
