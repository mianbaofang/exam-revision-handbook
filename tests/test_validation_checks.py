import json
from html import escape

from pypdf import PdfWriter

import intl_exam_guide.validation.checks as validation_checks
from intl_exam_guide.models import (
    AssessmentPaper,
    GuidePlan,
    GuideRunOptions,
    PracticeItem,
    Qualification,
    SourceRecord,
    SourceSnippet,
    Topic,
    TopicGuide,
    VisualBrief,
)
from intl_exam_guide.rendering.html import render_html
from intl_exam_guide.validation.checks import (
    duplicate_practice_question_topics,
    expected_topic_marker,
    has_pdf_local_footer_text,
    has_source_boilerplate_text,
    has_zh_placeholder_text,
    issues_to_dict,
    is_contents_or_index_snippet,
    is_cross_subject_borrowed_practice,
    is_cross_subject_borrowed_text,
    is_placeholder_practice_question,
    is_svg_safe_visual_brief,
    mixed_language_label_matches,
    normalize_practice_question,
    review_summary,
    validate_custom_image_provider,
    validate_plan,
    validate_guides,
    validate_html_language,
    validate_html_glossary_policy,
    validate_html_output,
    validate_html_topic_map_mastery,
    validate_html_visual_and_diagram_blocks,
    validate_image_assets,
    validate_output_package,
    validate_pdf_output,
    validate_practice_item,
    validate_preflight_and_source,
    validate_qualification_notes,
    validate_topic_coverage,
    validate_visual_briefs,
)
from intl_exam_guide.visuals.manifest import build_asset_metadata


def valid_plan() -> GuidePlan:
    topic = Topic(
        title="3.1 Source documents",
        points=["Students should explain source documents."],
        source_snippets=[
            SourceSnippet(
                page=12,
                text="Students should explain source documents and books of prime entry.",
                matched_term="source documents",
            )
        ],
    )
    return GuidePlan(
        qualification=Qualification(
            title="International GCSE Accounting (9215)",
            code="9215",
            qualification_type="international_gcse",
            subject_area="Accounting",
            page_url="https://example.test/accounting",
            summary=["International GCSE linear qualification."],
            topics=[topic],
            assessments=[AssessmentPaper(title="Paper 1")],
            source=SourceRecord(
                provider="oxfordaqa",
                page_url="https://example.test/accounting",
                specification_url="https://example.test/spec.pdf",
                specification_sha256="abc123",
            ),
            audience_note="International GCSE linear qualification for international students outside the UK.",
        ),
        run_options=GuideRunOptions(
            requested_subject="Accounting",
            image_provider="prompt-queue",
            explanation_style="friendly",
            output_language="en",
        ),
        topic_guides=[
            TopicGuide(
                topic_title=topic.title,
                essence="Source documents provide evidence for accounting entries.",
                analogy="Treat each invoice like a transaction label.",
                mini_worked_example="A sales invoice is first recorded in the sales day book.",
                worked_solution_steps=["Identify", "Classify", "Record", "Check"],
                pitfall="Do not post every invoice directly to final accounts.",
                checklist=["Name the document", "Choose the book", "Post the total"],
                diagram_brief="Show source documents flowing into books of prime entry.",
            )
        ],
        practice_items=[
            PracticeItem(
                topic_title=topic.title,
                command_word="Explain",
                difficulty="medium",
                focus_point="source document routing",
                question="Explain where a sales invoice is recorded first.",
                answer_frame=["Name document", "Name book", "Explain purpose"],
                public_solution_steps=["Read", "Identify", "Record", "Check"],
                answer_checkpoints=["Sales invoice", "Sales day book", "Ledger later"],
                source_points=["Students should explain source documents."],
            )
        ],
        visual_briefs=[
            VisualBrief(
                topic_title=topic.title,
                focus_point="source document flow",
                trigger="scenario flow relationship",
                visual_type="source-document ledger",
                complexity="infographic",
                image_provider="prompt-queue",
                prompt="Create a source document flow infographic.",
                source_points=["Students should explain source documents."],
            )
        ],
        diagram_briefs=[],
        revision_stages=["Read", "Practise"],
    )


def test_accounting_statement_svg_layouts_are_in_safe_scope():
    briefs = [
        VisualBrief(
            topic_title="3.2.5 - Partnership accounts",
            focus_point="partnership accounts",
            trigger="partnership accounts need profit appropriation and partner-current structure",
            visual_type="partnership appropriation and current account layout",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="",
            source_points=[],
        ),
        VisualBrief(
            topic_title="3.2.8 - Clubs and non-profit making organisations",
            focus_point="club accounts",
            trigger="club accounts need a receipts-to-income-expenditure distinction",
            visual_type="club receipts-payments and income-expenditure layout",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="",
            source_points=[],
        ),
    ]

    assert all(is_svg_safe_visual_brief(brief) for brief in briefs)


def test_placeholder_practice_question_catches_chinese_authoring_frames():
    assert is_placeholder_practice_question(
        "围绕“考点要求 1”完成一道原创练习：先找关键信息，再选择方法，最后写出可检查的答案。"
    )


def test_validate_html_output_accepts_escaped_chinese_topic_marker(tmp_path):
    plan = valid_plan()
    plan.run_options.output_language = "zh-CN"
    title = "P1.5 - Sequences and series: Students should be familiar with the notation |r|<1 in this context"
    plan.qualification.topics = [
        Topic(
            title=title,
            points=["Students should be familiar with the notation |r|<1 in this context."],
            source_snippets=[SourceSnippet(page=12, text=title, matched_term="P1.5")],
        )
    ]
    marker = expected_topic_marker(title, 1, "zh-CN")
    html_path = tmp_path / "guide.html"
    html_path.write_text(f"<html><body><h2>{escape(marker)}</h2></body></html>", encoding="utf-8")

    issues = validate_html_output(plan, html_path)

    assert not any(issue.message == f"Topic missing from HTML: {marker}" for issue in issues)


