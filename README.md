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

Connect the GitHub repo to Cloudflare Pages:

| Setting | Value |
|---------|--------|
| Production branch | `main` |
| Root directory | `frontend` |
| Build command | `npm run build` |
| Build output | `dist` |

Set environment variables in Cloudflare: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_PROJECT_DOMAIN`.

Enable **Supabase Auth → Email magic link** and add your Cloudflare URL to redirect allow list.

Backend pipelines run via **GitHub Actions** (`daily-scrape`, `ai-analysis`, `rag-indexing`, `backup-export`), not on Cloudflare.

## Quick start

```bash
# Environment
cp .env.example .env
# Fill Supabase, AI, and scraper keys locally only

# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/health_check.py
python scripts/seed_sources.py

# Frontend
cd frontend && npm install && npm run dev
```

Apply database schema:

```bash
# Supabase SQL editor or CLI
supabase db push   # or run supabase/migrations/20260525100000_stage1_core_schema.sql
```

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
