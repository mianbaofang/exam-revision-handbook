from __future__ import annotations

import re

from intl_exam_guide.models import Topic


ZH_TOPIC_KEYWORDS = [
    (("measurement", "data", "graph"), "测量与数据"),
    (("force", "motion"), "力与运动"),
    (("material", "change"), "材料与变化"),
    (("particle", "state", "solid", "liquid", "gas"), "粒子模型与物质状态"),
    (("bond", "structure"), "结构与性质"),
    (("acid", "alkali", "ph"), "酸碱与 pH"),
    (("accounting", "ledger", "bookkeeping"), "会计记录"),
    (("financial statement", "profit", "position"), "财务报表"),
    (("ratio", "liquidity", "profitability"), "比率分析"),
    (("demand", "supply", "market"), "市场供需"),
    (("opportunity", "scarcity", "choice"), "选择与机会成本"),
    (("set", "venn"), "集合与韦恩图"),
    (("triangle", "pythagoras", "geometry"), "几何图形"),
    (("statistics", "probability"), "统计与概率"),
]

ZH_MATH_AREA_LABELS = {
    "algebra": "代数",
    "coordinate geometry": "坐标几何",
    "differentiation": "微分",
    "integration": "积分",
    "sequences and series": "数列与级数",
    "circle": "圆",
    "trigonometry": "三角函数",
    "exponential and logarithms": "指数与对数",
    "further probability": "进阶概率",
    "discrete random variables": "离散随机变量",
    "bernoulli and binomial distributions": "伯努利与二项分布",
    "motion in a straight line with constant acceleration": "匀加速度直线运动",
    "motion in a straight line with variable acceleration": "变加速度直线运动",
    "forces and newton's laws": "力与牛顿定律",
    "momentum and impulse": "动量与冲量",
}

