from __future__ import annotations

import re

from intl_exam_guide.models import PracticeItem, Topic
from intl_exam_guide.planning.anti_ai_language import polish_ai_language, polish_texts
from intl_exam_guide.planning.practice_focus import (
    add_question_variant_marker,
    choose_command_word,
    choose_difficulty,
    visible_zh_practice_focus,
    visible_zh_single_focus,
)
from intl_exam_guide.planning.practice_business_examples import business_example
from intl_exam_guide.planning.practice_economics_examples import economics_example
from intl_exam_guide.planning.practice_math_examples import (
    mathematics_specialist_example,
    mathematics_specialist_example_zh,
)
from intl_exam_guide.planning.practice_history_examples import history_example
from intl_exam_guide.planning.practice_science_examples import (
    biology_example,
    chemistry_example,
    physics_example,
)
from intl_exam_guide.planning.practice_accounting_examples import (
    accounting_example,
    accounting_example_zh,
)
from intl_exam_guide.planning.source_points import choose_focus_point
from intl_exam_guide.planning.subject_profiles import has_terms, resolve_subject_profile


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
    text = re.sub(
        r"\bassign probabilities using\b", "probability from", text, flags=re.IGNORECASE
    ).strip()
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
        question, frame, steps, checkpoints = concrete_example_zh(
            topic, clean_focus or focus, example_number, subject_area
        )
    else:
        question, frame, steps, checkpoints = concrete_example(
            topic, clean_focus or focus, example_number, subject_area
        )
    question = contextualize_question(question, visible_focus, output_language)
    question = add_question_variant_marker(question, number, output_language)
    while len(steps) < 4:
        steps.append(
            "Check the final answer against the wording of the question."
            if output_language == "en"
            else "检查最终答案是否回应题目要求。"
        )
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
    number: int,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    code = topic.title.split(" ", 1)[0]
    prefix = code[:1]
    text = f"{topic.title} {focus}".lower()
    profile = resolve_subject_profile(subject_area, topic, text)
    if profile.example_domain == "chemistry":
        return chemistry_example(text, focus, number)
    if profile.example_domain == "physics":
        return physics_example(text, focus, number)
    if profile.example_domain == "biology":
        return biology_example(text, focus, number)
    if profile.example_domain == "business":
        return business_example(text, focus, number)
    if profile.example_domain == "economics":
        return economics_example(text, focus, number)
    if profile.example_domain == "accounting":
        return accounting_example(text, focus, number)
    if profile.example_domain == "history":
        return history_example(text, focus, number)
    if profile.example_domain == "generic":
        return generic_example(focus)
    if profile.example_domain == "mathematics" and "." in code:
        return mathematics_specialist_example(text, number)
    if prefix == "N" or has_terms(text, ["number", "ratio", "fraction", "percentage"]):
        if "ratio" in text or number % 3 == 0:
            if number % 2:
                return (
                    "A map uses the scale 1:25,000. Two towns are 6 cm apart on the map. Find the real distance in kilometres.",
                    [
                        "Use the scale to convert map distance to real distance.",
                        "Change centimetres to kilometres.",
                        "Check the size is reasonable.",
                    ],
                    [
                        "1 cm on the map represents 25,000 cm in real life.",
                        "6 cm represents 150,000 cm.",
                        "150,000 cm = 1,500 m = 1.5 km.",
                        "Answer: 1.5 km.",
                    ],
                    [
                        "The scale is multiplied by 6.",
                        "The unit conversion is correct.",
                        "A map distance becomes a larger real distance.",
                    ],
                )
            return (
                "A drink is mixed using juice and water in the ratio 2:5. If 140 ml of juice is used, find the amount of water needed.",
                [
                    "Write juice:water = 2:5.",
                    "Find the value of 1 part.",
                    "Multiply by the water parts.",
                ],
                [
                    "2 parts = 140 ml.",
                    "1 part = 140 / 2 = 70 ml.",
                    "Water = 5 parts = 5 x 70 = 350 ml.",
                    "Answer: 350 ml.",
                ],
                [
                    "Ratio order is not swapped.",
                    "The answer has ml.",
                    "Water should be more than juice because 5 parts > 2 parts.",
                ],
            )
        if "round" in text or "bounds" in text:
            return (
                "A mass is recorded as 12.4 kg to the nearest 0.1 kg. Write the lower and upper bounds.",
                [
                    "Half of 0.1 kg is 0.05 kg.",
                    "Subtract and add 0.05 kg.",
                    "Use the upper-bound inequality correctly.",
                ],
                [
                    "Lower bound = 12.4 - 0.05 = 12.35 kg.",
                    "Upper bound = 12.4 + 0.05 = 12.45 kg.",
                    "Answer: 12.35 kg <= mass < 12.45 kg.",
                ],
                ["Upper bound uses <.", "Both bounds have kg.", "The interval is centred on 12.4."],
            )
        return (
            "Calculate 3/4 of 280, then write the answer as a percentage of 350.",
            ["Find 3/4 of 280.", "Put that value over 350.", "Convert to a percentage."],
            ["3/4 of 280 = 210.", "210/350 = 0.6.", "0.6 = 60%.", "Answer: 60%."],
            [
                "Fraction operation is done before percentage conversion.",
                "The denominator for the percentage is 350.",
                "Answer is between 0% and 100%.",
            ],
        )
    if prefix == "A" or has_terms(text, ["algebra", "equation", "function", "sequence"]):
        if "function" in text or "graph" in text:
            if number % 2:
                return (
                    "The straight line y = 3x - 4 is drawn on a graph. Find the gradient, the y-intercept, and the value of y when x = 5.",
                    [
                        "Read the coefficient of x as the gradient.",
                        "Read the constant as the y-intercept.",
                        "Substitute x = 5.",
                    ],
                    [
                        "The gradient is 3.",
                        "The y-intercept is -4.",
                        "When x = 5, y = 3 x 5 - 4 = 11.",
                        "Answer: gradient 3, y-intercept -4, y = 11.",
                    ],
                    [
                        "Gradient and intercept are not swapped.",
                        "The negative intercept is kept.",
                        "Substitution uses the given x-value.",
                    ],
                )
            return (
                "For f(x) = 2x^2 - 3, find f(-2), then solve f(x) = 15.",
                [
                    "Substitute -2 carefully.",
                    "Set 2x^2 - 3 equal to 15.",
                    "Remember both square-root solutions.",
                ],
                [
                    "f(-2) = 2(-2)^2 - 3 = 5.",
                    "2x^2 - 3 = 15.",
                    "2x^2 = 18, so x^2 = 9.",
                    "Answer: x = -3 or x = 3.",
                ],
                [
                    "The negative input is squared correctly.",
                    "Both roots are included.",
                    "Substitution checks the answer.",
                ],
            )
        if "sequence" in text:
            if number % 2:
                return (
                    "The nth term of a sequence is 3n - 2. Write the first four terms and decide whether 31 is in the sequence.",
                    [
                        "Substitute n = 1, 2, 3 and 4.",
                        "Set 3n - 2 equal to 31.",
                        "Check whether n is a whole number.",
                    ],
                    [
                        "The first four terms are 1, 4, 7 and 10.",
                        "3n - 2 = 31.",
                        "3n = 33, so n = 11.",
                        "Answer: 31 is in the sequence because it is the 11th term.",
                    ],
                    [
                        "Term numbers start at n=1.",
                        "A valid position must be a whole number.",
                        "The conclusion names the term position.",
                    ],
                )
            return (
                "The sequence is 5, 9, 13, 17, ... Find the nth term and the 20th term.",
                ["Find the common difference.", "Use dn + c.", "Substitute n = 20."],
                [
                    "The common difference is 4.",
                    "Start with 4n: 4, 8, 12, 16, ...",
                    "Add 1 to match the sequence, so nth term = 4n + 1.",
                    "20th term = 4 x 20 + 1 = 81.",
                ],
                [
                    "The nth term gives 5 when n=1.",
                    "The 20th term uses n=20.",
                    "Do not confuse term number with term value.",
                ],
            )
        if number % 2:
            return (
                "Expand and simplify 2(x + 5) - 3(x - 1).",
                ["Expand both brackets.", "Collect x terms.", "Collect number terms."],
                [
                    "2(x + 5) = 2x + 10.",
                    "-3(x - 1) = -3x + 3.",
                    "2x + 10 - 3x + 3 = -x + 13.",
                    "Answer: -x + 13.",
                ],
                [
                    "The minus sign before 3 is applied to both terms.",
                    "Like terms are collected.",
                    "The final expression is simplified.",
                ],
            )
        return (
            "Solve 3(x - 2) + 5 = 20.",
            ["Expand the bracket.", "Collect constants.", "Divide by the coefficient of x."],
            ["3(x - 2) + 5 = 3x - 6 + 5.", "3x - 1 = 20.", "3x = 21.", "Answer: x = 7."],
            [
                "The bracket is expanded correctly.",
                "The same operation is applied to both sides.",
                "x=7 checks in the original equation.",
            ],
        )
    if prefix == "G" or has_terms(text, ["geometry", "triangle", "angle", "area", "volume"]):
        if "angle" in text:
            if number % 2:
                return (
                    "Angles around a point are 95 degrees, 130 degrees and x degrees. Find x.",
                    [
                        "Angles around a point add to 360 degrees.",
                        "Add the known angles.",
                        "Subtract from 360 degrees.",
                    ],
                    [
                        "95 + 130 = 225.",
                        "x = 360 - 225.",
                        "x = 135 degrees.",
                        "Answer: 135 degrees.",
                    ],
                    [
                        "Uses 360 degrees for a point.",
                        "Known angles are added first.",
                        "The answer is in degrees.",
                    ],
                )
            return (
                "Two angles on a straight line are x and 68 degrees. Find x.",
                [
                    "Angles on a straight line add to 180 degrees.",
                    "Write the equation.",
                    "Solve for x.",
                ],
                ["x + 68 = 180.", "x = 180 - 68.", "Answer: x = 112 degrees."],
                ["The angle fact is correct.", "The answer is in degrees.", "112 + 68 = 180."],
            )
        if number % 2:
            return (
                "A circle has radius 4 cm. Calculate its circumference in terms of pi.",
                ["Use C = 2 pi r.", "Substitute r = 4.", "Leave the answer in terms of pi."],
                ["C = 2 pi r.", "C = 2 pi x 4.", "C = 8 pi.", "Answer: 8 pi cm."],
                [
                    "Radius, not diameter, is substituted.",
                    "The unit is cm.",
                    "The answer is left in terms of pi.",
                ],
            )
        return (
            "A right-angled triangle has shorter sides 5 cm and 12 cm. Calculate the hypotenuse.",
            ["Identify the hypotenuse.", "Use c^2 = a^2 + b^2.", "Square-root the result."],
            ["c^2 = 5^2 + 12^2.", "c^2 = 25 + 144 = 169.", "c = sqrt(169) = 13.", "Answer: 13 cm."],
            [
                "Only perpendicular sides are added.",
                "Final answer is longer than 12 cm.",
                "The unit is cm.",
            ],
        )
    if prefix == "S" or has_terms(text, ["probability", "statistics", "data", "mean"]):
        if "probability" in text:
            if number % 2:
                return (
                    "A fair six-sided dice is rolled once. Find the probability of rolling an even number.",
                    [
                        "List the even outcomes.",
                        "Count the total outcomes.",
                        "Write favourable outcomes over total outcomes.",
                    ],
                    [
                        "The even outcomes are 2, 4 and 6.",
                        "There are 6 possible outcomes.",
                        "P(even) = 3/6.",
                        "Answer: 1/2.",
                    ],
                    [
                        "Only even outcomes are counted.",
                        "The denominator is 6.",
                        "The fraction is simplified.",
                    ],
                )
            return (
                "A bag contains 3 red counters, 5 blue counters and 2 green counters. One counter is chosen. Find P(blue).",
                [
                    "Find the total number of counters.",
                    "Put blue counters over total counters.",
                    "Simplify.",
                ],
                [
                    "Total = 3 + 5 + 2 = 10.",
                    "Blue counters = 5.",
                    "P(blue) = 5/10 = 1/2.",
                    "Answer: 1/2.",
                ],
                [
                    "Denominator is total outcomes.",
                    "Numerator is only blue outcomes.",
                    "Probability is between 0 and 1.",
                ],
            )
        if number % 2:
            return (
                "The scores are 4, 7, 9, 9, 11 and 14. Find the median and range.",
                [
                    "Check the data are in order.",
                    "Find the middle of six values.",
                    "Range = largest - smallest.",
                ],
                [
                    "The data are already in order.",
                    "The median is the mean of the 3rd and 4th values: (9 + 9) / 2 = 9.",
                    "Range = 14 - 4 = 10.",
                    "Answer: median 9, range 10.",
                ],
                [
                    "For an even number of values, two middle values are used.",
                    "Range uses largest minus smallest.",
                    "The repeated 9 is handled correctly.",
                ],
            )
        return (
            "The scores are 2, 5, 5, 8 and 10. Find the mean and range.",
            [
                "Add all values.",
                "Divide by how many values there are.",
                "Range = largest - smallest.",
            ],
            [
                "Total = 2 + 5 + 5 + 8 + 10 = 30.",
                "Mean = 30 / 5 = 6.",
                "Range = 10 - 2 = 8.",
                "Answer: mean 6, range 8.",
            ],
            [
                "The repeated 5 is counted twice.",
                "There are five values.",
                "Range uses largest minus smallest.",
            ],
        )
    if profile.example_domain == "mathematics":
        return mathematics_specialist_example(text, number)
    return (
        f"Using the idea '{focus}', answer a short exam-style question that asks for one definition, one application, and one check.",
        [
            "Identify the command word.",
            "Choose the matching syllabus term.",
            "Apply it to the given context.",
        ],
        [
            f"Name the focus point: {focus}.",
            "Apply the idea to the context using one precise sentence.",
            "Check that the final answer directly answers the question.",
        ],
        [
            "Uses a precise syllabus term.",
            "Links the idea to the context.",
            "Does not add unsupported facts.",
        ],
    )


