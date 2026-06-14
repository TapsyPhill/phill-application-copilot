"""Multi-model voting for final classification."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class VoteResult:
    final_category: str
    final_status: str
    agreement_ratio: float
    confidence: float
    needs_manual_review: bool


class VotingEngine:
    def decide(self, model_outputs: list[dict[str, Any]]) -> VoteResult:
        if not model_outputs:
            return VoteResult("manual_review", "manual_review", 0, 0, True)

        categories = [o.get("category", "manual_review") for o in model_outputs]
        statuses = [o.get("recommended_status", "manual_review") for o in model_outputs]
        cat_counter = Counter(categories)
        status_counter = Counter(statuses)
        top_cat, cat_votes = cat_counter.most_common(1)[0]
        top_status, _ = status_counter.most_common(1)[0]
        agreement = cat_votes / len(model_outputs)
        avg_conf = sum(float(o.get("confidence") or 0) for o in model_outputs) / len(model_outputs)

        needs_manual = agreement < 0.67 or avg_conf < 50
        if agreement == 1.0:
            conf_band = min(95, avg_conf + 10)
        elif agreement >= 0.67:
            conf_band = avg_conf
        else:
            conf_band = max(30, avg_conf * 0.6)
            top_status = "manual_review"

        return VoteResult(
            final_category=top_cat,
            final_status=top_status,
            agreement_ratio=round(agreement, 2),
            confidence=round(conf_band, 2),
            needs_manual_review=needs_manual,
        )
