"""Audit College Board AP course pages and their official CED documents.

This is a research utility, not a production provider. It deliberately crawls
sequentially and accepts a syllabus PDF only when the course page explicitly
labels the resource as a Course and Exam Description.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


COURSES_URL = "https://apstudents.collegeboard.org/courses"
COURSE_PATH_RE = re.compile(r"^/courses/ap-[a-z0-9-]+/?$")
UNIT_RE = re.compile(r"^Unit\s+(\d+)\s*:\s*(.+)$", re.IGNORECASE)
CED_LABEL_RE = re.compile(r"\bCourse and Exam Description\b", re.IGNORECASE)
OVERVIEW_PATHS = {"/courses/ap-computer-science-program", "/courses/ap-career-kickstart"}
OFFICIAL_PDF_HOSTS = {"apcentral.collegeboard.org"}


@dataclass(frozen=True)
class CourseLink:
    title: str
    url: str


def normalized_text(value: str) -> str:
    return " ".join(value.split())


def slug_from_url(url: str) -> str:
    return Path(urlparse(url).path).name


def get_with_backoff(
    session: requests.Session,
    url: str,
    *,
    attempts: int = 4,
    timeout: float = 45,
) -> requests.Response:
    last_response: requests.Response | None = None
    for attempt in range(attempts):
        response = session.get(url, timeout=timeout)
        last_response = response
        if response.status_code != 429 and response.status_code < 500:
            return response
        if attempt + 1 < attempts:
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 3 * 2**attempt
            time.sleep(delay)
    assert last_response is not None
    return last_response


def discover_courses(html: str) -> tuple[list[CourseLink], list[CourseLink]]:
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, CourseLink] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"])
        path = urlparse(urljoin(COURSES_URL, href)).path
        if not COURSE_PATH_RE.fullmatch(path):
            continue
        title = normalized_text(anchor.get_text(" ", strip=True))
        url = urljoin(COURSES_URL, path.rstrip("/"))
        found[url] = CourseLink(title=title, url=url)

    courses = sorted(
        (
            link
            for link in found.values()
            if urlparse(link.url).path not in OVERVIEW_PATHS and link.title.startswith("AP ")
        ),
        key=lambda link: link.title,
    )
    overviews = sorted(
        (link for link in found.values() if urlparse(link.url).path in OVERVIEW_PATHS),
        key=lambda link: link.title,
    )
    return courses, overviews


def extract_units(soup: BeautifulSoup) -> list[dict[str, object]]:
    units: dict[int, str] = {}
    for node in soup.find_all(["strong", "h2", "h3", "h4"]):
        text = normalized_text(node.get_text(" ", strip=True))
        match = UNIT_RE.fullmatch(text)
        if match:
            units[int(match.group(1))] = match.group(2)
    return [{"number": number, "title": units[number]} for number in sorted(units)]


def extract_ced_candidates(soup: BeautifulSoup, course_url: str) -> list[dict[str, str]]:
    candidates: dict[str, dict[str, str]] = {}
    for heading in soup.find_all(["h2", "h3", "h4"]):
        title = normalized_text(heading.get_text(" ", strip=True))
        if not CED_LABEL_RE.search(title) or re.search(
            r"\b(?:Clarifications?|Corrections?)\b", title, re.IGNORECASE
        ):
            continue

        container = heading.find_parent("div", class_=re.compile(r"\bcb-card\b")) or heading
        anchor = heading.find_parent("a", href=True)
        if anchor is None:
            for parent in heading.parents:
                links = parent.find_all("a", href=True) if hasattr(parent, "find_all") else []
                pdf_links = [
                    link
                    for link in links
                    if ".pdf" in str(link.get("href", "")).lower()
                ]
                if pdf_links:
                    anchor = pdf_links[0]
                    container = parent
                    break
        if anchor is None:
            continue

        url = urljoin(course_url, str(anchor["href"]))
        if ".pdf" not in urlparse(url).path.lower():
            continue
        context = normalized_text(container.get_text(" ", strip=True))
        candidates[url] = {"title": title, "url": url, "context": context}
    return list(candidates.values())


def audit_pdf(session: requests.Session, url: str) -> dict[str, object]:
    try:
        response = session.get(url, headers={"Range": "bytes=0-63"}, timeout=45)
        prefix = response.content[:8]
        source_host = (urlparse(url).hostname or "").lower()
        final_host = (urlparse(response.url).hostname or "").lower()
        return {
            "status": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "content_length": response.headers.get("Content-Length", ""),
            "is_pdf": prefix.startswith(b"%PDF-"),
            "is_official": source_host in OFFICIAL_PDF_HOSTS
            and final_host in OFFICIAL_PDF_HOSTS,
            "final_url": response.url,
        }
    except requests.RequestException as exc:
        return {"status": None, "is_pdf": False, "error": f"{type(exc).__name__}: {exc}"}


def audit_course(
    session: requests.Session,
    course: CourseLink,
    pages_dir: Path,
) -> dict[str, object]:
    record: dict[str, object] = {"course": course.title, "course_url": course.url}
    try:
        response = get_with_backoff(session, course.url)
    except requests.RequestException as exc:
        record.update(page_status=None, error=f"{type(exc).__name__}: {exc}")
        return record

    record["page_status"] = response.status_code
    if response.status_code != 200:
        record["error"] = f"HTTP {response.status_code}"
        return record

    html = response.text
    pages_dir.joinpath(f"{slug_from_url(course.url)}.html").write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    record["page_title"] = normalized_text(h1.get_text(" ", strip=True)) if h1 else ""
    units = extract_units(soup)
    candidates = extract_ced_candidates(soup, course.url)
    record.update(unit_count=len(units), units=units, pdf_candidate_count=len(candidates))
    record["pdf_candidates"] = candidates

    if len(candidates) != 1:
        record["ced_selection_error"] = f"Expected exactly one explicit CED; found {len(candidates)}"
        return record

    selected = candidates[0]
    record.update(ced_title=selected["title"], ced_url=selected["url"])
    return record


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    fields = [
        "course",
        "course_url",
        "page_status",
        "page_title",
        "unit_count",
        "units",
        "ced_title",
        "ced_url",
        "ced_status",
        "ced_is_pdf",
        "ced_is_official",
        "ced_final_url",
        "error",
        "ced_selection_error",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["units"] = " | ".join(
                f"Unit {unit['number']}: {unit['title']}" for unit in record.get("units", [])
            )
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=1.25)
    parser.add_argument(
        "--reuse-pages",
        action="store_true",
        help="Parse previously saved directory/course HTML instead of fetching pages again.",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    pages_dir = args.out / "course-pages"
    pages_dir.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; AP-CED-audit/1.0; research)",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    directory_path = args.out / "courses-raw.html"
    if args.reuse_pages and directory_path.exists():
        directory_html = directory_path.read_text(encoding="utf-8")
    else:
        directory_response = get_with_backoff(session, COURSES_URL)
        directory_response.raise_for_status()
        directory_html = directory_response.text
        directory_path.write_text(directory_html, encoding="utf-8")
    courses, overviews = discover_courses(directory_html)

    records: list[dict[str, object]] = []
    for index, course in enumerate(courses, start=1):
        print(f"[{index:02d}/{len(courses)}] {course.title}", flush=True)
        page_path = pages_dir / f"{slug_from_url(course.url)}.html"
        if args.reuse_pages and page_path.exists():
            html = page_path.read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")
            h1 = soup.find("h1")
            units = extract_units(soup)
            candidates = extract_ced_candidates(soup, course.url)
            record = {
                "course": course.title,
                "course_url": course.url,
                "page_status": 200,
                "page_title": normalized_text(h1.get_text(" ", strip=True)) if h1 else "",
                "unit_count": len(units),
                "units": units,
                "pdf_candidate_count": len(candidates),
                "pdf_candidates": candidates,
            }
            if len(candidates) == 1:
                selected = candidates[0]
                record.update(ced_title=selected["title"], ced_url=selected["url"])
            else:
                record["ced_selection_error"] = (
                    f"Expected exactly one explicit CED; found {len(candidates)}"
                )
        else:
            record = audit_course(session, course, pages_dir)
        records.append(record)
        if index < len(courses) and not args.reuse_pages:
            time.sleep(args.delay)

    pdf_results: dict[str, dict[str, object]] = {}
    for record in records:
        ced_url = record.get("ced_url")
        if not isinstance(ced_url, str):
            continue
        if ced_url not in pdf_results:
            pdf_results[ced_url] = audit_pdf(session, ced_url)
            time.sleep(0.35)
        result = pdf_results[ced_url]
        record.update(
            ced_status=result.get("status"),
            ced_content_type=result.get("content_type", ""),
            ced_content_length=result.get("content_length", ""),
            ced_is_pdf=result.get("is_pdf", False),
            ced_is_official=result.get("is_official", False),
            ced_final_url=result.get("final_url", ""),
        )
        if result.get("error"):
            record["ced_error"] = result["error"]

    shared_ceds = [
        {"ced_url": url, "courses": names}
        for url, names in sorted(
            (
                (url, [str(r["course"]) for r in records if r.get("ced_url") == url])
                for url in pdf_results
            ),
            key=lambda item: item[0],
        )
        if len(names) > 1
    ]
    missing = [str(record["course"]) for record in records if not record.get("ced_url")]
    invalid_pdfs = [
        str(record["course"])
        for record in records
        if record.get("ced_url") and not record.get("ced_is_pdf")
    ]
    non_official_pdfs = [
        str(record["course"])
        for record in records
        if record.get("ced_url") and not record.get("ced_is_official")
    ]
    payload = {
        "source": COURSES_URL,
        "source_sha256": hashlib.sha256(directory_html.encode("utf-8")).hexdigest(),
        "summary": {
            "directory_declared_subjects": int(
                re.search(r"information for\s+(\d+)\s+AP subjects", directory_html).group(1)
            ),
            "parsed_subjects": len(courses),
            "overview_pages_excluded": [
                {"title": link.title, "url": link.url} for link in overviews
            ],
            "pages_ok": sum(record.get("page_status") == 200 for record in records),
            "courses_with_explicit_ced": sum(bool(record.get("ced_url")) for record in records),
            "unique_ced_urls": len(pdf_results),
            "verified_pdf_urls": sum(bool(result.get("is_pdf")) for result in pdf_results.values()),
            "courses_with_units": sum(bool(record.get("units")) for record in records),
            "courses_without_explicit_ced": missing,
            "invalid_pdf_courses": invalid_pdfs,
            "non_official_pdf_courses": non_official_pdfs,
            "shared_ceds": shared_ceds,
        },
        "courses": records,
    }
    json_path = args.out / "ap-course-audit-v2.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.out / "ap-course-audit-v2.csv", records)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0 if len(courses) == 42 else 2


if __name__ == "__main__":
    raise SystemExit(main())
