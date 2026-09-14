# Plan: Self-Host Migration + Apify Store Revenue Strategy

**Date**: 2026-09-14
**Author**: Hugo
**Status**: 📋 Plan only (no code changes yet)
**Triggers**: (a) operational cost reduction at scale, (b) revenue offset via store actors

## Executive Summary

We currently run our 3 actors on Apify for ~$7/mo (low scale). Two strategic
options exist:

1. **Self-host on a VPS** when scale justifies migration (saves $5-7/mo at
   current scale, $50-100/mo at 100 customers)
2. **Publish 2 actors to Apify Store as paid actors** — turn infrastructure
   cost into a profit center, offset our own usage fees

**Recommendation**: Do both, in this order — publish to store first (passive
income, zero migration cost), then self-host when we hit the scale threshold.

---

## Part 1: Self-Host Migration Plan (When Scale Demands It)

### When to migrate

| Trigger | Action |
|---|---|
| 1-5 customers, current usage | **Stay on Apify.** Migration not worth dev time. |
| 5-10 customers, >$30/mo Apify spend | **Evaluate.** Migrate eBay actor first (highest cost). |
| 10+ customers, >$70/mo Apify spend | **Migrate all 3 actors.** Self-hosting wins. |

### What migration looks like

#### Architecture: Same code, different runner

**Current (Apify)**:
```
Bot → REST API → Apify cloud → our actor code → Bright Data → eBay
            (Apify wrapper around main())
```

**Future (Self-hosted)**:
```
Bot → HTTP POST → FastAPI wrapper on VPS → our actor code → Bright Data → eBay
```

We keep the same `main.js`. We just write a 50-line FastAPI server that:
1. Accepts the same input schema
2. Calls `main()` synchronously
3. Returns the same JSON output

#### Step-by-step migration (1 weekend per actor)

For each actor:

**Step 1: Stand up the VPS** (1 hour)
- Recommended: Hetzner CX22 (4GB RAM, 2 vCPU) — €4.85/mo
- Alternative: Oracle Cloud Always-Free tier (4 CPU, 24GB ARM) — $0/mo
- Install: Node.js 20, Python 3.11, systemd

**Step 2: Build FastAPI wrapper** (1 hour)
```python
# wrapper/ebay_actor_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, json
from pathlib import Path

app = FastAPI()
ACTOR_DIR = Path(__file__).parent.parent / "card-scout/actors/ebay-etsy-watch-scraper-monetized"

class RunRequest(BaseModel):
    smartSearch: str = ""
    presets: list = []
    customSearchTerms: list = []
    marketplaces: list = ["ebay"]
    maxListingsPerQuery: int = 30
    brightDataToken: str
    includeSold: bool = False

@app.post("/run")
async def run_ebay_actor(req: RunRequest):
    """Calls actor's main() with the same input shape Apify uses."""
    input_json = req.model_dump_json()
    # Write input to a file, run main() with --input, capture output
    input_path = ACTOR_DIR / "input.json"
    input_path.write_text(input_json)
    
    proc = subprocess.run(
        ["node", "main.js"],
        cwd=ACTOR_DIR,
        capture_output=True,
        timeout=360
    )
    if proc.returncode != 0:
        raise HTTPException(500, f"Actor failed: {proc.stderr[:500]}")
    return json.loads(proc.stdout)
```

**Step 3: Update the bot's call signature** (15 min)
```python
# In discord_alert_bot_v3.py
APIFY_BASE = "https://api.apify.com/v2"
ACTOR_EBAY = "AtQq66Qn8FB7aLq2l"

def run_apify_search(...):
    # OLD: requests.post(f"{APIFY_BASE}/acts/{ACTOR_EBAY}/runs", ...)
    # NEW: requests.post("http://vps.local:5001/run", json=...)
    # Same response shape. Bot doesn't care which one.
```

**Step 4: Run both in parallel for 1 week** (no code change, just config)
- Send 50% of traffic to Apify, 50% to VPS
- Compare cost, latency, error rate
- Flip the switch when confident

**Step 5: Decommission Apify runs** (5 min)
- Set Apify actor `isDeprecated: true` (still works, but new users see warning)
- Stop our own cron from using it
- Cancel Apify subscription if cost < $5/mo

#### Cost comparison (100 customers scale)

| Component | Apify | Self-hosted VPS |
|---|---|---|
| Compute | $70/mo (10x current) | $5.30/mo (Hetzner CX22) |
| Bright Data | Same ($1.50/GB) | Same ($1.50/GB) |
| Maintenance | $0 (Apify handles) | ~2 hrs/mo (updates, monitoring) |
| Total | **~$70/mo** | **~$5-10/mo + 2 hrs/mo engineer time** |
| Savings | — | **$60-65/mo at 100 customers** |

