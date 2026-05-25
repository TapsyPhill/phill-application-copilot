# GitHub Secrets — required for deploy & pipelines

**Repo:** `TapsyPhill/phill-application-copilot`  
**Add at:** https://github.com/TapsyPhill/phill-application-copilot/settings/secrets/actions

`gh secret list` is currently **empty** — that is why **Deploy to Cloudflare** and **Daily Scrape** fail.

## Required secrets (copy from your local `.env` / Cloudflare / Supabase)

| Secret name | Used by |
|-------------|---------|
| `CLOUDFLARE_API_TOKEN` | Deploy to Cloudflare |
| `CLOUDFLARE_ACCOUNT_ID` | Deploy to Cloudflare |
| `VITE_SUPABASE_URL` | Frontend build + deploy |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Frontend build + deploy |
| `VITE_PROJECT_DOMAIN` | Frontend build (e.g. `phill-application-copilot.uk`) |
| `SUPABASE_URL` | Daily scrape, AI analysis |
| `SUPABASE_SECRET_KEY` | Daily scrape, AI analysis (service role) |
| `TAVILY_API_KEY` | Daily scrape |
| `GEMINI_API_KEY` | AI analysis |
| `GROQ_API_KEY` | AI analysis |
| `FIRECRAWL_API_KEY` | Daily scrape (optional) |
| `SCRAPINGBEE_API_KEY` | Daily scrape (optional) |
| `APIFY_API_TOKEN` | Daily scrape (optional) |

After adding secrets:

1. **Actions → Validate Repository Secrets → Run workflow**
2. **Actions → Deploy to Cloudflare → Run workflow**
3. **Actions → Daily Scrape → Run workflow**

## Live URL (after deploy succeeds)

**https://phill-job-application-copilot.pages.dev**

The Cloudflare dashboard **Visit** button on the **Workers** project may still show the old placeholder until Git builds from latest `main` with correct settings.