def test_validate_html_output_rejects_internal_visual_status_text(tmp_path):
    plan = valid_plan()
    marker = expected_topic_marker(plan.qualification.topics[0].title, 1, "en")
    html_path = tmp_path / "guide.html"
    html_path.write_text(
        (
            "<html><body>"
            f"<h2>{marker}</h2>"
            "<p>How to Study Study Roadmap One-Sentence Essence Method Worked Example "
            "Solution Check Exam Pitfall Source anchor</p>"
            "<p>Reviewed visual asset</p>"
            "</body></html>"
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_html_output(plan, html_path)]

    assert "HTML output exposes internal visual status text: Reviewed visual asset" in messages


def test_validate_html_output_uses_disambiguated_rendered_topic_titles(tmp_path):
    plan = valid_plan()
    plan.run_options.output_language = "zh-CN"
    plan.visual_briefs = []
    plan.practice_items = []
    plan.qualification.topics = [
        Topic(title="P1.1 - Algebra: Factor Theorem", points=["Factor Theorem."]),
        Topic(
            title="P1.1 - Algebra: Application of the Factor Theorem",
            points=["Application of the Factor Theorem."],
        ),
    ]
    plan.topic_guides = [
        TopicGuide(
            topic_title=plan.qualification.topics[0].title,
            essence="Factor theorem links roots and factors.",
            analogy="A root is a key that unlocks a factor.",
            mini_worked_example="If f(2)=0, x-2 is a factor.",
            worked_solution_steps=["Substitute", "Check zero", "State factor", "Verify"],
            pitfall="Do not confuse factor theorem with long division.",
            checklist=[
                "因式定理说明 f(a)=0 与 x-a 是 f(x) 的因式互相等价。",
                "会用代入检查候选根。",
                "会把零值转化为线性因式。",
            ],
            diagram_brief="Show root to factor link.",
        ),
        TopicGuide(
            topic_title=plan.qualification.topics[1].title,
            essence="Factor theorem applications find factors of cubics.",
            analogy="Test likely roots like trying keys.",
            mini_worked_example="If f(1)=0, divide by x-1.",
            worked_solution_steps=["Test roots", "Find factor", "Divide", "Factor remaining"],
            pitfall="Do not stop after finding one factor.",
            checklist=[
                "因式定理应用是用 f(a)=0 寻找三次多项式的线性因式。",
                "会继续分解剩余因式。",
                "会检查重复根和不可分解二次因式。",
            ],
            diagram_brief="Show application flow.",
        ),
    ]
    html_path = render_html(plan, tmp_path / "guide.html")

    messages = [issue.message for issue in validate_html_output(plan, html_path)]

    assert not any(message.startswith("Topic missing from HTML:") for message in messages)


def test_as_only_validation_rejects_a_level_assessment_and_topics():
    plan = valid_plan()
    plan.qualification.qualification_type = "international_as_a_level"
    plan.qualification.route_tags = ["level-scope:as"]
    plan.qualification.topics = [
        Topic(
            title="P2.1 - Proof: Proof by contradiction",
            points=["Proof by contradiction."],
            source_snippets=[
                SourceSnippet(page=18, text="Proof by contradiction.", matched_term="P2.1")
            ],
        )
    ]
    plan.qualification.assessments = [AssessmentPaper(title="A-level Paper 1 - Unit P2")]

    messages = [issue.message for issue in validate_preflight_and_source(plan)]

    assert any("AS-only" in message and "A-level assessment" in message for message in messages)
    assert any("AS-only" in message and "A-level topic" in message for message in messages)


def test_fragment_topic_titles_are_delivery_errors():
    plan = valid_plan()
    plan.qualification.topics = [
        Topic(
            title="3.1.2 - 1",
            points=["1. construction and presentation of mathematical arguments"],
            source_snippets=[
                SourceSnippet(
                    page=9,
                    text="1. construction and presentation",
                    matched_term="3.1",
                )
            ],
        ),
        Topic(
            title="3.1.1 - Students will be required to demonstrate",
            points=["Students will be required to demonstrate"],
            source_snippets=[
                SourceSnippet(page=9, text="Students will be required", matched_term="3.1")
            ],
        ),
        Topic(
            title="P1.5 - Sequences and series: The binomial expansion of",
            points=["The binomial expansion of", "(1+ x)n for positive integer n."],
            source_snippets=[
                SourceSnippet(page=12, text="The binomial expansion of (1+x)n", matched_term="P1.5")
            ],
        ),
        Topic(
            title="P1.5 - Sequences and series: Arithmetic series,",
            points=[
                "Arithmetic series, including the formula for the sum of the first n natural numbers."
            ],
            source_snippets=[
                SourceSnippet(
                    page=12, text="Arithmetic series, including the formula", matched_term="P1.5"
                )
            ],
        ),
        Topic(
            title="M1.1 - Motion: Difference bet...",
            points=[
                "Difference between displacement and distance, and between velocity and speed."
            ],
            source_snippets=[
                SourceSnippet(
                    page=17,
                    text="Difference between displacement and distance",
                    matched_term="M1.1",
                )
            ],
        ),
    ]
    plan.topic_guides = []
    plan.practice_items = []

    messages = [issue.message for issue in validate_topic_coverage(plan)]

    assert any("fragment" in message for message in messages)


def test_preflight_topic_guide_practice_and_visual_validators_pin_error_messages():
    plan = valid_plan()
    plan.run_options.requested_subject = ""
    plan.run_options.explanation_style = "unsupported"
    plan.run_options.output_language = "bilingual"
    plan.run_options.image_provider = "gpt-image-2"
    plan.qualification.source.specification_url = None
    plan.qualification.source.specification_sha256 = None
    plan.qualification.assessments = []
    plan.topic_guides = []
    plan.practice_items = []
    plan.visual_briefs = []
    plan.qualification.topics[0].points = []
    plan.qualification.topics[0].source_snippets = []

    preflight = [issue.message for issue in validate_preflight_and_source(plan)]
    topics = [issue.message for issue in validate_topic_coverage(plan)]

    assert "Missing preflight subject selection." in preflight
    assert "Missing or unsupported explanation style selection." in preflight
    assert "Missing or unsupported term-support language selection." in preflight
    assert "Missing or unsupported image-provider selection." in preflight
    assert "Missing specification PDF URL." in preflight
    assert "Specification PDF hash was not recorded." in preflight
    assert "No assessment papers were extracted." in preflight
    assert "Topic guide coverage does not match topic count." in preflight
    assert "No topics were selected for visual explanation." in preflight
    assert "Missing authored guide block for topic: 3.1 Source documents" in topics
    assert "Missing practice item for topic: 3.1 Source documents" in topics
    assert "Syllabus topic has no extracted body points: 3.1 Source documents" in topics
    assert "No PDF source snippet matched for topic: 3.1 Source documents" in topics


def test_preflight_catches_downloaded_specification_and_custom_provider_edges(monkeypatch):
    plan = valid_plan()
    plan.run_options.image_provider = "custom"
    plan.run_options.image_model = "SenseNova U1 Fast"
    plan.run_options.image_endpoint_url = "https://example.test/v1/images/generations"
    plan.run_options.image_api_key_env = "IMAGE_KEY_FOR_TEST"
    plan.qualification.source.specification_path = "spec.pdf"
    plan.qualification.source.provider = "cambridge"
    plan.qualification.provider = "cambridge"
    plan.qualification.source.syllabus_year_range = "2027-2029"
    plan.qualification.topics[0].title = "Content unit 1"
    plan.qualification.assessments = []
    monkeypatch.delenv("IMAGE_KEY_FOR_TEST", raising=False)

    messages = [issue.message for issue in validate_preflight_and_source(plan)]

    assert "Custom image provider environment variable is not set: IMAGE_KEY_FOR_TEST" in messages
    assert "Only 1 syllabus topics were extracted from a downloaded specification PDF." in messages
    assert (
        "Downloaded specification fell back to generic Content unit topics; "
        "the syllabus parser needs a more precise provider-specific match."
    ) in messages
    assert (
        "Cambridge syllabus range is present but selected exam year was not recorded." in messages
    )
    assert "No assessment papers were extracted." in messages

    plan.run_options.image_model = None
    plan.run_options.image_endpoint_url = None
    plan.run_options.image_api_key_env = None
    custom_messages = [issue.message for issue in validate_custom_image_provider(plan.run_options)]
    assert "Custom image provider is missing a model name." in custom_messages
    assert "Custom image provider is missing an endpoint URL." in custom_messages
    assert (
        "Custom image provider is missing an API-key environment variable name." in custom_messages
    )


def test_guide_practice_and_visual_validators_pin_branch_specific_messages():
    plan = valid_plan()
    guide = plan.topic_guides[0]
    guide.essence = ""
    guide.worked_solution_steps = ["One", "Two"]
    guide.checklist = ["One"]
    practice = plan.practice_items[0]
    practice.command_word = ""
    practice.public_solution_steps = ["One", "Two"]
    practice.answer_checkpoints = ["One"]
    practice.question = "Answer an original short exam-style question."
    visual = plan.visual_briefs[0]
    visual.focus_point = ""
    visual.prompt = ""

    guide_messages = [issue.message for issue in validate_guides(plan)]
    practice_messages = [issue.message for issue in validate_practice_item(plan, practice)]
    visual_messages = [issue.message for issue in validate_visual_briefs(plan)]

    assert "Incomplete topic guide block: 3.1 Source documents" in guide_messages
    assert "Worked example has fewer than 4 public steps: 3.1 Source documents" in guide_messages
    assert "Checklist is too short: 3.1 Source documents" in guide_messages
    assert "Practice item is missing a command word: 3.1 Source documents" in practice_messages
    assert "Practice item has too few solution steps: 3.1 Source documents" in practice_messages
    assert "Practice item has too few answer checkpoints: 3.1 Source documents" in practice_messages
    assert (
        "Practice item is an authoring frame, not a concrete worked example: 3.1 Source documents"
        in practice_messages
    )
    assert "Visual brief is missing a focus point: 3.1 Source documents" in visual_messages
    assert "Visual brief is missing an image prompt: 3.1 Source documents" in visual_messages


def test_checklist_diversity_rejects_exact_duplicate_mastery_text():
    plan = valid_plan()
    plan.topic_guides.append(
        TopicGuide(
            topic_title="3.2 Ledger entries",
            essence="Ledger entries organize transaction effects.",
            analogy="Treat each account as a labelled box.",
            mini_worked_example="Post the source document into the correct account.",
            worked_solution_steps=["Read", "Identify", "Post", "Check"],
            pitfall="Do not reuse another topic's explanation.",
            checklist=list(plan.topic_guides[0].checklist),
            diagram_brief="Show ledger entry flow.",
        )
    )

    messages = [issue.message for issue in validate_guides(plan)]

    assert any(
        message.startswith(
            "Checklist mastery requirements are duplicated across topics: 2 topics share"
        )
        for message in messages
    )


def test_term_support_body_text_still_uses_english_ai_style_checks():
    plan = valid_plan()
    plan.run_options.output_language = "zh-CN"
    plan.topic_guides[0].essence = "Let's dive into source documents and ledger routing."

    messages = [issue.message for issue in validate_guides(plan)]

    assert "Topic guide contains formulaic AI-style wording: 3.1 Source documents" in messages


def test_topic_guide_rejects_cross_subject_borrowed_templates():
    plan = valid_plan()
    plan.topic_guides[
        0
    ].essence = "This topic is about angles to side ratios and periodic graph values."

    messages = [issue.message for issue in validate_guides(plan)]

    assert (
        "Topic guide appears to borrow a different subject template: 3.1 Source documents"
        in messages
    )
    assert is_cross_subject_borrowed_text(
        "A typical question gives masses and velocities before writing the momentum equation.",
        "Business",
    )
    assert not is_cross_subject_borrowed_text(
        "A typical question gives masses and velocities before writing the momentum equation.",
        "Physics",
    )


def test_topic_map_mastery_cells_must_not_repeat_across_topics():
    html = """
<section class="band">
  <h2>复习路线</h2>
  <table><tbody>
    <tr><td>1</td><td><a href="#topic-1">Topic A</a></td><td>同一句掌握目标</td></tr>
    <tr><td>2</td><td><a href="#topic-2">Topic B</a></td><td>同一句掌握目标</td></tr>
  </tbody></table>
</section>
"""

    messages = [issue.message for issue in validate_html_topic_map_mastery(html, "zh-CN")]

    assert any(
        message.startswith("Topic map mastery summary is duplicated across topics: 2 topics share")
        for message in messages
    )


def test_topic_map_titles_must_not_repeat_across_topics():
    html = """
<section class="band">
  <h2>复习路线</h2>
  <table><tbody>
    <tr><td>1</td><td><a href="#topic-1">重复知识点</a></td><td>第一句掌握目标</td></tr>
    <tr><td>2</td><td><a href="#topic-2">重复知识点</a></td><td>第二句掌握目标</td></tr>
  </tbody></table>
</section>
"""

    messages = [issue.message for issue in validate_html_topic_map_mastery(html, "zh-CN")]

    assert any(
        message.startswith(
            "Topic map knowledge-unit title is duplicated across topics: 2 rows share"
        )
        for message in messages
    )


def test_validate_guides_rejects_python_generated_mastery_text():
    plan = valid_plan()
    plan.topic_guides[0].checklist = [
        "Core content in P1.1.KP04: The discriminant of a quadratic function.",
        "Relationship to understand: connect the discriminant with root conditions.",
        "It is central because later examples first translate the question into the discriminant relationship.",
    ]

    messages = [issue.message for issue in validate_guides(plan)]

    assert any("Python-generated instead of Writer-authored" in message for message in messages)


def test_validate_guides_requires_writer_mastery_for_llm_outline():
    plan = valid_plan()
    plan.qualification.route_tags.append("outline-source:llm-analyst")
    plan.topic_guides[0].mastery_summary = ""

    messages = [issue.message for issue in validate_guides(plan)]

    assert any("missing Writer-authored mastery_summary" in message for message in messages)


def test_html_glossary_policy_is_enforced_for_term_support_mode():
    valid_rows = "".join(
        '<tr class="glossary-term-row"><td>术语</td><td>Term</td><td>Use</td></tr>'
        for _ in range(30)
    )
    valid_html = (
        '<section class="band professional-glossary">'
        "<p>Term support: English with zh-CN glossary</p>"
        "<table><thead><tr><th>Simplified Chinese</th><th>English exam term</th><th>Exam use</th></tr></thead>"
        f"<tbody>{valid_rows}</tbody></table></section>"
    )

    assert validate_html_glossary_policy(valid_html, "zh-CN") == []

    missing_messages = [issue.message for issue in validate_html_glossary_policy("", "zh-CN")]
    assert "Term-support handbook is missing the professional term glossary." in missing_messages

    short_rows = (
        '<section class="professional-glossary">'
        + "".join('<tr class="glossary-term-row"></tr>' for _ in range(12))
        + "</section>"
    )
    short_messages = [issue.message for issue in validate_html_glossary_policy(short_rows, "zh-CN")]
    assert any("30-50 rows" in message for message in short_messages)

    english_messages = [issue.message for issue in validate_html_glossary_policy(valid_html, "en")]
    assert (
        "English-only handbook must not include a professional term glossary." in english_messages
    )


def test_visual_prompt_rejects_board_or_course_packaging():
    plan = valid_plan()
    plan.visual_briefs[
        0
    ].prompt = "Create an OxfordAQA International GCSE visual with a course badge."

    visual_messages = [issue.message for issue in validate_visual_briefs(plan)]

    assert (
        "Visual image prompt includes board or course packaging: 3.1 Source documents"
        in visual_messages
    )


def test_visual_provider_contract_requires_exact_fit_svg_and_rejects_local_rendering():
    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title="Accounting flow",
            focus_point="source document to ledger route",
            trigger="medium process flow",
            visual_type="source-document ledger flow diagram",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="Draw the source document to ledger flow.",
            source_points=["Use source documents and books of prime entry."],
        ),
        VisualBrief(
            topic_title="Function graph",
            focus_point="quadratic graph",
            trigger="exact graph",
            visual_type="function graph and equation-balance visual",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="Draw the graph.",
            source_points=["Sketch quadratic graphs."],
        ),
        VisualBrief(
            topic_title="Probability tree",
            focus_point="independent trials",
            trigger="tree structure exactly represents the probability calculation",
            visual_type="probability tree diagram",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="Draw a probability tree.",
            source_points=["Use independent trial probabilities."],
            svg_fit="exact",
        ),
    ]

    messages = [issue.message for issue in validate_visual_briefs(plan)]

    assert any(
        "svg_fit='exact'" in message and "Accounting flow" in message for message in messages
    )
    assert any("Local deterministic SVG rendering" in message for message in messages)
    assert any(
        "Professional diagram visual must use Kroki renderer" in message for message in messages
    )
    assert any("svg_fit='exact'" in message and "Function graph" in message for message in messages)
    assert not any("Probability tree" in message for message in messages)


