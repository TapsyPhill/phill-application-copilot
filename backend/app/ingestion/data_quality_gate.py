"""Data quality gate — reject garbage before AI spend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QualityResult:
    quality_score: float
    quality_status: str  # passed | failed | manual_review | needs_rescrape
    rejection_reason: str | None = None
    manual_review_reason: str | None = None


class DataQualityGate:
    MIN_TEXT_LENGTH = 120
    MAX_NAV_RATIO = 0.35

    NAV_MARKERS = (
        "cookie",
        "accept all",
        "navigation",
        "menu",
        "subscribe",
        "sign in",
        "log in",
        "captcha",
    )

    def evaluate(self, title: str | None, body: str, source_url: str) -> QualityResult:
        reasons: list[str] = []
        score = 100.0

        if not source_url:
            return QualityResult(0, "failed", rejection_reason="missing_source_url")
        if not body or len(body.strip()) < self.MIN_TEXT_LENGTH:
            return QualityResult(
                10, "failed", rejection_reason="body_too_short_or_empty"
            )
        if not title or len(title.strip()) < 3:
            score -= 15
            reasons.append("weak_title")

        lower = body.lower()
        nav_hits = sum(1 for m in self.NAV_MARKERS if m in lower)
        if nav_hits >= 4:
            score -= 30
            reasons.append("mostly_navigation_or_banner")

        if "access denied" in lower or "403 forbidden" in lower:
            return QualityResult(0, "needs_rescrape", rejection_reason="blocked_page")

        if "captcha" in lower or "login required" in lower:
            return QualityResult(
                20,
                "manual_review",
                manual_review_reason="login_or_captcha_detected",
            )

        if score < 50:
            return QualityResult(
                score,
                "manual_review",
                manual_review_reason=";".join(reasons) or "low_quality",
            )
        if reasons:
            return QualityResult(score, "passed", manual_review_reason=";".join(reasons))
        return QualityResult(score, "passed")
