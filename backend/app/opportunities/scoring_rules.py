"""Stage 1 scoring rules — category-aware final score 0–100."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreBreakdown:
    profile_match_score: float = 0.0
    recency_score: float = 0.0
    evidence_score: float = 0.0
    contact_score: float = 0.0
    application_method_score: float = 0.0
    country_score: float = 0.0
    source_reliability_score: float = 0.0
    duplicate_penalty: float = 0.0
    urgency_score: float = 0.0
    final_score: float = 0.0


class ScoringRules:
    HIGH_PRIORITY = 80
    REVIEW_RECOMMENDED = 60
    MANUAL_REVIEW = 40

    def score_client_lead(self, data: dict[str, Any]) -> ScoreBreakdown:
        b = ScoreBreakdown()
        if data.get("contact_email") or data.get("contact_phone") or data.get("email_found") or data.get("phone_found"):
            b.contact_score = 90
        elif data.get("contact_form_url"):
            b.contact_score = 60
        else:
            b.contact_score = 25
        need = data.get("client_need_type") or data.get("technical_service_category")
        b.profile_match_score = 85 if need and need != "unknown_technical_need" else 45
        region = data.get("lead_region") or data.get("country")
        if region in ("Germany", "South Africa") or data.get("south_africa_focus"):
            b.country_score = 85
        else:
            b.country_score = 70
        b.evidence_score = min(100, (data.get("evidence_quality_score") or 50))
        return self._finalize(b)

    def score_phd(self, data: dict[str, Any]) -> ScoreBreakdown:
        b = ScoreBreakdown()
        funding = data.get("funding_status", "unclear")
        if funding in ("fully_funded", "salaried_phd", "scholarship_available"):
            b.profile_match_score = 90
        elif funding == "self_funded":
            b.profile_match_score = 15
        else:
            b.profile_match_score = 40
        if data.get("email_application_possible") == "yes" or data.get("email_found") or data.get("contact_email"):
            b.application_method_score = 90
            b.contact_score = 85
        elif data.get("application_url"):
            b.application_method_score = 65
        b.country_score = 85 if (data.get("country") in ("Germany", "EU", "Canada", "New Zealand", "Scotland")) else 60
        b.evidence_score = 80 if data.get("funding_proof") else 35
        b.urgency_score = data.get("urgency_score") or 0
        return self._finalize(b)

    def score_job(self, data: dict[str, Any]) -> ScoreBreakdown:
        b = ScoreBreakdown()
        skills = data.get("required_skills") or data.get("skills_required") or []
        skill_text = " ".join(skills).lower() if isinstance(skills, list) else str(skills).lower()
        keywords = ("python", "llm", "rag", "fastapi", "sql", "data scien", "machine learning", "actuarial")
        hits = sum(1 for k in keywords if k in skill_text)
        b.profile_match_score = min(95, 50 + hits * 12)
        langs = str(data.get("language_requirements", "")).lower()
        if "native german" in langs or "c2" in langs or "c1 german" in langs:
            b.profile_match_score *= 0.6
        if data.get("email_application_possible") == "yes" or data.get("email_found") or data.get("contact_email"):
            b.application_method_score = 88
            b.contact_score = 85
        elif data.get("application_url"):
            b.application_method_score = 65
        b.evidence_score = data.get("evidence_quality_score") or 55
        b.urgency_score = data.get("urgency_score") or 0
        return self._finalize(b)

    def score_remote_job(self, data: dict[str, Any]) -> ScoreBreakdown:
        b = ScoreBreakdown()
        restriction = data.get("remote_restriction", "unclear")
        remote_scores = {
            "worldwide_remote": 95,
            "eu_remote": 88,
            "africa_remote": 85,
            "south_africa_friendly": 90,
            "germany_remote": 75,
            "us_only_remote": 20,
            "hybrid_only": 10,
        }
        b.country_score = remote_scores.get(restriction, 40)
        b.evidence_score = 85 if data.get("remote_proof") else 30
        b.profile_match_score = data.get("fit_score") or 60
        return self._finalize(b)

    def _finalize(self, b: ScoreBreakdown) -> ScoreBreakdown:
        weights = (
            ("profile_match_score", 0.25),
            ("recency_score", 0.10),
            ("evidence_score", 0.20),
            ("contact_score", 0.15),
            ("application_method_score", 0.10),
            ("country_score", 0.10),
            ("source_reliability_score", 0.05),
            ("urgency_score", 0.05),
        )
        total = sum(getattr(b, k) * w for k, w in weights) - b.duplicate_penalty
        b.final_score = round(max(0, min(100, total)), 2)
        return b
