"""Clean raw posts, run quality gate, persist cleaned_posts."""

from __future__ import annotations

import structlog

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.deduplication.content_hash_deduper import content_hash
from backend.app.deduplication.url_deduper import url_hash
from backend.app.ingestion.data_quality_gate import DataQualityGate
from backend.app.ingestion.text_cleaner import clean_raw_post

logger = structlog.get_logger(__name__)


class CleaningRunner:
    def __init__(self, repo: SupabaseRepo, limit: int = 40) -> None:
        self._repo = repo
        self._gate = DataQualityGate()
        self._limit = limit

    def run(self) -> int:
        raw_posts = self._repo.get_raw_posts_without_cleaned(limit=self._limit)
        created = 0
        for raw in raw_posts:
            title, body = clean_raw_post(raw)
            quality = self._gate.evaluate(title, body, raw["source_url"])
            ch = content_hash(title, body)
            uh = raw.get("url_hash") or url_hash(raw["source_url"])
            self._repo.insert_cleaned_post(
                {
                    "raw_post_id": raw["id"],
                    "source_url": raw["source_url"],
                    "url_hash": uh,
                    "content_hash": ch,
                    "title": title,
                    "body_text": body,
                    "quality_score": quality.quality_score,
                    "quality_status": quality.quality_status,
                    "rejection_reason": quality.rejection_reason or quality.manual_review_reason,
                }
            )
            created += 1
        self._repo.audit("cleaning_complete", details={"created": created})
        logger.info("cleaning_complete", created=created)
        return created