### Risks & mitigations

| Risk | Mitigation |
|---|---|
| VPS goes down | Health check + auto-restart via systemd; UptimeRobot alert |
| Bright Data rate limits hit | Same risk as Apify; rotate proxies if it becomes a problem |
| Code changes (PSA, etc.) need re-deployment | git pull + restart; or use watchgod for auto-reload |
| Backup actor on Apify (paid plan) | Keep actor code published; can flip back if VPS dies |
| Bot needs API URL change | Add env var `ACTOR_BASE_URL` so we don't touch code |

---

## Part 2: Publish Actors to Apify Store (Revenue Strategy)

### Why this makes sense

1. **Zero marginal cost** — once code exists, Apify hosting is paid by users
2. **Users pay Apify** for the compute, you get a **revenue share** (~80/20)
3. **Validates market** — if others pay for our actors, our internal use is justified
4. **Marketing funnel** — store listings drive users to Card Scout itself
5. **Defensive moat** — if we publish first, competitors can't copy "our" version

### What we have (asset inventory)

| Actor | Status | Public? | Cost to publish |
|---|---|---|---|
| eBay + Etsy Marketplace Scraper | Build 0.4.11 | **YES (1 user — us)** | Already public, just need to enable pricing |
| PSA Population Lookup | Build 1.0.3 | No | Make public, add pricing |
| Sportscardspro + PriceCharting Lookup | Build 1.2.2 | No | Make public, add pricing |

### What's "secret sauce" vs commoditized

This is the critical question. Let me audit each actor:

#### eBay actor — secret sauce?

**Commoditized (safe to publish):**
- `bdFetch()` — generic Bright Data HTTP wrapper
- `buildEbaySearchUrl()` — builds URL with eBay's parameters
- `parseEbayListingsFromHtml()` — extracts title, price, shipping from HTML

**Secret sauce (DO NOT publish):**
- `interpretQuery()` — our "smart search" expansion logic (preset expansion)
- `matchPreset()` — knows about specific market segments (cards, watches)
- Custom presets (`cards-sports`, `cards-pokemon`, etc.) — these are domain-specific

**Verdict**: **Publish a stripped-down version** that supports general eBay/Etsy search but NOT the preset taxonomy. Generic users get a great eBay scraper. Our Card Scout keeps the smart expansion.

#### PSA actor — secret sauce?

**Commoditized (safe to publish):**
- Puppeteer/Playwright setup
- PSA login flow (Descope widget)
- Generic pop report parser

**Secret sauce (DO NOT publish):**
- (Looked at this actor — it's mostly generic scraping. PSA's site is the same for everyone.)

**Verdict**: **Publish entirely.** Our competitive edge is the bot integration + per-grade ticker, not the scraper itself. Anyone scraping PSA's public pop reports gets the same data.

#### Sportscardspro + PriceCharting actor — secret sauce?

**Commoditized (safe to publish):**
- Bright Data fetch
- HTML parsing of price tiers
- `sales[]` array extraction

**Secret sauce (DO NOT publish):**
- (Per working notes: "sportscardspro + pricecharting = SAME backend" was a discovery. The price tiers `manual_only_price`, `graded_price` etc. are discovered knowledge — but anyone could reverse-engineer them.)

**Verdict**: **Publish entirely.** Generic users get a price-charting scraper. Our bot gets the same data + we don't have to maintain it.

### Recommended store strategy: 3-actor product suite

**Product 1: "Trading Card Price Lookup" (sportscardspro + pricecharting actor)**
- Pricing: $0.50 per 1000 results (or $5/mo for unlimited with cap)
- Description: "Pull per-grade prices for any PSA/BGS/CGC-graded card. Returns raw + graded prices across all major card categories."
- Use case: eBay sellers checking market prices, TCGPlayer competitors, grading services

**Product 2: "PSA Population Report Lookup"**
- Pricing: $0.30 per 1000 results
- Description: "Authenticated PSA population data — get pop counts for any card set or individual card. Supports historical pop report snapshots."
- Use case: Card graders, investors tracking scarcity, set registry users

**Product 3: "eBay + Etsy Marketplace Scraper"** (stripped down)
- Pricing: $0.50 per 1000 results
- Description: "General-purpose eBay + Etsy scraper. Supports active listings, sold listings, custom queries. Bright Data proxy support."
- Use case: General e-commerce research, dropshippers, market analysts
- **NOTE**: Strip the preset taxonomy. Make it a generic search tool.

### Revenue model (APIs revenue share)

Apify's standard revenue share for paid actors:
- **80% to actor owner**
- 20% to Apify