ZH_PHRASE_LABELS = [
    (("production possibility",), "生产可能性曲线"),
    (("shifts", "ppc"), "生产可能性曲线移动"),
    (("individual", "market demand"), "个人与市场需求"),
    (("movements", "demand curve"), "需求曲线上的移动"),
    (("shifts", "demand curve"), "需求曲线移动"),
    (("individual", "market supply"), "个人与市场供给"),
    (("movements", "supply curve"), "供给曲线上的移动"),
    (("shifts", "supply curve"), "供给曲线移动"),
    (("price mechanism",), "价格机制"),
    (("market equilibrium",), "市场均衡"),
    (("market disequilibrium",), "市场失衡"),
    (("price changes",), "价格变化"),
    (("calculation", "ped"), "需求价格弹性计算"),
    (("determinants", "ped"), "需求价格弹性影响因素"),
    (("consumer expenditure", "firms", "revenue"), "弹性、支出与收入关系"),
    (("calculation", "pes"), "供给价格弹性计算"),
    (("determinants", "pes"), "供给价格弹性影响因素"),
    (("market economic system",), "市场经济制度"),
    (("government intervention",), "政府干预"),
    (("market failure",), "市场失灵"),
    (("wage determination",), "工资决定"),
    (("differences in wages",), "工资差异"),
    (("demand for factors",), "生产要素需求"),
    (("taxation",), "税收"),
    (("monetary policy",), "货币政策"),
    (("supply-side policy",), "供给侧政策"),
    (("economic growth",), "经济增长"),
    (("recession",), "经济衰退"),
    (("inflation",), "通货膨胀"),
    (("foreign exchange rate",), "外汇汇率"),
    (("floating exchange rate",), "浮动汇率"),
    (("appreciation", "depreciation"), "汇率升值与贬值"),
    (("extensions", "contractions", "demand"), "需求曲线上的移动"),
    (("decreases", "increases", "demand"), "需求曲线移动"),
    (("extensions", "contractions", "supply"), "供给曲线上的移动"),
    (("decreases", "increases", "supply"), "供给曲线移动"),
    (("surds", "simplification", "rationalisation"), "根式的化简与分母有理化"),
    (("laws", "indices", "rational exponents"), "有理指数的指数法则"),
    (("simultaneous", "linear", "quadratic"), "一次与二次联立方程"),
    (("linear", "quadratic", "inequalities"), "一次与二次不等式求解"),
    (("algebraic manipulation", "polynomials"), "多项式代数运算"),
    (("algebraic division",), "多项式除法"),
    (("remainder theorem",), "余式定理"),
    (("factor theorem",), "因式定理"),
    (("transformations", "functions"), "函数图像变换"),
    (("equation", "straight line"), "直线方程"),
    (("parallel", "perpendicular"), "平行线与垂直线的斜率关系"),
    (("derivative", "gradient"), "导数与曲线梯度"),
    (("applications", "differentiation"), "微分在切线、法线与驻点中的应用"),
    (("sequences", "generated"), "递推生成的数列"),
    (("arithmetic series",), "等差数列求和"),
    (("geometric series",), "等比数列求和"),
    (("binomial expansion",), "二项式展开"),
    (("sequences",), "数列"),
    (("use of factorisation",), "用因式分解求解"),
    (("geometrical interpretation", "algebraic solution"), "方程代数解的几何解释"),
    (("intersection points", "graphs"), "图像交点与方程解"),
    (("simple transformations", "graph"), "函数图像的平移、反射与伸缩"),
    (("type of transformation",), "图像变换组合"),
    (("product", "gradients", "perpendicular"), "垂直直线斜率乘积"),
    (("intersection", "straight line", "curve"), "直线与曲线交点"),
    (("algebraic methods",), "代数方法求交点"),
    (("notations", "d d y x"), "导数记号"),
    (("general appreciation", "derivative"), "导数意义理解"),
    (("first principles", "differentiation"), "微分第一原理要求"),
    (("differentiation", "polynomials"), "多项式求导"),
    (("differentiation", "rational number"), "有理指数幂函数求导"),
    (("second order derivatives",), "二阶导数"),
    (("indefinite integration", "reverse"), "不定积分与反导数"),
    (("integration", "polynomials"), "多项式积分"),
    (("integration", "rational number"), "有理指数幂函数积分"),
    (("evaluation", "definite integrals"), "定积分求值"),
    (("definite integral", "area under a curve"), "定积分与曲线下面积"),
    (("area", "region", "curve", "x-axis"), "曲线与 x 轴围成面积"),
    (("regions", "x-axis"), "曲线与 x 轴围成面积"),
    (("trapezium rule",), "梯形法则近似面积"),
    (("sum to infinity", "convergent"), "收敛等比级数无穷和"),
    (("|r|<1",), "等比级数收敛条件 |r|<1"),
    (("equation", "circle", "form"), "圆的标准方程"),
    (("translation", "circles"), "圆的平移"),
    (("coordinate geometry", "circle"), "圆的坐标几何"),
    (("tangent", "normal", "circle"), "圆的切线与法线方程"),
    (("implicit differentiation", "not required"), "隐函数微分不要求"),
    (("sine", "cosine", "rules"), "正弦定理与余弦定理"),
    (("odd", "even", "functions"), "奇函数与偶函数概念"),
    (("tan", "sin", "cos"), "三角恒等式"),
    (("tan", "sin"), "三角恒等式"),
    (("trigonometric equations", "interval"), "给定区间内三角方程求解"),
    (("y = a", "graph"), "指数函数图像"),
    (("logarithms", "laws"), "对数与对数法则"),
    (("assigning probabilities", "relative frequencies"), "用相对频率或等可能结果赋概率"),
    (("addition law", "probability"), "概率加法法则"),
    (("multiplication law", "conditional probability"), "概率乘法法则与条件概率"),
    (("application", "probability laws"), "概率法则应用"),
    (("number", "possible outcomes", "finite"), "有限可能结果"),
    (
        ("mean", "variance", "standard deviation", "discrete random variables"),
        "离散随机变量的均值、方差与标准差",
    ),
    (
        ("sum or difference", "independent discrete random variables"),
        "独立离散随机变量和差的均值与方差",
    ),
    (("conditions", "bernoulli"), "伯努利分布适用条件"),
    (("mean", "variance", "bernoulli"), "伯努利分布的均值与方差"),
    (("binomial distribution",), "二项分布"),
    (("calculation", "probabilities", "formula", "tables"), "用公式和表计算二项分布概率"),
    (("deductions", "bernoulli"), "由伯努利分布推导二项分布均值与方差"),
    (("displacement", "distance", "difference"), "位移与路程、速度与速率区别"),
    (("kinematics graphs",), "运动学图像绘制与解读"),
    (("gradients", "area under graphs"), "用图像斜率和面积解运动问题"),
    (("constant acceleration equations",), "匀加速度公式"),
    (("vertical motion under gravity",), "重力下竖直运动"),
    (("relationship", "displacement", "velocity", "acceleration"), "位移、速度与加速度关系"),
    (("calculus techniques", "solve problems"), "用微积分处理变加速度运动"),
    (("restricted", "calculus", "as unit p1"), "变加速度题目限于 AS P1 微积分范围"),
    (("force of gravity",), "重力"),
    (("tensions", "strings", "rods"), "绳张力、杆内力与推力"),
    (("normal reactions",), "法向反力"),
    (("newton", "three laws"), "牛顿三大运动定律"),
    (("resistive forces",), "阻力"),
    (("momentum", "impulse"), "动量与冲量"),
    (("concept", "momentum"), "动量概念"),
    (("conservation", "momentum", "two particles"), "两质点动量守恒"),
    (("law", "restitution", "not required"), "恢复系数定律不要求"),
    (("impulse",), "冲量"),
    (("direct impact", "fixed surface"), "与固定平面的直接碰撞"),
    (("graphs", "symmetries", "periodicity"), "图像、对称性与周期性"),
    (("distance-time graph",), "距离-时间图像"),
    (("cooling curve",), "冷却曲线"),
    (("graphs", "business functions"), "业务职能图"),
    (("business functions", "organization"), "组织中的业务职能"),
    (("function of the liver",), "肝脏功能"),
    (("quadratic", "functions", "graphs"), "二次函数图像"),
    (("discriminant", "quadratic"), "二次函数判别式"),
    (("factorisation", "quadratic"), "二次多项式因式分解"),
    (("completing", "square"), "配方法"),
    (("solution", "quadratic", "equations"), "二次方程求解"),
    (("measures", "central tendency"), "集中趋势量"),
    (("measures", "spread"), "离散程度量"),
    (("mean", "variance", "standard"), "均值、方差与标准差"),
    (("sine", "cosine", "tangent"), "正弦、余弦与正切"),
    (("degree", "radian"), "角度制与弧度制"),
    (("arc length", "sector"), "弧长与扇形面积"),
    (("surds",), "根式"),
    (("quadratic",), "二次函数"),
    (("quadratics",), "二次函数"),
    (("functions", "graphs"), "函数图像"),
    (("functions", "curves"), "函数图像"),
    (("function", "graph"), "函数图像"),
    (("function", "curve"), "函数图像"),
    (("derivative", "differentiation"), "导数与切线斜率"),
    (("integration", "integral"), "积分"),
    (("random variable",), "随机变量"),
    (("binomial", "bernoulli"), "伯努利与二项分布"),
]

