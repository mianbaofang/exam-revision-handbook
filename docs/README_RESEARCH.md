# README Presentation Research Notes

These notes summarize README presentation patterns observed from high-star
GitHub projects. They are not technical architecture references for this
project and are not comparable education or syllabus-generation tools.

Audit date: 2026-06-14. Star counts were checked with the public GitHub API.

## Repositories Checked For README Presentation Only

| Repository | Observed stars during research | README presentation pattern borrowed |
|---|---:|---|
| [open-webui/open-webui](https://github.com/open-webui/open-webui) | 141,366 | Badges, banner image, demo image, key features, install options, docs links |
| [astral-sh/uv](https://github.com/astral-sh/uv) | 86,333 | Sharp one-line positioning, fast quick-start path, clean package identity |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | 47,960 | Table of contents, installation commands, configuration, contribution links |
| [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | 82,648 | Trust messaging around grounded answers, citations, and reduced hallucinations |
| [matiassingers/awesome-readme](https://github.com/matiassingers/awesome-readme) | 21,034 | Recommends images, screenshots, GIFs, text formatting, badges, and navigation |
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | 99,167 | Strong bilingual/community-friendly docs and production-readiness messaging |

## Design Decisions Applied

Only README and documentation presentation decisions were borrowed:

1. Use a hero image and diagrams instead of a plain text wall.
2. Put a one-sentence project identity at the top.
3. Offer English and Chinese entry points.
4. Show quick start before implementation details.
5. Explain trust and accuracy before advanced generation.
6. Include examples of generated output.
7. Link to deeper docs instead of overloading the README.
8. Keep downloaded PDFs out of source control.

The core architecture, source-traceability model, OxfordAQA provider, parser,
validation gates, and generated guide structure are project-specific.

## Current Visual Policy

This research note is historical and does not define the runtime visual route.
The current Skill prefers a reviewed external raster infographic whenever it
adds teaching value, with landscape `4:3` as the default and `3:2` also allowed.
SVG is a last-resort exactness exception only: it must be explicitly justified,
marked `svg_fit="exact"`, and reviewed before delivery. A simple line-art SVG is
not a substitute for a richer external visual when a callable image route exists.
