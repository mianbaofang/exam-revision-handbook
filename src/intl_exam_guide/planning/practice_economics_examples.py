from __future__ import annotations


def economics_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if "dynamics of competition" in text or "short-run and long-run benefits" in text:
        if number % 2:
            return (
                "Several online supermarkets enter the same local market. Analyse one short-run benefit and one possible long-run benefit for consumers.",
                [
                    "Identify the competitive pressure.",
                    "Explain a short-run benefit.",
                    "Explain a longer-run benefit.",
                ],
                [
                    "More rival firms increase competitive pressure.",
                    "In the short run, consumers may benefit from lower prices, promotions, or better service as firms try to attract them.",
                    "In the long run, firms may become more efficient or innovate to keep customers.",
                    "This can increase consumer choice or improve value, although the result is not guaranteed.",
                ],
                [
                    "Separates short-run and long-run effects.",
                    "Links benefits to competition.",
                    "Avoids saying every firm or consumer always gains.",
                ],
            )
        return (
            "A new competitor enters a market for budget gyms. Explain how competition could affect firms and consumers over time.",
            [
                "State the immediate competitive response.",
                "Explain the firm's longer-run adjustment.",
                "Link the outcome to consumers.",
            ],
            [
                "Existing gyms may respond quickly with lower prices, offers, or better service.",
                "Over time they may reduce costs, improve facilities, or introduce new membership options.",
                "Consumers may gain from better value and more choice.",
                "However, benefits depend on whether competition remains strong.",
            ],
            [
                "Includes time period language.",
                "Explains firm behaviour, not only price.",
                "Links the outcome to consumer benefit.",
            ],
        )
    if (
        "competitive market process" in text
        or "compete on price" in text
        or "quality of the service" in text
    ):
        if number % 2:
            return (
                "Two cafes sell similar drinks on the same street. One cafe keeps prices the same but introduces faster service and a loyalty app. Analyse how this is part of the competitive market process.",
                [
                    "Identify the form of competition.",
                    "Explain how the firm is trying to attract customers.",
                    "Link the response to product quality, cost or service improvement.",
                ],
                [
                    "This is non-price competition because the cafe is not mainly lowering price.",
                    "Faster service and a loyalty app can make the product more attractive to customers.",
                    "Competition gives firms an incentive to improve service quality or reduce costs so they can keep or gain customers.",
                    "So the competitive market process can improve products and service even when prices do not change.",
                ],
                [
                    "Uses non-price competition.",
                    "Links competition to firm behaviour.",
                    "Mentions product, cost, quality or service improvement.",
                ],
            )
        return (
            "A phone producer faces several close competitors. Instead of cutting price, it improves battery life and after-sales support. Explain why competition can lead to these changes.",
            [
                "State that firms can compete in ways other than price.",
                "Explain the incentive created by rival firms.",
                "Connect the change to quality, cost or service.",
            ],
            [
                "Firms do not only compete by lowering prices.",
                "When rivals offer close alternatives, a producer has an incentive to make its product more attractive.",
                "Improving battery life raises product quality and better after-sales support improves service.",
                "These changes help the firm attract or retain customers in a competitive market.",
            ],
            [
                "Does not reduce competition to price only.",
                "Explains the incentive from rivals.",
                "Uses quality or service as the outcome.",
            ],
        )
    if any(
        word in text
        for word in ["need", "want", "economic activity", "basic economic problem", "scarcity"]
    ):
        if number % 2:
            return (
                "A family wants a larger apartment, a holiday and extra tutoring, but its monthly income is limited. Explain the basic economic problem in this situation.",
                [
                    "Identify unlimited wants.",
                    "Identify the limited resource.",
                    "Explain why choices must be made.",
                ],
                [
                    "The family's wants include housing, a holiday and tutoring.",
                    "The limited resource is monthly income.",
                    "Because income is scarce, the family cannot satisfy every want at once.",
                    "This is the basic economic problem: limited resources but unlimited wants.",
                ],
                [
                    "Uses wants and scarce resources.",
                    "Explains why choice is needed.",
                    "Does not treat income as unlimited.",
                ],
            )
        return (
            "A student has $20 and must choose between buying a revision guide and going to the cinema. Explain how scarcity creates an economic choice.",
            [
                "Identify the limited resource.",
                "Name the two competing wants.",
                "Explain why a choice has to be made.",
            ],
            [
                "The limited resource is the student's $20.",
                "The student wants both the revision guide and the cinema trip.",
                "Because the money is scarce, both wants cannot be satisfied at the same time.",
                "So the student must choose one option and give up the other.",
            ],
            [
                "Names the scarce resource.",
                "Uses needs/wants or choice language.",
                "Explains why not all wants can be satisfied.",
            ],
        )
    if any(word in text for word in ["specialisation", "division of labour", "exchange"]):
        if number % 2:
            return (
                "A car factory splits production into design, assembly and quality-checking teams. Explain how specialisation can improve output and give one risk.",
                [
                    "Identify specialised tasks.",
                    "Explain one productivity benefit.",
                    "Give one possible risk.",
                ],
                [
                    "Workers and teams focus on particular tasks.",
                    "This can increase output because workers build skill and save time switching tasks.",
                    "One risk is that work may become repetitive or production may stop if one stage fails.",
                    "So specialisation can raise efficiency but can create dependence between stages.",
                ],
                [
                    "Benefit and risk are both present.",
                    "The answer uses the factory context.",
                    "It links specialisation to output.",
                ],
            )
        return (
            "In a sandwich shop, one worker prepares bread, one adds fillings and one handles payments. Explain one benefit and one possible cost of division of labour.",
            ["Describe the specialised roles.", "Give one benefit.", "Give one cost."],
            [
                "Each worker focuses on a narrow task.",
                "A benefit is higher output because workers become faster at their task.",
                "A possible cost is boredom or lower motivation from repeated work.",
                "So division of labour can raise productivity but may affect workers negatively.",
            ],
            [
                "Benefit and cost are both included.",
                "The answer uses the sandwich-shop scenario.",
                "It links specialisation to productivity.",
            ],
        )
    if any(word in text for word in ["factor", "land", "capital", "enterprise"]):
        if number % 2:
            return (
                "A delivery business uses vans, drivers, fuel and a founder who organises the firm. Classify each resource as land, labour, capital or enterprise.",
                [
                    "Identify natural resources.",
                    "Identify human effort.",
                    "Separate man-made equipment from enterprise.",
                ],
                [
                    "Fuel is land because it comes from natural resources.",
                    "Drivers are labour because they provide human effort.",
                    "Vans are capital because they are man-made equipment used in production.",
                    "The founder is enterprise because they organise resources and take risk.",
                ],
                [
                    "All resources are classified.",
                    "Capital means equipment, not just money.",
                    "Enterprise is linked to organisation and risk.",
                ],
            )
        return (
            "A bakery uses wheat, ovens, workers and an owner who takes the business risk. Classify each as a factor of production.",
            [
                "Match each resource to land, labour, capital or enterprise.",
                "State the reward for at least one factor.",
                "Keep the classification tied to the scenario.",
            ],
            [
                "Wheat is land because it is a natural resource.",
                "Workers are labour because they provide human effort.",
                "Ovens are capital because they are man-made equipment used in production.",
                "The owner is enterprise because they organise resources and take risk.",
            ],
            [
                "All four factors are classified.",
                "Capital is not money in this context; it is equipment.",
                "Enterprise is linked to risk and organisation.",
            ],
        )
    if any(word in text for word in ["opportunity cost", "resource allocation", "making choices"]):
        if number % 2:
            return (
                "A government can spend the same budget on either a new clinic or a sports centre. If it chooses the clinic, explain the opportunity cost.",
                [
                    "Identify the chosen project.",
                    "Identify the next best alternative.",
                    "State what is given up.",
                ],
                [
                    "The chosen project is the clinic.",
                    "The next best alternative is the sports centre.",
                    "The opportunity cost is the sports centre that cannot be built with the same budget.",
                    "So opportunity cost is the value of the next best alternative forgone.",
                ],
                [
                    "Only the next best alternative is counted.",
                    "The answer uses the budget constraint.",
                    "The forgone option is named.",
                ],
            )
        return (
            "A school can use one classroom for either an economics club or a revision workshop. Explain the opportunity cost of choosing the economics club.",
            [
                "Identify the chosen option.",
                "Identify the next best alternative given up.",
                "State opportunity cost clearly.",
            ],
            [
                "The school chooses the economics club.",
                "The next best alternative is the revision workshop.",
                "The opportunity cost is the revision workshop that cannot happen in that classroom.",
                "Answer: opportunity cost is the value of the next best alternative forgone.",
            ],
            [
                "Opportunity cost is not every possible alternative.",
                "The answer names the forgone option.",
                "The context is used.",
            ],
        )
    if any(
        word in text
        for word in ["sector", "goods and services", "primary", "secondary", "tertiary"]
    ):
        if number % 2:
            return (
                "Classify a fishing boat, a canned-fish factory and a supermarket into economic sectors.",
                [
                    "Match each activity to a sector.",
                    "Explain each classification briefly.",
                    "Separate production from selling.",
                ],
                [
                    "The fishing boat is primary because it extracts a natural resource.",
                    "The canned-fish factory is secondary because it manufactures a product.",
                    "The supermarket is tertiary because it provides retail services to consumers.",
                    "Answer: primary, secondary and tertiary respectively.",
                ],
                [
                    "Each sector is used once.",
                    "Manufacturing is secondary.",
                    "Retail service is tertiary.",
                ],
            )
        return (
            "Classify a wheat farm, a flour mill and a bakery cafe into economic sectors, then explain the difference between a good and a service.",
            [
                "Identify primary, secondary and tertiary activities.",
                "Classify each business.",
                "Separate goods from services.",
            ],
            [
                "The wheat farm is primary because it extracts or grows raw materials.",
                "The flour mill is secondary because it manufactures a product.",
                "The bakery cafe is tertiary when it sells food and service to customers.",
                "A good is a physical item; a service is an activity provided for someone.",
            ],
            [
                "Each sector is named correctly.",
                "The cafe example includes service.",
                "The answer does not treat every business as one sector automatically.",
            ],
        )
    if any(word in text for word in ["demand", "supply", "price", "equilibrium", "market"]):
        if number % 2:
            return (
                "A drought reduces the supply of oranges while demand stays unchanged. Explain the likely effect on equilibrium price and quantity.",
                [
                    "Identify the supply change.",
                    "State the direction of the shift.",
                    "Explain the new equilibrium.",
                ],
                [
                    "A drought reduces supply, so the supply curve shifts left.",
                    "At the old price there is excess demand.",
                    "The equilibrium price is likely to rise.",
                    "The equilibrium quantity is likely to fall.",
                ],
                [
                    "Uses supply, not demand, as the cause.",
                    "Explains price and quantity.",
                    "Keeps demand unchanged.",
                ],
            )
        return (
            "A new phone becomes more popular. Using demand and supply, explain what is likely to happen to its market price, assuming supply is unchanged.",
            [
                "Identify which curve changes.",
                "State the direction of the shift.",
                "Explain the effect on equilibrium price.",
            ],
            [
                "Popularity affects demand, not supply.",
                "Demand shifts to the right.",
                "At the old price there is excess demand.",
                "Market price is likely to rise to a new equilibrium.",
            ],
            [
                "Uses demand, not just 'people like it'.",
                "Supply is held unchanged.",
                "Explains the price rise through excess demand.",
            ],
        )
    if "elasticity" in text:
        if number % 2:
            return (
                "Price falls by 20% and quantity demanded rises by 40%. Calculate price elasticity of demand and state whether demand is elastic or inelastic.",
                [
                    "Use PED = percentage change in quantity demanded / percentage change in price.",
                    "Substitute the percentages.",
                    "Interpret the absolute value.",
                ],
                [
                    "PED = 40% / -20%.",
                    "PED = -2.",
                    "The absolute value is 2, which is greater than 1.",
                    "Demand is price elastic.",
                ],
                [
                    "Quantity demanded is divided by price.",
                    "The sign is interpreted carefully.",
                    "Elasticity judgement uses absolute value.",
                ],
            )
        return (
            "Price rises by 10% and quantity demanded falls by 5%. Calculate price elasticity of demand and state whether demand is elastic or inelastic.",
            [
                "Use PED = percentage change in quantity demanded / percentage change in price.",
                "Substitute the two percentages.",
                "Interpret the absolute value.",
            ],
            [
                "PED = -5% / 10%.",
                "PED = -0.5.",
                "The absolute value is 0.5, which is less than 1.",
                "Demand is price inelastic.",
            ],
            [
                "Quantity demanded change is divided by price change.",
                "The negative sign is expected for demand.",
                "Elastic/inelastic judgement uses absolute value.",
            ],
        )
    if any(word in text for word in ["cost", "revenue", "profit", "production"]):
        if number % 2:
            return (
                "A firm sells 150 units at $12 each. Its total cost is $1,350. Calculate total revenue and profit.",
                [
                    "Total revenue = price x quantity.",
                    "Profit = total revenue - total cost.",
                    "Keep the currency.",
                ],
                [
                    "Total revenue = $12 x 150 = $1,800.",
                    "Profit = $1,800 - $1,350.",
                    "Profit = $450.",
                    "Answer: total revenue $1,800; profit $450.",
                ],
                [
                    "Revenue is calculated before profit.",
                    "Cost is subtracted once.",
                    "Currency is shown.",
                ],
            )
        return (
            "A producer sells 200 units at $8 each. Total cost is $1,100. Calculate total revenue and profit.",
            [
                "Total revenue = price x quantity.",
                "Profit = total revenue - total cost.",
                "Keep the currency.",
            ],
            [
                "Total revenue = $8 x 200 = $1,600.",
                "Profit = $1,600 - $1,100.",
                "Profit = $500.",
                "Answer: total revenue $1,600; profit $500.",
            ],
            [
                "Revenue is not the same as profit.",
                "Costs are subtracted after revenue is calculated.",
                "Currency is shown.",
            ],
        )
    if any(
        word in text
        for word in [
            "government",
            "inflation",
            "growth",
            "employment",
            "income",
            "balance of payments",
        ]
    ):
        if number % 2:
            return (
                "A government cuts taxes to reduce unemployment. Explain one possible benefit and one possible inflation risk.",
                [
                    "Identify the policy effect on spending.",
                    "Link spending to jobs.",
                    "Explain the inflation risk.",
                ],
                [
                    "Lower taxes can increase households' disposable income.",
                    "Higher spending may raise demand for goods and services, encouraging firms to hire more workers.",
                    "If demand rises faster than output, prices may rise.",
                    "So the policy may reduce unemployment but create inflationary pressure.",
                ],
                [
                    "Benefit and risk are both included.",
                    "Uses demand as the link.",
                    "Avoids saying the outcome is guaranteed.",
                ],
            )
        return (
            "A government wants lower inflation and faster economic growth at the same time. Explain why these objectives might conflict.",
            ["Name both objectives.", "Explain the policy tension.", "Give a balanced conclusion."],
            [
                "Lower inflation may require policies that reduce spending in the economy.",
                "Reduced spending can slow output growth.",
                "Faster growth may increase demand and put upward pressure on prices.",
                "So policies for one objective can make the other harder to achieve.",
            ],
            [
                "Both objectives are named.",
                "The answer explains a trade-off.",
                "It avoids saying conflict always happens.",
            ],
        )
    if any(
        word in text for word in ["trade", "exchange rate", "globalisation", "import", "export"]
    ):
        if number % 2:
            return (
                "A tariff is placed on imported shoes. Explain one likely effect on domestic consumers and one effect on domestic producers.",
                [
                    "Define the import barrier effect.",
                    "Apply it to consumers.",
                    "Apply it to producers.",
                ],
                [
                    "A tariff raises the cost of imported shoes.",
                    "Consumers may face higher prices or less choice.",
                    "Domestic producers may benefit because imported competitors become more expensive.",
                    "So consumers may lose, while some domestic producers may gain.",
                ],
                [
                    "Consumers and producers are separated.",
                    "The price effect is clear.",
                    "The answer avoids claiming everyone benefits.",
                ],
            )
        return (
            "A country's currency appreciates. Explain one likely effect on exporters and one likely effect on consumers buying imports.",
            [
                "Define the direction of the exchange-rate change.",
                "Apply it to export prices.",
                "Apply it to import prices.",
            ],
            [
                "Appreciation means the currency becomes stronger.",
                "Exports may become more expensive for foreign buyers, so exporters may sell less.",
                "Imports become cheaper for domestic consumers.",
                "Answer: exporters may lose competitiveness, while consumers may benefit from cheaper imports.",
            ],
            [
                "Exporter and consumer effects are separated.",
                "The direction of price change is correct.",
                "The answer links to competitiveness.",
            ],
        )
    if any(word in text for word in ["money", "bank", "financial", "interest"]):
        if number % 2:
            return (
                "A central bank raises interest rates. Explain one likely effect on saving and one likely effect on borrowing.",
                [
                    "Identify the interest-rate change.",
                    "Apply it to savers.",
                    "Apply it to borrowers.",
                ],
                [
                    "Higher interest rates increase the reward for saving.",
                    "Savers may choose to save more.",
                    "Borrowing becomes more expensive because loan repayments or interest costs rise.",
                    "So borrowing may fall while saving may rise.",
                ],
                [
                    "Saving and borrowing are both covered.",
                    "Direction of change is correct.",
                    "The answer uses incentives.",
                ],
            )
        return (
            "Explain how a commercial bank can help savers and borrowers in the economy.",
            [
                "Identify the two groups.",
                "Explain the service for savers.",
                "Explain the service for borrowers.",
            ],
            [
                "Savers can deposit money and earn interest.",
                "Borrowers can receive loans for spending or investment.",
                "The bank links people with surplus funds to people who need funds.",
                "This supports saving, borrowing and investment in the economy.",
            ],
            [
                "Mentions savers and borrowers.",
                "Uses the role of a bank, not just money storage.",
                "Links to the wider economy.",
            ],
        )
    return (
        f"Use the economics idea '{focus}' in a short market scenario: identify the economic agent, explain the incentive, and state the likely outcome.",
        [
            "Name the economic agent.",
            "Identify the incentive or constraint.",
            "Explain the likely outcome.",
        ],
        [
            f"The focus idea is {focus}.",
            "Apply it to a consumer, producer or government decision.",
            "Explain how incentives or scarcity affect the decision.",
            "Finish with the likely economic outcome.",
        ],
        [
            "Uses an economics agent.",
            "Explains a cause-and-effect link.",
            "Avoids unsupported real-world claims.",
        ],
    )
