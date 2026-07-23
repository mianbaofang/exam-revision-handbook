from __future__ import annotations

from intl_exam_guide.models import Qualification
from intl_exam_guide.planning.language_policy import glossary_language
from intl_exam_guide.rendering.text import html_escape


TermRow = tuple[str, str, str, str, str]


MATH_TERMS: tuple[TermRow, ...] = (
    ("Function", "函数", "函數", "関数", "A rule that maps each input to one output."),
    ("Domain", "定义域", "定義域", "定義域", "The allowed input values for a function."),
    ("Range", "值域", "值域", "値域", "The possible output values of a function."),
    ("Quadratic", "二次式", "二次式", "二次式", "An expression or equation with highest power 2."),
    (
        "Discriminant",
        "判别式",
        "判別式",
        "判別式",
        "The value b² − 4ac used to decide root types.",
    ),
    ("Root", "根", "根", "解", "A value that makes an equation equal zero."),
    ("Intercept", "截距", "截距", "切片", "Where a graph crosses an axis."),
    ("Gradient", "斜率", "斜率", "傾き", "The rate of change of y with respect to x."),
    (
        "Tangent",
        "切线",
        "切線",
        "接線",
        "A line touching a curve at a point with the same gradient.",
    ),
    ("Normal", "法线", "法線", "法線", "A line perpendicular to the tangent."),
    ("Derivative", "导数", "導數", "導関数", "The instantaneous rate of change of a function."),
    ("Differentiation", "求导", "求導", "微分", "The process of finding a derivative."),
    ("Stationary point", "驻点", "駐點", "停留点", "A point where the derivative is zero."),
    ("Maximum", "最大值", "最大值", "最大値", "A highest local or overall value."),
    ("Minimum", "最小值", "最小值", "最小値", "A lowest local or overall value."),
    (
        "Integral",
        "积分",
        "積分",
        "積分",
        "A quantity found by reversing differentiation or summing area.",
    ),
    (
        "Definite integral",
        "定积分",
        "定積分",
        "定積分",
        "An integral evaluated between two limits.",
    ),
    (
        "Indefinite integral",
        "不定积分",
        "不定積分",
        "不定積分",
        "A family of antiderivatives including + C.",
    ),
    (
        "Area under a curve",
        "曲线下面积",
        "曲線下面積",
        "曲線下の面積",
        "The region measured between a curve and an axis.",
    ),
    (
        "Trapezium rule",
        "梯形法则",
        "梯形法則",
        "台形公式",
        "A numerical method for approximating area under a curve.",
    ),
    (
        "Radian",
        "弧度",
        "弧度",
        "ラジアン",
        "An angle measure based on arc length divided by radius.",
    ),
    ("Sine", "正弦", "正弦", "サイン", "The trigonometric ratio or function sin x."),
    ("Cosine", "余弦", "餘弦", "コサイン", "The trigonometric ratio or function cos x."),
    (
        "Tangent function",
        "正切函数",
        "正切函數",
        "タンジェント関数",
        "The function tan x = sin x / cos x.",
    ),
    ("Periodicity", "周期性", "週期性", "周期性", "A repeating pattern in a function."),
    (
        "Sine rule",
        "正弦定理",
        "正弦定理",
        "正弦定理",
        "A triangle rule linking sides and opposite sines.",
    ),
    ("Cosine rule", "余弦定理", "餘弦定理", "余弦定理", "A triangle rule generalising Pythagoras."),
    (
        "Arithmetic sequence",
        "等差数列",
        "等差數列",
        "等差数列",
        "A sequence with a constant difference.",
    ),
    ("Geometric sequence", "等比数列", "等比數列", "等比数列", "A sequence with a constant ratio."),
    (
        "Binomial expansion",
        "二项式展开",
        "二項式展開",
        "二項展開",
        "The expansion of powers such as (a + b)^n.",
    ),
    ("Logarithm", "对数", "對數", "対数", "The inverse operation to exponentiation."),
    (
        "Exponential function",
        "指数函数",
        "指數函數",
        "指数関数",
        "A function with the variable in the exponent.",
    ),
    ("Probability", "概率", "機率", "確率", "A measure of chance from 0 to 1."),
    ("Mutually exclusive", "互斥", "互斥", "排反", "Events that cannot happen at the same time."),
    (
        "Independent events",
        "独立事件",
        "獨立事件",
        "独立事象",
        "Events where one outcome does not affect the other.",
    ),
    (
        "Random variable",
        "随机变量",
        "隨機變量",
        "確率変数",
        "A variable whose value depends on chance.",
    ),
    ("Expected value", "期望值", "期望值", "期待値", "The long-run mean of a random variable."),
    ("Variance", "方差", "變異數", "分散", "A measure of spread around the mean."),
    ("Standard deviation", "标准差", "標準差", "標準偏差", "The square root of the variance."),
    (
        "Binomial distribution",
        "二项分布",
        "二項分佈",
        "二項分布",
        "A distribution for repeated independent trials.",
    ),
    ("Displacement", "位移", "位移", "変位", "A vector change in position."),
    ("Velocity", "速度", "速度", "速度", "Rate of change of displacement."),
    ("Acceleration", "加速度", "加速度", "加速度", "Rate of change of velocity."),
    (
        "Resultant force",
        "合力",
        "合力",
        "合力",
        "The single force with the same effect as all forces combined.",
    ),
    ("Momentum", "动量", "動量", "運動量", "Mass multiplied by velocity."),
    ("Impulse", "冲量", "衝量", "力積", "Force multiplied by time, equal to change in momentum."),
)

