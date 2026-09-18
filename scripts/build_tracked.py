"""Build /tracked page - simple pivot table showing tracked cards with 90d sparklines.

Sept 18 (tracked-cards feature, simple version):
- Customer picks category from dropdown
- Sees their tracked cards with 90-day price history as SVG sparkline
- Sortable by 7d delta (default)
- Each row: name, sparkline, 7d delta, latest price, listings count
"""
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')

from cardhedger_client import CardHedgerClient


CACHE_DIR = Path('dashboard/trending_cache')
CACHE_DIR.mkdir(exist_ok=True)


def get_tracked_cards_for_customer(customer_slug=None, category=None):
    """Load all enabled customer cards from local DB, optionally filtered.

    Returns: list of {id, search_query, card_id, category, era, customer_slug}
    """
    db_path = 'card_scout.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = '''
        SELECT c.id, c.search_query, c.card_id, c.category, c.era,
               cust.customer_id AS customer_slug
        FROM cards c
        JOIN customers cust ON c.customer_id = cust.id
        WHERE c.enabled = 1
    '''
    args = []
    if customer_slug:
        query += ' AND cust.customer_id = ?'
        args.append(customer_slug)
    if category and category != 'All':
        query += ' AND c.category LIKE ?'
        args.append(f'%{category}%')

    query += ' ORDER BY cust.customer_id, c.id'
    cur.execute(query, args)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_categories_present(customer_slug=None):
    """Return sorted list of distinct categories among customer's cards."""
    cards = get_tracked_cards_for_customer(customer_slug)
    cats = set()
    for c in cards:
        if c.get('category'):
            cats.add(c['category'])
    return sorted(cats)


def fetch_price_history_cached(card_id, grade='PSA 10', days=90, ttl_hours=6):
    """Fetch price history with caching. Falls back to stale cache on error."""
    cache_file = CACHE_DIR / f'prices_{card_id}_{grade}_{days}d.json'

    # Check cache freshness
    if cache_file.exists():
        age_hours = (datetime.utcnow() - datetime.fromtimestamp(cache_file.stat().st_mtime)).total_seconds() / 3600
        if age_hours < ttl_hours:
            return json.loads(cache_file.read_text())

    # Fetch fresh
    client = CardHedgerClient()
    try:
        raw = client.get_price_history(card_id, grade, days=days)
        prices = raw.get('prices', [])
        cache_data = {
            'card_id': card_id,
            'grade': grade,
            'days': days,
            'fetched_at': datetime.utcnow().isoformat(),
            'prices': prices,
            'count': len(prices),
        }
        cache_file.write_text(json.dumps(cache_data, indent=2))
        return cache_data
    except Exception as e:
        print(f'Error fetching prices for {card_id}/{grade}: {e}')
        if cache_file.exists():
            print('  Using stale cache')
            return json.loads(cache_file.read_text())
        return {'card_id': card_id, 'grade': grade, 'prices': [], 'count': 0, 'fetched_at': None}


def make_sparkline_svg(prices, width=200, height=40):
    """Render a price history as an inline SVG sparkline.

    Returns SVG markup string.
    """
    if not prices:
        return f'<svg width="{width}" height="{height}" style="background:#fafafa;border:1px solid #eee;border-radius:3px;"><text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#888">No data</text></svg>'

    points = [float(p['price']) for p in prices if p.get('price')]
    if len(points) < 2:
        return f'<svg width="{width}" height="{height}" style="background:#fafafa;border:1px solid #eee;border-radius:3px;"><text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#888">Insufficient data ({len(points)} pts)</text></svg>'

    min_p, max_p = min(points), max(points)
    span = max_p - min_p if max_p != min_p else 1

    # Build polyline points
    coords = []
    for i, p in enumerate(points):
        x = i * (width / (len(points) - 1))
        y = height - 5 - ((p - min_p) / span) * (height - 10)
        coords.append(f'{x:.1f},{y:.1f}')

    # Compute trend color: green if latest is above median
    median_p = sorted(points)[len(points) // 2]
    latest = points[-1]
    color = '#2e7d32' if latest >= median_p else '#c33'

    polyline = ' '.join(coords)
    return (
        f'<svg width="{width}" height="{height}" style="background:#fff;border:1px solid #eee;border-radius:3px;">'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.5" />'
        f'<circle cx="{width - 4}" cy="{height - 5 - ((latest - min_p) / span) * (height - 10):.1f}" r="2.5" fill="{color}" />'
        f'</svg>'
    )


def compute_delta(prices):
    """Compute latest vs oldest % change from a price series."""
    if not prices or len(prices) < 2:
        return None
    latest = float(prices[-1]['price'])
    oldest = float(prices[0]['price'])
    if oldest == 0:
        return None
    return ((latest - oldest) / oldest) * 100


def render_tracked_page(customer_slug, category, cards_data):
    """Render the full /tracked HTML page."""
    # Group by category
    by_category = {}
    for card in cards_data:
        by_category.setdefault(card.get('category', 'Other'), []).append(card)

    # Build cards HTML
    if not cards_data:
        cards_html = '<p style="text-align:center;color:#888;padding:40px;">No cards tracked yet. Add cards in your dashboard to see them here with 90-day price history.</p>'
    else:
        cards_html = ''
        for card in cards_data:
            ch_card_id = card.get('card_id')
            if not ch_card_id:
                # Card without a card_id - show placeholder
                continue  # skip for now
            grade = card.get('tracked_grade', 'PSA 10')
            history = fetch_price_history_cached(ch_card_id, grade=grade, days=90)
            prices = history.get('prices', [])
            sparkline = make_sparkline_svg(prices)
            delta = compute_delta(prices)
            if delta is not None:
                delta_str = f'{delta:+.1f}%'
                delta_color = '#2e7d32' if delta >= 0 else '#c33'
            else:
                delta_str = 'n/a'
                delta_color = '#888'
            latest_price = prices[-1]['price'] if prices else 'n/a'

            cards_html += f'''
            <tr>
              <td class="info">
                <div class="desc">{card["search_query"][:60]}</div>
                <div class="meta">{card.get("customer_slug", "")} · {card.get("category", "")} · {card.get("era", "")}</div>
              </td>
              <td class="sparkline">{sparkline}</td>
              <td class="latest">${latest_price}</td>
              <td class="delta" style="color: {delta_color}; font-weight: 600;">{delta_str}</td>
              <td class="meta-small">{len(prices)} pts</td>
            </tr>'''

    # Category dropdown
    categories = sorted(by_category.keys()) or ['Sports Cards']
    cat_options = '<option value="All"' + (' selected' if category == 'All' else '') + '>All</option>'
    for cat in categories:
        sel = ' selected' if cat == category else ''
        cat_options += f'<option value="{cat}"{sel}>{cat}</option>'

    # Total stats
    total_cards = len(cards_data)
    cards_with_id = sum(1 for c in cards_data if c.get('card_id'))

    return f'''<!DOCTYPE html>
