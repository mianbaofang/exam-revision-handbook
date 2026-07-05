# GitHub Release Checklist / GitHub 发布检查清单

## Repository

- [ ] Repository name, description, and topics are set.
- [ ] `README.md` renders correctly on GitHub.
- [ ] `README.zh-CN.md` is linked from the English README.
- [ ] Static SVG assets used in README/docs render in GitHub Markdown.
- [ ] License is visible.
- [ ] CI is enabled.
- [ ] Issue templates and PR template are visible.

## Source and Copyright

- [ ] No downloaded official specification/syllabus PDFs are committed.
- [ ] No past-paper questions or mark schemes are committed.
- [ ] `outputs/` is ignored.
- [ ] Source policy is clear in README and docs.

## Local Artifact Hygiene

- [ ] Before release validation, review ignored local artifacts with
  `git clean -fdX -n`. Remove stale `outputs/` only after reviewing the dry
  run; release evidence must be regenerated from the current code into fresh
  output directories.
- [ ] Do not use old ignored `outputs/` folders, stale `validation.json`, or
  local design drafts as proof that the current release output is valid.

## Release Evidence Status

- [ ] Classify every changed delivery claim as one of `candidate`, `draft`,
  `final-ready`, or `certified`.
- [ ] Candidate routes are described only as candidate routes; they are not
  release-ready or delivery-grade.
- [ ] Draft outputs have a fresh command and review packet, but the remaining
  blocker is named: pending concepts, pending complex images, PDF/export gap,
  validation error, or Agent self-review block.
- [ ] Final-ready outputs have fresh validation, `final-review-packet.json`,
  concept status, visual status, package manifest, and PDF/export evidence from
  the current code.
- [ ] Certified outputs meet the final-ready bar and have an explicit release
  owner or subject-aware reviewer approval recorded in the manifest.
- [ ] For any `draft`, `final-ready`, or `certified` claim, create or update a
  concise `docs/release-evidence/<version>/manifest.json` entry. Do not commit
  the generated output directory used to collect the evidence.

## Commands

