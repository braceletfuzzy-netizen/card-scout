"""
Snapshot writer + trend detector for Card Scout.

Solves: "30-day trend without storing daily data on every card"

How it works:
- 3 fixed snapshots per card (current, 7d, 30d)
- On each run, rotate snapshots:
  - Current becomes new 7d
  - Old 7d becomes new 30d
  - Old 30d is deleted
- Storage: ~600 bytes per card (3 snapshots × 200 bytes)

Trend signals:
- ACCELERATING_UP: 7d > 5% AND 30d > 10% (🔥)
- STEADY_UP: 7d > 2% AND 30d > 5% (📈)
- FLAT: both deltas < 2% (➡️)
- COOLING: 7d < -2% AND 30d < -5% (📉)
- CRASHING: 7d < -5% AND 30d < -10% (❄️)
- INSUFFICIENT_DATA: first 1-2 runs (no history yet)
"""

from db_models import Snapshot, Card, get_session, init_db
from datetime import datetime, timedelta
import statistics


def compute_snapshot_stats(items):
    """Compute price statistics from a list of matching items.
    
    Args:
        items: list of dicts with 'price_usd' and optional 'sold_count'
    
    Returns:
        dict with all the math we care about
    """
    prices = [i['price_usd'] for i in items if i.get('price_usd') is not None and i['price_usd'] > 0]
    
    if not prices:
        return {
            'median_price': None,
            'avg_price': None,
            'min_price': None,
            'max_price': None,
            'q1_price': None,
            'q2_price': None,
            'q3_price': None,
            'total_listings': 0,
            'items_with_sold_count': 0,
            'total_sold_reported': 0,
            'hot_items_count': 0,
            'avg_sold_count': None,
        }
    
    sorted_p = sorted(prices)
    n = len(sorted_p)
    
    # Quartiles (using simple method - middle value between two)
    def percentile(data, pct):
        idx = int(len(data) * pct)
        idx = min(idx, len(data) - 1)
        return data[idx]
    
    stats = {
        'median_price': statistics.median(prices),
        'avg_price': statistics.mean(prices),
        'min_price': min(prices),
        'max_price': max(prices),
        'q1_price': percentile(sorted_p, 0.25),
        'q2_price': percentile(sorted_p, 0.50),
        'q3_price': percentile(sorted_p, 0.75),
        'total_listings': len(prices),
        'items_with_sold_count': sum(1 for i in items if i.get('sold_count') and i['sold_count'] > 0),
        'total_sold_reported': sum(i.get('sold_count', 0) or 0 for i in items),
        'hot_items_count': sum(1 for i in items if i.get('sold_count') and i['sold_count'] > 50),
        'avg_sold_count': (
            statistics.mean([i['sold_count'] for i in items if i.get('sold_count') and i['sold_count'] > 0])
            if any(i.get('sold_count') for i in items) else None
        ),
    }
    
    return stats


def write_snapshot(card_id, stats, window='current'):
    """Write a snapshot for a card. Overwrites existing snapshot for same window."""
    session = get_session()
    
    # Check if snapshot exists for this card+window
    existing = session.query(Snapshot).filter_by(card_id=card_id, window=window).first()
    
    if existing:
        # Update existing
        for key, val in stats.items():
            setattr(existing, key, val)
        existing.taken_at = datetime.utcnow()
        snap = existing
    else:
        # Create new
        snap = Snapshot(card_id=card_id, window=window, **stats, taken_at=datetime.utcnow())
        session.add(snap)
    
    session.commit()
    session.close()
    return snap


def rotate_snapshots(card_id):
    """Rotate snapshots: current → 7d, old 7d → 30d, delete old 30d.
    
    Call this BEFORE writing the new current snapshot.
    Uses a temp window to avoid unique constraint violations.
    """
    session = get_session()
    
    # Get existing snapshots
    current = session.query(Snapshot).filter_by(card_id=card_id, window='current').first()
    seven_day = session.query(Snapshot).filter_by(card_id=card_id, window='7d').first()
    thirty_day = session.query(Snapshot).filter_by(card_id=card_id, window='30d').first()
    
    now = datetime.utcnow()
    
    # Delete old 30d first
    if thirty_day:
        session.delete(thirty_day)
        session.flush()  # Apply delete before inserts
    
    # Rotate via temporary windows to avoid unique constraint
    if seven_day:
        seven_day.window = '__tmp_a__'
        seven_day.taken_at = now
    
    if current:
        current.window = '__tmp_b__'
        current.taken_at = now
    
    session.flush()  # Apply changes
    
    # Now move them to their final positions
    if seven_day:
        seven_day.window = '30d'
    
    if current:
        current.window = '7d'
    
    session.commit()
    session.close()