def test_qualification_notes_and_output_package_pin_release_quality_edges(tmp_path):
    plan = valid_plan()
    plan.qualification.source.listing_qualification_type = "gcse"
    plan.qualification.audience_note = "A qualification."
    plan.qualification.summary = []

    gcse_messages = [issue.message for issue in validate_qualification_notes(plan)]
    assert "Source listing metadata conflicts with International GCSE type." in gcse_messages
    assert "GCSE audience note does not explicitly mention international students." in gcse_messages
    assert (
        "GCSE audience note does not explain that the course is for use outside the UK."
        in gcse_messages
    )
    assert "GCSE guide does not mention the linear qualification structure." in gcse_messages

    plan.qualification.qualification_type = "international_as_a_level"
    plan.qualification.source.listing_qualification_type = "international_gcse"
    plan.qualification.provider = "pearson"
    plan.qualification.source.provider = "pearson"
    as_messages = [issue.message for issue in validate_qualification_notes(plan)]
    assert "Source listing metadata conflicts with AS-A-level type." in as_messages
    assert "AS-A-level guide does not mention the modular qualification structure." in as_messages

    output_messages = [issue.message for issue in validate_output_package(plan, tmp_path)]
    assert any(message.startswith("Sections directory is missing:") for message in output_messages)
    assert any(message.startswith("Images directory is missing:") for message in output_messages)
    assert "Run options file is missing from output directory." in output_messages
    assert any(
        message.startswith("Handbook package manifest is missing:") for message in output_messages
    )
    assert any("Concept explanation jobs are missing" in message for message in output_messages)
    assert any(
        "topic concept explanations still need LLM/Agent review" in message
        for message in output_messages
    )

    (tmp_path / "sections").mkdir()
    (tmp_path / "images").mkdir()
    (tmp_path / "run-options.json").write_text("{}", encoding="utf-8")
    (tmp_path / "handbook-package.json").write_text("{}", encoding="utf-8")
    output_messages = [issue.message for issue in validate_output_package(plan, tmp_path)]
    assert "Sections directory has only 0 section files." in output_messages
    assert "Visual manifest is missing from images directory." in output_messages


