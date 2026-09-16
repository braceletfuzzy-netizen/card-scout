# Card Scout Website Strategy (Sept 16, 2026)

## Time
Sept 16, 2026 (evening, founder inquiry)

## Status
**DRAFTED.** Founder asked: "Tell me about the web-hosting page"

## Two different things — don't conflate

| Thing | Purpose | User | Revenue |
|---|---|---|---|
| Customer Dashboard | Manage card alerts | Customers | Subscription |
| Public Website | Browse top deals | Anyone | Ad revenue |

## Current state

### Have (customer dashboard)
- `dashboard/app.py` (432+ lines Flask, gunicorn-ready)
- Customer login via Discord webhook
- Self-serve card management
- NOT deployed (localhost only)
- Cost to deploy: $5/mo (Render Starter)

### Don't have (public website)
- Top X deals page
- Landing page
- Pricing/marketing pages
- Ad slots
- SEO optimization

## Founder's beta notes (Sept 16, source for this work)

> "give a top x(5, 10) list on our webpage. I am undecided on
> the number of listings they can view on the website. This driving
> traffic to our website will eventually open the door for ad revenue."

> "we are only as useful as we are accurate"

## Two interpretations of "top X deals"

### Option A: Top X deals across platform
```
Top 10 deals this week (across all customers)
1. Bo Jackson 1987 Donruss PSA 10 — $450 (12% below market)
2. Black Lotus Alpha — $87,500 (4% below market)
...
```
- Better for SEO (more search terms)
- Worse for ad revenue (fewer pageviews per user)

### Option B: Top X deals per card
```
Bo Jackson PSA 10 — Top 10 deals:
1. $450 - "Bo Jackson rookie PSA 10" [eBay link]
2. $475 - "1987 Donruss Bo Jackson" [eBay link]
...
```
- Better for ad revenue (more pageviews)
- Worse for SEO (fewer search terms per page)

**Founder undecided on count (5 vs 10).**

## Architecture: One Render service, two apps

```
card-scout.onrender.com/
├── /                    ← Public landing page (NEW)
├── /deals               ← Public top X deals (NEW, ad revenue)
├── /pricing             ← Marketing/pricing (NEW)
├── /dashboard/<id>      ← Customer dashboard (existing)
└── /dashboard/login     ← Customer login (existing)
```

Public site = anonymous, SEO-friendly, has ads.
Customer dashboard = behind webhook auth, no ads.

## Build phases

### Phase 1: Deploy dashboard + public landing (1-2 hours)
- Deploy dashboard to Render ($5/mo)
- Add `/` route = public landing page
- Marketing copy + CTA
- Free trial first (Render gives 90 days free for new accounts)

### Phase 2: Add /deals page (2-3 hours)
- Top 10 deals across platform
- Each deal: card name, grade, asking price, market price, % discount
- Click → eBay listing (affiliate link opportunity)
- Ad slots: top, middle, bottom (placeholder for now)

### Phase 3: SEO (built-in)
- Meta tags (title, description, og:image)
- Schema.org markup (Google rich results)
- Sitemap
- Per-card pages (long tail SEO)

### Phase 4: Monetization (when traffic justifies)
- Google AdSense (need 1K+ pageviews/day)
- eBay Partner Network (free, 1-4% commission)
- Affiliate links from deal clicks

### Phase 5: Scale (1K+ customers)
- Newsletter signup
- Email digests of weekly top deals
- Premium content (deal explanations)

## Cost comparison: $5/mo hosting options

| Provider | $5/mo tier | Notes |
|---|---|---|
| **Render Starter** | 512MB RAM, 0.1 CPU | Sleeps after 15min idle |
| **Railway** | $5 credit then pay-as-you-go | Free $5/month |
| **Fly.io** | Free + paid | Free tier small |
| **DO App Platform** | 512MB RAM, 1 vCPU | Reliable |
| **Vercel** | Free | Frontend-only |
| **Netlify** | Free | Static + serverless |

**Render at $5/mo = best fit** (Flask + SQLite + persistent).

## Ad revenue math

| Pageviews/mo | Ad RPM | Revenue |
|---|---|---|
| 10K | $5 | $50 |
| 100K | $5 | $500 |
| 1M | $5 | $5,000 |

Card Scout V1: probably 10-50K pageviews/mo if SEO works
(long tail of "Bo Jackson PSA 10 deal" type queries).

## Total build time estimate
- Phase 1 (landing): 1-2 hours
- Phase 2 (/deals): 2-3 hours
- Phase 3 (SEO): 1-2 hours
- Phase 4 (monetization): 1-2 hours
- **Total: 6-8 hours**

## When to build

### NOW — Don't build yet
- Founder said funds tight, end of month
- Render $5/mo needs funds first

### AFTER $5/mo is available
1. Deploy dashboard (free trial first)
2. Add public routes
3. Submit to Google Search Console

### WHEN traffic justifies (1K+ pageviews/day)
1. Apply for AdSense
2. Add ad slots
3. eBay Partner Network affiliate links

## Tradeoffs

| Pro | Con |
|---|---|
| Diversifies revenue (subscription + ads) | Need traffic (SEO is slow) |
| Public site = marketing channel | Hosting cost ($5/mo) |
| Drives customer signups via SEO | More code to maintain |
| Affiliate links = passive income | Ad networks need traffic thresholds |
| | Founder undecided on top X count (5 vs 10) |

## Decisions captured

### CONFIRMED
- Website is a separate play from customer dashboard
- Public site = anonymous + SEO + ads
- Customer dashboard = behind webhook + no ads
- Top X count: 5 or 10 (founder undecided)
- Ad revenue is a future revenue stream (not V1 priority)

### DEFERRED
- Build timing (waiting on $5/mo funding)
- eBay Partner Network (free to join, defer to Phase 4)
- Google AdSense (need traffic threshold first)

## Open fires

1. When $5/mo is available: deploy dashboard to Render
2. Then add public landing + /deals pages
3. Then SEO + Google Search Console
4. Then ad integration when traffic justifies

## Related docs

- `For You/Plans/cost-cutting-roadmap-2026-09-16.md` (overall cost plan)
- `For You/Plans/z-score-framework-2026-09-16.md` (math thesis for deals)
- `dashboard/app.py` (existing customer dashboard code)
