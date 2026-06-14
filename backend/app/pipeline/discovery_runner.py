"""Discover candidate URLs from seeded sources, listing pages, and Tavily search."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, NamedTuple

import structlog

from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.ingestion.source_link_extractor import extract_listing_links
from backend.app.scraping.tavily_discovery import TavilyDiscovery

logger = structlog.get_logger(__name__)

ROOT = Path(__file__).resolve().parents[3]
SEARCH_TERMS_DIR = ROOT / "backend" / "app" / "sources" / "search_terms"


class SearchTerm(NamedTuple):
    term: str
    target_section: str | None = None
    language: str | None = None


class DiscoveryRunner:
    def __init__(
        self,
        repo: SupabaseRepo,
        max_terms: int = 15,
        max_sources: int | None = None,
    ) -> None:
        self._repo = repo
        self._tavily = TavilyDiscovery()
        self._max_terms = max_terms
        self._max_sources = max_sources or get_settings().discovery_max_sources

    def run(self) -> int:
        source_count = self._discover_from_sources()
        tavily_count = self._discover_from_tavily()
        total = source_count + tavily_count
        self._repo.audit(
            "discovery_complete",
            details={"urls_discovered": total, "from_sources": source_count, "from_tavily": tavily_count},
        )
        logger.info("discovery_complete", total=total, sources=source_count, tavily=tavily_count)
        return total

    def _discover_from_sources(self) -> int:
        count = 0
        sources = self._repo.get_enabled_sources(limit=self._max_sources)
        for src in sources:
            source_id = src.get("id")
            base_domain = (src.get("base_domain") or "").strip()
            main_url = (src.get("url") or "").strip()
            # PhD portals are scarce enough that their listing/search pages are
            # worth scraping even when they also allow search.
            seed_main_url = not src.get("allows_search") or src.get("target_section") == "phd"
            if main_url and seed_main_url:
                self._repo.upsert_discovered_url(
                    main_url,
                    source_id=source_id,
                    discovery_method="source_seed",
                    search_term=None,
                    metadata={"source_name": src.get("source_name"), "target_section": src.get("target_section")},
                )
                count += 1

            pattern = (src.get("search_url_pattern") or "").strip()
            if pattern and "{term}" in pattern:
                for term in self._terms_for_source(src)[:3]:
                    search_url = pattern.replace("{term}", term.replace(" ", "-"))
                    self._repo.upsert_discovered_url(
                        search_url,
                        source_id=source_id,
                        discovery_method="source_search",
                        search_term=term,
                        metadata={"source_name": src.get("source_name")},
                    )
                    count += 1

            if main_url and base_domain and not src.get("requires_login"):
                for link in extract_listing_links(
                    main_url,
                    base_domain,
                    max_links=8,
                    target_section=src.get("target_section"),
                ):
                    self._repo.upsert_discovered_url(
                        link,
                        source_id=source_id,
                        discovery_method="source_listing",
                        search_term=None,
                        metadata={"source_name": src.get("source_name"), "parent_url": main_url},
                    )
                    count += 1

        return count

    def _discover_from_tavily(self) -> int:
        count = 0
        terms = self._select_terms_by_section(self._collect_terms())
        for item in terms:
            query = self._query_for_term(item)
            links = self._tavily.search(query, max_results=8)
            self._repo.log_api_usage(
                "tavily",
                units=len(links),
                metadata={"term": item.term, "query": query, "target_section": item.target_section},
            )
            for link in links:
                self._repo.upsert_discovered_url(
                    link.url,
                    source_id=None,
                    discovery_method=link.discovery_method,
                    search_term=item.term,
                    metadata={
                        "title": link.title,
                        "snippet": link.snippet,
                        "target_section": item.target_section,
                        "query": query,
                    },
                )
                count += 1
        return count

    def _query_for_term(self, item: SearchTerm) -> str:
        section = item.target_section
        if section == "client_lead":
            return f'{item.term} ("gesucht" OR "looking for" OR "need help" OR "freelance")'
        if section == "phd":
            return f'{item.term} ("PhD position" OR "doctoral researcher" OR "fully funded" OR "application by email")'
        if section == "job":
            return f'{item.term} ("job" OR "career" OR "hiring")'
        if section == "remote_job":
            return f'{item.term} ("remote job" OR "work from anywhere" OR "remote role")'
        return item.term

    def _terms_for_source(self, src: dict[str, Any]) -> list[str]:
        terms: list[str] = []
        for t in src.get("search_terms") or []:
            if isinstance(t, str) and t.strip():
                terms.append(t.strip())
        section = src.get("target_section") or src.get("category")
        defaults = {
            "phd": ["machine learning PhD funded", "data science doctoral position"],
            "job": ["data scientist Germany", "LLM engineer Europe"],
            "remote_job": ["remote data scientist", "remote machine learning engineer"],
            "client_lead": ["WordPress Hilfe gesucht", "Webentwickler gesucht"],
        }
        if not terms and section in defaults:
            terms = defaults[section]
        return list(dict.fromkeys(terms))

    def _select_terms_by_section(self, terms: list[SearchTerm]) -> list[SearchTerm]:
        """Reserve search budget per section so PhD terms are not starved."""
        if len(terms) <= self._max_terms:
            return terms

        buckets: dict[str, list[SearchTerm]] = {}
        for term in terms:
            section = term.target_section or "general"
            buckets.setdefault(section, []).append(term)

        selected: list[SearchTerm] = []
        preferred_sections = ("phd", "job", "remote_job", "client_lead", "general")
        base_quota = max(3, self._max_terms // max(1, len([s for s in preferred_sections if buckets.get(s)])))
        for section in preferred_sections:
            if len(selected) >= self._max_terms:
                break
            for term in buckets.get(section, [])[:base_quota]:
                if term not in selected:
                    selected.append(term)
                    if len(selected) >= self._max_terms:
                        break

        if len(selected) < self._max_terms:
            for term in terms:
                if term not in selected:
                    selected.append(term)
                    if len(selected) >= self._max_terms:
                        break
        return selected

    def _collect_terms(self) -> list[SearchTerm]:
        db_terms = [
            SearchTerm(t["term"], t.get("target_section"), t.get("language"))
            for t in self._repo.get_search_terms()
            if t.get("term")
        ]
        if db_terms:
            return db_terms
        terms: list[SearchTerm] = []
        if SEARCH_TERMS_DIR.exists():
            for path in sorted(SEARCH_TERMS_DIR.glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                section = data.get("target_section")
                lang = data.get("language")
                for item in data.get("terms", data.get("search_terms", [])):
                    if isinstance(item, str):
                        terms.append(SearchTerm(item, section, lang))
                    elif isinstance(item, dict) and item.get("term"):
                        terms.append(SearchTerm(item["term"], item.get("target_section") or section, item.get("language") or lang))
        sources = self._repo.get_enabled_sources(limit=30)
        for src in sources:
            terms.extend(SearchTerm(term, src.get("target_section"), src.get("language")) for term in self._terms_for_source(src))
        return list(dict.fromkeys(terms))
