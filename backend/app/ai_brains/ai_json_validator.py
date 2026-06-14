"""Validate structured JSON from AI models."""

from __future__ import annotations

import json
import re
from typing import Any

REQUIRED_FIELDS = (
    "is_relevant",
    "category",
    "title",
    "summary",
    "confidence",
    "reason",
    "evidence",
)

RELEVANT_CATEGORIES = frozenset({"client_lead", "phd", "job", "remote_job"})


def parse_and_validate(raw: str) -> tuple[dict[str, Any] | None, str | None]:
    raw = _extract_json(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json: {exc}"
    if not isinstance(data, dict):
        return None, "root_must_be_object"
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return None, f"missing_fields: {','.join(missing)}"
    evidence = data.get("evidence")
    evidence = data.get("evidence")
    if not evidence or (isinstance(evidence, list) and len(evidence) == 0):
        if (data.get("confidence") or 0) > 70:
            data["confidence"] = 45
    cat = str(data.get("category") or "").strip()
    relevant = data.get("is_relevant")
    if relevant is True and cat not in RELEVANT_CATEGORIES:
        return None, f"invalid_category_for_relevant: {cat}"
    if relevant is False and cat not in ("rejected", "manual_review"):
        data["category"] = "rejected"
    return data, None


def _extract_json(raw: str) -> str:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text
