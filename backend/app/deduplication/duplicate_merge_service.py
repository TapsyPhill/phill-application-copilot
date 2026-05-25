"""Merge duplicate opportunities without resetting user state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MergeDecision:
    primary_id: str
    duplicate_id: str
    match_type: str
    preserve_viewed: bool = True
    increment_times_seen: bool = True


class DuplicateMergeService:
    """Apply merge rules: keep viewed, notes, status history."""

    def build_update_payload(
        self, primary: dict[str, Any], duplicate: dict[str, Any], match_type: str
    ) -> dict[str, Any]:
        times_seen = (primary.get("times_seen") or 1) + 1
        payload: dict[str, Any] = {
            "last_seen_at": duplicate.get("last_seen_at") or primary.get("last_seen_at"),
            "times_seen": times_seen,
        }
        if primary.get("viewed"):
            payload["viewed"] = True
            payload["viewed_at"] = primary.get("viewed_at")
        elif duplicate.get("viewed"):
            payload["viewed"] = True
            payload["viewed_at"] = duplicate.get("viewed_at")

        if (duplicate.get("final_score") or 0) > (primary.get("final_score") or 0):
            payload["final_score"] = duplicate["final_score"]
        return payload
