#!/usr/bin/env python3
"""Tracked Movers feature (Sept 18, Option B).

For all enabled customer-tracked cards, calculate:
1. Cross-window delta: 7d vs 90d median (is current higher than recent norm?)
2. Trend signal from latest snapshot
3. Sort by delta to find movers

Limitations:
- We only have ~3 days of snapshot history (Sept 16-18)
- The 3 snapshots per card are different WINDOWS (7d/30d/90d) from same run, not time series
- So traditional "7d delta" isn't possible. Use cross-window comparison instead.

Output: ranked list of tracked cards sorted by current-vs-90d-delta
"""
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('card_scout.db')


def get_tracked_cards_with_delta(category=None):
    """For enabled customer cards, calculate 7d vs 90d delta.

    Returns:
        list of dicts: {card_id, search_query, category, era,
                       median_7d, median_30d, median_90d,
                       delta_pct, trend_signal, total_listings}
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Join cards with latest snapshot for each window
    query = '''
        SELECT
            c.id AS card_id,
            c.search_query,
            c.category,
            c.era,
            c.customer_id,
            c.enabled,
            -- Get median for each window (one row per card per window)
            MAX(CASE WHEN s.window = '7d'  THEN s.median_price END) AS median_7d,
            MAX(CASE WHEN s.window = '30d' THEN s.median_price END) AS median_30d,
            MAX(CASE WHEN s.window = '90d' THEN s.median_price END) AS median_90d,
            -- Get latest trend signal (any window, prefer 7d)
            MAX(CASE WHEN s.window = '7d' THEN s.trend_signal END) AS trend_signal,
            MAX(CASE WHEN s.window = '7d' THEN s.total_listings END) AS listings_count
        FROM cards c
        JOIN snapshots s ON s.card_id = c.id
        WHERE c.enabled = 1
        {category_filter}
        GROUP BY c.id, s.taken_at
        -- Take only the most recent run per card
    '''.format(category_filter='AND c.category = ?' if category else '')

    args = [category] if category else []
    cur.execute(query, args)
    rows = cur.fetchall()

    results = []
    for r in rows:
        median_7d = r['median_7d']
        median_30d = r['median_30d']
        median_90d = r['median_90d']

        # Skip cards missing data
        if not (median_7d and median_90d):
            continue

        # Calculate delta: how far current (7d median) is from 90d median
        # This is a proxy for "momentum" - is the card above or below trend?
        delta_pct = ((median_7d - median_90d) / median_90d) * 100

        results.append({
            'card_id': r['card_id'],
            'search_query': r['search_query'],
            'category': r['category'],
            'era': r['era'],
            'median_7d': median_7d,
            'median_30d': median_30d,
            'median_90d': median_90d,
            'delta_pct': delta_pct,
            'trend_signal': r['trend_signal'] or 'INSUFFICIENT_DATA',
            'listings_count': r['listings_count'],
        })

    conn.close()

    return results


def render_tracked_section(category, movers_data, customer_links=True):
    """Render the 'tracked cards movers' section as HTML rows."""
    cards = movers_data.get('cards', [])

    if not cards:
        return '<tr><td colspan="6" style="text-align:center;color:#888;padding:30px;">No tracked card data yet. Run your alerts a few times to see movement.</td></tr>'

    rows = []
    for i, c in enumerate(cards[:10], 1):
        delta = c['delta_pct']
        delta_color = '#2e7d32' if delta > 0 else '#c33' if delta < 0 else '#888'
        delta_sign = '+' if delta > 0 else ''
        trend_emoji = {
            'ACCELERATING_UP': '🔥',
            'COOLING': '📉',
            'FLAT': '➡️',
            'INSUFFICIENT_DATA': '❓',
        }.get(c['trend_signal'], '❓')

        # Build a link - if customer is logged in, link to dashboard
        watchlist_link = f'/dashboard/{c.get("customer_slug", "")}' if customer_links and c.get('customer_slug') else '/dashboard/login'

        rows.append(f'''
        <tr>
          <td class="rank">{i}</td>
          <td class="info">
            <div class="desc">{c["search_query"][:60]}</div>
            <div class="meta">{c.get("category", "")} · {c.get("era", "")}</div>
          </td>
          <td class="delta" style="color: {delta_color}; font-weight: 600;">
            {delta_sign}{delta:.1f}%
            <div class="delta-detail" style="font-size: 11px; color: #888;">7d ${c["median_7d"]:.2f} vs 90d ${c["median_90d"]:.2f}</div>
          </td>
          <td class="trend" style="font-size: 18px;">{trend_emoji}</td>
          <td class="sales" style="font-size: 12px; color: #666;">{c['listings_count']} listings</td>
        </tr>''')

    return ''.join(rows)


def refresh_tracked_cache(category='All'):
    """Compute and cache tracked movers for a category."""
    cat = None if category == 'All' else category
    cards = get_tracked_cards_with_delta(cat)

    # Sort by absolute delta magnitude (biggest movers up OR down)
    cards.sort(key=lambda c: abs(c['delta_pct']), reverse=True)

    cache_file = Path('dashboard/trending_cache') / f'tracked_{category}.json'
    cache_data = {
        'category': category,
        'fetched_at': datetime.utcnow().isoformat(),
        'cards': cards,
    }
    cache_file.write_text(json.dumps(cache_data, indent=2, default=str))
    return cache_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        cat = sys.argv[2] if len(sys.argv) > 2 else 'All'
        data = refresh_tracked_cache(cat)
        print(f'category: {cat}, cards: {len(data["cards"])}')
        for c in data['cards'][:10]:
            print(f'  {c["delta_pct"]:+6.1f}% | {c["trend_signal"]:18} | {c["search_query"][:50]}')
    else:
        # Refresh all categories
        cats = ['All', 'Baseball', 'Basketball', 'Football', 'Pokemon', 'MTG']
        for cat in cats:
            data = refresh_tracked_cache(cat)
            print(f'  {cat:10}: {len(data["cards"])} cards cached')
