# Stage 1 Accounts and API Keys

This document lists the services used in Stage 1 of **Phill Application Copilot**. Secrets must never be committed to the repository.

## GitHub

| Purpose | Details |
|--------|---------|
| Repository | `https://github.com/TapsyPhill/phill-application-copilot` |
| Version control | Source code, branches, pull requests |
| GitHub Actions | Scheduler and workflow triggers (see `.github/workflows/stage-1-placeholder.yml`) |
| Deployment trigger | Push to `main` triggers Cloudflare Pages via Git integration |

Store sensitive values in **GitHub repository secrets** (Settings → Secrets and variables → Actions), not in code or `.env` files committed to the repo.

## Cloudflare

| Purpose | Details |
|--------|---------|
| Domain | `phill-application-copilot.uk` |
| Pages hosting | Frontend built and deployed from this repository |
| Account ID | `CLOUDFLARE_ACCOUNT_ID` (GitHub secret / `.env` locally only) |
| Zone ID | `CLOUDFLARE_ZONE_ID` |
| API token | `CLOUDFLARE_API_TOKEN` (scoped token for DNS/API as needed) |

### Cloudflare Pages build settings

| Setting | Value |
|--------|--------|
| Framework preset | Vite |
| Build command | `npm ci && npm run build` |
| Build output directory | `frontend/dist` |
| Root directory | `/` (repo root) |
| Production branch | `main` |

Deployment is handled by **Cloudflare Pages Git integration**, not Wrangler CLI.

## Supabase

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Project API URL |
| `SUPABASE_ANON_KEY` | Client-side anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side only; never expose in frontend |

## AI / scraping (planned)

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Gemini API for enrichment or parsing |
| `GROQ_API_KEY` | Groq API alternative |
| `SCRAPER_SCHEDULE` | Cron expression, e.g. `0 7 * * *` (daily 07:00 UTC) |

## Local development

Copy `.env.example` to `.env` and fill in values locally. Do not commit `.env`.

```bash
cp .env.example .env
```
