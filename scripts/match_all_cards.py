"""Run inline card matcher for all customer cards missing card_id.

Sept 18: prep for /tracked feature (90d graph requires card_id per card).
For each card with NULL card_id, call CH card-match, store result.
"""
import sys
import json
import sqlite3
import time
from pathlib import Path

sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')
from cardhedger_client import CardHedgerClient


def match_one(client, query, threshold=0.3):
    """Call card-match, return (card_id, confidence) or (None, 0)."""
    try:
        result = client._post('/v1/cards/card-match', {
            'query': query, 'limit': 1,
        })
        match = result.get('match')
        if match:
            confidence = float(match.get('confidence', 0))
            if confidence >= threshold:
                return match.get('card_id'), confidence
        return None, 0.0
    except Exception as e:
        print(f'  ERROR: {e}')
        return None, 0.0


def main():
    db_path = 'card_scout.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get all customer cards with NULL card_id
    cur.execute('''
        SELECT c.id, c.search_query, cust.customer_id
        FROM cards c
        JOIN customers cust ON c.customer_id = cust.id
        WHERE c.card_id IS NULL AND c.enabled = 1
        ORDER BY cust.customer_id, c.id
    ''')
    rows = cur.fetchall()
    print(f'{len(rows)} customer cards need matching:')

    client = CardHedgerClient()
    matched = 0
    unmatched = 0

    for row_id, query, customer_slug in rows:
        print(f'\n  card_id={row_id} ({customer_slug}): {query[:60]}')
        card_id, confidence = match_one(client, query)
        if card_id:
            cur.execute('UPDATE cards SET card_id = ?, card_match_confidence = ? WHERE id = ?',
                        (card_id, confidence, row_id))
            conn.commit()
            matched += 1
            print(f'    ✓ MATCHED (conf={confidence:.2f}, ch_id={card_id[:30]})')
        else:
            unmatched += 1
            print(f'    ✗ No match')

        # Rate limit: Card Hedger has 10 req/min on Starter
        time.sleep(7)  # 7 sec between calls = ~8.5/min

    conn.close()
    print(f'\n=== Done: {matched} matched, {unmatched} unmatched ===')


if __name__ == '__main__':
    main()
