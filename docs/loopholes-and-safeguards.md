# Loopholes and Safeguards — Risk Register

**Purpose:** Document known failure modes, abuse vectors, and spec loopholes for Stage 1 with **concrete mitigations** already designed or required before production cron.

Each risk uses: **ID** | **Risk** | **Impact** | **Safeguard** | **Verification**

---

## 1. Data integrity risks

### R1 — Duplicate opportunities on re-scrape

| Field | Detail |
|-------|--------|
| **Risk** | Same job posted daily creates multiple inbox rows |
| **Impact** | User loses trust; wasted review time |
| **Safeguard** | `url_hash` UNIQUE on `opportunities`; `content_hash` dedup; `DuplicateMergeService` preserves `viewed` |
| **Verify** | Re-run scrape on known URL; count stays 1; `times_seen` increments |

### R2 — Dedup merge resets viewed state

| Field | Detail |
|-------|--------|
| **Risk** | Merge overwrites `viewed=false` on already-read item |
| **Impact** | User re-reviews same opportunity |
| **Safeguard** | `build_update_payload()` keeps `viewed=true` if either side viewed |
| **Verify** | Mark viewed → inject duplicate → merge → still viewed |

### R3 — Tavily snippet creates opportunity without scrape

| Field | Detail |
|-------|--------|
| **Risk** | Search summary treated as ground truth |
| **Impact** | Hallucinated funding/remote flags |
| **Safeguard** | Tavily → `discovered_urls` only; AI runs on `cleaned_posts` body |
| **Verify** | Disable scraper; confirm no new `opportunities` from Tavily alone |

### R4 — Stale high scores after content change

| Field | Detail |
|-------|--------|
| **Risk** | `content_hash` changes but old score remains |
| **Impact** | Mis-prioritized queue |
| **Safeguard** | Re-analyze when `content_hash` differs from cached `opportunity_ai_analysis` |
| **Verify** | Edit simulated body → hash change → new analysis row |

---

## 2. AI and scoring risks

### R5 — High confidence without evidence

| Field | Detail |
|-------|--------|
| **Risk** | Model returns confidence 85 with empty evidence |
| **Impact** | False positives in high-priority band |
| **Safeguard** | `ai_json_validator`: reject if `confidence > 70` and no evidence |
| **Verify** | Unit test validator with bad JSON |

### R6 — Model disagreement hidden

| Field | Detail |
|-------|--------|
| **Risk** | Single model error drives wrong category |
| **Impact** | PhD listed as client lead |
| **Safeguard** | `VotingEngine` → `manual_review` if agreement &lt; 67% |
| **Verify** | Feed conflicting mock outputs; status manual_review |

### R7 — Unfunded PhD ranked highly

| Field | Detail |
|-------|--------|
| **Risk** | “PhD” keyword without funding proof |
| **Impact** | Time wasted on self-funded roles |
| **Safeguard** | `score_phd`: self_funded → profile_match 15; require `funding_proof` for high evidence_score |
| **Verify** | Fixture with self-funded text; score &lt; 40 |

### R8 — US-only remote scored as worldwide

| Field | Detail |
|-------|--------|
| **Risk** | “Remote” in title but US-only body |
| **Impact** | Irrelevant applications |
| **Safeguard** | `remote_restriction=us_only_remote` → country_score 20; UI warning badge |
| **Verify** | Sample US-only listing; appears in flagged tab |

### R9 — Cloud AI quota blowout

| Field | Detail |
|-------|--------|
| **Risk** | Thousands of posts analyzed daily |
| **Impact** | Unexpected API bill |
| **Safeguard** | `AI_DAILY_CLOUD_CALL_LIMIT`; content-hash cache; quality gate fail skips AI |
| **Verify** | Exceed limit in test env; calls stop; logged in `api_usage_logs` |

### R10 — Ollama unavailable silently degrades

| Field | Detail |
|-------|--------|
| **Risk** | No local model and no cloud keys |
| **Impact** | Empty pipeline |
| **Safeguard** | `health_check.py` warns; queue → `manual_review` |
| **Verify** | Run health check with empty AI config |

---

## 3. Scraping and legal risks

### R11 — Login wall bypass

| Field | Detail |
|-------|--------|
| **Risk** | Storing credentials to scrape LinkedIn etc. |
| **Impact** | Account ban, legal exposure |
| **Safeguard** | `requires_login` sources disabled; captcha → `manual_review` not bypass |
| **Verify** | No login env vars; checklist item in implementation doc |

### R12 — Aggressive scraping IP ban

| Field | Detail |
|-------|--------|
| **Risk** | Too many requests per domain |
| **Impact** | Sources permanently block |
| **Safeguard** | `rate_limit()` per scraper; domain hourly cap (ops); stagger groups |
| **Verify** | Log timestamps between requests ≥ delay |

### R13 — Copyright / full HTML hoarding

| Field | Detail |
|-------|--------|
| **Risk** | Storing entire sites indefinitely |
| **Impact** | Storage cost; legal gray area |
| **Safeguard** | Store text needed for classification; optional HTML trim; export policy |
| **Verify** | `raw_html` nullable; retention job future |

### R14 — Wrong User-Agent / bot blocking

