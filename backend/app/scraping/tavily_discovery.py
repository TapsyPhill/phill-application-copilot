"""Tavily web discovery — candidate URLs only; source page is truth."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import structlog

from backend.app.config.settings import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveredLink:
    url: str
    url_hash: str
    title: str | None
    snippet: str | None
    search_term: str
    discovery_method: str = "tavily_search"


class TavilyDiscovery:
    """Search the web for candidate opportunity pages."""

    def search(self, query: str, max_results: int = 10) -> list[DiscoveredLink]:
        settings = get_settings()
        if not settings.tavily_api_key:
            logger.warning("tavily_skipped", reason="missing_api_key")
            return []
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=settings.tavily_api_key)
            response = client.search(query=query, max_results=max_results)
            results = []
            for item in response.get("results", []):
                url = item.get("url")
                if not url:
                    continue
                url_hash = hashlib.sha256(url.encode()).hexdigest()
                results.append(
                    DiscoveredLink(
                        url=url,
                        url_hash=url_hash,
                        title=item.get("title"),
                        snippet=item.get("content"),
                        search_term=query,
                    )
                )
            return results
        except Exception as exc:
            logger.error("tavily_search_failed", query=query, error=str(exc))
            return []

    def discover_for_terms(self, terms: list[str]) -> list[DiscoveredLink]:
        all_links: list[DiscoveredLink] = []
        seen: set[str] = set()
        for term in terms:
            for link in self.search(term):
                if link.url_hash not in seen:
                    seen.add(link.url_hash)
                    all_links.append(link)
        return all_links
