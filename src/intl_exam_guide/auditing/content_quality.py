from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
import re


ZH_GENERIC_PATTERNS = [
    (re.compile(r"考点要求\s*\d+"), "generic placeholder"),
    (re.compile(r"本节核心主题\s*\d+"), "generic placeholder"),
    (re.compile(r"知识点\s*\d+"), "generic placeholder"),
    (re.compile(r"知识单元\s*\d+"), "generic placeholder"),
    (re.compile(r"(?:不看笔记也能)?完成至少一道原创考试风格练习"), "generic practice frame"),
    (re.compile(r"如果题目围绕"), "generic worked-example frame"),
    (re.compile(r"围绕[“\"']?考点要求"), "generic practice frame"),
]


def student_visible_text_issues(text: str, language: str) -> list[str]:
    issues: list[str] = []
    if language == "zh-CN":
        for pattern, label in ZH_GENERIC_PATTERNS:
            match = pattern.search(text)
            if match:
                issues.append(f"student-facing Chinese text contains {label}: {match.group(0)}")
    return issues


def topic_title_quality_issues(titles: Sequence[str], language: str) -> list[str]:
    issues: list[str] = []
    title_list = [
        normalize_rendered_topic_title(title)
        for title in titles
        if normalize_rendered_topic_title(title)
    ]
    if not title_list:
        return ["no student-facing topic titles were rendered"]
    unique_count = len(set(title_list))
    if len(title_list) >= 4 and unique_count / len(title_list) <= 0.5:
        issues.append(
            f"student-facing topic titles are too repetitive: "
            f"{unique_count} unique titles for {len(title_list)} topics"
        )
    if language == "zh-CN":
        for title in sorted(set(title_list)):
            if re.fullmatch(r"第\s+[A-Z]{1,3}\d+\s+节", title):
                issues.append(
                    f"student-facing topic title is module-only and not teachable: {title}"
                )
    for title, count in Counter(title_list).items():
        if count >= 5:
            issues.append(f"student-facing topic title repeats {count} times: {title}")
    return issues


def normalize_rendered_topic_title(title: str) -> str:
    text = re.sub(r"\s+", " ", title).strip()
    return re.sub(r"^T\d+\.\s*", "", text)