def concrete_example_zh(
    topic: Topic,
    focus: str,
    number: int,
    subject_area: str | None = None,
) -> tuple[str, list[str], list[str], list[str]]:
    text = f"{topic.title} {focus}".lower()
    prefix = topic.title.split(" ", 1)[0][:1]
    visible_focus = visible_zh_single_focus(topic, focus, number)
    profile = resolve_subject_profile(subject_area, topic, text)
    if profile.example_domain == "chemistry":
        if any(word in text for word in ["solid", "liquid", "states of matter", "diffusion"]):
            return (
                "一名学生几分钟后在房间另一端闻到香水味。用粒子模型解释扩散。",
                ["说出过程名称。", "描述粒子的运动方式。", "把运动和气味扩散联系起来。"],
                [
                    "香水粒子离开液体并与空气混合。",
                    "气体粒子会随机运动，并从高浓度区域向低浓度区域扩散。",
                    "这种过程叫扩散。",
                    "所以学生能闻到气味，是因为香水粒子在空气中扩散。",
                ],
                ["答案必须提到粒子。", "要说明随机运动或扩散方向。", "观察现象要和扩散联系起来。"],
            )
        if any(word in text for word in ["atom", "atomic", "proton", "neutron", "electron"]):
            return (
                "一个原子有 11 个质子、12 个中子和 11 个电子。写出它的原子序数、质量数，并判断它是否呈电中性。",
                [
                    "原子序数等于质子数。",
                    "质量数等于质子数加中子数。",
                    "比较质子数和电子数判断电荷。",
                ],
                [
                    "原子序数 = 11。",
                    "质量数 = 11 + 12 = 23。",
                    "质子数等于电子数，所以整体不带电。",
                    "答案：原子序数 11，质量数 23，电中性。",
                ],
                [
                    "不要用中子数决定原子序数。",
                    "质量数要包含质子和中子。",
                    "电中性意味着质子数等于电子数。",
                ],
            )
        if any(word in text for word in ["bond", "ionic", "covalent", "metallic", "structure"]):
            return (
                "氯化钠熔点很高。用离子键和结构解释原因。",
                ["说出结构类型。", "描述需要克服的作用力。", "把作用力和高熔点联系起来。"],
                [
                    "氯化钠形成巨型离子晶格。",
                    "带相反电荷的离子之间有很强的静电吸引。",
                    "克服这些吸引力需要大量能量。",
                    "因此氯化钠具有很高的熔点。",
                ],
                ["要说离子，而不是分子。", "结构必须和性质相连。", "要解释为什么需要能量。"],
            )
        if has_terms(text, ["molar", "concentration"]):
            return (
                "某溶液在 0.25 dm3 体积中含有 0.50 mol 溶质。计算浓度，单位用 mol/dm3。",
                ["使用浓度 = 物质的量 / 体积。", "代入数值。", "写出单位。"],
                [
                    "浓度 = 0.50 / 0.25。",
                    "0.50 / 0.25 = 2.0。",
                    "单位是 mol/dm3。",
                    "答案：2.0 mol/dm3。",
                ],
                ["体积单位是 dm3。", "物质的量要除以体积。", "答案要带单位。"],
            )
        return (
            f"围绕“{visible_focus}”完成一道化学解释题：说出现象，指出相关粒子、结构或反应规则，并写出结论。",
            ["找出题目中的现象或数据。", "匹配对应的化学概念。", "用因果关系写出解释。"],
            [
                f"本题考查“{visible_focus}”。",
                "先把现象转化为粒子、结构、能量或反应速率语言。",
                "再写出关键原因。",
                "最后用一句话回应题目要求。",
            ],
            ["解释必须对应题目情境。", "不要只背关键词。", "结论要和证据一致。"],
        )
    if profile.example_domain == "economics":
        if any(
            word in text for word in ["opportunity cost", "resource allocation", "making choices"]
        ):
            return (
                "学校有一间教室，可以办经济社团，也可以办复习课。若选择经济社团，解释机会成本是什么。",
                ["确定被选择的方案。", "找出放弃的次优选择。", "清楚写出机会成本。"],
                [
                    "学校选择了经济社团。",
                    "被放弃的次优选择是复习课。",
                    "机会成本就是这间教室无法举办的复习课。",
                    "答案：机会成本是被放弃的次优选择的价值。",
                ],
                ["机会成本不是所有备选方案。", "必须点名被放弃的方案。", "答案要贴合情境。"],
            )
        if any(word in text for word in ["demand", "supply", "market", "price", "equilibrium"]):
            return (
                "一款新手机更受欢迎。假设供给不变，用需求和供给解释市场价格可能如何变化。",
                ["判断哪条曲线变化。", "说明移动方向。", "解释均衡价格变化。"],
                [
                    "受欢迎程度影响需求，而不是供给。",
                    "需求曲线向右移动。",
                    "在原价格下会出现超额需求。",
                    "市场价格可能上升到新的均衡。",
                ],
                ["要用需求变化解释。", "供给保持不变。", "价格上升要通过超额需求说明。"],
            )
        return (
            f"用“{visible_focus}”分析一个生活经济场景：指出经济主体、激励或约束，并说明可能结果。",
            ["说出经济主体。", "找出激励或约束。", "解释结果。"],
            [
                f"本题聚焦“{visible_focus}”。",
                "把它应用到消费者、生产者或政府决策中。",
                "说明稀缺性、激励或成本如何影响选择。",
                "最后写出可能的经济结果。",
            ],
            ["必须有经济主体。", "要写出因果关系。", "不要加入无依据的现实断言。"],
        )
    if profile.example_domain == "accounting":
        return accounting_example_zh(text, visible_focus, number)
    if profile.example_domain == "generic":
        return generic_example_zh(visible_focus)
    if profile.example_domain == "mathematics" and "." in topic.title.split(" ", 1)[0]:
        return mathematics_specialist_example_zh(text, number)
    if prefix == "N" or has_terms(text, ["number", "ratio", "fraction", "percentage"]):
        return (
            "一杯饮料中果汁和水的比例是 2:5。若用了 140 毫升果汁，需要多少水？",
            ["写出果汁:水 = 2:5。", "求出 1 份是多少。", "乘以水对应的份数。"],
            [
                "2 份 = 140 毫升。",
                "1 份 = 140 ÷ 2 = 70 毫升。",
                "水 = 5 份 = 5 × 70 = 350 毫升。",
                "答案：350 毫升。",
            ],
            ["比例顺序不能颠倒。", "答案要带毫升。", "水应比果汁多，因为 5 份大于 2 份。"],
        )
    if prefix == "A" or has_terms(text, ["algebra", "equation", "function", "sequence"]):
        return (
            "解方程 3(x - 2) + 5 = 20。",
            ["先展开括号。", "合并常数项。", "再除以 x 的系数。"],
            ["3(x - 2) + 5 = 3x - 6 + 5。", "3x - 1 = 20。", "3x = 21。", "答案：x = 7。"],
            ["括号要展开正确。", "等式两边要做同样操作。", "把 x=7 代回去能成立。"],
        )
    if has_terms(text, ["triangle", "angle", "pythagoras", "trigonometry", "geometry"]):
        return (
            "一个直角三角形两条直角边分别为 5 cm 和 12 cm。求斜边长度。",
            ["确认这是直角三角形。", "使用勾股定理。", "开平方得到长度。"],
            ["c^2 = 5^2 + 12^2。", "c^2 = 25 + 144 = 169。", "c = 13。", "答案：斜边为 13 cm。"],
            ["斜边是最长边。", "平方后再相加。", "答案要带 cm。"],
        )
    if profile.example_domain == "mathematics":
        return mathematics_specialist_example_zh(text, number)
    return generic_example_zh(visible_focus)


