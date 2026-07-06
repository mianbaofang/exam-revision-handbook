from intl_exam_guide.rendering.story_modes import chinese_story_lines, english_story_lines


def test_english_story_lines_are_generic_and_source_bound():
    lines = english_story_lines("Source documents", "purchase invoice", 1)
    combined = " ".join(lines).lower()

    assert "source-bound" in combined
    assert "syllabus wording" in combined or "source point" in combined
    assert "audit trail" not in combined
    assert "demand curve" not in combined


def test_chinese_story_lines_are_generic_and_source_bound():
    lines = chinese_story_lines("Demand and supply", "市场价格", 2)
    combined = " ".join(lines)

    assert "真实学科应用" in combined
    assert "来源点" in combined
    assert "需求曲线" not in combined
    assert "银行调节表" not in combined


def test_story_lines_fall_back_to_index_variants_without_cross_subject_terms():
    lines = english_story_lines("Portfolio annotation", "visual balance", 2)
    combined = " ".join(lines).lower()

    assert "realistic subject setting" in combined
    assert "audit trail" not in combined
    assert "curve" not in combined
