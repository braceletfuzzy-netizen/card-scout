# Card Scout

**Project**: Card Scout V1 (Bloomberg Terminal for trading cards)
**Status**: ✅ Production-ready (12 cards alerting)
**Last major update**: 2026-09-14 (migration from vostok-tools)

## What This Project Does

Card Scout is a Discord alert bot that watches eBay and Sportscardspro for
mispriced trading cards. It uses Apify actors (3 we own, no third-party data
purchases) to scrape listings, then sends Discord alerts when a card is listed
below its per-grade market average.

**The product**: A Bloomberg-style ticker showing **price per grade** (PSA 10,
PSA 9, BGS 9.5, Raw) with 90% confidence intervals. Customers see the market
state and decide for themselves whether to buy. We don't recommend — we surface
the data.

**Why this exists**: Vostok-tools (the parent project) needed a price-discovery
side hustle for low-volume markets. Trading cards fit perfectly — high-value,
fragmented, sold by individual hobbyists, not catalogs. Card Scout launched as
a v0.9 prototype and grew into its own product.

## Repository Structure

```
card-scout/
├── README.md                       ← you are here
├── .gitignore
│
├── scripts/                        ← Python bot code
│   ├── discord_alert_bot_v3.py     ← main bot (SQLAlchemy + Discord)
│   ├── db_models.py                ← Customer, Card, Snapshot, RunHistory
│   ├── snapshot_system.py          ← price trend detection
│   ├── psa_pop_lookup.py           ← PSA actor wrapper (with retry)
│   ├── sportscardspro_lookup.py    ← Sportscardspro actor wrapper
│   ├── grade_detector.py           ← regex for PSA/BGS/CGC strings
│   ├── grade_detector.README.md    ← module doc
│   ├── grade_range_calculator.py   ← per-grade 90% CI from sales data
│   ├── grade_range_calculator.README.md
│   ├── ticker_formatter.py         ← Discord embed for ticker output
│   └── ticker_formatter.README.md
│
├── actors/                         ← Apify actors we own
│   └── ebay-etsy-watch-scraper-monetized/  ← eBay actor (build 0.4.11)
│
├── config/                         ← secrets (gitignored)
│   ├── apify-token.txt             ← Apify CLI auth
│   ├── bright-data-token.txt       ← Bright Data proxy auth
│   ├── discord-webhook.txt         ← Discord webhook URL
│   └── card-scout-sheet.json       ← Google Sheets sync config
│
├── card_scout.db                   ← SQLite bot DB (12 cards, 4 customers)
│
└── For You/                        ← user-curated content (NOT a code folder)
    ├── Brand/                      ← logo, avatar, favicon
    ├── Plans/                      ← specs + handoff docs
    ├── Marketing & Sales/          ← pitch docs, DM templates
    └── Research/                   ← customer research notes
```

## Quick Start

```bash
# From card-scout/ root
cd C:/Users/J/Documents/LLM/card-scout

# Verify imports
python -c "import sys; sys.path.insert(0, 'scripts'); import discord_alert_bot_v3"

# Run a test on one card
python -c "
import sys
sys.path.insert(0, 'scripts')
from discord_alert_bot_v3 import get_session, run_apify_search, filter_matching_items
from db_models import Card
session = get_session()
card = session.query(Card).filter_by(id=1).first()
result = run_apify_search(card.search_query, preset=card.preset, max_listings=15, include_sold=False)
print(f'{len(result[\"items\"])} items in {result[\"duration\"]:.0f}s')
session.close()
"
```

## How The Bot Works

```
For each card in cards table:
  1. eBay search (30 items in ~31s)
       ↓ actor: AtQq66Qn8FB7aLq2l (cost ~$0.04/run)
  2. Filter + match by customer keywords
  3. Compute summary (Q bands, median, deal count)
  4. Optional: PSA pop lookup (with retry, 180s timeout)
       ↓ actor: DgLihiFRCa1Qf781s (cost ~$0.012/run)
  5. Sportscardspro lookup (per-grade prices)
       ↓ actor: PGRtI1ZjuqUELHCGr (cost ~$0.005/run)
  6. Format alert with per-grade ticker + below-market deals
  7. Send to Discord webhook
```

## Cost

- Per-card cost: ~$0.05 (no PSA) or ~$0.07 (with PSA)
- Daily scan (12 cards × MWF = 156 runs/year): ~$10-15/year
- See `../vostok-tools/config/monthly-budget.json` for cap details

## Status — P0 Items

- ✅ P0-HUGO-EMPTY-TITLE — RESOLVED (commit eff2bf0)
- ✅ P0-HUGO-ACTOR-QUERY-CONFLICT — RESOLVED (commit c7e964a)
- ✅ P0-HUGO-INCLUDESOLD-BROKEN — RESOLVED (commit 1f3e87a)
- ✅ P0-HUGO-PSA-SOLD — RESOLVED (commit cc0f38c)
- ✅ Migration from vostok-tools — COMPLETE (2026-09-14)

## Documentation Map

| To learn about... | Read... |
|---|---|
| Product vision | `For You/Plans/card-scout-ticker-system-spec-2026-09-14.md` |
| Old/superseded spec | `For You/Plans/card-scout-graded-focus-spec-2026-09-14.md` (SUPERSEDED) |
| EBay actor internals | `actors/ebay-etsy-watch-scraper-monetized/README.md` |
| Grade parser logic | `scripts/grade_detector.README.md` |
| Per-grade math | `scripts/grade_range_calculator.README.md` |
| Discord output format | `scripts/ticker_formatter.README.md` |
| Resolved bugs (context) | `For You/Plans/hugo-handoff-*-RESOLVED.md` |
| Bot run flow | `scripts/discord_alert_bot_v3.py` (header comments) |

## Agents Working On This

- **Hugo** (actor code, parser, statistical math, output formatter)
  Workspace: `C:\Users\J\Documents\LLM\hugo\`
- **Cosmo** (specs, customer flow, DB queries, bug discovery)
  Workspace: `C:\Users\J\Documents\LLM\cosmo\`

## Customer Status

- **Jim** (`buddy_test_001`) — first beta customer. 12 cards on watchlist. Active.
- **Customer #2** — onboarding pending after V1 stable (this month).
- **Customer #3+** — TBD. V1 + 1-2 months of customer feedback before V2 (Ticker Pro).

## Contact

For questions, check the agent workspace (`hugo/` or `cosmo/`) for session notes.
Per the README-first protocol: **read before changing**.
