#!/usr/bin/env python3
"""Check whether Stage 1 core tables exist in Supabase."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings

CORE_TABLES = [
    "user_profiles",
    "sources",
    "discovered_urls",
    "raw_posts",
    "cleaned_posts",
    "opportunities",
    "opportunity_evidence",
    "source_categories",
]


def _headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }


def table_exists(client: httpx.Client, base: str, table: str, key: str) -> bool:
    r = client.get(
        f"{base}/rest/v1/{table}",
        params={"select": "id", "limit": "1"},
        headers=_headers(key),
    )
    if r.status_code == 200:
        return True
    if r.status_code in (404, 406):
        return False
    body = r.text[:200]
    if "does not exist" in body or "42P01" in body:
        return False
    raise RuntimeError(f"{table}: HTTP {r.status_code} — {body}")


def main() -> int:
    s = get_settings()
    url = s.supabase_url.rstrip("/")
    key = s.supabase_key_secret
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SECRET_KEY required")
        return 1

    missing: list[str] = []
    with httpx.Client(timeout=30.0) as client:
        for table in CORE_TABLES:
            try:
                ok = table_exists(client, url, table, key)
            except Exception as exc:
                print(f"{table}: ERROR {exc}")
                return 1
            status = "OK" if ok else "MISSING"
            print(f"{table}: {status}")
            if not ok:
                missing.append(table)

    if missing:
        print(f"\nSchema incomplete — missing: {', '.join(missing)}")
        return 2
    print("\nSchema OK — all core tables present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
