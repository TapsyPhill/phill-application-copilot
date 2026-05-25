"""ScrapingBee backup for difficult pages — quota-conscious."""

from __future__ import annotations

from typing import Any

import httpx

from backend.app.config.settings import get_settings
from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult


class ScrapingBeeScraper(BaseScraper):
    name = "scrapingbee"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        settings = get_settings()
        if not settings.scrapingbee_api_key:
            return ScrapeResult(
                success=False,
                source_url=url,
                scraper_name=self.name,
                error="SCRAPINGBEE_API_KEY not configured",
            )
        try:
            resp = httpx.get(
                "https://app.scrapingbee.com/api/v1/",
                params={
                    "api_key": settings.scrapingbee_api_key,
                    "url": url,
                    "render_js": str(
                        (source_config or {}).get("requires_js", False)
                    ).lower(),
                },
                timeout=90.0,
            )
            resp.raise_for_status()
            return ScrapeResult(
                success=True,
                source_url=url,
                scraper_name=self.name,
                html=resp.text,
                text=resp.text,
                metadata={"status_code": resp.status_code},
            )
        except Exception as exc:
            return self.handle_error(url, exc)