GENERIC_TERMS: tuple[TermRow, ...] = (
    ("Command word", "指令词", "指令詞", "指示語", "The verb that tells you how to answer."),
    ("Definition", "定义", "定義", "定義", "The precise meaning of a term."),
    ("Explain", "解释", "解釋", "説明する", "Give reasons or make the relationship clear."),
    ("Calculate", "计算", "計算", "計算する", "Use numbers or formulae to find an answer."),
    ("Compare", "比较", "比較", "比較する", "Give similarities and differences."),
    ("Evaluate", "评价", "評價", "評価する", "Make a judgement using evidence."),
    ("Evidence", "证据", "證據", "根拠", "Information used to support an answer."),
    ("Conclusion", "结论", "結論", "結論", "The final judgement or answer."),
    ("Assumption", "假设", "假設", "仮定", "A condition treated as true for the task."),
    ("Limitation", "限制", "限制", "限界", "A boundary or weakness in an answer."),
    ("Trend", "趋势", "趨勢", "傾向", "A general direction of change."),
    ("Variable", "变量", "變量", "変数", "A quantity or factor that can change."),
    ("Model", "模型", "模型", "モデル", "A simplified representation used for reasoning."),
    ("Accuracy", "准确度", "準確度", "正確さ", "How close a result is to the true value."),
    ("Reliability", "可靠性", "可靠性", "信頼性", "How consistently a method or source works."),
    (
        "Validity",
        "有效性",
        "有效性",
        "妥当性",
        "How well something measures or proves the intended point.",
    ),
    ("Method", "方法", "方法", "方法", "The process used to answer a question."),
    ("Formula", "公式", "公式", "公式", "A symbolic rule used in calculation."),
    ("Unit", "单位", "單位", "単位", "The measurement label attached to a value."),
    ("Source", "来源", "來源", "出典", "Where information comes from."),
    ("Structure", "结构", "結構", "構造", "The way parts are arranged."),
    ("Process", "过程", "過程", "過程", "A sequence of linked steps."),
    ("Relationship", "关系", "關係", "関係", "How two or more things are connected."),
    ("Cause", "原因", "原因", "原因", "A factor that produces an effect."),
    ("Effect", "结果", "結果", "結果", "What happens because of a cause."),
    ("Risk", "风险", "風險", "リスク", "The possibility of an unwanted outcome."),
    ("Efficiency", "效率", "效率", "効率", "Using resources with minimal waste."),
)

