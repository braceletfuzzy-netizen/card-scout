# `db_models.README.md` — Card Scout Database Models

## Status
**Production-ready.** Used by V1 ticker, alerts, audit trail, AND now the 30-day pricing_bands history (ADR-001, Sept 14).

## Tables
- `customers` — customer accounts (tier, webhook, settings)
- `cards` — cards in each customer's watchlist
- `snapshots` — Q-band stats for trend detection (current / 7d / 30d rotating)
- `run_history` — per-run audit trail (debugging + analytics)
- **`pricing_bands`** — *NEW (Sept 14, 2026)* daily per-grade pricing per card, 30-day TTL

## pricing_bands (the new table)
- One row per card per day
- 6 grade tiers: raw, PSA 7, PSA 8, PSA 9, PSA 9.5, PSA 10
- Each tier: low + high price + volume (sold count)
- Auto-cleaned after 30 days

### Why this exists
- **ADR-001** (architecture decision record): Jon wanted to be "future-ready without over-engineering"
- **Jim's chart ask**: needs 30-day history to draw price trend
- **V2 photo app**: needs historical baseline to predict value

### Key functions
- `capture_pricing_band_from_sc(session, card_id, sc_data)` — extracts from sportscardspro actor output
- `cleanup_old_pricing_bands(session, retention_days=30)` — daily TTL
- `get_30day_trend(session, card_id)` — returns avg + direction (up/down/flat)
- `PricingBand.get_30day_window(session, card_id)` — raw rows for chart rendering

### Auto-populated by
- `discord_alert_bot_v3.py` calls `capture_pricing_band_from_sc()` every time the sportscardspro actor returns data

### Cleanup
- `scripts/cleanup_old_pricing_bands.py` (standalone cron, ready to wire into `install-scheduler.bat`)

### Verification
- `scripts/verify_pricing_bands.py` — full end-to-end test with synthetic data (5/5 tests pass)

## Storage estimates
| Scale | Rows | Size | Engine |
|---|---|---|---|
| 12 cards x 30 days | 360 | ~55 KB | SQLite |
| 1,000 cards x 30 days | 30K | ~4.5 MB | SQLite |
| 100K cards x 30 days | 3M | ~450 MB | PostgreSQL |
| 10M cards x 30 days | 300M | ~45 GB | ClickHouse |

## Migrations
- All engine changes go through SQLAlchemy ORM — code unchanged
- SQLite → PostgreSQL: 30 min, 0 downtime (change DATABASE_URL)
- SQLite → ClickHouse: 1 week planned cutover

## Why the existing tables are fine
- `customers`, `cards`, `snapshots`, `run_history` — all <1 MB even at 10K customers
- No need to migrate from SQLite until 5K customers OR 60K cards

## Schema gotcha
- `pricing_bands.band_date` is `Date` type (not `DateTime`) — one row per calendar day
- `(card_id, band_date)` is unique — second insert of same day REPLACES the row
- `Date` column type works in SQLite AND PostgreSQL identically (SQLAlchemy abstraction)
