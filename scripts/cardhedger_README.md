# Card Hedge API Integration

## What this is

Thin Python client for the [Card Hedge REST API](https://api.cardhedger.com), which gives Card Scout:
- Real-time pricing across all major grading companies (PSA, BGS, SGC, CGC)
- 40M+ weekly sales for comps/trend data
- Fair Market Value (FMV) with confidence grades
- Card search across 3.5M+ cards
- Cert # lookup
- MCP server for agent-native integration (Claude Code, Codex)

## Files

- `cardhedger_client.py` — Main client. `CardHedgerClient` class with 9 methods.
- `cardhedger_smoke_test.py` — End-to-end test. Run after subscription is active.

## Setup

### 1. Sign up

Go to https://ai.cardhedger.com and create an account. Subscription is **$14.99/mo** (Casual tier, 0-25 customers).

### 2. Get an API key

In your Card Hedge dashboard → API Services → copy your key.

### 3. Add to .env

In `C:\Users\J\Documents\LLM\card-scout\.env`, add:

```
CARD_HEDGER_API_KEY=ch_your_key_here
```

Optional:
```
CARD_HEDGER_BASE_URL=https://api.cardhedger.com  # default
```

### 4. Verify

```bash
python scripts/cardhedger_smoke_test.py
```

Expected output:
```
=== Card Hedge API smoke test ===
[1/5] Pinging API...
[OK] API authenticated
[2/5] Searching for "Bo Jackson Donruss"...
[OK] Found N cards
[3/5] Getting FMV for ... PSA 10...
[OK] FMV = $XXX (confidence: medium)
[4/5] Getting 30-day price history...
[OK] Got N price points
[5/5] Getting comparable sales (comps)...
[OK] Got N comparable sales
=== SMOKE TEST PASSED ===
```

## Methods

```python
from cardhedger_client import CardHedgerClient

client = CardHedgerClient()  # reads CARD_HEDGER_API_KEY from env

# Search
results = client.search_cards(search='Bo Jackson', category='Baseball')
results = client.search_cards(player='Michael Jordan', subset='Base Set')

# Card details
details = client.card_details(card_id='abc123')
batch = client.details_by_certs(certs=['12345678', '87654321'], grader='PSA')

# Pricing
fmv = client.get_fmv(card_id='abc123', grade='PSA 10')
history = client.get_price_history(card_id='abc123', grade='PSA 10', days=30)
comps = client.get_comps(card_id='abc123', grade='PSA 10', count=20)

# Cert-based (uses GemRate cache for the cert lookup)
hist_by_cert = client.price_history_by_cert(cert='12345678', grader='PSA')
fmv_by_cert = client.fmv_by_cert(cert='12345678', grader='PSA')

# Analytics
sales = client.total_sales_by_player(player='Bo Jackson', days=30)
movers = client.top_movers(count=20, category='Baseball')

# Health
ok = client.ping()
```

## What we DON'T use (yet)

Card Hedge has population endpoints (`/v1/cards/population-by-*`) but **those require a GemRate contract**. Without our own GemRate subscription, those calls fail. We can revisit when we hit 7+ paying customers (Tier 2 trigger).

## Error handling

The client raises `CardHedgerError` with:
- `status_code` — HTTP status (if applicable)
- `response_body` — raw response body (if available)
- `endpoint` — which endpoint failed

Retry policy (built into client):
- 5xx: retry 3 times with exponential backoff (1s, 2s, 4s)
- 429 (rate limit): wait 60s, retry once
- 4xx: no retry (fix the request)
- Connection errors: retry 3 times

## What's next (after smoke test passes)

1. **Wire Card Hedge into the alert pipeline** (`discord_alert_bot_v3.py` or successor)
2. **Replace SCPro Apify actor** with Card Hedge + eBay Browse (when verified)
3. **Add to onboarding** — new customers get card data sourced from Card Hedge

## Open fires (Sept 17)

- Subscribe to Card Hedger at https://ai.cardhedger.com (founder action)
- Get eBay Developer verification (separate fire)
- Inline card search UX (PL-008, deferred until data layer settled)
