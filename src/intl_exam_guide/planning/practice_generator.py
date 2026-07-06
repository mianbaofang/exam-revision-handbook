from __future__ import annotations

import re

from intl_exam_guide.models import PracticeItem, Topic
from intl_exam_guide.planning.anti_ai_language import polish_ai_language, polish_texts
from intl_exam_guide.planning.practice_focus import (
    add_question_variant_marker,
    choose_command_word,
    choose_difficulty,
    visible_zh_practice_focus,
)
from intl_exam_guide.planning.source_points import choose_focus_point


def clean_focus_text(value: str) -> str:
    text = " ".join(value.split()).strip()
    if not text:
        return text
    replacements = [
        r"\bStudents will be expected to\b[: ]*",
        r"\bStudents are expected to\b[: ]*",
        r"\bStudents should be able to\s+(?:understand|identify|explain|describe|state|apply|prepare|calculate)\s*:\s*",
        r"\bStudents should be able to\s+(?:understand|identify|explain|describe|state|apply|prepare|calculate)\s*$",
        r"\bStudents should be able to\b[: ]*",
        r"\bCandidates should have an understanding of\b[: ]*",
        r"\bCandidates should\b[: ]*",
    ]
    for pattern in replacements:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\bunderstand\b\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\binterpret\b\s+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\.\s+the\b", ": the", text, flags=re.IGNORECASE).strip()
    text = text.lstrip(":;,- ").strip()
    if text.endswith("."):
        text = text[:-1].strip()
    return text


def build_practice_item(
    topic: Topic,
    points: list[str],
    number: int,
    qualification_type: str,
    explanation_style: str = "friendly",
    output_language: str = "en",
    subject_area: str | None = None,
    variant_number: int | None = None,
) -> PracticeItem:
    """Build a source-bound scaffold only.

    Python does not write subject examples.  The host LLM Writer replaces this
    scaffold from concepts/concept_explanations.json via apply_concept_entries().
    """

    focus = choose_focus_point(topic, number)
    example_number = number if variant_number is None else variant_number
    clean_focus = clean_focus_text(focus)
    visible_focus = (
        clean_focus
        if output_language == "en"
        else visible_zh_practice_focus(topic, points, clean_focus or focus, number)
    )
    command_word = choose_command_word(example_number, qualification_type, output_language)
    difficulty = choose_difficulty(example_number, output_language)
    if output_language == "zh-CN":
        question, frame, steps, checkpoints = concrete_example_zh(topic, clean_focus or focus)
    else:
        question, frame, steps, checkpoints = concrete_example(topic, clean_focus or focus)
    question = contextualize_question(question, visible_focus, output_language)
    question = add_question_variant_marker(question, number, output_language)
    question = polish_ai_language(question, output_language)
    frame = polish_texts(frame, output_language)
    steps = polish_texts(steps, output_language)
    checkpoints = polish_texts(checkpoints, output_language)
    return PracticeItem(
        topic_title=topic.title,
        command_word=command_word,
        difficulty=difficulty,
        focus_point=visible_focus,
        question=decorate_question(question, explanation_style, output_language),
        answer_frame=frame,
        public_solution_steps=steps,
        answer_checkpoints=checkpoints,
        source_points=points,
        source_snippets=topic.source_snippets[:2],
    )


def decorate_question(question: str, explanation_style: str, output_language: str = "en") -> str:
    if output_language == "zh-CN":
        prefixes = {
            "formal": "考试题：",
            "friendly": "热身题：",
            "life": "生活场景题：",
            "story": "故事题：",
            "detective": "案件线索：",
            "adventure": "闯关挑战：",
        }
        return f"{prefixes.get(explanation_style, prefixes['friendly'])}{question}"
    prefixes = {
        "formal": "Exam-style prompt: ",
        "friendly": "Warm-up prompt: ",
        "life": "Real-life prompt: ",
        "story": "Story prompt: ",
        "detective": "Case file: ",
        "adventure": "Checkpoint challenge: ",
    }
    return f"{prefixes.get(explanation_style, prefixes['friendly'])}{question}"


def contextualize_question(question: str, focus: str, output_language: str) -> str:
    focus = clean_focus_text(focus)
    if not focus:
        return question
    lower_focus = focus.lower()
    if (
        lower_focus.endswith((" but", " to", " and", " of", " from", " with"))
        or len(focus.split()) <= 2
        or ("not " in lower_focus and " but" in lower_focus)
    ):
        return question
    if focus.lower() in question.lower():
        return question
    if output_language == "zh-CN":
        return f"围绕“{focus}”：{question}"
    return f"Focus on {focus}: {question}"


def concrete_example(
    topic: Topic,
    focus: str,
    number: int = 0,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    return generic_example(focus)


def concrete_example_zh(
    topic: Topic,
    focus: str,
    number: int = 0,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    return generic_example_zh(focus)


def generic_example(focus: str) -> tuple[str, list[str], list[str], list[str]]:
    focus_label = clean_focus_text(focus).strip().rstrip(".") or "this source point"
    return (
        f"The LLM Writer must replace this scaffold with a realistic, source-bound example for '{focus_label}'.",
        [
            "Read the command word and identify the exact source point being tested.",
            "Use a short scenario that fits this subject and does not add unsupported syllabus content.",
            "Write the answer steps so a student can follow the reasoning, not just the final result.",
        ],
        [
            f"Source point to use: {focus_label}.",
            "The final worked example should name the scenario, apply the source point, and show the reasoning path.",
            "The conclusion should answer the command word and avoid facts not found in the evidence.",
            "If a calculation, diagram, table, or policy chain is needed, the LLM Writer supplies it explicitly.",
        ],
        [
            "The example is written by the LLM Writer, not selected from a Python subject template.",
            "The scenario is close to the actual subject application named by the source point.",
            "All claims can be traced back to the official evidence or the Writer's source-bound reasoning.",
        ],
    )


def generic_example_zh(focus: str) -> tuple[str, list[str], list[str], list[str]]:
    focus_label = clean_focus_text(focus).strip().rstrip("。") or "本节来源点"
    return (
        f"LLM 写作者必须把这个脚手架替换成围绕“{focus_label}”的真实学科应用例题。",
        [
            "先读指令词，确定考查的具体来源点。",
            "使用贴合本学科的短情境，不能加入来源证据以外的内容。",
            "步骤要让学生看懂推理过程，而不只是看到最后答案。",
        ],
        [
            f"本题来源点：{focus_label}。",
            "最终例题应写明情境、应用来源点，并展示推理路线。",
            "结论要回应指令词，避免使用证据之外的事实。",
            "如果需要计算、图表、流程或评价链条，由 LLM 写作者明确给出。",
        ],
        [
            "例题由 LLM 写作者完成，不使用 Python 学科模板。",
            "情境要接近来源点对应的真实学科应用。",
            "所有判断都能回到官方证据或有来源约束的推理。",
        ],
    )
