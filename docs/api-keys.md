# API Keys and Environment Variables

**Template file:** `.env.example` (repository root)  
**Local usage:** Copy to `.env` — **never commit `.env`**  
**CI usage:** GitHub repository **Secrets** and **Variables**  
**Frontend rule:** Only variables prefixed with `VITE_` may appear in the Cloudflare build.

---

## 1. Security rules (mandatory)

| Rule | Detail |
|------|--------|
| **No secrets in git** | `.env`, service keys, tokens stay local or in GitHub Secrets |
| **No secrets in frontend bundle** | Never prefix secret keys with `VITE_` |
| **Service role server-only** | `SUPABASE_SECRET_KEY` only in Actions and Python scripts |
| **Publishable key in browser** | `VITE_SUPABASE_PUBLISHABLE_KEY` is safe with RLS enabled |
| **Rotate on leak** | Revoke token in provider dashboard immediately |
| **Do not log values** | Log presence/absence only in `health_check.py` |
| **Separate dev/prod** | Different Supabase projects or keys per environment recommended |
| **Principle of least privilege** | Cloudflare token scoped to Pages deploy only |

---

## 2. Variable reference

### 2.1 Cloudflare / deployment

| Variable | Required | Where used | Description |
|----------|----------|------------|-------------|
| `CLOUDFLARE_ACCOUNT_ID` | Deploy | GitHub Actions `wrangler-action` | Cloudflare account identifier |
| `CLOUDFLARE_API_TOKEN` | Deploy | GitHub Actions | API token with Pages deploy permission |
| `CLOUDFLARE_ZONE_ID` | Optional | DNS automation (future) | Zone for `phill-application-copilot.uk` |
| `PROJECT_DOMAIN` | Recommended | Build metadata, CORS config | Production hostname without scheme |

**Example (non-secret shape):** `PROJECT_DOMAIN=phill-application-copilot.uk`

---

### 2.2 Supabase / database

| Variable | Required | Where used | Description |
|----------|----------|------------|-------------|
| `SUPABASE_URL` | Yes | Backend scripts, can mirror to Vite | Project API URL `https://<ref>.supabase.co` |
| `SUPABASE_PUBLISHABLE_KEY` | Yes (FE) | Backend optional | Publishable/anon key for client SDK |
| `SUPABASE_SECRET_KEY` | Yes (BE) | `seed_sources.py`, scrape, AI scripts | **Service role** — full DB access, bypasses RLS |
| `SUPABASE_DB_PASSWORD` | Optional | Direct `psql` / migrations CLI | Database password for non-API tools |

| Variable | Required | Where used | Description |
|----------|----------|------------|-------------|
| `VITE_SUPABASE_URL` | Yes (FE build) | Vite → React | Same URL as `SUPABASE_URL` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Yes (FE build) | Vite → React | Same as publishable key |
| `VITE_PROJECT_DOMAIN` | Optional | Frontend links, canonical URLs | Public site domain |

**Naming note:** Older docs may reference `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY`. This project uses **publishable** and **secret** naming per Supabase’s newer key types — map accordingly in dashboard.

---

### 2.3 AI models

| Variable | Required | Where used | Description |
|----------|----------|------------|-------------|
| `GEMINI_API_KEY` | Recommended | `GeminiClient`, `ai-analysis.yml` | Google Gemini API for classification |
| `GROQ_API_KEY` | Recommended | `GroqClient` | Groq fast inference |
| `HF_TOKEN` | Optional | HuggingFace hub downloads | Embedding model auth if gated |
| `OPENAI_API_KEY` | Optional | Future extractors / tie-break | OpenAI API |
| `ANTHROPIC_API_KEY` | Optional | Long-document PhD parsing | Claude API |
| `OLLAMA_API_KEY` | Optional | Ollama Cloud (if used) | Often empty for local Ollama |
| `OLLAMA_BASE_URL` | Optional | `OllamaClient` | Default `http://127.0.0.1:11434` |

**Cost control:** Pair cloud keys with `AI_DAILY_CLOUD_CALL_LIMIT`.

---

### 2.4 Scraping / discovery

| Variable | Required | Where used | Description |
|----------|----------|------------|-------------|
| `FIRECRAWL_API_KEY` | Optional | `FirecrawlScraper`, daily scrape | Firecrawl extract/crawl API |
| `SCRAPINGBEE_API_KEY` | Optional | `ScrapingBeeScraper` | Proxy/render fallback |
| `APIFY_API_TOKEN` | Optional | `ApifyScraper` | Apify platform token |
| `TAVILY_API_KEY` | Recommended | `TavilyDiscovery` | Web search URL discovery |

Missing scraping keys **degrade gracefully** — router skips unavailable paid methods.

---

