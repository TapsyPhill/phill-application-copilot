#!/usr/bin/env python3
"""Export key Supabase tables to data/exports/."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABLES = ["opportunities", "sources", "opportunity_evidence", "user_profiles", "cleaned_posts"]


def main() -> int:
    repo = SupabaseRepo.from_settings()
    out_dir = ROOT / "data" / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest: dict = {"exported_at": stamp, "tables": {}}

    for table in TABLES:
        rows = repo._client.table(table).select("*").limit(5000).execute().data or []
        manifest["tables"][table] = len(rows)
        manifest[table] = rows

    path = out_dir / f"backup_{stamp}.json"
    path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    logger.info("backup_written", extra={"path": str(path), "tables": manifest["tables"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
