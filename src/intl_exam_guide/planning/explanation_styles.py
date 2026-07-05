from __future__ import annotations

from intl_exam_guide.models import Topic
from intl_exam_guide.planning.localization import zh_topic_reference


def styled_explanation(
    topic: Topic,
    primary: str,
    level_hint: str,
    explanation_style: str,
    output_language: str,
) -> tuple[str, str, str, str]:
    if output_language == "en":
        return styled_explanation_en(topic, primary, level_hint, explanation_style)
    unit = zh_topic_reference(topic)
    if explanation_style == "formal":
        return (
            f"本 {level_hint} 的目标是准确掌握“{primary}”，并能在题目中按指令词完成计算、解释或判断。",
            f"把“{unit}”看成考试说明中的一个能力模块：每个官方大纲点都对应一种可检查的作答动作。",
            f"例题处理顺序：定位 '{primary}'，列出已知条件，选择公式、定义或判断规则，再写出可复核的结论。",
            "常见失分点是结论正确但过程不足，或没有回应题目指定的指令词。",
        )
    if explanation_style == "life":
        return (
            f"这一节要把 '{primary}' 变成生活中看得见、说得清、用得上的判断动作。",
            f"把“{unit}”放进真实场景：先观察发生了什么，再用官方大纲点解释为什么。",
            "例题先找生活场景里的数据或现象，再把它翻译成公式、定义、图像或因果关系。",
            "常见失分点是只写课本词，没有把它和题目里的真实情境连起来。",
        )
    if explanation_style == "story":
        return (
            f"这一节像一段小故事：'{primary}' 是主线，题目给出的条件是推动故事往前走的线索。",
            f"把“{unit}”拆成开头、冲突和解决：看懂概念，遇到题目障碍，再用正确方法收束答案。",
            "例题先讲清楚题目场景，再一步步把线索收集成答案。",
            "常见失分点是跳过中间推理，让答案像突然出现的结尾。",
        )
    if explanation_style == "detective":
        return (
            f"这一节的核心是用“{primary}”破案：题干是现场，数据是线索，指令词是结案要求。",
            f"把“{unit}”当成一宗小案子：先锁定证据，再判断哪条大纲规则能解释它。",
            "例题按侦探流程走：圈线索，选证据，排除误解，最后写出能回到题问的结论。",
            "常见失分点是看到熟悉词就急着下结论，没有把证据链写完整。",
        )
    if explanation_style == "adventure":
        return (
            f"这一节是一关学习任务：先解锁 '{primary}'，再用它通过计算、解释或判断挑战。",
            f"把“{unit}”看成原创闯关地图：术语是装备，例题是关卡，检查句是通关确认。",
            "例题先确认本关目标，再选择工具，最后用一条检查句确认答案没有跑偏。",
            "常见失分点是装备拿对了但用错地方，也就是知道词却没有按题目要求行动。",
        )
    return (
        f"这一节的核心任务是把 '{primary}' 变成能做题的动作：先看懂关键词，再把它用于计算、解释、比较或判断。",
        f"把“{unit}”当成一个小工具箱：每个官方大纲点是一件工具，题目真正考的是你能不能选对工具并说清楚为什么。",
        f"小例题思路：读到和 '{primary}' 有关的题干时，先圈出数据或关键词，再写出对应公式、定义或判断规则，最后检查单位和答案是否回应题问。",
        "常见失分点是只背关键词，却没有按题目的指令词行动。看到题目先问自己：它要我算、解释、比较，还是证明？",
    )


def styled_explanation_en(
    topic: Topic,
    primary: str,
    level_hint: str,
    explanation_style: str,
) -> tuple[str, str, str, str]:
    if explanation_style == "formal":
        return (
            f"This {level_hint} asks the student to master '{primary}' accurately and apply it under the command word.",
            f"Treat '{topic.title}' as one exam skill block: each syllabus point should map to a checkable answer action.",
            f"Worked-example route: locate '{primary}', list the given conditions, choose the formula, definition, or judgement rule, then write a verifiable conclusion.",
            "A common mark loss is giving the right conclusion without enough method, or missing the command word.",
        )
    if explanation_style == "life":
        return (
            f"Turn '{primary}' into something visible in a real situation, then explain the situation using the syllabus idea.",
            f"Place '{topic.title}' in a real-life scene: observe what happens, then use the syllabus point to explain why.",
            "For examples, first find the data or event in the scene, then translate it into a formula, definition, graph, or cause-effect link.",
            "A common mark loss is writing a memorised phrase without linking it to the context in the question.",
        )
    if explanation_style == "story":
        return (
            f"This topic works like a short story: '{primary}' is the plot line and the question data moves the story forward.",
            f"Break '{topic.title}' into setup, conflict, and resolution: understand the idea, meet the exam obstacle, then close the answer clearly.",
            "For examples, state the scenario first, then collect each clue into a final answer step by step.",
            "A common mark loss is skipping the middle reasoning, so the answer appears without evidence.",
        )
    if explanation_style == "detective":
        return (
            f"Use '{primary}' like a case-solving tool: the question is the scene, the data are clues, and the command word is the case brief.",
            f"Treat '{topic.title}' as a small investigation: lock onto the evidence, then decide which syllabus rule explains it.",
            "For examples, circle clues, choose evidence, rule out the wrong reading, then write a conclusion that answers the question.",
            "A common mark loss is jumping to a familiar conclusion before finishing the evidence chain.",
        )
    if explanation_style == "adventure":
        return (
            f"This topic is a learning mission: unlock '{primary}', then use it to pass a calculation, explanation, or judgement challenge.",
            f"Think of '{topic.title}' as an original quest map: terms are tools, examples are checkpoints, and final checks confirm the route.",
            "For examples, identify the checkpoint goal, choose the right tool, then use one final check sentence to confirm the answer.",
            "A common mark loss is using the right tool in the wrong place: knowing the term but not answering the question.",
        )
    return (
        f"The core task is to turn '{primary}' into an answer action: calculate, explain, compare, or judge using the question wording.",
        f"Treat '{topic.title}' as a small toolkit. Each syllabus point is one tool, and the exam checks whether the student can choose it correctly.",
        f"Example route: circle the data or key terms around '{primary}', choose the matching formula, definition, or judgement rule, then check the unit and final sentence.",
        "A common mark loss is memorising key words without acting on the command word.",
    )
