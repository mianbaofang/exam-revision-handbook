from intl_exam_guide.models import SourceRecord
from intl_exam_guide.providers import get_provider, provider_for_course_market
from intl_exam_guide.providers import aqa as aqa_module
from intl_exam_guide.providers import pearson as pearson_module
from intl_exam_guide.providers.aqa import AQAUKProvider
from intl_exam_guide.providers.base import Link
from intl_exam_guide.providers.common import TextNode
from intl_exam_guide.providers.pearson import PearsonEdexcelUKProvider
from intl_exam_guide.rendering.cover import exam_board_identity, qualification_type_display


class FakeParser:
    def __init__(self, title: str, links: list[Link], nodes: list[TextNode]):
        self.title = title
        self.links = links
        self.nodes = nodes


def test_course_market_routes_each_board_to_the_selected_provider():
    assert provider_for_course_market("aqa", "international") == "oxfordaqa"
    assert provider_for_course_market("aqa", "uk-domestic") == "aqa_uk"
    assert provider_for_course_market("edexcel", "international") == "pearson"
    assert provider_for_course_market("edexcel", "uk-domestic") == "pearson_uk"
    assert provider_for_course_market("caie", "international") == "cambridge"
    assert provider_for_course_market("caie", "uk-domestic") == "cambridge_uk"
    assert get_provider("aqa_uk").name == "aqa_uk"
    assert get_provider("pearson_uk").name == "pearson_uk"
    assert get_provider("cambridge_uk").name == "cambridge_uk"


def test_aqa_uk_provider_selects_a_domestic_gcse_and_records_market(monkeypatch):
    catalogue = FakeParser(
        "AQA Subjects",
        [
            Link(
                text="Mathematics (8300)",
                href="https://www.aqa.org.uk/subjects/mathematics/gcse/mathematics-8300",
            ),
            Link(
                text="Mathematics (7357)",
                href="https://www.aqa.org.uk/subjects/mathematics/a-level/mathematics-7357",
            ),
        ],
        [],
    )
    course = FakeParser(
        "GCSE Mathematics 8300 | Overview | AQA",
        [
            Link(
                text="Download specification",
                href="https://cdn.example.test/aqa-8300-specification.pdf",
            )
        ],
        [TextNode("h1", "GCSE Mathematics 8300")],
    )
    monkeypatch.setattr(
        aqa_module,
        "parse_page",
        lambda url: course if "mathematics-8300" in url else catalogue,
    )

    provider = AQAUKProvider()
    link = provider.find_qualification("Mathematics", "gcse")
    qualification = provider.parse_qualification(link.href, "gcse")

    assert link.qualification_type == "uk_gcse"
    assert qualification.qualification_type == "uk_gcse"
    assert qualification.source.course_market == "uk-domestic"
    assert qualification.qualification_family == "AQA GCSE"
    assert qualification.source.specification_url.endswith("aqa-8300-specification.pdf")


def test_pearson_uk_provider_selects_as_pdf_and_records_market(monkeypatch):
    parser = FakeParser(
        "Pearson Edexcel AS and A level Mathematics (2017) | Pearson qualifications",
        [
            Link(
                text="Download",
                href="https://example.test/a-level-mathematics-specification.pdf",
            ),
            Link(
                text="Download",
                href="https://example.test/as-mathematics-specification.pdf",
            ),
        ],
        [TextNode("h1", "Pearson Edexcel AS and A level Mathematics (2017)")],
    )
    monkeypatch.setattr(pearson_module, "parse_page", lambda _url: parser)

    qualification = PearsonEdexcelUKProvider().parse_qualification(
        "https://qualifications.pearson.com/en/qualifications/edexcel-a-levels/mathematics-2017.html",
        "as",
    )

    assert qualification.qualification_type == "uk_as_a_level"
    assert qualification.source.course_market == "uk-domestic"
    assert qualification.qualification_family == "Pearson Edexcel AS & A Level"
    assert qualification.source.specification_url.endswith("as-mathematics-specification.pdf")


def test_uk_course_labels_do_not_render_as_international():
    qualification = type(
        "QualificationStub",
        (),
        {
            "provider": "aqa_uk",
            "source": SourceRecord(
                provider="aqa_uk",
                page_url="https://www.aqa.org.uk/subjects/mathematics/gcse/mathematics-8300",
                course_market="uk-domestic",
                qualification_family="AQA GCSE",
            ),
            "qualification_family": "AQA GCSE",
            "page_url": "https://www.aqa.org.uk/subjects/mathematics/gcse/mathematics-8300",
            "qualification_type": "uk_gcse",
        },
    )()

    assert exam_board_identity(qualification)["full"] == "AQA Qualifications"
    assert qualification_type_display(qualification) == "AQA GCSE"
