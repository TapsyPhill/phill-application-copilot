"""Validate structured JSON from AI models."""

from __future__ import annotations

import json
from typing import Any

REQUIRED_FIELDS = (
    "is_relevant",
    "category",
    "title",
    "summary",
    "confidence",
    "reason",
    "evidence",
    "model_name",
)


def parse_and_validate(raw: str) -> tuple[dict[str, Any] | None, str | None]:
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
    if not evidence or (isinstance(evidence, list) and len(evidence) == 0):
        if (data.get("confidence") or 0) > 70:
            return None, "high_confidence_requires_evidence"
    return data, None
