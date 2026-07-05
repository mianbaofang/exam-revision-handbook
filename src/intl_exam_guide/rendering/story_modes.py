from __future__ import annotations

import html


def english_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    text = f"{title} {focus}".lower()
    themed = english_themed_story_lines(text, escaped_title, escaped_focus)
    if themed:
        return themed
    variants = [
        (
            f"Treat <strong>{escaped_title}</strong> as a real situation: observe what changes, then explain it with <strong>{escaped_focus}</strong>.",
            "Read the question like a case file: data are clues, the syllabus term is evidence, and the final line must answer the command word.",
            "Turn the topic into a mission: unlock the term, avoid the common trap, and finish with one check sentence.",
        ),
        (
            f"Imagine the concept showing up in a school, shop, lab, or household decision. First name the visible action, then connect it to <strong>{escaped_focus}</strong>.",
            "Build the answer like an investigation: identify the suspect idea, test it against the evidence, then write the verdict precisely.",
            "Use a three-step route: collect the fact, choose the method, and check whether the answer would earn the final mark.",
        ),
        (
            f"Start with the everyday version of <strong>{escaped_title}</strong>: what would a person notice before they knew the technical word?",
            "Separate clues from noise. The useful clue is the one that proves the syllabus point, not the one that merely sounds familiar.",
            "Make the checkpoint explicit: term, evidence, conclusion. If one is missing, the answer is not finished.",
        ),
    ]
    return variants[(index - 1) % len(variants)]


def chinese_story_lines(title: str, focus: str, index: int) -> tuple[str, str, str]:
    escaped_title = html.escape(title, quote=True)
    escaped_focus = html.escape(focus, quote=True)
    text = f"{title} {focus}".lower()
    themed = chinese_themed_story_lines(text, escaped_title, escaped_focus)
    if themed:
        return themed
    variants = [
        (
            f"把 <strong>{escaped_title}</strong> 放进身边场景：先找看得见的现象，再用 <strong>{escaped_focus}</strong> 解释为什么。",
            "像破案一样答题：题干数据是线索，大纲术语是证据，最后一句必须回应指令词。",
            "把本节拆成三关：认出术语、避开陷阱、用一句检查句收尾。",
        ),
        (
            f"想象它出现在学校、商店、实验室或家庭决策里：先说发生了什么，再把它连回 <strong>{escaped_focus}</strong>。",
            "先筛线索：能证明知识点的才是关键证据，只是眼熟的词不一定有用。",
            "按“事实-方法-检查”走：拿到题干事实，选择解法，再确认答案能不能拿最后一分。",
        ),
        (
            f"先用普通话说清 <strong>{escaped_title}</strong>：如果不背术语，一个人会先观察到什么？",
            "把答案当作结案陈词：结论不能单独站着，前面必须有题干证据支撑。",
            "最后检查三件事：术语是否准确，证据是否来自题干，结论是否回答了问题。",
        ),
    ]
    return variants[(index - 1) % len(variants)]


def english_themed_story_lines(
    text: str,
    escaped_title: str,
    escaped_focus: str,
) -> tuple[str, str, str] | None:
    if any(term in text for term in ["ledger", "invoice", "account", "trial balance"]):
        return (
            f"Treat <strong>{escaped_title}</strong> like checking a small shop's records: every document must leave a trace that explains <strong>{escaped_focus}</strong>.",
            "Read it like an audit trail: follow the document, test the account, and only close the case when the figures agree.",
            "Make it a checkpoint run: source document, correct book, final account effect.",
        )
    if any(term in text for term in ["demand", "supply", "market", "scarcity", "production"]):
        return (
            f"Put <strong>{escaped_title}</strong> into a shop queue, factory decision, or family budget before naming <strong>{escaped_focus}</strong>.",
            "Investigate the incentive: who gains, who loses, what changed, and which curve or trade-off proves it.",
            "Pass the mission by linking agent, incentive, and outcome in one clear chain.",
        )
    if any(term in text for term in ["gas", "chromatography", "acid", "particle", "bond"]):
        return (
            f"Imagine the lab bench version of <strong>{escaped_title}</strong>: what would the student see, measure, or label before using <strong>{escaped_focus}</strong>?",
            "Use evidence like a lab investigator: observation first, test result second, conclusion last.",
            "The checkpoint is simple: apparatus or model, observation, syllabus conclusion.",
        )
    if any(term in text for term in ["triangle", "graph", "set", "venn", "ratio", "probability"]):
        return (
            f"Turn <strong>{escaped_title}</strong> into marks on a diagram: label the known parts before applying <strong>{escaped_focus}</strong>.",
            "Separate useful clues from decorative numbers; the useful clue changes the diagram or calculation.",
            "Finish the level by writing the method, substitution, and final check.",
        )
    return None


def chinese_themed_story_lines(
    text: str,
    escaped_title: str,
    escaped_focus: str,
) -> tuple[str, str, str] | None:
    if any(
        term in text
        for term in ["ledger", "invoice", "account", "trial balance", "分类账", "发票", "试算"]
    ):
        return (
            f"把 <strong>{escaped_title}</strong> 想成一家小店在查账：每张凭证都要留下能解释 <strong>{escaped_focus}</strong> 的记录。",
            "像审计一样破案：先追凭证，再查账户，最后看数字能不能对上。",
            "闯关顺序是：原始凭证、正确账簿、最终报表影响。",
        )
    if any(
        term in text
        for term in [
            "demand",
            "supply",
            "market",
            "scarcity",
            "production",
            "需求",
            "供给",
            "市场",
            "生产",
        ]
    ):
        return (
            f"把 <strong>{escaped_title}</strong> 放到商店排队、工厂决策或家庭预算里，再说清 <strong>{escaped_focus}</strong>。",
            "像调查动机一样答题：谁受影响，什么改变了，哪条曲线或取舍能证明。",
            "通关句要连成一条链：经济主体、激励变化、结果。",
        )
    if any(
        term in text
        for term in [
            "gas",
            "chromatography",
            "acid",
            "particle",
            "bond",
            "气体",
            "色谱",
            "酸",
            "粒子",
            "结构",
        ]
    ):
        return (
            f"先想象 <strong>{escaped_title}</strong> 出现在实验台上：学生先看到、测到或标出什么，再用 <strong>{escaped_focus}</strong> 解释。",
            "像实验侦探一样走：先观察，再判断测试结果，最后写结论。",
            "本关检查三件事：装置或模型、观察结果、大纲结论。",
        )
    if any(
        term in text
        for term in [
            "triangle",
            "graph",
            "set",
            "venn",
            "ratio",
            "probability",
            "三角",
            "图像",
            "集合",
            "比例",
            "概率",
        ]
    ):
        return (
            f"把 <strong>{escaped_title}</strong> 变成图上的标记：先标已知条件，再使用 <strong>{escaped_focus}</strong>。",
            "把有用线索和装饰数字分开；真正有用的线索一定会改变图形或计算。",
            "通关格式是：方法、代入、最后检查。",
        )
    return None
