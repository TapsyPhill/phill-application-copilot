"""Scrape pending discovered URLs and persist raw_posts."""

from __future__ import annotations

import structlog

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.deduplication.url_deduper import url_hash
from backend.app.scraping.scraper_router import ScraperRouter

logger = structlog.get_logger(__name__)


class ScrapeRunner:
    def __init__(self, repo: SupabaseRepo, max_urls: int = 20) -> None:
        self._repo = repo
        self._router = ScraperRouter()
        self._max_urls = max_urls

    def run(self) -> int:
        pending = self._repo.get_pending_urls(limit=self._max_urls)
        scraped = 0
        for row in pending:
            url = row["url"]
            source = row.get("sources") or {}
            config = {
                "scraping_method_preference": source.get("scraping_method_preference", "requests_bs4"),
                "priority": source.get("priority", 5),
            }
            result = self._router.scrape(url, config)
            uh = url_hash(url)
            if result.success:
                self._repo.insert_raw_post(
                    {
                        "source_id": row.get("source_id"),
                        "discovered_url_id": row.get("id"),
                        "source_url": url,
                        "url_hash": uh,
                        "scraper_used": result.scraper_name,
                        "raw_html": (result.html or "")[:500000],
                        "raw_text": result.text,
                        "raw_markdown": result.markdown,
                        "metadata": {
                            "title": result.title,
                            **(result.metadata or {}),
                        },
                    }
                )
                self._repo.mark_discovered_url(uh, "scraped")
                scraped += 1
            else:
                self._repo.mark_discovered_url(uh, "failed")
                self._repo._client.table("source_failures").insert(
                    {
                        "source_id": row.get("source_id"),
                        "url": url,
                        "error_type": "scrape_failed",
                        "error_message": result.error,
                        "scraper_used": result.scraper_name,
                    }
                ).execute()
        self._repo.audit("scrape_complete", details={"scraped": scraped, "attempted": len(pending)})
        logger.info("scrape_complete", scraped=scraped, attempted=len(pending))
        return scraped
