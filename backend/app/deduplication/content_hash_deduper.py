"""Content hash deduplication."""

from __future__ import annotations

import hashlib
import re


def content_hash(title: str | None, body: str) -> str:
    normalized = re.sub(r"\s+", " ", (title or "") + " " + body).strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()
