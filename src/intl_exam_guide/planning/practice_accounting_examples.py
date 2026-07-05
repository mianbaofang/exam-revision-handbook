from __future__ import annotations

from intl_exam_guide.planning.subject_profiles import has_terms


def accounting_example(
    text: str,
    focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(
        text,
        [
            "source document",
            "source documents",
            "prime entry",
            "ledger",
            "double entry",
            "recording of transactions",
        ],
    ):
        if number % 2:
            return (
                "A business receives a purchase invoice for goods bought on credit. State one source document, name the book of prime entry, and explain why the transaction is later posted to ledger accounts.",
                [
                    "Identify the evidence document.",
                    "Choose the correct book of prime entry.",
                    "Link prime entry to ledger posting.",
                ],
                [
                    "The source document is the purchase invoice.",
                    "The transaction is first recorded in the purchases journal.",
                    "It is later posted to ledger accounts so the double entry records are updated.",
                    "This keeps a trace from source document to book of prime entry to ledger.",
                ],
                [
                    "Uses an accounting source document.",
                    "Names a book of prime entry.",
                    "Does not treat the journal and ledger as the same record.",
                ],
            )
        return (
            "A trader sells goods on credit and issues a sales invoice. Explain how this source document starts the accounting record.",
            [
                "Name the source document.",
                "Name the first accounting book used.",
                "Explain the link to ledger accounts.",
            ],
            [
                "The sales invoice is the source document.",
                "The sale is first recorded in the sales journal.",
                "The amount is then posted to the receivables ledger and general ledger as part of the double entry system.",
                "So the original business event is supported by a document and recorded systematically.",
            ],
            [
                "The answer starts with a source document.",
                "Credit sale is not treated as immediate cash.",
                "Ledger posting follows the book of prime entry.",
            ],
        )
    if has_terms(
        text,
        [
            "trial balance",
            "control account",
            "bank reconciliation",
            "suspense account",
            "correction of errors",
            "verification",
        ],
    ):
        if number % 2:
            return (
                "A cash book shows a different balance from the bank statement. Explain two reasons why the balances may differ and name the statement used to compare them.",
                [
                    "Identify timing differences or errors.",
                    "Name the reconciliation document.",
                    "Keep cash book and bank statement separate.",
                ],
                [
                    "One reason is unpresented cheques: payments recorded in the cash book but not yet processed by the bank.",
                    "Another reason is outstanding bankings: receipts recorded by the business but not yet shown by the bank.",
                    "A bank reconciliation statement is prepared to compare and explain the difference.",
                    "This verifies the cash book against external bank evidence.",
                ],
                [
                    "Uses bank reconciliation language.",
                    "Gives reasons for disagreement.",
                    "Does not say one balance is automatically wrong.",
                ],
            )
        return (
            "A trial balance does not agree. State one error that could cause this and one error that a trial balance may not reveal.",
            [
                "Separate revealed and unrevealed errors.",
                "Name specific error types.",
                "Explain the limitation.",
            ],
            [
                "A partial omission can cause the trial balance not to agree because only one side of the double entry is recorded.",
                "An error of principle may not be revealed if equal debit and credit amounts were still posted.",
                "Therefore the trial balance checks arithmetic equality, not every accounting error.",
                "It is a verification tool with limitations.",
            ],
            [
                "Mentions double entry equality.",
                "Includes one revealed and one unrevealed error.",
                "Explains the limitation, not just the name.",
            ],
        )
    if has_terms(
        text,
        [
            "depreciation",
            "non-current asset",
            "irrecoverable",
            "receivables",
            "payables",
            "accrual",
            "prudence",
            "going concern",
            "accounting concepts",
        ],
    ):
        if number % 2:
            return (
                "A machine costing $5,000 is depreciated by 20% per year using the straight-line method. Calculate the annual depreciation and explain why depreciation is recorded.",
                [
                    "Use cost x rate.",
                    "State the annual depreciation.",
                    "Link the charge to asset use over time.",
                ],
                [
                    "Annual depreciation = $5,000 x 20%.",
                    "Annual depreciation = $1,000.",
                    "Depreciation records part of the asset's cost as an expense for the period it helps generate revenue.",
                    "This avoids treating a long-term asset as if it were used up immediately.",
                ],
                [
                    "Uses the stated method.",
                    "Keeps depreciation separate from cash payment.",
                    "Explains the accounting purpose.",
                ],
            )
        return (
            "A customer debt of $300 is judged irrecoverable. Explain the accounting treatment and its effect on profit.",
            ["Identify the debt.", "Record the expense effect.", "Link it to profit."],
            [
                "The irrecoverable debt is removed from trade receivables.",
                "It is recorded as an expense in the income statement.",
                "Expenses increase by $300, so profit decreases by $300.",
                "This applies prudence by not overstating receivables.",
            ],
            [
                "Receivables and expense are both mentioned.",
                "Profit effect direction is correct.",
                "The answer links to an accounting concept.",
            ],
        )
    if has_terms(
        text,
        [
            "financial statements",
            "income statement",
            "statement of financial position",
            "partnership",
            "sole trader",
            "limited company",
            "manufacturing account",
            "non-profit",
            "incomplete records",
        ],
    ):
        if number % 2:
            return (
                "A sole trader has sales of $18,000, cost of sales of $11,000 and expenses of $3,200. Calculate gross profit and profit for the year.",
                [
                    "Calculate gross profit first.",
                    "Subtract expenses after gross profit.",
                    "Keep the currency.",
                ],
                [
                    "Gross profit = sales - cost of sales.",
                    "Gross profit = $18,000 - $11,000 = $7,000.",
                    "Profit for the year = $7,000 - $3,200 = $3,800.",
                    "Answer: gross profit $7,000; profit for the year $3,800.",
                ],
                [
                    "Cost of sales is subtracted from sales.",
                    "Expenses are subtracted after gross profit.",
                    "Currency is shown.",
                ],
            )
        return (
            "A partnership agreement gives a partner a salary of $2,000 and interest on capital of $500. Explain where these items are shown in the partnership financial statements.",
            [
                "Identify the organisation type.",
                "Name the relevant statement/account.",
                "Explain the purpose.",
            ],
            [
                "The business is a partnership.",
                "Partner salary and interest on capital are recorded in the appropriation account.",
                "They show how profit is shared between partners after the income statement profit is calculated.",
                "They are not ordinary business expenses in the same way as rent or wages.",
            ],
            [
                "Names the appropriation account.",
                "Separates profit sharing from normal expenses.",
                "Uses partnership context.",
            ],
        )
    if has_terms(
        text,
        [
            "ratio",
            "profitability",
            "liquidity",
            "trade receivable days",
            "trade payable days",
            "appraising business performance",
        ],
    ):
        if number % 2:
            return (
                "A business has current assets of $12,000 and current liabilities of $8,000. Calculate the current ratio and comment briefly on liquidity.",
                [
                    "Use current assets divided by current liabilities.",
                    "Simplify the ratio.",
                    "Comment on ability to meet short-term debts.",
                ],
                [
                    "Current ratio = 12,000 : 8,000.",
                    "Simplified current ratio = 1.5 : 1.",
                    "This means the business has $1.50 of current assets for each $1 of current liabilities.",
                    "It suggests some ability to meet short-term debts, but more evidence is needed for a full judgement.",
                ],
                [
                    "Uses current assets and liabilities.",
                    "Ratio is simplified.",
                    "Comment is cautious and evidence-based.",
                ],
            )
        return (
            "A business has gross profit of $9,000 and sales revenue of $30,000. Calculate the gross profit margin.",
            [
                "Use gross profit / sales revenue x 100.",
                "Substitute the figures.",
                "Add the percentage sign.",
            ],
            [
                "Gross profit margin = 9,000 / 30,000 x 100.",
                "9,000 / 30,000 = 0.3.",
                "0.3 x 100 = 30%.",
                "Answer: gross profit margin is 30%.",
            ],
            [
                "Gross profit is the numerator.",
                "Sales revenue is the denominator.",
                "Answer is a percentage.",
            ],
        )
    return (
        f"Use the accounting idea '{focus}' in a short business scenario: identify the document, account, statement, or calculation involved, then explain the effect on the records.",
        [
            "Identify the accounting evidence or record.",
            "Apply the named accounting rule.",
            "State the effect on the accounts or statement.",
        ],
        [
            f"The focus idea is {focus}.",
            "First connect the business event to the correct accounting record.",
            "Then apply the calculation, classification, or double entry logic required.",
            "Finish by stating the effect on profit, assets, liabilities, equity, or control of records.",
        ],
        [
            "Uses accounting records or statements.",
            "Explains the effect, not just the term.",
            "Does not borrow a question from another subject.",
        ],
    )


def accounting_example_zh(
    text: str,
    visible_focus: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(text, ["source document", "prime entry", "ledger", "double entry", "recording"]):
        return (
            "一家企业赊购商品并收到购货发票。说明这张原始凭证如何进入会计记录。",
            ["先指出原始凭证。", "再指出首次记录的账簿。", "最后说明如何进入分类账。"],
            [
                "购货发票是原始凭证。",
                "赊购交易先记录在购货日记账。",
                "之后再过账到相关分类账账户。",
                "这样交易就能从凭证追踪到初始记录和分类账。",
            ],
            ["要有原始凭证。", "要区分初始记录账簿和分类账。", "不能把赊购当作现金交易。"],
        )
    if has_terms(
        text, ["trial balance", "bank reconciliation", "control account", "verification", "error"]
    ):
        return (
            "现金簿余额和银行对账单余额不同。说明两个可能原因，并说出用于核对的报表。",
            ["找出时间差或错误。", "说出银行调节表。", "区分现金簿和银行对账单。"],
            [
                "可能原因之一是未兑现支票。",
                "另一个可能原因是在途存款。",
                "企业会编制银行调节表来解释差异。",
                "这可以用外部银行资料核对现金簿。",
            ],
            ["原因要具体。", "要说出银行调节。", "不能默认某一方一定错。"],
        )
    if has_terms(
        text, ["financial statements", "income statement", "profit", "ratio", "liquidity"]
    ):
        return (
            "某企业销售收入为 $18,000，销售成本为 $11,000，费用为 $3,200。计算毛利和本年利润。",
            ["先算毛利。", "再扣除费用。", "保留货币单位。"],
            [
                "毛利 = 销售收入 - 销售成本。",
                "$18,000 - $11,000 = $7,000。",
                "本年利润 = $7,000 - $3,200 = $3,800。",
                "答案：毛利为 $7,000，本年利润为 $3,800。",
            ],
            ["不要先扣费用。", "货币单位要保留。", "毛利和本年利润要区分。"],
        )
    return (
        f"围绕“{visible_focus}”完成一道会计情境题：判断相关凭证、账户、报表或计算，并说明对会计记录的影响。",
        ["找出业务事件。", "匹配对应会计记录或规则。", "说明对账户或报表的影响。"],
        [
            f"本题考查“{visible_focus}”。",
            "先把业务事件转成会计语言。",
            "再应用分类、计算或复式记账逻辑。",
            "最后说明对利润、资产、负债、权益或记录核对的影响。",
        ],
        ["使用会计记录或报表。", "说明影响，而不是只背词。", "没有借用其他科目的题型。"],
    )
