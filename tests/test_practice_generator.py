from intl_exam_guide.models import SourceSnippet, Topic
from intl_exam_guide.planning.practice_generator import (
    build_practice_item,
    choose_command_word,
    choose_difficulty,
    clean_focus_text,
    concrete_example,
    concrete_example_zh,
    contextualize_question,
)


def combined_text(parts: tuple[str, list[str], list[str], list[str]]) -> str:
    question, frame, steps, checkpoints = parts
    return " ".join([question, *frame, *steps, *checkpoints]).lower()


def test_build_practice_item_uses_requested_style_and_source_snippets():
    topic = Topic(
        title="3.1.2 - Sources and recording of data",
        points=["Source documents are purchase invoices and sales invoices."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Source documents include purchase invoices and sales invoices.",
                matched_term="Source documents",
            )
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=0,
        qualification_type="international_gcse",
        explanation_style="detective",
        output_language="en",
        subject_area="Accounting",
    )

    combined = " ".join([item.question, *item.public_solution_steps, *item.answer_checkpoints]).lower()
    assert item.command_word == "state"
    assert item.source_snippets == topic.source_snippets
    assert item.question.startswith("Case file:")
    assert "llm writer must replace this scaffold" in combined
    assert "purchase invoices and sales invoices" in combined
    assert "not selected from a python subject template" in combined


def test_chinese_practice_focus_falls_back_from_untranslated_formula_detail():
    topic = Topic(
        title="P1.1 - Algebra: Solution of linear and quadratic inequalities",
        points=[
            "Solution of linear and quadratic inequalities.",
            "eg 2 2xx + /greaterthanorequalangled6",
        ],
    )

    item = build_practice_item(
        topic,
        topic.points,
        number=1,
        qualification_type="international_as_a_level",
        explanation_style="friendly",
        output_language="zh-CN",
        subject_area="Mathematics",
    )

    assert item.focus_point == "一次与二次不等式求解"
    assert "本节核心主题" not in item.focus_point


def test_concrete_example_is_source_bound_scaffold_for_all_subjects():
    cases = [
        ("Accounting", "Source documents are purchase invoices and sales invoices."),
        ("Chemistry", "Concentration is related to number of moles and volume of solution."),
        ("Mathematics", "Solution of linear and quadratic inequalities."),
        ("Economics", "Demand and supply determine market price."),
        ("Physics", "pressure = force / area"),
    ]

    outputs = [
        combined_text(
            concrete_example(Topic(title=subject, points=[focus]), focus, 0, subject)
        )
        for subject, focus in cases
    ]

    assert len(set(outputs)) == len(outputs)
    for output in outputs:
        assert "llm writer must replace this scaffold" in output
        assert "python subject template" in output
        assert "ledger" not in output
        assert "hydrochloric" not in output
        assert "x = 7" not in output
        assert "demand curve shifts" not in output


def test_chinese_concrete_example_is_source_bound_scaffold():
    question, frame, steps, checkpoints = concrete_example_zh(
        Topic(title="Demand and supply", points=["demand supply market price"]),
        "demand supply market price",
        0,
        "Economics",
    )
    combined = " ".join([question, *frame, *steps, *checkpoints])

    assert "LLM 写作者必须" in combined
    assert "真实学科应用例题" in combined
    assert "Python 学科模板" in combined
    assert "需求曲线" not in combined
    assert "银行调节表" not in combined


def test_generic_scaffold_preserves_source_phrase_without_cross_subject_content():
    focus = "explore solutions, equilibrium and factors in a design brief"
    text = combined_text(
        concrete_example(Topic(title="Art", points=[focus]), focus, 0, "Art and Design")
    )

    assert focus in text
    assert "source-bound example" in text
    assert "subject application" in text
    assert "hydrochloric" not in text
    assert "demand" not in text.replace(focus, "")


def test_contextualize_question_does_not_expose_incomplete_syllabus_fragments():
    question = "Two cafes compete through faster service and a loyalty app."

    assert (
        contextualize_question(question, "Firms do not just compete on price but", "en") == question
    )


def test_clean_focus_text_removes_exam_boilerplate_without_rewriting_subject_terms():
    assert clean_focus_text("Students should be able to calculate: pressure = force / area.") == (
        "pressure = force / area"
    )
    assert clean_focus_text("Source documents are purchase invoices.") == (
        "Source documents are purchase invoices"
    )


def test_command_words_and_difficulty_rotate_by_level_and_language():
    assert [choose_command_word(i, "international_gcse") for i in range(4)] == [
        "state",
        "describe",
        "explain",
        "suggest",
    ]
    assert [choose_command_word(i, "international_as_a_level") for i in range(4)] == [
        "explain",
        "analyse",
        "compare",
        "evaluate",
    ]
    assert [choose_command_word(i, "international_gcse", "zh-CN") for i in range(4)] == [
        "写出",
        "描述",
        "解释",
        "提出",
    ]
    assert [choose_difficulty(i) for i in range(3)] == ["core", "standard", "stretch"]
    assert [choose_difficulty(i, "zh-CN") for i in range(3)] == ["基础", "标准", "挑战"]