| Field | Detail |
|-------|--------|
| **Risk** | Generic bot blocked |
| **Impact** | Empty `raw_posts` |
| **Safeguard** | Identifiable UA with project URL; fallback chain |
| **Verify** | `requests_bs4` UA string in code review |

---

## 4. Security risks

### R15 — Service role in frontend

| Field | Detail |
|-------|--------|
| **Risk** | `SUPABASE_SECRET_KEY` bundled in Vite |
| **Impact** | Full database read/write for anyone |
| **Safeguard** | Only `VITE_*` publishable keys in build; ESLint/check script |
| **Verify** | `grep SECRET dist/` empty |

### R16 — RLS misconfiguration public read

| Field | Detail |
|-------|--------|
| **Risk** | Opportunities exposed to anonymous users |
| **Impact** | Personal job search data leaked |
| **Safeguard** | RLS enabled; authenticated-only policies; no anon policy on opportunities |
| **Verify** | Supabase policy audit |

### R17 — Secrets in GitHub logs

| Field | Detail |
|-------|--------|
| **Risk** | `echo $GEMINI_API_KEY` in workflow |
| **Impact** | Key in log archive |
| **Safeguard** | Never print secrets; use env injection only |
| **Verify** | Workflow review |

### R18 — Manual URL SSRF

| Field | Detail |
|-------|--------|
| **Risk** | User submits `file://` or internal IP URL |
| **Impact** | Scanner hits internal network |
| **Safeguard** | Allowlist schemes `http/https`; block private IP ranges in validator |
| **Verify** | Submit `http://127.0.0.1` → rejected |

---

## 5. UX and workflow risks

### R19 — Stage 2 button sends email accidentally

| Field | Detail |
|-------|--------|
| **Risk** | Premature automation |
| **Impact** | Embarrassing auto-apply |
| **Safeguard** | Buttons disabled with “Stage 2” label; no Gmail code in Stage 1 |
| **Verify** | UI inspection; no outbound email deps |

### R20 — Review queue starvation

| Field | Detail |
|-------|--------|
| **Risk** | Everything → `manual_review` |
| **Impact** | Dashboard unusable |
| **Safeguard** | Tune voting thresholds; rule pre-filter; source health disable noisy sources |
| **Verify** | Track manual_review % metric &lt; 40% |

### R21 — German C1 jobs ranked top

| Field | Detail |
|-------|--------|
| **Risk** | Profile mismatch |
| **Impact** | Low application success |
| **Safeguard** | `score_job` multiplies down for native German requirements |
| **Verify** | Job with C1 German → score drop |

---

## 6. Operational risks

### R22 — GitHub Actions silent failure

| Field | Detail |
|-------|--------|
| **Risk** | Cron fails without notification |
| **Impact** | Stale data |
| **Safeguard** | GitHub failure emails; `health_check` daily; Overview “last scrape” KPI |
| **Verify** | Force fail workflow; alert received |

### R23 — Chroma CI ephemeral loss

| Field | Detail |
|-------|--------|
| **Risk** | Vectors lost each run |
| **Impact** | Weak RAG until reindex |
| **Safeguard** | Reindex script post-AI; migrate to pgvector |
| **Verify** | rag-index job duration logged |

### R24 — Seed script duplicates sources

| Field | Detail |
|-------|--------|
| **Risk** | Re-seed without upsert key |
| **Impact** | Duplicate scrape load |
| **Safeguard** | Upsert on `external_id` |
| **Verify** | Run seed twice; count stable |

---

## 7. Safeguard implementation matrix

| Safeguard | Component | Doc |
|-----------|-----------|-----|
| URL dedup | DB constraint + url deduper | `database-schema.md` |
| Content dedup | `content_hash_deduper.py` | `scraping-strategy.md` |
| Semantic dedup | `semantic_deduper.py` | `rag-strategy.md` |
| Quality gate | `data_quality_gate.py` | `scraping-strategy.md` |
| JSON evidence | `ai_json_validator.py` | `ai-brain-rules.md` |
| Voting | `voting_engine.py` | `ai-brain-rules.md` |
| Scoring | `scoring_rules.py` | `stage-1-product-plan.md` |
| Tavily rule | `tavily_discovery.py` | `source-strategy.md` |
| Rate limit | `base_scraper.py` | `scraping-strategy.md` |
| Quota | env + `api_usage_logs` | `api-keys.md` |

---

## 8. Pre-production checklist (safeguards)

- [ ] R3 Tavily-only path blocked
- [ ] R7 unfunded PhD scores low in sample set
- [ ] R8 US-only remote flagged
- [ ] R11 no login scraping enabled
- [ ] R15 dist bundle secret scan clean
- [ ] R19 Stage 2 controls disabled
- [ ] R2 viewed preserved on merge test

---

## 9. Incident response (lightweight)

| Severity | Example | Action |
|----------|---------|--------|
| P1 | Service role leaked | Rotate key; audit `audit_logs`; redeploy |
| P2 | Runaway Apify spend | Disable workflow; revoke token |
| P3 | Single source ToS letter | Disable source; export evidence |

---

## 10. Related documentation

| File | Topic |
|------|-------|
| `implementation-checklist.md` | Delivery verification |
| `stage-1-product-plan.md` | Evidence requirements |
| `api-keys.md` | Secret handling |
