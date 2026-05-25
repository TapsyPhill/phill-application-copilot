"""Normalize raw scrape output into cleaned post text."""

from __future__ import annotations

import re
from html import unescape

from bs4 import BeautifulSoup


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def clean_raw_post(raw: dict) -> tuple[str | None, str]:
    title = raw.get("metadata", {}).get("title") if isinstance(raw.get("metadata"), dict) else None
    body = raw.get("raw_text") or ""
    if not body and raw.get("raw_html"):
        body = html_to_text(raw["raw_html"])
    if not body and raw.get("raw_markdown"):
        body = raw["raw_markdown"]
    if not title and body:
        first = body.split("\n", 1)[0].strip()
        if len(first) < 200:
            title = first
    return title, body
