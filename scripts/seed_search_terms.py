#!/usr/bin/env python3
"""Load search term JSON files into source_search_terms."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TERMS_DIR = ROOT / "backend" / "app" / "sources" / "search_terms"


def main() -> int:
    repo = SupabaseRepo.from_settings()
    client = repo._client
    client.table("source_search_terms").delete().is_("source_id", "null").execute()
    total = 0
    for path in sorted(TERMS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        section = data.get("target_section", "client_lead")
        lang = data.get("language")
        for term in data.get("terms", []):
            text = term if isinstance(term, str) else term.get("term")
            if not text:
                continue
            client.table("source_search_terms").insert(
                {
                    "term": text,
                    "language": lang,
                    "target_section": section,
                    "enabled": True,
                }
            ).execute()
            total += 1
        logger.info("seeded_terms_file", extra={"file": path.name})
    logger.info("search_terms_complete", extra={"count": total})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
