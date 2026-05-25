"""Map AI classification output to opportunity + detail table payloads."""

from __future__ import annotations

import re
from dataclasses import asdict
from datetime import date
from typing import Any

from backend.app.deduplication.url_deduper import url_hash
from backend.app.opportunities.scoring_rules import ScoreBreakdown, ScoringRules


def build_opportunity_payload(
    vote_category: str,
    vote_status: str,
    confidence: float,
    model_data: dict[str, Any],
    cleaned_post: dict[str, Any],
    source: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], ScoreBreakdown]:
    source_url = cleaned_post["source_url"]
    uh = cleaned_post.get("url_hash") or url_hash(source_url)
    ch = cleaned_post.get("content_hash")
    rules = ScoringRules()
    data = {**model_data, "evidence_quality_score": _evidence_score(model_data)}

    if vote_category == "client_lead":
        breakdown = rules.score_client_lead(data)
        details = {
            "client_type": model_data.get("organization"),
            "need_detected": model_data.get("summary"),
            "technical_service_category": model_data.get("client_need_type")
            or model_data.get("subcategory")
            or "unknown_technical_need",
            "lead_region": model_data.get("country"),
            "south_africa_focus": (model_data.get("country") == "South Africa")
            or "south africa" in (model_data.get("summary") or "").lower(),
        }
    elif vote_category == "phd":
        breakdown = rules.score_phd(data)
        details = {
            "university": model_data.get("organization"),
            "department": model_data.get("subcategory"),
            "funding_status": model_data.get("funding_status") or "unclear",
            "funding_proof": _snippet(model_data, "funding_proof"),
            "email_application_possible": "yes" if model_data.get("email_found") else "unclear",
            "application_email": model_data.get("email_found"),
            "email_proof": _snippet(model_data, "email_proof"),
        }
    elif vote_category == "job":
        breakdown = rules.score_job(data)
        details = {
            "company": model_data.get("organization"),
            "skills_required": model_data.get("required_skills") or [],
            "language_requirements": model_data.get("language_requirements") or [],
            "email_application_possible": "yes" if model_data.get("email_found") else "unclear",
            "application_email": model_data.get("email_found"),
            "why_fits_profile": model_data.get("reason"),
        }
    elif vote_category == "remote_job":
        breakdown = rules.score_remote_job(data)
        details = {
            "company": model_data.get("organization"),
            "remote_restriction": model_data.get("remote_status") or "unclear",
            "remote_proof": _snippet(model_data, "remote_proof"),
            "skills": model_data.get("required_skills") or [],
        }
    else:
        breakdown = ScoreBreakdown(final_score=20)
        details = {}

    reliability = float((source or {}).get("health_score") or 50)
    breakdown.source_reliability_score = reliability

    opp = {
        "title": model_data.get("title") or cleaned_post.get("title") or "Untitled opportunity",
        "summary": model_data.get("summary"),
        "category": vote_category,
        "subcategory": model_data.get("subcategory"),
        "country": model_data.get("country"),
        "city": model_data.get("city"),
        "organization": model_data.get("organization"),
        "source_url": source_url,
        "canonical_url": source_url,
        "original_url": source_url,
        "application_method": model_data.get("application_method") or "unknown",
        "contact_method": model_data.get("contact_method") or "unknown",
        "contact_email": model_data.get("email_found"),
        "contact_phone": model_data.get("phone_found"),
        "posted_date": _parse_date(model_data.get("posted_date")),
        "deadline": _parse_date(model_data.get("deadline")),
        "status": vote_status,
        "final_score": breakdown.final_score,
        "confidence_score": confidence,
        "url_hash": uh,
        "content_hash": ch,
        "language": cleaned_post.get("language"),
    }
    return opp, details, breakdown


def score_to_row(breakdown: ScoreBreakdown) -> dict[str, Any]:
    d = asdict(breakdown)
    return {k: v for k, v in d.items() if k != "final_score" or True}


def _snippet(data: dict[str, Any], ev_type: str) -> str | None:
    for ev in data.get("evidence") or []:
        if (ev.get("type") or ev.get("evidence_type")) == ev_type:
            return ev.get("snippet")
    return None


def _parse_date(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text
    return None


def _evidence_score(data: dict[str, Any]) -> float:
    ev = data.get("evidence") or []
    return min(100, 40 + len(ev) * 15)
