"""Base scraper interface and shared result types."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ScrapeResult:
    """Normalized output from any scraper implementation."""

    success: bool
    source_url: str
    scraper_name: str
    title: str | None = None
    text: str | None = None
    markdown: str | None = None
    html: str | None = None
    links: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseScraper(ABC):
    """Common contract for all scraping backends."""

    name: str = "base"

    def __init__(self, rate_limit_seconds: float = 1.0) -> None:
        self._rate_limit_seconds = rate_limit_seconds
        self._last_request_at: float = 0.0

    def rate_limit(self, source: dict[str, Any] | None = None) -> None:
        """Simple per-scraper throttle."""
        priority = (source or {}).get("priority", 5)
        delay = max(0.5, self._rate_limit_seconds * (11 - min(priority, 10)) / 5)
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request_at = time.monotonic()

    @abstractmethod
    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        ...

    def search_source(
        self, source: dict[str, Any], terms: list[str]
    ) -> list[ScrapeResult]:
        """Optional search within a source. Override when supports search."""
        return []

    def normalize_result(self, result: ScrapeResult) -> ScrapeResult:
        if result.text:
            result.text = "\n".join(line.strip() for line in result.text.splitlines() if line.strip())
        return result

    def handle_error(self, url: str, error: Exception) -> ScrapeResult:
        logger.warning("scrape_failed", url=url, scraper=self.name, error=str(error))
        return ScrapeResult(
            success=False,
            source_url=url,
            scraper_name=self.name,
            error=str(error),
        )
