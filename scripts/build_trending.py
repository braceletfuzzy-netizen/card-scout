#!/usr/bin/env python3
"""Build public /trending page (Option A: Card Hedger top movers).

Sept 18: First ship of largest-mover / X feature.
- Public page at /trending
- Category tabs (All, Baseball, Basketball, Football, Pokemon, MTG, One Piece)
- Top 10 weekly gainers per category from Card Hedger top-movers endpoint
- Each card has 'Add to my watchlist' button (links to login)
- Daily cron refreshes data, caches to disk
"""
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')

from cardhedger_client import CardHedgerClient


CACHE_DIR = Path('dashboard/trending_cache')
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_HOURS = 6  # Refresh every 6 hours (4x/day)


def fetch_top_movers(category='All', count=10):
    """Fetch top movers for a category, with caching."""
    cache_file = CACHE_DIR / f'movers_{category or "All"}.json'

    # Check cache freshness
    if cache_file.exists():
        age_hours = (datetime.utcnow() - datetime.fromtimestamp(cache_file.stat().st_mtime)).total_seconds() / 3600
        if age_hours < CACHE_TTL_HOURS:
            return json.loads(cache_file.read_text())

    # Fetch fresh
    client = CardHedgerClient()
    try:
        if category and category != 'All':
            result = client.top_movers(count=count, category=category)
        else:
            result = client.top_movers(count=count)
        cards = result.get('cards', [])

        # Cache
        cache_data = {
            'category': category,
            'fetched_at': datetime.utcnow().isoformat(),
            'cards': cards,
        }
        cache_file.write_text(json.dumps(cache_data, indent=2))
        return cache_data
    except Exception as e:
        print(f'Error fetching top movers for {category}: {e}')
        # Fall back to stale cache if available
        if cache_file.exists():
            print(f'  Using stale cache')
            return json.loads(cache_file.read_text())
        return {'category': category, 'cards': [], 'fetched_at': None}


def render_trending_html(category, movers_data):
    """Render the /trending HTML page."""
    cards = movers_data.get('cards', [])

    # Category tabs
    categories = ['All', 'Baseball', 'Basketball', 'Football', 'Hockey', 'Pokemon', 'MTG', 'One Piece']
    tabs_html = ' | '.join(
        f'<a href="/trending?category={c}" class="{"active" if c == category else ""}">{c}</a>'
        for c in categories
    )

    # Card rows
    rows = []
    for i, card in enumerate(cards[:10], 1):
        rows.append(f'''
        <tr>
          <td class="rank">{i}</td>
          <td class="thumb"><img src="{card.get("image", "")}" onerror="this.style.display='none'" style="width:50px;height:70px;object-fit:cover;"></td>
          <td class="info">
            <div class="desc">{card.get("description", "?")}</div>
            <div class="meta">{card.get("player", "")} · {card.get("set", "")} · #{card.get("number", "")}</div>
          </td>
          <td class="gain">+{card.get("gain", 0):.2f}%</td>
          <td class="sales">7d: {card.get("7 Day Sales", 0)}<br>30d: {card.get("30 Day Sales", 0)}</td>
          <td class="action"><a href="/login" class="add-btn">+ Watchlist</a></td>
        </tr>''')

    return f'''<!DOCTYPE html>
<html>
<head>
  <title>Card Scout - Trending Cards</title>
  <meta name="description" content="Weekly top movers across baseball, basketball, football, and TCG cards.">
  <style>
    body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f7f7f9; }}
    h1 {{ color: #333; }}
    .subtitle {{ color: #888; margin-bottom: 20px; }}
    .tabs {{ background: #fff; padding: 14px 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .tabs a {{ color: #555; text-decoration: none; padding: 8px 14px; margin-right: 6px; border-radius: 4px; }}
    .tabs a:hover {{ background: #f0f0f3; }}
    .tabs a.active {{ background: #5865f2; color: white; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 14px; text-align: left; border-bottom: 1px solid #eee; }}
    th {{ background: #fafafa; font-size: 12px; color: #888; text-transform: uppercase; }}
    .rank {{ font-size: 18px; color: #aaa; width: 30px; }}
    .desc {{ font-weight: 600; color: #333; }}
    .meta {{ font-size: 12px; color: #888; margin-top: 2px; }}
    .gain {{ color: #2e7d32; font-weight: 600; }}
    .sales {{ font-size: 12px; color: #666; }}
    .action {{ text-align: right; }}
    .add-btn {{ background: #5865f2; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; }}
    .footer {{ color: #999; font-size: 12px; margin-top: 30px; text-align: center; }}
    .fetched {{ color: #aaa; font-size: 11px; text-align: right; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <h1>🔥 Trending Cards</h1>
  <p class="subtitle">Top 10 weekly gainers by category. Click any card to add it to your watchlist.</p>
  <div class="tabs">{tabs_html}</div>
  <div class="fetched">Data fetched {movers_data.get('fetched_at', 'pending')[:19]} UTC · Refreshes every 6 hours</div>
  <table>
    <thead><tr><th>#</th><th></th><th>Card</th><th>7d Gain</th><th>Sales</th><th></th></tr></thead>
    <tbody>{''.join(rows) if rows else '<tr><td colspan="6" style="text-align:center;color:#888;padding:30px;">No movers found for this category.</td></tr>'}</tbody>
  </table>
  <p class="footer">
    Powered by <a href="/">Card Scout</a> · Data from <a href="https://cardhedger.com">Card Hedger</a><br>
    <a href="/pricing">Pricing</a> · <a href="/login">Login</a>
  </p>
</body>
</html>'''


def main():
    """Build all category cache files. Run daily by cron."""
    categories = ['', 'Baseball', 'Basketball', 'Football', 'Hockey', 'Pokemon', 'MTG', 'One Piece']
    print(f'Refreshing top-movers cache for {len(categories)} categories...')
    for cat in categories:
        data = fetch_top_movers(cat if cat else 'All', count=10)
        print(f'  {cat or "All":12} cached {len(data.get("cards", []))} cards')
    print('Done')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        # Render a single category's HTML to stdout
        cat = sys.argv[2] if len(sys.argv) > 2 else 'All'
        data = fetch_top_movers(cat, count=10)
        print(render_trending_html(cat, data))
    else:
        main()
