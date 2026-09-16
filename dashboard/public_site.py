"""
Card Scout Public Website (Sept 16, 2026).

Founder: 'tell me about the web-hosting page'

Public-facing routes:
- /                    -> Landing page (marketing)
- /deals               -> Top 10 deals across platform (ad revenue)
- /pricing             -> 4-tier pricing page
- /health              -> Health check endpoint
- /sitemap.xml         -> SEO sitemap
- /robots.txt          -> SEO robots

Authentication-aware: if logged in, / shows "Go to dashboard" CTA.
"""

from flask import Blueprint, render_template_string, redirect, url_for, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from pathlib import Path
import os

# Use the same DB as dashboard
DB_PATH = Path(__file__).parent.parent / 'card_scout.db'
if os.environ.get('DATABASE_URL', '').startswith('sqlite:///'):
    DB_PATH = Path(os.environ['DATABASE_URL'].replace('sqlite:////', '/').replace('sqlite:///', ''))

engine = create_engine(f'sqlite:///{DB_PATH}')
db_session = scoped_session(sessionmaker(bind=engine))

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from db_models import Customer, Card, PricingBand  # noqa: E402

site_bp = Blueprint('site', __name__)


# ============================================================================
# PUBLIC LANDING PAGE
# ============================================================================

LANDING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card Scout — AI-Powered Card Deal Alerts</title>
<meta name="description" content="Get Discord alerts when your favorite cards drop below market. Sports cards, TCG, and more. AI finds the deals, you make the trade.">
<meta property="og:title" content="Card Scout — AI-Powered Card Deal Alerts">
<meta property="og:description" content="Get Discord alerts when your favorite cards drop below market.">
<meta property="og:type" content="website">
<link rel="canonical" href="https://cardscout.app/">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <nav>
    <a href="/" class="logo">Card Scout</a>
    <div class="nav-links">
      <a href="/deals">Top Deals</a>
      <a href="/pricing">Pricing</a>
      {% if logged_in %}
        <a href="/dashboard/{{ customer_id }}" class="cta">Dashboard</a>
      {% else %}
        <a href="/login" class="cta">Sign In</a>
      {% endif %}
    </div>
  </nav>
</header>

<main>
  <section class="hero">
    <h1>Find the deals.<br><span class="highlight">Skip the noise.</span></h1>
    <p class="hero-sub">Card Scout watches the market 24/7 and alerts you on Discord when your cards drop below typical asking prices.</p>
    <div class="hero-cta">
      <a href="/pricing" class="btn btn-primary">View Pricing</a>
      <a href="/deals" class="btn btn-secondary">See Top Deals</a>
    </div>
    <p class="hero-trust">Built for collectors, investors, and dealers. 4 simple tiers. No spam.</p>
  </section>

  <section class="how-it-works">
    <h2>How it works</h2>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h3>Add your cards</h3>
        <p>Search our database or paste an eBay / Sportscardspro URL. Each card you track counts as 1 toward your tier limit.</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h3>Set your tier</h3>
        <p>Casual, Standard, Dealer, or Pro. Higher tiers get more frequent updates and stronger filters.</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h3>Get Discord alerts</h3>
        <p>When a card drops below its 1-month median, you get a Discord alert with the deal link. No noise, no false positives.</p>
      </div>
    </div>
  </section>

  <section class="why-us">
    <h2>Why Card Scout</h2>
    <div class="features">
      <div class="feature">
        <h3>Real deals, not noise</h3>
        <p>Every alert is verified against the 1-month market median. No spam, no junk listings.</p>
      </div>
      <div class="feature">
        <h3>Multi-source data</h3>
        <p>eBay + Sportscardspro + PriceCharting + Card Ladder. We pull from every source so you don't miss anything.</p>
      </div>
      <div class="feature">
        <h3>Self-serve</h3>
        <p>Add or remove cards anytime from your dashboard. No waiting on us to make changes.</p>
      </div>
    </div>
  </section>

  <section class="cta-section">
    <h2>Ready to find deals?</h2>
    <p>Start with our free trial. 14 days, no credit card required.</p>
    <a href="/pricing" class="btn btn-primary btn-large">View Pricing</a>
  </section>
</main>

<footer>
  <p>&copy; 2026 Card Scout. Built by collectors, for collectors.</p>