def compute_trend(card_id):
    """Compute trend signal by comparing current, 7d, 30d snapshots.
    
    Returns:
        str: one of ACCELERATING_UP, STEADY_UP, FLAT, COOLING, CRASHING, INSUFFICIENT_DATA
    """
    session = get_session()
    
    current = session.query(Snapshot).filter_by(card_id=card_id, window='current').first()
    seven_day = session.query(Snapshot).filter_by(card_id=card_id, window='7d').first()
    thirty_day = session.query(Snapshot).filter_by(card_id=card_id, window='30d').first()
    
    session.close()
    
    # Need all three for trend
    if not current or not seven_day or not thirty_day:
        return 'INSUFFICIENT_DATA'
    
    # Need valid prices
    if not current.median_price or not seven_day.median_price or not thirty_day.median_price:
        return 'INSUFFICIENT_DATA'
    
    if seven_day.median_price == 0 or thirty_day.median_price == 0:
        return 'INSUFFICIENT_DATA'
    
    # Compute percentage changes
    delta_7d = (current.median_price - seven_day.median_price) / seven_day.median_price
    delta_30d = (current.median_price - thirty_day.median_price) / thirty_day.median_price
    
    # Classify
    if delta_7d > 0.05 and delta_30d > 0.10:
        return 'ACCELERATING_UP'
    elif delta_7d > 0.02 and delta_30d > 0.05:
        return 'STEADY_UP'
    elif delta_7d < -0.02 and delta_30d < -0.05:
        return 'COOLING'
    elif delta_7d < -0.05 and delta_30d < -0.10:
        return 'CRASHING'
    else:
        return 'FLAT'


def save_run_snapshot(card_id, items):
    """Full workflow: rotate, compute stats, write snapshot, compute trend.
    
    Args:
        card_id: int (Card.id)
        items: list of dicts with price/sold data
    
    Returns:
        str: trend signal
    """
    # 1. Rotate (old current → 7d, old 7d → 30d, delete old 30d)
    rotate_snapshots(card_id)
    
    # 2. Compute stats from items
    stats = compute_snapshot_stats(items)
    
    # 3. Write new current snapshot
    write_snapshot(card_id, stats, window='current')
    
    # 4. Compute trend (compares current vs 7d and 30d)
    trend = compute_trend(card_id)
    
    # 5. Update current snapshot's trend signal
    session = get_session()
    current = session.query(Snapshot).filter_by(card_id=card_id, window='current').first()
    if current:
        current.trend_signal = trend
        session.commit()
    session.close()
    
    return trend


def get_card_snapshots(card_id):
    """Get all 3 snapshots for a card (for display/debugging)."""
    session = get_session()
    snaps = session.query(Snapshot).filter_by(card_id=card_id).all()
    session.close()
    return {s.window: s for s in snaps}


def get_trend_emoji(trend_signal):
    """Get emoji for trend signal."""
    return {
        'ACCELERATING_UP': '🔥',
        'STEADY_UP': '📈',
        'FLAT': '➡️',
        'COOLING': '📉',
        'CRASHING': '❄️',
        'INSUFFICIENT_DATA': '⏳',
    }.get(trend_signal, '❓')


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SNAPSHOT SYSTEM TEST")
    print("=" * 60)
    
    # Initialize DB
    init_db()
    
    # Get a test card
    session = get_session()
    test_card = session.query(Card).first()
    
    if not test_card:
        print("No cards in DB. Run the bot first to create Jim's cards.")
        session.close()
    else:
        session.close()
        print(f"Testing with card: {test_card.search_query}")
        
        # Test data (fake price points)
        test_items = [
            {'price_usd': 10, 'sold_count': 5},
            {'price_usd': 12, 'sold_count': 12},
            {'price_usd': 15, 'sold_count': 8},
            {'price_usd': 14, 'sold_count': 25},
            {'price_usd': 18, 'sold_count': 60},
            {'price_usd': 22, 'sold_count': 100},
            {'price_usd': 8, 'sold_count': 3},
            {'price_usd': 25, 'sold_count': 150},
        ]
        
        # Compute stats
        stats = compute_snapshot_stats(test_items)
        print(f"\nComputed stats:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        
        # Save snapshot
        trend = save_run_snapshot(test_card.id, test_items)
        print(f"\nTrend signal: {trend} {get_trend_emoji(trend)}")
        
        # Get all snapshots
        snaps = get_card_snapshots(test_card.id)
        print(f"\nSnapshots for card:")
        for window, snap in snaps.items():
            print(f"  {window}: median=${snap.median_price} trend={snap.trend_signal}")
