"""Daily cron job: clean up pricing_bands older than 30 days.

Run via install-scheduler.bat or manually:
    python cleanup_old_pricing_bands.py

Also runs once at startup as a safety net (idempotent).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db_models import init_db, get_session, cleanup_old_pricing_bands


def main():
    print("=" * 60)
    print("Card Scout Daily Pricing Band Cleanup")
    print("=" * 60)

    init_db()  # ensure tables exist
    session = get_session()

    deleted = cleanup_old_pricing_bands(session, retention_days=30)
    print(f"[OK] Cleaned up {deleted} pricing band rows older than 30 days")

    # Quick stats
    from db_models import PricingBand
    total = session.query(PricingBand).count()
    print(f"[OK] Total pricing band rows now: {total}")

    session.close()


if __name__ == '__main__':
    main()
