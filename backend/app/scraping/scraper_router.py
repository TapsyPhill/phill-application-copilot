"""Route URLs to the best scraper with ordered fallback."""

from __future__ import annotations

from typing import Any

import structlog

from backend.app.scraping.apify_scraper import ApifyScraper
from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult
from backend.app.scraping.firecrawl_scraper import FirecrawlScraper
from backend.app.scraping.playwright_scraper import PlaywrightScraper
from backend.app.scraping.requests_bs4_scraper import RequestsBs4Scraper
from backend.app.scraping.rss_scraper import RssScraper
from backend.app.scraping.scrapingbee_scraper import ScrapingBeeScraper

logger = structlog.get_logger(__name__)

PREFERENCE_MAP: dict[str, type[BaseScraper]] = {
    "requests_bs4": RequestsBs4Scraper,
    "playwright": PlaywrightScraper,
    "rss": RssScraper,
    "firecrawl": FirecrawlScraper,
    "scrapingbee": ScrapingBeeScraper,
    "apify": ApifyScraper,
}

DEFAULT_FALLBACK_CHAIN = [
    "requests_bs4",
    "firecrawl",
    "playwright",
    "scrapingbee",
]


class ScraperRouter:
    """Select scraper from source preference; fall back on failure."""

    def __init__(self) -> None:
        self._instances: dict[str, BaseScraper] = {}

    def _get(self, name: str) -> BaseScraper:
        if name not in self._instances:
            cls = PREFERENCE_MAP.get(name, RequestsBs4Scraper)
            self._instances[name] = cls()
        return self._instances[name]

    def scrape(
        self, url: str, source_config: dict[str, Any] | None = None
    ) -> ScrapeResult:
        config = source_config or {}
        preference = config.get("scraping_method_preference", "requests_bs4")
        chain = [preference] + [m for m in DEFAULT_FALLBACK_CHAIN if m != preference]

        last_result: ScrapeResult | None = None
        for method in chain:
            if method not in PREFERENCE_MAP:
                continue
            scraper = self._get(method)
            scraper.rate_limit(config)
            result = scraper.scrape_url(url, config)
            result = scraper.normalize_result(result)
            if result.success:
                logger.info("scrape_ok", url=url, scraper=method)
                return result
            last_result = result
            logger.info("scrape_fallback", url=url, failed=method)

        return last_result or ScrapeResult(
            success=False,
            source_url=url,
            scraper_name="none",
            error="All scrapers failed",
        )
