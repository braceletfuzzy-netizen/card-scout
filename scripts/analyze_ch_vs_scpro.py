"""Analyze the Card Hedger vs SCPro comparison log.

Reads /data/card_hedger_vs_scpro.log (or local card_hedger_vs_scpro.log),
groups by card_id, computes summary stats, and surfaces patterns.

Usage:
  python scripts/analyze_ch_vs_scpro.py [--log path]

Outputs:
- Per-card stats (mean CH price, mean SCPro price, mean % diff, confidence)
- Aggregate patterns (e.g., does higher CH confidence → smaller % diff?)
- Recommendations for Sept 24 decision
"""
import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


def parse_log(log_path: str) -> list:
    """Parse the JSON log file into a list of dicts."""
    entries = []
    if not Path(log_path).exists():
        return entries

    with open(log_path) as f:
        for line in f:
            # Format: "TIMESTAMP {json}"
            m = re.match(r'^(\S+ \S+) (.+)$', line.strip())
            if not m:
                continue
            ts, json_part = m.groups()
            try:
                entry = json.loads(json_part)
                entry['_ts'] = ts
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def analyze(entries: list) -> dict:
    """Analyze comparison entries and return summary stats."""
    if not entries:
        return {'error': 'no_entries'}

    # Group by card_id
    by_card = defaultdict(list)
    for e in entries:
        by_card[e['card_id']].append(e)

    # Per-card aggregates
    per_card = {}
    for cid, items in by_card.items():
        ch_prices = [i['card_hedger_price'] for i in items if i.get('card_hedger_price')]
        sc_prices = [i['scpro_price'] for i in items if i.get('scpro_price') is not None]
        pct_diffs = [i['pct_difference'] for i in items if i.get('pct_difference') is not None]
        confidences = [i['card_hedger_confidence'] for i in items if i.get('card_hedger_confidence')]

        # Latest grade (from latest entry)
        latest_grade = items[-1].get('card_hedger_grade')
        latest_confidence = items[-1].get('card_hedger_confidence')

        per_card[cid] = {
            'search_query': items[-1]['search_query'],
            'n_runs': len(items),
            'latest_ch_price': ch_prices[-1] if ch_prices else None,
            'latest_sc_price': sc_prices[-1] if sc_prices else None,
            'mean_ch_price': statistics.mean(ch_prices) if ch_prices else None,
            'mean_sc_price': statistics.mean(sc_prices) if sc_prices else None,
            'mean_pct_diff': statistics.mean(pct_diffs) if pct_diffs else None,
            'median_pct_diff': statistics.median(pct_diffs) if pct_diffs else None,
            'abs_pct_diff': [abs(p) for p in pct_diffs if p is not None],
            'card_hedger_grade': latest_grade,
            'card_hedger_confidence': latest_confidence,
        }

    # Patterns
    grades = ['A', 'B', 'C', 'D']
    by_grade = defaultdict(list)
    for cid, stats in per_card.items():
        g = stats['card_hedger_grade']
        if g and stats['mean_pct_diff'] is not None:
            by_grade[g].append({
                'card_id': cid,
                'search_query': stats['search_query'],
                'mean_pct_diff': stats['mean_pct_diff'],
                'confidence': stats['card_hedger_confidence'],
                'ch_price': stats['latest_ch_price'],
                'sc_price': stats['latest_sc_price'],
            })

    # Aggregate
    all_pct_diffs = []
    for stats in per_card.values():
        if stats['mean_pct_diff'] is not None:
            all_pct_diffs.append(stats['mean_pct_diff'])

    return {
        'total_entries': len(entries),
        'unique_cards': len(per_card),
        'per_card': per_card,
        'by_grade': dict(by_grade),
        'overall': {
            'mean_pct_diff': statistics.mean(all_pct_diffs) if all_pct_diffs else None,
            'median_pct_diff': statistics.median(all_pct_diffs) if all_pct_diffs else None,
            'cards_with_diff': len(all_pct_diffs),
        },
        'grades': grades,
    }