</footer>
</body>
</html>
'''


@site_bp.route('/')
def landing():
    """Public landing page."""
    # Check if logged in
    customer_id = request.cookies.get('customer_id') or _get_logged_in_customer()
    logged_in = bool(customer_id)

    return render_template_string(
        LANDING_TEMPLATE,
        logged_in=logged_in,
        customer_id=customer_id if logged_in else None,
    )


def _get_logged_in_customer():
    """Check session for logged-in customer."""
    from flask import session
    return session.get('customer_id')


# ============================================================================
# TOP DEALS PAGE
# ============================================================================

DEALS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Top Card Deals — Card Scout</title>
<meta name="description" content="Live top deals on graded sports cards and TCG. AI-powered deal detection across eBay, Sportscardspro, and more.">
<meta property="og:title" content="Top Card Deals — Card Scout">
<meta property="og:description" content="Live top deals across all major card marketplaces.">
<link rel="canonical" href="https://cardscout.app/deals">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <nav>
    <a href="/" class="logo">Card Scout</a>
    <div class="nav-links">
      <a href="/deals">Top Deals</a>
      <a href="/pricing">Pricing</a>
      <a href="/" class="cta">Home</a>
    </div>
  </nav>
</header>

<main>
  <section class="page-header">
    <h1>Top 10 Deals</h1>
    <p class="page-sub">Live deals across all customers. Updated whenever the bot runs.</p>
  </section>

  <!-- Ad slot placeholder -->
  <div class="ad-slot ad-top">
    <small>Advertisement</small>
  </div>

  {% if deals %}
  <section class="deals-grid">
    {% for deal in deals %}
    <article class="deal-card">
      <div class="deal-header">
        <h3>{{ deal.card_name }}</h3>
        <span class="grade-badge">{{ deal.grade }}</span>
      </div>
      <div class="deal-price">
        <span class="price-now">${{ "%.2f"|format(deal.price) }}</span>
        {% if deal.market_price %}
        <span class="price-market">market: ${{ "%.2f"|format(deal.market_price) }}</span>
        <span class="discount">-{{ "%.0f"|format(deal.discount_pct) }}%</span>
        {% endif %}
      </div>
      {% if deal.url %}
      <a href="{{ deal.url }}" class="deal-link" target="_blank" rel="nofollow noopener">View Listing →</a>
      {% endif %}
    </article>
    {% endfor %}
  </section>
  {% else %}
  <section class="empty">
    <p>No deals found yet. Check back after the next bot run!</p>
    <p class="empty-detail">The bot typically runs daily. Once deals are detected, they'll appear here.</p>
  </section>
  {% endif %}

  <!-- Ad slot placeholder -->
  <div class="ad-slot ad-bottom">
    <small>Advertisement</small>
  </div>

  <section class="cta-section">
    <h2>Want alerts like these in your Discord?</h2>
    <a href="/pricing" class="btn btn-primary">View Pricing</a>
  </section>
</main>

<footer>
  <p>&copy; 2026 Card Scout. <a href="/">Home</a> · <a href="/pricing">Pricing</a></p>
</footer>
</body>
</html>
'''


@site_bp.route('/deals')
def deals():
    """Top 10 deals page — pulls from latest snapshot."""
    deals_data = _get_top_deals(limit=10)
    return render_template_string(DEALS_TEMPLATE, deals=deals_data)


def _get_top_deals(limit=10):
    """
    Get top deals across all customers.

    Schema note: PricingBand has per-grade columns (psa_7_low, psa_7_high, etc.)
    For V1: pull each grade's price + volume and compute lower-third threshold.
    Real z-score deal detection comes when Card Ladder ships (gets σ from sold).

    Future: z-score-based selection. For now: top 10 grades by lowest
    price (volume >= 1, sorted by median price ascending for "cheapest first").
    """
    try:
        # Get all bands (latest only — but V1 doesn't track multiple snapshots per day)
        bands = db_session.query(PricingBand).all()

        # Grade columns to check
        grade_cols = ['raw', 'psa_7', 'psa_8', 'psa_9', 'psa_9_5', 'psa_10']

        deals = []
        for band in bands:
            card = db_session.query(Card).filter_by(id=band.card_id).first()
            if not card:
                continue

            for grade in grade_cols:
                low = getattr(band, f'{grade}_low', None)
                high = getattr(band, f'{grade}_high', None)
                median = getattr(band, f'{grade}_median', None)
                volume = getattr(band, f'{grade}_volume', None)

                # Skip if no data
                if low is None or high is None or volume is None or volume < 1:
                    continue

                # Skip if no spread
                if low >= high:
                    continue

                # Lower-third threshold (founder's z-score framework v1)
                threshold = low + (high - low) / 3

                # For V1: list grades with real spread
                deals.append({
                    'card_name': card.search_query,
                    'card_id': card.id,
                    'grade': grade.upper().replace('_', ' '),
                    'price': low,
                    'market_price': median if median else (low + high) / 2,
                    'discount_pct': ((median - low) / median * 100) if median and median > 0 else 0,
                    'volume': volume,
                    'url': card.sportscardspro_url or card.psa_set_url or '#',
                    'threshold': threshold,
                })

        # Sort by biggest discount (best deals first)
        deals.sort(key=lambda d: d['discount_pct'], reverse=True)
        return deals[:limit]

    except Exception as e:
        # Log and return empty list (don't crash public site)
        print(f"Error loading top deals: {e}")
        return []