At our current scale, we'd earn roughly:
- Sportscardspro actor: $0.50/1000 results × 100K results/mo = **$50/mo revenue**
- PSA actor: $0.30/1000 × 50K = **$15/mo revenue**
- eBay actor: $0.50/1000 × 200K = **$100/mo revenue** (high demand for general scrapers)

**Conservative estimate: $50-100/mo passive revenue** once store actors have users.

### Pricing experiments to run

1. **Free tier + paid overage** — drives adoption, revenue from power users
2. **Per-result vs flat monthly** — different customers prefer different models
3. **Bundle pricing** — discount for using all 3 actors together

### What's protected if we publish

**Our competitive moat** (per the master ticker spec) is NOT the scraping:
- Per-grade 90% confidence intervals (statistical math)
- "Below-market deals" detection (algorithmic, not data)
- Discord alert flow + customer-specific filtering
- The TICKER FORMAT — Bloomberg-style output

Anyone can scrape eBay/PSA/PriceCharting and get raw data. **Nobody else
has the ticker format + 90% CI + alert flow.** That's what we charge for.

### Implementation timeline

**Week 1**: Strip eBay actor's preset taxonomy, build "store version" of all 3
  actors with cleaner input schemas (just basic eBay search, no smart expansion)
**Week 2**: Set up Apify Store listings (descriptions, screenshots, pricing)
**Week 3**: Submit for Apify Store review + add "Related Actor" links to
  Card Scout marketing site (when it exists)
**Week 4**: First revenue. Track usage, iterate on pricing.

**Monthly maintenance**: ~2 hours (handle user questions, fix edge cases
  users find, respond to Apify Store review moderation).

### Risk: Leaking secret sauce

The biggest risk is **recreating a competitor by giving away the scraper code**.

**Mitigation**:
- **Strip the eBay actor** — keep preset expansion in the bot, not the actor
- **Use code obfuscation** on published actor code (Apify Store hides source anyway)
- **Don't include test data or sample queries** that hint at our card catalog
- **Test the published version** yourself to verify nothing leaks

The reality: our scraper logic isn't proprietary. The value is in the **alert
flow + statistical math + customer relationship**. Publishing scrapers helps
us, doesn't hurt us.

---

## Part 3: Decision Matrix

| Strategy | When to do it | Cost | Revenue | Risk |
|---|---|---|---|---|
| **A. Stay on Apify + publish 2 actors** | Now | $0 (existing spend) | $50-100/mo passive | Low — just makes our code available |
| **B. Self-host + publish 2 actors** | When >$30/mo Apify | +$5-10/mo VPS | $50-100/mo passive | Medium — VPS maintenance |
| **C. Self-host + keep actors private** | When >$70/mo Apify | -$60/mo savings | $0 | Medium — engineering time, no revenue |

**My recommendation as CTO**: Start with **A** (publish actors, stay on Apify).
When monthly Apify spend exceeds $30, add **B** (self-host the actor we use
the most + keep all 3 published for revenue).

This gets you:
- **Immediate revenue** ($50-100/mo passive)
- **Lower risk** (no migration until scale demands it)
- **Future optionality** (self-host path is documented, ready when needed)

---

## Implementation Steps (When You Approve)

If you approve Part 2 (publish actors), here's the work order:

1. **Hugo** (1 hour): Strip preset taxonomy from eBay actor → build "store edition"
2. **Hugo** (1 hour): Write store listings (description, screenshots, pricing)
3. **Hugo** (30 min): Update each actor's `actor.json` with monetization fields
4. **Hugo** (15 min): Submit to Apify Store for review
5. **You** (when ready): Approve pricing tier choices
6. **Wait** (3-7 days): Apify Store review
7. **You + Hugo** (1 hour): Promote in Card Scout marketing materials

### What I need from you

- [ ] **Approve publishing** the 2 actors (PSA + sportscardspro) to Apify Store
- [ ] **Approve pricing model** (my default: $0.30-$0.50 per 1000 results)
- [ ] **Decide on eBay actor**: publish a stripped-down version OR keep private?
- [ ] **Decide on revenue destination**: Apify credits vs bank payout?

### What I'll do

- [ ] Build store-grade versions of the actors (cleaner schemas, no Card-Scout-specific logic)
- [ ] Write store listings
- [ ] Submit for Apify review
- [ ] Report back when actors are live + first revenue starts

---

## Final Note: This is the right time to do this

- Card Scout has a working bot + 1 customer
- The actors are stable (no big code changes expected soon)
- We have 0 marketing presence on Apify Store (1 user, the bot)
- Revenue is the only thing missing from the puzzle

**Cost to act**: ~4 hours of my time + your sign-off on pricing
**Reward**: $50-100/mo passive, scales with market, AND validates that our
code is worth running at all (if nobody else pays for it, maybe nobody needs it)

That's a great deal.
