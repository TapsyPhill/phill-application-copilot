# phill-job-application-copilot

**Opportunity Command Center** — Stage 1 production intelligence layer for discovering, analyzing, scoring, and reviewing opportunities. Stage 1 does **not** send applications or emails; it prepares evidence-backed decisions for manual action.

## What Stage 1 does

| Area | Purpose |
|------|---------|
| Client Leads | Germany, global, and South Africa technical-service opportunities |
| PhD Opportunities | Fully funded doctoral / research positions with proof |
| Job Applications | Profile-matched roles in Germany and target countries |
| Remote Jobs | Global remote roles with remote-restriction proof |

Pipeline: **sources → discover → scrape → clean → quality gate → dedupe → AI + voting → score → Supabase → dashboard**.

## Deployment (Cloudflare Pages)

Connect the GitHub repo to Cloudflare Pages (or rely on the GitHub Actions workflow `cloudflare-deploy.yml`):

| Setting | Value |
|---------|--------|
| Production branch | `main` |
| Root directory | `/` (repo root) |
| Build command | `npm ci && npm run build` |
| Build output | `frontend/dist` |
| Deploy command | Leave empty for Git integration, or use Pages deploy (not `wrangler deploy`) |

Set environment variables in Cloudflare: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_PROJECT_DOMAIN`.

Enable **Supabase Auth → Email/password** for the private dashboard user, then bootstrap the login user locally:

```bash
# Add to .env (never commit real password)
BOOTSTRAP_AUTH_EMAIL=phillmhembere@gmail.com
BOOTSTRAP_AUTH_PASSWORD=your-private-password
python scripts/bootstrap_auth_user.py
```

See [docs/supabase-auth-setup.md](docs/supabase-auth-setup.md) for details.

Backend pipelines run via **GitHub Actions** (`daily-scrape`, `ai-analysis`, `rag-indexing`, `backup-export`), not on Cloudflare.

**Cloudflare deploy failed with `wrangler deploy`?** See [docs/cloudflare-pages-setup.md](docs/cloudflare-pages-setup.md) — use `frontend/dist` and **Pages**, not Workers deploy.

**GitHub Actions scrape/AI failed?** From repo root with `.env` filled, run `python scripts/sync_github_secrets.py`, then workflow **Validate Repository Secrets**. Full local smoke: `python scripts/run_stage1_smoke.py`.

## Quick start

```bash
# Environment
cp .env.example .env
# Fill Supabase, AI, and scraper keys locally only
# Frontend reads VITE_* from repo root .env (not frontend/.env)

# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/health_check.py
python scripts/seed_sources.py
python scripts/seed_search_terms.py
python scripts/seed_profile.py

# Auth user (required for dashboard login)
python scripts/bootstrap_auth_user.py

# Frontend
npm ci
npm run dev
# Open http://localhost:5173 — restart dev server after editing .env
```

Apply database schema (all migrations, in order):

```bash
# Option A: Supabase SQL editor — run each file in supabase/migrations/
# Option B: direct Postgres apply (needs SUPABASE_DB_PASSWORD in .env)
python scripts/apply_migration.py
python scripts/check_schema.py
```

Pipeline tuning vars (`DISCOVERY_MAX_TERMS`, `SCRAPE_MAX_URLS`, `AI_ANALYSIS_LIMIT`, etc.) are loaded from `.env` via `backend/app/config/settings.py`.

## Repository layout

```
├── docs/                    # Full Stage 1 product & architecture documentation
├── supabase/migrations/     # PostgreSQL schema (8 table groups, Stage 2-ready)
├── backend/app/             # Scrapers, AI brains, RAG, dedup, scoring
├── frontend/                # React + Vite dashboard (Cloudflare Pages)
├── scripts/                 # Daily scrape, AI analysis, seed, backup
├── data/                    # Local raw/cleaned exports and Chroma persistence
└── .github/workflows/       # Deploy, scrape, AI, RAG, backup
```

## Documentation index

| Document | Description |
|----------|-------------|
| [docs/stage-1-product-plan.md](docs/stage-1-product-plan.md) | Full product specification |
| [docs/stage-1-architecture.md](docs/stage-1-architecture.md) | Technical architecture & data flow |
| [docs/database-schema.md](docs/database-schema.md) | Table groups and fields |
| [docs/api-keys.md](docs/api-keys.md) | Environment variables & security |
| [docs/implementation-checklist.md](docs/implementation-checklist.md) | Delivery checklist |
| [docs/stage-2-future-connection.md](docs/stage-2-future-connection.md) | How Stage 2 plugs in |

## Core philosophy

- Do not trust one source, scraper, or AI model
- Source page is truth; Tavily only discovers candidate URLs
- Every high-confidence AI decision requires **evidence** from source text
- Duplicates merge without resetting **viewed** status
- Secrets never in frontend; use `VITE_` prefix only for public Supabase keys

## Stage 2 (not implemented)

Gmail drafts, application automation, cover letters, portal assist, and follow-ups will attach to existing `applications`, `email_drafts`, and `document_vault` tables.

## License

Private project — Tapuwa Phill Mhembere.