ZH_FALLBACK_WORD_LABELS = {
    "apply": "应用",
    "calculate": "计算",
    "compare": "比较",
    "describe": "描述",
    "explain": "解释",
    "identify": "识别",
    "interpret": "解读",
    "plot": "绘制",
    "sketch": "绘制",
    "source": "来源",
    "statement": "陈述",
    "unmatched": "未匹配",
}

ZH_FALLBACK_STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "by",
    "for",
    "from",
    "in",
    "of",
    "or",
    "the",
    "their",
    "to",
    "with",
}

ZH_POINT_KEYWORDS = [
    (("si units", "standard prefixes"), "SI 单位与词头"),
    (("record measurements", "precision"), "测量记录精度"),
    (("mean values", "anomalous"), "平均值与异常值"),
    (("tables and graphs", "represent data"), "表格与图像表示数据"),
    (("speed", "distance travelled", "per unit time"), "速度概念"),
    (("distance-time",), "距离-时间图像"),
    (("balanced and unbalanced forces",), "平衡力与非平衡力"),
    (("force and motion relationships",), "力与运动关系"),
    (("observable properties",), "可观察性质"),
    (("physical changes", "chemical changes"), "物理变化与化学变化"),
    (("conservation of mass",), "质量守恒"),
    (("source document", "purchase invoice", "sales invoice", "invoice"), "原始凭证与发票"),
    (("prime entry", "purchases journal", "sales journal"), "初始记录账簿"),
    (("ledger", "double entry"), "分类账与复式记账"),
    (("trial balance",), "试算平衡"),
    (("bank reconciliation", "unpresented cheque", "outstanding banking"), "银行对账"),
    (("control account", "suspense account", "correction of errors"), "账户核对与错误更正"),
    (("depreciation", "non-current asset"), "折旧与非流动资产"),
    (("irrecoverable", "receivables", "payables"), "应收应付与坏账处理"),
    (("accrual", "prudence", "going concern", "accounting concepts"), "会计概念应用"),
    (("financial statements", "income statement", "statement of financial position"), "财务报表"),
    (("profitability", "liquidity", "ratio"), "比率分析"),
    (("demand", "supply", "market"), "市场需求与供给"),
    (("production", "land", "labour", "capital", "enterprise"), "生产要素"),
    (("opportunity cost", "choice", "scarcity"), "选择与机会成本"),
    (("set", "venn"), "集合与韦恩图"),
    (("triangle", "geometry", "bearing", "construction"), "几何图形与标注"),
    (("statistics", "probability"), "统计与概率"),
    (("bond", "structure"), "结构与性质"),
    (("chromatography",), "色谱与分离"),
    (("gas test", "gas tests"), "气体检验"),
    (("particle", "states of matter", "diffusion"), "粒子模型"),
    (("acid", "alkali", "pH", "neutralisation"), "酸碱与 pH"),
]


