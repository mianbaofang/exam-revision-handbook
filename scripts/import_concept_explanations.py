from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import LLM-reviewed concept explanations into a generated guide."
    )
    parser.add_argument("output_dir", help="A generated guide output directory.")
    parser.add_argument(
        "--concept-file", required=True, help="JSON file with topic_title and explanations."
    )
    parser.add_argument(
        "--force", action="store_true", help="Replace existing concept explanations."
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    concept_file = Path(args.concept_file).resolve()
    plan_path = output_dir / "guide-plan.json"
    if not plan_path.exists():
        print(f"missing guide plan: {plan_path}", file=sys.stderr)
        return 1
    if not concept_file.exists():
        print(f"missing concept file: {concept_file}", file=sys.stderr)
        return 1

    from intl_exam_guide.models import GuidePlan
    from intl_exam_guide.planning.concept_integration import apply_concept_entries

    plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8-sig")))
    explanations = load_concept_explanations(concept_file)
    imported, missing = apply_concept_entries(plan, explanations, force=args.force)
    if missing:
        print(
            json.dumps(
                {"ok": False, "imported": imported, "missing": missing},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    plan_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    (concepts_dir / "concept_explanations.json").write_text(
        json.dumps(explanations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rerender_result = rerender_handbook(output_dir)
    if not rerender_result.get("rerendered"):
        print(
            json.dumps(
                {"ok": False, "imported": imported, "rerender": rerender_result},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "imported": imported,
                "concept_explanations": str(concepts_dir / "concept_explanations.json"),
                "rerender": rerender_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print("Review the updated handbook with:")
    print(f"python -m intl_exam_guide review --out {output_dir}")
    return 0


def load_concept_explanations(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("concept_explanations") or data.get("concepts") or data
    else:
        entries = data
    if isinstance(entries, dict):
        return [
            {"topic_title": title, "explanations": explanations}
            for title, explanations in entries.items()
        ]
    if not isinstance(entries, list):
        raise ValueError("concept file must contain a list or mapping")
    return [entry for entry in entries if isinstance(entry, dict)]


def apply_concept_explanations(
    plan: Any,
    explanations: list[dict[str, object]],
    force: bool = False,
) -> tuple[int, list[str]]:
    from intl_exam_guide.planning.concept_integration import apply_concept_entries

    return apply_concept_entries(plan, explanations, force=force)


def apply_optional_text(entry: dict[str, object], guide: object, field_name: str) -> None:
    value = entry.get(field_name)
    if isinstance(value, str) and value.strip():
        setattr(guide, field_name, value.strip())


def build_clean_diagram_brief(topic_title: str, values: list[str]) -> str:
    branches = [value.rstrip(".") for value in values[:3]]
    branch_text = ", ".join(branches) if branches else "definition, relationship, common pitfall"
    return (
        f"Draw a clean concept map for '{topic_title}' with the central title in the middle, "
        f"branches for {branch_text}, and one short exam-action label on each branch."
    )


def rerender_handbook(output_dir: Path) -> dict[str, object]:
    try:
        from intl_exam_guide.models import GuidePlan
        from intl_exam_guide.rendering.handbook_package import write_handbook_package
        from intl_exam_guide.rendering.html import render_html
        from intl_exam_guide.rendering.output_names import find_handbook_html, find_handbook_pdf
        from intl_exam_guide.rendering.visual_assets import load_visual_manifest
        from intl_exam_guide.rendering.handbook_package import visual_manifest_matches_plan

        plan_path = output_dir / "guide-plan.json"
        plan = GuidePlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8-sig")))
        manifest_path = output_dir / "images" / "visual_manifest.json"
        refresh_visual_manifest = not manifest_path.exists() or not visual_manifest_matches_plan(
            plan,
            load_visual_manifest(manifest_path),
        )
        write_handbook_package(
            plan,
            output_dir,
            refresh_visual_manifest=refresh_visual_manifest,
        )
        html_path = render_html(
            plan,
            find_handbook_html(output_dir, plan.qualification),
            output_dir / "images" / "visual_manifest.json",
        )
        result: dict[str, object] = {
            "rerendered": True,
            "html": str(html_path),
            "sections": str(output_dir / "sections"),
        }
        pdf_path = find_handbook_pdf(output_dir, plan.qualification)
        if pdf_path.exists():
            result["superseded_pdf"] = str(pdf_path)
        result["pdf_status"] = "blocked_pending_current_html_review"
        validation_path = output_dir / "validation.json"
        if validation_path.exists():
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
            if isinstance(validation, dict):
                validation["pdf"] = None
                validation["pdf_export_gate"] = {
                    "llm_html_review_required": True,
                    "status": "pending_current_html_review",
                }
                validation_path.write_text(
                    json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
                )
        return result
    except Exception as exc:  # pragma: no cover - defensive script boundary
        return {"rerendered": False, "reason": str(exc)}


if __name__ == "__main__":
    raise SystemExit(main())
