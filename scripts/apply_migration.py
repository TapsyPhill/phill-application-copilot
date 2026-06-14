#!/usr/bin/env python3
"""Apply Stage 1 migrations via direct Postgres connection."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings

MIGRATIONS_DIR = ROOT / "supabase" / "migrations"
MIGRATION_FILES = sorted(MIGRATIONS_DIR.glob("*.sql"))


def db_url_from_settings() -> str:
    s = get_settings()
    if not s.supabase_url:
        raise ValueError("SUPABASE_URL required")
    password = s.supabase_db_password or __import__("os").environ.get("SUPABASE_DB_PASSWORD", "")
    if not password:
        raise ValueError("SUPABASE_DB_PASSWORD required for direct migration apply")
    parsed = urlparse(s.supabase_url)
    host = parsed.hostname or ""
    project_ref = host.split(".")[0] if host else ""
    if not project_ref:
        raise ValueError(f"Cannot parse project ref from SUPABASE_URL host: {host}")
    db_host = f"db.{project_ref}.supabase.co"
    return (
        f"host={db_host} port=5432 dbname=postgres user=postgres "
        f"password={password} sslmode=require"
    )


def apply_migration(cur, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    cur.execute(sql)


def main() -> int:
    if not MIGRATION_FILES:
        print(f"ERROR: no migrations found in {MIGRATIONS_DIR}")
        return 1

    conninfo = db_url_from_settings()
    conn = psycopg2.connect(conninfo)
    conn.autocommit = False
    applied = 0
    try:
        with conn.cursor() as cur:
            for migration in MIGRATION_FILES:
                print(f"Applying migration: {migration.name}")
                try:
                    apply_migration(cur, migration)
                    conn.commit()
                    applied += 1
                    print(f"  OK: {migration.name}")
                except psycopg2.Error as exc:
                    conn.rollback()
                    msg = str(exc)
                    if "already exists" in msg:
                        print(f"  SKIP: {migration.name} (objects already exist)")
                        continue
                    print(f"  FAILED: {migration.name}: {msg}")
                    return 1
        print(f"\nApplied {applied}/{len(MIGRATION_FILES)} migrations")
        print("Run scripts/check_schema.py to verify tables and RLS.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
