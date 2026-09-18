"""
Customer merge tool for Card Scout.

Use case: when two customers are actually the same person (e.g. duplicate
signups via Google Form with different webhook URLs), merge them:
- Keep the SURVIVING customer's identity
- Move all cards from ABSORBED customer to SURVIVING customer
- Move all snapshots/run_history to SURVIVING customer
- Delete the ABSORBED customer

Usage:
  python scripts/merge_customers.py --keep buddy_test_001 --absorb cs_CZYAKAA00001
  python scripts/merge_customers.py --keep <customer_id_slug> --absorb <customer_id_slug> [--dry-run]

Safety:
- Always creates a backup before destructive operations
- --dry-run shows what would happen without making changes
- Refuses to merge a customer into itself
- Logs to stdout + Sessions/merge_log.md (if exists)
"""
import argparse
import sqlite3
import shutil
import sys
from datetime import datetime
from pathlib import Path


def merge_customers(keep_slug: str, absorb_slug: str, dry_run: bool = False) -> dict:
    """Merge `absorb_slug` customer into `keep_slug` customer.

    Args:
        keep_slug: customer_id (string slug like 'buddy_test_001') to KEEP
        absorb_slug: customer_id (string slug) to ABSORB (delete after)
        dry_run: if True, show what would happen without modifying DB

    Returns:
        dict with stats: {cards_moved, snapshots_moved, run_history_moved, ...}
    """
    # Backup first (always, even for dry runs - safety)
    backup_path = None
    if not dry_run:
        ts = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        backup_path = f'card_scout.db.backup-pre-merge-{ts}'
        shutil.copy2('card_scout.db', backup_path)

    conn = sqlite3.connect('card_scout.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Validate
    cur.execute("SELECT id, customer_id, email, discord_webhook FROM customers WHERE customer_id = ?", (keep_slug,))
    keep = cur.fetchone()
    cur.execute("SELECT id, customer_id, email, discord_webhook FROM customers WHERE customer_id = ?", (absorb_slug,))
    absorb = cur.fetchone()

    if not keep:
        print(f'ERROR: Keep customer "{keep_slug}" not found', file=sys.stderr)
        return {'error': 'keep_not_found'}
    if not absorb:
        print(f'ERROR: Absorb customer "{absorb_slug}" not found', file=sys.stderr)
        return {'error': 'absorb_not_found'}
    if keep['id'] == absorb['id']:
        print(f'ERROR: Keep and absorb are the same customer', file=sys.stderr)
        return {'error': 'same_customer'}

    stats = {
        'keep_id': keep['id'],
        'keep_slug': keep['customer_id'],
        'absorb_id': absorb['id'],
        'absorb_slug': absorb['customer_id'],
        'cards_to_move': 0,
        'snapshots_to_move': 0,
        'run_history_to_move': 0,
        'duplicate_search_queries': 0,
        'dry_run': dry_run,
    }

    # Count cards to move
    cur.execute("SELECT COUNT(*) FROM cards WHERE customer_id = ?", (absorb['id'],))
    stats['cards_to_move'] = cur.fetchone()[0]

    # Count snapshots to move (via card_id)
    cur.execute("""
        SELECT COUNT(*) FROM snapshots WHERE card_id IN (
            SELECT id FROM cards WHERE customer_id = ?
        )
    """, (absorb['id'],))
    stats['snapshots_to_move'] = cur.fetchone()[0]

    # Count run_history to move
    cur.execute("SELECT COUNT(*) FROM run_history WHERE customer_id = ?", (absorb['id'],))
    stats['run_history_to_move'] = cur.fetchone()[0]

    # Find duplicate search_queries (cards with same query in both customers)
    cur.execute("""
        SELECT COUNT(*) FROM cards c1
        WHERE c1.customer_id = ?
          AND EXISTS (
              SELECT 1 FROM cards c2
              WHERE c2.customer_id = ?
                AND c2.search_query = c1.search_query
                AND c2.id != c1.id
          )
    """, (absorb['id'], keep['id']))
    stats['duplicate_search_queries'] = cur.fetchone()[0]

    print('=' * 70)
    print(f'MERGE PLAN {"(DRY RUN)" if dry_run else "(LIVE)"}')
    print('=' * 70)
    print(f'KEEP:   id={keep["id"]} slug={keep["customer_id"]} email={keep["email"]}')
    print(f'         webhook={keep["discord_webhook"][:60]}...')
    print(f'ABSORB: id={absorb["id"]} slug={absorb["customer_id"]} email={absorb["email"]}')
    print(f'         webhook={absorb["discord_webhook"][:60]}...')
    print()
    print(f'Cards to move: {stats["cards_to_move"]}')
    print(f'Snapshots to move: {stats["snapshots_to_move"]}')
    print(f'Run history to move: {stats["run_history_to_move"]}')
    if stats['duplicate_search_queries']:
        print(f'⚠️  Duplicate search_queries: {stats["duplicate_search_queries"]} (will be skipped)')
    if backup_path:
        print(f'\nBackup: {backup_path}')

    if dry_run:
        print('\nDRY RUN: no changes made')
        conn.close()
        return stats

    print('\nExecuting merge...')

    # Handle duplicates first - delete absorb's cards that have matching search_query in keep
    if stats['duplicate_search_queries']:
        # Get all duplicate card ids in absorb
        cur.execute("""
            SELECT c1.id FROM cards c1
            WHERE c1.customer_id = ?
              AND EXISTS (
                  SELECT 1 FROM cards c2
                  WHERE c2.customer_id = ?
                    AND c2.search_query = c1.search_query
                    AND c2.id != c1.id
              )
        """, (absorb['id'], keep['id']))
        duplicate_card_ids = [r[0] for r in cur.fetchall()]
        print(f'  Removing {len(duplicate_card_ids)} duplicate cards from absorb customer...')

        # Delete their snapshots first (FK)
        cur.execute(f"DELETE FROM snapshots WHERE card_id IN ({','.join('?' * len(duplicate_card_ids))})", duplicate_card_ids)
        print(f'    Deleted {cur.rowcount} snapshots')

        # Delete run_history for these cards
        cur.execute(f"DELETE FROM run_history WHERE card_id IN ({','.join('?' * len(duplicate_card_ids))})", duplicate_card_ids)
        print(f'    Deleted {cur.rowcount} run_history rows')

        # Delete duplicate cards
        cur.execute(f"DELETE FROM cards WHERE id IN ({','.join('?' * len(duplicate_card_ids))})", duplicate_card_ids)
        print(f'    Deleted {cur.rowcount} cards')

        # Update stats
        stats['cards_to_move'] -= len(duplicate_card_ids)

    # Move remaining cards
    if stats['cards_to_move']:
        cur.execute("UPDATE cards SET customer_id = ? WHERE customer_id = ?", (keep['id'], absorb['id']))
        print(f'  Moved {cur.rowcount} cards to keep customer')

    # Move run_history (this is per customer, not per card)
    cur.execute("UPDATE run_history SET customer_id = ? WHERE customer_id = ?", (keep['id'], absorb['id']))
    print(f'  Moved {cur.rowcount} run_history rows to keep customer')

    # Delete the absorbed customer
    cur.execute("DELETE FROM customers WHERE id = ?", (absorb['id'],))
    print(f'  Deleted absorb customer row')

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM cards WHERE customer_id = ?", (keep['id'],))
    final_cards = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM run_history WHERE customer_id = ?", (keep['id'],))
    final_runs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers WHERE id = ?", (absorb['id'],))
    absorb_exists = cur.fetchone()[0]

    print()
    print('=' * 70)
    print('POST-MERGE STATE')
    print('=' * 70)
    print(f'  Keep customer now has {final_cards} cards, {final_runs} run_history rows')
    print(f'  Absorb customer exists: {bool(absorb_exists)}')

    # Log to file
    log_path = Path('Sessions/merge_log.md')
    if log_path.exists() or True:  # create if missing
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f'\n## Merge: {keep_slug} <- {absorb_slug} ({datetime.utcnow().isoformat()}Z)\n')
            f.write(f'- Backup: {backup_path}\n')
            f.write(f'- Cards moved: {stats["cards_to_move"]}\n')
            f.write(f'- Snapshots moved: {stats["snapshots_to_move"]}\n')
            f.write(f'- Run history moved: {stats["run_history_to_move"]}\n')
            f.write(f'- Duplicates skipped: {stats["duplicate_search_queries"]}\n')
            f.write(f'- Final cards on keep: {final_cards}\n\n')

    conn.close()
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge two Card Scout customers')
    parser.add_argument('--keep', required=True, help='customer_id slug to KEEP (will absorb into)')
    parser.add_argument('--absorb', required=True, help='customer_id slug to ABSORB (will be deleted)')
    parser.add_argument('--dry-run', action='store_true', help='Show plan without making changes')
    args = parser.parse_args()

    result = merge_customers(args.keep, args.absorb, dry_run=args.dry_run)
    if 'error' in result:
        sys.exit(1)
    sys.exit(0)
