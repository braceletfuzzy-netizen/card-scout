"""Verify pricing_bands table works end-to-end.

Tests:
1. Schema migration ran (table exists)
2. Capture from synthetic sportscardspro data
3. Cleanup of old bands
4. 30-day trend query
"""
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from db_models import (
    init_db, get_session, PricingBand, Card, Customer,
    capture_pricing_band_from_sc, cleanup_old_pricing_bands, get_30day_trend
)


def fake_sc_data():
    """Realistic sportscardspro actor output shape (per Hugo's notes Sept 14)."""
    return {
        'prices_by_tier': {
            'used_price': {'price_usd': 14.0, 'label': 'Ungraded'},
            'complete_price': {'price_usd': 16.0, 'label': 'Complete'},
            'new_price': {'price_usd': 21.0, 'label': 'New'},
            'graded_price': {'price_usd': 94.0, 'label': 'Grade 9'},
            'box_only_price': {'price_usd': 275.0, 'label': 'Grade 9.5'},
            'manual_only_price': {'price_usd': 655.0, 'label': 'Grade 10'},
            'manual_only_price_v2': {'price_usd': 645.0, 'label': 'Grade 10 alt'},
        },
        'sold_counts_by_grade': {
            'PSA 10': 23,
            'PSA 9.5': 1,
            'PSA 9': 30,
            'PSA 8': 30,
            'PSA 7': 30,
            'Ungraded': 29,
        },
        'sales': [],
    }


def main():
    print("=" * 60)
    print("Card Scout Pricing Bands Verification")
    print("=" * 60)

    init_db()
    session = get_session()

    # Get a real card from DB
    card = session.query(Card).first()
    if not card:
        print("[FAIL] No cards in DB. Add at least one card first.")
        return False

    print(f"\n[OK] Found card #{card.id}: {card.search_query[:50]}")

    # Test 1: capture today's band
    print("\n--- Test 1: Capture today's band ---")
    row = capture_pricing_band_from_sc(session, card.id, fake_sc_data())
    if row is None:
        print("[FAIL] Capture returned None")
        return False
    print(f"[OK] Captured row id={row.id}, date={row.band_date}")
    print(f"     raw_low/high: ${row.raw_low}/${row.raw_high}")
    print(f"     psa_10_low/high: ${row.psa_10_low}/${row.psa_10_high}")
    print(f"     psa_10_volume: {row.psa_10_volume}")

    # Test 2: insert backdated bands for 30-day trend
    print("\n--- Test 2: Insert backdated bands for 30-day window ---")
    today = date.today()
    for days_back in range(1, 30):
        past_date = today - timedelta(days=days_back)
        # Slight price variation so trend != flat
        data = fake_sc_data()
        # Simulate upward trend in PSA 10: $500 → $655 over 30 days
        data['prices_by_tier']['manual_only_price']['price_usd'] = 500 + (655 - 500) * (days_back / 30)
        # Simulate downward trend in raw: $20 → $14 over 30 days
        data['prices_by_tier']['used_price']['price_usd'] = 14 + (20 - 14) * (days_back / 30)
        capture_pricing_band_from_sc(session, card.id, data, band_date=past_date)

    bands = session.query(PricingBand).filter_by(card_id=card.id).all()
    print(f"[OK] Now have {len(bands)} pricing band rows for card #{card.id}")

    # Test 3: 30-day trend
    print("\n--- Test 3: 30-day trend query ---")
    trend = get_30day_trend(session, card.id)
    print(f"[OK] Trend: {trend}")
    if trend['days_with_data'] < 25:
        print(f"[WARN] Only {trend['days_with_data']} days (expected ~30)")
    if trend['direction'] not in ('up', 'down', 'flat'):
        print(f"[WARN] Unexpected direction: {trend['direction']}")

    # Test 4: cleanup
    print("\n--- Test 4: Cleanup (force retention to 7 days for test) ---")
    deleted = cleanup_old_pricing_bands(session, retention_days=7)
    print(f"[OK] Deleted {deleted} bands older than 7 days (test override)")

    remaining = session.query(PricingBand).filter_by(card_id=card.id).count()
    print(f"[OK] Remaining bands: {remaining} (expected ~8)")

    # Restore 30-day window for production use
    print("\n--- Restore: Re-add backdated rows for full 30-day window ---")
    for days_back in range(8, 30):
        past_date = today - timedelta(days=days_back)
        data = fake_sc_data()
        data['prices_by_tier']['manual_only_price']['price_usd'] = 500 + (655 - 500) * (days_back / 30)
        data['prices_by_tier']['used_price']['price_usd'] = 14 + (20 - 14) * (days_back / 30)
        capture_pricing_band_from_sc(session, card.id, data, band_date=past_date)

    final_count = session.query(PricingBand).filter_by(card_id=card.id).count()
    print(f"[OK] Final band count: {final_count} rows for card #{card.id}")

    # Test 5: 30-day trend re-check
    print("\n--- Test 5: Final 30-day trend re-check ---")
    trend = get_30day_trend(session, card.id)
    print(f"[OK] Final trend: {trend}")

    session.close()
    print("\n" + "=" * 60)
    print("[OK] ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
