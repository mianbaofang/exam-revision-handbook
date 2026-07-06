from __future__ import annotations

import html


def english_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    variants = [
        (
            f"Treat <strong>{escaped_title}</strong> as a source-bound situation: observe the evidence, then explain it with <strong>{escaped_focus}</strong>.",
            "Read the question like a case file: the data are clues, the syllabus wording is evidence, and the final line must answer the command word.",
            "Turn the topic into a mission: identify the idea, avoid adding outside facts, and finish with one check sentence.",
        ),
        (
            f"Imagine <strong>{escaped_title}</strong> appearing in a realistic subject setting. First name what changes, then connect it to <strong>{escaped_focus}</strong>.",
            "Build the answer like an investigation: identify the useful evidence, test it against the source point, then write the verdict precisely.",
            "Use a three-step route: collect the fact, choose the method, and check whether the answer would earn the final mark.",
        ),
        (
            f"Start with the student version of <strong>{escaped_title}</strong>: what would someone notice before they knew the technical wording?",
            "Separate clues from noise. The useful clue is the one that proves the source point, not the one that merely sounds familiar.",
            "Make the checkpoint explicit: term, evidence, conclusion. If one is missing, the answer is not finished.",
        ),
    ]
    return variants[(index - 1) % len(variants)]


def chinese_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    variants = [
        (
            f"把 <strong>{escaped_title}</strong> 放进有来源依据的学科情境：先找证据，再用 <strong>{escaped_focus}</strong> 解释。",
            "像破案一样答题：题干信息是线索，大纲表述是证据，最后一句必须回应指令词。",
            "把本节拆成三关：认出概念、避免加入外部事实、用一句检查句收尾。",
        ),
        (
            f"想象 <strong>{escaped_title}</strong> 出现在真实学科应用中：先说明发生了什么，再把它连回 <strong>{escaped_focus}</strong>。",
            "先筛线索：能证明来源点的才是关键证据，只是眼熟的词不一定有用。",
            "按“事实-方法-检查”走：拿到题干事实，选择解法，再确认答案能不能拿最后一分。",
        ),
        (
            f"先用学生能懂的话说清 <strong>{escaped_title}</strong>：不背术语时，一个人会先观察到什么？",
            "把答案当作结论陈述：结论不能单独站着，前面必须有题干证据支撑。",
            "最后检查三件事：术语是否准确，证据是否来自题干，结论是否回答了问题。",
        ),
    ]
    return variants[(index - 1) % len(variants)]
