from __future__ import annotations

import json
from pathlib import Path

from intl_exam_guide.models import GuidePlan, Topic
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.planning.localization import zh_teachable_topic_title
from intl_exam_guide.planning.source_points import visible_source_points
from intl_exam_guide.subjects import (
    build_subject_review_job,
    build_subject_writing_job,
    resolve_subject_pack,
)


CONCEPT_REVIEW_FILE = "concept_explanations.json"


def build_concept_jobs(plan: GuidePlan) -> list[dict[str, object]]:
    topics = {topic.title: topic for topic in plan.qualification.topics}
    language = handbook_body_language(plan.run_options.output_language)
    jobs: list[dict[str, object]] = []
    for index, guide in enumerate(plan.topic_guides, start=1):
        topic = topics.get(guide.topic_title)
        source_points = visible_source_points(topic) if topic else []
        source_text = " ".join([guide.topic_title, *source_points])
        pack = resolve_subject_pack(plan.qualification.subject_area, topic, source_text)
        job_id = f"concept_{index:03d}"
        student_title = student_topic_title(topic, index, language)
        jobs.append(
            {
                "id": job_id,
                "contract_version": "v0.5-visual-decision-pedagogy",
                "topic_title": guide.topic_title,
                "student_title": student_title,
                "output_language": language,
                "subject_pack": pack.name,
                "priority_subject": pack.priority,
                "current_draft": guide.checklist[:3],
                "source_points": source_points,
                "source_pages": [
                    snippet.page for snippet in (topic.source_snippets if topic else [])
                ],
                "task": concept_task_text(language),
                "writing_contract": build_subject_writing_job(
                    job_id=job_id,
                    topic_title=guide.topic_title,
                    student_title=student_title,
                    source_points=source_points,
                    output_language=language,
                    pack=pack,
                ),
                "review_contract": build_subject_review_job(
                    writing_job_id=job_id,
                    topic_title=guide.topic_title,
                    output_language=language,
                    pack=pack,
                ),
                "visual_policy": {
                    "visual_guidance_required": True,
                    "external_route_available": bool(
                        plan.run_options.external_visual_capability == "yes"
                        and plan.run_options.image_route_verified
                        and str(plan.run_options.image_method or "").strip().lower()
                        not in {"", "none", "disabled", "prompt-queue"}
                    ),
                    "image_method": plan.run_options.image_method
                    or plan.run_options.image_provider,
                    "prefer_external_infographic_when_learning_value_exists": True,
                    "simple_svg_is_not_default": True,
                },
            }
        )
    return jobs


def student_topic_title(topic: Topic | None, index: int, language: str) -> str:
    if topic is None:
        return f"Topic {index}"
    if language == "zh-CN":
        return zh_teachable_topic_title(topic.title, index)
    return topic.title


def concept_task_text(language: str) -> str:
    if language == "zh-CN":
        return (
            "写 2-3 条学生可直接阅读的中文概念解释。只围绕 topic_title 和 source_points；"
            "说明这个概念是什么、描述什么关系或边界、为什么是本节核心。"
            "不要写做题动作清单，不要写“会识别/会操作/会检查”，不要引入相邻章节。"
        )
    return (
        "Write 2-3 student-facing concept explanation bullets. Stay inside "
        "topic_title and source_points; explain what the concept is, what "
        "relationship or boundary it describes, and why it is central. Do not "
        "write a procedural checklist or import adjacent topics. Use print-ready "
        "math/science notation: b², t³, x<sup>−1/2</sup>, √(...), ≤, ≥, ≠, θ, μ; "
        "do not leave b^2, t^3, x^(-1/2), sqrt(...), <=, >=, or != in student-facing text."
    )


def concept_jobs_markdown(jobs: list[dict[str, object]]) -> str:
    lines = [
        "# Concept Explanation Jobs",
        "",
        "These jobs are for the LLM concept-writing pass before final delivery.",
        "",
    ]
    for job in jobs:
        lines.extend(
            [
                f"## {job['id']} - {job['student_title']}",
                "",
                f"- Topic: {job['topic_title']}",
                f"- Subject pack: {job.get('subject_pack', 'generic')}",
                f"- Task: {job['task']}",
                "- Source points:",
            ]
        )
        source_points = job.get("source_points", [])
        if isinstance(source_points, list):
            for point in source_points:
                lines.append(f"  - {point}")
        lines.append("")
    return "\n".join(lines)


