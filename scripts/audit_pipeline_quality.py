#!/usr/bin/env python3
"""Audit Stage 1 pipeline data quality across all stages (read-only)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import get_repo


def _count(client, table: str, **filters) -> int:
    q = client.table(table).select("id", count="exact")
    for k, v in filters.items():
        q = q.eq(k, v)
    r = q.limit(1).execute()
    return r.count or 0


def _sample(client, table: str, select: str, limit: int = 5, order: str | None = None):
    q = client.table(table).select(select).limit(limit)
    if order:
        q = q.order(order, desc=True)
    return (q.execute().data or [])


def _pct(n: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{100 * n / total:.0f}%"


def main() -> int:
    repo = get_repo()
    c = repo._client
    issues: list[str] = []
    report: dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat()}

    # --- Sources ---
    sources_total = _count(c, "sources")
    sources_enabled = _count(c, "sources", enabled=True)
    report["sources"] = {"total": sources_total, "enabled": sources_enabled}
    if sources_total < 10:
        issues.append(f"Low source count ({sources_total}); expected seeded registry")

    # --- Discovery ---
    disc_total = _count(c, "discovered_urls")
    disc_pending = _count(c, "discovered_urls", status="pending")
    disc_scraped = _count(c, "discovered_urls", status="scraped")
    disc_failed = _count(c, "discovered_urls", status="failed")
    report["discovered_urls"] = {
        "total": disc_total,
        "pending": disc_pending,
        "scraped": disc_scraped,
        "failed": disc_failed,
    }
    if disc_total == 0:
        issues.append("No discovered URLs — discovery may not have run")

    # --- Raw posts ---
    raw_total = _count(c, "raw_posts")
    raw_samples = _sample(
        c,
        "raw_posts",
        "id,source_url,raw_text,scraper_used,created_at,metadata",
        limit=20,
        order="created_at",
    )
    raw_with_title = sum(
        1
        for r in raw_samples
        if (r.get("metadata") or {}).get("title") or len((r.get("raw_text") or "").split("\n", 1)[0]) > 5
    )
    raw_with_body = sum(
        1
        for r in raw_samples
        if len((r.get("raw_text") or "").strip()) >= 100
    )
    raw_methods = Counter(r.get("scraper_used") or "unknown" for r in raw_samples)
    report["raw_posts"] = {
        "total": raw_total,
        "sample_size": len(raw_samples),
        "sample_with_title": raw_with_title,
        "sample_with_body_100plus": raw_with_body,
        "scrape_methods_in_sample": dict(raw_methods),
    }
    if raw_total == 0:
        issues.append("No raw_posts — scrape stage empty")

    # --- Cleaned posts ---
    clean_total = _count(c, "cleaned_posts")
    clean_samples = _sample(
        c,
        "cleaned_posts",
        "id,title,body_text,quality_status,content_hash,created_at",
        limit=20,
        order="created_at",
    )
    q_status = Counter(r.get("quality_status") or "unknown" for r in clean_samples)
    clean_with_text = sum(
        1 for r in clean_samples if len((r.get("body_text") or "").strip()) >= 80
    )
    report["cleaned_posts"] = {
        "total": clean_total,
        "quality_status_in_sample": dict(q_status),
        "sample_with_text_80plus": clean_with_text,
    }
    if clean_total == 0 and raw_total > 0:
        issues.append("Raw posts exist but no cleaned_posts — cleaning not run")

    # --- AI analysis ---
    ai_total = _count(c, "opportunity_ai_analysis")
    vote_total = _count(c, "opportunity_votes")
    report["ai"] = {"analysis_results": ai_total, "vote_results": vote_total}

    # --- Opportunities ---
    opp_total = _count(c, "opportunities")
    opp_samples = _sample(
        c,
        "opportunities",
        "id,title,category,subcategory,status,final_score,country,source_url,viewed,contact_email,deadline,application_method,application_status,created_at",
        limit=50,
        order="created_at",
    )
    by_cat = Counter(o.get("category") or "unknown" for o in opp_samples)
    by_status = Counter(o.get("status") or "unknown" for o in opp_samples)
    with_score = sum(1 for o in opp_samples if (o.get("final_score") or 0) > 0)
    with_url = sum(1 for o in opp_samples if (o.get("source_url") or "").startswith("http"))
    with_email = sum(1 for o in opp_samples if o.get("contact_email"))
    with_deadline = sum(1 for o in opp_samples if o.get("deadline"))
    email_apply = sum(1 for o in opp_samples if (o.get("application_method") or "").lower() == "email")
    rejected = by_status.get("rejected", 0)
    report["opportunities"] = {
        "total": opp_total,
        "by_category_in_sample": dict(by_cat),
        "by_status_in_sample": dict(by_status),
        "sample_with_score": with_score,
        "sample_with_source_url": with_url,
        "sample_with_contact_email": with_email,
        "sample_with_deadline": with_deadline,
        "sample_email_apply": email_apply,
        "rejected_in_sample": rejected,
    }
    if opp_total == 0:
        issues.append("No opportunities — AI pipeline or relevance filter may block all output")

    # --- Evidence ---
    ev_total = _count(c, "opportunity_evidence")
    contact_total = _count(c, "opportunity_contacts")
    report["evidence"] = {"total": ev_total, "contacts": contact_total}
    if opp_total > 0 and ev_total == 0:
        issues.append("Opportunities exist but no evidence rows")
    if opp_total > 0 and contact_total == 0:
        issues.append("Opportunities exist but no extracted contact rows")

    # --- Profile ---
    profile_chunks = _count(c, "profile_knowledge_chunks")
    skills = _count(c, "profile_skills")
    report["profile"] = {"knowledge_chunks": profile_chunks, "skills": skills}
    if skills == 0:
        issues.append("Profile not seeded (no profile_skills)")

    # --- API usage ---
    usage = _sample(c, "api_usage_logs", "service_name,units_used,created_at", limit=10, order="created_at")
    report["recent_api_usage"] = usage

    # --- Audit ---
    audits = _sample(c, "audit_logs", "action,created_at", limit=15, order="created_at")
    report["recent_audit_actions"] = [a.get("action") for a in audits]

    report["issues"] = issues
    report["stage1_score_estimate"] = _score_stage1(report, issues)

    print(json.dumps(report, indent=2, default=str))
    print("\n--- SUMMARY ---")
    print(f"Stage 1 completeness estimate: {report['stage1_score_estimate']}/10")
    if issues:
        print("Issues:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("No critical pipeline gaps detected in data counts.")
    return 1 if len(issues) > 3 else 0


def _score_stage1(report: dict, issues: list) -> int:
    """Heuristic 1-10 based on pipeline fullness and checklist signals."""
    score = 10
    if report["sources"]["total"] < 20:
        score -= 1
    if report["discovered_urls"]["total"] == 0:
        score -= 2
    if report["raw_posts"]["total"] == 0:
        score -= 2
    if report["cleaned_posts"]["total"] == 0:
        score -= 1
    if report["opportunities"]["total"] == 0:
        score -= 2
    if report["evidence"]["total"] == 0 and report["opportunities"]["total"] > 0:
        score -= 1
    if report["evidence"].get("contacts", 0) == 0 and report["opportunities"]["total"] > 0:
        score -= 1
    if report["profile"]["skills"] == 0:
        score -= 1
    score -= min(len(issues), 3)
    return max(1, min(10, score))


if __name__ == "__main__":
    raise SystemExit(main())