### 2.5 Pipeline tuning

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SCRAPER_SCHEDULE` | Optional | `0 7 * * *` | Documentary cron; actual schedule in workflow YAML |
| `AI_DAILY_CLOUD_CALL_LIMIT` | Optional | `200` | Max cloud LLM calls per UTC day |
| `CHROMA_PERSIST_DIR` | Optional | `./data/chroma` | Local Chroma persistence path |
| `LOG_LEVEL` | Optional | `INFO` | Python logging: DEBUG, INFO, WARNING |

---

## 3. Mapping to `Settings` class

`backend/app/config/settings.py` loads via Pydantic (case-insensitive env):

| Env var | Settings attribute |
|---------|-------------------|
| `SUPABASE_URL` | `supabase_url` |
| `SUPABASE_PUBLISHABLE_KEY` | `supabase_publishable_key` |
| `SUPABASE_SECRET_KEY` | `supabase_secret_key` |
| `GEMINI_API_KEY` | `gemini_api_key` |
| `GROQ_API_KEY` | `groq_api_key` |
| `HF_TOKEN` | `hf_token` |
| `OPENAI_API_KEY` | `openai_api_key` |
| `ANTHROPIC_API_KEY` | `anthropic_api_key` |
| `OLLAMA_API_KEY` | `ollama_api_key` |
| `OLLAMA_BASE_URL` | `ollama_base_url` |
| `FIRECRAWL_API_KEY` | `firecrawl_api_key` |
| `SCRAPINGBEE_API_KEY` | `scrapingbee_api_key` |
| `APIFY_API_TOKEN` | `apify_api_token` |
| `TAVILY_API_KEY` | `tavily_api_key` |
| `AI_DAILY_CLOUD_CALL_LIMIT` | `ai_daily_cloud_call_limit` |
| `CHROMA_PERSIST_DIR` | `chroma_persist_dir` |
| `LOG_LEVEL` | `log_level` |

Cloudflare vars are **not** loaded in Python settings — CI/deploy only.

---

## 4. GitHub Actions secret matrix

| Secret / Var | Workflow |
|--------------|----------|
| `SUPABASE_URL` | daily-scrape, ai-analysis, seed |
| `SUPABASE_SECRET_KEY` | daily-scrape, ai-analysis, seed |
| `FIRECRAWL_API_KEY` | daily-scrape |
| `SCRAPINGBEE_API_KEY` | daily-scrape |
| `APIFY_API_TOKEN` | daily-scrape |
| `TAVILY_API_KEY` | daily-scrape |
| `GEMINI_API_KEY` | ai-analysis |
| `GROQ_API_KEY` | ai-analysis |
| `OPENAI_API_KEY` | ai-analysis |
| `ANTHROPIC_API_KEY` | ai-analysis |
| `AI_DAILY_CLOUD_CALL_LIMIT` | ai-analysis (as `vars` with default) |
| `VITE_SUPABASE_URL` | deploy-frontend |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | deploy-frontend |
| `VITE_PROJECT_DOMAIN` | deploy-frontend |
| `CLOUDFLARE_API_TOKEN` | deploy-frontend |
| `CLOUDFLARE_ACCOUNT_ID` | deploy-frontend |

---

## 5. Local setup

```bash
cp .env.example .env
# Edit .env with your values — never commit
pip install -r requirements.txt
python scripts/health_check.py   # when implemented: checks required keys
```

### 5.1 Minimum viable `.env` (development)

| Variable | Needed for |
|----------|------------|
| `SUPABASE_URL` | Any DB script |
| `SUPABASE_SECRET_KEY` | Seed + scrape persistence |
| `VITE_SUPABASE_*` | Frontend local dev |

AI and scraping keys optional for UI-only development.

### 5.2 Full pipeline `.env`

Add all scraping + at least one of `GEMINI_API_KEY` / `GROQ_API_KEY` / local Ollama.

---

## 6. Key rotation procedure

| Step | Action |
|------|--------|
| 1 | Generate new key in provider dashboard |
| 2 | Update GitHub Secret |
| 3 | Update local `.env` |
| 4 | Revoke old key |
| 5 | Re-run failed workflow |
| 6 | Record in `audit_logs` (manual note) |

---

## 7. What must never appear in repo

| Item | Risk |
|------|------|
| `.env` | Full secret leak |
| Service role in `frontend/` | Database takeover |
| Tavily/Firecrawl keys in `dist/` | Billing abuse |
| Supabase DB password in docs | Direct DB access |

`.gitignore` should include `.env`, `data/chroma/`, and export dumps.

---

## 8. Health check expectations

`scripts/health_check.py` should verify:

| Check | Pass condition |
|-------|----------------|
| Supabase URL set | non-empty |
| Secret key set for batch jobs | non-empty |
| At least one LLM path | Ollama reachable OR cloud key present |
| Chroma directory | writable |
| No secret printed | only boolean flags |

---

## 9. Provider signup links (documentation only)

| Provider | Console |
|----------|---------|
| Supabase | https://supabase.com/dashboard |
| Cloudflare | https://dash.cloudflare.com |
| Tavily | https://tavily.com |
| Firecrawl | https://firecrawl.dev |
| Google AI Studio | Gemini keys |
| Groq | https://console.groq.com |

---

## 10. Related documentation

| File | Topic |
|------|-------|
| `stage-1-accounts.md` | Account-level overview |
| `stage-1-architecture.md` | Where keys are consumed |
| `loopholes-and-safeguards.md` | Secret leakage risks |