def write_concept_jobs(plan: GuidePlan, output_dir: Path) -> list[dict[str, object]]:
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    jobs = build_concept_jobs(plan)
    (concepts_dir / "concept_jobs.json").write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (concepts_dir / "concept_jobs.md").write_text(
        concept_jobs_markdown(jobs),
        encoding="utf-8",
    )
    return jobs


def reviewed_concept_titles(output_dir: Path) -> set[str]:
    path = output_dir / "concepts" / CONCEPT_REVIEW_FILE
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    if isinstance(data, dict):
        entries = data.get("concept_explanations") or data.get("concepts") or data
    else:
        entries = data
    titles: set[str] = set()
    if isinstance(entries, dict):
        titles.update(str(title) for title in entries)
        return titles
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("topic_title"):
                titles.add(str(entry["topic_title"]))
    return titles


def build_concept_writing_prompt(
    jobs: list[dict[str, object]],
    style: str,
    term_support_language: str,
    image_method: str,
    external_visual_capability: str | None = None,
    image_route_verified: bool = False,
) -> str:
    """
    Build detailed prompt for LLM Writer to write concept explanations for all topics.

    This is Phase 2 of the three-phase workflow. The LLM must:
    1. Read the concept job list (from Analyst's outline)
    2. Write original teaching content for each topic
    3. Judge visual needs case-by-case
    4. Extract glossary terms if term support language is requested
    """
    jobs_payload = json.dumps(jobs, ensure_ascii=False, indent=2)

    style_descriptions = {
        "formal": "Academic and precise, like a university textbook",
        "friendly": "Conversational and encouraging, like a helpful tutor",
        "story": "Narrative-driven with story framing and characters",
        "detective": "Mystery-solving approach, building understanding through investigation",
        "adventure": "Exploration and discovery metaphors",
        "life": "Real-world scenarios and everyday applications",
    }
    style_desc = style_descriptions.get(style, "Clear and student-appropriate")

    method = (image_method or "").strip()
    external_route_available = (
        str(external_visual_capability or "").strip().lower() == "yes"
        and bool(image_route_verified)
        and method.lower() not in {"", "none", "disabled", "prompt-queue"}
    )

    image_guidance = ""
    if external_route_available:
        image_guidance = (
            f"A verified external image route is available: {method}. When a topic gains learning value from "
            "apparatus, process detail, realistic context, modelling, or rich annotation, prefer external-infographic "
            "and write a topic-specific visual_guidance object. Do not silently downgrade that need to simple SVG. "
            "Use exact-svg or Kroki only when exact geometry, notation, scale, or machine-readable structure is the "
            "teaching claim and record the external-route exclusion reason."
        )
    elif method == "prompt-queue":
        image_guidance = (
            "You are specifying what visuals are needed. Python records non-text visual specs as pending jobs for review/import.\n"
            "Every topic still needs visual_decision; only exact-fit SVG specs may use svg-basic, and all other non-text visual specs become external infographic jobs."
        )
    elif method == "custom":
        image_guidance = (
            "A custom image method is recorded but has not been verified as callable for this run. Keep complex visual specs explicit and pending until verification.\n"
            "Every topic still needs visual_decision; do not claim a verified external route or silently downgrade a useful visual to simple SVG."
        )
    elif method and method not in {"none", "disabled"}:
        image_guidance = (
            f"An image method is recorded ({method}) but is not verified as callable for this run. Keep complex visual "
            "specs pending, write topic-specific visual_guidance, and do not claim a verified external route or silently "
            "downgrade a useful visual to simple SVG."
        )
    else:
        image_guidance = (
            "No external image generation route is verified. Still record visual_decision and visual_guidance for every "
            "topic; use text-ok only with a concrete reason, or specify an exact SVG/Kroki route when exact structure "
            "is the teaching claim."
        )

    glossary_guidance = ""
    if term_support_language != "en":
        glossary_guidance = (
            f"\nYou MUST also extract 30-50 professional terms and translate to {term_support_language}.\n"
            "These go in the glossary_entries[] array at the end of your JSON output.\n"
            "Choose high-frequency technical vocabulary from the exam_points across all topics."
        )

    return "\n".join(
        [
            "=" * 80,
            "PHASE 2: HANDBOOK WRITER",
            "=" * 80,
            "",
            "You are the handbook_writer. Your task is to write original teaching content for",
            "each topic in the revision handbook.",
            "",
            "IMPORTANT: You are writing for students, not copying from the syllabus.",
            "The Analyst already identified topics and exam points. Now you explain them clearly.",
            "",
            "INPUT:",
            "The following JSON contains concept_jobs.json (generated from the Analyst's outline).",
            "Each job has:",
            "- topic_title: the teaching topic",
            "- exam_points: specific learning outcomes",
            "- source_snippets: page references from the official syllabus",
            "",
            f"WRITING STYLE: {style} — {style_desc}",
            f"TERM SUPPORT: {term_support_language} {'(glossary required)' if term_support_language != 'en' else '(no glossary)'}",
            f"IMAGE METHOD: {image_method}",
            "",
            "YOUR TASK:",
            "",
            "For EACH topic in concept_jobs.json:",
            "",
            "1. Write 'essence' (one sentence, 15-25 words)",
            "   - Capture the core idea in one clear sentence",
            "   - Example: 'The source evidence shows which conditions, relationships, or limits the student must explain for this topic.'",
            "",
            "2. Write 'analogy' (student-friendly comparison)",
            "   - Compare to something familiar",
            "   - Example: 'A source point is like a map pin: it keeps your explanation attached to the exact place the course wants you to understand.'",
            f"   - Use {style} voice",
            "",
            "3. Write 'concepts' (2-3 paragraphs)",
            "   - Explain the topic clearly",
            "   - Cover all exam_points",
            "   - Do NOT just copy source_snippets",
            "   - Write original teaching language",
            f"   - Use {style} voice",
            "   - Each paragraph: 3-5 sentences",
            "",
            "4. Write 'worked_examples' (1-2 examples)",
            "   - Problem statement (realistic scenario)",
            "   - Full solution with step-by-step reasoning",
            "   - Check questions (how to verify the answer)",
            "   - Example:",
            "     {",
            '       "problem": "A question gives a new case that tests this source point. Explain which condition applies and why.",',
            '       "solution": "Step 1: Identify the relevant source condition. Step 2: Apply it to the case evidence. Step 3: State the exam-ready conclusion.",',
            '       "check": "Verify that each step uses a source point and does not import an unsupported topic."',
            "     }",
            "",
            "5. Write 'mastery_summary' (what students should be able to do)",
            "   - Example: 'You can explain the source-bound relationship, apply it to a short exam case, and check that your answer stays inside the syllabus point.'",
            "   - For maths, physics, chemistry, statistics, and similar subjects, use stable student-facing symbols such as ², ³, √, ≤, ≥, ≠, θ, and μ instead of plain-text fallbacks such as ^2, sqrt(), <=, or >=.",
            "",
            "6. RECORD VISUAL_DECISION AFTER WRITING EACH TOPIC",
            "   - First finish the source-bound explanation, worked example, solution, pitfall, and mastery_summary.",
            "   - Then ask whether a visual materially improves this completed topic for a teenager trying to learn it.",
            "   - Always output visual_decision, for every subject and every topic.",
            '   - If NO: set recommended_route: "text-ok" and include no_visual_reason explaining why a separate visual would not add learning value.',
            '   - If YES and labels/geometry fully carry the meaning: set recommended_route: "exact-svg" and include visual_spec with complexity: "svg-basic" and svg_fit: "exact".',
            '   - If YES and the need is a professional formal diagram: set recommended_route: "kroki-diagram" and include visual_spec for a reviewed Kroki route.',
            '   - If YES and the need requires realism, rich annotation, apparatus, scenes, or modelling nuance: set recommended_route: "external-infographic" and include visual_spec for a reviewed image asset route.',
            "   - Always include visual_guidance as a separate object for the same topic.",
            "   - text-ok visual_guidance: visual_kind='none' and no_visual_rationale matching no_visual_reason.",
            "   - Non-text visual_guidance: visual_kind, composition, reading_order, required_elements, and student_inference.",
            "   - exact-svg/Kroki visual_guidance: also state exactness_exception; if an external route is verified, state external_route_exclusion_reason.",
            "   - exact-svg example:",
            "     {",
            '       "visual_decision": {',
            '         "recommended_route": "exact-svg",',
            '         "learning_claim": "A simple branching structure carries the repeated-choice calculation more clearly than text alone.",',
            '         "visual_teaching_value": "Students can follow each branch and see where values combine."',
            "       },",
            '       "visual_guidance": {',
            '         "visual_kind": "decision tree",',
            '         "composition": "A left-to-right branching structure with the source-bound conditions labelled.",',
            '         "reading_order": "Read the root condition, then follow each branch to the resulting case.",',
            '         "required_elements": ["root condition", "branch labels", "end states"],',
            '         "student_inference": "The branch selected by the condition determines the correct case outcome.",',
            '         "exactness_exception": "Branch labels and order are the exact teaching claim."',
            "       },",
            '       "visual_spec": {',
            '         "type": "branching decision tree",',
            '         "complexity": "svg-basic",',
            '         "svg_fit": "exact",',
            '         "prompt": "Create a clean labelled branching diagram from the source-bound conditions in this topic.",',
            '         "llm_visual_approved": true,',
            '         "trigger": "The relationship is exactly represented by branches and labels."',
            "       }",
            "     }",
            "   - text-ok example:",
            "     {",
            '       "visual_decision": {',
            '         "recommended_route": "text-ok",',
            '         "no_visual_reason": "The topic is best learned through the worked example and source anchor; a separate image would repeat the same short relationship.",',
            '         "learning_claim": "The explanation already gives the needed sequence and check."',
            "       },",
            '       "visual_guidance": {',
            '         "visual_kind": "none",',
            '         "no_visual_rationale": "The topic is best learned through the worked example and source anchor; a separate image would repeat the same short relationship."',
            "       }",
            "     }",
            "",
            image_guidance,
            glossary_guidance,
            "",
            "OUTPUT JSON SCHEMA:",
            "{",
            '  "schema_version": "v0.5-concept-explanations",',
            '  "concepts": [',
            "    {",
            '      "topic_title": "Topic title from concept_jobs.json",',
            '      "essence": "One source-bound sentence naming the core relationship...",',
            '      "analogy": "A student-friendly comparison that fits this exact topic...",',
            '      "concepts": [',
            '        "Paragraph 1: Explain what the source point means...",',
            '        "Paragraph 2: Explain the relationship, boundary, or condition...",',
            '        "Paragraph 3: Explain how a student uses it in an exam answer..."',
            "      ],",
            '      "worked_examples": [',
            "        {",
            '          "problem": "A short original case that tests this topic...",',
            '          "solution": "Step 1... Step 2...",',
            '          "check": "Verify the answer against the source point..."',
            "        }",
            "      ],",
            '      "mastery_summary": "You can explain the source-bound relationship, apply it, and check your answer stays inside the syllabus point.",',
            '      "visual_decision": {',
            '        "recommended_route": "text-ok",',
            '        "no_visual_reason": "The worked example is clearer than a repeated image for this topic."',
            "      },",
            '      "visual_guidance": {',
            '        "visual_kind": "none",',
            '        "no_visual_rationale": "The worked example is clearer than a repeated image for this topic."',
            "      },",
            '      "visual_spec": { ... } // ONLY for exact-svg, kroki-diagram, or external-infographic routes',
            "    }",
            "  ],",
            '  "glossary_entries": [ // ONLY if term_support_language != "en"',
            "    {",
            '      "term_english": "Source document",',
            f'      "term_target": "原始凭证", // translation to {term_support_language}',
            f'      "target_language": "{term_support_language}"',
            "    }",
            "  ]",
            "}",
            "",
            "CRITICAL RULES:",
            "",
            "1. Write in ORIGINAL teaching language.",
            "   Do NOT copy/paste from source_snippets or syllabus text.",
            "",
            f"2. Use {style} voice consistently.",
            "   Formal = academic precision. Friendly = conversational encouragement.",
            "",
            "3. Do NOT output visual_decision or visual_spec before writing the topic content.",
            "   Visual choice comes after the explanation and worked example exist.",
            "   Only add visual_spec when a diagram/chart/infographic genuinely helps understanding.",
            "",
            "4. Visual judgment is YOUR responsibility for every topic and every subject.",
            "   Think: 'Would a diagram or richer image make this clearer for a student, or is text genuinely sufficient?'",
            "   If text is sufficient, visual_decision must still record recommended_route='text-ok', no_visual_reason, and matching visual_guidance.",
            "",
            "5. Worked examples must be COMPLETE.",
            "   Problem + full solution + check. Not just 'solve this problem'.",
            "",
            "6. Glossary terms (if required): 30-50 professional vocabulary terms.",
            "   Not every word. High-frequency technical terms only.",
            "",
            "7. Do NOT write Module 1 (cover), Module 2 (how to use), Module 6 (practice cards).",
            "   You are writing Module 5 (topic guides) content only.",
            "   Python will render the full 8-module framework.",
            "",
            "AFTER YOU OUTPUT THIS JSON:",
            "- Python will validate your JSON schema and import content to guide-plan.json",
            "- Python may render HTML after Analyst and Writer artifacts exist; it must not generate PDF before LLM HTML approval",
            "- Writer must make an independent visual_decision and visual_guidance record for every final topic; text-ok is a reasoned exception, not a default",
            "- external-infographic may be a source-bound explanatory visual or realistic/reference/example image, not only a formal diagram",
            "- visual labels, callouts, legends, captions, and short annotations are allowed when accurate, legible, and source-bound; the Skill does not require text-free images",
            "- Python validates that every topic records visual_decision and visual_guidance; text-ok decisions need a concrete matching rationale",
            "- If you specified visual_spec, Python records pending visual entries; the host LLM must generate or import exact SVG/Kroki/infographic assets and review them before final delivery",
            "- Mechanical checks are diagnostics only; the LLM Reviewer must personally open the rendered HTML, repair and rerender until it passes, then approve that exact HTML hash before PDF export",
            "",
            "MEMORY & CONSISTENCY:",
            f"- Writing style: {style} ({style_desc})",
            f"- Term support: {term_support_language}",
            f"- Image method: {image_method}",
            "- Keep terminology, voice, worked-example depth, and visual judgment consistent across all topics.",
            "- If you notice a previous topic uses a different pattern, flag it in your completion summary.",
            "",
            "ERROR HANDLING:",
            "- If a job has missing source_points, flag: 'Topic [X] has no source_points; Analyst should re-check evidence.'",
            "- If a topic is ambiguous, write the safest source-bound explanation and mark it for subject-specialist review.",
            "- If the topic list is very long, keep output complete; suggest splitting only in your summary, not by omitting topics.",
            "- If visual evidence is insufficient, choose visual_decision text-ok with no_visual_reason instead of inventing a diagram.",
            "",
            "DELIVERY CHECKLIST:",
            "- Every concept_jobs.json topic is covered exactly once",
            f"- Style remains consistently {style}",
            "- Each worked example has problem, solution, and check",
            "- Every topic has visual_decision and visual_guidance; visual_spec appears only where it materially improves understanding",
            f"- Glossary contains 30-50 terms if {term_support_language} is not en",
            "- No placeholder text such as '[insert explanation here]' remains",
            "",
            "HANDOFF NOTE:",
            '"Content complete for [X] topics. [Y] non-text visual specs created; [Z] text-ok decisions include no_visual_reason. Ready for rendered handbook review."',
            "",
            "=" * 80,
            "CONCEPT JOBS (write content for each):",
            "=" * 80,
            "",
            jobs_payload,
        ]
    )
