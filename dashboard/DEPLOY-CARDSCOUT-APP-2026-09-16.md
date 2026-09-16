# Card Scout Deployment Guide (Sept 16, 2026)

## Quick summary

| Item | Value |
|---|---|
| **Hosting** | Render.com (Starter $5/mo) |
| **Domain** | cardscout.app (Porkbun, $8.75/yr) |
| **Persistent disk** | $1/mo extra (for SQLite) |
| **TOTAL** | **$6.25/mo** |
| **Deploy time** | ~30 min |

## Architecture (one service, two apps)

```
cardscout.app/
├── /                     ← Public landing page (marketing)
├── /deals                ← Top 10 deals across platform
├── /pricing              ← 4-tier pricing page
├── /sitemap.xml          ← SEO sitemap
├── /robots.txt           ← SEO robots
├── /health               ← Health check endpoint
│
├── /dashboard/login      ← Customer login (webhook auth)
├── /dashboard/<id>       ← Customer dashboard (auth required)
├── /dashboard/<id>/update ← Update cards (POST)
└── /logout               ← Logout
```

## Step-by-step (founder does ~25 min)

### Step 1: Buy domain at Porkbun (5 min)

1. Go to https://porkbun.com
2. Sign up (free)
3. Search "cardscout.app"
4. Purchase ($8.75 first year)
5. Free WHOIS privacy + free SSL
6. Save credentials

### Step 2: Sign up for Render (3 min)

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your GitHub repos

### Step 3: Push code to GitHub (5 min)

If your code isn't on GitHub yet:

```bash
cd C:\Users\J\Documents\LLM\card-scout
git remote add origin https://github.com/<your-username>/card-scout.git
git push -u origin master
```

(I can guide you through this — just say "push to github")

### Step 4: Configure Render (10 min)

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Select your `card-scout` repo
3. Render auto-detects `render.yaml` and creates the service
4. Before deploying, set these environment variables:
   - `SECRET_KEY` = random 64-char hex (I can generate this)
   - `DATABASE_URL` = `sqlite:////data/card_scout.db` (already set in render.yaml)
   - `GOOGLE_SHEET_ID` = `18NgDXIJvzwZRJODWwuNELDQgKLLJDpEr-prlHHvEuds`
   - `GOOGLE_APPLICATION_CREDENTIALS` = paste JSON content of SA key
   - `STRIPE_SECRET_KEY` = from .env (we have this)
   - `STRIPE_PAYMENT_LINK` = from .env

5. Click **"Apply"** to deploy
6. Wait ~5 min for first deploy

### Step 5: Copy database to persistent disk (5 min)

In Render shell:

```bash
mkdir -p /data
# Upload your local card_scout.db
# (You'll need to do this via S3 or scp — ask me to help)
```

Or: start fresh, customer signs up via Google Form, dashboard fetches their data.

### Step 6: Add custom domain (2 min)

1. In Render, go to your service → Settings → Custom Domains
2. Add `cardscout.app` and `www.cardscout.app`
3. Render gives you CNAME records
4. Add these to Porkbun DNS settings
5. SSL is automatic

### Step 7: Verify (5 min)

1. Visit https://cardscout.app — should see landing page
2. Visit https://cardscout.app/pricing — should see 4 tiers
3. Visit https://cardscout.app/deals — should see "no deals" (we have no spread data yet)
4. Visit https://cardscout.app/dashboard/login — should see login form
5. Visit https://cardscout.app/health — should return JSON healthy

## Environment variables to set

| Variable | Where to get it |
|---|---|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Set in render.yaml (already there) |
| `GOOGLE_SHEET_ID` | From .env |
| `GOOGLE_APPLICATION_CREDENTIALS` | Paste JSON content (one line) |
| `STRIPE_SECRET_KEY` | From .env |
| `STRIPE_PAYMENT_LINK` | From .env |
| `FLASK_COOKIE_SECURE` | Set to `true` (for HTTPS) |

## What needs to happen next (your time vs my time)

| Step | Time | Who |
|---|---|---|
| Buy domain | 5 min | You |
| Sign up Render | 3 min | You |
| Push to GitHub | 5 min | You (I guide) |
| Set env vars | 5 min | You |
| Deploy | 5 min | Auto |
| Verify | 5 min | You + me |
| **YOUR TOTAL** | **~25 min** | — |
| Build the rest | Already done | Me (today) |

## Backup / Disaster Recovery

| What | How |
|---|---|
| Daily DB backup | Add cron job that copies /data/card_scout.db to S3 |
| Code rollback | Render auto-deploys from git, can rollback to any commit |
| Disaster recovery | Restore DB from S3 backup + redeploy |

(Future enhancement — not V1 critical)

## Pricing math reminder

| Tier | Revenue | Customers needed for $1K MRR |
|---|---|---|
| Casual $15 | $15/mo each | 67 |
| Standard $30 | $30/mo each | 33 |
| Dealer $75 | $75/mo each | 13 |
| Pro $150 | $150/mo each | 7 |

7 Pro customers = $1,050/mo revenue. Hosting costs $6.25/mo. **170x margin.**

## When to upgrade

| Stage | When | Move to |
|---|---|---|
| 1-10 customers | Now | Render Starter ($5/mo) |
| 10-100 customers | ~25 customers | Render Standard $25/mo (better CPU) |
| 100-500 customers | ~100 customers | Render Pro $85/mo (always-on, more RAM) |
| 500-1000 customers | ~500 customers | Move to Hetzner VPS (€4.50/mo + full control) |
| 1000+ customers | When revenue supports | Dedicated server or cloud (e.g., AWS) |

## Files for deployment

| File | Purpose |
|---|---|
| `render.yaml` | Render deployment config |
| `dashboard/app.py` | Flask app (customer dashboard + public site) |
| `dashboard/public_site.py` | Public site blueprint |
| `dashboard/static/style.css` | Public site styles |
| `dashboard/requirements.txt` | Python dependencies |
| `dashboard/DEPLOY.md` | Old deployment notes (still useful) |

## What's NOT deployed yet

1. **Customer webhook URLs** — secrets in DB need to be in env vars
2. **GCP SA key** — paste as env var in Render dashboard
3. **Stripe webhook handler** — V3 Stripe integration pending
4. **Cron jobs** — need to add Render cron for daily bot runs
5. **Backup strategy** — manual S3 backup for now

## Open fires for next session

1. Sign up for Porkbun (5 min)
2. Sign up for Render (3 min)
3. Generate SECRET_KEY (1 min)
4. Push to GitHub (5 min, I guide)
5. Configure Render env vars (10 min)
6. Deploy (5 min)
7. Verify all routes (5 min)

**Total: ~35 min to live production**

Once live, you have:
- Self-serve customer dashboard
- Public landing page (marketing)
- Top deals page (ad revenue ready)
- Pricing page (Stripe-ready)
- SEO foundation
- Health checks

## Questions?

Ask Hugo. One fire at a time. 🎯
