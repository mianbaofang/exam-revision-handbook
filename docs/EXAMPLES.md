# Examples / 示例

## Offline Demo

The offline demo uses `src/intl_exam_guide/assets/demo_qualification.json`. It
does not download OxfordAQA content and does not include copyrighted PDFs.

```bash
python scripts/run_runtime.py -- demo --out ./outputs/demo-science
```

Expected files:

```text
outputs/demo-science/
  <board>-<level>-<subject>-<time>.html
  <board>-<level>-<subject>-<time>.html  HTML preview; demo stops before PDF
  guide-plan.json
  qualification.json
  validation.json
```

Open `validation.json` after each run. The `issues` list is a mechanical
diagnostic, not a teaching or approval decision. The demo is a framework preview
and cannot replace an LLM Analyst/Writer/Reviewer run.

The HTML records visual slots from the manifest. Exact SVG appears only when an
LLM-authored visual spec marks `svg_fit: "exact"` and the asset has been
reviewed; complex visuals stay as pending jobs until reviewed raster assets are
imported.

Each topic also receives practice cards. A card records the command word,
difficulty, focus point, public solution steps, answer checkpoints, and the
source points used to shape the prompt.

## OxfordAQA International GCSE Example

First inspect the subject page listings:

```bash
python scripts/run_runtime.py -- discover --subject-url https://www.oxfordaqa.com/subjects/science/
```

The science page should show International GCSE rows tagged as
`international_gcse` with the blue listing group, and International A-Level
rows tagged as `international_as_a_level` with the red listing group.

```bash
python scripts/run_runtime.py -- generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

## OxfordAQA International A-Level Example

```bash
python scripts/run_runtime.py -- generate --query chemistry --level a-level --out ./outputs/chemistry-9620
```

## OxfordAQA Non-Science International GCSE Example

```bash
python scripts/run_runtime.py -- generate --query economics --level igcse --out ./outputs/economics-9214
```

## OxfordAQA Revised Non-Science A-Level Example

```bash
python scripts/run_runtime.py -- generate --query 9725 --level a-level --out ./outputs/business-9725
```

This covers a revised qualification page where the subject listing text does
not include the code, but the qualification detail page does.

## Pearson Edexcel Examples

Pearson support first tries official subject-page candidates from the subject
name. If several routes match, the CLI returns the choices for the user to pick.
Official subject-page URLs or direct specification PDF URLs still work as exact
inputs:

```bash
python scripts/run_runtime.py -- generate --provider pearson --query "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html" --level igcse --out ./outputs/pearson-igcse-maths
python scripts/run_runtime.py -- generate --provider pearson --query "https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels/mathematics-2018.html" --level a-level --out ./outputs/pearson-ial-maths
```

## Cambridge International / CAIE Examples

Cambridge support searches the official subject indexes by subject name or code.
If several routes match, the CLI returns the choices for the user to pick.
Cambridge subject pages often list several syllabus year ranges, so provide
`--exam-year` when the selected page has multiple syllabus PDFs:

```bash
python scripts/run_runtime.py -- generate --provider cambridge --query "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-chemistry-0620/" --level igcse --exam-year 2027 --out ./outputs/cambridge-igcse-chemistry-2027
python scripts/run_runtime.py -- generate --provider cambridge --query "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-chemistry-9701/" --level a-level --exam-year 2029 --out ./outputs/cambridge-ial-chemistry-2029
```

## Release Sample Verification

The repository's public homepage should be built from completed guide samples.
Use the release verifier before publishing:

```bash
python scripts/verify_release_samples.py --outputs-root ./outputs --allow-pending
```

`--allow-pending` is only for pre-image checks. Final publication must pass
without that flag:

```bash
python scripts/import_infographic_assets.py ./outputs/mathematics-9260-sample --asset-dir ./generated-infographics/mathematics-9260-sample --provider "external-reviewed-workflow"
python scripts/import_infographic_assets.py ./outputs/economics-9214-sample --asset-dir ./generated-infographics/economics-9214-sample --provider "external-reviewed-workflow"
python scripts/import_infographic_assets.py ./outputs/chemistry-9202-sample --asset-dir ./generated-infographics/chemistry-9202-sample --provider "external-reviewed-workflow"
# Repeat review -> complete visible LLM inspection -> export-pdf for each sample.
python scripts/run_runtime.py -- review --out ./outputs/<sample>
python scripts/run_runtime.py -- export-pdf --out ./outputs/<sample>
python scripts/verify_release_samples.py --outputs-root ./outputs
python scripts/capture_release_assets.py --outputs-root ./outputs --docs-assets docs/assets
python scripts/render_intro_animation.py --html docs/project-intro-animation.html --mp4 outputs/project-intro-animation.mp4 --gif docs/assets/intro-animation-preview.gif
python scripts/render_intro_animation.py --html docs/project-intro-animation-en.html --mp4 outputs/project-intro-animation-en.mp4 --gif docs/assets/intro-animation-preview-en.gif
```

If your image provider or image-generation Skill writes files outside the guide
package, the Agent should import them before rerendering HTML. The active LLM
must then review the complete current HTML and record approval before any PDF
export.
Generated filenames should start with the manifest ID, such as
`visual_001.png` or `visual_001_lab-apparatus.png`:

```bash
python scripts/import_infographic_assets.py ./outputs/chemistry-9202 \
  --asset-dir ./generated-infographics/chemistry-9202 \
  --provider "custom-image-model"
