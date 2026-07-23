"""Rebuild the two standalone intro pages from shared animation sources."""

from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = REPO_ROOT / "docs" / "assets"
ANIMATIONS_PATH = ASSET_ROOT / "three-board-support-video" / "animations.jsx"
TARGETS = (
    ("three-board-support-video", "zh-CN", "IGCSE、A-Level 与 AP 复习手册 Skill 介绍动画"),
    ("three-board-support-video-en", "en", "IGCSE, A-Level & AP Revision Handbook Skill"),
)


def build_html(folder: str, language: str, title: str) -> str:
    animations = ANIMATIONS_PATH.read_text(encoding="utf-8").rstrip()
    video = (ASSET_ROOT / folder / "video.jsx").read_text(encoding="utf-8").rstrip()
    return f"""<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="../intro-animation.css">
</head>
<body>
  <div id="root"></div>
  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
  <script type="text/babel">
{animations}
  </script>
  <script type="text/babel">
{video}
  </script>
</body>
</html>
"""


def sync(check: bool) -> list[Path]:
    changed: list[Path] = []
    for folder, language, title in TARGETS:
        target = ASSET_ROOT / folder / "index.html"
        expected = build_html(folder, language, title)
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current == expected:
            continue
        changed.append(target)
        if not check:
            target.write_text(expected, encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when an index is stale.")
    args = parser.parse_args()
    changed = sync(args.check)
    if args.check and changed:
        for path in changed:
            print(f"stale: {path.relative_to(REPO_ROOT)}")
        return 1
    for path in changed:
        print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
