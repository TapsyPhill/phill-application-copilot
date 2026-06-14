#!/usr/bin/env python3
"""Full Stage 1 smoke: seed → discover → scrape → clean → dedup → AI → audit counts."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _run(script: str, extra_env: dict | None = None) -> None:
    env = {**os.environ, **(extra_env or {})}
    logger.info("running %s", script)
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, env=env, check=True)


def main() -> int:
    os.environ.setdefault("DISCOVERY_MAX_TERMS", "18")
    os.environ.setdefault("DISCOVERY_MAX_SOURCES", "30")
    os.environ.setdefault("SCRAPE_MAX_URLS", "30")

    _run("seed_sources.py")
    _run("seed_search_terms.py")
    _run("run_daily_scrape.py")
    _run("run_ai_analysis.py")
    _run("run_deduplication.py")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_pipeline_quality.py")], cwd=ROOT, check=False)

    from backend.app.db.supabase_repo import get_repo

    c = get_repo()._client
    opps = c.table("opportunities").select("category").execute().data or []
    by_cat: dict[str, int] = {}
    for o in opps:
        cat = o.get("category") or "unknown"
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print("\n=== OPPORTUNITIES BY CATEGORY ===")
    print(json.dumps(by_cat, indent=2))
    print(f"TOTAL: {len(opps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
