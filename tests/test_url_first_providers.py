import pytest

from intl_exam_guide.models import Topic
from intl_exam_guide.providers import get_provider
from intl_exam_guide.providers.base import Link
from intl_exam_guide.providers import cambridge as cambridge_module
from intl_exam_guide.providers import pearson as pearson_module
from intl_exam_guide.providers.cambridge import CambridgeInternationalProvider
from intl_exam_guide.providers.cambridge import parse_exam_year
from intl_exam_guide.providers.cambridge import select_syllabus_link
from intl_exam_guide.providers.common import (
    TextNode,
    chunk_informative_lines,
    code_from_text,
    dedupe_links,
    dedupe_topics,
    find_pdf_link,
    first_assessment_from_nodes,
    first_teaching_from_nodes,
    format_candidate_choices,
    infer_qualification_type,
    is_pdf_url,
    is_url,
    normalize_level,
    parse_content_overview_topics,
    parse_assessment_objectives_from_pdf,
    parse_assessments_from_pdf,
    parse_command_words_from_pdf,
    parse_generic_topics_from_pdf,
    parse_humanities_topics,
    parse_pearson_subsection_line,
    parse_pearson_topic_tables,
    parse_page,
    qualification_family,
    safe_url,
    subject_slug_from_query,
    subject_terms_from_query,
    title_from_url,
)
from intl_exam_guide.providers.pearson import (
    PearsonEdexcelProvider,
    pearson_candidate_urls,
    pearson_clean_title,
    pearson_code_from_title_or_url,
    pearson_is_specification_pdf,
    pearson_route_tags,
    pearson_subject_area,
)


