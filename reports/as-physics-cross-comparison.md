# AS Physics Handbook Cross-Comparison

Date: 2026-09-06

## Scope

This report compares the isolated `v0.7.2` renderer, the current `main` renderer, the existing desktop canonical HTML, and the separate desktop Chinese HTML.

## Reproduction

The same `guide-plan.json` and `images/visual_manifest.json` were rendered with:

- `tmp/repro-v0.7.2` at tag `v0.7.2` (`28d771b`)
- current `main` source at `4d0fa4b` / tag `v0.7.4`

The outputs are byte-identical:

- SHA-256: `49422346c8a9337d9f39a7a55fdc3e9170ac759341b43c2a6eddd00025e70377`
- Size: `253606` bytes
- `sections`: 40
- `articles`: 170
- `topics`: 33
- AQA cover marker `cover-template-aqa`: 2
- `professional-glossary`: 1
- HTML language: `en`

The byte-identical desktop canonical file is:
`LOCAL_PATH

## Separate Bypass Output

The desktop file:
`LOCAL_PATH

has these signatures:

- SHA-256: `d6db35449bb37b69265b2797ccaa817cfaf7eeca8ceac53ef9d6fe03699c0148`
- Size: `53823` bytes
- `sections`: 69
- `articles`: 33
- `topics`: 33
- `cover-template-aqa`: 0
- `professional-glossary`: 0
- `.hero`: 1
- `linear-gradient`: 1
- HTML language: `zh-CN`

The source is the untracked script `scripts/create_chinese_as_physics_handbook.py`. It hard-codes desktop output paths, constructs a custom `.hero`, writes Chinese body content, and calls `OUT_HTML.write_text(build_html(...))` directly. It does not call `write_handbook_package()` or `render_html()`.

## Conclusion

The `SKILL.md` relocation from the repository root to `skills/exam-revision-handbook/SKILL.md` between `v0.7.2` and `v0.7.3` did not remove the framework. The canonical renderer and templates remained stable, and the `v0.7.2` reproduction matches the current renderer exactly.

The format regression is caused by a separate, untracked desktop generation path. Its delivery manifest already marks it `generated_not_canonical_final` and `canonical_status: blocked`, but its formal-looking filename made it easy to mistake for the canonical output.

One remaining canonical content issue is a Chinese `audience_note` in the source appendix. For the requested language policy (English body plus Chinese-English glossary only), that field must be changed to English before the next canonical rerender.
