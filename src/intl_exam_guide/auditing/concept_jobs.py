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
                "contract_version": "v0.4-pedagogy-mvp",
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
        "write a procedural checklist or import adjacent topics."
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

    image_guidance = ""
    if image_method == "prompt-queue":
        image_guidance = (
            "You are specifying what visuals are needed. Python records your visual specs as pending jobs for review/import.\n"
            "Only exact-fit SVG specs may use svg-basic; all other visual specs become external infographic jobs."
        )
    elif image_method == "custom":
        image_guidance = (
            "You are specifying what visuals are needed. Python will call the user's custom API.\n"
            "Be specific in your visual prompts."
        )
    else:
        image_guidance = (
            "No image generation configured. Only specify visuals if absolutely critical."
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
            "   - Example: 'Source documents provide the evidence needed to record transactions in books of prime entry before posting to ledgers.'",
            "",
            "2. Write 'analogy' (student-friendly comparison)",
            "   - Compare to something familiar",
            "   - Example: 'Source documents are like receipts you collect when shopping—they prove a transaction happened before you write it in your budget notebook.'",
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
            '       "problem": "A business receives an invoice for £500 of supplies on credit. Record this transaction.",',
            '       "solution": "Step 1: Identify the source document (invoice). Step 2: Record in purchases day book...",',
            '       "check": "Verify that the purchases account debit equals the trade payables credit."',
            "     }",
            "",
            "5. Write 'mastery_summary' (what students should be able to do)",
            "   - Example: 'You can identify source documents, prepare correct prime entry records, and post to ledger accounts.'",
            "",
            "6. JUDGE VISUAL NEEDS (case-by-case)",
            "   - Question: Does this topic benefit from a diagram/infographic/chart?",
            "   - If NO: do not output visual_spec.",
            "   - If YES, first decide whether a simple SVG can fully and precisely express the teaching idea.",
            '   - Use complexity: "svg-basic" ONLY when the SVG is an exact-fit diagram: axes, set regions, simple flow, table, tree, timeline, or another structure where labels and geometry fully carry the concept.',
            '   - For any visual that needs nuance, realistic setup, multiple linked states, spatial interpretation, rich annotation, or could become misleading as simple shapes, use complexity: "infographic" so it goes to the external infographic model.',
            "   - SVG exact-fit example:",
            "     {",
            '       "visual_spec": {',
            '         "type": "probability tree for independent Bernoulli trials",',
            '         "complexity": "svg-basic",',
            '         "svg_fit": "exact",',
            '         "prompt": "Create a clean probability tree with success p and failure 1-p for repeated independent trials.",',
            '         "llm_visual_approved": true,',
            '         "trigger": "A tree structure exactly represents the branching probability calculation."',
            "       }",
            "     }",
            "   - External infographic example:",
            "     {",
            '       "visual_spec": {',
            '         "type": "connected-particle forces explanation",',
            '         "complexity": "infographic",',
            '         "prompt": "Create a polished teaching infographic explaining the modelling steps, force diagram, assumptions, and F=ma equations for connected particles.",',
            '         "llm_visual_approved": true,',
            '         "trigger": "The topic needs modelling assumptions and linked equations that a simple SVG could oversimplify."',
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
            '      "topic_title": "3.1.8 Prepare accounting records from source documents",',
            '      "essence": "Source documents provide the evidence needed to record transactions...",',
            '      "analogy": "Source documents are like receipts you collect when shopping...",',
            '      "concepts": [',
            '        "Paragraph 1: Source documents are the original records...",',
            '        "Paragraph 2: Books of prime entry organize transactions...",',
            '        "Paragraph 3: Ledger accounts provide the final classification..."',
            "      ],",
            '      "worked_examples": [',
            "        {",
            '          "problem": "A business receives an invoice...",',
            '          "solution": "Step 1... Step 2...",',
            '          "check": "Verify that..."',
            "        }",
            "      ],",
            '      "mastery_summary": "You can identify source documents, prepare correct prime entry records, and post to ledger accounts.",',
            '      "visual_spec": { ... } // ONLY if this topic needs a visual',
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
            "3. Do NOT output visual_spec for every topic.",
            "   Only when a diagram/chart/infographic genuinely helps understanding.",
            "",
            "4. Visual judgment is YOUR responsibility.",
            "   Think: 'Would a diagram make this clearer, or is text sufficient?'",
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
            "- Python will validate your JSON schema",
            "- Coordinator will check that every concept job has a matching topic entry",
            "- Python will import content to sections/ directory",
            "- Python will render guide.html and guide.pdf",
            "- If you specified visual_spec, Python imports it into guide-plan.json and writes pending entries to images/infographic_jobs.md",
            "- Coordinator will then dispatch Quality Inspector before the independent Final Reviewer",
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
            "- If visual evidence is insufficient, leave visual_spec out instead of inventing a diagram.",
            "",
            "DELIVERY CHECKLIST:",
            "- Every concept_jobs.json topic is covered exactly once",
            f"- Style remains consistently {style}",
            "- Each worked example has problem, solution, and check",
            "- Visual specs appear only where they materially improve understanding",
            f"- Glossary contains 30-50 terms if {term_support_language} is not en",
            "- No placeholder text such as '[insert explanation here]' remains",
            "",
            "HANDOFF NOTE TO COORDINATOR:",
            '"Content complete for [X] topics. [Y] visual specs created. Ready for Quality Inspector to check format and completeness."',
            "",
            "=" * 80,
            "CONCEPT JOBS (write content for each):",
            "=" * 80,
            "",
            jobs_payload,
        ]
    )
