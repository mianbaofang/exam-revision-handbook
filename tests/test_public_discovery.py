from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REPO = "https://github.com/mianbaofang/exam-revision-handbook"
CANONICAL_SITE = "https://mianbaofang.github.io/exam-revision-handbook/"


def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_public_readmes_put_installation_before_origin_story() -> None:
    english = read("README.md")
    chinese = read("README.zh-CN.md")

    assert english.index("## Start In One Minute") < english.index("## Why This Skill Exists")
    assert chinese.index("## 一分钟开始使用") < chinese.index("## 为什么要做这个 Skill")
    for text in (english, chinese):
        assert CANONICAL_REPO in text
        assert "gcse-igcse-alevel-ap-revision-guide" not in text
        assert "AS/A-Level" not in text
        assert "AS-A-level" not in text


def test_pages_publish_complete_search_and_ai_discovery_signals() -> None:
    manifest = json.loads(read("manifest.json"))
    version = manifest["version"]
    chinese = read("docs/index.html")
    english = read("docs/index-en.html")
    robots = read("docs/robots.txt")
    llms = read("docs/llms.txt")

    for page in (chinese, english):
        assert 'name="description"' in page
        assert 'name="robots"' in page
        assert 'property="og:image"' in page
        assert 'type="application/ld+json"' in page
        assert CANONICAL_REPO in page
        assert f"v{version}" in page

    assert f"Sitemap: {CANONICAL_SITE}sitemap.xml" in robots
    assert f"{CANONICAL_SITE}index-en.html" in llms
    assert f"{CANONICAL_REPO}/releases/latest" in llms

    sitemap = ET.fromstring(read("docs/sitemap.xml"))
    locations = {
        node.text
        for node in sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    assert CANONICAL_SITE in locations
    assert f"{CANONICAL_SITE}index-en.html" in locations
    assert f"{CANONICAL_SITE}llms.txt" in locations


def test_public_release_links_share_the_skill_name_and_version() -> None:
    version = json.loads(read("manifest.json"))["version"]
    expected = f"exam-revision-handbook-v{version}.zip"

    for relative in ("README.md", "README.zh-CN.md", "docs/index.html", "docs/index-en.html"):
        text = read(relative)
        assert expected in text
        assert not re.search(r"exam-revision-handbook-v(?!" + re.escape(version) + r")", text)
