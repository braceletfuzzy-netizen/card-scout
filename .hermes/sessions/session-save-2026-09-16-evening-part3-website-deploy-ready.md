# Session Save - Sept 16, 2026 (Evening Part 3 - cardscout.app Website)

## Time
Sept 16, 2026 (evening, late)

## Status
**DONE.** Full website built locally, ready to deploy.

## What we shipped this session

### Domain research
- cardscout.com TAKEN (since 2004, German owner)
- Alternative TLDs: cardscout.app $8.75/yr (Porkbun) → founder choice
- Registrar: Porkbun (free WHOIS + SSL, no markup)
- Total cost: $5/mo hosting + $1/mo disk + $8.75/yr domain = **$6.25/mo**

### Website architecture
One Flask app, two experiences:
- `/` -> Public landing page (NEW)
- `/deals` -> Top 10 platform-wide deals (NEW)
- `/pricing` -> 4-tier pricing page (NEW)
- `/health` -> JSON health check (NEW)
- `/sitemap.xml` + `/robots.txt` -> SEO (NEW)
- `/dashboard/login` -> Customer dashboard login (moved from `/`)
- `/dashboard/<id>` -> Customer dashboard (existing)
- `/static/style.css` -> Responsive styles (9.5KB)

### Files created/modified
- `render.yaml` (NEW) — Render deployment config
- `dashboard/public_site.py` (NEW) — Public routes blueprint
- `dashboard/static/style.css` (NEW) — Responsive styles
- `dashboard/app.py` (MODIFIED) — registered site_bp, moved login
- `dashboard/DEPLOY-CARDSCOUT-APP-2026-09-16.md` (NEW) — 30-min deployment guide

### Local test results
All routes verified:
- `GET /` -> 200, new landing page (3294 bytes, "Card Scout — AI-Powered Card Deal Alerts")
- `GET /deals` -> 200, shows empty state (no spread in pricing_bands yet)
- `GET /pricing` -> 200, 4-tier pricing
- `GET /health` -> 200, healthy JSON
- `GET /sitemap.xml` -> 200, XML sitemap
- `GET /robots.txt` -> 200, robots.txt
- `GET /dashboard/login` -> 200, login form
- `GET /static/style.css` -> 200, 9550 bytes CSS

### Bugs fixed during build
1. **stdlib `site` conflict** — renamed `site.py` to `public_site.py`
2. **Stale Flask server** — kill + restart needed after code changes
3. **SQLAlchemy 2.0 syntax** — `text('SELECT 1')` for raw SQL

## Architecture decisions

### One Flask app (not two)
- Both public site + customer dashboard in same `app.py`
- Different routes, different auth (public = no auth, dashboard = webhook auth)
- Same DB, same deployment
- Easy to maintain

### Render vs alternatives
- **Render Starter $5/mo** — chosen
- Alternative: Render free tier (sleeps after 15min idle)
- Future: upgrade to Standard $25/mo when 25+ customers

### Database
- SQLite + persistent disk ($1/mo)
- In production: `DATABASE_URL=sqlite:////data/card_scout.db`
- Migration path: upgrade to Render Postgres free tier if needed

### SEO foundation
- Meta tags (title, description, og:image)
- Sitemap.xml + robots.txt
- Canonical URLs
- Card Ladder future: per-card landing pages for long-tail SEO

## Open fires for founder

### Immediate (today/tonight, ~25 min)
1. Buy cardscout.app at porkbun.com ($8.75 first year)
2. Sign up for render.com (free, GitHub signup)
3. Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
4. Push code to GitHub (I can guide you)
5. Configure Render env vars (5 vars)
6. Deploy (5 min auto)
7. Verify (5 min)

### Next session
1. eBay Developer verification (already in flight)
2. Card Ladder subscription (when ready)
3. Phase 1 PSA search actor (October)
4. Cron job for bot (auto-alerts)
5. Stripe products for new tiers (when ad revenue matters)

### Pending (lower priority)
1. Email field on form
2. 90% CI + 70% CI section
3. Top X deals on website (5 or 10? — built with 10)
4. URL set-page scraping to find specific card URLs
5. eBay Partner Network affiliate links
6. Backup strategy (S3)

## Today's grand total (Sept 16, FINAL)

| Metric | Count |
|---|---|
| Features/docs delivered | 22 |
| Git commits today | ~20 |
| Tests passing | 100+ |
| Modules built | 8 (deal_detector, url_parser, url_orchestrator, url_resolver, public_site, etc.) |
| Infrastructure spent | $0 |
| Time invested | ~8 hours |

## Memory note for next session

When conversation resumes:
- Pricing: Casual $15 / Standard $30 / Dealer $75 / Pro $150
- Cost-cutting roadmap: 5 stages with customer count triggers
- IMMEDIATE: Buy cardscout.app + sign up Render
- Then: GitHub push + deploy (I guide)
- Then: eBay Browse API integration (verification pending)
- Then: Card Ladder (next month)
- z-score framework is the mathematical thesis
- URL search infrastructure ready
- V3 alert layout in production
- 11/12 Jim alerts delivered

## When founder returns

Likely next:
1. Buy cardscout.app
2. Sign up Render
3. Push to GitHub
4. Deploy
5. Verify
6. One fire at a time per founder's preference

## Files for deployment

`render.yaml` — Deploy config (Render reads this)
`dashboard/DEPLOY-CARDSCOUT-APP-2026-09-16.md` — Step-by-step guide

## Summary in one line

**cardscout.app ready to deploy. ~25 min of founder time + $6.25/mo total. The hard part is done.**