def zh_topic_reference(topic: Topic) -> str:
    match = re.match(r"^\s*([A-Z]\d+[A-Z]?|\d+(?:\.\d+)+)\b", topic.title)
    if match:
        return f"第 {match.group(1)} 节"
    return "本节内容"


def zh_teachable_topic_title(raw_title: str, index: int) -> str:
    match = re.match(r"^\s*([A-Z]{1,3}\d+(?:\.\d+)?)\s+-\s+([^:]+):\s*(.+)$", raw_title)
    if match:
        code, area, concept = match.groups()
        return f"{code} {zh_area_label(area)}：{zh_point_label(concept, index)}"

    module_match = re.match(r"^\s*([A-Z]{1,3}\d+(?:\.\d+)?[A-Z]?)\s+(.+)$", raw_title)
    if module_match:
        code, source_phrase = module_match.groups()
        label = zh_area_label_or_none(source_phrase.strip(" -–—:"))
        if label:
            return f"{code} {label}"

    match = re.match(r"^\s*([A-Z]{1,3}\d+(?:\.\d+)?[A-Z]?|\d+(?:\.\d+)+)\b", raw_title)
    if match:
        return f"第 {match.group(1)} 节"

    return (
        zh_phrase_label(raw_title)
        or zh_topic_keyword_label(raw_title)
        or zh_point_label(raw_title, index)
    )


def zh_area_label(area: str) -> str:
    return zh_area_label_or_none(area) or zh_point_label(area, 0)


def zh_area_label_or_none(area: str) -> str | None:
    normalized = normalize_lookup_text(area)
    return (
        ZH_MATH_AREA_LABELS.get(normalized)
        or zh_mapped_point_label(area)
        or zh_topic_keyword_label(area)
    )


def zh_topic_keyword_label(title: str) -> str | None:
    text = normalize_lookup_text(title)
    tokens = set(re.findall(r"[a-z0-9]+", text))
    for keywords, label in ZH_TOPIC_KEYWORDS:
        if topic_keyword_group_matches(text, tokens, keywords):
            return label
    return None


def topic_keyword_group_matches(text: str, tokens: set[str], keywords: tuple[str, ...]) -> bool:
    if "set" in keywords and "venn" in keywords:
        return "venn" in tokens or "sets" in tokens or "set notation" in text
    return any(topic_keyword_matches(text, tokens, keyword) for keyword in keywords)


def topic_keyword_matches(text: str, tokens: set[str], keyword: str) -> bool:
    key = normalize_lookup_text(keyword)
    if " " in key:
        return key in text
    return key in tokens


def zh_mapped_point_label(
    point: str,
    *,
    allow_english_fallback: bool = False,
    index: int = 0,
) -> str | None:
    text = re.sub(r"\s+", " ", point.strip())
    lowered = text.lower()
    phrase_label = zh_phrase_label(text)
    if phrase_label:
        return phrase_label
    for keywords, label in ZH_POINT_KEYWORDS:
        if keyword_group_matches(lowered, keywords):
            return label
    if re.search(r"[\u4e00-\u9fff]", text):
        return text[:24]
    if allow_english_fallback:
        return zh_english_fallback_label(text, index)
    return None


