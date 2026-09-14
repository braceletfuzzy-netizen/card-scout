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
    ForeignKey, Index, UniqueConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
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
    
    for model in [Customer, Card, Snapshot, RunHistory]:
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
    print(f"✓ Models: {[m.__name__ for m in [Customer, Card, Snapshot, RunHistory]]}")
