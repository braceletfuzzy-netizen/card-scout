# Hugo Handoff: includeSold=True Bug

# Hugo Handoff: includeSold=True Bug — SUPERSEDED

> **NOTICE**: This bug handoff is now RESOLVED. See `hugo-handoff-includesold-broken-2026-09-14-RESOLVED.md` (commit `6b1d454`).
>
> **TL;DR**: eBay actor's `includeSold=True` returns 0 bytes (BD rate-limited LH_Sold=1 endpoint). Per the ticker spec reframe, we don't need this anymore — sportscardspro+pricecharting actor already provides per-grade sold data. The bot's broken `includeSold=True` flow was REMOVED.
>
> **Original doc below kept for historical reference only.**

## TL;DR (original)

The eBay+Etsy actor returns 1 empty placeholder item when called with `includeSold=True`, instead of fetching sold listings (LH_Sold=1). When called with `includeSold=False`, the same payload returns 60 real items in 45 seconds.

This blocks the "buy + sell spread" feature in Card Scout alerts (v4.271).

## Symptoms

**Bot flow with `includeSold=True`**:
```
[APIFY] Run started: Uaq2qPml0OFtgyi4F
[APIFY] Found 1 items (216s)   ← Empty placeholder
```

**Manual test with `includeSold=False`**:
```
✅ Got 60 items in 45s
   $ 20.00 - Shop on eBay
   $  2.00 - 1995 Topps - Future Star Derek Jeter #199
   $269.00 - 1996 Topps Chrome Derek Jeter #80 Yankees PSA 9
   ... 57 more items
```

**Identical payload** except `includeSold` flag.

## Root Cause Hypothesis

The actor's `main.js` has separate code paths for sold vs active listings. When `includeSold=True`, the actor probably:
1. Hits `https://www.ebay.com/sch/i.html?...&LH_Sold=1` (eBay sold listings endpoint)
2. Either gets blocked by eBay's anti-bot (returns 0 items)
3. Or the parser fails to extract sold items from the sold-page HTML

The actor then falls back to returning the `_summary` placeholder item (1 item, empty title).

## Reproduction

From terminal:
```bash
python -c "
import requests
import time
from pathlib import Path
import importlib.util

bot_path = Path(r'C:/Users/J/Documents/LLM/vostok-tools/scripts/discord_alert_bot_v3.py')
spec = importlib.util.spec_from_file_location('bot', bot_path)
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

payload = {
    'smartSearch': '',
    'maxListingsPerQuery': 15,
    'marketplaces': ['ebay'],
    'brightDataToken': bot.BD_TOKEN,
    'brightDataZone': 'web_unlocker1',
    'presets': [],
    'customSearchTerms': ['Derek Jeter Topps Future Star', 'baseball card'],
    'includeSold': True,  # Bot sends this
}

r = requests.post(f'https://api.apify.com/v2/acts/{bot.ACTOR_ID}/runs?token={bot.APIFY_TOKEN}', json=payload, timeout=30)
run_id = r.json().get('data', {}).get('id')

for i in range(15):
    time.sleep(15)
    s = requests.get(f'https://api.apify.com/v2/actor-runs/{run_id}?token={bot.APIFY_TOKEN}', timeout=15).json().get('data', {})
    print(f\"  [{(i+1)*15}s] {s.get('status')} - {s.get('stats', {}).get('itemsCount', 0)} items\")
    if s.get('status') in ['SUCCEEDED', 'FAILED', 'ABORTED']:
        break
"
```

## Files To Investigate

| File | Lines | Purpose |
|---|---|---|
| `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` | ~250-330 | `buildEbaySearchUrl()` with `soldOnly` parameter |
| `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` | ~330-450 | `parseEbayListingsFromHtml()` — sold detection regex |
| `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` | ~460-540 | Main scrape loop that calls the above |

## Suggested Fix Options

**Option A**: Fix the sold-listing parser to extract real sold items from LH_Sold=1 pages.
- More work, but keeps single-actor architecture.

**Option B**: Don't use `includeSold` in this actor. Use the existing Sportscardspro+PriceCharting actor (already wired up for sold prices via `sportscardspro_url` column on Card model).
- Faster. Sportscardspro is more reliable than eBay sold scraping.
- Already deployed at `fuzzy_bracelet/sportscardspro-lookup` (`PGRtI1ZjuqUELHCGr`).

**My pick: Option B.** The Sportscardspro actor is already proven and returns real sold data (verified with Hugo's earlier work). The eBay sold scraping is a nice-to-have but not worth the maintenance.

## Workaround For Now

If Hugo goes with Option B, the bot can drop the `includeSold=True` flow entirely and rely on Sportscardspro for sold prices (which it already does via `lookup_sportscardspro()` in the bot code).

If Hugo wants to keep Option A, the bot code is already correct — just fix the actor.

## Test That Reproduces

The live bot test on 2026-09-14 09:13 CT failed:
```
[APIFY] Searching: Derek Jeter Topps Future Star (preset: cards-sports, include_sold: True)
[APIFY] Run started: Uaq2qPml0OFtgyi4F
[APIFY] Found 1 items (216s)
...
[NO MATCHES] No items match 'Derek Jeter Topps Future Star'
[DONE] 0 alerts sent to buddy_test_001
```

## Related Parking Lot Items

- **P0-HUGO-ACTOR-QUERY-CONFLICT** — Earlier actor input format issue (now resolved by Hugo's 2-query approach commit c7e964a)
- **P0-HUGO-EMPTY-TITLE** — Empty title was a red herring (placeholder item from actor)
- **P0-HUGO-INCLUDESOLD-BROKEN** — This bug

## Working Knowledge

- Bot v3 is the production bot (replaces V2)
- Jim (`buddy_test_001`) gets alerts at 2pm Central on Mon/Wed/Fri
- Cron job ID: `2fb20f7ad396`
- Bot v3 + DB + grade filter + customer ID v2 all shipped
- This is the LAST blocker for full bot flow with sell data

## How To Pick Up This Session

Just say "Hugo" in chat. The next session will:
1. Read this doc
2. Read `working-notes.md`
3. Read the actor's `main.js` (especially the sold-listing fetch path)
4. Either fix the actor OR drop the eBay sold flow and rely on Sportscardspro

## Files Touched Today

- `scripts/discord_alert_bot_v3.py` — bot code (Hugo's 2-query fix already in)
- `For You/Plans/hugo-handoff-includesold-broken-2026-09-14.md` — THIS DOC
- `.hermes/sessions/ideas-parking-lot-2026-09-12.json` — parking lot updated
