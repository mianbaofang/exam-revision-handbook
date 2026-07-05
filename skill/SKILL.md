---
name: igcse-a-level-revision-guide
description: Framework for generating International GCSE and A-Level revision handbooks. Provides presentation templates, workflow guidance, and rendering engine. You fill the content.
---

# IGCSE & A-Level Revision Handbook Skill

## What This Is

**This is a presentation framework and workflow guide, not a content generator.**

You (the LLM agent) are responsible for all content understanding, judgment, creation, and review. This Skill provides:

1. **Visual System** - Three exam board themes (AQA / Edexcel / Cambridge) with brand colors, cover layouts, and logo placement
2. **HTML/PDF Framework** - 8 module templates with print-friendly layout rules
3. **Workflow Guide** - Step-by-step instructions for five coordinated roles: Project Manager → Analyst → Writer → Quality Inspector → Reviewer
4. **Artifact Contracts** - JSON schemas for your outputs (handbook-project-manager.json, syllabus-outline.json, concept_explanations.json, quality-inspection.json, final-review-packet.json)
5. **Python Execution Engine** - No intelligence. Downloads PDFs, extracts text, receives your JSON, renders HTML, exports PDF

**Python does not decide topics, exam points, or visual needs. You do.**

**This Skill does not include a fixed built-in image-generation router.** Visual judgment is your responsibility in Phase 2 (Writer).

---

## What This Skill Provides

### 1. Three Exam Board Visual Themes

Each board has a distinct visual identity applied to covers, headers, and PDF styling:

**AQA (Oxford International AQA)**
- Primary color: `#0066cc` (deep blue)
- Cover layout: Centered title, board logo top-right
- Typography: Clean sans-serif, high contrast

**Edexcel (Pearson Edexcel International)**
- Primary color: `#ff6600` (orange)
- Cover layout: Bold title bar, board logo header
- Typography: Modern sans-serif, dynamic spacing

**Cambridge (Cambridge International / CAIE)**
- Primary color: `#009639` (green)
- Cover layout: Traditional academic, crest placement
- Typography: Serif headings, formal structure

### 2. Handbook Framework (8 Modules)

Every handbook follows this structure:

**Module 1: Cover**
- Exam board branding
- `{Board} {Level} {Subject} Revision Handbook`
- Selected exam year (when applicable)

**Module 2: How to Use This Handbook**
- Study approach guidance
- Module overview
- Revision stage recommendations

**Module 3: Study Roadmap / Topic Map**
- Visual topic tree or structured table
- Shows all topics with exam point counts
- Level tags (foundation/extended, AS/A2)

**Module 4: Term Glossary** (when requested)
- Professional terms in target language ↔ English
- 30-50 high-frequency terms from exam points
- Alphabetically sorted

