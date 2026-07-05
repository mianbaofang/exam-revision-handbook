"""Fallback provider for when an external LLM provider is unavailable."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from intl_exam_guide.llm.provider import (
    ConceptExplanation,
    ConceptJob,
    LLMContextProvider,
)

logger = logging.getLogger(__name__)


class FallbackProvider(LLMContextProvider):
    """Write concept jobs to the standard handbook concepts directory."""

    def __init__(self, output_dir: Path | str):
        self.output_dir = Path(output_dir)

    def generate_concept_explanations(
        self,
        jobs: list[ConceptJob],
        max_concurrency: int = 5,
    ) -> list[ConceptExplanation]:
        """Write concept jobs and return pending explanation records."""

        concepts_dir = self._concepts_dir()
        jobs_file = concepts_dir / "concept_jobs.json"
        jobs_file.parent.mkdir(parents=True, exist_ok=True)
        jobs_data = [self._job_to_dict(index, job) for index, job in enumerate(jobs, start=1)]
        jobs_file.write_text(json.dumps(jobs_data, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.warning(
            "LLM unavailable. %s concept jobs written to %s. Generate explanations manually "
            "with the Skill host LLM and import them before final delivery.",
            len(jobs),
            jobs_file,
        )
        return [
            ConceptExplanation(
                concept_term=job.concept_term,
                explanation="",
                status="pending",
                metadata={"fallback": True, "topic_title": job.topic_title},
            )
            for job in jobs
        ]

    def estimate_cost(self, jobs: list[ConceptJob]) -> float:
        return 0.0

    def _concepts_dir(self) -> Path:
        if self.output_dir.name == "concepts":
            return self.output_dir
        return self.output_dir / "concepts"

    def _job_to_dict(self, index: int, job: ConceptJob) -> dict[str, object]:
        source_points = [job.context_snippet] if job.context_snippet else []
        return {
            "id": job.topic_id or f"concept_{index:03d}",
            "topic_id": job.topic_id,
            "concept_term": job.concept_term,
            "context": job.context_snippet,
            "contract_version": "v0.4-pedagogy-mvp",
            "topic_title": job.topic_title,
            "student_title": job.topic_title,
            "output_language": "en",
            "subject_pack": job.subject.lower() or "generic",
            "current_draft": [],
            "source_points": source_points,
            "source_pages": [],
            "task": (
                "Write 2-3 student-facing concept explanation bullets. Stay inside "
                "topic_title and source_points; explain what the concept is, what "
                "relationship or boundary it describes, and why it is central."
            ),
            "provider_job": {
                "topic_id": job.topic_id,
                "concept_term": job.concept_term,
                "subject": job.subject,
                "level": job.level,
                "context_snippet": job.context_snippet,
            },
        }
