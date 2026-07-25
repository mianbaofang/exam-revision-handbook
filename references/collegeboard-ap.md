# College Board AP Provider Notes

Use `--provider collegeboard` or an exact subject request beginning with `AP`.
The provider discovers the official directory at:

`https://apstudents.collegeboard.org/courses`

Provider rules:

- accept only official subject pages whose visible title begins with `AP `;
- exclude AP Career Kickstart and the AP Computer Science program overview;
- select exactly one core link titled `Course and Exam Description`;
- never substitute a `Clarifications and Corrections` PDF for the core CED;
- accept CED PDFs only from `apcentral.collegeboard.org`;
- preserve shared CEDs, including Calculus AB/BC and the three Art and Design courses;
- read the CED effective Fall version after download and reject a target exam
  year earlier than the first exam year that version can cover;
- use numbered course-page units only as a cross-check. The LLM Analyst must
  still derive the authoritative outline from the downloaded CED evidence.

Example:

```bash
python -m intl_exam_guide extract-evidence --provider collegeboard --query "AP Cybersecurity" --level ap --exam-year 2027 --out ./outputs/ap-cybersecurity
```

AP source discovery is implemented, but handbook delivery status remains
`candidate` until a subject-specific output completes the normal Analyst,
Writer, visual, PDF, and final-review evidence chain.
