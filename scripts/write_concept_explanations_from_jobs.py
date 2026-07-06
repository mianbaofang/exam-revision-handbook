from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REFUSAL_REASON = (
    "Python does not write teaching content or decide visual need. "
    "Use the Skill host LLM to write concepts/concept_explanations.json from "
    "concepts/concept_jobs.json, including mastery_summary and visual_decision for every topic."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Legacy command placeholder; concept explanations must be LLM-authored."
    )
    parser.add_argument("output_dir", help="Generated guide output directory.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Accepted for legacy CLI compatibility; this command still refuses to write content.",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir).resolve()
    jobs_path = output_dir / "concepts" / "concept_jobs.json"
    target = output_dir / "concepts" / "concept_explanations.json"
    payload = {
        "ok": False,
        "reason": REFUSAL_REASON,
        "concept_jobs": str(jobs_path),
        "target": str(target),
        "concept_jobs_present": jobs_path.exists(),
        "next_step": (
            "Ask the host LLM Writer to read concept_jobs.json and write the current "
            "concept_explanations.json contract. Then import or rerender through the normal Skill flow."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
