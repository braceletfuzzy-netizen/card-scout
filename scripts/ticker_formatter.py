"""
Per-grade ticker formatter.

Renders the Bloomberg-style ticker output per the master spec
(card-scout-ticker-system-spec-2026-09-14.md):
- Market value per grade (typical range from sportscardspro)
- 90% confidence interval per grade (mean ± 1.645×SD)
- Below-market deals (listing price < typical range for THAT grade)
- 7d/30d trend signals
- Q bands
- PSA population data (scarcity)

Show, don't recommend. Customer decides if it's a deal.
"""

from typing import Dict, List, Optional


def get_30day_average(session, card_id: int, tier: str) -> Optional[float]:
    """Get the 30-day average price for a card+tier from pricing_bands.

    Args:
        session: SQLAlchemy session
        card_id: cards.id
        tier: column prefix (raw, psa_7, psa_8, psa_9, psa_9_5, psa_10)

    Returns:
        Average price across all pricing_bands rows in last 30 days, or None if no history.
    """
    from datetime import date, timedelta
    from db_models import PricingBand

    col_name = f'{tier}_low'  # Use low as the canonical price per tier
    cutoff = date.today() - timedelta(days=30)

    rows = session.query(PricingBand).filter(
        PricingBand.card_id == card_id,
        PricingBand.band_date >= cutoff,
    ).all()

    if not rows:
        return None

    prices = []
    for r in rows:
        v = getattr(r, col_name, None)
        if v is not None and v > 0:
            prices.append(v)

    return sum(prices) / len(prices) if prices else None


def format_trend_indicator(current_price: Optional[float], avg_30d: Optional[float]) -> str:
    """Format a trend indicator showing current vs 30-day average.

    Returns:
        - "" if either is None or no history
        - " (vs 30d avg $X)" if no significant change
        - " (↑N% vs 30d avg $X)" if up
        - " (↓N% vs 30d avg $X)" if down
    """
    if current_price is None or current_price <= 0:
        return ""
    if avg_30d is None or avg_30d <= 0:
        return ""  # No history yet

    pct_change = ((current_price - avg_30d) / avg_30d) * 100

    # Within 2% = "flat"
    if abs(pct_change) < 2:
        return f" (vs 30d avg ${avg_30d:.0f}, flat)"

    if pct_change > 0:
        return f" (↑{pct_change:.0f}% vs 30d avg ${avg_30d:.0f})"
    else:
        return f" (↓{abs(pct_change):.0f}% vs 30d avg ${avg_30d:.0f})"


def format_per_grade_ticker(grade_table: List[Dict], max_chars: int = 600, session=None, card_id=None) -> str:
    """
    Render the per-grade market ticker table.

    Input: list of grade_table rows from grade_range_calculator.build_per_grade_table()
    Each row: {tier, grade, label, price, range, sold_count_30d}

    Output: Discord embed field string showing each grade tier with
    typical price + 90% range.

    If session + card_id provided, also shows "vs 30d avg" trend for each tier.
    If PSA pop data is available for the card, also shows the
    "stock-class hierarchy" section (Sept 16 V3 feature).
    """
    if not grade_table:
        return "(no per-grade data)"

    lines = []
    for row in grade_table:
        tier = row.get('tier')
        label = row.get('label', 'Raw')
        price = row.get('price', 0)
        range_data = row.get('range', {})
        sold_30d = row.get('sold_count_30d', 0)

        # Format price as the "typical" middle value
        mean = range_data.get('mean', price)
        low = range_data.get('low', price * 0.7)
        high = range_data.get('high', price * 1.3)
        sold_str = f" ({sold_30d} sold/30d)" if sold_30d > 0 else ""

        # Pick display value: typical price (mean if available, else single price)
        if range_data.get('count', 0) >= 2 and price > 0:
            val_str = f"${price:.2f}  (typical ${low:.2f}–${high:.2f})"
        elif price > 0:
            val_str = f"${price:.2f}"
        else:
            val_str = "—"

        # Add 30-day trend indicator (ADR-001 trend-aware alerts)
        trend_str = ""
        if session is not None and card_id is not None and tier:
            avg = get_30day_average(session, card_id, tier)
            trend_str = format_trend_indicator(price, avg)

        lines.append(f"**{label}:** {val_str}{trend_str}{sold_str}")

    return "\n".join(lines)


def format_stock_class_section(card) -> Optional[str]:
    """
    Format the 'stock-class hierarchy' section for a card (Sept 16 V3 feature).

    Founder's framing: PSA grades are like stock classes (10=A, 9=B, 8=C).
    Graded cards are stock certificates. Pop data = outstanding shares.

    Shows:
    - Stock-class label (A/B/C/D) per grade
    - Rarity % (PSA 10 as % of total pop)
    - Total outstanding (total graded)
    - Market depth (sales volume)
    - Premium (PSA 10 / PSA 9 ratio)

    Returns None if no pop data, or a formatted string.
    """
    # Lazy import to avoid circular
    try:
        from psa_pop_persister import compute_rarity, get_stock_class_label, compute_premium
    except ImportError:
        return None

    # Need both prices AND pop data
    if not card.psa_total_pop:
        return None

    # Build the section
    lines = []
    lines.append("**🎖️ Stock-Class Hierarchy:**")

    # Rarity
    rarity = compute_rarity(card.psa_10_pop, card.psa_total_pop)
    rarity_emoji = {
        'RARE': '⭐',
        'SCARCE': '💎',
        'COMMON': '📊',
        'PLENTIFUL': '📈',
        'UNKNOWN': '❓'
    }.get(rarity['label'], '')

    if rarity['pct'] is not None:
        lines.append(
            f"  {rarity_emoji} **PSA 10** = **{rarity['label']}** "
            f"({rarity['pct']:.1f}% of pop, only **{card.psa_10_pop:,}** exist)"
        )

    # Stock classes (just show the structure, no per-grade pop data we have)
    # We don't have per-grade pop for PSA 9, 8, 7 etc in DB. Show what we know.
    if card.psa_9_pop:
        lines.append(f"  • PSA 9 = B-class ({card.psa_9_pop:,} exist)")

    # Total outstanding
    lines.append(f"")
    lines.append(f"**🏷️ Total outstanding:** {card.psa_total_pop:,} graded")

    return "\n".join(lines)


