#!/usr/bin/env python3
"""Run deduplication merge pass on opportunities."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.pipeline.dedup_runner import DedupRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    repo = SupabaseRepo.from_settings()
    n = DedupRunner(repo).run()
    logger.info("deduplication_finished", extra={"merged": n})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
