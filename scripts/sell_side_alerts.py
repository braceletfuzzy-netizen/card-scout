"""Sept 18 — sell-side alert copywriter.

Build a new alert_type='sell_window' that:
1. Compares CURRENT active listing prices vs 30-day realized sale median
2. When active listing is significantly ABOVE 30d realized median,
   it's a sell window for customers who own this card
3. Use threshold tier labels (no z-score mentioned)

Per Sept 18 founder directive:
- "thresholds, because we are telling you the arbitrage that is available
   and spelling it out without telling you how we came up with our calculations"
- "Strip out that we are using std dev, z scores, etc."

Tier mapping (internal pct → customer-facing label):
  1.0-1.5x typical: 'above typical price'
  1.5-2.0x typical: 'hot market'
  2.0-3.0x typical: 'premium pricing window'
  >3.0x typical:    'extreme premium'

Implementation:
1. Add 'compute_recent_sold_median()' that pulls recent_sales[] and computes
   30-day median (no z-score — just ratio thresholds)
2. Add 'find_sell_window()' that classifies items + compares to 30d median
3. Add 'format_sell_alert()' with mock C-style conversational copy
4. Wire into alert_type dispatch (currently only 'below_median', 'below_fmv')

This will use SCPro's recent_sales[] which we ALREADY capture. No new API calls.
"""
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')