def test_output_package_validates_llm_syllabus_outline_self_consistency(tmp_path):
    plan = valid_plan()
    plan.qualification.route_tags.append("outline-source:llm-analyst")
    (tmp_path / "syllabus-outline.json").write_text(
        json.dumps(
            {
                "schema_version": "v0.5-llm-syllabus-outline",
                "status": "llm-analyst-approved",
                "structure_analysis": {
                    "model": "nested",
                    "rationale": "The PDF groups rows under one source container.",
                    "lowest_source_unit": "content rows",
                },
                "official_structure": [
                    {"id": "S1", "title": "1.1 Ratio and proportion", "role": "source-structure"}
                ],
                "source_coverage": [
                    {"id": "SC001", "content": "Use ratios.", "page": 4},
                    {"id": "SC002", "content": "Solve direct proportion problems.", "page": 4},
                ],
                "topics": [
                    {
                        "title": "1.1 Ratio and proportion",
                        "source_coverage_ids": ["SC001", "SC002"],
                        "exam_points": ["Use ratios and direct proportion."],
                        "source_snippets": [
                            {"page": 4, "text": "Use ratios. Solve direct proportion problems.", "matched_term": "ratio"}
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_output_package(plan, tmp_path)]

    assert any("LLM Analyst syllabus outline invalid" in message for message in messages)
    assert any("reuses a declared structure title" in message for message in messages)


def test_image_assets_error_when_svg_titles_and_shapes_are_repetitive(tmp_path):
    plan = valid_plan()
    plan.visual_briefs = []
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    manifest_entries = []
    for index in range(1, 7):
        filename = f"visual_{index:03d}.svg"
        (images_dir / filename).write_text(
            f"""
            <svg class="visual-svg" viewBox="0 0 100 100">
              <title>Repeated layout</title>
              <rect x="10" y="10" width="80" height="80"/>
              <text>{index}</text>
            </svg>
            """,
            encoding="utf-8",
        )
        manifest_entries.append(
            {
                "id": f"visual_{index:03d}",
                "file": filename,
                "complexity": "svg-basic",
                "asset_status": "svg-draft",
            }
        )
    (images_dir / "visual_manifest.json").write_text(
        json.dumps({"schema_version": 2, "visuals": manifest_entries}),
        encoding="utf-8",
    )

    messages = validate_image_assets(plan, images_dir)

    assert any(
        issue.severity == "error" and "SVG visual titles are too repetitive" in issue.message
        for issue in messages
    )
    assert any(
        issue.severity == "error" and "SVG visual structures are too repetitive" in issue.message
        for issue in messages
    )


def test_image_assets_allow_one_reused_svg_template_in_small_sets(tmp_path):
    plan = valid_plan()
    plan.visual_briefs = []
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    manifest_entries = []
    for index in range(1, 8):
        filename = f"visual_{index:03d}.svg"
        title = "Shared flow" if index <= 2 else f"Unique {index}"
        rect_width = 70 if index <= 2 else 70 + index
        (images_dir / filename).write_text(
            f"""
            <svg class="visual-svg" viewBox="0 0 100 100">
              <title>{title}</title>
              <rect x="10" y="10" width="{rect_width}" height="80"/>
              <text>{index}</text>
            </svg>
            """,
            encoding="utf-8",
        )
        manifest_entries.append(
            {
                "id": f"visual_{index:03d}",
                "file": filename,
                "complexity": "svg-basic",
                "asset_status": "svg-draft",
            }
        )
    (images_dir / "visual_manifest.json").write_text(
        json.dumps({"schema_version": 2, "visuals": manifest_entries}),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert not any("SVG visual titles are too repetitive" in message for message in messages)
    assert not any("SVG visual structures are too repetitive" in message for message in messages)


def test_html_language_output_assets_and_summary_helpers_have_direct_contracts(tmp_path):
    plan = valid_plan()
    html_path = tmp_path / "guide.html"
    html_path.write_text(
        '<html lang="en"><body><h1>3.1 Source documents</h1>'
        "How to Study Study Roadmap One-Sentence Essence Method Worked Example "
        "Solution Check Exam Pitfall Source anchor Concept Map "
        '<figure class="visual-example"></figure>'
        '<div class="topic-diagram"></div>'
        "复习路线 / Study Roadmap"
        "</body></html>",
        encoding="utf-8",
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "complexity": "infographic",
                    "asset_status": "external-generation-required",
                    "file": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    html_issues = [issue.message for issue in validate_html_output(plan, html_path)]
    required_english_body = (
        "How to Study Study Roadmap One-Sentence Essence Method Worked Example "
        "Solution Check Exam Pitfall Source anchor"
    )
    language_issues = [
        issue.message for issue in validate_html_language("zh-CN", required_english_body)
    ]
    term_support_body_issues = [
        issue.message
        for issue in validate_html_language("zh-CN", required_english_body + "<p>中文正文</p>")
    ]
    image_issues = [issue.message for issue in validate_image_assets(plan, images_dir)]
    summary = review_summary(plan, html_path=html_path, output_dir=tmp_path)

    assert any("bilingual mixed-language label" in message for message in html_issues)
    assert any("English output contains Chinese characters" in message for message in html_issues)
    assert not language_issues
    assert (
        "English output contains Chinese characters in the student-facing HTML."
        in term_support_body_issues
    )
    assert any(
        "infographic briefs are queued for external image generation" in message
        for message in image_issues
    )
    assert summary["topics"] == 1
    assert summary["pending_infographic_assets"] == 1
    assert summary["topic_diagrams_in_html"] == 1
    assert summary["pending_concept_explanations"] == 1
    assert mixed_language_label_matches("<p>复习路线 / Study Roadmap</p>")
    assert expected_topic_marker("3.1 Source documents", 1, "zh-CN") == "第 3.1 节"
    assert issues_to_dict(validate_html_language("en", ""))[0] == {
        "severity": "error",
        "message": "HTML missing required section phrase: How to Study",
    }
    assert duplicate_practice_question_topics([plan.practice_items[0], plan.practice_items[0]]) == [
        "3.1 Source documents"
    ]


def test_validation_small_helpers_have_direct_branch_contracts():
    assert is_placeholder_practice_question(
        "How the syllabus idea could be used in an exam question."
    )
    assert normalize_practice_question("Case file:  Explain source documents. ") == (
        "explain source documents."
    )
    assert duplicate_practice_question_topics(object()) == []
    assert not is_contents_or_index_snippet(
        SourceSnippet(
            page=2, text="Students should explain source documents.", matched_term="source"
        )
    )
    assert is_contents_or_index_snippet(
        SourceSnippet(page=12, text="Contents Specification at a glance", matched_term="contents")
    )
    assert is_contents_or_index_snippet(
        SourceSnippet(
            page=2,
            text="Source document index",
            matched_term="contents",
        )
    )
    assert is_cross_subject_borrowed_practice(
        "Find the hypotenuse of a right-angled triangle.",
        "Accounting",
    )
    assert not is_cross_subject_borrowed_practice(
        "Find the hypotenuse of a right-angled triangle.",
        "Mathematics",
    )
    assert has_source_boilerplate_text(
        "Cambridge IGCSE Economics 0455 syllabus for 2027, 2028 and 2029. Subject content"
    )
    assert has_source_boilerplate_text("Faculty feedback: this is not syllabus content.")
    assert not has_source_boilerplate_text("Explain demand and supply in a market.")
    assert has_zh_placeholder_text(["官方大纲要求 本单元第 1 个细分要求"])


def test_html_visual_block_validator_catches_missing_visual_block():
    plan = valid_plan()

    messages = [
        issue.message for issue in validate_html_visual_and_diagram_blocks(plan, "<html></html>")
    ]

    assert "HTML missing required visual explanation block." in messages


def test_validate_html_output_rejects_real_rendered_weak_topic_headings(tmp_path):
    plan = valid_plan()
    plan.run_options.output_language = "zh-CN"
    plan.qualification.topics = [
        Topic(title="P1 Algebra", points=["algebra"], source_snippets=[]),
        Topic(title="P1 Quadratics", points=["quadratics"], source_snippets=[]),
        Topic(title="P1 Functions", points=["functions"], source_snippets=[]),
        Topic(title="PP1 Trigonometry", points=["trigonometry"], source_snippets=[]),
    ]
    html_path = tmp_path / "guide.html"
    required_phrases = [
        "How to Study",
        "Study Roadmap",
        "One-Sentence Essence",
        "Method",
        "Worked Example",
        "Solution",
        "Check",
        "Exam Pitfall",
        "Source anchor",
        "Visual Worked Example",
        "Infographic Pending",
    ]
    topic_sections = "\n".join(
        f'<section class="topic"><h2>T{index}. {title}</h2>'
        f'<figure class="topic-diagram"></figure></section>'
        for index, title in enumerate(["P1", "P1", "P1", "PP1"], start=1)
    )
    html_path.write_text(
        "<html><body>"
        + "".join(f"<p>{phrase}</p>" for phrase in required_phrases)
        + "<p>中文正文不应出现在英文主体里</p>"
        + topic_sections
        + "</body></html>",
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_html_output(plan, html_path)]

    assert (
        "student-facing topic titles are too repetitive: 2 unique titles for 4 topics" in messages
    )
    assert "Topic missing from HTML: P1 Algebra" in messages
    assert "Topic missing from HTML: PP1 Trigonometry" in messages
    assert "English output contains Chinese characters in the student-facing HTML." in messages


def test_expected_topic_marker_localizes_all_keyword_fallback_groups():
    cases = {
        "Measurement data graph": "测量与数据",
        "Force and motion": "力与运动",
        "Material change": "材料与变化",
        "Particle state solid liquid gas": "粒子模型与物质状态",
        "Bond structure": "结构与性质",
        "Acid alkali pH": "酸碱与 pH",
        "Accounting ledger bookkeeping": "会计记录",
        "Financial statement profit position": "财务报表",
        "Ratio liquidity profitability": "比率分析",
        "Demand supply market": "市场供需",
        "Opportunity scarcity choice": "选择与机会成本",
        "Set Venn": "集合与韦恩图",
        "Triangle Pythagoras geometry": "几何图形",
        "Statistics probability": "统计与概率",
    }

    assert {title: expected_topic_marker(title, 1, "zh-CN") for title in cases} == cases


def test_expected_topic_marker_uses_shared_chinese_teachable_title():
    assert (
        expected_topic_marker(
            "PP1.2 - Trigonometry: Their graphs, symmetries and periodicity",
            90,
            "zh-CN",
        )
        == "PP1.2 三角函数：图像、对称性与周期性"
    )


def test_validate_plan_aggregates_html_pdf_and_output_package_checks(tmp_path):
    plan = valid_plan()
    html_path = tmp_path / "missing.html"
    pdf_path = tmp_path / "missing.pdf"

    messages = [issue.message for issue in validate_plan(plan, html_path, pdf_path, tmp_path)]

    assert any(message.startswith("HTML output is missing:") for message in messages)
    assert any(message.startswith("PDF output is missing:") for message in messages)
    assert any(message.startswith("Sections directory is missing:") for message in messages)
    assert any(message.startswith("Images directory is missing:") for message in messages)


def test_custom_image_provider_accepts_complete_environment(monkeypatch):
    plan = valid_plan()
    plan.run_options.image_provider = "custom"
    plan.run_options.image_model = "reviewed-model"
    plan.run_options.image_endpoint_url = "https://example.test/images"
    plan.run_options.image_api_key_env = "IMAGE_PROVIDER_OK"
    monkeypatch.setenv("IMAGE_PROVIDER_OK", "set")

    assert validate_custom_image_provider(plan.run_options) == []
    assert not [
        issue
        for issue in validate_preflight_and_source(plan)
        if issue.message.startswith("Custom image provider")
    ]


def test_chinese_placeholder_checks_cover_guide_practice_and_visual_branches():
    assert has_zh_placeholder_text(["官方大纲要求 本单元第 1 个细分要求"])
    assert has_zh_placeholder_text(["官方大纲要求 知识点 1"])
    assert has_zh_placeholder_text(["官方大纲要求 知识单元 1"])

    messages = [
        issue.message for issue in validate_html_language("en", "<p>官方大纲要求 知识点 1</p>")
    ]

    assert "English output contains Chinese characters in the student-facing HTML." in messages


def test_english_syllabus_shell_checks_cover_visible_branches():
    plan = valid_plan()
    plan.topic_guides[0].checklist[0] = "Core content: Candidates should have an understanding of:"
    plan.practice_items[0].question = "a) Explain the purpose of the:"
    plan.visual_briefs[
        0
    ].focus_point = "Students must study one breadth study in change from the following:"

    messages = [
        *[issue.message for issue in validate_guides(plan)],
        *[issue.message for issue in validate_practice_item(plan, plan.practice_items[0])],
        *[issue.message for issue in validate_visual_briefs(plan)],
    ]

    assert "Topic guide contains syllabus shell text: 3.1 Source documents" in messages
    assert "Practice item contains syllabus shell text: 3.1 Source documents" in messages
    assert "Visual brief contains syllabus shell text: 3.1 Source documents" in messages


def test_html_output_rejects_student_visible_syllabus_shell_text(tmp_path):
    plan = valid_plan()
    html_path = tmp_path / "guide.html"
    html_path.write_text(
        '<html lang="en"><body><section><h2>Study Roadmap</h2></section>'
        "<section><h2>T1. 3.1 Source documents</h2>"
        "<p>Students should be able to understand the nature of an economic resource.</p>"
        "</section></body></html>",
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_html_output(plan, html_path)]

    assert "HTML output contains syllabus shell text in student-facing content." in messages


def test_encoding_artifact_checks_cover_visible_text_and_html(tmp_path):
    plan = valid_plan()
    plan.topic_guides[0].checklist[0] = "????"
    plan.practice_items[0].question = "Explain the corrupted symbol �."
    plan.visual_briefs[0].visual_type = "????????"
    html_path = tmp_path / "guide.html"
    html_path.write_text("<html><body>????</body></html>", encoding="utf-8")

    messages = [
        *[issue.message for issue in validate_guides(plan)],
        *[issue.message for issue in validate_practice_item(plan, plan.practice_items[0])],
        *[issue.message for issue in validate_visual_briefs(plan)],
        *[issue.message for issue in validate_html_output(plan, html_path)],
    ]

    assert "Topic guide contains encoding replacement artifacts: 3.1 Source documents" in messages
    assert "Practice item contains encoding replacement artifacts: 3.1 Source documents" in messages
    assert "Visual brief contains encoding replacement artifacts: 3.1 Source documents" in messages
    assert "HTML output contains encoding replacement artifacts." in messages


def test_validation_rejects_svg_briefs_outside_safe_scope():
    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title="Market process poster",
            focus_point="complex market cycle",
            trigger="dense process poster with many labelled examples",
            visual_type="multi-panel narrative infographic",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="Draw a dense poster.",
            source_points=["Explain market processes."],
        )
    ]

    messages = [issue.message for issue in validate_visual_briefs(plan)]

    assert "SVG visual brief is not in the SVG-safe scope: Market process poster" in messages


def test_pdf_validation_rejects_excessive_blank_output(tmp_path):
    plan = valid_plan()
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    for _ in range(30):
        writer.add_blank_page(width=595, height=842)
    with pdf_path.open("wb") as handle:
        writer.write(handle)

    messages = [issue.message for issue in validate_pdf_output(plan, pdf_path)]
    summary = review_summary(plan, pdf_path=pdf_path)

    assert any("above the recommended maximum" in message for message in messages)
    assert any("almost no extractable text" in message for message in messages)
    assert summary["pdf_pages"] == 30
    assert summary["pdf_blank_text_pages"] == 30


def test_pdf_validation_rejects_any_blank_text_page(tmp_path):
    plan = valid_plan()
    pdf_path = tmp_path / "one-blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with pdf_path.open("wb") as handle:
        writer.write(handle)

    messages = [issue.message for issue in validate_pdf_output(plan, pdf_path)]

    assert "PDF output has 1 pages with almost no extractable text." in messages


def test_pdf_local_footer_text_detection_covers_file_urls_and_local_guide_paths():
    assert has_pdf_local_footer_text("file:///E:/Object/output/guide.html")
    assert has_pdf_local_footer_text(r"file:\C:\Users\Ethan\Desktop\guide.htm")
    assert has_pdf_local_footer_text(
        r"C:\Users\Ethan\Desktop\aqa-as-accounting-revision-guide\guide.htm"
    )
    assert not has_pdf_local_footer_text("Source anchor: page 12")


def test_pdf_validation_rejects_local_file_url_footer(monkeypatch, tmp_path):
    plan = valid_plan()
    pdf_path = tmp_path / "guide.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    def fake_pdf_quality_summary(_plan, _pdf_path):
        return {
            "pdf_pages": 5,
            "pdf_max_recommended_pages": 30,
            "pdf_size_mib": 1.0,
            "pdf_max_recommended_mib": 30.0,
            "pdf_blank_text_pages": 0,
            "pdf_file_uri_footer_pages": 2,
            "pdf_average_text_chars": 500,
        }

    monkeypatch.setattr(validation_checks, "pdf_quality_summary", fake_pdf_quality_summary)

    messages = [issue.message for issue in validate_pdf_output(plan, pdf_path)]

    assert (
        "PDF output contains local file URL header/footer text on 2 page(s). "
        "Re-export with headers and footers disabled."
    ) in messages


def test_image_assets_catch_missing_manifest_file_reference_and_svg_shortfall(tmp_path):
    plan = valid_plan()
    plan.visual_briefs.append(
        VisualBrief(
            topic_title="3.1 Source documents",
            focus_point="source flow",
            trigger="diagram",
            visual_type="source flow",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="draw source flow",
            source_points=["Students should explain source documents."],
        )
    )
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {"complexity": "infographic", "asset_status": "generated", "file": "missing.png"},
            ]
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert "Images directory has 0 renderable assets for 1 SVG-safe visual briefs." in messages
    assert "Visual manifest references a missing image file: missing.png" in messages
    assert "0/1 selected infographic briefs have generated raster assets." in messages


def test_image_assets_accept_reviewed_raster_for_svg_safe_visuals(tmp_path):
    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title="Quadratics",
            focus_point="turning point",
            trigger="diagram",
            visual_type="axis graph",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="draw graph",
            source_points=["Sketch graphs."],
        )
    ]
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_001.png").write_bytes(b"png")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "complexity": "svg-basic",
                    "asset_status": "reviewed-generated",
                    "review_status": "reviewed",
                    "file": "visual_001.png",
                }
            ]
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert not any("SVG-safe visual briefs" in message for message in messages)


