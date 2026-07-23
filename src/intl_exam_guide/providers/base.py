from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from intl_exam_guide.models import Qualification


@dataclass
class Link:
    """A discovered exam-board link: subject page, qualification page, or PDF.

    Re-exported from providers.oxfordaqa for backward compatibility.
    """

    text: str
    href: str
    qualification_type: str | None = None
    subject_heading: str | None = None
    group_label: str | None = None
    style_class: str | None = None
    specification_url: str | None = None
    syllabus_year_range: str | None = None
    selected_exam_year: str | None = None


class ExamBoardProvider(ABC):
    """Contract for an exam-board provider.

    OxfordAQA implements full catalogue discovery. Other providers can resolve
    subject-name candidates or accept official URLs/PDFs through
    find_qualification, parse_qualification, and download_specification;
    discovery methods default to a clear error.
    """

    name: str = ""
    supported_levels: tuple[str, ...] = ()

    @abstractmethod
    def find_qualification(
        self, query: str, level: str | None = None, exam_year: str | None = None
    ) -> Link:
        """Resolve a subject query, subject-page URL, or direct PDF URL to a Link."""

    @abstractmethod
    def parse_qualification(
        self, page_url: str, level: str | None = None, exam_year: str | None = None
    ) -> Qualification:
        """Parse a qualification/subject page into a Qualification object."""

    @abstractmethod
    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        """Download the spec/syllabus PDF, attach detailed topics and source snippets."""

    def discover_subject_pages(self) -> list[Link]:
        raise NotImplementedError(
            f"{self.name or type(self).__name__} does not implement subject discovery."
        )

    def list_qualifications(self, subject_url: str) -> list[Link]:
        raise NotImplementedError(
            f"{self.name or type(self).__name__} does not implement qualification listing."
        )

    def apply_listing_metadata(self, qualification: Qualification, link: Link) -> Qualification:
        return qualification


# Providers fully implemented in this release. Append a name once get_provider
# returns a working instance for it.
PROVIDER_NAMES: tuple[str, ...] = (
    "oxfordaqa",
    "aqa_uk",
    "pearson",
    "pearson_uk",
    "cambridge",
    "cambridge_uk",
    "collegeboard",
)

# Domain fingerprints used to infer a provider from a user-supplied URL.
PROVIDER_DOMAINS: dict[str, tuple[str, ...]] = {
    "oxfordaqa": ("oxfordaqa.com",),
    "aqa_uk": ("aqa.org.uk",),
    "pearson": ("qualifications.pearson.com", "edexcel"),
    "cambridge": ("cambridgeinternational.org",),
    "collegeboard": ("apstudents.collegeboard.org", "apcentral.collegeboard.org"),
}


def provider_for_course_market(name: str, course_market: str | None) -> str:
    """Resolve an exam-board family to its explicit market-specific Provider."""

    normalized = name.lower().strip()
    if course_market is None:
        return normalized
    if course_market not in {"international", "uk-domestic", "not-applicable"}:
        raise ValueError(f"Unsupported course market: {course_market!r}.")
    if course_market == "not-applicable":
        if normalized in {"collegeboard", "college-board", "ap", "advanced-placement"}:
            return "collegeboard"
        raise ValueError("course_market=not-applicable is only valid for College Board AP.")

    routes = {
        "international": {
            "aqa": "oxfordaqa",
            "oxfordaqa": "oxfordaqa",
            "aqa_uk": "oxfordaqa",
            "edexcel": "pearson",
            "pearson": "pearson",
            "pearson_uk": "pearson",
            "caie": "cambridge",
            "cambridge": "cambridge",
            "cambridge_uk": "cambridge",
        },
        "uk-domestic": {
            "aqa": "aqa_uk",
            "oxfordaqa": "aqa_uk",
            "aqa_uk": "aqa_uk",
            "edexcel": "pearson_uk",
            "pearson": "pearson_uk",
            "pearson_uk": "pearson_uk",
            "caie": "cambridge_uk",
            "cambridge": "cambridge_uk",
            "cambridge_uk": "cambridge_uk",
        },
    }
    try:
        return routes[course_market][normalized]
    except KeyError as exc:
        raise ValueError(
            f"Provider {name!r} does not support course_market={course_market!r}."
        ) from exc


def infer_provider_from_url(url: str) -> str | None:
    """Return the provider name whose domain fingerprint matches the URL."""
    lower = url.lower()
    for name, domains in PROVIDER_DOMAINS.items():
        if any(domain in lower for domain in domains):
            return name
    return None


def get_provider(name: str) -> ExamBoardProvider:
    """Return a provider instance by name.

    Unknown providers raise a clear ValueError instead of silently using
    OxfordAQA.
    """
    normalized = name.lower().strip()
    if normalized in {"oxfordaqa", "oxford-aqa", "oxford_international_aqa"}:
        from intl_exam_guide.providers.oxfordaqa import OxfordAQAProvider

        return OxfordAQAProvider()
    if normalized in {"aqa_uk", "aqa-uk", "uk-aqa"}:
        from intl_exam_guide.providers.aqa import AQAUKProvider

        return AQAUKProvider()
    if normalized in {"pearson", "edexcel", "pearson-edexcel"}:
        from intl_exam_guide.providers.pearson import PearsonEdexcelProvider

        return PearsonEdexcelProvider()
    if normalized in {"pearson_uk", "pearson-uk", "edexcel-uk", "uk-edexcel"}:
        from intl_exam_guide.providers.pearson import PearsonEdexcelUKProvider

        return PearsonEdexcelUKProvider()
    if normalized in {"cambridge", "caie", "cie"}:
        from intl_exam_guide.providers.cambridge import CambridgeInternationalProvider

        return CambridgeInternationalProvider()
    if normalized in {"cambridge_uk", "cambridge-uk", "caie-uk", "uk-caie"}:
        from intl_exam_guide.providers.cambridge import CambridgeUKProvider

        return CambridgeUKProvider()
    if normalized in {"collegeboard", "college-board", "ap", "advanced-placement"}:
        from intl_exam_guide.providers.collegeboard import CollegeBoardAPProvider

        return CollegeBoardAPProvider()
    raise ValueError(
        f"Unknown provider: {name!r}. Implemented providers: {', '.join(PROVIDER_NAMES)}."
    )
