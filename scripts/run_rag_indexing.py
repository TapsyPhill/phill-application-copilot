#!/usr/bin/env python3
"""Index profile and opportunity chunks into Chroma."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    repo = SupabaseRepo.from_settings()
    try:
        from backend.app.rag.chroma_store import ChromaStore
    except Exception as exc:
        logger.warning("chroma_unavailable", extra={"error": str(exc)})
        return 0

    profile_store = ChromaStore("profile")
    opp_store = ChromaStore("opportunities")

    chunks = (
        repo._client.table("profile_knowledge_chunks").select("id,title,content").limit(100).execute()
    ).data or []
    if chunks:
        profile_store.upsert(
            ids=[c["id"] for c in chunks],
            documents=[f"{c.get('title') or ''}\n{c['content']}" for c in chunks],
            metadatas=[{"type": "profile"} for _ in chunks],
        )

    opps = (
        repo._client.table("opportunities")
        .select("id,title,summary,category")
        .order("updated_at", desc=True)
        .limit(200)
        .execute()
    ).data or []
    if opps:
        opp_store.upsert(
            ids=[o["id"] for o in opps],
            documents=[f"{o['title']}\n{o.get('summary') or ''}" for o in opps],
            metadatas=[{"category": o.get("category")} for o in opps],
        )

    repo.audit("rag_index_complete", details={"profile_chunks": len(chunks), "opportunities": len(opps)})
    logger.info("rag_indexing_finished", extra={"profile": len(chunks), "opportunities": len(opps)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
