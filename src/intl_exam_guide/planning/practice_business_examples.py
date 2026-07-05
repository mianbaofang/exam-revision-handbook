from __future__ import annotations


def business_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if any(word in text for word in ["stakeholder", "stakeholders"]):
        return (
            "A business plans to extend opening hours. Explain how this decision could affect two stakeholder groups differently.",
            [
                "Name two stakeholder groups.",
                "Explain a different objective or concern for each group.",
                "Link the effect to the business decision.",
            ],
            [
                "Customers may benefit because longer opening hours make the business more convenient.",
                "Employees may be affected because longer hours could change shifts or work-life balance.",
                "The same decision can therefore create different benefits and costs for different stakeholders.",
                "A strong answer names the stakeholder and explains the effect, not just lists them.",
            ],
            [
                "Uses two stakeholder groups.",
                "Explains different objectives or effects.",
                "Links both points to the decision.",
            ],
        )
    if any(
        word in text
        for word in ["ownership", "sole trader", "partnership", "limited company", "franchise"]
    ):
        return (
            "A small cafe owner is deciding whether to remain a sole trader or form a partnership. Explain one benefit and one drawback of changing to a partnership.",
            [
                "Identify the ownership options.",
                "Give one benefit of partnership.",
                "Give one drawback or risk.",
            ],
            [
                "A partnership may bring extra finance, ideas or shared workload.",
                "A drawback is that decisions and profits may need to be shared.",
                "The best choice depends on the owner's need for control, finance and expertise.",
                "This is a business ownership judgement, not just a definition.",
            ],
            [
                "Benefit and drawback are both included.",
                "Control or finance is mentioned.",
                "The answer uses the cafe context.",
            ],
        )
    if any(
        word in text
        for word in [
            "marketing",
            "market research",
            "marketing mix",
            "product",
            "price",
            "promotion",
            "place",
            "segmentation",
        ]
    ):
        return (
            "A sportswear business is launching a new trainer for teenagers. Explain how one marketing mix decision could help it reach the target market.",
            [
                "Identify the target market.",
                "Choose one marketing mix element.",
                "Explain how that decision supports sales.",
            ],
            [
                "The target market is teenagers.",
                "Promotion through social media could reach customers where they are likely to see the product.",
                "The message should match the product and customer needs.",
                "This links the marketing decision to the chosen market segment.",
            ],
            [
                "Uses a marketing mix element.",
                "Links to the target market.",
                "Explains why the decision could affect demand.",
            ],
        )
    if any(
        word in text
        for word in ["quality", "production", "operations", "stock control", "inventory"]
    ):
        return (
            "A bakery receives complaints that some products are stale. Explain one quality problem and one action the business could take to improve operations.",
            [
                "Identify the quality issue.",
                "Suggest an operational action.",
                "Explain how the action could reduce the problem.",
            ],
            [
                "The quality problem is that customers are receiving stale products.",
                "The business could improve stock rotation or reduce overproduction.",
                "This helps ensure older stock is sold first or less unsold stock remains.",
                "Better operations can improve customer satisfaction and reduce waste.",
            ],
            [
                "Names a quality or operations problem.",
                "Suggests a realistic business action.",
                "Explains the effect on customers, waste or costs.",
            ],
        )
    if any(
        word in text
        for word in [
            "cash flow",
            "break-even",
            "breakeven",
            "finance",
            "cost",
            "revenue",
            "profit",
            "payback",
        ]
    ):
        return (
            "A business has fixed costs of $600, variable costs of $4 per unit and sells each unit for $10. Calculate the break-even output.",
            [
                "Find contribution per unit.",
                "Use fixed costs divided by contribution.",
                "State the output in units.",
            ],
            [
                "Contribution per unit = selling price - variable cost.",
                "Contribution = $10 - $4 = $6.",
                "Break-even output = $600 / $6 = 100 units.",
                "The business must sell 100 units to cover total costs.",
            ],
            [
                "Uses contribution correctly.",
                "Divides fixed costs by contribution.",
                "Answer is in units.",
            ],
        )
    if any(
        word in text
        for word in ["location", "e-commerce", "digital", "communication", "technology"]
    ):
        return (
            "A retailer is choosing between a town-centre shop and selling mainly online. Explain one factor that could influence this business location or channel decision.",
            [
                "Identify the location or channel choice.",
                "Choose one relevant factor.",
                "Explain the effect on costs, customers or sales.",
            ],
            [
                "A town-centre shop may give access to passing customers but usually has higher rent.",
                "Selling online may reduce premises costs and reach wider customers.",
                "The best option depends on where the target market shops and what costs the business can afford.",
                "The answer links location/channel to business performance.",
            ],
            [
                "Uses a business location or channel factor.",
                "Explains cost or customer access.",
                "Avoids a generic definition-only answer.",
            ],
        )
    if any(
        word in text for word in ["aim", "aims", "objective", "objectives", "growth", "expansion"]
    ):
        return (
            "A new business wants to increase sales in its first year. Explain why setting a clear objective could help decision-making.",
            [
                "State the objective.",
                "Explain how it guides decisions.",
                "Link it to measuring performance.",
            ],
            [
                "The objective is to increase sales.",
                "A clear objective helps managers choose actions such as promotion, pricing or expansion.",
                "It also gives a way to judge whether the business is making progress.",
                "Objectives turn a general aim into a target for decisions.",
            ],
            [
                "Names a business objective.",
                "Explains decision-making use.",
                "Mentions measuring performance or progress.",
            ],
        )
    return (
        f"Use the business idea '{focus}' in a short business scenario: identify the decision, explain one effect on the business, and give one judgement or recommendation.",
        [
            "Identify the business decision or issue.",
            "Explain the likely effect on costs, revenue, customers, workers or owners.",
            "Finish with a judgement linked to the context.",
        ],
        [
            f"The focus idea is {focus}.",
            "Apply it to a named business situation rather than defining it only.",
            "Explain one cause-and-effect link for the business.",
            "Finish by saying what the business should consider before deciding.",
        ],
        [
            "Uses a business context.",
            "Explains an effect on the business or stakeholders.",
            "Avoids a generic definition-only template.",
        ],
    )