def test_image_assets_reject_unreviewed_svg_draft(tmp_path):
    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title="Probability tree",
            focus_point="independent trials",
            trigger="tree structure exactly represents the probability calculation",
            visual_type="probability tree diagram",
            complexity="svg-basic",
            image_provider="kroki",
            prompt="Draw a probability tree.",
            source_points=["Use independent trial probabilities."],
            svg_fit="exact",
        )
    ]
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_001.svg").write_text("<svg><title>Draft</title></svg>", encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "visual_001",
                    "complexity": "svg-basic",
                    "asset_status": "svg-draft",
                    "review_status": "draft",
                    "file": "visual_001.svg",
                }
            ]
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert any(
        "0 renderable assets for 1 SVG-safe visual briefs" in message for message in messages
    )
    assert any("SVG asset must be reviewed/approved" in message for message in messages)

    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title=f"Topic {index}",
            focus_point=f"focus {index}",
            trigger="diagram",
            visual_type="concept diagram",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="draw concept diagram",
            source_points=[f"source {index}"],
        )
        for index in range(12)
    ]
    images_dir = tmp_path / "repeated-images"
    images_dir.mkdir()
    for index in range(12):
        (images_dir / f"visual_{index:03}.svg").write_text(
            f"""
            <svg role="img" aria-labelledby="visual-title-{index}">
              <title id="visual-title-{index}">Repeated concept map</title>
              <rect x="20" y="20" width="100" height="60"/>
              <path d="M20 50h100" marker-end="url(#arrow-{index})"/>
              <text>Topic {index}</text>
            </svg>
            """,
            encoding="utf-8",
        )
    (images_dir / "visual_manifest.json").write_text("[]", encoding="utf-8")

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert any("SVG visual titles are too repetitive" in message for message in messages)
    assert any("SVG visual structures are too repetitive" in message for message in messages)


