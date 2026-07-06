from __future__ import annotations

import html
import re

from intl_exam_guide.models import Qualification


SUPERSCRIPT_MAP = str.maketrans(
    {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
        "(": "⁽",
        ")": "⁾",
        "n": "ⁿ",
        "x": "ˣ",
        "y": "ʸ",
        "a": "ᵃ",
        "b": "ᵇ",
        "c": "ᶜ",
        "t": "ᵗ",
    }
)

GREEK_SYMBOLS = {
    "theta": "θ",
    "mu": "μ",
    "pi": "π",
    "alpha": "α",
    "beta": "β",
    "lambda": "λ",
}


def subject_display_name(qualification: Qualification) -> str:
    source = f"{qualification.subject_area or ''} {qualification.title}".lower()
    subject_map = [
        ("mathematics", "数学"),
        ("maths", "数学"),
        ("chemistry", "化学"),
        ("economics", "经济学"),
        ("accounting", "会计学"),
        ("business", "商务"),
        ("physics", "物理"),
        ("biology", "生物"),
        ("computer science", "计算机科学"),
        ("english", "英语"),
    ]
    for key, label in subject_map:
        if key in source:
            return label
    return "本课程"


def html_escape(value: str) -> str:
    return html.escape(normalize_math_notation(str(value)), quote=True)


def html_attribute_escape(value: str) -> str:
    return html.escape(str(value), quote=True)


def normalize_math_notation(value: str) -> str:
    """Format common plain-text maths notation without changing meaning."""

    text = str(value)
    text = re.sub(r"\bsqrt\s*\(", "√(", text, flags=re.IGNORECASE)
    text = text.replace(">=", "≥").replace("<=", "≤").replace("!=", "≠")
    text = re.sub(r"\b1/2\b", "½", text)
    text = re.sub(r"\b1/4\b", "¼", text)
    text = re.sub(r"\b3/4\b", "¾", text)
    text = re.sub(r"\^\{([^{}]{1,8})\}", superscript_replacement, text)
    text = re.sub(r"\^\(([-+0-9nxyabct]{1,8})\)", superscript_replacement, text)
    text = re.sub(r"\^([-+]?\d+|[nxyabct])", superscript_replacement, text)
    for name, symbol in GREEK_SYMBOLS.items():
        text = re.sub(rf"\b{name}\b", symbol, text, flags=re.IGNORECASE)
    return text


def superscript_replacement(match: re.Match[str]) -> str:
    raw = match.group(1)
    rendered = raw.translate(SUPERSCRIPT_MAP)
    return rendered if rendered != raw else match.group(0)


def strip_internal_review_panel(html_text: str) -> str:
    """Remove internal review-status panels from student-facing HTML exports."""

    return re.sub(
        r'\s*<section\b[^>]*class="[^"]*\bdelivery-panel\b[^"]*"[^>]*>.*?</section>\s*',
        "\n",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
