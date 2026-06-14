#!/usr/bin/env python3
"""Daily discovery + scrape pipeline entrypoint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.pipeline.cleaning_runner import CleaningRunner
from backend.app.pipeline.dedup_runner import DedupRunner
from backend.app.pipeline.discovery_runner import DiscoveryRunner
from backend.app.pipeline.scrape_runner import ScrapeRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    settings = get_settings()
    max_urls = settings.scrape_max_urls
    max_terms = settings.discovery_max_terms
    max_sources = settings.discovery_max_sources

    repo = SupabaseRepo.from_settings()
    logger.info("daily_scrape_started")

    discovered = DiscoveryRunner(repo, max_terms=max_terms, max_sources=max_sources).run()
    scraped = ScrapeRunner(repo, max_urls=max_urls).run()
    cleaned = CleaningRunner(repo).run()
    merged = DedupRunner(repo).run()

    repo.audit(
        "daily_scrape_finished",
        details={"discovered": discovered, "scraped": scraped, "cleaned": cleaned, "merged": merged},
    )
    logger.info(
        "daily_scrape_finished",
        extra={"discovered": discovered, "scraped": scraped, "cleaned": cleaned, "merged": merged},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
