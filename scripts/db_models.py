"""
Database models for Card Scout.

Uses SQLAlchemy ORM with environment-based DB URL.
- SQLite now (development, 1 customer)
- Postgres (Supabase Pro) at 10 customers ($25/mo)
- Migration between them is ~30 minutes

Tables:
- customers: customer accounts (tier, webhook, settings)
- cards: cards in each customer's watchlist
- snapshots: price statistics over time (for trend detection)
- run_history: per-run summaries (audit trail, debugging)

Storage at 10 customers × 20 cards:
- 3 snapshots × 200 bytes = ~2 MB total
- Negligible vs Supabase 500 MB free / 8 GB pro limits
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, Text,
    ForeignKey, Index, UniqueConstraint, Date, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, date as date_type, timedelta
import os

Base = declarative_base()

# ============================================================================
# MODELS
# ============================================================================

class Customer(Base):
    """Customer account (Jim = first, future customers 2-N)."""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    discord_webhook = Column(Text, nullable=True)
    
    # Tier & status
    tier = Column(String(20), nullable=False, default='trial')  # trial, lite, standard, pro, beta, beta_power, beta_casual
    subscription_status = Column(String(20), default='trial')  # active, trial, paused, cancelled
    beta_end_date = Column(DateTime, nullable=True)
    
    # Limits (derived from tier)
    max_cards = Column(Integer, default=3)
    
    # Metadata
    joined_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    settings = Column(JSON, default=dict)  # tier-specific settings
    
    # Relationships
    cards = relationship('Card', back_populates='customer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Customer {self.customer_id} ({self.tier})>"
    
    @property
    def is_active(self):
        return self.subscription_status in ('active', 'trial')


class Card(Base):
    """A card in a customer's watchlist."""
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Card identification
    search_query = Column(String(500), nullable=False)
    preset = Column(String(50), default='cards-sports')
    alert_type = Column(String(50), default='below_median')
    max_listings = Column(Integer, default=15)
    
    # Status
    enabled = Column(Boolean, default=True)
    include_sold = Column(Boolean, default=False)  # Phase 2: sold comps
    include_pop = Column(Boolean, default=False)  # PSA population lookup
    psa_set_url = Column(String(500), nullable=True)  # PSA set URL for pop lookup
    sportscardspro_url = Column(String(500), nullable=True)  # sportscardspro.com OR pricecharting.com URL for sold data
    market_thin = Column(Integer, default=0, nullable=False)  # 1 = skip below-median deal detection; show market ticker + 90% CI only

    # V3 PSA Population Data (Sept 16 — stock-ticker insight)
    # Founder's framing: PSA grades are like stock classes (10=A, 9=B, 8=C).
    # Graded cards are stock certificates. Pop data = "outstanding shares."
    psa_total_pop = Column(Integer, nullable=True)        # total PSA-graded count
    psa_10_pop = Column(Integer, nullable=True)            # PSA 10 count (A-class)
    psa_9_pop = Column(Integer, nullable=True)             # PSA 9 count (B-class)
    psa_pop_fetched_at = Column(DateTime, nullable=True)   # when last fetched from PSA

    # Card Hedge integration (Sept 17 — inline card matcher)
    # card_id is Card Hedge's canonical ID for the matched card (string).
    # card_match_confidence is 0-1 score from AI matcher (or 1.0 if user-selected).
    # Both are nullable: cards added before Card Hedge integration have NULL.
    card_id = Column(String(100), nullable=True)
    card_match_confidence = Column(Float, nullable=True)

    # Card metadata for clean-data + math model (Sept 18)
    # era: decade (1980s, 1990s, 2000s, 2010s, 2020s)
    # category: top-level (Sports Cards, Pokemon, MTG, etc.)
    # subcategory: sport (Baseball, Football, Basketball, Hockey) or TCG sub
    # is_rookie: True if rookie card
    # is_key_card: True if particularly notable (Hank Aaron 1969 Topps, etc.)
    era = Column(String(20), nullable=True)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    is_rookie = Column(Boolean, nullable=True)
    is_key_card = Column(Boolean, nullable=True)

    # Vault / portfolio tracking (Sept 18 — PL-007 build)
    # cost_basis_usd: what the customer paid for this card. NULL = unknown.
    # cost_basis_set_date: when they acquired it. NULL = use added_date for ROI.
    # vault_notes: customer's free-text notes about this card.
    # Tier policy (Sept 18): Vault is FREE for all tiers. Differentiation is
    # in max_cards per tier (Casual=25, Standard=75, Dealer=250, Pro=unlimited)
    # and active alert treatment (Pro gets sell-window alerts on Vault items).
    cost_basis_usd = Column(Float, nullable=True)
    cost_basis_set_date = Column(Date, nullable=True)
    vault_notes = Column(Text, nullable=True)

    # Grade filter checkboxes (6-bucket system)
    # Customer picks which grades matter for THIS card
    track_psa_10 = Column(Boolean, default=True)       # Tier 1: Gem Mint
    track_psa_9 = Column(Boolean, default=True)        # Tier 2: Mint
    track_psa_8 = Column(Boolean, default=True)        # Tier 3: Upper mid
    track_psa_lower = Column(Boolean, default=True)    # Tier 4: PSA 7 or below
    track_raw = Column(Boolean, default=True)          # Ungraded
    track_other_graders = Column(Boolean, default=True)  # SGC, CGC, etc.
    
    # Metadata
    added_date = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Unique: same customer can't track same card twice
    __table_args__ = (
        UniqueConstraint('customer_id', 'search_query', name='uq_customer_card'),
        Index('idx_customer_enabled', 'customer_id', 'enabled'),
    )
    
    # Relationships
    customer = relationship('Customer', back_populates='cards')
    snapshots = relationship('Snapshot', back_populates='card', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Card {self.search_query[:50]} ({'on' if self.enabled else 'off'})>"


class Snapshot(Base):
    """Price statistics snapshot for trend detection.
    
    Three snapshots per card (rotating):
    - 'current': just ran
    - '7d': 1 week ago
    - '30d': 1 month ago
    
    On each run:
    - Current becomes new '7d'
    - Old '7d' becomes new '30d'  
    - Old '30d' is deleted
    
    Storage: ~200 bytes per snapshot = 600 bytes per card.
    """
    __tablename__ = 'snapshots'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False, index=True)
    
    # Window: which snapshot is this?
    window = Column(String(10), nullable=False)  # 'current', '7d', '30d'
    
    # When was this snapshot taken?
    taken_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Price statistics (the math, not raw listings)
    median_price = Column(Float, nullable=True)
    avg_price = Column(Float, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    
    # Quartile bands (the SHAPE of the market)
    q1_price = Column(Float, nullable=True)
    q2_price = Column(Float, nullable=True)  # = median but stored explicitly
    q3_price = Column(Float, nullable=True)
    
    # Volume signals
    total_listings = Column(Integer, default=0)
    items_with_sold_count = Column(Integer, default=0)
    total_sold_reported = Column(Integer, default=0)
    hot_items_count = Column(Integer, default=0)
    avg_sold_count = Column(Float, nullable=True)
    
    # Trend signal (computed when comparing snapshots)
    trend_signal = Column(String(30), nullable=True)  # ACCELERATING_UP, STEADY_UP, FLAT, COOLING, CRASHING, INSUFFICIENT_DATA
    
    __table_args__ = (
        UniqueConstraint('card_id', 'window', name='uq_card_window'),
        Index('idx_card_window', 'card_id', 'window'),
    )
    
    # Relationships
    card = relationship('Card', back_populates='snapshots')
    
    def __repr__(self):
        return f"<Snapshot {self.window} median=${self.median_price}>"


class RunHistory(Base):
    """Per-run audit trail (debugging + analytics)."""
    __tablename__ = 'run_history'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False, index=True)

    # Run metadata
    run_at = Column(DateTime, default=datetime.utcnow, index=True)
    apify_run_id = Column(String(100), nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Results summary
    total_listings = Column(Integer, default=0)
    matching_items = Column(Integer, default=0)
    deals_found = Column(Integer, default=0)
    alert_sent = Column(Boolean, default=False)
    alert_error = Column(Text, nullable=True)

    # Cost tracking (internal only - NEVER expose to customers)
    apify_cost = Column(Float, nullable=True)

    def __repr__(self):
        return f"<RunHistory {self.run_at} customer={self.customer_id}>"


class PricingBand(Base):
    """Daily pricing band per card, aggregated from sportscardspro/PriceCharting.

    Purpose:
    - Powers "30-day trend" feature (Jim's chart ask)
    - Foundation for V2 chart panel + photo app value calc
    - Source of truth for "below market by X%?" comparisons

    Storage estimate:
    - 1 row per card per day = 12 cards × 30 days = 360 rows max
    - Each row ~150 bytes = ~55 KB total @ 12 cards
    - Scales to 1,000 cards × 30 days = 30,000 rows = ~4.5 MB

    Lifecycle:
    - Inserted daily (cron job or piggyback on alert run)
    - Deleted automatically when older than 30 days (cleanup query)
    - PK is (card_id, band_date) — INSERT OR REPLACE semantics

    Why SQLAlchemy:
    - Migration to PostgreSQL/ClickHouse later is the same ORM code
    - Today: SQLite handles it. Tomorrow: change DATABASE_URL.
    """
    __tablename__ = 'pricing_bands'

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False, index=True)
    band_date = Column(Date, nullable=False, index=True)

    # Per-grade tiered pricing (one row covers all grades)
    raw_low = Column(Float, nullable=True)
    raw_high = Column(Float, nullable=True)
    raw_median = Column(Float, nullable=True)
    raw_volume = Column(Integer, default=0)

    psa_7_low = Column(Float, nullable=True)
    psa_7_high = Column(Float, nullable=True)
    psa_7_volume = Column(Integer, default=0)

    psa_8_low = Column(Float, nullable=True)
    psa_8_high = Column(Float, nullable=True)
    psa_8_volume = Column(Integer, default=0)

    psa_9_low = Column(Float, nullable=True)
    psa_9_high = Column(Float, nullable=True)
    psa_9_volume = Column(Integer, default=0)

    psa_9_5_low = Column(Float, nullable=True)
    psa_9_5_high = Column(Float, nullable=True)
    psa_9_5_volume = Column(Integer, default=0)

    psa_10_low = Column(Float, nullable=True)
    psa_10_high = Column(Float, nullable=True)
    psa_10_volume = Column(Integer, default=0)

    # Metadata
    captured_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(20), default='sportscardspro')  # future: tcgplayer, etc

    __table_args__ = (
        UniqueConstraint('card_id', 'band_date', name='uq_card_band_date'),
        Index('idx_band_date', 'band_date'),
    )

    # Relationship
    card = relationship('Card', backref='pricing_bands')

    def __repr__(self):
        return f"<PricingBand card={self.card_id} date={self.band_date}>"

    def to_summary_dict(self):
        """Compact view for API responses / alert embeds."""
        return {
            'card_id': self.card_id,
            'date': self.band_date.isoformat() if self.band_date else None,
            'raw': {'low': self.raw_low, 'high': self.raw_high, 'median': self.raw_median, 'volume': self.raw_volume},
            'psa_10': {'low': self.psa_10_low, 'high': self.psa_10_high, 'volume': self.psa_10_volume},
        }

    @classmethod
    def get_30day_window(cls, session, card_id, end_date=None):
        """Return pricing bands for last 30 days, ordered oldest first.

        Useful for trend chart.
        """
        from datetime import timedelta
        if end_date is None:
            end_date = date_type.today()
        start_date = end_date - timedelta(days=29)  # 30-day inclusive window

        return session.query(cls).filter(
            cls.card_id == card_id,
            cls.band_date >= start_date,
            cls.band_date <= end_date
        ).order_by(cls.band_date.asc()).all()