ECONOMICS_TERMS: tuple[TermRow, ...] = (
    ("Scarcity", "稀缺性", "稀缺性", "希少性", "Limited resources compared with unlimited wants."),
    ("Opportunity cost", "机会成本", "機會成本", "機会費用", "The next best alternative given up."),
    (
        "Factors of production",
        "生产要素",
        "生產要素",
        "生産要素",
        "Land, labour, capital and enterprise.",
    ),
    ("Demand", "需求", "需求", "需要", "The willingness and ability to buy."),
    ("Supply", "供给", "供給", "供給", "The willingness and ability to sell."),
    (
        "Market equilibrium",
        "市场均衡",
        "市場均衡",
        "市場均衡",
        "The price and quantity where demand equals supply.",
    ),
    (
        "Elasticity",
        "弹性",
        "彈性",
        "弾力性",
        "Responsiveness to a change in price, income, or another factor.",
    ),
    ("External cost", "外部成本", "外部成本", "外部費用", "A cost borne by a third party."),
    (
        "External benefit",
        "外部收益",
        "外部收益",
        "外部便益",
        "A benefit received by a third party.",
    ),
    (
        "Inflation",
        "通货膨胀",
        "通貨膨脹",
        "インフレーション",
        "A sustained rise in the general price level.",
    ),
    ("Unemployment", "失业", "失業", "失業", "People willing and able to work but without a job."),
    (
        "Exchange rate",
        "汇率",
        "匯率",
        "為替レート",
        "The price of one currency in terms of another.",
    ),
)

ACCOUNTING_TERMS: tuple[TermRow, ...] = (
    (
        "Source document",
        "原始凭证",
        "原始憑證",
        "証憑書類",
        "Evidence used to record a transaction.",
    ),
    (
        "Book of prime entry",
        "初始分录簿",
        "初始分錄簿",
        "補助記入帳",
        "The first book used to record a transaction.",
    ),
    (
        "Ledger account",
        "分类账账户",
        "分類帳帳戶",
        "元帳勘定",
        "A record of increases and decreases in one item.",
    ),
    (
        "Trial balance",
        "试算平衡表",
        "試算平衡表",
        "試算表",
        "A list of ledger balances used to check arithmetic accuracy.",
    ),
    (
        "Bank reconciliation",
        "银行调节表",
        "銀行調節表",
        "銀行勘定調整",
        "A check between cash book and bank statement balances.",
    ),
    (
        "Depreciation",
        "折旧",
        "折舊",
        "減価償却",
        "Allocation of non-current asset cost over useful life.",
    ),
    (
        "Accruals",
        "应计费用",
        "應計費用",
        "未払費用",
        "Expenses incurred but not yet paid or recorded.",
    ),
    (
        "Prepayments",
        "预付款",
        "預付款",
        "前払費用",
        "Amounts paid before the accounting period expense is incurred.",
    ),
    ("Bad debt", "坏账", "壞帳", "貸倒れ", "A receivable that is not expected to be collected."),
    (
        "Control account",
        "控制账户",
        "控制帳戶",
        "統制勘定",
        "A summary account used to check subsidiary ledgers.",
    ),
    (
        "Financial statement",
        "财务报表",
        "財務報表",
        "財務諸表",
        "A formal report of financial performance or position.",
    ),
    ("Gross profit", "毛利", "毛利", "売上総利益", "Revenue minus cost of sales."),
)

