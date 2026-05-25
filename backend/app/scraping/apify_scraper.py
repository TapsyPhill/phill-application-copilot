"""Optional Apify actor integration for specialized sources."""

from __future__ import annotations

from typing import Any

from backend.app.config.settings import get_settings
from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult


class ApifyScraper(BaseScraper):
    name = "apify"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        settings = get_settings()
        actor_id = (source_config or {}).get("apify_actor_id")
        if not settings.apify_api_token or not actor_id:
            return ScrapeResult(
                success=False,
                source_url=url,
                scraper_name=self.name,
                error="Apify not configured or apify_actor_id missing on source",
            )
        try:
            from apify_client import ApifyClient

            client = ApifyClient(settings.apify_api_token)
            run = client.actor(actor_id).call(run_input={"startUrls": [{"url": url}]})
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            text = "\n".join(str(item) for item in items[:20])
            return ScrapeResult(
                success=bool(items),
                source_url=url,
                scraper_name=self.name,
                text=text,
                metadata={"item_count": len(items)},
            )
        except Exception as exc:
            return self.handle_error(url, exc)
