"""Simple HTTP + BeautifulSoup scraper for static public pages."""

from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup

from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult

USER_AGENT = (
    "OpportunityCommandCenter/1.0 (+https://github.com/TapsyPhill/phill-application-copilot)"
)


class RequestsBs4Scraper(BaseScraper):
    name = "requests_bs4"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        try:
            resp = requests.get(
                url,
                timeout=30,
                headers={"User-Agent": USER_AGENT},
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            title = soup.title.string.strip() if soup.title and soup.title.string else None
            text = soup.get_text("\n", strip=True)
            links = [a["href"] for a in soup.find_all("a", href=True)][:200]
            return ScrapeResult(
                success=True,
                source_url=url,
                scraper_name=self.name,
                title=title,
                text=text,
                html=resp.text,
                links=links,
                metadata={"status_code": resp.status_code},
            )
        except Exception as exc:
            return self.handle_error(url, exc)
