from __future__ import annotations


def history_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    focus_label = focus.strip().rstrip(".") or "this history topic"
    if any(word in text for word in ["source", "evidence", "interpretation", "historian"]):
        return (
            f"A source gives one viewpoint about {focus_label}. Explain one useful piece of evidence a historian could take from it and one limitation of using it on its own.",
            [
                "Identify what the source directly says or shows.",
                "Link that evidence to the historical issue.",
                "Add one limitation about perspective, purpose, or missing context.",
            ],
            [
                f"The source can be useful because it gives evidence linked to {focus_label}.",
                "A strong answer selects a specific detail rather than saying the source is generally useful.",
                "The limitation is that one source may reflect one viewpoint, purpose, or moment in time.",
                "So the source should be checked against other evidence before reaching a judgement.",
            ],
            [
                "Uses evidence from the source.",
                "Explains usefulness and limitation separately.",
                "Avoids treating one source as the whole story.",
            ],
        )
    if any(
        word in text
        for word in ["change", "continuity", "transformation", "developments", "medicine"]
    ):
        return (
            f"Explain one important change and one important continuity in {focus_label}.",
            [
                "Pick one change in the period.",
                "Pick one feature that stayed similar.",
                "Link both points to the same historical theme.",
            ],
            [
                f"One change in {focus_label} can be explained by identifying what was different by the end of the period.",
                "One continuity can be shown by naming something that still worked in a similar way.",
                "The answer should compare before and after, not just list facts.",
                "A balanced response explains why both change and continuity matter.",
            ],
            [
                "Includes both change and continuity.",
                "Uses the period or topic named in the question.",
                "Makes a comparison rather than a timeline only.",
            ],
        )
    if any(
        word in text
        for word in ["cause", "causes", "origins", "war", "conflict", "revolution", "crisis"]
    ):
        if number % 2:
            return (
                f"Explain two causes that could help account for {focus_label}.",
                [
                    "Choose two different factors.",
                    "Explain how each factor contributed.",
                    "Show which factor was more direct or important if the command asks for judgement.",
                ],
                [
                    f"One cause of {focus_label} should be stated clearly.",
                    "The answer then explains the link between that factor and the event or development.",
                    "A second cause should be different, not the same point repeated.",
                    "The strongest answer connects causes together instead of listing isolated facts.",
                ],
                [
                    "Gives two distinct causes.",
                    "Uses because/therefore reasoning.",
                    "Keeps the explanation inside the named period or topic.",
                ],
            )
        return (
            f"Describe one short-term cause and one longer-term cause linked to {focus_label}.",
            [
                "Separate immediate triggers from background conditions.",
                "Explain each cause in context.",
                "Avoid turning the answer into a simple date list.",
            ],
            [
                f"A short-term cause of {focus_label} is the kind of trigger close to the event.",
                "A longer-term cause is a deeper condition or tension built up over time.",
                "Both causes need explanation, not just names.",
                "This structure helps show why the event happened when it did.",
            ],
            [
                "Distinguishes short-term and longer-term causes.",
                "Explains each cause.",
                "Uses historical causation rather than a maths or science template.",
            ],
        )
    return (
        f"Using {focus_label}, explain what happened, why it mattered, and one consequence for people, government, society, or international relations.",
        [
            "State the event, period, or development.",
            "Explain why it mattered in context.",
            "Add one consequence that follows from the explanation.",
        ],
        [
            f"The answer starts by identifying the historical focus: {focus_label}.",
            "It then explains importance by linking the focus to a wider issue or period.",
            "A consequence should follow logically from the event or development.",
            "The final sentence should answer the command word rather than just retell facts.",
        ],
        [
            "Uses historical context.",
            "Includes importance or consequence.",
            "Does not borrow a mathematics, science, or accounting template.",
        ],
    )
