# Master Strategy: Multi-Vertical Collectibles Asymmetry Framework

**Date**: 2026-09-14 evening
**Author**: Hugo (capturing user's verbal strategy)
**Audience**: Hugo, Cosmo, future agents (any new agent added for new silos)
**Status**: 🔒 Locked strategy — read this before adding/changing anything

---

## TL;DR (30 seconds)

We're not building a card tool. We're building a **multi-vertical framework
for trading in markets with wide pricing bands caused by information and
geographical asymmetry**. Cards is vertical #1. Coins, comic books, and
others are vertical #N.

**The opportunity**: In markets with imperfect information, the bid-ask spread
is artificially wide. People overpay because they don't know what's "fair."
Our framework narrows that spread by surfacing real market data — and we
capture value at multiple layers of the stack.

---

## The Core Insight (verbatim from user, 2026-09-14)

> "Each market (cards, coins, comicbooks etc) are markets that we can attach
> this framework to, and lower the spread between the buy and ask price.
> I am not trying to solely do one market, the end goal is to do markets
> with wide pricing bands due to information/geographical dislocation/ etc
> asymmetries that people trade."

### What this means

**The market we target is NOT "card collectors."**
**The market we target is "asymmetric information markets."**

Cards happen to be the first vertical. We chose it because:
- Wide price dispersion (raw vs graded, sub-grade variations)
- Geographical dispersion (NY vs LA collectors see different supply)
- Information asymmetry (some sellers know pop counts; most don't)
- High enough per-item value to justify a subscription alert

**Other verticals with the same characteristics**:
- **Graded coins** (PCGS/NGC, $50-50,000 per coin)
- **Comic books** (CGC-graded, $10-100,000 per book)
- **Vintage sports memorabilia** (game-worn, autographed, $100-1M+)
- **Trading cards (non-sports)**: Pokémon, Magic, vintage Garbage Pail Kids
- **Vintage toys** (Star Wars, G.I. Joe, He-Man in original packaging)
- **Vintage watches** (back to where we started — Vostok, vintage Rolex, etc.)
- **Stamps** (rare collections, $100-100,000)
- **Vinyl records** (first pressings, rare variants)
- **Wine** (rare vintages, investment-grade bottles)

**Each is a vertical with the same DNA**: imperfect information + dispersed
sellers + per-item value high enough to support tooling.

---

## Why This Matters Strategically

### 1. The framework compounds

```
Vertical #1 (Card Scout):  ~65h dev → framework + card-specific code
Vertical #2 (Coin Scout):  ~50h dev → ~80% reuse from #1
Vertical #3 (Comic Scout): ~50h dev → ~80% reuse from #1+#2
Vertical #4 (Toy Scout):   ~50h dev → ~80% reuse from #1+#2+#3
                              ─────────
                              Total dev: ~215h for 4 verticals
                              Per-vertical cost after #3: ~35h marginal
```

After 3-4 verticals, the framework has:
- 4 sets of customer relationships
- 4 sets of per-vertical actors
- 1 robust bot framework (tested across markets)
- 1 statistical engine (validated across markets)
- The compounded moat is **the framework itself**

### 2. Information asymmetry is durable

This isn't a fad. Asymmetric information in collectibles markets is **structural**:
- New collectors enter constantly (don't know fair prices)
- Geographic dispersion (regional shows, regional pricing)
- Authentication opacity (PSA knows, casual buyer doesn't)
- Population reports are technical (most sellers don't read them)
- Time asymmetry (collector doesn't have time to track 100 listings/day)

**Card Scout narrows the spread by giving buyers confidence.** That's the product.

### 3. The revenue model scales per vertical

```
Vertical #1 (Cards):   10 customers × $25/mo = $250/mo
Vertical #2 (Coins):   20 customers × $25/mo = $500/mo  (cards warms up market)
Vertical #3 (Comics): 15 customers × $25/mo = $375/mo  (compounding credibility)
Vertical #4 (Toys):   10 customers × $25/mo = $250/mo
                       ───────────────────────
                       Total: $1,375/mo at 55 customers across 4 verticals
```

At 5 customers per vertical (20-25 total), we're at $500/mo. **Recession-resistant** because collectibles countercyclical — when stocks dip, people buy collectibles.

### 4. The "small fee for LLM builders" angle

User: "I wouldn't mind having actors available for LLMs to help people find
what they are looking for and we get a small fee since we are already doing
alot of the heavy lifting."

This is the **infrastructure play**. We do the heavy lifting (scraping +
parsing + tier mapping). LLMs are the new interface layer. By exposing our
data via paid actors, we capture rent from the LLM ecosystem without having
to build an LLM product ourselves.

**The risk**: publishing the WRONG actors gives competitors the data layer
to clone our verticals fast. The hard policy (actors stay private) protects
this.

---

## What Each Layer Of The Stack Is

### Layer 1: Data acquisition (scrapers / actors)

**What's reusable across verticals**: HTTP fetching pattern, Bright Data proxy, HTML parsing patterns, retry logic, observability.

**What's vertical-specific**: The website (PSA.com for cards, PCGS.com for coins, GPAnalysis.com for comics), the authentication flow, the HTML schema.

**Status**: Currently 3 actors for cards. Future = 2 actors per vertical.

### Layer 2: Statistical engine (the math)

**What's reusable**: 90% confidence intervals (mean ± 1.645×SD), per-grade market table construction, sold-counting logic, trend detection (7d/30d deltas).

**What's vertical-specific**: Grade scales (PSA 1-10 for cards, PCGS 1-70 for coins), price tier definitions (manual_only_price vs coin-specific names).

**Status**: Built for cards. Future = parameterize by vertical.

### Layer 3: Alert orchestration (the bot)

**What's reusable**: Discord webhook integration, customer filtering, snapshot saving, alert frequency logic, "below market" detection.

**What's vertical-specific**: None. The bot is fully generic.

**Status**: Built for cards. Future = same bot serves all verticals.

### Layer 4: User-facing format (the ticker)

**What's reusable**: Discord embed structure, header/title/footer formatting, color coding, the Bloomberg-style table layout.

**What's vertical-specific**: Grade labels (PSA 10 vs PCGS PR70), price tier names.

**Status**: Built for cards. Future = same formatter, parameterized labels.

### Layer 5: Customer acquisition + billing

**What's reusable**: Discord onboarding flow, subscription management (TBD), customer support templates.

**What's vertical-specific**: Marketing copy per market, target communities per vertical.

**Status**: Card Scout only. Future = each vertical gets its own customer pipeline.

---

## The Competitive Moat (Per Layer)

| Layer | Our moat | A competitor cloning our scrapers gets... |
|---|---|---|
| 1. Scrapers | 6 months of reverse-engineering | Same scrapers (if leaked) |
| 2. Stats engine | 90% CI math (commodity math, but the implementation is clean) | They could replicate in a weekend |
| 3. Alert bot | The orchestration (data → Discord flow) | They could clone in a week |
| 4. Ticker format | The Bloomberg-style presentation | They could clone |
| 5. Customer relationships | Trust + customer service + multi-vertical credibility | **This is the real moat** |

**Insight**: Scrapers are NOT the moat, even though they're the most "novel"
piece. **Customer relationships and cross-vertical trust are the moat.**

**Implication**: Even if a competitor clones our scrapers (via leaked code
or their own reverse-engineering), they still need to:
1. Build the framework (bot, math, format)
2. Acquire customers in each vertical
3. Build credibility across 3+ verticals
4. Earn the trust of paying customers

That's 18-24 months of work, not 6. The compounding comes from having
multiple verticals of paying customers.

---

## What This Changes About the Publishing Decision

| Strategy | Verdict | Reasoning |
|---|---|---|
| Publish Card Scout's 3 actors | ❌ NEVER | Even "general-purpose" leaks our vertical #1 data layer |
| Publish generic framework parts (HTTP fetcher, math, formatter) | ✅ When ready | Doesn't leak verticals; helps LLM builders |
| Publish vertical-specific actors for coin/comic/toy | ❌ NEVER | Same reasoning as cards |
| Publish the framework itself (multi-vertical bot code) | ⚠️ MAYBE in year 3 | Once we have 3+ verticals, the framework is the moat, not the verticals |

---

## The 5-Year Vision (User-Approved)

```
Year 1 (now):   Card Scout only, 10+ customers, framework validated
Year 2:         Add Coin Scout, 25 customers across 2 verticals
Year 3:         Add Comic Scout, 50 customers across 3 verticals
                Publish generic framework parts as paid actors
Year 4:         Add Toy Scout + watch/record verticals, 100+ customers
Year 5:         Multi-vertical platform, 200+ customers, $5K+/mo revenue
                Publish framework as commercial product (B2B SaaS)
```

---

## Cross-Agent Forward Vision (User-Requested)

User said:
> "Exactly, this is part of the reason I want you and Cosmo to see the future.
> He has some of this in his notes/memory but I haven't told him that each 
> market... [is a vertical we can attach to]"

**Cosmo has NOT been told this directly.** This doc is the canonical version.
Cosmo should read this whenever starting new work.

**Future agents (any agent added for a new silo)** should:
1. Read this doc FIRST before designing any vertical
2. Apply the framework (don't reinvent per vertical)
3. Identify which layer they're working on (1-5)
4. Make sure changes propagate cleanly across verticals
5. Update this doc with new learnings

---

## Decision Triggers (When To Do What)

| Trigger | Action |
|---|---|
| 1 customer (Jim) | Focus on Card Scout. Don't expand yet. |
| 5 customers | Start documenting framework's generic parts |
| 10 customers | Consider publishing generic framework parts as paid actors |
| 25 customers (across 1 vertical OR 2) | Consider scoping Coin Scout |
| 50 customers | Begin building Coin Scout (~50h dev) |
| 100 customers (across 2-3 verticals) | Publish framework as commercial product |

---

## Reference

- Master ticker spec: `For You/Plans/card-scout-ticker-system-spec-2026-09-14.md`
- Self-host + revenue plan: `For You/Plans/self-host-migration-and-store-revenue-plan-2026-09-14.md`
- Hard policy (publishing rules): see working notes Session 12-13
- Multi-vertical strategy discussion: working notes Session 13 (this doc is the canonical version)

---

## TL;DR (one more time, in case anyone skimmed)

**Card Scout = vertical #1 of a multi-vertical collectibles asymmetry
framework.** We attach this framework to any market with wide bid-ask
spreads due to imperfect information. Each new vertical is ~50h of dev work
+ 80% framework reuse. The compounding creates the moat. **Customer
relationships across multiple verticals are what we actually own.**

Read this before touching anything. Especially Cosmo.
