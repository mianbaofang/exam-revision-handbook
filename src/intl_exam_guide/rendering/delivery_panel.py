from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from intl_exam_guide.auditing.concept_jobs import reviewed_concept_titles
from intl_exam_guide.models import GuidePlan
from intl_exam_guide.planning.language_policy import handbook_body_language
from intl_exam_guide.rendering.text import html_escape
from intl_exam_guide.rendering.visual_assets import PENDING_ASSET_STATUSES


def render_delivery_panel(
    plan: GuidePlan,
    manifest_entries: list[dict[str, Any]],
    output_dir: Path,
) -> str:
    language = handbook_body_language(plan.run_options.output_language)
    summary = delivery_panel_summary(plan, manifest_entries, output_dir)
    state = str(summary["state"])
    label = state_label(state, language)
    message = state_message(summary, language)
    detail_items = delivery_detail_items(summary, language)
    items = "".join(f"<li>{html_escape(item)}</li>" for item in detail_items)
    heading = "Review Check" if language == "en" else "复查提示"
    status_label = "Current check" if language == "en" else "当前检查"
    return f"""
<section class="band delivery-panel" data-review-state="{html_escape(state)}">
  <h2>{html_escape(heading)}</h2>
  <div class="delivery-status-grid">
    <div class="delivery-state-badge delivery-state-{html_escape(state)}">
      <span>{html_escape(status_label)}</span>
      <strong>{html_escape(label)}</strong>
    </div>
    <div class="delivery-state-detail">
      <p>{html_escape(message)}</p>
      <ul>{items}</ul>
    </div>
  </div>
</section>
"""


def delivery_panel_summary(
    plan: GuidePlan,
    manifest_entries: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, object]:
    guide_titles = {guide.topic_title for guide in plan.topic_guides}
    reviewed_titles = reviewed_concept_titles(output_dir)
    pending_concepts = max(0, len(guide_titles) - len(guide_titles & reviewed_titles))
    pending_images = sum(
        1
        for entry in manifest_entries
        if entry.get("complexity") == "infographic"
        and str(entry.get("asset_status", "")).lower() in PENDING_ASSET_STATUSES
    )
    packet = read_json(output_dir / "final-review-packet.json")
    validation = read_json(output_dir / "validation.json")
    state = state_from_artifacts(pending_concepts, pending_images, packet, validation)
    return {
        "state": state,
        "pending_concepts": pending_concepts,
        "pending_images": pending_images,
        "has_review_packet": bool(packet),
    }


def state_from_artifacts(
    pending_concepts: int,
    pending_images: int,
    packet: dict[str, Any],
    validation: dict[str, Any],
) -> str:
    delivery_status = str(validation.get("delivery_status") or "")
    delivery_state = str(validation.get("delivery_state") or "")
    if delivery_status == "blocked_errors" or delivery_state in {"candidate", "unsupported"}:
        return "blocked"
    if pending_concepts or pending_images or delivery_state == "draft":
        return "draft"
    return "needs-review"


def state_label(state: str, language: str) -> str:
    if language == "en":
        return {
            "blocked": "Blocked",
            "draft": "Draft",
            "needs-review": "Needs visible review",
        }.get(state, state)
    return {
        "blocked": "阻断",
        "draft": "草稿",
        "needs-review": "需要打开复查",
    }.get(state, state)


def state_message(summary: dict[str, object], language: str) -> str:
    pending_concepts = int_value(summary.get("pending_concepts"))
    pending_images = int_value(summary.get("pending_images"))
    state = str(summary.get("state") or "")
    if language == "en":
        if state == "blocked":
            return "Mechanical validation has blocking errors; repair them before handoff."
        if pending_concepts or pending_images:
            return "This handbook is still a draft because required concept or visual review work is open."
        if summary.get("has_review_packet"):
            return "A review packet exists, but the host LLM must still inspect the rendered HTML before claiming completion."
        return "The rendered HTML is ready for host LLM review, not automatic approval."
    if state == "blocked":
        return "机器验证仍有阻断错误，交付前必须修复。"
    if pending_concepts or pending_images:
        return "这份手册仍是草稿，未完成的概念讲解或复杂配图不能当作最终成品。"
    if summary.get("has_review_packet"):
        return "已生成复查包，但宿主 LLM 仍必须打开 HTML 后才能声称完成。"
    return "HTML 已可进入宿主 LLM 复查，但不能自动批准。"


def delivery_detail_items(summary: dict[str, object], language: str) -> list[str]:
    pending_concepts = int_value(summary.get("pending_concepts"))
    pending_images = int_value(summary.get("pending_images"))
    has_review_packet = bool(summary.get("has_review_packet"))
    if language == "en":
        return [
            f"Pending concept explanation reviews: {pending_concepts}",
            f"Pending complex image assets: {pending_images}",
            "Review packet: present" if has_review_packet else "Review packet: not yet run",
            "Rendered HTML must be opened or screenshot-inspected before handoff.",
        ]
    return [
        f"待复查概念讲解：{pending_concepts}",
        f"待完成复杂配图：{pending_images}",
        "复查包：已生成" if has_review_packet else "复查包：尚未运行",
        "交付前必须打开或截图检查渲染后的 HTML。",
    ]


def int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
