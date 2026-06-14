"""Extract same-domain links from source listing pages for discovery."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

_SKIP_EXTENSIONS = re.compile(r"\.(jpg|jpeg|png|gif|svg|css|js|pdf|zip)(\?|$)", re.I)
_SKIP_PATHS = re.compile(r"(login|signin|signup|register|cart|privacy|impressum|cookie|/api/)", re.I)

_SECTION_TERMS = {
    "client_lead": (
        "hilfe",
        "gesucht",
        "auftrag",
        "projekt",
        "freelance",
        "freelancer",
        "entwickler",
        "wordpress",
        "website",
        "webdesign",
        "automation",
        "integration",
    ),
    "phd": ("phd", "doctoral", "doctorand", "promotion", "stipend", "funded", "researcher"),
    "job": ("job", "career", "stellen", "position", "data-scientist", "engineer", "analyst"),
    "remote_job": ("remote", "work-from-anywhere", "worldwide", "distributed", "engineer", "developer"),
}


def extract_listing_links(
    page_url: str,
    base_domain: str,
    *,
    max_links: int = 8,
    target_section: str | None = None,
    timeout: float = 15.0,
) -> list[str]:
    """Return absolute URLs on the same domain, preferring post-like paths."""
    domain = base_domain.lstrip(".").lower()
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.get(
                page_url,
                headers={"User-Agent": "OCC-Stage1-Bot/1.0 (+discovery)"},
            )
            r.raise_for_status()
            html = r.text
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    candidates: list[tuple[int, str]] = []
    terms = _SECTION_TERMS.get(target_section or "", ())

    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        absolute = urljoin(page_url, href)
        parsed = urlparse(absolute)
        if domain not in (parsed.netloc or "").lower():
            continue
        if _SKIP_EXTENSIONS.search(parsed.path) or _SKIP_PATHS.search(parsed.path):
            continue
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        if parsed.query:
            clean = f"{clean}?{parsed.query}"
        if clean in seen or clean == page_url.rstrip("/"):
            continue
        seen.add(clean)
        text = f"{a.get_text(' ', strip=True)} {clean}".lower()
        score = sum(1 for term in terms if term in text)
        if terms and score == 0:
            continue
        candidates.append((score, clean))

    # Prefer links that look section-relevant, then deeper paths (likely detail pages).
    candidates.sort(key=lambda item: (-item[0], -len(urlparse(item[1]).path), item[1]))
    return [url for _, url in candidates[:max_links]]
