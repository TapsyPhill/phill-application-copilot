# Supabase Auth — fix localhost redirect & login

## Why magic links open `localhost:3000`

Supabase builds confirmation links from **Authentication → URL Configuration → Site URL**.

If Site URL is `http://localhost:3000`, every email link goes there — even when you use Cloudflare.

### Fix in Supabase (required)

1. Open **Authentication → URL Configuration**
2. Set **Site URL** to:

   ```
   https://phill-job-application-copilot.pages.dev
   ```

3. **Redirect URLs** — add all of these:

   ```
   https://phill-job-application-copilot.pages.dev/**
   http://localhost:5173/**
   http://localhost:3000/**
   ```

4. Save.

5. Request a **new** magic link (old links stay invalid — explains `403 Email link is invalid or expired`).

### Cloudflare env vars

Set on Cloudflare Pages (and GitHub Secrets for deploy):

| Variable | Example |
|----------|---------|
| `VITE_PROJECT_DOMAIN` | `phill-job-application-copilot.pages.dev` |
| `VITE_AUTH_REDIRECT_URL` | `https://phill-job-application-copilot.pages.dev/` (optional override) |

Redeploy after changing env vars.

---

## Temporary email + password login

Until magic links are fully configured, use **Email & password** on the login page.

### Create the user (one time, local)

```bash
source .venv/bin/activate
export BOOTSTRAP_AUTH_EMAIL=phillmhembere@gmail.com
export BOOTSTRAP_AUTH_PASSWORD='your-password-here'
python scripts/bootstrap_auth_user.py
```

Do **not** commit the password to git.

### Supabase provider settings

**Authentication → Providers → Email**

- Enable Email provider: **ON**
- Confirm email: can be **OFF** for solo testing (faster)
- Allow new users: ON (or create user only via script above)

---

## Postgres log: `schema_migrations does not exist`

Harmless for this app if you applied SQL manually. Optional: run `supabase db push` or ignore if tables already exist (`scripts/check_schema.py` passes).