def format_below_market_deals(items: List[Dict], grade_table: List[Dict], max_items: int = 5) -> Optional[Dict]:
    """
    For each item, check if its listing price is below the typical range for its grade.
    Flag it as a "deal" only if listing_price < grade_range_low.

    Returns: { 'deals': [...], 'table': 'grade comparison string' } or None if no deals.
    """
    import re
    from grade_detector import detect_grade

    if not items or not grade_table:
        return None

    # Build a quick lookup: tier → range low
    range_by_tier = {}
    for row in grade_table:
        tier = row.get('tier')
        if tier:
            range_by_tier[tier] = row.get('range', {})

    deals = []
    for item in items:
        price = item.get('price_usd', 0)
        if not price or price <= 0:
            continue

        title = item.get('title', '')
        grade_info = detect_grade(title)
        tier = grade_info['tier']
        grade_label = grade_info.get('label', tier)  # tier label is psa_10 etc.
        if grade_info['authority']:
            grade_label = f"{grade_info['authority']} {grade_info['grade']}"

        # Get the typical range for this tier
        tier_range = range_by_tier.get(tier, {})
        low = tier_range.get('low', 0)
        high = tier_range.get('high', 0)

        # Compare: if price < typical range low → deal
        if low > 0 and price < low:
            pct_off = ((low - price) / low) * 100
            deals.append({
                'title': title,
                'url': item.get('url', '#'),
                'price_usd': price,
                'grade_label': grade_label,
                'tier': tier,
                'typical_low': low,
                'typical_high': high,
                'discount_pct': pct_off,
            })
        elif tier == 'raw' and low > 0 and price < low:
            # Raw listing below typical raw range
            pct_off = ((low - price) / low) * 100
            deals.append({
                'title': title,
                'url': item.get('url', '#'),
                'price_usd': price,
                'grade_label': grade_label or 'Raw',
                'tier': tier,
                'typical_low': low,
                'typical_high': high,
                'discount_pct': pct_off,
            })

    if not deals:
        return None

    deals.sort(key=lambda d: -d['discount_pct'])  # biggest discount first
    return {
        'deals': deals[:max_items],
        'total_found': len(deals),
    }


# Self-test
if __name__ == '__main__':
    print("="*70)
    print("format_per_grade_ticker test (Jeter sample)")
    print("="*70)

    sample = [
        {'tier': 'psa_10', 'grade': 10.0, 'label': 'PSA 10 / BGS 10', 'price': 107.50,
         'range': {'mean': 105.0, 'sd': 7.07, 'low': 93.37, 'high': 116.63, 'count': 2},
         'sold_count_30d': 5},
        {'tier': 'psa_9', 'grade': 9.0, 'label': 'PSA 9', 'price': 18.36,
         'range': {'mean': 19.0, 'sd': 1.41, 'low': 16.67, 'high': 21.33, 'count': 2},
         'sold_count_30d': 12},
        {'tier': 'psa_8', 'grade': 8.0, 'label': 'PSA 8', 'price': 13.18,
         'range': {'mean': 13.18, 'sd': 3.95, 'low': 9.23, 'high': 17.13, 'count': 1},
         'sold_count_30d': 8},
        {'tier': 'psa_lower', 'grade': 7.0, 'label': 'PSA 7', 'price': 12.75,
         'range': {'mean': 12.75, 'sd': 3.82, 'low': 8.92, 'high': 16.57, 'count': 0},
         'sold_count_30d': 0},
        {'tier': 'raw', 'grade': None, 'label': 'Raw (Ungraded)', 'price': 1.50,
         'range': {'mean': 2.0, 'sd': 0.0, 'low': 2.0, 'high': 2.0, 'count': 1},
         'sold_count_30d': 5},
    ]
    print(format_per_grade_ticker(sample))

    print("\n" + "="*70)
    print("format_below_market_deals test")
    print("="*70)

    sample_items = [
        {'title': '1996 Topps Chrome #80 Derek Jeter PSA 7', 'price_usd': 5.0, 'url': '#'},
        {'title': '1996 Topps Chrome #80 Derek Jeter BGS 9.5', 'price_usd': 200.0, 'url': '#'},
        {'title': '1995 Topps Jeter Future Star', 'price_usd': 0.50, 'url': '#'},
        {'title': 'PSA 10 GEM MINT Jeter #199', 'price_usd': 50.0, 'url': '#'},
    ]
    result = format_below_market_deals(sample_items, sample)
    if result:
        print(f"Found {result['total_found']} below-market deals:")
        for d in result['deals']:
            print(f"  ${d['price_usd']} {d['grade_label']} | typical ${d['typical_low']:.2f}-${d['typical_high']:.2f} | {d['discount_pct']:.0f}% off")
    else:
        print("No deals below market range")