```

## 中文说明

离线 demo 使用仓库内置的合成 qualification，不下载 OxfordAQA 内容，也不包含任何
受版权限制的 PDF。它适合用于测试安装环境、查看 HTML 样式、验证
`validation.json` 的结构；它不会替代 LLM 审查，也不会自动导出 PDF。

每次生成后都可以打开 `validation.json` 查看机械诊断；它不是教学质量或
最终交付的自动通过结论。离线 demo 只用于检查框架和 HTML，不是教学级手册。

HTML 会记录 manifest 中的视觉槽位。只有 LLM 写明 `svg_fit="exact"` 且资产经过复核时，exact SVG 才能进入手册；复杂视觉内容会保持为待处理任务，直到导入已复核的 raster 图片。

每个 topic 也会生成练习卡片。卡片会记录指令词、难度、
聚焦知识点、公开解题步骤、答案检查点，以及用于约束题干的
source points。

建议先运行 `discover --subject-url` 检查学科页。International GCSE 行应标记为
`international_gcse` 和蓝色 listing；International A-Level 行应标记为
`international_as_a_level` 和红色 listing。

真实 OxfordAQA 示例会在运行时下载公开 specification PDF。不要把下载得到的 PDF
提交到仓库。

Economics 示例用于覆盖非 Science 页面结构：该页面使用 strong headings 和 paragraph
points 描述 syllabus summary。

Business 9725 示例用于覆盖修订版 A-level 页面结构：subject listing 的文字不带
代码，但 qualification 详情页带代码，因此可以验证代码查询不会被同级别科目带偏。

发布前应使用 release verifier 检查各份样板。`--allow-pending` 只适合信息图还没生成时做预检查；最终发布前必须去掉这个参数，并确认每份手册都分别完成当前 HTML 的全量 LLM 审查、写入自己的 `agent-product-review.json`，再通过 `export-pdf` 导出 PDF。不能把一份样板的审查结论共用于另一份手册。
这三份只是公开展示和回归验证样例，不是 OxfordAQA 科目支持上限。
截图更新后，再用 `scripts/render_intro_animation.py` 重新导出介绍动画 GIF；MP4 仅在需要视频文件时导出到 `outputs/`。

如果你的生图 Skill、API 或脚本把图片输出到手册目录外，Agent 应该用
`scripts/import_infographic_assets.py` 自动导入。文件名需要以 manifest ID 开头，
例如 `visual_001.png` 或 `visual_001_lab-apparatus.png`。
