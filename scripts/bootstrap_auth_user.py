#!/usr/bin/env python3
"""Create or update the Stage 1 dashboard login user (service role only)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings


def main() -> int:
    s = get_settings()
    email = os.environ.get("BOOTSTRAP_AUTH_EMAIL") or s.bootstrap_auth_email
    password = os.environ.get("BOOTSTRAP_AUTH_PASSWORD") or s.bootstrap_auth_password
    if not password:
        print("ERROR: set BOOTSTRAP_AUTH_PASSWORD in .env or environment (do not commit to git)")
        return 1

    if not s.supabase_url or not s.supabase_key_secret:
        print("ERROR: SUPABASE_URL and SUPABASE_SECRET_KEY required")
        return 1

    from supabase import create_client

    client = create_client(s.supabase_url, s.supabase_key_secret)

    try:
        client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
            }
        )
        print(f"Created user: {email}")
    except Exception as exc:
        msg = str(exc).lower()
        if "already" in msg or "registered" in msg or "exists" in msg:
            users = client.auth.admin.list_users()
            uid = None
            for u in users:
                if getattr(u, "email", None) == email or (isinstance(u, dict) and u.get("email") == email):
                    uid = getattr(u, "id", None) or u.get("id")
                    break
            if uid:
                client.auth.admin.update_user_by_id(uid, {"password": password, "email_confirm": True})
                print(f"Updated password for existing user: {email}")
            else:
                print(f"User may exist but could not update: {exc}")
                return 1
        else:
            print(f"Failed: {exc}")
            return 1

    print("Enable in Supabase: Authentication → Providers → Email → ON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
