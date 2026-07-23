# College Board AP Provider Feasibility Audit

Audit date: 2026-07-20

Status: implemented as the `collegeboard` production source provider after the
feasibility audit. Subject-specific handbook delivery remains evidence-gated.

## Source

- Official directory: <https://apstudents.collegeboard.org/courses>
- Official course pages: `apstudents.collegeboard.org/courses/ap-*`
- Official Course and Exam Description PDFs: `apcentral.collegeboard.org`

The directory HTML states that it covers 42 AP subjects. It contains 44 AP-like
course paths: 42 subject pages plus two overview pages, `AP Career Kickstart`
and `AP Computer Science Courses`. The overview pages must not be treated as
subjects.

## Audit Result

- 42 of 42 official subject pages returned successfully in a low-frequency,
  sequential crawl.
- All 42 subject pages contained one identifiable core `Course and Exam
  Description` (CED) after excluding separate clarification/correction files.
- The 42 courses resolved to 39 unique CED URLs.
- All 39 unique URLs stayed on official College Board domains and returned a
  valid `%PDF-` file signature.
- 35 course pages exposed numbered `Unit N: ...` headings directly in static
  HTML. The other seven use a different course structure and must be outlined
  from their CED rather than forced into numbered web-page units.

The seven pages without numbered unit headings are:

- AP 2-D Art and Design
- AP 3-D Art and Design
- AP Computer Science Principles
- AP Drawing
- AP English Language and Composition
- AP Research
- AP Seminar

## Shared And Supplemental Documents

- AP Calculus AB and AP Calculus BC share one CED.
- AP 2-D Art and Design, AP 3-D Art and Design, and AP Drawing share one CED.
- AP Computer Science A and AP Latin each expose a separate
  `Clarifications and Corrections` PDF. This is supplemental evidence, not the
  core CED, and must not create an ambiguous core-document match.

## PDF Content Check

Six representative CEDs were downloaded and parsed with `pypdf`: AP Art and
Design, AP African American Studies, AP Business with Personal Finance, AP
Calculus AB/BC, AP Cybersecurity, and AP Latin. All six contained the course
title, CED identity, course framework, and assessment or portfolio information.
The numbered-unit courses also exposed their unit sequence in PDF text.

The sample confirmed that effective dates vary. Examples include Calculus
effective Fall 2020, Art and Design and African American Studies effective Fall
2024, Latin effective Fall 2025, and Business with Personal Finance and
Cybersecurity effective Fall 2026. A production provider must therefore retain
the effective version and check it against the user's exam year.

## Production Acceptance Rules

The College Board AP provider now:

1. Enumerates the official directory and accepts only the 42 subject links whose
   visible title begins with `AP `.
2. Explicitly excludes the two overview pages.
3. Selects only the core card whose title identifies it as a `Course and Exam
   Description`; clarification/correction files remain supplemental evidence.
4. Requires an official College Board domain, a successful response, and a PDF
   file signature before accepting the CED.
5. Preserves shared CED relationships instead of duplicating or inventing
   course-specific documents.
6. Extracts and retains the CED effective date/version and downloaded content
   hash. The standalone audit additionally records the final redirected URL,
   content hash because College Board states that CEDs are updated periodically.
7. Uses page units as a cross-check where present, but lets the CED define the
   actual outline for non-unit and portfolio/capstone courses.
8. Stops with a source-verification error if any required condition fails. It
   must never guess a syllabus from a similarly named PDF.

## Reproduction

Install the isolated audit dependencies and run the research utility:

```powershell
python -m pip install -e ".[audit]"
python scripts/audit_ap_courses.py --out .\outputs\ap-course-audit
```

The utility writes the raw directory page, all course pages, a JSON audit, and
a CSV course-to-CED mapping. It crawls sequentially with retry/backoff to avoid
turning College Board rate limits into false missing-document results.
