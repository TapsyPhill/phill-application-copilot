"""URL normalization and exact hash matching."""

from __future__ import annotations

import hashlib
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

TRACKING_PARAMS = frozenset(
    {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
)


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    query = parse_qs(parsed.query, keep_blank_values=False)
    filtered = {k: v for k, v in query.items() if k not in TRACKING_PARAMS}
    clean_query = urlencode(filtered, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, "", clean_query, "")
    )


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()