def test_pearson_metadata_cleans_site_chrome_and_does_not_use_year_as_code():
    title = "Edexcel International GCSE Accounting | Pearson qualifications"
    url = "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-accounting-2017.html"

    assert pearson_clean_title(title) == "Pearson Edexcel International GCSE Accounting"
    assert pearson_code_from_title_or_url(title, url) is None
    assert pearson_subject_area(pearson_clean_title(title), url) == "Accounting"

    coded_title = "Pearson Edexcel International GCSE Accounting (4AC1)"
    assert pearson_code_from_title_or_url(coded_title, url) == "4AC1"

    def __init__(self, title="", links=None, nodes=None):
        self.title = title
        self.links = links or []
        self.nodes = nodes or []


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_url_first_providers_are_registered():
    assert get_provider("pearson").name == "pearson"
    assert get_provider("edexcel").name == "pearson"
    assert get_provider("cambridge").name == "cambridge"
    assert get_provider("caie").name == "cambridge"


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_common_parser_helpers_normalize_urls_titles_queries_and_candidates():
    assert safe_url("https://example.test/spec folder/数学 syllabus.pdf?q=A level") == (
        "https://example.test/spec%20folder/%E6%95%B0%E5%AD%A6%20syllabus.pdf?q=A%20level"
    )
    assert is_url("https://example.test/spec.pdf")
    assert not is_url("example.test/spec.pdf")
    assert is_pdf_url("https://example.test/download?id=1&file=spec.PDF") is False
    assert is_pdf_url("https://example.test/spec.PDF?download=1")
    assert code_from_text("Cambridge IGCSE Accounting (0452)") == "0452"
    assert code_from_text("Syllabus 9706 for AS Level") == "9706"
    assert title_from_url("https://example.test/igcse-accounting-specification.pdf") == (
        "Igcse Accounting"
    )
    assert normalize_level("International_GCSE") == "international-gcse"
    assert subject_terms_from_query(
        "CAIE International GCSE Accounting 0452 2027 syllabus guide"
    ) == ["accounting"]
    assert subject_slug_from_query("Edexcel International GCSE Mathematics A") == "mathematics"

    candidates = [
        Link(
            text="Accounting - 0452", href="https://example.test/0452", qualification_type="igcse"
        ),
        Link(text="Accounting", href="https://example.test/no-code"),
    ]
    message = format_candidate_choices("CAIE", "Accounting", candidates)

    assert "cannot choose safely" in message
    assert "0452, igcse" in message
    assert "no-code, unknown-level" in message


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_common_parser_html_and_metadata_helpers(monkeypatch):
    html = """
    <title>Sample Qualification</title>
    <h1>Accounting</h1>
    <a href="/spec.pdf">Download specification</a>
    <a href="/empty.pdf"></a>
    """

    from intl_exam_guide.providers import common as common_module

    monkeypatch.setattr(common_module, "fetch_bytes", lambda _url, timeout=45: html.encode())
    parser = parse_page("https://example.test/course/")

    assert parser.title == "Sample Qualification"
    assert parser.nodes[0] == TextNode(tag="title", text="Sample Qualification")
    assert parser.links[0].href == "https://example.test/spec.pdf"
    assert parser.links[0].text == "Download specification"
    assert parser.links[1].text == "empty.pdf"
    assert (
        first_teaching_from_nodes(
            [TextNode("p", "First teaching:"), TextNode("p", "September 2026")]
        )
        == "September 2026"
    )
    assert (
        first_assessment_from_nodes([TextNode("p", "First external assessment: June 2028")])
        == "June 2028"
    )
    assert (
        first_assessment_from_nodes([TextNode("p", "First assessment"), TextNode("p", "")]) is None
    )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_common_link_level_and_family_helpers_cover_fallbacks():
    links = [
        Link(text="A", href="https://example.test/a"),
        Link(text="A duplicate", href="https://example.test/A"),
        Link(text="B", href="https://example.test/b"),
    ]

    assert [link.text for link in dedupe_links(links)] == ["A", "B"]
    assert infer_qualification_type("International Advanced Level Biology") == (
        "international_as_a_level"
    )
    assert infer_qualification_type("AS & A Level Chemistry") == "international_as_a_level"
    assert infer_qualification_type("International GCSE Accounting") == "international_gcse"
    assert infer_qualification_type("Biology", level="igcse") == "international_gcse"
    assert infer_qualification_type("Unknown course") == "unknown"
    assert qualification_family("pearson", "international_gcse") == (
        "Pearson Edexcel International GCSE"
    )
    assert qualification_family("cambridge", "international_as_a_level") == (
        "Cambridge International AS & A Level"
    )
    assert qualification_family("oxfordaqa", "international_gcse") == "oxfordaqa"


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_common_pdf_overview_chunking_and_dedupe_helpers():
    overview = parse_content_overview_topics(
        [
            (
                8,
                """
                Candidates study the following topics
                1.1 The purpose of accounting
                1.2 The accounting equation
                AO1 Knowledge and understanding
                """,
            )
        ]
    )

    assert [topic.title for topic in overview] == [
        "1.1 - The purpose of accounting",
        "1.2 - The accounting equation",
    ]
    assert overview[0].source_snippets[0].page == 8

    chunks = chunk_informative_lines(
        [
            (
                11,
                "\n".join(
                    [
                        "Candidates should understand business documents.",
                        "Prepare purchase invoices from given data.",
                        "Record transactions in books of prime entry.",
                        "Post totals to ledger accounts.",
                        "Balance the account at the period end.",
                        "Explain the purpose of a trial balance.",
                    ]
                ),
            )
        ]
    )

    assert chunks[0].title.startswith("Content unit 1 - Candidates should understand")
    assert len(chunks[0].points) == 5
    assert [topic.title for topic in dedupe_topics([Topic("A"), Topic("A"), Topic("B")])] == [
        "A",
        "B",
    ]


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_generic_pdf_parser_handles_pearson_split_topic_codes():
    pages = [
        (
            17,
            """
            1.1
            Integers
            A understand and use integers
            B understand place value
            1.2
            Fractions
            A understand equivalent fractions
            B use mixed numbers
            1.3
            Decimals
            A use decimal notation
            B understand place value
            1.4
            Powers and roots
            A identify square numbers
            B use index notation
            1.5
            Set language and notation
            A understand set notation
            B use Venn diagrams
            1.6
            Percentages
            A convert between percentages
            B calculate percentage change
            3 Assessment information
            """,
        )
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert [topic.title for topic in topics[:6]] == [
        "1.1 - Integers",
        "1.2 - Fractions",
        "1.3 - Decimals",
        "1.4 - Powers and roots",
        "1.5 - Set language and notation",
        "1.6 - Percentages",
    ]
    assert all(topic.points for topic in topics)


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_generic_pdf_parser_handles_pearson_learning_tables():
    pages = [
        (
            19,
            """
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of
            business
            organisation
            a) Explain the characteristics of public sector organisations.
            b) Explain the connection between stakeholders and a business.
            2 Accounting
            concepts
            a) Understand the significance of consistency and prudence.
            b) Apply accounting concepts to simple scenarios.
            """,
        ),
        (
            21,
            """
            Topic 2: Introduction to bookkeeping
            What students need to learn:
            1 Business
            documentation
            a) Explain the purpose of business documents.
            b) Prepare purchase invoices and sales invoices.
            2 Books of original
            entry
            a) Explain the purpose of books of original entry.
            b) Prepare purchases and sales day books.
            3 Ledger
            accounting
            a) Explain the purpose of the nominal ledger.
            b) Record transactions using double entry principles.
            """,
        ),
        (
            23,
            """
            Topic 3: Introduction to control processes
            What students need to learn:
            1 Trial balance  a) Explain the purpose of a trial balance.
            b) Prepare a trial balance.
            2 Control accounts a) Explain the purpose of control accounts.
            b) Prepare trade receivables control accounts.
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert [topic.title for topic in topics[:7]] == [
        "1.1 - Types of business organisation",
        "1.2 - Accounting concepts",
        "2.1 - Business documentation",
        "2.2 - Books of original entry",
        "2.3 - Ledger accounting",
        "3.1 - Trial balance",
        "3.2 - Control accounts",
    ]
    assert "a) Explain the purpose of books of original entry." in topics[3].points


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_humanities_parser_handles_cambridge_history_question_headings():
    pages = [
        (
            12,
            """
            Core content: Option A
            1 Were the revolutions of 1848 important?
            Focus points
            Why were there revolutions in 1848?
            How far did the revolutions change Europe?
            Specified content
            The causes and consequences of the 1848 revolutions.
            2 How was Italy unified?
            Focus points
            Why was Mazzini important?
            How important was Garibaldi?
            Specified content
            The role of Cavour, Garibaldi and foreign intervention.
            3 Why was there a civil war in the United States?
            Focus points
            How important was slavery as a cause of conflict?
            What were the consequences of the war?
            4 Why did the First World War break out?
            Focus points
            How far was Germany responsible for the war?
            What was the impact of alliances?
            5 How secure was the Treaty of Versailles?
            Focus points
            Why did the peacemakers disagree?
            What were the consequences of the treaty?
            6 Why had international peace collapsed by 1939?
            Focus points
            What was the impact of appeasement?
            Why did the League of Nations fail?
            """,
        )
    ]

    topics = parse_humanities_topics(pages)
    titles = [topic.title for topic in topics]
    joined = " ".join(titles + [point for topic in topics for point in topic.points])

    assert len(topics) >= 6
    assert "1 - Were the revolutions of 1848 important?" in titles
    assert "6 - Why had international peace collapsed by 1939?" in titles
    assert "Content unit" not in joined
    assert "AO1" not in joined


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_humanities_parser_handles_pearson_history_option_codes():
    pages = [
        (
            16,
            """
            Paper 1: Depth Studies
            Students must study one depth study from the following:
            A1 The origins and course of the First World War, 1905-18
            What students need to study
            The Alliance System and international rivalry.
            The Schlieffen Plan and the outbreak of war.
            A2 Russia and the Soviet Union, 1905-24
            What students need to study
            The 1905 Revolution and its consequences.
            The Bolshevik seizure of power.
            A3 Germany: development of dictatorship, 1918-45
            What students need to study
            The Weimar Republic and the rise of the Nazi Party.
            A4 Colonial rule and the nationalist challenge in India, 1919-47
            What students need to study
            Gandhi, Congress and independence campaigns.
            A5 Dictatorship and conflict in the USSR, 1924-53
            What students need to study
            Stalin's control and economic change.
            B8 Diversity, rights and equality in Britain, 1914-2010
            What students need to study
            Changes in migration, rights and social attitudes.
            """,
        )
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]

    assert len(topics) >= 6
    assert "A1 - The origins and course of the First World War, 1905-18" in titles
    assert "B8 - Diversity, rights and equality in Britain, 1914-2010" in titles
    assert not any(title.startswith("Content unit") for title in titles)


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_humanities_parser_filters_study_option_shell_points():
    pages = [
        (
            20,
            """
            Students must study one breadth study in change from the following:
            A5 East Germany, 1958-90.
            Students must study one breadth study in change from the following:
            B4 China: conflict, crisis and change, 1900-89
            B5 Russia and the Soviet Union, 1924-53
            B6 South Africa, 1948-94
            B7 The Middle East: conflict, crisis and change, 1917-2012
            B8 Diversity, rights and equality in Britain, 1914-2010.
            Students will:
            """,
        )
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert [topic.title for topic in topics] == [
        "A5 - East Germany, 1958-90.",
        "B4 - China: conflict, crisis and change, 1900-89",
        "B5 - Russia and the Soviet Union, 1924-53",
        "B6 - South Africa, 1948-94",
        "B7 - The Middle East: conflict, crisis and change, 1917-2012",
        "B8 - Diversity, rights and equality in Britain, 1914-2010.",
    ]
    assert topics[0].points == ["East Germany, 1958-90."]
    assert topics[1].points == ["China: conflict, crisis and change, 1900-89"]


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_learning_tables_ignore_trailing_front_matter():
    pages = [
        (
            17,
            """
            Paper 1: Introduction to Bookkeeping and Accounting
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of business organisation a) Explain the characteristics of public sector organisations.
            b) Explain the connection between stakeholders and a business.
            2 Accounting concepts a) Understand consistency and prudence.
            b) Apply accounting concepts to simple scenarios.
            Topic 2: Introduction to bookkeeping
            What students need to learn:
            1 Business documentation a) Explain the purpose of business documents.
            2 Books of original entry a) Prepare purchases and sales day books.
            3 Ledger accounting a) Record transactions using double entry principles.
            Topic 3: Introduction to control processes
            What students need to learn:
            1 Trial balance a) Explain the purpose of a trial balance.
            2 Control accounts a) Prepare trade receivables control accounts.
            """,
        ),
        (
            42,
            """
            Specification - Issue 1 - October 2016 © Pearson Education Limited 2016
            We have guided Pearson through what we judge to be a rigorous world-class qualification
            development process that has included benchmarking assessments against UK and overseas providers.
            Professor Sing Kong Lee
            Chief Education Advisor, Pearson plc
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]
    joined = " ".join(titles + [point for topic in topics for point in topic.points])

    assert len(topics) >= 6
    assert any("Books of original entry" in title for title in titles)
    assert "Content unit" not in joined
    assert "Specification - Issue" not in joined
    assert "Pearson Education Limited" not in joined


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_subsection_parser_rejects_noise_and_long_lines():
    assert parse_pearson_subsection_line("a) Explain the purpose of accounting.") is None
    assert parse_pearson_subsection_line("12") is None
    assert parse_pearson_subsection_line("1 " + "very long " * 20) is None

    assert parse_pearson_subsection_line(
        "2 Books of original entry a) Explain the purpose of books of original entry."
    ) == (
        "2",
        "Books of original entry",
        "a) Explain the purpose of books of original entry.",
    )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_topic_tables_stop_at_appendix_and_administration():
    pages = [
        (
            20,
            """
            Topic 1: The accounting environment
            What students need to learn:
            1 Types of business organisation a) Explain public sector organisations.
            b) Explain stakeholder connections.
            2 Accounting concepts a) Understand prudence.
            b) Apply consistency.
            Topic 2: Bookkeeping
            What students need to learn:
            1 Business documentation a) Explain invoices.
            b) Prepare credit notes.
            2 Ledger accounting a) Record transactions.
            b) Balance ledger accounts.
            Appendix 1 Formulae
            1 Assessment objectives a) This is not subject content.
            Administration arrangements
            Topic 9: Noise
            What students need to learn:
            1 Do not parse this a) It belongs to admin pages.
            """,
        )
    ]

    topics = parse_pearson_topic_tables(pages)
    titles = [topic.title for topic in topics]
    joined = " ".join(titles + [point for topic in topics for point in topic.points])

    assert "1.1 - Types of business organisation" in titles
    assert "2.2 - Ledger accounting" in titles
    assert "9.1 - Do not parse this" not in titles
    assert "Administration arrangements" not in joined


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_generic_pdf_parser_does_not_treat_assessment_objectives_as_topics():
    pages = [
        (
            12,
            """
            Subject content
            1.1 The purpose of accounting
            Candidates should understand the role of accounting information.
            1.2 The accounting equation
            Candidates should understand assets, liabilities and capital.
            2.1 The double entry system of book-keeping
            Candidates should prepare ledger accounts.
            2.2 Business documents
            Candidates should understand invoices and credit notes.
            3.1 The trial balance
            Candidates should prepare and interpret a trial balance.
            3.2 Corrections of errors
            Candidates should correct errors and understand suspense accounts.
            """,
        ),
        (
            23,
            """
            Assessment objectives
            AO1 Knowledge and understanding
            AO2 Analysis
            AO3 Evaluation
            Paper 1 Paper 2
            AO1 Knowledge and understanding 80 60
            AO2 Analysis 20 25
            AO3 Evaluation 0 15
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]

    assert len(topics) >= 6
    assert any("The accounting equation" in title for title in titles)
    assert not any(title.startswith("AO") for title in titles)


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_content_overview_is_not_mixed_with_detailed_subject_content():
    pages = [
        (
            8,
            """
            Syllabus overview
            Content overview
            1 The fundamentals of accounting
            1.1 The purpose of accounting
            1.2 The accounting equation
            2 Sources and recording of data
            2.1 The double entry system of book-keeping
            2.2 Business documents
            2.3 Books of prime entry
            7 Accounting concepts and modern practice
            7.3 Technology and sustainability
            """,
        ),
        (
            11,
            """
            3 Subject content
            1.1 The purpose of accounting
            Candidates should have an understanding of:
            the difference between book-keeping and accounting
            the role of accounting in providing information
            1.2 The accounting equation
            Candidates should have an understanding of:
            assets, liabilities and owner’s equity
            how to apply the accounting equation
            2.1 The double entry system of book-keeping
            Candidates should have an understanding of:
            the dual effect of transactions
            how to prepare ledger accounts
            2.2 Business documents
            Candidates should have an understanding of:
            invoices, credit notes and statements of account
            how documents are used as sources of information
            2.3 Books of prime entry
            Candidates should have an understanding of:
            how to process accounting data in the books of prime entry
            how to post the ledger entries from the books of prime entry
            3.1 The trial balance
            Candidates should have an understanding of:
            how to prepare and use a trial balance
            how to identify errors not revealed by a trial balance
            4 Details of the assessment
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)
    titles = [topic.title for topic in topics]

    assert titles[:6] == [
        "1.1 - The purpose of accounting",
        "1.2 - The accounting equation",
        "2.1 - The double entry system of book-keeping",
        "2.2 - Business documents",
        "2.3 - Books of prime entry",
        "3.1 - The trial balance",
    ]
    assert "7.3 - Technology and sustainability" not in titles


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_accounting_parser_filters_understanding_shell_points():
    pages = [
        (
            11,
            """
            3 Subject content
            3.2 Corrections of errors
            Candidates should have an understanding of:
            how to correct errors using journal entries
            how to prepare suspense accounts
            4 Details of the assessment
            """,
        ),
    ]

    topics = parse_generic_topics_from_pdf(pages)

    assert topics[0].title == "3.2 - Corrections of errors"
    assert "Candidates should have an understanding of:" not in topics[0].points
    assert topics[0].points == [
        "how to correct errors using journal entries",
        "how to prepare suspense accounts",
    ]


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_subject_page_requires_exam_year_when_ranges_are_ambiguous():
    links = [
        Link(
            text="2023 - 2025 Syllabus (PDF, 693KB)",
            href="https://www.cambridgeinternational.org/Images/123-2023-2025-syllabus.pdf",
        ),
        Link(
            text="2026 - 2028 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
        ),
    ]

    with pytest.raises(ValueError, match="Please provide --exam-year"):
        select_syllabus_link(links, None)

    chosen = select_syllabus_link(links, "2027")
    assert chosen.href.endswith("456-2026-2028-syllabus.pdf")
    assert chosen.syllabus_year_range == "2026-2028"
    assert chosen.selected_exam_year == "2027"


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_subject_page_rejects_unmatched_exam_year():
    links = [
        Link(
            text="2026 - 2028 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
        ),
        Link(
            text="2029 - 2031 Syllabus (PDF, 1MB)",
            href="https://www.cambridgeinternational.org/Images/789-2029-2031-syllabus.pdf",
        ),
    ]

    with pytest.raises(ValueError, match="does not match any syllabus range"):
        select_syllabus_link(links, "2032")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_subject_query_resolves_unique_official_candidate(monkeypatch):
    def fake_parse_page(url):
        if url.endswith("/international-gcse-accounting-2017.html"):
            return FakeParser(title="Edexcel International GCSE Accounting (2017)")
        raise OSError("not found")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    link = PearsonEdexcelProvider().find_qualification("Edexcel Accounting", "igcse")

    assert link.href.endswith("/international-gcse-accounting-2017.html")
    assert link.qualification_type == "international_gcse"


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_subject_query_does_not_swallow_code_errors(monkeypatch):
    def fake_parse_page(_url):
        raise RuntimeError("parser bug")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    with pytest.raises(RuntimeError, match="parser bug"):
        PearsonEdexcelProvider().find_qualification("Edexcel Accounting", "igcse")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_parse_qualification_extracts_spec_pdf_and_metadata(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[
            Link(
                text="Download specification",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-specification.pdf",
            ),
            Link(text="Past paper", href="https://example.test/past-paper.pdf"),
        ],
        nodes=[
            TextNode(tag="h1", text="Pearson Edexcel International GCSE Accounting (2017)"),
            TextNode(tag="p", text="First teaching: September 2017"),
            TextNode(tag="p", text="First external assessment: June 2019"),
        ],
    )

    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    qualification = PearsonEdexcelProvider().parse_qualification(
        "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-accounting-2017.html",
        "igcse",
    )

    assert qualification.provider == "pearson"
    assert qualification.qualification_type == "international_gcse"
    assert qualification.subject_area == "Accounting"
    assert qualification.source.specification_url.endswith("accounting-specification.pdf")
    assert qualification.source.first_teaching == "September 2017"
    assert qualification.source.first_assessment == "June 2019"
    assert "Pearson Edexcel" in qualification.route_tags


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_parse_qualification_rejects_page_without_spec_pdf(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[Link(text="Welcome guide", href="https://example.test/welcome-guide.pdf")],
    )
    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    with pytest.raises(ValueError, match="No Pearson specification PDF link"):
        PearsonEdexcelProvider().parse_qualification(
            "https://example.test/accounting.html", "igcse"
        )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_rejects_non_specification_pdf_links_even_if_downloadable(monkeypatch):
    parser = FakeParser(
        title="Pearson Edexcel International GCSE Accounting (2017)",
        links=[
            Link(
                text="Download welcome guide",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-welcome-guide.pdf",
            ),
            Link(
                text="Download mark scheme",
                href="https://qualifications.pearson.com/content/dam/pdf/accounting-mark-scheme.pdf",
            ),
        ],
    )
    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    with pytest.raises(ValueError, match="No Pearson specification PDF link"):
        PearsonEdexcelProvider().parse_qualification(
            "https://example.test/accounting.html", "igcse"
        )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_helper_functions_cover_subject_area_and_route_tags():
    assert (
        pearson_subject_area(
            "Pearson Edexcel International GCSE Accounting (2017)",
            "https://example.test/international-gcse-accounting-2017.html",
        )
        == "Accounting"
    )
    assert pearson_route_tags(
        "international_as_a_level",
        "https://example.test/biology-2018.html",
    ) == ["Pearson Edexcel", "modular"]
    assert pearson_route_tags(
        "international_gcse",
        "https://example.test/mathematics-2024-modular.html",
    ) == ["Pearson Edexcel", "modular"]
    assert pearson_is_specification_pdf("https://example.test/accounting-specification.pdf")
    assert not pearson_is_specification_pdf("https://example.test/accounting-past-paper.pdf")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_find_pdf_link_scores_include_terms_and_excludes_noise():
    parser = FakeParser(
        links=[
            Link(text="Past paper PDF", href="https://example.test/past-paper.pdf"),
            Link(text="Download specification", href="https://example.test/specification.pdf"),
            Link(text="Welcome guide", href="https://example.test/welcome-guide.pdf"),
        ]
    )

    assert (
        find_pdf_link(
            parser,
            include_terms=("specification", "download"),
            exclude_terms=("past paper", "past-paper", "welcome"),
        )
        == "https://example.test/specification.pdf"
    )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_common_pdf_parser_extracts_assessments_command_words_and_objectives():
    pages = [
        (
            31,
            """
            Details of assessment
            Paper 1: Introduction to Bookkeeping and Accounting
            1 hour 30 minutes
            80 marks
            50%
            Written examination with structured questions.
            Paper 2: Financial Statements
            1 hour 45 minutes
            90 marks
            50%
            Written examination with questions based on accounting statements.
            """,
        ),
        (
            42,
            """
            Command words
            Calculate - Work out from given facts, figures or information.
            Explain - Set out purposes or reasons.
            Analyse - Examine in detail to show meaning.
            3 Appendix
            """,
        ),
        (
            44,
            """
            Assessment objectives
            AO1 Knowledge and understanding of accounting terms
            AO2 Application and analysis of accounting information
            AO3 Evaluation and judgement
            """,
        ),
    ]

    assessments = parse_assessments_from_pdf(pages)
    command_words = parse_command_words_from_pdf(pages)
    objectives = parse_assessment_objectives_from_pdf(pages)

    assert [paper.title for paper in assessments[:2]] == [
        "Paper 1: Introduction to Bookkeeping and Accounting",
        "Paper 2: Financial Statements",
    ]
    assert assessments[0].duration == "1 hour 30 minutes"
    assert assessments[0].marks == "80 marks"
    assert assessments[0].weighting == "50%"
    assert command_words[:3] == ["Calculate", "Explain", "Analyse"]
    assert objectives == [
        "AO1 Knowledge and understanding of accounting terms",
        "AO2 Application and analysis of accounting information",
        "AO3 Evaluation and judgement",
    ]


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_parse_qualification_uses_exam_year_to_choose_syllabus(monkeypatch):
    parser = FakeParser(
        title="Cambridge IGCSE Accounting (0452)",
        links=[
            Link(
                text="2023 - 2025 Syllabus",
                href="https://www.cambridgeinternational.org/Images/123-2023-2025-syllabus.pdf",
            ),
            Link(
                text="2026 - 2028 Syllabus",
                href="https://www.cambridgeinternational.org/Images/456-2026-2028-syllabus.pdf",
            ),
            Link(
                text="2026 - 2028 Syllabus update",
                href="https://www.cambridgeinternational.org/Images/999-2026-2028-syllabus-update.pdf",
            ),
        ],
    )
    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: parser)

    qualification = CambridgeInternationalProvider().parse_qualification(
        "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        "igcse",
        exam_year="2027",
    )

    assert qualification.provider == "cambridge"
    assert qualification.code == "0452"
    assert qualification.source.syllabus_year_range == "2026-2028"
    assert qualification.source.selected_exam_year == "2027"
    assert qualification.source.specification_url.endswith("456-2026-2028-syllabus.pdf")
    assert qualification.selected_exam_year == "2027"


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_parse_direct_pdf_validates_exam_year():
    qualification = CambridgeInternationalProvider().parse_qualification(
        "https://www.cambridgeinternational.org/Images/123-2026-2028-syllabus.pdf",
        "igcse",
        exam_year="2027",
    )

    assert qualification.source.syllabus_year_range == "2026-2028"
    assert qualification.source.selected_exam_year == "2027"
    assert qualification.source.specification_url.endswith("123-2026-2028-syllabus.pdf")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_parse_direct_pdf_rejects_exam_year_outside_range():
    with pytest.raises(ValueError, match="does not match syllabus PDF range"):
        CambridgeInternationalProvider().parse_qualification(
            "https://www.cambridgeinternational.org/Images/123-2026-2028-syllabus.pdf",
            "igcse",
            exam_year="2029",
        )


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_parse_exam_year_requires_four_digit_year():
    with pytest.raises(ValueError, match="Invalid Cambridge exam year"):
        parse_exam_year("27")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_igcse_subject_slug_preserves_mathematics_a_suffix():
    urls = pearson_candidate_urls("Edexcel Mathematics A", "igcse")

    assert any(url.endswith("/international-gcse-mathematics-a-2016.html") for url in urls)


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_pearson_subject_query_lists_multiple_candidates(monkeypatch):
    def fake_parse_page(url):
        if "biology" in url:
            return FakeParser(title=f"Edexcel {url.rsplit('/', 1)[-1]}")
        raise OSError("not found")

    monkeypatch.setattr(pearson_module, "parse_page", fake_parse_page)

    with pytest.raises(ValueError) as exc:
        PearsonEdexcelProvider().find_qualification("Biology", None)

    message = str(exc.value)
    assert "multiple official candidates" in message
    assert "international-gcse-biology-2017.html" in message
    assert "biology-2018.html" in message


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_subject_query_lists_ambiguous_level_and_codes(monkeypatch):
    links = [
        Link(
            text="Accounting - 0452",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        ),
        Link(
            text="Accounting (9-1) - 0985",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-9-1-0985/",
        ),
        Link(
            text="Accounting - 9706",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-accounting-9706/",
        ),
    ]

    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: FakeParser(links=links))

    with pytest.raises(ValueError) as exc:
        CambridgeInternationalProvider().find_qualification("CAIE Accounting", None)

    message = str(exc.value)
    assert "0452" in message
    assert "0985" in message
    assert "9706" in message


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_subject_query_does_not_swallow_code_errors(monkeypatch):
    def fake_parse_page(_url):
        raise RuntimeError("parser bug")

    monkeypatch.setattr(cambridge_module, "parse_page", fake_parse_page)

    with pytest.raises(RuntimeError, match="parser bug"):
        CambridgeInternationalProvider().find_qualification("CAIE Accounting", "igcse")


@pytest.mark.skip(
    reason="Deprecated: Python no longer parses topics. LLM Analyst decides topics from evidence."
)
def test_cambridge_subject_query_uses_code_to_resolve_unique_candidate(monkeypatch):
    links = [
        Link(
            text="Accounting - 0452",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-0452/",
        ),
        Link(
            text="Accounting (9-1) - 0985",
            href="https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-accounting-9-1-0985/",
        ),
    ]

    monkeypatch.setattr(cambridge_module, "parse_page", lambda _url: FakeParser(links=links))

    link = CambridgeInternationalProvider().find_qualification("Accounting 0452", "igcse")

    assert link.href.endswith("cambridge-igcse-accounting-0452/")
    assert link.qualification_type == "international_gcse"
