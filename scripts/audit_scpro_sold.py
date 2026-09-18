"""Audit SCPro sold-data capture for cards with sportscardspro_url.

Sept 18 dual-source fix #2: For Jim's 5 cards (which have URLs),
run the alert pipeline and check if sold_data is captured correctly.

This is a quick verification, not a full audit (which would cost $).
"""
import sys
import sqlite3
import json
from pathlib import Path

sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')


def get_cards_with_urls():
    conn = sqlite3.connect('card_scout.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT id, search_query, sportscardspro_url FROM cards WHERE enabled=1 AND sportscardspro_url IS NOT NULL ORDER BY id')
    return [dict(r) for r in cur.fetchall()]


def test_lookup(sportscardspro_url):
    """Call lookup_sportscardspro and extract_sold_summary. Return summary or None."""
    import scripts.discord_alert_bot_v3 as dab
    try:
        sc_data = dab.lookup_sportscardspro(sportscardspro_url, max_sales=10, max_wait_sec=60)
        if sc_data:
            sold_data = dab.extract_sold_summary(sc_data)
            return sold_data, sc_data
    except Exception as e:
        return {'error': str(e)}, None
    return None, None


def main():
    cards = get_cards_with_urls()
    print(f'Auditing sold-data capture for {len(cards)} cards with sportscardspro_url\n')

    results = []
    for card in cards:
        print(f'Card {card["id"]}: {card["search_query"][:50]}')
        print(f'  URL: {card["sportscardspro_url"][:80]}...')

        sold_data, sc_data = test_lookup(card['sportscardspro_url'])

        if sold_data is None:
            print(f'  ✗ Lookup returned None')
            results.append({'card_id': card['id'], 'status': 'no_data', 'psa_10_price': None})
        elif 'error' in sold_data:
            print(f'  ✗ Error: {sold_data["error"]}')
            results.append({'card_id': card['id'], 'status': 'error', 'error': sold_data['error']})
        else:
            psa10 = sold_data.get('psa_10_price', 'n/a')
            psa9 = sold_data.get('psa_9_price', 'n/a')
            raw_count = sold_data.get('psa_10_sold_30d', 'n/a')
            print(f'  ✓ PSA 10 ref: ${psa10 if isinstance(psa10, (int, float)) else psa10}')
            print(f'  ✓ PSA 10 sold: {raw_count}')
            print(f'  ✓ PSA 9 price: ${psa9 if isinstance(psa9, (int, float)) else psa9}')
            results.append({
                'card_id': card['id'],
                'search_query': card['search_query'],
                'status': 'ok',
                'psa_10_price': sold_data.get('psa_10_price'),
                'psa_9_price': sold_data.get('psa_9_price'),
                'psa_10_sold_30d': sold_data.get('psa_10_sold_30d'),
                'all_keys': list(sold_data.keys()) if sold_data else []
            })
        print()

    # Summary
    print('\n=== SUMMARY ===')
    ok = [r for r in results if r.get('status') == 'ok']
    print(f'Successful sold-data captures: {len(ok)}/{len(results)}')

    # Audit: which fields are captured
    all_fields = set()
    for r in ok:
        for k in r.get('all_keys', []):
            all_fields.add(k)
    print(f'\nFields captured across all ok lookups ({len(all_fields)}):')
    for f in sorted(all_fields):
        print(f'  - {f}')

    # Save audit
    out = Path('scpro_sold_capture_audit.json')
    out.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nSaved audit: {out}')


if __name__ == '__main__':
    main()
