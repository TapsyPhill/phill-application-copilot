#!/usr/bin/env python3
"""Run AI classification, evidence extraction, scoring, and opportunity upsert."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.pipeline.ai_runner import AiRunner
from backend.app.pipeline.dedup_runner import DedupRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    repo = SupabaseRepo.from_settings()
    limit = get_settings().ai_analysis_limit
    processed = AiRunner(repo, limit=limit).run()
    merged = DedupRunner(repo).run()
    logger.info("ai_analysis_finished", extra={"processed": processed, "merged": merged})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
