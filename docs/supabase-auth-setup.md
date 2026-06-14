# Supabase Auth — email/password login

## Dashboard login mode

Stage 1 uses a private Supabase Auth dashboard with **email/password only**.
The login page keeps the dashboard email pre-filled. Password changes are handled locally with `scripts/bootstrap_auth_user.py`.

### Cloudflare env vars

Set on Cloudflare Pages (and GitHub Secrets for deploy):

| Variable | Example |
|----------|---------|
| `VITE_PROJECT_DOMAIN` | `phill-job-application-copilot.pages.dev` |

Redeploy after changing env vars.

---

## Create or update the password user

### Create the user (one time, local)

Add these to local `.env` only, then run the script:

```bash
BOOTSTRAP_AUTH_EMAIL=phillmhembere@gmail.com
BOOTSTRAP_AUTH_PASSWORD=your-private-password
```

```bash
source .venv/bin/activate
python scripts/bootstrap_auth_user.py
```

Do **not** commit the password to git.

### Lost password

Set a new `BOOTSTRAP_AUTH_PASSWORD` in local `.env` and rerun:

```bash
python scripts/bootstrap_auth_user.py
```

### Supabase provider settings

**Authentication → Providers → Email**

- Enable Email provider: **ON**
- Confirm email: can be **OFF** for solo testing (faster)
- Allow new users: ON (or create user only via script above)

---

## Postgres log: `schema_migrations does not exist`

Harmless for this app if you applied SQL manually. Apply all migrations with `python scripts/apply_migration.py`, then verify with `python scripts/check_schema.py`.
