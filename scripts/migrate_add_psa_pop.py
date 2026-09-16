"""
Migration: Add PSA population columns to cards table.

Adds 4 columns to persist PSA pop data:
- psa_total_pop: total PSA-graded count for this card
- psa_10_pop: PSA 10 count (highest grade)
- psa_9_pop: PSA 9 count
- psa_pop_fetched_at: timestamp of last successful fetch

This enables the "stock ticker" feature (founder's Sept 16 insight):
- Compute rarity % (PSA 10 as % of total)
- Show grade hierarchy (A/B/C/D classes)
- Display market depth

Run: python scripts/migrate_add_psa_pop.py
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from db_models import init_db, get_session


def migrate():
    """Add psa_* columns to cards table."""
    print("=" * 70)
    print("PSA POP MIGRATION")
    print("=" * 70)

    init_db()
    session = get_session()

    # Check current schema
    print("\n[Step 1] Checking current schema...")
    result = session.execute(text("PRAGMA table_info(cards)"))
    existing_columns = {row[1] for row in result.fetchall()}
    print(f"  Existing columns: {len(existing_columns)}")

    # Columns to add
    new_columns = [
        ("psa_total_pop", "INTEGER"),
        ("psa_10_pop", "INTEGER"),
        ("psa_9_pop", "INTEGER"),
        ("psa_pop_fetched_at", "TIMESTAMP"),
    ]

    # Add missing columns
    print("\n[Step 2] Adding missing columns...")
    added = []
    skipped = []
    for col_name, col_type in new_columns:
        if col_name in existing_columns:
            print(f"  [SKIP] {col_name} already exists")
            skipped.append(col_name)
        else:
            try:
                session.execute(text(f"ALTER TABLE cards ADD COLUMN {col_name} {col_type}"))
                session.commit()
                print(f"  [OK] Added {col_name} ({col_type})")
                added.append(col_name)
            except Exception as e:
                print(f"  [FAIL] {col_name}: {e}")
                session.rollback()

    # Verify
    print("\n[Step 3] Verifying schema...")
    result = session.execute(text("PRAGMA table_info(cards)"))
    new_schema = {row[1] for row in result.fetchall()}
    for col_name, _ in new_columns:
        if col_name in new_schema:
            print(f"  [OK] {col_name} present")
        else:
            print(f"  [FAIL] {col_name} missing")

    print(f"\n{'='*70}")
    print(f"Added: {len(added)} | Skipped: {len(skipped)}")
    print(f"{'='*70}")

    session.close()
    return len(added)


if __name__ == '__main__':
    migrate()
