# Card Scout Actors

**Purpose**: Apify actor source code that Card Scout owns and operates.

## Current Actors

### `ebay-etsy-watch-scraper-monetized/` (Build 0.4.11)

The eBay + Etsy marketplace scraper. This is the actor the bot calls for every
active listing search.

- **Actor ID**: `AtQq66Qn8FB7aLq2l`
- **Owner**: `fuzzy_bracelet` (Hermes)
- **Latest build**: 0.4.11 (released 2026-09-14 after migration)
- **Default build tag**: 0.4.11
- **Cost**: ~$0.001-0.05 per run (depends on `maxListingsPerQuery`)
- **Known issues**: 
  - `includeSold=True` returns 0 bytes from Bright Data — disabled in bot (uses Sportscardspro instead)
  - 3-tier preset expansion (10 terms) was hanging past 5min — bot uses 2-query approach to avoid

**Documentation**: See `README.md` in the actor directory for full input schema,
presets, and behavior.

## Republishing After Changes

```bash
# From card-scout/ root
cd C:/Users/J/Documents/LLM/card-scout

# Push the actor
cd actors/ebay-etsy-watch-scraper-monetized
apify push --force
# Note the build ID (e.g., 0.4.12)

# Update default build (NOT automatic — must use API)
python -c "
import requests
apify_token = open('../../config/apify-token.txt').read().strip()
r = requests.put(
    f'https://api.apify.com/v2/acts/AtQq66Qn8FB7aLq2l?token={apify_token}',
    json={'defaultRunOptions': {'build': '0.4.12', 'timeoutSecs': 360, 'memoryMbytes': 4096}},
    timeout=10
)
print(r.status_code)
"
```

## Adding New Actors

Before creating a new actor:
1. Check if an existing actor can be extended (chat with Hugo first)
2. Read `ebay-etsy-watch-scraper-monetized/README.md` for the standard structure
3. Use `apify init` to scaffold
4. Add the new actor to this `actors/` folder
5. Add a new section to this README

## Cleanup of Orphaned Actors

Old actors from the vostok-tools era that returned 0 items were identified
on 2026-09-14 as wasting $94.48/mo. They are NOT in this folder (they live
in vostok-tools). Migration cleanup is the vostok-tools repo's responsibility.
