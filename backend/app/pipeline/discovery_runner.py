"""Discover candidate URLs from sources and Tavily search terms."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.scraping.tavily_discovery import TavilyDiscovery

logger = structlog.get_logger(__name__)

ROOT = Path(__file__).resolve().parents[3]
SEARCH_TERMS_DIR = ROOT / "backend" / "app" / "sources" / "search_terms"


class DiscoveryRunner:
    def __init__(self, repo: SupabaseRepo, max_terms: int = 15) -> None:
        self._repo = repo
        self._tavily = TavilyDiscovery()
        self._max_terms = max_terms

    def run(self) -> int:
        count = 0
        terms = self._collect_terms()
        for term in terms[: self._max_terms]:
            links = self._tavily.search(term, max_results=5)
            self._repo.log_api_usage("tavily", units=len(links), metadata={"term": term})
            for link in links:
                self._repo.upsert_discovered_url(
                    link.url,
                    source_id=None,
                    discovery_method=link.discovery_method,
                    search_term=term,
                    metadata={"title": link.title, "snippet": link.snippet},
                )
                count += 1
        self._repo.audit("discovery_complete", details={"urls_discovered": count})
        logger.info("discovery_complete", count=count)
        return count

    def _collect_terms(self) -> list[str]:
        db_terms = [t["term"] for t in self._repo.get_search_terms() if t.get("term")]
        if db_terms:
            return db_terms
        terms: list[str] = []
        if SEARCH_TERMS_DIR.exists():
            for path in sorted(SEARCH_TERMS_DIR.glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                for item in data.get("terms", data.get("search_terms", [])):
                    if isinstance(item, str):
                        terms.append(item)
                    elif isinstance(item, dict) and item.get("term"):
                        terms.append(item["term"])
        sources = self._repo.get_enabled_sources(limit=30)
        for src in sources:
            for t in src.get("search_terms") or []:
                if isinstance(t, str):
                    terms.append(t)
        return list(dict.fromkeys(terms))