def main():
    parser = argparse.ArgumentParser(description='Analyze Card Hedger vs SCPro log')
    parser.add_argument('--log', default='card_hedger_vs_scpro.log', help='Path to log file')
    args = parser.parse_args()

    print(f'Analyzing {args.log}...')
    print()
    entries = parse_log(args.log)
    print(f'Found {len(entries)} log entries')
    print()

    if not entries:
        print('No entries to analyze')
        return

    result = analyze(entries)

    # Print summary
    print('=' * 70)
    print('OVERALL')
    print('=' * 70)
    o = result['overall']
    print(f'  Total entries: {result["total_entries"]}')
    print(f'  Unique cards compared: {result["unique_cards"]}')
    print(f'  Mean % difference: {o["mean_pct_diff"]:.1f}%' if o["mean_pct_diff"] else '  Mean % difference: N/A')
    print(f'  Median % difference: {o["median_pct_diff"]:.1f}%' if o["median_pct_diff"] else '  Median % difference: N/A')
    print()

    # By grade
    print('=' * 70)
    print('PATTERNS BY CARD HEDGER GRADE')
    print('=' * 70)
    for g in result['grades']:
        cards = result['by_grade'].get(g, [])
        if not cards:
            continue
        diffs = [c['mean_pct_diff'] for c in cards if c['mean_pct_diff'] is not None]
        print(f'\n  Grade {g}: {len(cards)} cards')
        if diffs:
            print(f'    Mean % diff: {statistics.mean(diffs):.1f}%')
            print(f'    Median % diff: {statistics.median(diffs):.1f}%')
        print(f'    Cards:')
        for c in cards:
            conf = c['confidence'] or 0
            ch = c['ch_price']
            sc = c['sc_price']
            ch_str = f'${ch:,.2f}' if ch else 'N/A'
            sc_str = f'${sc:,.2f}' if sc else 'N/A'
            pct_str = f'{c["mean_pct_diff"]:.1f}%' if c['mean_pct_diff'] else 'N/A'
            print(f'      {c["search_query"][:35]:35} | CH {ch_str:>12} | SC {sc_str:>12} | diff {pct_str:>10} | conf {conf:.2f}')

    # Per-card detail
    print()
    print('=' * 70)
    print('PER-CARD DETAIL (sorted by % diff magnitude)')
    print('=' * 70)
    cards_with_diff = [(cid, s) for cid, s in result['per_card'].items() if s['mean_pct_diff'] is not None]
    cards_with_diff.sort(key=lambda x: abs(x[1]['mean_pct_diff']), reverse=True)

    for cid, stats in cards_with_diff:
        ch = stats['latest_ch_price']
        sc = stats['latest_sc_price']
        ch_str = f'${ch:,.2f}' if ch else 'N/A'
        sc_str = f'${sc:,.2f}' if sc else 'N/A'
        pct_str = f'{stats["mean_pct_diff"]:.1f}%' if stats['mean_pct_diff'] else 'N/A'
        grade = stats['card_hedger_grade'] or '?'
        conf = stats['card_hedger_confidence'] or 0
        print(f'  {stats["search_query"][:38]:38} | grade {grade} conf {conf:.2f} | CH {ch_str:>13} | SC {sc_str:>13} | diff {pct_str:>10}')

    print()
    print('=' * 70)
    print('INTERPRETATION')
    print('=' * 70)
    print()
    print('Card Hedger gives: PSA 10 Fair Market Value (FMV) - what a graded card is worth.')
    print('SCPro gives:        Median of active eBay listings (often raw + various grades).')
    print()
    print('Expected pattern: SCPro median is usually LOWER than PSA 10 FMV because it')
    print('includes raw cards and lower grades. So CH > SC is expected.')
    print()
    # Compute CH > SC ratio
    ch_gt_sc = sum(1 for cid, s in result['per_card'].items() if s['latest_ch_price'] and s['latest_sc_price'] and s['latest_ch_price'] > s['latest_sc_price'])
    ch_lt_sc = sum(1 for cid, s in result['per_card'].items() if s['latest_ch_price'] and s['latest_sc_price'] and s['latest_ch_price'] < s['latest_sc_price'])
    ch_eq_sc = sum(1 for cid, s in result['per_card'].items() if s['latest_ch_price'] and s['latest_sc_price'] and s['latest_ch_price'] == s['latest_sc_price'])
    print(f'CH > SC (PSA 10 > listing median): {ch_gt_sc} cards')
    print(f'CH < SC (rare, often listing has premium example): {ch_lt_sc} cards')
    print(f'CH = SC: {ch_eq_sc} cards')
    print()
    # Confidence distribution
    print('Card Hedger confidence distribution:')
    confs = [s['card_hedger_confidence'] for s in result['per_card'].values() if s['card_hedger_confidence'] is not None]
    high_conf = sum(1 for c in confs if c >= 0.9)
    med_conf = sum(1 for c in confs if 0.5 <= c < 0.9)
    low_conf = sum(1 for c in confs if c < 0.5)
    print(f'  High (>=0.9): {high_conf} cards - reliable FMV')
    print(f'  Med (0.5-0.9): {med_conf} cards - decent')
    print(f'  Low (<0.5): {low_conf} cards - sparse market, FMV is guess')
    print()
    print('Sept 24 decision implications:')
    print('- SCPro gives ACTIVE listings (current buy-side opportunity)')
    print('- Card Hedger gives HISTORICAL FMV (what card sold for recently)')
    print('- Both serve different purposes. CH FMV is better for "is this a good deal?"')
    print('  because it shows the actual market value, not the median of noisy listings.')


if __name__ == '__main__':
    main()
