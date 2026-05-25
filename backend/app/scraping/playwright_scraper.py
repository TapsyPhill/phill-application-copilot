"""Playwright scraper for JS-rendered public pages. Does not bypass login/captcha."""

from __future__ import annotations

from typing import Any

from backend.app.scraping.base_scraper import BaseScraper, ScrapeResult


class PlaywrightScraper(BaseScraper):
    name = "playwright"

    def scrape_url(self, url: str, source_config: dict[str, Any] | None = None) -> ScrapeResult:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=60000)
                if self._detect_blocked(page.content()):
                    browser.close()
                    return ScrapeResult(
                        success=False,
                        source_url=url,
                        scraper_name=self.name,
                        error="Login or captcha detected — manual review required",
                    )
                title = page.title()
                text = page.inner_text("body")
                html = page.content()
                links = page.eval_on_selector_all(
                    "a[href]", "elements => elements.map(e => e.href)"
                )[:200]
                browser.close()
            return ScrapeResult(
                success=True,
                source_url=url,
                scraper_name=self.name,
                title=title,
                text=text,
                html=html,
                links=links,
            )
        except Exception as exc:
            return self.handle_error(url, exc)

    @staticmethod
    def _detect_blocked(html: str) -> bool:
        markers = ("captcha", "sign in", "log in", "login required", "access denied")
        lower = html.lower()
        return any(m in lower for m in markers)
