#!/usr/bin/env python3
"""Load seed source JSON files into Supabase sources table."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_DIR = ROOT / "backend" / "app" / "sources" / "seed_sources"
SEED_FILES = [
    "germany_local_client_sources.json",
    "global_client_sources.json",
    "south_africa_client_sources.json",
    "phd_sources.json",
    "job_sources.json",
    "remote_job_sources.json",
]


def load_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("sources", data if isinstance(data, list) else [])


def main() -> int:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key_secret:
        logger.error("SUPABASE_URL and SUPABASE_SECRET_KEY required")
        return 1

    from supabase import create_client

    client = create_client(settings.supabase_url, settings.supabase_key_secret)
    total = 0
    for filename in SEED_FILES:
        path = SEED_DIR / filename
        if not path.exists():
            logger.warning("missing_seed_file", extra={"file": filename})
            continue
        for row in load_json(path):
            payload = {
                k: v
                for k, v in row.items()
                if k not in ("created_at", "updated_at", "id")
            }
            payload["external_id"] = row.get("id")
            client.table("sources").upsert(payload, on_conflict="external_id").execute()
            total += 1
        logger.info("seeded_file", extra={"file": filename})
    logger.info("seed_complete", extra={"count": total})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
