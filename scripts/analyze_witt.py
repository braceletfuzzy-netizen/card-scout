"""Analyze Witt 30-30 price data and produce the case study markdown."""

import json
from datetime import date, timedelta
from pathlib import Path

RAW = Path(r'C:\Users\J\Documents\LLM\cardscout-2.0\For You\Research\event_case_studies\witt_price_raw.json')
OUT = Path(r'C:\Users\J\Documents\LLM\cardscout-2.0\For You\Research\event_case_studies\witt_3030_case_study.md')

data = json.loads(RAW.read_text())
raw_prices = data['prices']  # list of {date, price}

# Build sorted list of (date_str, price_float) tuples
sorted_items = sorted([(p['date'], float(p['price'])) for p in raw_prices], key=lambda x: x[0])

# Build lookup: date -> price
price_map = {d: p for d, p in sorted_items}

# ---- HELPERS ----

def closest_on_or_before(target):
    """Return (date, price) for the closest date <= target."""
    best = None
    for d, p in sorted_items:
        if d <= target:
            best = (d, p)
        else:
            break
    return best

def month_slice(year, month):
    """Return all (date, price) in given YYYY-MM."""
    prefix = f'{year:04d}-{month:02d}'
    return [(d, p) for d, p in sorted_items if d[:7] == prefix]

def month_avg(year, month):
    items = month_slice(year, month)
    return sum(p for _, p in items) / len(items) if items else None

def month_stats(year, month):
    items = month_slice(year, month)
    if not items:
        return None
    prices = [p for _, p in items]
    peak = max(items, key=lambda x: x[1])
    return {
        'avg': sum(prices) / len(prices),
        'min': min(prices),
        'max': max(prices),
        'peak_date': peak[0],
        'peak_price': peak[1],
        'count': len(items),
    }

# ---- KEY ANALYTICS ----

# Pre-30-30 baseline: May-Aug 2024
may_aug_2024 = month_slice(2024, 5) + month_slice(2024, 6) + month_slice(2024, 7) + month_slice(2024, 8)
may_aug_avg = sum(p for _, p in may_aug_2024) / len(may_aug_2024) if may_aug_2024 else None

# Early August (pre-chase): Aug 1-15
early_aug = [(d, p) for d, p in sorted_items if '2024-08-01' <= d <= '2024-08-15']
early_aug_avg = sum(p for _, p in early_aug) / len(early_aug) if early_aug else None
early_aug_max = max(p for _, p in early_aug) if early_aug else None

# Late August (chase heats up): Aug 16-31
late_aug = [(d, p) for d, p in sorted_items if '2024-08-16' <= d <= '2024-08-31']
late_aug_avg = sum(p for _, p in late_aug) / len(late_aug) if late_aug else None
late_aug_max = max(p for _, p in late_aug) if late_aug else None
late_aug_min = min(p for _, p in late_aug) if late_aug else None

# September 2024 — the 30-30 month
sep = month_stats(2024, 9)

# October 2024 — immediate aftermath
oct_st = month_stats(2024, 10)

# Q4 2024 (Oct-Dec)
q4_2024 = month_slice(2024, 10) + month_slice(2024, 11) + month_slice(2024, 12)
q4_avg = sum(p for _, p in q4_2024) / len(q4_2024) if q4_2024 else None
q4_max = max(p for _, p in q4_2024) if q4_2024 else None
q4_min = min(p for _, p in q4_2024) if q4_2024 else None

# January 2025
jan_2025_items = month_slice(2025, 1)
jan_avg = sum(p for _, p in jan_2025_items) / len(jan_2025_items) if jan_2025_items else None
jan_end = jan_2025_items[-1][1] if jan_2025_items else None
jan_end_date = jan_2025_items[-1][0] if jan_2025_items else None

# Full year 2025
y2025_items = month_slice(2025, 1) + month_slice(2025, 2) + month_slice(2025, 3) + \
              month_slice(2025, 4) + month_slice(2025, 5) + month_slice(2025, 6) + \
              month_slice(2025, 7) + month_slice(2025, 8) + month_slice(2025, 9) + \
              month_slice(2025, 10) + month_slice(2025, 11) + month_slice(2025, 12)
