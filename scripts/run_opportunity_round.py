#!/usr/bin/env python3
"""Run one full opportunity selection round now."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.pipeline.ai_runner import AiRunner
from backend.app.pipeline.cleaning_runner import CleaningRunner
from backend.app.pipeline.dedup_runner import DedupRunner
from backend.app.pipeline.discovery_runner import DiscoveryRunner
from backend.app.pipeline.scrape_runner import ScrapeRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    settings = get_settings()
    repo = SupabaseRepo.from_settings()
    logger.info("opportunity_round_started")

    discovered = DiscoveryRunner(
        repo,
        max_terms=settings.discovery_max_terms,
        max_sources=settings.discovery_max_sources,
    ).run()
    scraped = ScrapeRunner(repo, max_urls=settings.scrape_max_urls).run()
    cleaned = CleaningRunner(repo).run()
    merged_before_ai = DedupRunner(repo).run()
    processed = AiRunner(repo, limit=settings.ai_analysis_limit).run()
    merged_after_ai = DedupRunner(repo).run()

    details = {
        "discovered": discovered,
        "scraped": scraped,
        "cleaned": cleaned,
        "merged_before_ai": merged_before_ai,
        "processed": processed,
        "merged_after_ai": merged_after_ai,
    }
    repo.audit("opportunity_round_finished", details=details)
    logger.info("opportunity_round_finished", extra=details)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
