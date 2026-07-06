"""
Skill-optimized handbook generation interface.

This module is for Agent runtimes where an LLM is already present. The Python
code builds the handbook package and records artifacts; the host Agent/LLM writes
concept explanations through the provided callback.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

from intl_exam_guide.core import course_contract_payload
from intl_exam_guide.auditing.quality_inspector import write_quality_inspection
from intl_exam_guide.auditing.concept_jobs import build_concept_jobs, write_concept_jobs
from intl_exam_guide.llm.provider import ConceptExplanation, ConceptJob
from intl_exam_guide.models import GuidePlan, Qualification
from intl_exam_guide.planning.concept_integration import (
    apply_concept_entries,
    concept_entry_from_callback_response,
)
from intl_exam_guide.planning.guide_plan import build_guide_plan, is_scope_exclusion_topic
from intl_exam_guide.planning.syllabus_outline import (
    apply_syllabus_outline_response,
    build_syllabus_evidence,
    build_syllabus_outline_prompt,
    write_syllabus_evidence,
    write_syllabus_outline,
)
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

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Progress information for handbook generation."""

    stage: str
    current: int
    total: int
    message: str


class SkillHandbookGenerator:
    """Generate handbooks in a Skill host using the current conversation LLM."""

    def __init__(
        self,
        llm_callback: Callable[[str], Awaitable[str]],
        progress_callback: Callable[[GenerationProgress], None] | None = None,
        analyst_callback: Callable[[str], Awaitable[str]] | None = None,
    ):
        self.llm_callback = llm_callback
        self.progress_callback = progress_callback
        self.analyst_callback = analyst_callback

    def _report_progress(self, stage: str, current: int, total: int, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(GenerationProgress(stage, current, total, message))

    async def generate(
        self,
        qualification: Qualification,
        output_dir: str | Path,
        questions_per_topic: int = 1,
        explanation_style: str = "friendly",
        output_language: str = "en",
        skip_pdf: bool = False,
    ) -> Path:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self._report_progress(
            "analysis", 0, 7, "Preparing syllabus evidence for LLM outline analysis..."
        )
        qualification = await self._apply_analyst_outline(qualification, output_path)

        self._report_progress("planning", 1, 7, "Building handbook structure...")
        plan = build_guide_plan(
            qualification=qualification,
            questions_per_topic=questions_per_topic,
            explanation_style=explanation_style,
            output_language=output_language,
            requested_subject=qualification.subject_area or qualification.title,
        )

        self._write_base_artifacts(plan, output_path)
        concept_jobs = write_concept_jobs(plan, output_path)

        if concept_jobs:
            self._report_progress(
                "concepts", 3, 7, f"Writing {len(concept_jobs)} concept explanations..."
            )
            entries = await self._write_concept_entries_async(concept_jobs)
            if entries:
                imported, missing = apply_concept_entries(plan, entries)
                self._write_concept_explanations(output_path, entries)
                if missing:
                    logger.warning(
                        "Concept explanations did not match topics: %s", ", ".join(missing)
                    )
                logger.info("Imported %s concept explanation entries", imported)
                self._write_plan(plan, output_path)

        self._report_progress("package", 4, 7, "Writing handbook package...")
        write_handbook_package(plan, output_path)

        self._report_progress("rendering", 5, 7, "Rendering HTML and PDF...")
        html_output, pdf_output = default_handbook_paths(output_path, plan.qualification)
        html_path = render_html(
            plan, html_output, output_path / "images" / "visual_manifest.json"
        )
        pdf_path = pdf_output
        pdf_error: str | None = None
        if not skip_pdf:
            try:
                export_pdf(html_path, pdf_path)
            except PdfExportError as exc:
                pdf_error = str(exc)
                logger.warning("PDF generation failed: %s", exc)

        self._report_progress("validation", 6, 7, "Running quality checks...")
        write_quality_inspection(output_path)
        self._write_validation(
            plan, output_path, html_path, None if skip_pdf else pdf_path, pdf_error
        )
        self._report_progress("complete", 7, 7, "Generation complete.")
        return html_path

    async def _apply_analyst_outline(
        self,
        qualification: Qualification,
        output_path: Path,
    ) -> Qualification:
        pages = _pages_from_extracted_text(qualification.source.extracted_text_path)
        write_syllabus_evidence(qualification, output_path, pages)
        if not self.analyst_callback:
            logger.warning(
                "No syllabus analyst callback supplied. Keeping provider topics as draft evidence only."
            )
            return qualification
        evidence = build_syllabus_evidence(qualification, pages)
        prompt = build_syllabus_outline_prompt(qualification, evidence)
        response = await self.analyst_callback(prompt)
        result = apply_syllabus_outline_response(qualification, response)
        write_syllabus_outline(output_path, result.outline)
        if not result.ok:
            messages = "; ".join(issue.message for issue in result.issues)
            raise ValueError(f"Syllabus analyst outline is invalid: {messages}")
        (output_path / "qualification.json").write_text(
            json.dumps(result.qualification.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return result.qualification

    async def _write_concept_entries_async(
        self,
        jobs: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        for index, job in enumerate(jobs, start=1):
            logger.info("Writing concept %s/%s: %s", index, len(jobs), job.get("topic_title"))
            try:
                response = await self.llm_callback(self._build_concept_prompt(job))
                entry = concept_entry_from_callback_response(job, response)
                if entry:
                    entries.append(entry)
            except Exception as exc:
                logger.error("Failed to write concept %s: %s", job.get("topic_title"), exc)
        return entries

    @staticmethod
    def _build_concept_prompt(job: dict[str, object] | ConceptJob) -> str:
        if isinstance(job, ConceptJob):
            topic_title = job.topic_title
            student_title = job.topic_title
            source_points = [job.context_snippet]
            task = "Write 2-3 source-bound student-facing concept explanation bullets."
            subject = job.subject
            level = job.level
        else:
            topic_title = str(job.get("topic_title") or "")
            student_title = str(job.get("student_title") or topic_title)
            raw_source_points = job.get("source_points", [])
            source_points = (
                [str(point) for point in raw_source_points if str(point).strip()]
                if isinstance(raw_source_points, list)
                else []
            )
            task = str(
                job.get("task")
                or "Write 2-3 source-bound student-facing concept explanation bullets."
            )
            subject = str(job.get("subject_pack") or "")
            level = ""
        return "\n".join(
            [
                "Write the final concept explanations for this handbook topic.",
                "Return JSON only, with keys: topic_title, essence, analogy, mastery_summary, mini_worked_example, pitfall, explanations, and optional visual_spec.",
                "The explanations value must be a list of 2-4 direct student-facing bullets.",
                "The mastery_summary value must be one concrete student-facing sentence for the Study Roadmap 'What to master' column.",
                "Stay inside the topic title and source points. Do not write a procedural checklist.",
                "Add visual_spec only when a visual materially improves understanding.",
                "For visual_spec, use complexity='svg-basic' with svg_fit='exact' only for exact-fit diagrams such as axes, set regions, simple flows, tables, trees, or timelines.",
                "Use complexity='infographic' for visuals needing nuance, realistic setup, multiple linked states, rich annotation, or modelling assumptions.",
                f"Topic title: {topic_title}",
                f"Student title: {student_title}",
                f"Subject: {subject}",
                f"Level: {level}",
                f"Task: {task}",
                "Source points:",
                *[f"- {point}" for point in source_points],
            ]
        )

    def _parse_concept_response(self, concept_term: str, response: str) -> ConceptExplanation:
        entry = concept_entry_from_callback_response(
            {"topic_title": concept_term, "student_title": concept_term},
            response,
        )
        if entry:
            explanations = entry.get("explanations")
            first = explanations[0] if isinstance(explanations, list) and explanations else ""
            return ConceptExplanation(
                concept_term=concept_term,
                explanation=str(entry.get("essence") or first),
                analogy=str(entry.get("analogy") or "") or None,
                example=str(entry.get("mini_worked_example") or "") or None,
                common_misconception=str(entry.get("pitfall") or "") or None,
                status="generated",
            )
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return ConceptExplanation(
                concept_term=concept_term, explanation=response, status="generated"
            )
        return ConceptExplanation(
            concept_term=concept_term,
            explanation=str(data.get("explanation") or ""),
            analogy=data.get("analogy"),
            example=data.get("example"),
            common_misconception=data.get("common_misconception") or data.get("misconception"),
            status="generated" if data.get("explanation") else "failed",
        )

    async def _generate_concepts_async(self, jobs: list[ConceptJob]) -> list[ConceptExplanation]:
        explanations: list[ConceptExplanation] = []
        for job in jobs:
            try:
                response = await self.llm_callback(self._build_concept_prompt(job))
                explanations.append(self._parse_concept_response(job.concept_term, response))
            except Exception as exc:
                logger.error("Failed to generate concept %s: %s", job.concept_term, exc)
                explanations.append(
                    ConceptExplanation(
                        concept_term=job.concept_term, explanation="", status="failed"
                    )
                )
        return explanations

    def _write_base_artifacts(self, plan: GuidePlan, output_dir: Path) -> None:
        (output_dir / "qualification.json").write_text(
            json.dumps(plan.qualification.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (output_dir / "run-options.json").write_text(
            json.dumps(plan.run_options.__dict__, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._write_plan(plan, output_dir)

    def _write_plan(self, plan: GuidePlan, output_dir: Path) -> None:
        (output_dir / "guide-plan.json").write_text(
            json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_concept_explanations(
        self,
        output_dir: Path,
        entries: list[dict[str, object]],
    ) -> None:
        concepts_dir = output_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        (concepts_dir / "concept_explanations.json").write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_validation(
        self,
        plan: GuidePlan,
        output_dir: Path,
        html_path: Path,
        pdf_path: Path | None,
        pdf_error: str | None,
    ) -> None:
        issues = validate_plan(plan, html_path=html_path, pdf_path=pdf_path, output_dir=output_dir)
        summary = review_summary(
            plan, html_path=html_path, pdf_path=pdf_path, output_dir=output_dir
        )
        delivery_status = delivery_status_from_issues(issues, summary)
        contract = course_contract_payload(
            plan,
            delivery_status,
            quality_inspection_complete=(output_dir / "quality-inspection.json").exists(),
        )
        (output_dir / "delivery-contract.json").write_text(
            json.dumps(contract, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        payload = {
            "qualification": plan.qualification.title,
            "html": str(html_path),
            "pdf": str(pdf_path) if pdf_path and pdf_path.exists() else None,
            "pdf_error": pdf_error,
            "quality_inspection": str(output_dir / "quality-inspection.json"),
            "review_summary": summary,
            "delivery_status": delivery_status,
            "delivery_state": contract["delivery_state"],
            "issues": issues_to_dict(issues),
        }
        (output_dir / "validation.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class IncrementalGenerator:
    """Step-by-step generation for interactive Skill hosts."""

    def __init__(
        self,
        qualification: Qualification,
        output_dir: str | Path,
        questions_per_topic: int = 1,
        explanation_style: str = "friendly",
        output_language: str = "en",
    ):
        self.qualification = qualification
        self.output_dir = Path(output_dir)
        self.questions_per_topic = questions_per_topic
        self.explanation_style = explanation_style
        self.output_language = output_language
        self.plan: GuidePlan | None = None
        self.concept_jobs: list[dict[str, object]] = []
        self.concept_explanations: list[ConceptExplanation] = []
        self.current_concept_index = 0

    def step1_prepare(self) -> dict[str, object]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plan = build_guide_plan(
            qualification=self.qualification,
            questions_per_topic=self.questions_per_topic,
            explanation_style=self.explanation_style,
            output_language=self.output_language,
            requested_subject=self.qualification.subject_area or self.qualification.title,
        )
        (self.output_dir / "qualification.json").write_text(
            json.dumps(self.plan.qualification.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.output_dir / "run-options.json").write_text(
            json.dumps(self.plan.run_options.__dict__, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.output_dir / "guide-plan.json").write_text(
            json.dumps(self.plan.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.concept_jobs = build_concept_jobs(self.plan)
        write_concept_jobs(self.plan, self.output_dir)
        self.concept_explanations = []
        return {
            "total_topics": len(self.plan.topic_guides),
            "total_concepts": len(self.concept_jobs),
            "total_practice": len(self.plan.practice_items),
            "output_dir": str(self.output_dir),
        }

    def step2_get_next_concept(self) -> dict[str, object]:
        if self.current_concept_index >= len(self.concept_jobs):
            return {"status": "done", "message": "All concepts generated"}
        job = self.concept_jobs[self.current_concept_index]
        return {
            "status": "ready",
            "concept_index": self.current_concept_index + 1,
            "total_concepts": len(self.concept_jobs),
            "concept_term": job.get("student_title") or job.get("topic_title"),
            "topic_title": job.get("topic_title"),
            "prompt": SkillHandbookGenerator._build_concept_prompt(job),
        }

    def step2_submit_concept(
        self,
        content: str,
        analogy: str = "",
        misconception: str = "",
        visual_spec: dict[str, object] | None = None,
        mastery_summary: str = "",
    ) -> None:
        if not self.plan:
            raise ValueError("Must call step1_prepare first")
        if self.current_concept_index >= len(self.concept_jobs):
            raise ValueError("No more concepts to generate")
        job = self.concept_jobs[self.current_concept_index]
        metadata: dict[str, object] = {"topic_title": str(job.get("topic_title") or "")}
        if mastery_summary.strip():
            metadata["mastery_summary"] = mastery_summary.strip()
        if visual_spec:
            metadata["visual_spec"] = visual_spec
        self.concept_explanations.append(
            ConceptExplanation(
                concept_term=str(job.get("student_title") or job.get("topic_title") or ""),
                explanation=content,
                analogy=analogy or None,
                common_misconception=misconception or None,
                status="generated",
                metadata=metadata,
            )
        )
        self.current_concept_index += 1

    def step2_skip_concept(self) -> None:
        if not self.plan:
            raise ValueError("Must call step1_prepare first")
        if self.current_concept_index >= len(self.concept_jobs):
            raise ValueError("No more concepts to skip")
        job = self.concept_jobs[self.current_concept_index]
        self.concept_explanations.append(
            ConceptExplanation(
                concept_term=str(job.get("student_title") or job.get("topic_title") or ""),
                explanation="",
                status="failed",
                metadata={"topic_title": str(job.get("topic_title") or "")},
            )
        )
        self.current_concept_index += 1

    def step3_render(self, skip_pdf: bool = False) -> dict[str, object]:
        if not self.plan:
            raise ValueError("Must call step1_prepare first")
        entries = self._incremental_entries()
        if entries:
            apply_concept_entries(self.plan, entries)
            concepts_dir = self.output_dir / "concepts"
            concepts_dir.mkdir(parents=True, exist_ok=True)
            (concepts_dir / "concept_explanations.json").write_text(
                json.dumps(entries, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        (self.output_dir / "guide-plan.json").write_text(
            json.dumps(self.plan.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        write_handbook_package(self.plan, self.output_dir)
        html_output, pdf_output = default_handbook_paths(self.output_dir, self.plan.qualification)
        html_path = render_html(
            self.plan,
            html_output,
            self.output_dir / "images" / "visual_manifest.json",
        )
        result: dict[str, object] = {"html_path": str(html_path)}
        pdf_path = pdf_output
        if not skip_pdf:
            try:
                export_pdf(html_path, pdf_path)
                result["pdf_path"] = str(pdf_path)
            except PdfExportError as exc:
                result["pdf_error"] = str(exc)
        issues = validate_plan(
            self.plan,
            html_path=html_path,
            pdf_path=None if skip_pdf else pdf_path,
            output_dir=self.output_dir,
        )
        write_quality_inspection(self.output_dir)
        summary = review_summary(
            self.plan,
            html_path=html_path,
            pdf_path=None if skip_pdf else pdf_path,
            output_dir=self.output_dir,
        )
        delivery_status = delivery_status_from_issues(issues, summary)
        contract = course_contract_payload(
            self.plan,
            delivery_status,
            quality_inspection_complete=(self.output_dir / "quality-inspection.json").exists(),
        )
        (self.output_dir / "delivery-contract.json").write_text(
            json.dumps(contract, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.output_dir / "validation.json").write_text(
            json.dumps(
                {
                    "html": str(html_path),
                    "pdf": result.get("pdf_path"),
                    "pdf_error": result.get("pdf_error"),
                    "quality_inspection": str(self.output_dir / "quality-inspection.json"),
                    "review_summary": summary,
                    "delivery_status": delivery_status,
                    "delivery_state": contract["delivery_state"],
                    "issues": issues_to_dict(issues),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        result["validation_issues"] = len(issues)
        return result

    def _incremental_entries(self) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        for explanation in self.concept_explanations:
            if explanation.status != "generated" or not explanation.explanation.strip():
                continue
            topic_title = str(explanation.metadata.get("topic_title") or explanation.concept_term)
            values = [explanation.explanation]
            if explanation.analogy:
                values.append(explanation.analogy)
            if explanation.common_misconception:
                values.append(explanation.common_misconception)
            if len(values) < 2:
                values.append(explanation.explanation)
            entry: dict[str, object] = {
                "topic_title": topic_title,
                "concept_term": explanation.concept_term,
                "explanations": values[:4],
                "essence": explanation.explanation,
            }
            mastery_summary = explanation.metadata.get("mastery_summary")
            if isinstance(mastery_summary, str) and mastery_summary.strip():
                entry["mastery_summary"] = mastery_summary.strip()
            if explanation.analogy:
                entry["analogy"] = explanation.analogy
            if explanation.common_misconception:
                entry["pitfall"] = explanation.common_misconception
            visual_spec = explanation.metadata.get("visual_spec")
            if isinstance(visual_spec, dict):
                entry["visual_spec"] = visual_spec
            entries.append(entry)
        return entries

    def get_progress(self) -> dict[str, object]:
        return {
            "step": "preparation"
            if not self.plan
            else (
                "generation"
                if self.current_concept_index < len(self.concept_jobs)
                else "ready_to_render"
            ),
            "concepts_generated": self.current_concept_index,
            "concepts_total": len(self.concept_jobs),
            "concepts_remaining": len(self.concept_jobs) - self.current_concept_index,
        }

    def save_state(self, state_file: str | Path) -> None:
        state = {
            "current_concept_index": self.current_concept_index,
            "concept_explanations": [
                {
                    "concept_term": explanation.concept_term,
                    "explanation": explanation.explanation,
                    "analogy": explanation.analogy,
                    "example": explanation.example,
                    "common_misconception": explanation.common_misconception,
                    "status": explanation.status,
                    "metadata": explanation.metadata,
                }
                for explanation in self.concept_explanations
            ],
        }
        Path(state_file).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_state(self, state_file: str | Path) -> None:
        state = json.loads(Path(state_file).read_text(encoding="utf-8"))
        self.current_concept_index = int(state["current_concept_index"])
        self.concept_explanations = [
            ConceptExplanation(
                concept_term=str(item.get("concept_term") or ""),
                explanation=str(item.get("explanation") or ""),
                analogy=item.get("analogy"),
                example=item.get("example"),
                common_misconception=item.get("common_misconception"),
                status=item.get("status", "pending"),
                metadata=item.get("metadata", {}),
            )
            for item in state.get("concept_explanations", [])
            if isinstance(item, dict)
        ]


def handbook_topics(plan: GuidePlan) -> list[object]:
    return [topic for topic in plan.qualification.topics if not is_scope_exclusion_topic(topic)]


def _pages_from_extracted_text(path_value: str | None) -> list[tuple[int, str]]:
    if not path_value:
        return []
    path = Path(path_value)
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    pages: list[tuple[int, str]] = []
    chunks = text.split("--- Page ")
    for chunk in chunks:
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


__all__ = [
    "SkillHandbookGenerator",
    "IncrementalGenerator",
    "GenerationProgress",
]