y2025_avg = sum(p for _, p in y2025_items) / len(y2025_items) if y2025_items else None
y2025_high = max(p for _, p in y2025_items) if y2025_items else None
y2025_low = min(p for _, p in y2025_items) if y2025_items else None

# 2026 YTD (through latest)
y2026_items = month_slice(2026, 1) + month_slice(2026, 2) + month_slice(2026, 3) + \
              month_slice(2026, 4) + month_slice(2026, 5) + month_slice(2026, 6) + \
              month_slice(2026, 7) + month_slice(2026, 8) + month_slice(2026, 9)
y2026_avg = sum(p for _, p in y2026_items) / len(y2026_items) if y2026_items else None
y2026_high = max(p for _, p in y2026_items) if y2026_items else None

# May 1, 2024 → Dec 31, 2024 move
may_1 = closest_on_or_before('2024-05-01')
dec_31 = closest_on_or_before('2025-01-01')  # last price of 2024
if may_1 and dec_31:
    pop_pct = (dec_31[1] - may_1[1]) / may_1[1] * 100
else:
    pop_pct = None

# Pre-event (May 1) → Peak (Sep 11)
sep_peak = closest_on_or_before('2024-09-11')
if may_1 and sep_peak:
    peak_pop_pct = (sep_peak[1] - may_1[1]) / may_1[1] * 100
else:
    peak_pop_pct = None

# Post-peak → end of year reversion
if sep_peak and dec_31:
    reversion = (dec_31[1] - sep_peak[1]) / sep_peak[1] * 100
else:
    reversion = None

# All-time
all_prices = [p for _, p in sorted_items]
all_time_high = max(all_prices)
all_time_high_item = max(sorted_items, key=lambda x: x[1])
all_time_high_date = all_time_high_item[0]
all_time_low = min(all_prices)
all_time_low_item = min(sorted_items, key=lambda x: x[1])
all_time_low_date = all_time_low_item[0]

# Oct 28, 2025 outlier
oct_28_2025_item = closest_on_or_before('2025-10-28')
oct_28_2025 = oct_28_2025_item[1] if oct_28_2025_item and oct_28_2025_item[0] == '2025-10-28' else None

# Late Sep → Oct avg reversion
late_sep_items = [(d, p) for d, p in sorted_items if '2024-09-20' <= d <= '2024-09-30']
late_sep_avg = sum(p for _, p in late_sep_items) / len(late_sep_items) if late_sep_items else None
oct_items = month_slice(2024, 10)
oct_avg = sum(p for _, p in oct_items) / len(oct_items) if oct_items else None

# 30-30 achievement date context: Witt reached 30 SB on Sep 11, 2024
# Let's see Sep 10, 11, 12 specifically
sep_10 = closest_on_or_before('2024-09-10')
sep_11 = closest_on_or_before('2024-09-11')
sep_12 = closest_on_or_before('2024-09-12')

# Pre-30-30 "steady state": Feb-Apr 2024
feb_apr_2024 = month_slice(2024, 2) + month_slice(2024, 3) + month_slice(2024, 4)
feb_apr_avg = sum(p for _, p in feb_apr_2024) / len(feb_apr_2024) if feb_apr_2024 else None