def zh_phrase_label(point: str) -> str | None:
    lowered = re.sub(r"\s+", " ", point.strip()).lower()
    for keywords, label in ZH_PHRASE_LABELS:
        if all(keyword_matches(lowered, keyword) for keyword in keywords):
            return label
    return None


def normalize_lookup_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower()).replace("’", "'")


def zh_point_label(point: str, index: int = 0) -> str:
    text = re.sub(r"\s+", " ", point.strip())
    if not text:
        return f"考点要求 {index + 1}"
    label = zh_mapped_point_label(text, allow_english_fallback=True, index=index)
    if label:
        return label
    # ponytail: legacy helper retained for tests; production body text stays English.
    return f"本节核心主题 {index + 1}"


def is_generic_zh_label(label: str) -> bool:
    return re.fullmatch(r"(?:考点要求|本节核心主题)\s*\d+", label.strip()) is not None


def zh_english_fallback_label(text: str, index: int) -> str | None:
    if not re.search(r"[A-Za-z]", text):
        return None
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text.lower())
        if token not in ZH_FALLBACK_STOP_WORDS
    ]
    if not tokens:
        return None
    translated = []
    for token in tokens:
        label = ZH_FALLBACK_WORD_LABELS.get(token)
        if label:
            translated.append(label)
        elif token.isdigit():
            translated.append(token)
        else:
            return f"本节核心主题 {index + 1}"
    return "".join(translated)


def keyword_matches(lowered_text: str, keyword: str) -> bool:
    key = keyword.lower()
    if re.fullmatch(r"[a-z0-9]+", key):
        return re.search(rf"\b{re.escape(key)}\b", lowered_text) is not None
    return key in lowered_text


def keyword_group_matches(lowered_text: str, keywords: tuple[str, ...]) -> bool:
    if "set" in keywords and "venn" in keywords:
        tokens = set(re.findall(r"[a-z0-9]+", lowered_text))
        return "venn" in tokens or "sets" in tokens or "set notation" in lowered_text
    return any(keyword_matches(lowered_text, keyword) for keyword in keywords)


def zh_point_labels(points: list[str]) -> list[str]:
    return [zh_point_label(point, index) for index, point in enumerate(points)]


def zh_visual_type(visual_type: str) -> str:
    text = visual_type.lower()
    if (
        "source-document" in text
        or "prime-entry" in text
        or "ledger" in text
        or "accounting process" in text
    ):
        return "会计记录流程图"
    if "verification" in text or "reconciliation" in text or "trial balance" in text:
        return "核对与调节流程图"
    if "financial-statement" in text or "financial statement" in text or "ratio-analysis" in text:
        return "财务报表与比率信息图"
    if "accounting adjustment" in text or "concept-effect" in text:
        return "会计调整影响信息图"
    if "chromatography" in text or "lab" in text:
        return "实验流程信息图"
    if "gas" in text:
        return "气体检验观察信息图"
    if "particle" in text or "states" in text:
        return "粒子模型示意图"
    if "bond" in text or "structure" in text:
        return "结构与性质关系信息图"
    if re.search(r"\bph\b", text) or "acid" in text or "alkali" in text or "neutralisation" in text:
        return "酸碱与流程示意图"
    if "demand" in text or "supply" in text or "market" in text:
        return "市场曲线与情境信息图"
    if "production" in text:
        return "生产要素场景信息图"
    if "set" in text or "venn" in text:
        return "集合与韦恩图信息图"
    if "triangle" in text or "geometry" in text:
        return "几何标注图"
    if "statistics" in text or "probability" in text:
        return "统计与概率图表"
    return "图文结合学习图"


def zh_visual_trigger(trigger: str) -> str:
    text = trigger.lower()
    if "apparatus" in text or "process" in text:
        return "需要同时看清装置、步骤和观察结果，单纯文字不够直观。"
    if "spatial" in text or "structure" in text:
        return "结构关系需要空间示意，单纯文字容易误解。"
    if "curve" in text or "graph" in text:
        return "曲线、坐标或移动方向需要图上标注。"
    if "scenario" in text or "flow" in text:
        return "场景、因果和流程需要用箭头串起来。"
    return "这个知识点用图文结合更容易理解和复习。"