**Module 5: Topic Guides** (core content)
- For each topic:
  - Essence (one-sentence core idea)
  - Analogy (student-friendly comparison)
  - Concepts (2-3 paragraphs of explanation)
  - Worked Examples (problems + solutions + checks)
  - Visuals (when you judge they're needed)

**Module 6: Practice Workbook**
- Practice cards for each topic
- Problem + solution + self-check questions
- Grid layout for quick reference

**Module 7: Exam Structure**
- Assessment papers table (duration, marks, weighting)
- Command words (if available from specification)
- Assessment objectives (if available)

**Module 8: Revision Checklist**
- Stage-by-stage review plan
- Topic mastery checkboxes
- Suggested timeline (6 weeks, 3 weeks, 1 week before exam)

**PDF Layout Rules**:
- A4 portrait pages
- Page breaks: before each topic, before practice workbook
- Images: max 600px width, centered with captions
- Print-friendly: no background colors, high contrast text

### 3. Your Workflow (Five Coordinated Roles)

See detailed instructions in the "Your Workflow" section below.

### 4. Artifact Contracts (JSON Schemas)

Python validates your outputs against these schemas. If validation fails, you'll receive error details to fix.

**handbook-project-manager.json** - Python writes this for the Coordinator role
**syllabus-evidence.json** - Python writes this (you read it)
**syllabus-outline.json** - Analyst writes this in Phase 1
**qualification.json** - Python writes this from the Analyst outline
**concept_jobs.json** - Python writes this (Writer task list)
**concept_explanations.json** - Writer writes this in Phase 2
**quality-inspection.json** - Quality Inspector writes/checks this in Phase 3
**final-review-packet.json** - Reviewer writes/checks this in Phase 4
**agent-orchestration.json** - Python tracks role completion

### 5. Python Execution Engine (No Intelligence)

Python performs only mechanical tasks:
- Downloads specification PDFs from official URLs
- Extracts page text and saves as `syllabus-evidence.json`
- Receives your JSON outputs
- Validates JSON schemas
- Renders HTML using the 8-module framework
- Exports PDF via headless browser
- Manages artifact files

Python **does not**:
- ❌ Decide topic boundaries
- ❌ Extract exam points
- ❌ Determine if a topic needs a visual
- ❌ Write concept explanations
- ❌ Judge content quality

**You do all of that.**

---

## Your Workflow

### Preflight: Collect Parameters

Before starting, confirm these with the user:

**Required**:
1. **Exam board**: AQA / Edexcel / Cambridge
2. **Level**: International GCSE / International AS / International A-Level
3. **Subject**: Chemistry, Mathematics, Economics, etc.
4. **Code** (if known): e.g., 9260, 9EB0, 0455

**Optional**:
5. **Exam year**: When the official page lists multiple syllabus versions (e.g., 2025-2027 vs 2027-2029)
6. **Term support language**: `en` (no glossary) or `zh-CN`, `zh-TW`, `ja` for bilingual term glossary
7. **Explanation style**: `formal`, `friendly`, `story`, `detective`, `adventure`, `life` (applies to Module 5 concept writing)
8. **Image generation method**:
   - `prompt-queue`: You list visual needs, user generates/imports them later
   - `custom`: User has configured an external API (you won't call it, Python will)

**Example preflight dialogue**:
```
You: I'll help you generate a revision handbook. Let me confirm:
- Exam board: AQA
- Level: International GCSE
- Subject: Chemistry
- Term support: Chinese (zh-CN) glossary
- Style: Friendly explanations
- Visuals: prompt-queue (I'll list what's needed, you provide them)

Proceed?
```

---

### Coordinator: Handbook Project Manager

**Your role**: `handbook_project_manager`

Before dispatching specialist work, create or update `handbook-project-manager.json`:
- Confirm preflight inputs and missing fields
- Dispatch roles in order: Analyst → Writer → Quality Inspector → Final Reviewer
- Validate each role's output before the next handoff
- Send failed artifacts back to the responsible role with exact issues
- Keep the package labeled `draft`, `review-ready`, or `blocked` until all gates pass

---

### Phase 1: Analyst — Understand the Official Syllabus

**Your role**: `syllabus_outline_analyst`

**Input**: `syllabus-evidence.json` (Python has already downloaded the specification PDF and extracted page text)

**Your task**:
1. Read `syllabus-evidence.json` carefully. It contains:
   - `course.title`, `course.code`, `course.qualification_type`
   - `pages[]`: array of `{ page: number, text: string }` from the official PDF
   - `specification_url`, `page_url`

2. **Identify topic boundaries**:
   - Real teaching units like "3.1.8 Prepare accounting records from source documents"
   - NOT placeholder headings like "Content 1.1" or "Unit A"
   - Use page numbers, headings, table structures, bullet points to judge boundaries

3. **Extract exam points for each topic**:
   - Specific learning outcomes like "Use source documents, books of prime entry and ledger accounts"
   - NOT vague statements like "Students should understand the content"

4. **Record source snippets**:
   - For each topic, save 1-3 short text snippets from the PDF showing where you found this topic/point
   - Include page numbers

5. **Output JSON**: `syllabus-outline.json`

**Detailed Prompt Template**:

```
You are the syllabus_outline_analyst. Your task is to read the official specification PDF evidence and produce an authoritative topic outline.

Input file: syllabus-evidence.json

Instructions:
1. Read all pages in the evidence file
2. Identify real teaching topics (not placeholder headings)
3. For each topic:
   - Write a clear topic title (e.g., "3.1.8 Prepare accounting records from source documents")
   - Extract specific exam points (learning outcomes)
   - Record level_tags if the syllabus distinguishes foundation/extended or AS/A2
   - Save 1-3 source_snippets with page numbers showing where you found this

Output JSON schema:
{
  "schema_version": "v0.5-llm-syllabus-outline",
  "status": "llm-analyst-approved",
  "course_spec": {
    "title": "...",
    "code": "...",
    "qualification_type": "...",
    "subject_area": "...",
    "provider": "...",
    "page_url": "...",
    "specification_url": "..."
  },
  "topics": [
    {
      "title": "3.1.8 Prepare accounting records from source documents",
      "exam_points": [
        "Use source documents",
        "Prepare books of prime entry",
        "Prepare ledger accounts"
      ],
      "level_tags": ["foundation", "extended"],
      "source_snippets": [
        {
          "page": 12,
          "text": "Students should be able to use source documents...",
          "matched_term": "source documents"
        }
      ]
    }
  ]
}

Critical rules:
- Do NOT rely on any *-candidate-hints.json files. Those are optional suggestions only.
- Do NOT accept "Content 1.1" as a teaching topic. Find the real topic name.
- Do NOT output exam_points like "Understand the topic". Be specific.
- Each topic must have at least one exam_point and one source_snippet.

After you output this JSON, call the Python function to import it:
- Python will validate your JSON
- Python will write qualification.json and concept_jobs.json
- You can then proceed to Phase 2
```

**What happens after you output**:
- Python receives your `syllabus-outline.json`
- Python validates the schema
- Python writes `qualification.json` (authoritative topics)
- Python generates `concept_jobs.json` (your writing task list)
- You can now start Phase 2

---

### Phase 2: Writer — Fill the Content Modules

**Your role**: `handbook_writer`

**Input**: `concepts/concept_jobs.json` (Python generated this from your Analyst outline)

**Your task**:
1. Read `concept_jobs.json`. It lists all topics you need to write, like:
   ```json
   {
     "jobs": [
       {
         "topic_title": "3.1.8 Prepare accounting records from source documents",
         "exam_points": ["Use source documents", "..."],
         "source_snippets": [...]
       }
     ]
   }
   ```

2. **For each topic, write**:
   - `essence`: One-sentence core idea (15-25 words)
   - `analogy`: Student-friendly comparison to familiar concepts
   - `concepts`: 2-3 paragraphs explaining the topic in the requested style (friendly/formal/story/etc.)
   - `worked_examples`: 1-2 problems with full solutions and self-check questions
   - `mastery_summary`: What a student should be able to do after mastering this topic

3. **Judge visual needs**:
   - Does this topic benefit from a diagram/infographic/chart?
   - If no, omit `visual_spec`.
   - If yes, decide whether an exact SVG can fully and precisely express the concept.
   - Use `complexity: "svg-basic"` only for exact-fit visuals such as axes, set regions, simple flow, table, tree, timeline, or another structure where labels and geometry fully carry the teaching meaning. Include `svg_fit: "exact"`.
   - For any visual requiring nuance, realistic setup, multiple linked states, spatial interpretation, rich annotation, or modelling assumptions, use `complexity: "infographic"` for the external infographic model.

4. **If term glossary is requested** (user chose zh-CN, zh-TW, ja):
   - Extract 30-50 high-frequency professional terms from all exam_points
   - Translate to target language
   - Output `glossary_entries[]`

5. **Output JSON**: `concepts/concept_explanations.json`

**Detailed Prompt Template**:

```
You are the handbook_writer. Your task is to write original teaching content for each topic.

Input file: concepts/concept_jobs.json
Style: {user_selected_style} (friendly / formal / story / detective / adventure / life)
Term support: {user_selected_language} (en / zh-CN / zh-TW / ja)

For each topic in concept_jobs.json:

1. Write essence (one sentence, 15-25 words, captures the core idea)
2. Write analogy (compare to something familiar to students)
3. Write concepts (2-3 paragraphs):
   - Explain the topic clearly in {style} voice
   - Reference the exam_points
   - Do NOT just copy/paste from source_snippets
   - Use original teaching language
4. Write worked_examples (1-2 examples):
   - Problem statement
   - Full solution with steps
   - Check questions (how to verify your answer)
5. Write mastery_summary (what students should be able to do)

Judge visual needs:
- Does this topic benefit from a diagram/infographic/chart?
- If NO: do not output visual_spec.
- If YES, first decide whether SVG is an exact fit.
- SVG exact fit: axes, set regions, simple flow, table, tree, timeline, or another structure where labels and geometry fully carry the concept.
- Any visual that needs nuance, realistic setup, multiple linked states, spatial interpretation, rich annotation, or modelling assumptions must be an external infographic.
- SVG exact-fit example:
  {
    "visual_spec": {
      "type": "probability tree for independent Bernoulli trials",
      "complexity": "svg-basic",
      "svg_fit": "exact",
      "prompt": "Create a clean probability tree with success p and failure 1-p for repeated independent trials.",
      "llm_visual_approved": true,
      "trigger": "A tree structure exactly represents the branching probability calculation."
    }
  }
- External infographic example:
  {
    "visual_spec": {
      "type": "connected-particle forces explanation",
      "complexity": "infographic",
      "prompt": "Create a polished teaching infographic explaining the modelling steps, force diagram, assumptions, and F=ma equations for connected particles.",
      "llm_visual_approved": true,
      "trigger": "The topic needs modelling assumptions and linked equations that an exact SVG could oversimplify."
    }
  }

Output JSON schema:
{
  "schema_version": "v0.5-concept-explanations",
  "concepts": [
    {
      "topic_title": "3.1.8 Prepare accounting records from source documents",
      "essence": "Source documents provide the evidence needed to record transactions in books of prime entry before posting to ledgers.",
      "analogy": "Source documents are like receipts you collect when shopping—they prove a transaction happened before you write it in your budget notebook.",
      "concepts": [
        "Paragraph 1...",
        "Paragraph 2...",
        "Paragraph 3..."
      ],
      "worked_examples": [
        {
          "problem": "A business receives an invoice...",
          "solution": "Step 1... Step 2...",
          "check": "Verify that..."
        }
      ],
      "mastery_summary": "You can identify source documents, prepare correct prime entry records, and post to ledger accounts.",
      "visual_spec": { ... } // optional, only if this topic needs a visual
    }
  ],
  "glossary_entries": [ // only if term_support_language != "en"
    {
      "term_english": "Source document",
      "term_target": "原始凭证",
      "target_language": "zh-CN"
    }
  ]
}

Critical rules:
- Write in {style} voice (friendly = conversational, formal = academic, story = narrative framing, etc.)
- Do NOT output visual_spec for every topic. Only when truly beneficial.
- SVG visuals require `svg_fit: "exact"`; otherwise choose `complexity: "infographic"`.
- External infographic specs are written to `images/infographic_jobs.md` and must be generated/imported before final-ready delivery.
- Glossary entries: 30-50 terms, high-frequency professional vocabulary only.

After you output this JSON, call the Python function to import it:
- Python will validate your JSON
- Python will render HTML using the 8-module framework with AQA/Edexcel/Cambridge theme
- Python will generate guide.html and guide.pdf
- If you specified visual_spec, Python writes images/infographic_jobs.md
- You can then proceed to Phase 3 (Quality Inspector)
```

**What happens after you output**:
- Python receives your `concept_explanations.json`
- Python validates schema
- Python imports content to `sections/` directory
- Python renders `guide.html` and `guide.pdf` using the appropriate board theme
- If you specified visuals with `prompt-queue`, Python writes `images/infographic_jobs.md`
- Python generates `validation.json` with preliminary checks
- Python writes `quality-inspection.json` for the fast Inspector gate
- You can now start Phase 3 (Quality Inspector)

---

### Phase 3: Quality Inspector — Fast Completeness Gate

**Your role**: `quality_inspector`

**Input**:
- `guide.html`
- `qualification.json`
- `syllabus-outline.json`
- `concepts/concept_jobs.json`
- `concepts/concept_explanations.json`
- `images/visual_manifest.json`

**Your task**:
1. Check required files exist.
2. Check the visible handbook has cover, how-to-use, topic map, topic guides, practice, exam structure, and revision checklist markers.
3. Check topic count and concept explanation count match.
4. Flag visible placeholders such as `[insert ...]`, `undefined`, `null`, or `TODO`.
5. Check visual specs are explicit and not repeated five or more times.
6. Output or verify `quality-inspection.json` with `inspection_status: "pass" | "fail"`.

If inspection fails, send exact issues back to the Writer or renderer before Final Reviewer starts. If it passes, proceed to Phase 4.

---

### Phase 4: Reviewer — Independent Quality Audit

**Your role**: `final_reviewer` (independent subagent)

**Critical**: You are a **fresh, independent context**. You cannot see the conversation from Analyst, Writer, or Quality Inspector.

**Input**:
- `guide.html` (the rendered handbook)
- `syllabus-evidence.json` (original specification evidence)
- `validation.json` (preliminary automated checks)
- `quality-inspection.json` (fast structure/completeness report)
- `images/visual_manifest.json` (if visuals were generated)

**Your task**:
1. **Read the rendered handbook** (`guide.html`)
2. **Compare with original syllabus** (`syllabus-evidence.json`):
   - Are the topics accurate?
   - Are the exam points covered?
   - Are there claims that aren't supported by the specification?
3. **Check teaching quality**:
   - Are concept explanations clear?
   - Are worked examples appropriate?
   - Are analogies helpful or confusing?
   - Is the style consistent?
4. **Check visuals** (if any):
   - Do visual specs match the topic needs?
   - Are there missing visuals that should be there?
   - Are there unnecessary visuals?
5. **Check PDF rendering** (if available):
   - Are there blank pages?
   - Is the page count reasonable?
   - Are images rendering correctly?
6. **Check validation.json**:
   - Are there any errors or warnings?

7. **Output JSON**: `final-review-packet.json`

**Detailed Prompt Template**:

```
You are the final_reviewer, an independent subagent auditing the handbook.

IMPORTANT: You are NOT the analyst or writer. You did not create this content. You are reviewing it fresh.

Input files:
- guide.html (the rendered handbook)
- syllabus-evidence.json (original specification PDF evidence)
- validation.json (automated checks)

Your audit checklist:

1. syllabus_outline_compared:
   - Read guide.html Module 3 (Topic Map)
   - Read syllabus-evidence.json pages
   - Question: Does the outline match the official specification?
   - Output: { "status": "approved" | "repair_needed", "notes": "..." }

2. visible_handbook_inspected:
   - Read guide.html Module 5 (Topic Guides)
   - Question: Are concept explanations clear, analogies helpful, examples appropriate?
   - Look for:
     * Vague explanations
     * Confusing analogies
     * Worked examples with errors
     * Inconsistent style
   - Output: { "status": "approved" | "repair_needed", "issues": [...] }

3. visuals_inspected:
   - Read images/visual_manifest.json (if exists)
   - Read guide.html visual placements
   - Question: Are visuals appropriate and non-repetitive?
   - Look for:
     * Missing visuals where diagrams would help
     * Unnecessary visuals for text-only topics
     * Repetitive visual specs (e.g., 5 identical "process flowcharts")
   - Output: { "status": "approved" | "repair_needed", "issues": [...] }

4. pdf_pages_sampled:
   - If guide.pdf exists, check:
     * Blank pages
     * Broken image links
     * Page count (should be 15-60 pages for typical IGCSE subject)
   - Output: { "status": "approved" | "not_checked" | "repair_needed", "notes": "..." }

5. validation_issues_reviewed:
   - Read validation.json
   - Are there any severity="error" items?
   - Output: { "status": "clean" | "has_errors", "summary": "..." }

6. repair_loop_completed:
   - If you found issues in 1-5:
     * output "repair_needed" with detailed instructions
   - If all approved:
     * output "approved"

Output JSON schema:
{
  "schema_version": "v0.5-final-review",
  "syllabus_outline_compared": {
    "status": "approved",
    "notes": "Topic boundaries match the official spec page 12-35. All exam points covered."
  },
  "visible_handbook_inspected": {
    "status": "repair_needed",
    "issues": [
      "Topic 3.2 analogy compares journal entries to 'filing taxes' which may confuse international students. Suggest using 'recording daily expenses in a notebook'.",
      "Worked example 4.1 solution step 2 has calculation error: should be 125 not 120."
    ]
  },
  "visuals_inspected": {
    "status": "approved",
    "notes": "5 visual specs are all distinct and appropriate for their topics."
  },
  "pdf_pages_sampled": {
    "status": "approved",
    "notes": "PDF is 42 pages, no blank pages, all images render correctly."
  },
  "validation_issues_reviewed": {
    "status": "clean",
    "summary": "No errors. 2 warnings about pending concept imports (expected for prompt-queue workflow)."
  },
  "repair_loop_completed": {
    "status": "repair_needed",
    "instructions": "Fix the 2 issues in visible_handbook_inspected, then rerender guide.html and resubmit for review."
  }
}

After you output this JSON:
- If repair_needed: the handler will fix issues, rerender, and call you again
- If approved: Python marks delivery_status = "final-ready"
```

**What happens after you output**:
- Python receives your `final-review-packet.json`
- If you reported `repair_needed`:
  - Handler goes back to Phase 2 to fix issues
  - Python rerenders guide.html
  - You are called again (fresh review)
- If you reported all `approved`:
  - Python writes `agent-product-review.json` (handler's final inspection)
  - Python marks `delivery_status = "final-ready"`
  - Handbook is ready for user

---

## Delivery

When all five roles are complete and approved, you deliver:

**Files**:
- `handbook-project-manager.json` - Coordinator state and handoff log
- `guide.html` - Full handbook with all 8 modules
- `guide.pdf` - Print-friendly A4 PDF (if browser runtime available)
- `qualification.json` - Authoritative topics from your Analyst outline
- `syllabus-evidence.json` - Original PDF evidence
- `syllabus-outline.json` - Your Analyst output
- `concepts/concept_explanations.json` - Your Writer output
- `quality-inspection.json` - Inspector output
- `final-review-packet.json` - Your Reviewer output
- `validation.json` - Automated checks
- `agent-orchestration.json` - Role completion log

**If visuals were requested** (prompt-queue method):
- `images/infographic_jobs.md` - Markdown list of visual specs you wrote
- User can generate these visuals externally, then import with `scripts/import_infographic_assets.py`

**If term glossary was requested**:
- Module 4 in guide.html contains the bilingual term table

**Message to user**:
```
Your {Board} {Subject} {Level} revision handbook is ready:

📄 guide.html - Open in browser to view
📑 guide.pdf - {page_count} pages, print-friendly

8 modules included:
✓ Cover ({Board} branding)
✓ How to Use This Handbook
✓ Study Roadmap ({topic_count} topics)
✓ Term Glossary ({glossary_count} terms in {language})
✓ Topic Guides (concepts + examples + visuals)
✓ Practice Workbook ({practice_count} cards)
✓ Exam Structure
✓ Revision Checklist

Quality gates passed:
✓ Quality Inspector passed format/completeness
✓ Independent reviewer approved
✓ Validation checks clean
✓ PDF rendering verified

{If prompt-queue visuals}
📸 {visual_count} visual specs listed in images/infographic_jobs.md
Generate these images and import with scripts/import_infographic_assets.py
```

---

## Supported Exam Boards

### AQA (Oxford International AQA)

**Discovery method**: Subject name + level
- Python searches public OxfordAQA catalogue
- Returns candidates with code, URL, PDF

**Example subjects**:
- Mathematics (9260, 9265)
- Chemistry (9620)
- Business (9370)

**Coverage**: International GCSE, International AS, International A-Level

### Edexcel (Pearson Edexcel International)

**Discovery method**: Subject name + level
- Python searches Pearson International subject pages
- Returns candidates with code, URL, PDF

**Example subjects**:
- Mathematics (9-1) 4MA1
- Chemistry 4CH1
- Economics 4EC1

**Coverage**: International GCSE, International AS, International A-Level

**Exam year**: Ask user if multiple syllabus ranges found (e.g., 2024-2026 vs 2027-2029)

### Cambridge (Cambridge International / CAIE)

**Discovery method**: Subject name + level + code (optional)
- Python searches Cambridge subject index
- Returns candidates with syllabus code, URL, PDF

**Example subjects**:
- Mathematics 0580 (IGCSE Core and Extended)
- Chemistry 0620
- Economics 0455

**Coverage**: Cambridge IGCSE, Cambridge International AS & A Level

**Exam year**: REQUIRED when multiple syllabus ranges listed (e.g., "for examination from 2025" vs "for examination from 2027")

---

## CLI Fallback (Framework Demo Only)

**Command**: `python -m intl_exam_guide demo {board} {subject}`

**Purpose**: Demonstrates the 8-module framework structure without LLM content

**Output**:
- `template-demo.html` with all modules present
- Each content section shows placeholder: `[LLM fills: topic essence]`, `[LLM judges: visual needed?]`
- Cover and structure are complete
- Content is skeleton only

**Not for production use**. This is a framework preview. Real handbooks require you (LLM) to run the five-role workflow.

---

## Evidence Extraction Only

**Command**: `python -m intl_exam_guide extract-evidence {board} {subject}`

**Purpose**: Downloads PDF and extracts text evidence without generating handbook

**Output**:
- `syllabus-evidence.json` (page text from official specification PDF)
- Message: "Evidence ready. Now run this Skill in your LLM agent to generate the handbook."

**Use case**: Preparing evidence for later handbook generation

---

## Critical Rules

1. **Python has no intelligence**. It does not understand topics, exam points, or teaching needs.
2. **You own all content decisions**. Topic boundaries, exam points, concept explanations, visual needs, quality judgments.
3. **Quality Inspector is mandatory before final review**. Do not skip the fast completeness gate.
4. **Independent reviewer is mandatory**. Do not skip Phase 4. Do not self-review in the same context.
5. **Repair loops are expected**. If inspector or reviewer finds issues, fix and rerender. Do not deliver `final-ready` with known problems.
6. **Validation alone is not enough**. Passing automated checks does not mean teaching quality is good.
7. **Do not reuse syllabus fragments as teaching content**. Write original explanations in the requested style.
8. **Visual judgment is content work**. Do not auto-generate visuals for every topic. Judge case-by-case.
9. **Term glossary is professional vocabulary only**. Not every word from the syllabus. 30-50 high-frequency terms.

---

## Reference Files

Before starting, read:
- `references/revision_guide_spec.md` - Full output contract and artifact details
- `references/style_guide.md` - Writing style definitions (friendly/formal/story/etc.)
- `references/visual_routing_guide.md` - When to use infographics vs diagrams vs no visual

---

## Questions?

If you encounter:
- **Specification PDF not found**: Ask user for direct PDF URL
- **Subject not uniquely resolved**: Show candidates and ask user to pick
- **Exam year ambiguous**: Ask user which syllabus range to use
- **Visual method unclear**: Ask if user has image generation capability or wants prompt-queue

Do not guess. Do not skip steps. Do not deliver draft output as final-ready.
