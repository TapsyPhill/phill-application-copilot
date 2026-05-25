#!/usr/bin/env python3
"""Clean raw_posts into cleaned_posts with quality gate."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.pipeline.cleaning_runner import CleaningRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    repo = SupabaseRepo.from_settings()
    n = CleaningRunner(repo).run()
    logger.info("cleaning_pipeline_finished", extra={"created": n})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
