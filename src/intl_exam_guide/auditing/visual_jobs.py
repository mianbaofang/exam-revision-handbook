from __future__ import annotations


PENDING_STATUSES = {
    "external-generation-required",
    "infographic-provider-required",
    "provider-selected-pending-generation",
    "svg-fallback-needs-review",
    "professional-diagram-required",
}
IMPORT_HINT = (
    "Import with scripts/import_infographic_assets.py using a file named with this visual ID."
)


def build_visual_jobs(manifest: list[dict[str, object]]) -> list[dict[str, object]]:
    jobs: list[dict[str, object]] = []
    for entry in manifest:
        if str(entry.get("asset_status", "")).lower() not in PENDING_STATUSES:
            continue
        jobs.append(
            {
                "id": entry.get("id"),
                "topic_title": entry.get("topic_title"),
                "status": "needs_generation_or_review",
                "complexity": entry.get("complexity"),
                "visual_type": entry.get("visual_type"),
                "current_file": entry.get("file"),
                "replacement_target": entry.get("id"),
                "prompt": entry.get("prompt"),
                "source_pages": entry.get("source_pages", []),
                "import_hint": IMPORT_HINT,
            }
        )
    return jobs


def visual_jobs_markdown(jobs: list[dict[str, object]]) -> str:
    if not jobs:
        return "# Infographic Jobs\n\nNo pending complex infographic jobs.\n"

    lines = [
        "# Infographic Jobs",
        "",
        "These complex visuals are not final. Generate reviewed PNG/JPG/WebP assets for the IDs below, "
        "or keep the handbook marked as a draft.",
        "",
        "Generation choices:",
        "",
        "- Use an external image model or designer with the prompt under each visual ID.",
        "- Exact SVG or professional diagram assets must be reviewed before final delivery.",
        "- Name each generated file with the visual ID prefix, for example `visual_001.png` or `visual_001_tangent.png`.",
        "",
        "After generation, import and rebuild the handbook:",
        "",
        "`python scripts/import_infographic_assets.py <output-dir> --asset-dir <generated-asset-dir> --provider <provider-name>`",
        "",
        "The import script updates `images/visual_manifest.json` and re-renders `guide.html` and section files by default.",
        "",
    ]
    for job in jobs:
        raw_source_pages = job.get("source_pages", [])
        source_pages = raw_source_pages if isinstance(raw_source_pages, list) else []
        page_text = (
            ", ".join(str(page) for page in source_pages) if source_pages else "not recorded"
        )
        lines.extend(
            [
                f"## {job['id']} - {job['topic_title']}",
                "",
                f"- Status: {job['status']}",
                f"- Current fallback: {job['current_file']}",
                f"- Replacement target: {job['replacement_target']}",
                f"- Source pages: {page_text}",
                f"- Import hint: {job['import_hint']}",
                "",
                "Prompt:",
                "",
                str(job.get("prompt") or ""),
                "",
            ]
        )
    return "\n".join(lines)
