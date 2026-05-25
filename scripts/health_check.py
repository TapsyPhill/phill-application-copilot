#!/usr/bin/env python3
"""Verify environment, Supabase connectivity, and optional API keys."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    s = get_settings()
    ok = True
    if not s.supabase_url or not s.supabase_key_secret:
        logger.error("missing_supabase_credentials")
        ok = False
    else:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_schema.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.error("schema_check_failed", extra={"output": r.stdout + r.stderr})
            ok = False
        else:
            logger.info("schema_ok")

    for name, val in [
        ("gemini", s.gemini_api_key),
        ("groq", s.groq_api_key),
        ("tavily", s.tavily_api_key),
        ("firecrawl", s.firecrawl_api_key),
    ]:
        if val:
            logger.info("%s_configured", name)
        else:
            logger.warning("%s_missing", name)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