BUSINESS_TERMS: tuple[TermRow, ...] = (
    (
        "Stakeholder",
        "利益相关者",
        "利益相關者",
        "利害関係者",
        "A group affected by business decisions.",
    ),
    (
        "Entrepreneur",
        "企业家",
        "企業家",
        "起業家",
        "A person who starts and takes risk in a business.",
    ),
    (
        "Limited liability",
        "有限责任",
        "有限責任",
        "有限責任",
        "Owners' losses are limited to their investment.",
    ),
    (
        "Market segment",
        "细分市场",
        "細分市場",
        "市場セグメント",
        "A group of customers with shared characteristics.",
    ),
    (
        "Marketing mix",
        "营销组合",
        "行銷組合",
        "マーケティングミックス",
        "Product, price, place and promotion decisions.",
    ),
    (
        "Cash flow",
        "现金流",
        "現金流",
        "キャッシュフロー",
        "Money moving into and out of a business.",
    ),
    (
        "Break-even",
        "盈亏平衡",
        "損益分岐",
        "損益分岐点",
        "The output where total revenue equals total cost.",
    ),
    (
        "Quality control",
        "质量控制",
        "品質控制",
        "品質管理",
        "Checking output against quality standards.",
    ),
    (
        "Economies of scale",
        "规模经济",
        "規模經濟",
        "規模の経済",
        "Cost advantages from producing on a larger scale.",
    ),
    (
        "Organisational structure",
        "组织结构",
        "組織結構",
        "組織構造",
        "How roles and reporting lines are arranged.",
    ),
)

SCIENCE_TERMS: tuple[TermRow, ...] = (
    ("Hypothesis", "假设", "假設", "仮説", "A testable scientific explanation."),
    ("Independent variable", "自变量", "自變量", "独立変数", "The variable deliberately changed."),
    (
        "Dependent variable",
        "因变量",
        "因變量",
        "従属変数",
        "The variable measured in an investigation.",
    ),
    (
        "Control variable",
        "控制变量",
        "控制變量",
        "統制変数",
        "A variable kept constant for a fair test.",
    ),
    ("Accuracy", "准确度", "準確度", "正確度", "How close a result is to the true value."),
    ("Precision", "精密度", "精密度", "精度", "How close repeated readings are to each other."),
    (
        "Reliability",
        "可靠性",
        "可靠性",
        "信頼性",
        "How consistently a method gives similar results.",
    ),
    ("Validity", "有效性", "有效性", "妥当性", "Whether a method tests what it is meant to test."),
    ("Anomaly", "异常值", "異常值", "異常値", "A result that does not fit the pattern."),
)

PHYSICS_TERMS: tuple[TermRow, ...] = (
    (
        "Resultant force",
        "合力",
        "合力",
        "合力",
        "The single force with the same effect as all forces combined.",
    ),
    ("Acceleration", "加速度", "加速度", "加速度", "Rate of change of velocity."),
    ("Momentum", "动量", "動量", "運動量", "Mass multiplied by velocity."),
    ("Impulse", "冲量", "衝量", "力積", "Force multiplied by time, equal to change in momentum."),
    (
        "Work done",
        "做功",
        "做功",
        "仕事",
        "Energy transferred by a force moving through a distance.",
    ),
    ("Power", "功率", "功率", "仕事率", "Rate of energy transfer."),
) + SCIENCE_TERMS

CHEMISTRY_TERMS: tuple[TermRow, ...] = (
    ("Atom", "原子", "原子", "原子", "The smallest particle of an element."),
    ("Ion", "离子", "離子", "イオン", "A charged particle formed by gaining or losing electrons."),
    ("Covalent bond", "共价键", "共價鍵", "共有結合", "A bond formed by sharing electron pairs."),
    ("Ionic bond", "离子键", "離子鍵", "イオン結合", "Attraction between oppositely charged ions."),
    (
        "Mole",
        "摩尔",
        "莫耳",
        "モル",
        "Amount of substance containing Avogadro's number of particles.",
    ),
    ("pH", "pH 值", "pH 值", "pH", "A measure of acidity or alkalinity."),
) + SCIENCE_TERMS

BIOLOGY_TERMS: tuple[TermRow, ...] = (
    ("Cell", "细胞", "細胞", "細胞", "The basic unit of living organisms."),
    ("Enzyme", "酶", "酵素", "酵素", "A biological catalyst."),
    ("Diffusion", "扩散", "擴散", "拡散", "Net movement from high to low concentration."),
    (
        "Osmosis",
        "渗透",
        "滲透",
        "浸透",
        "Diffusion of water through a partially permeable membrane.",
    ),
    ("Photosynthesis", "光合作用", "光合作用", "光合成", "Making glucose using light energy."),
    ("Respiration", "呼吸作用", "呼吸作用", "呼吸", "Releasing energy from glucose."),
) + SCIENCE_TERMS

