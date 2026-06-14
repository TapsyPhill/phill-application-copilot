# Scripts

| Script | Purpose |
|--------|---------|
| `health_check.py` | Environment validation (Supabase + schema + key warnings) |
| `check_schema.py` | Verify core and pipeline tables exist |
| `apply_migration.py` | Apply all SQL migrations in `supabase/migrations/` |
| `bootstrap_auth_user.py` | Create/update Supabase Auth dashboard user |
| `seed_sources.py` | Load JSON seed sources into Supabase |
| `seed_search_terms.py` | Load search terms for Tavily discovery |
| `seed_profile.py` | Seed user profile for AI relevance scoring |
| `run_daily_scrape.py` | Discovery + scrape + clean + dedup pipeline |
| `run_opportunity_round.py` | Full current-time round: discovery, scrape, clean, dedup, AI, audit |
| `run_cleaning_pipeline.py` | Raw → cleaned posts |
| `run_deduplication.py` | Merge duplicates |
| `run_ai_analysis.py` | AI + voting + opportunities |
| `run_rag_indexing.py` | Chroma / vector indexing |
| `run_stage1_smoke.py` | End-to-end pipeline smoke test |
| `audit_pipeline_quality.py` | Read-only pipeline quality audit |
| `backfill_application_contacts.py` | Repair boolean placeholder contacts and extract real emails from cleaned text |
| `sync_github_secrets.py` | Push `.env` values to GitHub Secrets |
| `export_backup.py` | Table export backup |

Pipeline tuning (`DISCOVERY_MAX_TERMS`, `SCRAPE_MAX_URLS`, `AI_ANALYSIS_LIMIT`, etc.) is loaded from `.env` via `backend/app/config/settings.py`.
