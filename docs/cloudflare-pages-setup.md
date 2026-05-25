# Cloudflare Pages — fix deploy error

## The error you saw

```
Could not detect a directory containing static files (html, css, js)
Failed: error occurred while running deploy command: npx wrangler deploy
```

**Cause:** Cloudflare is running **`wrangler deploy`** (Workers bundle). This project is a **static Vite SPA** in `frontend/dist`, not a Worker script.

## Correct Cloudflare dashboard settings

Project name on Cloudflare: **`phill-job-application-copilot`** (matches `wrangler.toml`).

| Setting | Value |
|---------|--------|
| **Production branch** | `main` |
| **Root directory** | `/` (repo root) or leave default |
| **Build command** | `npm ci && npm run build` |
| **Build output directory** | `frontend/dist` |
| **Deploy command** | Leave **empty** (Git integration deploys `frontend/dist` automatically) |

**Remove** custom deploy command `npx wrangler deploy` if present.

### If Cloudflare requires a deploy command

Use Pages deploy, not Workers deploy:

```bash
npm ci && npm run build && npx wrangler pages deploy frontend/dist --project-name=phill-job-application-copilot
```

## Environment variables (Cloudflare → Settings → Environment variables)

| Name | Example |
|------|---------|
| `VITE_SUPABASE_URL` | `https://xxxx.supabase.co` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | `eyJ...` (anon/publishable only) |
| `VITE_PROJECT_DOMAIN` | `phill-application-copilot.uk` |

Never put `SUPABASE_SECRET_KEY` or AI keys in Cloudflare (frontend is public).

## Custom domain

1. Pages → **Custom domains** → add `phill-application-copilot.uk`
2. Ensure DNS points to Cloudflare (nameservers or CNAME to Pages)

## Local test before push

```bash
npm ci
npm run build
npx wrangler pages deploy frontend/dist --project-name=phill-job-application-copilot
```

## GitHub Actions (backend)

Frontend CI only verifies build. Pipelines need **repository secrets** (see `docs/api-keys.md`):

- `SUPABASE_URL`, `SUPABASE_SECRET_KEY` (required)
- `TAVILY_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, etc.

If Actions logs show empty `SUPABASE_URL`, secrets are missing on **this repo** under Settings → Secrets → Actions.
