#!/usr/bin/env python3
"""Apply Stage 1 core schema migration via direct Postgres connection."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings

MIGRATION = ROOT / "supabase" / "migrations" / "20260525100000_stage1_core_schema.sql"


def db_url_from_settings() -> str:
    s = get_settings()
    if not s.supabase_url:
        raise ValueError("SUPABASE_URL required")
    password = s.supabase_db_password or __import__("os").environ.get("SUPABASE_DB_PASSWORD", "")
    if not password:
        raise ValueError("SUPABASE_DB_PASSWORD required for direct migration apply")
    parsed = urlparse(s.supabase_url)
    host = parsed.hostname or ""
    # https://abcdefgh.supabase.co -> db.abcdefgh.supabase.co
    project_ref = host.split(".")[0] if host else ""
    if not project_ref:
        raise ValueError(f"Cannot parse project ref from SUPABASE_URL host: {host}")
    db_host = f"db.{project_ref}.supabase.co"
    return (
        f"host={db_host} port=5432 dbname=postgres user=postgres "
        f"password={password} sslmode=require"
    )


def main() -> int:
    if not MIGRATION.exists():
        print(f"ERROR: migration not found: {MIGRATION}")
        return 1

    sql = MIGRATION.read_text(encoding="utf-8")
    conninfo = db_url_from_settings()
    print(f"Applying migration: {MIGRATION.name}")
    conn = psycopg2.connect(conninfo)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Migration applied successfully")
        return 0
    except psycopg2.Error as exc:
        conn.rollback()
        msg = str(exc)
        if "already exists" in msg:
            print("Migration partially/fully applied (objects already exist).")
            print("Run scripts/check_schema.py to verify tables.")
            return 0
        print(f"Migration failed: {msg}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
