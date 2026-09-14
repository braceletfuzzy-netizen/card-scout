> **⚠️  SUPERSEDED — Sept 14, 2026**
>
> **STATUS**: RESOLVED. See `hugo-handoff-psa-sold-2026-09-13-RESOLVED.md` (commit `cc0f38c`).
>
> Bot code fixes: Card model missing `sportscardspro_url` column was added, `extract_pop_summary` now uses priority logic for best-match instead of first-match, PSA pop lookup now retries on empty result.
>
> **This original handoff doc is kept for historical reference only — do not implement from it.**

---

# Hugo Handoff: PSA Pop + eBay Sold Data

**Status**: Bot v3 is live and working (4/8 alerts sent today). Two data sources need work to make the alert complete.

## What's working ✅

- Bot sends Discord alerts to Jim MWF (2pm Central)
- Format: Q bands + trend + buy deals + pop section
- Grade filter (6 checkboxes) shipped but not yet wired to form
- Customer ID v2 (date-encodable)
- Buy/Sell alert format coded but Sell section hidden when no sold data

## What needs Hugo 👷

### 1. PSA Pop Data (Currently Returns 0)

**Problem**: Bot calls Hugo's PSA actor with this URL for Jeter:
```
https://www.psacard.com/pop/baseball-cards/1993-topps/110001
```
Returns 0/0/0. Per Jim's Google search, Jeter cards DO have PSA pop data (PSA 10 ~$110).

**Possible causes**:
- Wrong set URL (1993 vs 1995 Topps?)
- Actor's parser misses per-card rows
- Set URL needs different spec_id format

**What I need from Hugo**:
- Test the actor with Jeter 1993 Topps Future Star URL
- If 0 results, check if 1995 Topps is the right set
- Update bot's `psa_set_url` per card

**Files**:
- `scripts/discord_alert_bot_v3.py` - calls `lookup_psa_pop()`
- `scripts/psa_pop_lookup.py` - lulzasaur wrapper
- `scripts/db_models.py` - `psa_set_url` column on Card

### 2. eBay Sold Data (Parser Bug)

**Problem**: Bot sends `LH_Sold=1` correctly but parser returns 0 sold items. eBay returns 91 items but all classified `listing_type: "active"`.

**Root cause** (from main.js line 299):
```javascript
const isSold = soldOnlyFlag && /class="[^"]*s-card__sold[^"]*"|>Sold\s*</i.test(block);
```
eBay's current HTML doesn't match `s-card__sold` class or `>Sold<` text.

**What I need from Hugo**:
- Run a test on the actor with `includeSold: true`
- Inspect actual eBay HTML for sold items
- Update regex to match eBay's current sold HTML markers

**Files**:
- `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` - line 299 (parser)
- `scripts/discord_alert_bot_v3.py` - sold_items handling

**Workaround I added**: When `sold_items` is empty, alert gracefully hides the section (no error).

## Customer-Visible Impact

- **PSA 0 issue**: Customers see "ULTRA RARE (0 PSA 10s)" which is misleading (we have no data, not 0 PSA 10s)
- **Missing sold section**: Customers see buy deals but not the spread/arbitrage info

## Priority

**Both are P0 for the dealer use case** (sell side = the money). But can ship with these gaps while we iterate. Jim hasn't complained yet because his bot is in beta.

## Parking Lot Items (P2 - For Later)

- Parse `s-card__sold` regex → eBay's actual sold HTML markers
- Verify PSA URL format (1993 vs 1995 for Jeter Topps Future Star)
- Add "No PSA data available" state (vs. showing "0" as "ULTRA RARE")
- Wire grade filter checkboxes into the Google Form (Cosmo does this)
- Update form to capture customer's grade preferences per card
- Add `psa_set_url` field to the Google Form so customers can self-service
