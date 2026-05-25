"""Merge duplicate opportunities by url_hash and content_hash."""

from __future__ import annotations

import structlog

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.deduplication.duplicate_merge_service import DuplicateMergeService

logger = structlog.get_logger(__name__)


class DedupRunner:
    def __init__(self, repo: SupabaseRepo) -> None:
        self._repo = repo
        self._merge = DuplicateMergeService()

    def run(self) -> int:
        merged = 0
        opps = (
            self._repo._client.table("opportunities")
            .select("*")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        ).data or []

        by_content: dict[str, list[dict]] = {}
        for o in opps:
            ch = o.get("content_hash")
            if ch:
                by_content.setdefault(ch, []).append(o)

        for _ch, group in by_content.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: x.get("final_score") or 0, reverse=True)
            primary, *dupes = group
            for dup in dupes:
                payload = self._merge.build_update_payload(primary, dup, "content_hash")
                self._repo._client.table("opportunities").update(payload).eq("id", primary["id"]).execute()
                self._repo._client.table("opportunities").update(
                    {"status": "archived"}
                ).eq("id", dup["id"]).execute()
                self._repo._client.table("opportunity_duplicates").insert(
                    {
                        "primary_opportunity_id": primary["id"],
                        "duplicate_opportunity_id": dup["id"],
                        "match_type": "content_hash",
                        "similarity_score": 1.0,
                    }
                ).execute()
                merged += 1

        self._repo.audit("dedup_complete", details={"merged": merged})
        logger.info("dedup_complete", merged=merged)
        return merged
