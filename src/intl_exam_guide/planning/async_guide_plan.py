"""Async helpers for guide planning with a host WriterAgent."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from intl_exam_guide.auditing.concept_jobs import write_concept_jobs
from intl_exam_guide.llm.provider import ConceptExplanation, ConceptJob
from intl_exam_guide.models import GuidePlan, Qualification
from intl_exam_guide.planning.concept_integration import (
    apply_concept_entries,
    collect_concept_jobs,
    concept_entries_from_explanations,
)
from intl_exam_guide.planning.guide_plan import build_guide_plan, is_scope_exclusion_topic
from intl_exam_guide.planning.syllabus_outline import (
    apply_syllabus_outline_response,
    build_syllabus_evidence,
    build_syllabus_outline_prompt,
    write_syllabus_evidence,
    write_syllabus_outline,
)

logger = logging.getLogger(__name__)


class AnalystAgentProtocol(Protocol):
    async def analyze(self, prompt: str) -> str | dict[str, object]: ...


class WriterAgentProtocol(Protocol):
    async def write_all(self, jobs: list[ConceptJob]) -> list[ConceptExplanation]: ...


async def build_guide_plan_with_writer_agent(
    qualification: Qualification,
    writer_agent: WriterAgentProtocol,
    questions_per_topic: int = 1,
    analyst_agent: AnalystAgentProtocol | None = None,
    image_provider: str | None = None,
    explanation_style: str = "friendly",
    output_language: str = "en",
    requested_subject: str | None = None,
    exam_year: str | None = None,
    image_model: str | None = None,
    image_endpoint_url: str | None = None,
    image_api_key_env: str | None = None,
    output_dir: Path | None = None,
    **_: object,
) -> GuidePlan:
    """Run Analyst outline first, then build a plan and apply WriterAgent concepts."""

    if output_dir:
        write_syllabus_evidence(qualification, output_dir, [])
    if analyst_agent:
        evidence = build_syllabus_evidence(qualification, [])
        try:
            response = await analyst_agent.analyze(
                build_syllabus_outline_prompt(qualification, evidence)
            )
            outline_result = apply_syllabus_outline_response(qualification, response)
        except Exception as exc:
            logger.error(
                "AnalystAgent syllabus outlining failed: %s. Keeping draft provider evidence.", exc
            )
        else:
            if outline_result.ok:
                qualification = outline_result.qualification
                if output_dir:
                    write_syllabus_outline(output_dir, outline_result.outline)
            else:
                logger.error(
                    "AnalystAgent returned invalid syllabus outline: %s",
                    "; ".join(issue.message for issue in outline_result.issues),
                )

    guide_plan = build_guide_plan(
        qualification=qualification,
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

    handbook_topics = [
        topic for topic in guide_plan.qualification.topics if not is_scope_exclusion_topic(topic)
    ]
    jobs = collect_concept_jobs(
        handbook_topics,
        guide_plan.qualification.subject_area or "General",
        guide_plan.qualification.qualification_type,
    )
    if output_dir:
        write_concept_jobs(guide_plan, output_dir)
    if not jobs:
        return guide_plan

    try:
        explanations = await writer_agent.write_all(jobs)
    except Exception as exc:
        logger.error("WriterAgent generation failed: %s. Keeping draft plan.", exc)
        return guide_plan

    entries = concept_entries_from_explanations(jobs, explanations)
    apply_concept_entries(guide_plan, entries)
    return guide_plan
