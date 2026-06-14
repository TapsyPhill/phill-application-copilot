#!/usr/bin/env python3
"""Push local .env values to GitHub Actions secrets (never prints secret values)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# GitHub secret name -> .env key(s), first non-empty wins
SECRET_MAP: dict[str, list[str]] = {
    "SUPABASE_URL": ["SUPABASE_URL"],
    "SUPABASE_SECRET_KEY": ["SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY"],
    "SUPABASE_PUBLISHABLE_KEY": ["SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"],
    "SUPABASE_DB_PASSWORD": ["SUPABASE_DB_PASSWORD"],
    "TAVILY_API_KEY": ["TAVILY_API_KEY"],
    "FIRECRAWL_API_KEY": ["FIRECRAWL_API_KEY"],
    "SCRAPINGBEE_API_KEY": ["SCRAPINGBEE_API_KEY"],
    "APIFY_API_TOKEN": ["APIFY_API_TOKEN"],
    "GEMINI_API_KEY": ["GEMINI_API_KEY"],
    "GROQ_API_KEY": ["GROQ_API_KEY"],
    "OPENAI_API_KEY": ["OPENAI_API_KEY"],
    "ANTHROPIC_API_KEY": ["ANTHROPIC_API_KEY"],
    "HF_TOKEN": ["HF_TOKEN"],
    "CLOUDFLARE_API_TOKEN": ["CLOUDFLARE_API_TOKEN"],
    "CLOUDFLARE_ACCOUNT_ID": ["CLOUDFLARE_ACCOUNT_ID"],
    "CLOUDFLARE_ZONE_ID": ["CLOUDFLARE_ZONE_ID"],
    "PROJECT_DOMAIN": ["PROJECT_DOMAIN"],
    "VITE_SUPABASE_URL": ["VITE_SUPABASE_URL", "SUPABASE_URL"],
    "VITE_SUPABASE_PUBLISHABLE_KEY": ["VITE_SUPABASE_PUBLISHABLE_KEY", "SUPABASE_PUBLISHABLE_KEY"],
    "VITE_PROJECT_DOMAIN": ["VITE_PROJECT_DOMAIN", "PROJECT_DOMAIN"],
}


def _load_env() -> dict[str, str]:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("ERROR: .env not found at repo root")
        sys.exit(1)
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        if val:
            values[key.strip()] = val
    return values


def main() -> int:
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: GitHub CLI (gh) required. Install and run: gh auth login")
        return 1

    env = _load_env()
    set_count = 0
    skipped: list[str] = []

    for secret_name, keys in SECRET_MAP.items():
        value = ""
        for key in keys:
            if env.get(key):
                value = env[key]
                break
        if not value:
            skipped.append(secret_name)
            continue
        subprocess.run(
            ["gh", "secret", "set", secret_name, "--body", value],
            check=True,
            cwd=ROOT,
        )
        print(f"OK: set {secret_name}")
        set_count += 1

    print(f"\nSet {set_count} secrets.")
    if skipped:
        print("Skipped (empty in .env):", ", ".join(skipped))
    print("\nRun workflow: gh workflow run 'Validate Repository Secrets'")
    return 0 if set_count >= 4 else 1


if __name__ == "__main__":
    raise SystemExit(main())