HISTORY_TERMS: tuple[TermRow, ...] = (
    ("Chronology", "年代顺序", "年代順序", "年代順", "The order in which events happened."),
    ("Cause", "原因", "原因", "原因", "A factor that helps explain why something happened."),
    ("Consequence", "后果", "後果", "結果", "What happened because of an event or decision."),
    ("Change", "变化", "變化", "変化", "How something became different over time."),
    ("Continuity", "延续性", "延續性", "継続性", "What stayed the same over time."),
    (
        "Source utility",
        "史料价值",
        "史料價值",
        "史料の有用性",
        "How useful a source is for answering a question.",
    ),
    ("Provenance", "来源背景", "來源背景", "出所", "Who made a source, when, and why."),
    ("Interpretation", "历史解释", "歷史解釋", "解釈", "A view or explanation of the past."),
)


def render_professional_glossary(
    qualification: Qualification,
    selected_language: str,
) -> str:
    support_language = glossary_language(selected_language)
    if not support_language:
        return ""
    terms = professional_glossary_terms(qualification, support_language)
    if not terms:
        return ""
    language_name = support_language_label(support_language)
    rows = "".join(
        '<tr class="glossary-term-row">'
        f"<td>{html_escape(term['translation'])}</td>"
        f"<td>{html_escape(term['english'])}</td>"
        f"<td>{html_escape(term['note'])}</td>"
        "</tr>"
        for term in terms
    )
    return f"""
<section class="band professional-glossary">
  <h2>Professional Term Glossary</h2>
  <p class="language-note">The handbook body stays in English for the exam. This table gives {html_escape(language_name)} support for key terms.</p>
  <table>
    <thead><tr><th>{html_escape(language_name)}</th><th>English exam term</th><th>Exam use</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>
"""


def professional_glossary_terms(
    qualification: Qualification,
    support_language: str,
) -> list[dict[str, str]]:
    # The qualification's declared subject is authoritative. Topic titles can
    # include cross-curricular appendices such as mathematical requirements.
    subject = " ".join(
        [qualification.subject_area or "", qualification.title]
    ).lower()
    source_terms = glossary_bank_for_subject(subject)
    language_index = {"zh-CN": 1, "zh-TW": 2, "ja": 3}.get(support_language, 1)
    return [
        {
            "english": english,
            "translation": values[language_index - 1],
            "note": note,
        }
        for english, *values, note in source_terms[:50]
    ]


def glossary_bank_for_subject(subject: str) -> tuple[TermRow, ...]:
    subject = subject.lower()
    if "math" in subject:
        return MATH_TERMS
    banks: list[TermRow] = []
    if "economic" in subject:
        banks.extend(ECONOMICS_TERMS)
    if "accounting" in subject:
        banks.extend(ACCOUNTING_TERMS)
    if "business" in subject:
        banks.extend(BUSINESS_TERMS)
    if "physics" in subject:
        banks.extend(PHYSICS_TERMS)
    if "chemistry" in subject:
        banks.extend(CHEMISTRY_TERMS)
    if "biology" in subject:
        banks.extend(BIOLOGY_TERMS)
    if "history" in subject:
        banks.extend(HISTORY_TERMS)
    banks.extend(GENERIC_TERMS)
    return tuple(dedupe_terms(banks))


def dedupe_terms(terms: list[TermRow]) -> list[TermRow]:
    seen: set[str] = set()
    result: list[TermRow] = []
    for row in terms:
        key = row[0].lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def support_language_label(language: str) -> str:
    return {
        "zh-CN": "Simplified Chinese",
        "zh-TW": "Traditional Chinese",
        "ja": "Japanese",
    }.get(language, language)
