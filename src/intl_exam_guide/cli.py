from __future__ import annotations

import argparse
import json
import os
import sys
from importlib import resources
from pathlib import Path

from intl_exam_guide.core import course_contract_payload
from intl_exam_guide.auditing.quality_inspector import write_quality_inspection
from intl_exam_guide.models import Qualification
from intl_exam_guide.planning.guide_plan import (
    IMAGE_PROVIDERS,
    LANGUAGE_CHOICES,
    STYLE_LABELS,
    build_guide_plan,
)
from intl_exam_guide.planning.syllabus_outline import (
    write_syllabus_evidence,
    write_syllabus_outline,
)
from intl_exam_guide.providers import PROVIDER_NAMES, get_provider, infer_provider_from_url
from intl_exam_guide.rendering.handbook_package import write_handbook_package
from intl_exam_guide.rendering.html import render_html
from intl_exam_guide.rendering.output_names import default_handbook_paths
from intl_exam_guide.rendering.pdf import PdfExportError, export_pdf
from intl_exam_guide.validation.checks import (
    delivery_status_from_issues,
    issues_to_dict,
    review_summary,
    validate_plan,
)


def print_json_payload(payload: object) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    try:
        print(text)
    except UnicodeEncodeError:
        print(json.dumps(payload, ensure_ascii=True, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="intl-exam-guide")
    subcommands = parser.add_subparsers(dest="command", required=True)

    discover = subcommands.add_parser(
        "discover", help="List exam-board subject pages or qualifications."
    )
    discover.add_argument(
        "--provider",
        default="oxfordaqa",
        help=f"Exam board provider ({', '.join(PROVIDER_NAMES)}).",
    )
    discover.add_argument("--subject-url", help="Optional provider subject page URL.")

    generate = subcommands.add_parser(
        "generate",
        help="Prepare official evidence for the host LLM handbook workflow.",
    )
    generate.add_argument(
        "--query", required=True, help="Subject name, code, slug, or qualification URL."
    )
    generate.add_argument(
        "--provider",
        default=None,
        help=f"Exam board provider ({', '.join(PROVIDER_NAMES)}). Inferred from --query URL when omitted.",
    )
    generate.add_argument(
        "--level",
        choices=["gcse", "igcse", "as", "as-level", "a-level", "alevel", "as-a-level"],
        help="Qualification level.",
    )
    generate.add_argument(
        "--exam-year",
        help="Exam year used by year-ranged syllabuses, especially Cambridge subject pages.",
    )
    generate.add_argument("--out", required=True, help="Output directory.")

    extract_evidence = subcommands.add_parser(
        "extract-evidence",
        help="Download the official specification and write syllabus evidence only.",
    )
    extract_evidence.add_argument(
        "--query", required=True, help="Subject name, code, slug, qualification URL, or direct PDF URL."
    )
    extract_evidence.add_argument(
        "--provider",
        default=None,
        help=f"Exam board provider ({', '.join(PROVIDER_NAMES)}). Inferred from --query URL when omitted.",
    )
    extract_evidence.add_argument(
        "--level",
        choices=["gcse", "igcse", "as", "as-level", "a-level", "alevel", "as-a-level"],
        help="Qualification level.",
    )
    extract_evidence.add_argument(
        "--exam-year",
        help="Exam year used by year-ranged syllabuses, especially Cambridge subject pages.",
    )
    extract_evidence.add_argument("--out", required=True, help="Output directory.")

    demo = subcommands.add_parser("demo", help="Generate an offline synthetic demo guide.")
    demo.add_argument("--out", required=True, help="Output directory.")
    demo.add_argument("--questions-per-topic", type=int, default=1)
    add_generation_choice_args(demo)
    demo.add_argument("--skip-pdf", action="store_true")

    review = subcommands.add_parser(
        "review",
        help="Build a final Agent/LLM review packet for an output directory.",
    )
    review.add_argument("--out", required=True, help="Existing handbook output directory.")

    inspect = subcommands.add_parser(
        "inspect",
        help="Run fast package checks for an output directory.",
    )
    inspect.add_argument("--out", required=True, help="Existing handbook output directory.")

    args = parser.parse_args(argv)

    if args.command == "discover":
        provider = get_provider(args.provider)
        if args.subject_url:
            for item in provider.list_qualifications(args.subject_url):
                print(
                    "\t".join(
                        [
                            item.text,
                            item.qualification_type or "unknown",
                            item.subject_heading or "",
                            item.group_label or "",
                            item.href,
                        ]
                    )
                )
        else:
            for item in provider.discover_subject_pages():
                print(f"{item.text}\t{item.href}")
        return 0

    if args.command == "review":
        from intl_exam_guide.auditing.final_review import write_final_review_packet

        path = write_final_review_packet(Path(args.out))
        print_json_payload({"final_review_packet": str(path)})
        return 0

    if args.command == "inspect":
        path = write_quality_inspection(Path(args.out))
        print_json_payload({"quality_inspection": str(path)})
        return 0

    if args.command == "generate":
        try:
            qualification = resolve_and_download_qualification(
                args.query,
                args.provider,
                args.level,
                args.exam_year,
                Path(args.out) / "source",
            )
        except (ValueError, NotImplementedError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = write_evidence_package(qualification, out_dir)
        print_json_payload(
            {
                "qualification": qualification.title,
                "mode": "evidence-only",
                "syllabus_evidence": str(evidence_path),
                "qualification_json": str(out_dir / "qualification.json"),
                "message": (
                    "Evidence ready. The host LLM must write syllabus-outline.json, "
                    "concepts/concept_explanations.json, mastery_summary values, and visual decisions "
                    "before rendering HTML/PDF."
                ),
            }
        )
        return 0

    if args.command == "extract-evidence":
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            qualification = resolve_and_download_qualification(
                args.query,
                args.provider,
                args.level,
                args.exam_year,
                out_dir / "source",
            )
        except (ValueError, NotImplementedError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        evidence_path = write_evidence_package(qualification, out_dir)
        print_json_payload(
            {
                "qualification": qualification.title,
                "mode": "evidence-only",
                "syllabus_evidence": str(evidence_path),
                "qualification_json": str(out_dir / "qualification.json"),
                "message": "Evidence ready. Run the Skill host LLM workflow to write syllabus-outline.json, concepts/concept_explanations.json, and render the named HTML/PDF outputs.",
            }
        )
        return 0

    if args.command == "demo":
        validate_generation_choices(parser, args)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        qualification = load_demo_qualification()
        return write_guide_outputs(
            qualification,
            out_dir,
            args.questions_per_topic,
            args.skip_pdf,
            args.image_provider,
            args.explanation_style,
            args.language,
            "demo science",
            None,
            args.image_model,
            args.image_endpoint_url,
            args.image_api_key_env,
            provider=qualification.provider or qualification.source.provider or "synthetic-demo",
            level="igcse",
        )

    return 2


def add_generation_choice_args(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--image-provider",
        default="prompt-queue",
        choices=sorted(IMAGE_PROVIDERS),
        help=(
            "Optional visual route. Defaults to prompt-queue, which writes source-bound "
            "visual briefs for complex infographics. Real image generation/import requires "
            "a callable external skill, API, script, asset directory, or custom provider."
        ),
    )
    command.add_argument(
        "--explanation-style",
        required=True,
        choices=sorted(STYLE_LABELS),
        help="User-selected writing style for topic explanations and worked examples.",
    )
    command.add_argument(
        "--language",
        required=True,
        choices=sorted(LANGUAGE_CHOICES),
        help=(
            "Term-support language. The handbook body stays English; non-en "
            "values add a 30-50 item professional glossary."
        ),
    )
    command.add_argument("--image-model", help="Model name when --image-provider custom.")
    command.add_argument("--image-endpoint-url", help="Custom image API endpoint URL.")
    command.add_argument(
        "--image-api-key-env",
        help="Environment variable name that stores the custom image API key. Do not pass raw keys.",
    )


def validate_generation_choices(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.image_provider != "custom":
        return
    missing = [
        flag
        for flag, value in [
            ("--image-model", args.image_model),
            ("--image-endpoint-url", args.image_endpoint_url),
            ("--image-api-key-env", args.image_api_key_env),
        ]
        if not value
    ]
    if missing:
        parser.error("--image-provider custom requires " + ", ".join(missing))
    if not os.environ.get(args.image_api_key_env):
        parser.error(
            "--image-provider custom requires environment variable "
            f"{args.image_api_key_env} to be set"
        )


def resolve_provider(provider: str | None, query: str) -> str:
    """Return provider name: explicit choice, URL inference, or OxfordAQA default."""
    if provider:
        return provider
    if query.lower().startswith(("http://", "https://")):
        return infer_provider_from_url(query) or "oxfordaqa"
    return "oxfordaqa"


def resolve_and_download_qualification(
    query: str,
    provider_name: str | None,
    level: str | None,
    exam_year: str | None,
    source_dir: Path,
) -> Qualification:
    provider = get_provider(resolve_provider(provider_name, query))
    link = provider.find_qualification(query, level, exam_year)
    qualification = provider.parse_qualification(link.href, level, exam_year)
    qualification = provider.apply_listing_metadata(qualification, link)
    return provider.download_specification(qualification, source_dir, exam_year)


def write_evidence_package(qualification: Qualification, out_dir: Path) -> Path:
    (out_dir / "qualification.json").write_text(
        json.dumps(qualification.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return write_syllabus_evidence(
        qualification,
        out_dir,
        pages_from_extracted_text(qualification.source.extracted_text_path),
    )


def pages_from_extracted_text(path_value: str | None) -> list[tuple[int, str]]:
    if not path_value:
        return []
    path = Path(path_value)
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    pages: list[tuple[int, str]] = []
    for chunk in text.split("--- Page "):
        chunk = chunk.strip()
        if not chunk:
            continue
        header, _, body = chunk.partition("---")
        try:
            page_number = int(header.strip())
        except ValueError:
            continue
        pages.append((page_number, body.strip()))
    return pages


def load_demo_qualification() -> Qualification:
    data = json.loads(
        resources.files("intl_exam_guide")
        .joinpath("assets/demo_qualification.json")
        .read_text(encoding="utf-8")
    )
    return Qualification.from_dict(data)


def write_guide_outputs(
    qualification: Qualification,
    out_dir: Path,
    questions_per_topic: int,
    skip_pdf: bool,
    image_provider: str | None,
    explanation_style: str,
    output_language: str,
    requested_subject: str,
    exam_year: str | None,
    image_model: str | None,
    image_endpoint_url: str | None,
    image_api_key_env: str | None,
    *,
    provider: str | None = None,
    level: str | None = None,
) -> int:
    plan = build_guide_plan(
        qualification,
        questions_per_topic=questions_per_topic,
        image_provider=image_provider,
        explanation_style=explanation_style,
        output_language=output_language,
        requested_subject=requested_subject,
        exam_year=exam_year,
        image_model=image_model,
        image_endpoint_url=image_endpoint_url,
        image_api_key_env=image_api_key_env,
    )

    qualification_path = out_dir / "qualification.json"
    plan_path = out_dir / "guide-plan.json"
    html_path, pdf_path = default_handbook_paths(out_dir, plan.qualification)
    validation_path = out_dir / "validation.json"
    delivery_contract_path = out_dir / "delivery-contract.json"
    run_options_path = out_dir / "run-options.json"
    if pdf_path.exists():
        pdf_path.unlink()

    qualification_path.write_text(
        json.dumps(plan.qualification.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # CLI fallback writes evidence and a placeholder outline so demo runs stay
    # structurally complete. The CLI is not an LLM Analyst; teaching-grade
    # output must come from the Skill host's analyst callback.
    write_syllabus_evidence(plan.qualification, out_dir, [])
    outline_payload: dict[str, object] = {
        "schema_version": "v0.5-cli-fallback-outline",
        "status": "cli-fallback-not-llm-analyst",
        "note": "Generated by CLI without an LLM syllabus_outline_analyst pass. Treat as draft evidence only.",
        "course_spec": {
            "title": plan.qualification.title,
            "code": plan.qualification.code,
            "qualification_type": plan.qualification.qualification_type,
            "subject_area": plan.qualification.subject_area,
            "provider": plan.qualification.provider or plan.qualification.source.provider,
            "page_url": plan.qualification.page_url,
            "specification_url": plan.qualification.source.specification_url,
        },
        "topics": [
            {
                "title": topic.title,
                "exam_points": list(topic.points),
                "level_tags": list(topic.level_tags),
                "source_snippets": [
                    {
                        "page": snippet.page,
                        "text": snippet.text,
                        "matched_term": snippet.matched_term,
                    }
                    for snippet in topic.source_snippets
                ],
            }
            for topic in plan.qualification.topics
        ],
    }
    write_syllabus_outline(out_dir, outline_payload)
    if "outline-source:llm-analyst" not in plan.qualification.route_tags:
        fallback_qualification = Qualification(
            title=plan.qualification.title,
            code=plan.qualification.code,
            qualification_type=plan.qualification.qualification_type,
            subject_area=plan.qualification.subject_area,
            page_url=plan.qualification.page_url,
            summary=plan.qualification.summary,
            topics=plan.qualification.topics,
            assessments=plan.qualification.assessments,
            source=plan.qualification.source,
            audience_note=plan.qualification.audience_note,
            provider=plan.qualification.provider,
            qualification_family=plan.qualification.qualification_family,
            selected_exam_year=plan.qualification.selected_exam_year,
            route_tags=[*plan.qualification.route_tags, "outline-source:cli-fallback"],
            command_words=plan.qualification.command_words,
            assessment_objectives=plan.qualification.assessment_objectives,
        )
        plan = type(plan)(
            qualification=fallback_qualification,
            run_options=plan.run_options,
            topic_guides=plan.topic_guides,
            practice_items=plan.practice_items,
            visual_briefs=plan.visual_briefs,
            diagram_briefs=plan.diagram_briefs,
            revision_stages=plan.revision_stages,
        )
        qualification_path.write_text(
            json.dumps(plan.qualification.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    run_options_path.write_text(
        json.dumps(plan.run_options.__dict__, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plan_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    package_manifest = write_handbook_package(plan, out_dir)
    render_html(plan, html_path, out_dir / "images" / "visual_manifest.json")

    pdf_error: str | None = None
    if not skip_pdf:
        try:
            export_pdf(html_path, pdf_path)
        except PdfExportError as exc:  # pragma: no cover - depends on local browser
            pdf_error = str(exc)

    quality_inspection_path = write_quality_inspection(out_dir)

    issues = validate_plan(
        plan,
        html_path=html_path,
        pdf_path=None if skip_pdf else pdf_path,
        output_dir=out_dir,
    )
    summary = review_summary(
        plan,
        html_path=html_path,
        pdf_path=None if skip_pdf else pdf_path,
        output_dir=out_dir,
    )
    delivery_status = delivery_status_from_issues(issues, summary)
    delivery_contract = course_contract_payload(
        plan,
        delivery_status,
        quality_inspection_complete=quality_inspection_path.exists(),
    )
    delivery_contract_path.write_text(
        json.dumps(delivery_contract, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    payload = {
        "qualification": qualification.title,
        "html": str(html_path),
        "pdf": str(pdf_path) if pdf_path.exists() else None,
        "pdf_error": pdf_error,
        "package": package_manifest,
        "delivery_contract": str(delivery_contract_path),
        "quality_inspection": str(quality_inspection_path),
        "review_summary": summary,
        "delivery_status": delivery_status,
        "delivery_state": delivery_contract["delivery_state"],
        "issues": issues_to_dict(issues),
    }
    validation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print clear warning for CLI-generated output
    print("\n" + "=" * 80, file=sys.stderr)
    print("WARNING: CLI FRAMEWORK DEMO ONLY", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "This output was generated by Python CLI without LLM content generation.", file=sys.stderr
    )
    print("", file=sys.stderr)
    print(
        "Python no longer attempts to parse topics or generate content automatically.",
        file=sys.stderr,
    )
    print("To generate a complete, teaching-grade handbook:", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "  1. Use this Skill in an LLM agent environment with the extracted evidence.", file=sys.stderr
    )
    print("  2. The host LLM must run the lightweight workflow:", file=sys.stderr)
    print("     - Analyst: read syllabus evidence and write syllabus-outline.json", file=sys.stderr)
    print("     - Writer: write concepts, mastery summaries, and visual decisions", file=sys.stderr)
    print("     - Reviewer: open the rendered HTML and audit it against the evidence", file=sys.stderr)
    print("", file=sys.stderr)
    print("See skill/SKILL.md for LLM workflow instructions.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Current output status: {}".format(delivery_status), file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("", file=sys.stderr)

    print_json_payload(payload)
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