def generic_example(focus: str) -> tuple[str, list[str], list[str], list[str]]:
    focus_label = focus.strip().rstrip(".") or "this syllabus point"
    return (
        f"Using only the syllabus point '{focus_label}', explain what the idea means, what relationship or boundary it describes, and one exam context where it would be applied.",
        [
            "State the idea in the words of the source point.",
            "Name the relationship, condition, or boundary it controls.",
            "Apply it to one short exam context without adding outside facts.",
        ],
        [
            f"The focus point is: {focus_label}.",
            "A complete answer first defines or describes that focus point.",
            "It then names the relationship or limit stated by the source.",
            "The final sentence applies the idea to the question context and stays inside the source point.",
        ],
        [
            "The answer stays inside the source wording.",
            "It explains a relationship or boundary, not just a keyword.",
            "It gives an application without borrowing another subject's template.",
        ],
    )


def generic_example_zh(visible_focus: str) -> tuple[str, list[str], list[str], list[str]]:
    focus_label = visible_focus.strip().rstrip("。") or "本节知识点"
    return (
        f"本题只围绕“{focus_label}”：说明这个概念是什么意思，它描述了哪一种关系或边界，并给出一个不超出本节来源点的应用情境。",
        [
            "先用来源点的范围说明概念。",
            "指出它控制的关系、条件或边界。",
            "给出一个短情境，但不借用其他学科模板。",
        ],
        [
            f"本题聚焦“{focus_label}”。",
            "完整答案先解释这个知识点本身，而不是只写关键词。",
            "然后说明它对应的关系、限制或判断边界。",
            "最后把这个想法放进题目情境中，且不加入来源点之外的事实。",
        ],
        ["内容必须留在当前来源点内。", "要解释关系或边界。", "不能套用其他科目的例题场景。"],
    )
