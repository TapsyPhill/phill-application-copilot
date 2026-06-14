# Stage 1 Implementation Checklist

Use this checklist to track delivery of **phill-job-application-copilot** (Opportunity Command Center). Stage 1 is complete when every item in a section is checked and verified in staging.

## Foundation

- [ ] Repository structure matches `docs/stage-1-architecture.md`
- [ ] `.env.example` documented in `docs/api-keys.md`
- [ ] Supabase project created; migrations applied
- [ ] Cloudflare Pages connected to `main` branch
- [ ] GitHub Actions secrets configured (no keys in repo)

## Database

- [ ] All migrations in `supabase/migrations/` applied
- [ ] RLS policies enabled for single-user mode
- [ ] Indexes verified on `opportunities` hot paths
- [ ] Seed profile loaded for Tapuwa Phill Mhembere
- [ ] `sources` table populated via `scripts/seed_sources.py`

## Data collection

- [ ] Seed JSON files present under `backend/app/sources/seed_sources/`
- [ ] Search term JSON files under `backend/app/sources/search_terms/`
- [ ] `scripts/seed_sources.py` runs without error
- [ ] `scripts/run_daily_scrape.py` discovers URLs and writes `raw_posts`
- [ ] Scraper router falls back across methods
- [ ] Tavily discovery stores `discovered_urls` only (no direct opportunity creation)

## Pipeline

- [ ] Cleaning pipeline writes `cleaned_posts`
- [ ] Data quality gate rejects garbage and flags manual review
- [ ] Deduplication merges without resetting `viewed`
- [ ] AI analysis writes evidence for every high-confidence decision
- [ ] Voting engine stores per-model outputs
- [ ] Opportunities created/updated with category-specific detail tables
- [ ] RAG indexing updates Chroma + optional pgvector

## AI & scoring

- [ ] Rule-based pre-filter before cloud models
- [ ] Content-hash cache prevents re-analysis
- [ ] Daily cloud call limit enforced
- [ ] Client / PhD / Job / Remote scoring rules applied
- [ ] API usage logged to `api_usage_logs`

## Frontend dashboard

- [ ] Auth / single-user access (Supabase)
- [ ] Overview metrics page
- [ ] Client Leads tabs (Germany, Global, South Africa, filters)
- [ ] PhD, Job, Remote Jobs pages with required tabs
- [ ] Opportunity detail with evidence panel
- [ ] Sources management page
- [ ] Profile knowledge page
- [ ] Review queue
- [ ] Logs / health page
- [ ] Settings page
- [ ] Stage 2 buttons visible but disabled

## Operations

- [ ] `daily-scrape.yml` scheduled + manual dispatch
- [ ] `ai-analysis.yml` processes new cleaned posts
- [ ] `rag-indexing.yml` updates embeddings
- [ ] `backup-export.yml` exports tables
- [ ] `cloudflare-deploy.yml` deploys on push to main
- [ ] `scripts/health_check.py` passes

## Safeguards verified

- [ ] No secrets in frontend bundle
- [ ] No login/captcha bypass in scrapers
- [ ] Duplicate opportunity not created on re-scrape
- [ ] `viewed` status preserved on merge
- [ ] Unfunded PhDs deprioritized without proof
- [ ] US-only remote jobs flagged correctly
- [ ] Manual URL ingestion works from dashboard

## Documentation

- [ ] `README.md` (root) complete
- [ ] All `docs/*.md` files reviewed
- [ ] Folder READMEs present for major directories

## Stage 2 readiness (no implementation yet)

- [ ] `applications`, `email_drafts`, `document_vault` tables exist
- [ ] `stage2_ready` fields on opportunities
- [ ] Placeholder UI actions labeled “Stage 2”

---

**Definition of done for Stage 1:** User can run daily discovery, review classified/scored opportunities with evidence in four dashboard sections, manually save/reject/note, and trust deduplication — without sending applications or emails.
