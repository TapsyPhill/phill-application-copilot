"""RSS/Atom feed parser — stores entries as discovered URL candidates."""

from __future__ import annotations

from typing import Any

import feedparser

from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult


class RssScraper(BaseScraper):
    name = "rss"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        try:
            feed = feedparser.parse(url)
            entries = []
            for entry in feed.entries[:50]:
                entries.append(
                    {
                        "title": entry.get("title"),
                        "link": entry.get("link"),
                        "summary": entry.get("summary"),
                        "published": entry.get("published"),
                    }
                )
            text = "\n\n".join(
                f"{e.get('title', '')}\n{e.get('link', '')}\n{e.get('summary', '')}"
                for e in entries
            )
            links = [e["link"] for e in entries if e.get("link")]
            return ScrapeResult(
                success=True,
                source_url=url,
                scraper_name=self.name,
                title=feed.feed.get("title"),
                text=text,
                links=links,
                metadata={"entry_count": len(entries)},
            )
        except Exception as exc:
            return self.handle_error(url, exc)
