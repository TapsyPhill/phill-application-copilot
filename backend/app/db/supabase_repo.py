"""Supabase repository — batch pipeline and dashboard persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import structlog
from supabase import Client, create_client

from backend.app.config.settings import get_settings
from backend.app.deduplication.url_deduper import url_hash as compute_url_hash

logger = structlog.get_logger(__name__)


def _utc_day_start_iso() -> str:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


class SupabaseRepo:
    def __init__(self, client: Client) -> None:
        self._client = client

    @classmethod
    def from_settings(cls) -> SupabaseRepo:
        s = get_settings()
        if not s.supabase_url or not s.supabase_key_secret:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY required")
        return cls(create_client(s.supabase_url, s.supabase_key_secret))

    def audit(self, action: str, entity_type: str | None = None, entity_id: str | None = None, details: dict | None = None) -> None:
        self._client.table("audit_logs").insert(
            {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details or {},
            }
        ).execute()

    def log_api_usage(self, service_name: str, units: float = 1, metadata: dict | None = None) -> None:
        self._client.table("api_usage_logs").insert(
            {
                "service_name": service_name,
                "units_used": units,
                "metadata": metadata or {},
            }
        ).execute()

    # --- Sources ---

    def get_enabled_sources(self, limit: int = 50) -> list[dict[str, Any]]:
        r = (
            self._client.table("sources")
            .select("*")
            .eq("enabled", True)
            .order("priority", desc=True)
            .limit(limit)
            .execute()
        )
        return r.data or []

    def get_search_terms(self, source_id: str | None = None) -> list[dict[str, Any]]:
        q = self._client.table("source_search_terms").select("*").eq("enabled", True)
        if source_id:
            q = q.eq("source_id", source_id)
        return (q.limit(500).execute().data) or []

    # --- Discovery ---

    def upsert_discovered_url(
        self,
        url: str,
        *,
        source_id: str | None,
        discovery_method: str,
        search_term: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any] | None:
        uh = compute_url_hash(url)
        payload = {
            "url": url,
            "url_hash": uh,
            "source_id": source_id,
            "discovery_method": discovery_method,
            "search_term": search_term,
            "status": "pending",
            "metadata": metadata or {},
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        }
        r = self._client.table("discovered_urls").upsert(payload, on_conflict="url_hash").execute()
        return (r.data or [None])[0]

    def get_pending_urls(self, limit: int = 30) -> list[dict[str, Any]]:
        r = (
            self._client.table("discovered_urls")
            .select("*, sources(*)")
            .eq("status", "pending")
            .order("first_seen_at")
            .limit(limit * 4)
            .execute()
        )
        rows = r.data or []
        priority = {"phd": 0, "job": 1, "remote_job": 2, "client_lead": 3}

        def sort_key(row: dict[str, Any]) -> tuple[int, str]:
            source = row.get("sources") or {}
            metadata = row.get("metadata") or {}
            section = source.get("target_section") or metadata.get("target_section") or ""
            return (priority.get(section, 4), row.get("first_seen_at") or "")

        return sorted(rows, key=sort_key)[:limit]

    def mark_discovered_url(self, url_hash: str, status: str) -> None:
        self._client.table("discovered_urls").update(
            {"status": status, "last_seen_at": datetime.now(timezone.utc).isoformat()}
        ).eq(
            "url_hash", url_hash
        ).execute()

    # --- Raw / cleaned ---

    def insert_raw_post(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        r = self._client.table("raw_posts").insert(payload).execute()
        return (r.data or [None])[0]

    def get_raw_posts_without_cleaned(self, limit: int = 50) -> list[dict[str, Any]]:
        r = (
            self._client.table("raw_posts")
            .select("*")
            .order("scraped_at", desc=True)
            .limit(limit * 3)
            .execute()
        )
        raw = r.data or []
        if not raw:
            return []
        ids = [row["id"] for row in raw]
        cleaned = (
            self._client.table("cleaned_posts")
            .select("raw_post_id")
            .in_("raw_post_id", ids)
            .execute()
        ).data or []
        done = {c["raw_post_id"] for c in cleaned}
        return [row for row in raw if row["id"] not in done][:limit]

    def insert_cleaned_post(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        r = self._client.table("cleaned_posts").insert(payload).execute()
        return (r.data or [None])[0]

    def get_cleaned_posts_for_analysis(self, limit: int = 25) -> list[dict[str, Any]]:
        r = (
            self._client.table("cleaned_posts")
            .select("*")
            .eq("quality_status", "passed")
            .order("cleaned_at", desc=True)
            .limit(limit * 2)
            .execute()
        )
        posts = r.data or []
        out: list[dict[str, Any]] = []
        for post in posts:
            ch = post.get("content_hash")
            if not ch:
                continue
            existing = (
                self._client.table("opportunity_ai_analysis")
                .select("id")
                .eq("content_hash", ch)
                .limit(1)
                .execute()
            ).data
            if not existing:
                out.append(post)
            if len(out) >= limit:
                break
        return out

    # --- Opportunities ---

    def get_opportunity_by_url_hash(self, url_hash: str) -> dict[str, Any] | None:
        r = (
            self._client.table("opportunities")
            .select("*")
            .eq("url_hash", url_hash)
            .limit(1)
            .execute()
        )
        data = r.data or []
        return data[0] if data else None

    def upsert_opportunity(self, payload: dict[str, Any]) -> dict[str, Any]:
        uh = payload["url_hash"]
        existing = self.get_opportunity_by_url_hash(uh)
        if existing:
            preserve = {
                k: existing[k]
                for k in ("viewed", "viewed_at", "status", "open_count")
                if k in existing and existing.get(k) is not None
            }
            if existing.get("viewed"):
                preserve["viewed"] = True
            if existing.get("status") in ("saved", "rejected", "reviewing", "stage2_ready", "checked_out", "archived"):
                preserve["status"] = existing["status"]
            payload = {**payload, **preserve, "times_seen": (existing.get("times_seen") or 1) + 1}
            r = self._client.table("opportunities").update(payload).eq("id", existing["id"]).execute()
            row = (r.data or [existing])[0]
            return row if isinstance(row, dict) else existing
        r = self._client.table("opportunities").insert(payload).execute()
        return (r.data or [payload])[0]

    def insert_evidence_rows(self, opportunity_id: str, evidence: list[dict[str, Any]], model_name: str) -> None:
        rows = []
        for ev in evidence:
            if not ev.get("snippet"):
                continue
            rows.append(
                {
                    "opportunity_id": opportunity_id,
                    "evidence_type": ev.get("type") or ev.get("evidence_type") or "classification_reason",
                    "snippet": ev["snippet"][:2000],
                    "model_name": model_name,
                    "confidence": ev.get("confidence"),
                }
            )
        if rows:
            self._client.table("opportunity_evidence").insert(rows).execute()

    def replace_opportunity_contacts(self, opportunity_id: str, contacts: list[dict[str, Any]]) -> None:
        self._client.table("opportunity_contacts").delete().eq("opportunity_id", opportunity_id).execute()
        rows = []
        for contact in contacts:
            contact_type = contact.get("contact_type")
            contact_value = contact.get("contact_value")
            if not contact_type or not contact_value:
                continue
            rows.append(
                {
                    "opportunity_id": opportunity_id,
                    "contact_type": contact_type,
                    "contact_value": contact_value,
                    "proof_snippet": contact.get("proof_snippet"),
                    "confidence": contact.get("confidence"),
                }
            )
        if rows:
            self._client.table("opportunity_contacts").insert(rows).execute()

    def insert_score_row(self, opportunity_id: str, breakdown: dict[str, Any]) -> None:
        self._client.table("opportunity_scores").insert(
            {"opportunity_id": opportunity_id, **breakdown, "scoring_version": "stage1_v1"}
        ).execute()

    def insert_ai_analysis(self, opportunity_id: str, cleaned_post_id: str | None, model_output: dict[str, Any]) -> None:
        self._client.table("opportunity_ai_analysis").insert(
            {
                "opportunity_id": opportunity_id,
                "cleaned_post_id": cleaned_post_id,
                "model_name": model_output.get("model_name", "unknown"),
                "is_relevant": model_output.get("is_relevant"),
                "category": model_output.get("category"),
                "subcategory": model_output.get("subcategory"),
                "fit_score": model_output.get("fit_score"),
                "confidence": model_output.get("confidence"),
                "reason": model_output.get("reason"),
                "raw_json": model_output,
                "content_hash": model_output.get("content_hash"),
            }
        ).execute()

    def insert_vote(self, opportunity_id: str, vote: dict[str, Any]) -> None:
        self._client.table("opportunity_votes").insert(
            {
                "opportunity_id": opportunity_id,
                "vote_round": "stage1_classify",
                "models_used": vote.get("models_used", []),
                "agreement_ratio": vote.get("agreement_ratio"),
                "final_category": vote.get("final_category"),
                "final_status": vote.get("final_status"),
                "final_confidence": vote.get("final_confidence"),
                "decision_json": vote,
            }
        ).execute()

    def upsert_category_details(self, category: str, opportunity_id: str, data: dict[str, Any]) -> None:
        table_map = {
            "client_lead": "client_lead_details",
            "phd": "phd_opportunity_details",
            "job": "job_opportunity_details",
            "remote_job": "remote_job_details",
        }
        table = table_map.get(category)
        if not table:
            return
        payload = {"opportunity_id": opportunity_id, **data}
        self._client.table(table).upsert(payload).execute()

    def get_profile_context(self) -> str:
        profiles = (self._client.table("user_profiles").select("*").limit(1).execute()).data or []
        if not profiles:
            return ""
        pid = profiles[0]["id"]
        skills = (
            self._client.table("profile_skills").select("skill_name,skill_category,proficiency").eq("profile_id", pid).execute()
        ).data or []
        prefs = (
            self._client.table("profile_preferences").select("preference_key,preference_value").eq("profile_id", pid).execute()
        ).data or []
        chunks = (
            self._client.table("profile_knowledge_chunks")
            .select("title,content")
            .eq("profile_id", pid)
            .limit(12)
            .execute()
        ).data or []
        lines = [
            f"Name: {profiles[0].get('display_name')}",
            f"Headline: {profiles[0].get('headline')}",
            f"Location: {profiles[0].get('location_city')}, {profiles[0].get('location_country')}",
            f"Summary: {profiles[0].get('summary')}",
            "Skills: " + ", ".join(s["skill_name"] for s in skills),
            "Preferences: " + str(prefs),
        ]
        for c in chunks:
            lines.append(f"{c.get('title') or 'chunk'}: {(c.get('content') or '')[:400]}")
        return "\n".join(lines)

    def count_opportunities_today(self) -> int:
        r = self._client.table("opportunities").select("id", count="exact").gte(
            "first_seen_at", _utc_day_start_iso()
        ).execute()
        return r.count or 0

    def cloud_calls_today(self) -> int:
        r = (
            self._client.table("api_usage_logs")
            .select("id", count="exact")
            .gte("created_at", _utc_day_start_iso())
            .in_("service_name", ["gemini", "groq", "openai", "anthropic"])
            .execute()
        )
        return r.count or 0


@lru_cache
def get_repo() -> SupabaseRepo:
    return SupabaseRepo.from_settings()
