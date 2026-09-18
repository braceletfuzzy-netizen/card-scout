"""Sept 18 — Tier-aware alert scheduler.

Replaces the single shared cron with 4 tier-specific crons:
- Casual/Standard/Beta/Trial: 3x/week (MWF)
- Dealer: 1/day
- Pro: 3x/day

Each cron calls run_alerts.py --tiers X which selects only customers in those
tiers and applies throttle logic for big portfolios.
"""
import sys
import os
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))


def get_customer_card_counts():
    """Return {customer_id: enabled_card_count}."""
    conn = sqlite3.connect('card_scout.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT customer_id, COUNT(*) as card_count
        FROM cards
        WHERE enabled = 1
        GROUP BY customer_id
    """)
    counts = {r['customer_id']: r['card_count'] for r in cur.fetchall()}
    conn.close()
    return counts


def get_customers_by_tier(tiers):
    """Return list of customer_ids in the given tiers (with active settings)."""
    conn = sqlite3.connect('card_scout.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    placeholders = ','.join('?' for _ in tiers)
    cur.execute(f"""
        SELECT cs.customer_id, c.customer_id as slug, c.email,
               cs.tier, cs.max_cards, cs.alert_runs_per_month,
               cs.allow_sell_window, c.discord_webhook
        FROM customer_settings cs
        JOIN customers c ON cs.customer_id = c.id
        WHERE cs.tier IN ({placeholders})
          AND c.discord_webhook IS NOT NULL
    """, tiers)
    customers = [dict(r) for r in cur.fetchall()]
    conn.close()
    return customers


def compute_effective_runs(tier, card_count):
    """Apply throttling logic: tier base cadence × card-count factor.

    Path A (Sept 18): tier has base cadence, throttled DOWN for big portfolios.

    Cadence runs/mo:
    - Casual: 4 (1/week), no throttle
    - Standard: 12 (3/wk) ≤25 cards, 4 (1/wk) >25
    - Dealer: 30 (1/day) ≤25, 12 (3/wk) 26-100, 4 (1/wk) >100
    - Pro: 90 (3/day) ≤25, 30 (1/day) 26-100, 12 (3/wk) >100
    """
    base_runs = {
        'casual': 4,
        'standard': 12,
        'dealer': 30,
        'pro': 90,
        'beta_power': 12,  # Same as Standard
        'trial': 12,
    }.get(tier, 12)

    # Throttle down based on card count
    if tier in ('dealer', 'pro'):
        if card_count <= 25:
            return base_runs
        elif card_count <= 100:
            return max(4, base_runs // 3)  # 30 for Pro, 12 for Dealer
        else:
            return max(4, base_runs // 6)  # 12 for Pro, 4 for Dealer
    elif tier in ('standard', 'beta_power', 'trial'):
        if card_count <= 25:
            return base_runs
        else:
            return 4  # Drop to 1/week
    else:  # casual
        return base_runs


def compute_effective_max_cards(tier):
    """Return max_cards for this tier."""
    return {
        'casual': 25,
        'standard': 75,
        'dealer': 250,
        'pro': 999,
        'beta_power': 25,
        'trial': 25,
    }.get(tier, 25)


def main():
    parser = argparse.ArgumentParser(description='Tier-aware Card Scout alerts')
    parser.add_argument('--tiers', required=True, help='Comma-separated tier names (e.g. casual,standard)')
    parser.add_argument('--dry-run', action='store_true', help='Print plan, do not actually run')
    args = parser.parse_args()

    tiers = [t.strip() for t in args.tiers.split(',')]
    print(f'=== Tier-aware alerts: {tiers} ===\n')

    # Get customers in these tiers
    customers = get_customers_by_tier(tiers)
    print(f'Found {len(customers)} customers in tiers {tiers}')

    if not customers:
        print('No customers to process. Exiting.')
        return

    # Get card counts
    card_counts = get_customer_card_counts()

    # Print plan
    total_estimated_cost = 0.0
    print(f'\n{"Customer":<30} {"Tier":<12} {"Cards":<6} {"Runs/mo":<9} {"Cost/mo":<10}')
    print('-' * 75)

    cost_per_run = 0.0353 + 0.0033  # eBay + SCPro

    for cust in customers:
        cards = card_counts.get(cust['customer_id'], 0)
        effective_runs = compute_effective_runs(cust['tier'], cards)
        monthly_cost = cards * effective_runs * cost_per_run
        total_estimated_cost += monthly_cost
        print(f'  {cust["slug"]:<28} {cust["tier"]:<12} {cards:<6} {effective_runs:<9} ${monthly_cost:.2f}')

    print(f'\nTotal estimated monthly cost for these tiers: ${total_estimated_cost:.2f}')

    if args.dry_run:
        print('\n[DRY RUN] Not actually running alerts.')
        return

    # Run actual alert logic — delegated to existing run_bot.py
    # run_bot.py forwards --tiers to discord_alert_bot_v3.py (Sept 18 tier scheduler)
    print(f'\n[EXEC] Running alert logic for tiers={tiers}...')
    import subprocess
    import os
    # Inherit env so dotenv + .env loading works in subprocess
    env = os.environ.copy()
    r = subprocess.run(
        ['python', 'run_bot.py', '--tiers', ','.join(tiers)],
        capture_output=True, text=True, timeout=1800, env=env,
    )
    print(r.stdout[-3000:] if len(r.stdout) > 3000 else r.stdout)
    if r.returncode != 0:
        print(f'\nERROR: {r.stderr[-1000:]}')
    else:
        print(f'\n✓ Done')


if __name__ == '__main__':
    main()
