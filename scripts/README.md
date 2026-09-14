# Card Scout Bot Scripts

**Purpose**: All Python code that powers the Card Scout Discord alert bot.

## Entry Point

The main bot is `discord_alert_bot_v3.py`. Read its header comments first
before changing anything.

## Module Map

| Module | Role |
|---|---|
| `discord_alert_bot_v3.py` | Main bot — orchestration, alert formatting, DB ops |
| `db_models.py` | SQLAlchemy models (Customer, Card, Snapshot, RunHistory) |
| `snapshot_system.py` | Save/load price snapshots, trend detection |
| `psa_pop_lookup.py` | Wrapper around PSA actor (with retry logic) |
| `sportscardspro_lookup.py` | Wrapper around sportscardspro+pricecharting actor |
| `grade_detector.py` | Regex for PSA/BGS/CGC strings in eBay titles |
| `grade_range_calculator.py` | Per-grade market table + 90% CI |
| `ticker_formatter.py` | Discord embed for per-grade ticker |

## Reading Order (NEW to the codebase)

1. Read `../README.md` first (project orientation)
2. Read this README (scripts orientation)
3. Read `../For You/Plans/card-scout-ticker-system-spec-2026-09-14.md` (the master spec)
4. Then read each module's README (`grade_detector.README.md`, etc.) in order
5. **THEN** read `discord_alert_bot_v3.py` line by line

## Quick Start

```bash
# From card-scout/ root
cd C:/Users/J/Documents/LLM/card-scout

# Test one card end-to-end
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

## Path Conventions

All paths are **relative** to the `card-scout/` project root:

- `card_scout.db` — SQLite bot DB
- `config/*.txt` — secrets (gitignored)
- `For You/Brand/*` — brand assets (logo, avatar)
- `For You/Plans/*` — specs and handoffs

If you need to add a new path, use `Path(__file__).parent.parent / "..."` pattern
to keep it relative to the project root. **Do not hardcode absolute paths** —
this was a real bug we fixed during the vostok-tools migration (commit `...`).

## Module READMEs

Each non-trivial module has its own README. If you write a new module, **also
write its README** — this is enforced per the project standard.

## Cost (Per Run)

- eBay search: ~$0.04 (Bright Data proxy)
- Sportscardspro lookup: ~$0.005
- PSA pop lookup: ~$0.012 (only if `card.include_pop = True`)
- **Total per card**: ~$0.05-0.07