<html>
<head>
  <title>Card Scout - Tracked Cards</title>
  <meta name="description" content="90-day price history for cards you track on Card Scout.">
  <style>
    body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f7f7f9; }}
    h1 {{ color: #333; }}
    .subtitle {{ color: #888; margin-bottom: 20px; }}
    .controls {{ background: #fff; padding: 14px 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; gap: 16px; align-items: center; }}
    .controls label {{ font-size: 13px; color: #666; }}
    .controls select {{ padding: 6px; font-size: 13px; border-radius: 4px; border: 1px solid #ccc; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; vertical-align: middle; }}
    th {{ background: #fafafa; font-size: 12px; color: #888; text-transform: uppercase; }}
    .desc {{ font-weight: 600; color: #333; font-size: 14px; }}
    .meta {{ font-size: 11px; color: #888; margin-top: 2px; }}
    .meta-small {{ font-size: 11px; color: #999; }}
    .latest {{ font-weight: 600; color: #333; }}
    .sparkline {{ padding: 4px 8px; }}
    .footer {{ color: #999; font-size: 12px; margin-top: 30px; text-align: center; }}
    .stats {{ color: #666; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>📊 Tracked Cards</h1>
  <p class="subtitle">90-day price history from Card Hedger for cards you track.</p>

  <div class="controls">
    <label>Category:</label>
    <select onchange="window.location='/tracked' + (this.value !== 'All' ? '?category=' + encodeURIComponent(this.value) : '')">
      {cat_options}
    </select>
    <span class="stats">{total_cards} cards tracked · {cards_with_id} matched in Card Hedger · last updated just now</span>
  </div>

  <table>
    <thead><tr><th>Card</th><th>90d trend</th><th>Latest PSA 10</th><th>Δ vs 90d ago</th><th>Data points</th></tr></thead>
    <tbody>{cards_html}</tbody>
  </table>

  <p class="footer">
    Powered by <a href="/">Card Scout</a> · Data from <a href="https://cardhedger.com">Card Hedger</a><br>
    <a href="/pricing">Pricing</a> · <a href="/login">Login</a>
  </p>
</body>
</html>'''


def main():
    """Standalone test/demo."""
    cards = get_tracked_cards_for_customer()
    print(f'{len(cards)} tracked cards found')
    for c in cards:
        print(f'  id={c["id"]} ch_id={(c.get("card_id") or "NULL")[:25]:25} | {c["search_query"][:50]}')

    page = render_tracked_page(None, 'All', cards)
    out = Path('dashboard/tracked_test.html')
    out.write_text(page)
    print(f'\nRendered to {out}')


if __name__ == '__main__':
    main()