# ============================================================================
# DATABASE CONNECTION (Environment-based)
# ============================================================================

def get_database_url():
    """Get DB URL from env var. Defaults to SQLite for dev.

    Examples:
        DATABASE_URL=sqlite:///card_scout.db
        DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
    """
    env_url = os.getenv('DATABASE_URL')
    if env_url:
        return env_url
    # Default: SQLite in project root (one level up from scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.join(project_root, 'card_scout.db')
    return f'sqlite:///{db_path.replace(os.sep, "/")}'


def create_db_engine():
    """Create SQLAlchemy engine. Works with SQLite OR Postgres."""
    url = get_database_url()
    
    # SQLite-specific: enable WAL mode for better concurrency
    connect_args = {}
    if url.startswith('sqlite'):
        connect_args['check_same_thread'] = False
    
    engine = create_engine(url, connect_args=connect_args, echo=False)
    return engine


def init_db():
    """Create all tables. Safe to run multiple times."""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session."""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


# ============================================================================
# PRICING BAND HELPERS
# ============================================================================

def capture_pricing_band_from_sc(session, card_id, sc_data, band_date=None):
    """Capture today's pricing band from sportscardspro actor output.

    Args:
        session: SQLAlchemy session
        card_id: cards.id
        sc_data: dict from lookup_sportscardspro() (has prices_by_tier + sold_counts_by_grade)
        band_date: defaults to today

    Returns: PricingBand row (inserted or updated)
    """
    if sc_data is None:
        return None

    prices = sc_data.get('prices_by_tier') if isinstance(sc_data, dict) else None
    sold_counts = sc_data.get('sold_counts_by_grade') if isinstance(sc_data, dict) else None

    if not prices:
        return None

    if band_date is None:
        band_date = date_type.today()

    # Map sportscardspro tier keys to our pricing_bands columns
    # Actor returns prices_by_tier with these keys (verified Sept 15):
    #   ungraded, psa_7, psa_8, psa_9, psa_9_5, psa_10
    tier_to_col = {
        'ungraded': 'raw',
        'psa_7': 'psa_7',
        'psa_8': 'psa_8',
        'psa_9': 'psa_9',
        'psa_9_5': 'psa_9_5',
        'psa_10': 'psa_10',
        # Legacy keys (kept for backward compat)
        'used_price': 'raw',
        'complete_price': 'psa_7',
        'new_price': 'psa_8',
        'graded_price': 'psa_9',
        'box_only_price': 'psa_9_5',
        'manual_only_price': 'psa_10',
        'manual_only_price_v2': 'psa_10',
    }

    # Build per-tier data
    tier_data = {}
    for tier_key, col_prefix in tier_to_col.items():
        tier_info = prices.get(tier_key)
        if isinstance(tier_info, dict):
            tier_data[col_prefix] = {
                'low': tier_info.get('price_usd'),
                'high': tier_info.get('price_usd'),
                # Same price for low/high = midpoint from sportscardspro (their data is a single price per grade)
            }

    # Sold counts (volumes) per grade
    def get_volume(grade_prefix):
        """Map our column prefix (raw, psa_7, psa_10, etc) to sportscardspro sold count.

        sportscardspro keys are like 'PSA 10', 'BGS 10', 'Ungraded'
        Our prefixes are like 'psa_10', 'raw'
        """
        if not sold_counts:
            return 0
        for k, v in sold_counts.items():
            if not k:
                continue
            kl = str(k).lower().replace('.', '').replace(' ', '').replace('_', '')
            grade_norm = grade_prefix.lower().replace('_', '')
            if kl == grade_norm:
                return v if isinstance(v, int) else (v.get('total') if isinstance(v, dict) else 0)
            # Handle 'ungraded' = 'raw'
            if grade_norm == 'raw' and 'ungraded' in kl:
                return v if isinstance(v, int) else (v.get('total') if isinstance(v, dict) else 0)
        return 0

    # Look for existing row (insert-or-replace logic)
    existing = session.query(PricingBand).filter_by(
        card_id=card_id, band_date=band_date
    ).first()

    if existing:
        row = existing
    else:
        row = PricingBand(card_id=card_id, band_date=band_date)

    for col_prefix, tier in tier_data.items():
        setattr(row, f'{col_prefix}_low', tier['low'])
        setattr(row, f'{col_prefix}_high', tier['high'])
        # PSA actor returns single value per grade — if sportscardspro starts
        # returning range, we have low/high separation. Today: low==high.
        setattr(row, f'{col_prefix}_volume', get_volume(col_prefix))

    if 'raw' in tier_data and tier_data['raw'].get('low'):
        row.raw_median = (tier_data['raw']['low'] + tier_data['raw']['high']) / 2 if tier_data['raw']['high'] else tier_data['raw']['low']

    if not existing:
        session.add(row)

    session.commit()
    return row


def cleanup_old_pricing_bands(session, retention_days=30):
    """Delete pricing bands older than retention window. Run daily.

    Returns: number of rows deleted.
    """
    cutoff = date_type.today() - timedelta(days=retention_days)
    deleted = session.query(PricingBand).filter(
        PricingBand.band_date < cutoff
    ).delete()
    session.commit()
    return deleted


def get_30day_trend(session, card_id):
    """Get 30-day trend for a card.

    Returns:
        {
            'card_id': int,
            'days_with_data': int,
            'psa_10_median_30d_avg': float | None,
            'psa_10_high_30d_avg': float | None,
            'psa_10_volume_total': int,
            'raw_median_30d_avg': float | None,
            'direction': 'up' | 'down' | 'flat' | 'unknown'
        }
    """
    bands = PricingBand.get_30day_window(session, card_id)
    if not bands:
        return {'card_id': card_id, 'days_with_data': 0, 'direction': 'unknown'}

    import statistics
    psa_10_highs = [b.psa_10_high for b in bands if b.psa_10_high is not None]
    psa_10_vols = [b.psa_10_volume or 0 for b in bands]
    raw_medians = [b.raw_median for b in bands if b.raw_median is not None]

    psa_10_avg = statistics.mean(psa_10_highs) if psa_10_highs else None
    raw_avg = statistics.mean(raw_medians) if raw_medians else None
    vol_total = sum(psa_10_vols)

    # Direction: compare first half vs second half
    direction = 'unknown'
    if len(psa_10_highs) >= 4:
        mid = len(psa_10_highs) // 2
        first_half_avg = statistics.mean(psa_10_highs[:mid])
        second_half_avg = statistics.mean(psa_10_highs[mid:])
        if first_half_avg == 0:
            direction = 'flat'
        else:
            change = (second_half_avg - first_half_avg) / first_half_avg
            if change > 0.05:
                direction = 'up'
            elif change < -0.05:
                direction = 'down'
            else:
                direction = 'flat'

    return {
        'card_id': card_id,
        'days_with_data': len(bands),
        'psa_10_high_30d_avg': psa_10_avg,
        'psa_10_volume_total': vol_total,
        'raw_median_30d_avg': raw_avg,
        'direction': direction,
    }


# ============================================================================
# MIGRATION HELPERS
# ============================================================================

def migrate_sqlite_to_postgres(sqlite_path, postgres_url):
    """Migrate data from SQLite to Postgres. Takes ~5 minutes for small datasets.
    
    Usage:
        1. Set DATABASE_URL=postgresql://...
        2. Run: python -c "from db_models import migrate_sqlite_to_postgres; migrate_sqlite_to_postgres('card_scout.db', 'postgresql://...')"
        3. Update DATABASE_URL env var
        4. Restart bot
    """
    from sqlalchemy import create_engine as ce
    
    # Connect to source SQLite
    src_engine = ce(f'sqlite:///{sqlite_path}')
    # Connect to destination Postgres
    dst_engine = ce(postgres_url)
    
    # Create tables in destination
    Base.metadata.create_all(dst_engine)
    
    # Copy each table
    Session_src = sessionmaker(bind=src_engine)
    Session_dst = sessionmaker(bind=dst_engine)
    
    src = Session_src()
    dst = Session_dst()
    
    for model in [Customer, Card, Snapshot, RunHistory, PricingBand]:
        records = src.query(model).all()
        for r in records:
            # Detach from source session
            src.expunge(r)
            # Add to destination
            dst.merge(r)
        dst.commit()
        print(f"Migrated {len(records)} {model.__name__} rows")
    
    src.close()
    dst.close()
    print("Migration complete!")


if __name__ == '__main__':
    # Test: create the DB
    print("Initializing Card Scout database...")
    engine = init_db()
    print(f"✓ Tables created at {get_database_url()}")
    print(f"[OK] Models: {[m.__name__ for m in [Customer, Card, Snapshot, RunHistory, PricingBand]]}")