print(f'=== KEY ANALYTICS ===')
print(f'Feb-Apr 2024 baseline (pre-rally): ${feb_apr_avg:,.2f}')
print(f'May 1, 2024 (pre-30-30 steady state): ${may_1[1]:,.2f} ({may_1[0]})')
print(f'Early Aug 2024 (pre-chase): ${early_aug_avg:,.2f}, max ${early_aug_max:,.2f}')
print(f'Late Aug 2024 (chase begins): avg ${late_aug_avg:,.2f}, range ${late_aug_min:,.2f}-${late_aug_max:,.2f}')
print(f'September 2024 (30-30 month): avg ${sep["avg"]:,.2f}, range ${sep["min"]:,.2f}-${sep["max"]:,.2f}')
print(f'  Peak: ${sep["peak_price"]:,.2f} on {sep["peak_date"]}')
print(f'  Sep 10 (day before milestone): ${sep_10[1]:,.2f}' if sep_10 else '  Sep 10: N/A')
print(f'  Sep 11 (30 SB achieved!): ${sep_11[1]:,.2f}' if sep_11 else '  Sep 11: N/A')
print(f'  Sep 12 (day after): ${sep_12[1]:,.2f}' if sep_12 else '  Sep 12: N/A')
print(f'October 2024: avg ${oct_st["avg"]:,.2f}, range ${oct_st["min"]:,.2f}-${oct_st["max"]:,.2f}')
print(f'Q4 2024 (Oct-Dec): avg ${q4_avg:,.2f}, range ${q4_min:,.2f}-${q4_max:,.2f}')
print(f'January 2025: avg ${jan_avg:,.2f}, end: ${jan_end:,.2f} ({jan_end_date})')
print(f'Full year 2025: avg ${y2025_avg:,.2f}, high ${y2025_high:,.2f}, low ${y2025_low:,.2f}')
print(f'2026 YTD (through Sep): avg ${y2026_avg:,.2f}, high ${y2026_high:,.2f}')
print()
print(f'May 1 → Dec 31, 2024: ${may_1[1]:,.2f} → ${dec_31[1]:,.2f} = {pop_pct:+.1f}%')
print(f'May 1 → Sep 11 peak: ${may_1[1]:,.2f} → ${sep_peak[1]:,.2f} = {peak_pop_pct:+.1f}%')
print(f'Sep 11 peak → Dec 31: ${sep_peak[1]:,.2f} → ${dec_31[1]:,.2f} = {reversion:+.1f}%')
print(f'Late Sep avg → Oct avg: ${late_sep_avg:,.2f} → ${oct_avg:,.2f}')
print(f'Oct 28, 2025 outlier: ${oct_28_2025:,.2f}' if oct_28_2025 else 'Oct 28, 2025: N/A')
print(f'All-time high: ${all_time_high:,.2f} on {all_time_high_date}')
print(f'All-time low: ${all_time_low:,.2f} on {all_time_low_date}')

# Save analytics
analytics = {
    'feb_apr_avg': feb_apr_avg,
    'may_1_date': may_1[0], 'may_1_price': may_1[1],
    'early_aug_avg': early_aug_avg, 'early_aug_max': early_aug_max,
    'late_aug_avg': late_aug_avg, 'late_aug_min': late_aug_min, 'late_aug_max': late_aug_max,
    'sep': sep,
    'sep_10': sep_10,
    'sep_11': sep_11,
    'sep_12': sep_12,
    'oct_st': oct_st,
    'q4_avg': q4_avg, 'q4_min': q4_min, 'q4_max': q4_max,
    'jan_avg': jan_avg, 'jan_end': jan_end, 'jan_end_date': jan_end_date,
    'y2025_avg': y2025_avg, 'y2025_high': y2025_high, 'y2025_low': y2025_low,
    'y2026_avg': y2026_avg, 'y2026_high': y2026_high,
    'pop_pct': pop_pct,
    'peak_pop_pct': peak_pop_pct,
    'reversion': reversion,
    'late_sep_avg': late_sep_avg,
    'oct_avg': oct_avg,
    'oct_28_2025': oct_28_2025,
    'all_time_high': all_time_high, 'all_time_high_date': all_time_high_date,
    'all_time_low': all_time_low, 'all_time_low_date': all_time_low_date,
    'pre_3030_baseline': may_aug_avg,
    'may_aug_2024_count': len(may_aug_2024),
    'late_aug_2024_count': len(late_aug),
    'sep_2024_count': sep['count'],
    'q4_2024_count': len(q4_2024),
    'jan_2025_count': len(jan_2025_items),
    'y2025_count': len(y2025_items),
    'y2026_count': len(y2026_items),
}

analytics_path = Path(r'C:\Users\J\Documents\LLM\cardscout-2.0\For You\Research\event_case_studies\witt_analytics.json')
analytics_path.write_text(json.dumps(analytics, indent=2, default=str))
print(f'\nAnalytics saved to: {analytics_path}')