# ============================================================================
# PRICING PAGE
# ============================================================================

PRICING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing — Card Scout</title>
<meta name="description" content="4 simple tiers. Casual, Standard, Dealer, Pro. Pick the tier that matches your collecting style.">
<link rel="canonical" href="https://cardscout.app/pricing">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <nav>
    <a href="/" class="logo">Card Scout</a>
    <div class="nav-links">
      <a href="/deals">Top Deals</a>
      <a href="/pricing">Pricing</a>
      <a href="/" class="cta">Home</a>
    </div>
  </nav>
</header>

<main>
  <section class="page-header">
    <h1>Simple, transparent pricing</h1>
    <p class="page-sub">4 tiers. Cancel anytime. 14-day free trial.</p>
  </section>

  <section class="tiers">
    <div class="tier">
      <h3>Casual</h3>
      <p class="price">$15<span>/month</span></p>
      <ul>
        <li>3 cards</li>
        <li>1 refresh / month</li>
        <li>Discord alerts</li>
        <li>Self-serve dashboard</li>
      </ul>
      <p class="tier-best">Best for hobbyists starting out</p>
    </div>

    <div class="tier">
      <h3>Standard</h3>
      <p class="price">$30<span>/month</span></p>
      <ul>
        <li>6 cards</li>
        <li>4 refreshes / month (weekly)</li>
        <li>Discord alerts</li>
        <li>Stock-class ticker</li>
      </ul>
      <p class="tier-best">Best for active collectors</p>
    </div>

    <div class="tier tier-popular">
      <span class="popular-badge">Most Popular</span>
      <h3>Dealer</h3>
      <p class="price">$75<span>/month</span></p>
      <ul>
        <li>20 cards</li>
        <li>12 refreshes / month (3x/week)</li>
        <li>Discord alerts</li>
        <li>All features unlocked</li>
      </ul>
      <p class="tier-best">Best for power users and dealers</p>
    </div>

    <div class="tier">
      <h3>Pro</h3>
      <p class="price">$150<span>/month</span></p>
      <ul>
        <li>50 cards</li>
        <li>30 refreshes / month (daily)</li>
        <li>Discord alerts</li>
        <li>Custom thresholds</li>
      </ul>
      <p class="tier-best">Best for dealers with daily volume</p>
    </div>
  </section>

  <section class="faq">
    <h2>Common questions</h2>
    <details>
      <summary>What counts as a "card"?</summary>
      <p>Each card-grader combo counts as 1. So "Bo Jackson 1987 Topps PSA 10" and "Bo Jackson 1987 Topps PSA 9" are 2 cards.</p>
    </details>
    <details>
      <summary>How do refreshes work?</summary>
      <p>Each refresh checks current market prices against your cards. Higher refresh tiers catch deals faster but cost more in API fees.</p>
    </details>
    <details>
      <summary>What sources do you pull from?</summary>
      <p>eBay (live listings + sold), Sportscardspro, PriceCharting, Card Ladder. We deduplicate and outlier-trim automatically.</p>
    </details>
    <details>
      <summary>Can I cancel anytime?</summary>
      <p>Yes. Cancel from your dashboard. No contracts, no questions.</p>
    </details>
  </section>

  <section class="cta-section">
    <h2>Try Card Scout free for 14 days</h2>
    <p>No credit card required. Cancel anytime.</p>
    <a href="/login" class="btn btn-primary btn-large">Get Started</a>
  </section>
</main>

<footer>
  <p>&copy; 2026 Card Scout. <a href="/">Home</a> · <a href="/deals">Top Deals</a></p>
</footer>
</body>
</html>
'''


@site_bp.route('/pricing')
def pricing():
    """Pricing page."""
    return render_template_string(PRICING_TEMPLATE)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@site_bp.route('/health')
def health():
    """Health check endpoint for Render."""
    from sqlalchemy import text
    try:
        # Test DB connection
        db_session.execute(text('SELECT 1'))
        return Response('{"status": "healthy", "db": "ok"}', mimetype='application/json')
    except Exception as e:
        return Response(f'{{"status": "unhealthy", "error": "{str(e)}"}}', mimetype='application/json', status=500)


# ============================================================================
# SEO: SITEMAP + ROBOTS
# ============================================================================

SITEMAP_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://cardscout.app/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://cardscout.app/deals</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://cardscout.app/pricing</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
'''


ROBOTS_TEMPLATE = '''User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /login

Sitemap: https://cardscout.app/sitemap.xml
'''


@site_bp.route('/sitemap.xml')
def sitemap():
    """SEO sitemap."""
    return Response(SITEMAP_TEMPLATE, mimetype='application/xml')


@site_bp.route('/robots.txt')
def robots():
    """SEO robots.txt."""
    return Response(ROBOTS_TEMPLATE, mimetype='text/plain')
