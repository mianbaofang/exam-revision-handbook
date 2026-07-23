from __future__ import annotations

from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import (
    is_generic_zh_label,
    zh_point_label,
    zh_topic_reference,
)


def visible_zh_practice_focus(topic: Topic, points: list[str], focus: str, number: int) -> str:
    label = zh_point_label(focus, number)
    if not is_generic_zh_label(label):
        return label
    for index, point in enumerate(points):
        candidate = zh_point_label(point, index)
        if not is_generic_zh_label(candidate):
            return candidate
    return visible_zh_single_focus(topic, focus, number)


def visible_zh_single_focus(topic: Topic, focus: str, number: int) -> str:
    label = zh_point_label(focus, number)
    if not is_generic_zh_label(label):
        return label
    fallback = zh_point_label(topic.title, 0)
    return fallback if not is_generic_zh_label(fallback) else zh_topic_reference(topic)


def add_question_variant_marker(question: str, number: int, output_language: str) -> str:
    if number == 0:
        return question
    if output_language == "zh-CN":
        return f"变式 {number + 1}：换一个证据点再做一遍。{question}"
    return f"Variant {number + 1}: use a different source detail. {question}"


def choose_command_word(number: int, qualification_type: str, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        words = (
            ["解释", "分析", "比较", "评价"]
            if qualification_type == "international_as_a_level"
            else ["写出", "描述", "解释", "提出"]
        )
        return words[number % len(words)]
    if qualification_type == "international_as_a_level":
        words = ["explain", "analyse", "compare", "evaluate"]
    elif qualification_type == "advanced_placement":
        words = ["identify", "explain", "analyze", "evaluate"]
    else:
        words = ["state", "describe", "explain", "suggest"]
    return words[number % len(words)]


def choose_difficulty(number: int, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        return ["基础", "标准", "挑战"][number % 3]
    return ["core", "standard", "stretch"][number % 3]