- [ ] Offline demo works:

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --language en --image-provider prompt-queue --explanation-style friendly --skip-pdf
```

- [ ] Subject-page discovery shows qualification metadata:

```bash
python -m intl_exam_guide discover --subject-url https://www.oxfordaqa.com/subjects/science/
```

- [ ] Discovery output includes `international_gcse` rows with the blue listing
  group and `international_as_a_level` rows with the red listing group.

- [ ] OxfordAQA International GCSE sample works:

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

- [ ] OxfordAQA International AS-A-level sample works:

```bash
python -m intl_exam_guide generate --query chemistry --level a-level --language en --image-provider prompt-queue --explanation-style detective --out ./outputs/chemistry-9620
```

- [ ] OxfordAQA non-Science International GCSE sample works:

```bash
python -m intl_exam_guide generate --query economics --level igcse --language en --explanation-style life --out ./outputs/economics-9214
```

- [ ] OxfordAQA revised non-Science International AS-A-level code lookup sample works:

```bash
python -m intl_exam_guide generate --query 9725 --level a-level --language en --explanation-style story --out ./outputs/business-9725
```

- [ ] Pearson Edexcel International GCSE candidate-discovery sample works:

```bash
python -m intl_exam_guide generate --provider pearson --query "Mathematics B" --level igcse --language en --explanation-style friendly --out ./outputs/pearson-igcse-maths-b --skip-pdf
```

- [ ] Pearson Edexcel International AS/A Level candidate-discovery sample works:

```bash
python -m intl_exam_guide generate --provider pearson --query "Biology" --level a-level --language en --explanation-style friendly --out ./outputs/pearson-ial-biology --skip-pdf
```

- [ ] Cambridge IGCSE candidate-discovery sample works with `--exam-year`:

```bash
python -m intl_exam_guide generate --provider cambridge --query "Accounting 0452" --level igcse --exam-year 2027 --language en --explanation-style friendly --out ./outputs/cambridge-igcse-accounting-2027 --skip-pdf
```

- [ ] Cambridge AS/A Level candidate-discovery sample works with `--exam-year`:

```bash
python -m intl_exam_guide generate --provider cambridge --query "Chemistry 9701" --level a-level --exam-year 2029 --language en --explanation-style friendly --out ./outputs/cambridge-ial-chemistry-2029 --skip-pdf
```

## Validation

- [ ] `python -m pytest -q` passes.
- [ ] `python -m compileall -q src tests scripts` passes.
- [ ] Run or refresh the delivery matrix evidence for every
  subject/board/level claim changed in this release.
- [ ] Run `python -m intl_exam_guide review --out <sample-output>` for each
  release sample and record whether it is `ready`,
  `draft_needs_concept_review`, `draft_needs_image_review`, or
  `blocked_errors`. Map that internal result to release evidence status:
  `draft`, `final-ready`, or `certified`; leave route-only checks as
  `candidate`.
- [ ] For every release-ready sample,
  `validation.json.review_summary.pending_concept_explanations` is `0`. If it is
  nonzero, write the missing items from `concepts/concept_jobs.json`, save
  `concepts/concept_explanations.json`, import with
  `scripts/import_concept_explanations.py`, and rerun review.
- [ ] Skill smoke validation passes through at least one local demo/generate
  command and `validation.json` review.
- [ ] Release notes or changelog include fresh end-to-end evidence from the
  current working copy: command, output directory, `issues` count, topic count,
  practice-card count, visual-brief count, section-file count, image-file count,
  and whether HTML/PDF were produced. Do not commit the generated `outputs/`
  folder used for this evidence.
- [ ] A raw-key scan across the repository and release outputs reports
  `raw_key_matches=0`:

```bash
python scripts/scan_for_raw_keys.py . ./outputs
```

- [ ] Pending complex infographics are marked as prompt-queue/external
  generation work, not as generated assets.
- [ ] If complex infographics are pending, release notes must say which
  visual IDs need generation/review and where `images/infographic_jobs.md` is
  located.
- [ ] After a callable image Skill/API/script or designer review workflow has
  produced the pending showcase images, import those reviewed assets into the
  sample guides. If the workflow is callable, the Agent should run it and import
  the results; this is not intended as a manual user file-moving step:

```bash
python scripts/import_infographic_assets.py ./outputs/mathematics-9260-sample --asset-dir ./generated-infographics/mathematics-9260-sample --provider "external-reviewed-workflow"
python scripts/import_infographic_assets.py ./outputs/economics-9214-sample --asset-dir ./generated-infographics/economics-9214-sample --provider "external-reviewed-workflow"
python scripts/import_infographic_assets.py ./outputs/chemistry-9202-sample --asset-dir ./generated-infographics/chemistry-9202-sample --provider "external-reviewed-workflow"
```

- [ ] After infographic assets are generated, `python scripts/finalize_release_samples.py --outputs-root <outputs-dir>` regenerates the final Mathematics, Economics, and Chemistry HTML/PDF samples.
- [ ] `python scripts/verify_release_samples.py --outputs-root <outputs-dir>` passes
  for the final Mathematics, Economics, and Chemistry sample guides.
- [ ] Final guide screenshots are recaptured for `docs/assets/sample-math-guide.png`,
  `docs/assets/sample-economics-guide.png`, `docs/assets/sample-chemistry-guide.png`,
  and `docs/assets/sample-guide-snapshot.png`.
- [ ] The intro animation HTML and GIF preview are regenerated after final guide
  screenshots are recaptured. MP4 export is optional and should stay out of the
  repo unless the release explicitly needs a downloadable video file:

```bash
python scripts/render_intro_animation.py --html docs/project-intro-animation.html --mp4 outputs/project-intro-animation.mp4 --gif docs/assets/intro-animation-preview.gif
python scripts/render_intro_animation.py --html docs/project-intro-animation-en.html --mp4 outputs/project-intro-animation-en.mp4 --gif docs/assets/intro-animation-preview-en.gif
```

- [ ] `validation.json` has no `error` issues for the offline demo.
- [ ] `validation.json` has no `error` issues for one International GCSE subject.
- [ ] `validation.json` has no `error` issues for one International AS-A-level subject.
- [ ] `validation.json` has no `error` issues for one non-Science International GCSE subject.
- [ ] `validation.json` has no `error` issues for one revised non-Science
  International AS-A-level code lookup subject.
- [ ] Live parser audit across discovered OxfordAQA qualification pages shows
  no missing topics, assessments, specification links, or listing/type conflicts.
- [ ] `validation.json.review_summary` has the expected topic, guide, practice-card, diagram, and source-snippet counts.
- [ ] Generated HTML includes source checks.
- [ ] Generated HTML includes website listing metadata when discovered from a subject page.
- [ ] Generated HTML includes one concept map per topic.
- [ ] Generated HTML includes practice cards with command words, solution steps, and answer checkpoints.
- [ ] Generated HTML records the selected term-support language in `run-options.json`.
- [ ] Handbook body, template labels, examples, diagram text, and image prompts remain English.
- [ ] Non-`en` runs include a 30-50 item professional glossary mapping the selected support language to English exam terms.
- [ ] Official source text remains traceable in structured files or a separated review appendix, not mixed into the student-facing topic body.
- [ ] Generated PDF opens locally.

## Accuracy

- [ ] The README clearly says the current release creates source-grounded handbooks, not copied past-paper questions.
- [ ] Deep worked examples are marked as requiring subject review.
- [ ] Regional/exam-centre availability is described as something families must confirm locally.

## 中文发布检查

- [ ] 中文 README 能解释项目是什么、适合谁、怎么跑。
- [ ] 中文 README 解释 International GCSE / International AS-A-level 的蓝色/红色 listing 映射。
- [ ] 准确性政策中明确说明“不编造 syllabus、不复制真题、不提交 PDF”。
- [ ] 语言策略明确：生成前选择术语辅助语言；手册正文保持英文，非 `en` 只增加 30-50 个“用户语言 → English exam term”专业词对照表。
- [ ] 给孩子正式使用前，需要老师或熟悉大纲的人复核深度例题。