def test_image_assets_allow_moderate_scientific_template_reuse(tmp_path):
    plan = valid_plan()
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    for index in range(18):
        group = index % 9
        offset = group * 8
        (images_dir / f"visual_{index:03}.svg").write_text(
            f"""
            <svg role="img" aria-labelledby="visual-title-{index}">
              <title id="visual-title-{index}">Scientific template {group}</title>
              <rect x="{20 + offset}" y="20" width="100" height="60"/>
              <path d="M{20 + offset} 50h100" marker-end="url(#arrow-{group})"/>
              <text>Topic {index}</text>
            </svg>
            """,
            encoding="utf-8",
        )
    (images_dir / "visual_manifest.json").write_text("[]", encoding="utf-8")

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert not any("SVG visual titles are too repetitive" in message for message in messages)
    assert not any("SVG visual structures are too repetitive" in message for message in messages)


def test_image_assets_error_for_pairwise_scientific_svg_reuse(tmp_path):
    plan = valid_plan()
    plan.visual_briefs = [
        VisualBrief(
            topic_title="Integral as area",
            focus_point="area between curve and x-axis",
            trigger="exact curve diagram",
            visual_type="integral area under curve graph",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="Draw area under curve.",
            source_points=["Find the area under a curve."],
        ),
        VisualBrief(
            topic_title="Signed area",
            focus_point="area below x-axis is negative",
            trigger="exact curve diagram",
            visual_type="integral area under curve graph",
            complexity="svg-basic",
            image_provider="deterministic-svg",
            prompt="Draw signed area under curve.",
            source_points=["Interpret areas below the x-axis as negative."],
        ),
    ]
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    for index in range(1, 3):
        filename = f"visual_{index:03d}.svg"
        (images_dir / filename).write_text(
            """
            <svg><title>Integral diagram</title>
              <path d="M10 80 C 40 10, 80 10, 110 80"/>
              <text>label</text>
            </svg>
            """,
            encoding="utf-8",
        )
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "file": "visual_001.svg",
                        "complexity": "svg-basic",
                        "asset_status": "svg-draft",
                    },
                    {
                        "id": "visual_002",
                        "file": "visual_002.svg",
                        "complexity": "svg-basic",
                        "asset_status": "svg-draft",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert any(
        "Different scientific SVG visuals reuse the same structure" in message
        for message in messages
    )


def test_image_assets_report_pending_professional_diagram_jobs(tmp_path):
    plan = valid_plan()
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "visuals": [
                    {
                        "id": "visual_001",
                        "topic_title": "Source document flow",
                        "complexity": "svg-basic",
                        "asset_status": "professional-diagram-required",
                        "file": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    messages = [issue.message for issue in validate_image_assets(plan, images_dir)]

    assert any(
        "Professional diagram rendering failed or is pending" in message for message in messages
    )


def test_image_assets_warn_for_exact_duplicate_raster_assets(tmp_path):
    plan = valid_plan()
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    first = images_dir / "visual_001.png"
    second = images_dir / "visual_002.png"
    first.write_bytes(b"same-raster")
    second.write_bytes(b"same-raster")
    manifest = {
        "schema_version": 2,
        "visuals": [
            {
                "id": "visual_001",
                "complexity": "infographic",
                "asset_status": "reviewed-generated",
                "file": first.name,
                "asset": build_asset_metadata(first),
            },
            {
                "id": "visual_002",
                "complexity": "infographic",
                "asset_status": "reviewed-generated",
                "file": second.name,
                "asset": build_asset_metadata(second),
            },
        ],
    }
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    issues = validate_image_assets(plan, images_dir)
    messages = [issue.message for issue in issues]

    assert any("Raster infographic assets are reused exactly" in message for message in messages)
    assert any(
        issue.severity == "error"
        and "Raster infographic assets are reused exactly" in issue.message
        for issue in issues
    )


def test_review_summary_counts_generated_fallback_and_pending_assets(tmp_path):
    plan = valid_plan()
    output_dir = tmp_path
    images_dir = output_dir / "images"
    sections_dir = output_dir / "sections"
    images_dir.mkdir()
    sections_dir.mkdir()
    (sections_dir / "cover.txt").write_text("cover", encoding="utf-8")
    (output_dir / "handbook-package.json").write_text("{}", encoding="utf-8")
    (images_dir / "generated.png").write_bytes(b"png")
    (images_dir / "fallback.svg").write_text("<svg></svg>", encoding="utf-8")
    (images_dir / "visual_manifest.json").write_text(
        json.dumps(
            [
                {"complexity": "infographic", "asset_status": "generated", "file": "generated.png"},
                {
                    "complexity": "infographic",
                    "asset_status": "svg-fallback-needs-review",
                    "file": "fallback.svg",
                },
            ]
        ),
        encoding="utf-8",
    )

    summary = review_summary(plan, output_dir=output_dir)

    assert summary["section_files"] == 1
    assert summary["image_files"] == 2
    assert summary["generated_infographic_assets"] == 1
    assert summary["svg_fallback_assets"] == 1
    assert summary["pending_infographic_assets"] == 1
    assert summary["has_visual_manifest"] is True
    assert summary["has_package_manifest"] is True


def test_review_summary_reports_svg_repetition_metrics(tmp_path):
    plan = valid_plan()
    output_dir = tmp_path
    images_dir = output_dir / "images"
    sections_dir = output_dir / "sections"
    images_dir.mkdir()
    sections_dir.mkdir()
    (sections_dir / "cover.txt").write_text("cover", encoding="utf-8")
    (output_dir / "handbook-package.json").write_text("{}", encoding="utf-8")
    for index, title in enumerate(["A", "A", "B"], start=1):
        (images_dir / f"visual_{index:03}.svg").write_text(
            f"<svg><title>{title}</title><rect x='{index}' y='1'/></svg>",
            encoding="utf-8",
        )
    (images_dir / "visual_manifest.json").write_text("[]", encoding="utf-8")

    summary = review_summary(plan, output_dir=output_dir)

    assert summary["svg_files"] == 3
    assert summary["svg_unique_titles"] == 2
    assert summary["svg_max_title_repeats"] == 2
