"""Firecrawl API — clean Markdown for AI analysis."""

from __future__ import annotations

from typing import Any

from backend.app.config.settings import get_settings
from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult


class FirecrawlScraper(BaseScraper):
    name = "firecrawl"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        settings = get_settings()
        if not settings.firecrawl_api_key:
            return ScrapeResult(
                success=False,
                source_url=url,
                scraper_name=self.name,
                error="FIRECRAWL_API_KEY not configured",
            )
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=settings.firecrawl_api_key)
            doc = app.scrape_url(url, formats=["markdown", "html"])
            data = doc if isinstance(doc, dict) else getattr(doc, "data", {}) or {}
            md = data.get("markdown") or ""
            html = data.get("html") or ""
            meta = data.get("metadata") or {}
            return ScrapeResult(
                success=bool(md or html),
                source_url=url,
                scraper_name=self.name,
                title=meta.get("title"),
                text=md or None,
                markdown=md or None,
                html=html or None,
                metadata=meta,
            )
        except Exception as exc:
            return self.handle_error(url, exc)