def compute_recent_sold_median(sold_data, days=30):
    """Compute the median sold price from recent_sales[] over the last N days.

    Args:
        sold_data: dict from extract_sold_summary()
        days: lookback window (default 30)

    Returns:
        median price (float) or None if no data
        count of sales used in the median
    """
    if not sold_data:
        return None, 0

    sales = sold_data.get('recent_sales', []) or []
    if not sales:
        # Maybe top-level sold data doesn't have it; try the 30-day count
        return None, 0

    cutoff = datetime.now() - timedelta(days=days)
    recent_prices = []
    for sale in sales:
        try:
            sale_date = datetime.strptime(sale.get('date', ''), '%Y-%m-%d')
            if sale_date >= cutoff:
                price = sale.get('price_usd')
                if price and price > 0:
                    recent_prices.append(price)
        except (ValueError, TypeError):
            continue

    if not recent_prices:
        return None, 0

    recent_prices.sort()
    n = len(recent_prices)
    if n % 2 == 1:
        median = recent_prices[n // 2]
    else:
        median = (recent_prices[n // 2 - 1] + recent_prices[n // 2]) / 2
    return median, n


def classify_premium_tier(ratio):
    """Map listing-vs-typical ratio to a customer-facing tier label.

    Per Sept 18 founder directive: NO z-scores, NO std dev mentioned.
    Just a tier label that conveys the opportunity.

    Args:
        ratio: listing_price / typical_price (e.g. 1.5 = listing is 50% above)

    Returns:
        (tier_label, suggested_window) tuple
    """
    if ratio < 1.0:
        return None, None  # No sell signal (listing below typical)
    elif ratio < 1.5:
        return 'above typical price', None
    elif ratio < 2.0:
        return 'hot market, well above typical', '48-72 hours'
    elif ratio < 3.0:
        return 'premium pricing window', '48-72 hours'
    else:
        return 'EXTREME PREMIUM', '24-48 hours (urgent)'


def find_sell_window(matching_items, sold_data, min_days=7, days=30):
    """Find SCPro listings that are above typical 30d realized price.

    Returns list of items with sell-signal annotation:
      {..., _typical_30d: float, _ratio: float, _tier: str,
       _window: str|None}
    """
    if not matching_items:
        return []

    typical_30d, sale_count = compute_recent_sold_median(sold_data, days=days)
    if not typical_30d or typical_30d <= 0:
        # No historical anchor — can't tell if current is "above typical"
        # Fallback: use SCPro's own psa_10_price as the anchor (current asking median)
        typical_30d = (sold_data or {}).get('psa_10_price') if sold_data else None
        if not typical_30d or typical_30d <= 0:
            return []

    sells = []
    for item in matching_items:
        price = item.get('price_usd')
        if not price or price <= 0:
            continue
        ratio = price / typical_30d
        tier, window = classify_premium_tier(ratio)
        if tier is None:
            continue  # Not above typical
        # Only fire if there's ACTUALLY signal (ratio >= 1.0 is the floor)
        if ratio < 1.0:
            continue
        item_with_meta = dict(item)
        item_with_meta['_typical_30d'] = typical_30d
        item_with_meta['_ratio'] = ratio
        item_with_meta['_tier'] = tier
        item_with_meta['_window'] = window
        item_with_meta['_sale_count'] = sale_count
        sells.append(item_with_meta)

    return sells


def format_sell_alert(search_query, sells, sold_data, ch_data=None, max_items=3):
    """Format sell-side alerts (Sept 18, conversational mock C style).

    Returns: list of Discord message dicts (ready to send)
             [] if no qualifying sells
    """
    if not sells:
        return []

    # Pick top N sells (most extreme ratios)
    sells_sorted = sorted(sells, key=lambda x: x.get('_ratio', 0), reverse=True)[:max_items]

    messages = []
    for sell in sells_sorted:
        title = sell.get('title', search_query)[:80]
        price = sell.get('price_usd')
        ratio = sell.get('_ratio', 0)
        typical = sell.get('_typical_30d', 0)
        tier = sell.get('_tier', '')
        window = sell.get('_window') or 'soon'
        grade = sell.get('_classified_grade', 'unknown')

        if not price or not typical:
            continue

        # Compute % above typical (for the message)
        pct_above = (price - typical) / typical * 100

        # Customer-facing copy — NO z-scores, NO std dev
        # Per Sept 18: tier names are the secret sauce
        message = (
            f"📈 **Sell window: {title}**\n\n"
            f"Someone just listed at **${price:.0f}** — {pct_above:.0f}% above "
            f"what similar copies have been selling for recently (${typical:.0f}).\n\n"
        )

        # Tier-specific body
        if tier == 'EXTREME PREMIUM':
            message += (
                f"This is a **rare premium pricing window**. Buyers are paying far "
                f"above the norm right now. If you have one to sell, list within "
                f"**{window}** before the spike cools.\n"
            )
        elif tier.startswith('premium'):
            message += (
                f"This is a **premium pricing window**. Demand seems strong — "
                f"if you're sitting on one, now is a good time to list.\n"
            )
        elif tier.startswith('hot'):
            message += (
                f"The market seems hot for this card. Worth considering listing "
                f"if you have a copy to sell.\n"
            )
        else:
            message += (
                f"Listed above the typical market range. If you've been thinking "
                f"about selling, this is a reasonable time.\n"
            )

        # Add sale count for credibility
        sale_count = sell.get('_sale_count', 0)
        if sale_count:
            message += f"\n_Based on {sale_count} recent sales · graded {grade}_\n"

        # Listing link
        listing_url = sell.get('listing_url') or sell.get('url')
        if listing_url:
            message += f"\n[View the listing]({listing_url})"

        messages.append({
            'title': f"🔥 Sell window: {title[:60]}",
            'description': message,
            'tier': tier,
            'ratio': ratio,
            'price': price,
            'typical_30d': typical,
            'grade': grade,
        })

    return messages


# ============================================================================
# Tests using real data from Sept 18 (Frank Thomas Bo Jackson Jordan Jeter Aaron)
# ============================================================================

if __name__ == '__main__':
    # Quick sanity check with real data shape
    fake_sales = [
        {'date': '2026-09-15', 'price_usd': 5.00, 'title': '1987 Donruss ...'},
        {'date': '2026-08-13', 'price_usd': 26.00, 'title': '1987 Donruss ...'},
        {'date': '2026-09-05', 'price_usd': 13.88, 'title': '1987 Donruss ...'},
    ]
    sold_data = {'recent_sales': fake_sales, 'psa_10_price': 655.34}
    median, count = compute_recent_sold_median(sold_data)
    print(f'Frank Thomas test: median=${median} (from {count} sales)')

    # Edge case: ratio threshold mapping
    for r in [0.9, 1.1, 1.4, 1.7, 2.5, 3.5]:
        tier, window = classify_premium_tier(r)
        print(f'  ratio={r:.1f} → tier={tier} window={window}')
