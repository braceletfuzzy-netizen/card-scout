#!/usr/bin/env python3
"""
Fuzzy Bracelet Discord Alert Bot v3.0 - SQLAlchemy + Trend Detection

Reads customer config from DB (not hardcoded).
Saves snapshots on each run.
Computes trend signals + Q bands.
Sends alerts with rich market data.

Usage:
  python discord_alert_bot.py --test-customer EMAIL  # Test mode for specific customer
  python discord_alert_bot.py --dry-run             # Check for deals but don't send
  python discord_alert_bot.py                       # Full run (production mode)

Database:
  SQLite (default): card_scout.db
  Postgres: set DATABASE_URL=postgresql://...
"""
import json
import sys
import argparse
import os
import requests
from pathlib import Path
from datetime import datetime
import time

# Add scripts dir to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))

from db_models import Customer, Card, Snapshot, RunHistory, PricingBand, init_db, get_session, capture_pricing_band_from_sc, cleanup_old_pricing_bands, get_30day_trend
from snapshot_system import (
    save_run_snapshot, get_card_snapshots, get_trend_emoji,
    compute_snapshot_stats
)
from psa_pop_lookup import lookup_psa_population, extract_pop_summary
from sportscardspro_lookup import lookup_sportscardspro, extract_sold_summary

# ============ CONFIG ============
# Apify token: loaded from env var (NEVER commit tokens to code)
APIFY_TOKEN = os.environ['APIFY_TOKEN']
ACTOR_ID = "AtQq66Qn8FB7aLq2l"  # eBay+Etsy scraper
BASE_URL = "https://api.apify.com/v2"

# Load Bright Data token
BD_TOKEN_PATH = Path(r"C:/Users/J/Documents/LLM/card-scout/config/bright-data-token.txt")
BD_TOKEN = BD_TOKEN_PATH.read_text().strip() if BD_TOKEN_PATH.exists() else None

# Bot appearance
BOT_NAME = "Card Scout"
BOT_AVATAR_PATH = "For You/Brand/card-scout-binoculars-logo.png"
BOT_TAGLINE = "Scouting card deals 24/7"
BOT_COLOR = 0x2C3E50  # Dark blue-gray

# Tier limits (matches DB tier column)
TIER_LIMITS = {
    "trial": 3,
    "lite": 3,
    "standard": 10,
    "pro": 30,
    "beta": 6,
    "beta_casual": 6,
    "beta_power": 20,
}

# First expanded term from each preset (avoids full preset expansion hang).
# Use ONE term from each preset in customSearchTerms instead of all 10.
# NOTE: These mirror the FIRST ebayTerms entry in the actor's PRESET_TERMS dict.
PRESET_FIRST_TERMS = {
    "cards-sports": "baseball card",     # cards-sports preset's first term
    "cards-graded": "PSA 10",            # cards-graded preset's first term
    "cards-pokemon": "pokemon card",     # cards-pokemon preset's first term
    "cards-tcg": "magic the gathering",  # cards-tcg preset's first term
    # Watch presets (for completeness)
    "watches-luxury": "rolex",
    "watches-japanese": "seiko",
    "watches-vintage": "vintage watch",
    "watches-dive": "dive watch",
    "watches-dress": "dress watch",
    "watches-sports": "chronograph",
    "watches-pilot": "pilot watch",
    "watches-field": "field watch",
}

print(f"✓ Card Scout bot configured (v3.0 - SQLAlchemy)")
print(f"  Logo: {BOT_AVATAR_PATH}")
print(f"  Name: {BOT_NAME}")
print(f"  DB: SQLite (default)")


# ============ APIFY RUNNER ============
def build_grade_search_suffix(card):
    """Build eBay search suffix based on grade filter checkboxes.

    Customer picks which grades matter. We narrow the eBay search to those.

    Tiers (6-bucket system):
        track_psa_10:         "PSA 10" / "BGS 9.5 Black Label"
        track_psa_9:          "PSA 9" / "BGS 9-9.5"
        track_psa_8:          "PSA 8" / "BGS 8.5-9"
        track_psa_lower:      "PSA 7" or below / BGS 8 or below
        track_raw:            "raw" / "ungraded" / "unslabbed"
        track_other_graders:  "SGC" / "CGC" / other grading companies

    Returns:
        String to append to eBay search, like " (PSA 9 OR raw)"
        Empty string if all False (or all True) - means no filter
    """
    # Build a list of grade keywords
    grade_terms = []

    if card.track_psa_10:
        grade_terms.append('(PSA 10 OR "BGS 9.5" OR "Black Label")')

    if card.track_psa_9:
        grade_terms.append('(PSA 9 OR "BGS 9")')

    if card.track_psa_8:
        grade_terms.append('(PSA 8 OR "BGS 8.5")')

    if card.track_psa_lower:
        grade_terms.append('(PSA 7 OR PSA 6 OR PSA 5 OR PSA 4 OR PSA 3 OR PSA 2 OR PSA 1 OR "BGS 8" OR lower)')

    if card.track_raw:
        grade_terms.append('(raw OR ungraded OR unslabbed OR "no grade")')

    if card.track_other_graders:
        grade_terms.append('(SGC OR CGC OR "other grader")')

    if not grade_terms:
        return ""  # No filter - all grades

    if len(grade_terms) == 6:
        return ""  # All checked = no filter needed (default behavior)

    # Combine with OR
    return " " + " OR ".join(grade_terms)


def build_search_query_for_card(card):
    """Build full eBay search query for a card, including grade filter.

    Args:
        card: Card model with search_query + grade checkboxes

    Returns:
        Full search string for eBay
    """
    base = card.search_query or ""
    grade_suffix = build_grade_search_suffix(card)
    return f"{base}{grade_suffix}"


def run_apify_search(search_query, preset="cards-sports", max_listings=15, include_sold=False):
    """Run the eBay+Etsy scraper and return results.

    NOTE: Preset expansion is broken (creates 8 BD queries that hang).
    Use empty presets + custom_search_terms for reliable single-query runs.

    Returns:
        dict with 'run_id', 'items', 'duration'
    """
    print(f"  [APIFY] Searching: {search_query} (preset: {preset}, include_sold: {include_sold})")

    # Use SMART approach: customSearchTerms for the exact query (1 query) PLUS
    # the FIRST term from the preset's expanded list (1 more query). This gives
    # us preset-matching coverage without triggering the full expansion hang.
    preset_first_term = ""
    if preset and preset in PRESET_FIRST_TERMS:
        preset_first_term = PRESET_FIRST_TERMS[preset]

    payload = {
        "smartSearch": "",  # Skip smart expansion (interp is single-term for proper nouns)
        "maxListingsPerQuery": max_listings,
        "marketplaces": ["ebay"],
        "brightDataToken": BD_TOKEN,
        "brightDataZone": "web_unlocker1",
        "presets": [],  # No preset expansion (hangs); rely on preset's top term below
        "customSearchTerms": [search_query] + ([preset_first_term] if preset_first_term else []),
        "includeSold": include_sold,
    }

    start_time = time.time()

    # Start run
    start_url = f"{BASE_URL}/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    resp = requests.post(start_url, json=payload, timeout=30)
    run_data = resp.json().get("data", {})
    run_id = run_data.get("id")
    dataset_id = run_data.get("defaultDatasetId")

    if not run_id:
        print(f"  [ERROR] Failed to start Apify run: {resp.text[:200]}")
        return None

    print(f"  [APIFY] Run started: {run_id}")

    # Poll for completion (max 5 min)
    for i in range(30):
        time.sleep(10)
        status_resp = requests.get(
            f"{BASE_URL}/actor-runs/{run_id}?token={APIFY_TOKEN}",
            timeout=15
        )
        status = status_resp.json().get("data", {}).get("status")
        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            break

    duration = time.time() - start_time

    if status != "SUCCEEDED":
        print(f"  [APIFY] Run failed: {status}")
        return None

    # Get items
    items_url = f"{BASE_URL}/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
    items = requests.get(items_url, timeout=30).json()
    print(f"  [APIFY] Found {len(items)} items ({duration:.0f}s)")

    return {
        'run_id': run_id,
        'items': items,
        'duration': duration,
    }


# ============ DEAL FINDER ============
def filter_matching_items(items, search_query):
    """Filter items that match the search query keywords."""
    keywords = [k.lower() for k in search_query.split() if len(k) > 2]
    matching = []
    for item in items:
        title = (item.get('title') or '').lower()
        if any(kw in title for kw in keywords):
            matching.append(item)
    return matching


def compute_summary(matching_items):
    """Compute market summary from matching items."""
    prices = [i['price_usd'] for i in matching_items if i.get('price_usd') is not None and i['price_usd'] > 0]
    if not prices:
        return None

    sorted_p = sorted(prices)
    n = len(sorted_p)

    def pct(p):
        idx = min(int(n * p), n - 1)
        return sorted_p[idx]

    return {
        'total_listings': len(matching_items),
        'median_price_usd': sorted_p[n // 2],
        'avg_price_usd': sum(prices) / len(prices),
        'min_price_usd': min(prices),
        'max_price_usd': max(prices),
        'q1_price_usd': pct(0.25),
        'q3_price_usd': pct(0.75),
    }


def classify_grade(item):
    """Classify a SCPro listing into a grade tier based on title text.

    Returns one of: 'PSA 10', 'PSA 9', 'BGS 9.5', 'CGC 10', 'raw', 'unknown'
    Falls back to 'unknown' if no clear signal.

    Sept 18: each grade tier is its own market, so we need to know
    which tier a listing is in to compare against the right CH FMV.
    """
    title = (item.get('title') or item.get('description') or '').lower()
    if not title:
        return 'unknown'

    # Order matters - check SGC/CGC/BGS BEFORE PSA (they have unique prefixes)
    if 'cgc 10' in title or 'cgc10' in title:
        return 'CGC 10'
    if 'sgc' in title:
        return 'sgc'  # Not in our 4 main grades - skip FMV alert
    if 'bgs 9.5' in title or 'bgs 9.5' in title or 'black label' in title:
        return 'BGS 9.5'
    if 'bgs' in title:
        return 'bgs_other'  # BGS but not 9.5
    if 'psa 10' in title or 'psa10' in title or 'gem mint' in title:
        return 'PSA 10'
    if 'psa 9' in title or 'psa9' in title:
        return 'PSA 9'
    if 'psa 8' in title or 'psa8' in title:
        return 'PSA 8'  # Mapped but no CH FMV - falls back to PSA 9
    if 'psa' in title:
        return 'unknown_graded'  # PSA but couldn't parse grade number
    if 'raw' in title or 'ungraded' in title or 'unslabbed' in title or 'no grade' in title:
        return 'raw'
    return 'unknown'


def find_deals(matching_items, summary, alert_type='below_median', ch_data=None):
    """Find items that match the alert criteria.

    Sept 18: extended to support 'below_fmv' alert_type which uses
    per-grade Card Hedger FMV as the threshold (not blended median).

    Args:
        matching_items: list of listing dicts from SCPro
        summary: SCPro summary stats (median, avg, q1, q3)
        alert_type: 'below_median' | 'below_q1' | 'below_q3' | 'below_avg' | 'below_fmv'
        ch_data: dict from fetch_card_hedger_data() with per-grade FMVs

    Returns:
        list of items that match the threshold
    """
    if not summary or not matching_items:
        return []

    # Per-grade FMV alert (Sept 18): alert when listing < CH FMV × 0.85 for that grade
    if alert_type == 'below_fmv' and ch_data:
        fmvs = ch_data.get('fmvs', {})
        if not fmvs:
            return []  # No FMV data, fall back gracefully

        # CLEAN DATA FIX #1 (Sept 18): Drop D-grade FMVs before alert logic.
        # D-grade = CH confidence <0.10 (essentially guessing).
        # Per Jonathan: 'CH FMV should be treated like an opinion rather than
        # a stated fact.' D-grade opinions are too unreliable to alert on.
        # Example: Derek Jeter PSA 9 = $775 while PSA 10 = $25 looks like a
        # CH mapping bug, not a real price relationship.
        clean_fmvs = {}
        dropped_grades = []
        for grade, fmv in fmvs.items():
            conf = fmv.get('confidence') or 0
            conf_grade = fmv.get('confidence_grade', '?')
            if conf_grade == 'D' or conf < 0.10:
                dropped_grades.append(f"{grade}(CH {conf_grade} {conf:.2f})")
                continue
            clean_fmvs[grade] = fmv
        if dropped_grades:
            print(f"  [CLEAN DATA] Dropped D-grade FMVs: {', '.join(dropped_grades)}")
        if not clean_fmvs:
            return []  # All FMVs were D-grade, no reliable data

        threshold_pct = 0.85  # Alert when listing is 15%+ below FMV

        deals = []
        for item in matching_items:
            price = item.get('price_usd')
            if not price:
                continue

            grade = classify_grade(item)
            # Map grade tier to CH FMV (use clean_fmvs only - D-grade dropped)
            # PSA 8 falls back to PSA 9 FMV (closest tier)
            # SGC and BGS-other tiers skip FMV alert (no FMV for them)
            grade_to_fmv = {
                'PSA 10': clean_fmvs.get('PSA 10', {}).get('price'),
                'PSA 9': clean_fmvs.get('PSA 9', {}).get('price'),
                'BGS 9.5': clean_fmvs.get('BGS 9.5', {}).get('price'),
                'CGC 10': clean_fmvs.get('CGC 10', {}).get('price'),
                'PSA 8': clean_fmvs.get('PSA 9', {}).get('price'),  # Fallback
                'unknown_graded': clean_fmvs.get('PSA 10', {}).get('price'),  # Default
                'unknown': clean_fmvs.get('PSA 10', {}).get('price'),  # Default
                'raw': None,  # No FMV for raw
                'sgc': None,  # No CH FMV for SGC
                'bgs_other': None,  # No CH FMV for BGS <9.5
            }
            fmv = grade_to_fmv.get(grade)
            if not fmv:
                continue  # Skip raw cards for FMV-based alerts

            threshold = fmv * threshold_pct
            if price < threshold:
                # Annotate item with grade + discount vs FMV
                item_with_meta = dict(item)
                item_with_meta['_classified_grade'] = grade
                item_with_meta['_ch_fmv'] = fmv
                item_with_meta['_discount_pct'] = (fmv - price) / fmv * 100
                deals.append(item_with_meta)
        return deals

    # Legacy blended-median alerts (unchanged)
    threshold = {
        'below_median': summary.get('median_price_usd'),
        'below_q1': summary.get('q1_price_usd'),
        'below_q3': summary.get('q3_price_usd'),
        'below_avg': summary.get('avg_price_usd'),
    }.get(alert_type)

    if not threshold:
        return []

    deals = [i for i in matching_items if i.get('price_usd') and i['price_usd'] < threshold]
    return deals


# ============ DISCORD MESSAGES ============
def format_deal_alert(search_query, summary, deals, snapshot, alert_type='below_median', pop_data=None, sold_items=None, sold_data=None, market_thin=False, ch_data=None, comps_data=None):
    """Format the Discord alert embed.

    Per ticker spec (card-scout-ticker-system-spec-2026-09-14.md):
    - SHOW per-grade market values, typical ranges
    - DO NOT calculate profit or recommend whether to buy
    - Customer decides based on per-grade ticker data

    Args:
        deals: list of below-median deal dicts (raw bot-style)
        sold_items: list of recent sold listings (optional)
        sold_data: sportscardspro extracted summary (legacy single-tier)
        pop_data: PSA pop data
        ch_data: Card Hedger FMV data (Sept 18: per-grade FMVs)
    """
    """Create a Discord embed with Q bands + per-grade ticker + trend signal."""
    if not deals:
        return None

    deals = sorted(deals, key=lambda x: x.get('price_usd', 0))

    # Sept 18: alert_type='below_fmv' shows FMV context
    if alert_type == 'below_fmv':
        threshold_label = "Market FMV (per-grade)"
        threshold_value = None  # Variable per grade
    else:
        threshold_label = {
            "below_median": "median",
            "below_q1": "Q1 (25th percentile)",
            "below_q3": "Q3 (75th percentile)",
            "below_avg": "average"
        }.get(alert_type, "market")

        threshold_value = {
            "below_median": summary.get('median_price_usd'),
            "below_q1": summary.get('q1_price_usd'),
            "below_q3": summary.get('q3_price_usd'),
            "below_avg": summary.get('avg_price_usd'),
        }.get(alert_type)

    # Trend signal emoji + label
    trend_emoji = "⏳" if not snapshot else get_trend_emoji(snapshot.trend_signal or 'INSUFFICIENT_DATA')
    trend_label = snapshot.trend_signal.replace('_', ' ') if snapshot and snapshot.trend_signal else "INSUFFICIENT DATA"

    embed = {
        "title": f"🎯 Deal Alert: {search_query[:80]}",
        "description": (
            (f"📊 **{len(deals)} active listings** — thin market snapshot\n"
             f"{trend_emoji} **Trend: {trend_label}**\n"
             f"\n⚠️ This is a thin market. Listed prices reflect individual sellers, not market consensus. "
             f"Use the per-grade ticker + 90% CI ranges as the market signal.")
            if market_thin else
            ((f"Found **{len(deals)}** listings below {threshold_label} (${threshold_value}) "
              f"\n{trend_emoji} **Trend: {trend_label}**")
             if alert_type != 'below_fmv' else
             (f"Found **{len(deals)}** listings below Market per-grade FMV (×0.85 threshold)\n"
              f"{trend_emoji} **Trend: {trend_label}**\n"
              f"_Sept 18: each grade tier is its own market — comparing to per-grade FMV not blended median._"))
        ),
        "color": BOT_COLOR,
        "fields": [],
        "footer": {"text": f"{BOT_NAME} - {BOT_TAGLINE}"},
        "timestamp": datetime.utcnow().isoformat()
    }

    # Sept 18: Add Card Hedger comps display (recent actual sales)
    if comps_data and comps_data.get('count_used'):
        low = comps_data['low']
        high = comps_data['high']
        median = comps_data['comp_price']
        count = comps_data['count_used']
        grade = comps_data.get('grade', 'PSA 10')
        embed["fields"].append({
            "name": f"📊 Recent actual sales ({grade}, last 10)",
            "value": (
                f"**Range:** ${low:,.0f} - ${high:,.0f}\n"
                f"**Median sale:** ${median:,.0f}\n"
                f"_Sample size: {count} recent comparable sales_"
            ),
            "inline": False
        })

    # Sept 18: Add per-grade FMV display if we have ch_data
    if ch_data and ch_data.get('fmvs'):
        fmvs = ch_data['fmvs']
        grade_lines = []
        for grade, fmv in fmvs.items():
            price = fmv.get('price')
            price_low = fmv.get('price_low')
            price_high = fmv.get('price_high')
            conf_grade = fmv.get('confidence_grade', '?')
            if price:
                # Sept 18: show range when available (Jonathan: FMV is opinion, show range not point)
                if price_low and price_high and (price_high - price_low) / price > 0.1:
                    grade_lines.append(f"**{grade}:** ${price_low:,.0f}-${price_high:,.0f} (Market opinion: ${price:,.0f}, {conf_grade})")
                else:
                    grade_lines.append(f"**{grade}:** ${price:,.0f} (Market opinion, {conf_grade})")
        if grade_lines:
            embed["fields"].append({
                "name": "💎 Per-grade price range",
                "value": '\n'.join(grade_lines),
                "inline": False
            })

    # V3 ALERT LAYOUT (Sept 16 — Jim + founder beta feedback):
    # Order: Trend → Per-grade → Stock-Class → Market Shape → Deals → Top listings
    # Jim: more spacing + bigger formatting
    # Founder: per-grade values at top (under trend), Market Shape under per-grade

    # 1. TREND — first dedicated field (move from description to field for readability)
    embed["fields"].append({
        "name": f"{trend_emoji} Trend Signal",
        "value": (
            f"**Current:** {trend_label}\n\n"
            "_Trend detection builds over multiple runs — more history = more accurate signal_"
        ),
        "inline": False
    })

    # Market Shape (Q bands) — MOVED to position 4 (after per-grade ticker)
    if False and summary:  # disable for now — moved below
        embed["fields"].append({
            "name": "📊 Market Shape (Q Bands)",
            "value": (
                f"**Q1** ${summary.get('q1_price_usd', 0):.2f} → "
                f"**Median** ${summary.get('median_price_usd', 0):.2f} → "
                f"**Q3** ${summary.get('q3_price_usd', 0):.2f}\n"
                f"Range: ${summary.get('min_price_usd', 0):.2f} - ${summary.get('max_price_usd', 0):.2f}"
            ),
            "inline": False
        })

    # PSA Population Data (if available)
    if pop_data:
        psa_10 = pop_data.get('psa_10_pop', 0)
        psa_9 = pop_data.get('psa_9_pop', 0)
        total = pop_data.get('total_pop', 0)
        subject = pop_data.get('subject', 'Unknown card')

        # Rarity scoring: how rare is PSA 10?
        if psa_10 == 0:
            rarity = "🔥 ULTRA RARE (0 PSA 10s)"
        elif psa_10 <= 5:
            rarity = f"💎 RARE ({psa_10} PSA 10s)"
        elif psa_10 <= 25:
            rarity = f"🪨 SCARCE ({psa_10} PSA 10s)"
        elif psa_10 <= 100:
            rarity = f"📊 COMMON ({psa_10} PSA 10s)"
        else:
            rarity = f"📦 ABUNDANT ({psa_10} PSA 10s)"

        embed["fields"].append({
            "name": "🎯 PSA Population (Scarcity)",
            "value": (
                f"**Card:** {subject}\n"
                f"**PSA 10:** {psa_10}  |  **PSA 9:** {psa_9}  |  **Total:** {total}\n"
                f"{rarity}"
            ),
            "inline": False
        })

    # Per-Grade Ticker (Bloomberg-style market value per grade)
    # Per ticker spec: SHOW the typical range, don't calculate profit
    if sold_data:
        try:
            from grade_range_calculator import build_per_grade_table
            from ticker_formatter import format_per_grade_ticker

            # Build per-grade table from sportscardspro raw data
            # We need the raw sc_data, but sold_data is already extracted.
            # If we have raw sc_data, prefer it (more fields like sales array).
            sc_raw = sold_data.get('_raw_data') if isinstance(sold_data, dict) else None

            if sc_raw:
                grade_table = build_per_grade_table(sc_raw)
            else:
                # Fall back to legacy single-tier sold_data
                grade_table = build_per_grade_table({'prices': [
                    {'tier': 'manual_only_price', 'label': 'PSA 10', 'price': sold_data.get('psa_10_price', 0)},
                    {'tier': 'graded_price', 'label': 'Grade 9', 'price': sold_data.get('psa_9_price', 0)},
                    {'tier': 'used_price', 'label': 'Ungraded', 'price': sold_data.get('raw_price', 0)},
                ], 'sold_counts': [], 'sales': []})

            ticker_text = format_per_grade_ticker(grade_table)
            # ADR-001 trend-aware: fetch 30-day averages from pricing_bands if available
            try:
                trend_session = get_session()
                ticker_text = format_per_grade_ticker(
                    grade_table, session=trend_session, card_id=card.id
                )
                trend_session.close()
            except Exception:
                pass  # Trend is optional — fall back to non-trend display
            embed["fields"].append({
                "name": "📊 Per-Grade Market Values (ticker)",
                "value": ticker_text,
                "inline": False
            })

            # V3 STOCK-CLASS HIERARCHY (Sept 16): show PSA pop as stock-class data
            # Founder's framing: PSA grades are like stock classes (10=A, 9=B, 8=C).
            # Graded cards are stock certificates. Pop data = outstanding shares.
            try:
                from ticker_formatter import format_stock_class_section
                stock_text = format_stock_class_section(card)
                if stock_text:
                    embed["fields"].append({
                        "name": "🎖️ Stock-Class Hierarchy",
                        "value": stock_text,
                        "inline": False
                    })
            except Exception:
                pass  # Non-fatal: skip if no pop data

            # V3: NEW — Market Shape (moved here per founder's spec)
            # Founder's layout: per-grade values → stock-class → Market Shape
            if summary:
                # Build CI-style display (Q1-Q3 with median split into thirds)
                q1 = summary.get('q1_price_usd', 0)
                median = summary.get('median_price_usd', 0)
                q3 = summary.get('q3_price_usd', 0)
                spread = q3 - q1
                lower_third = q1 + spread / 3
                upper_third = q1 + 2 * spread / 3
                embed["fields"].append({
                    "name": "📊 Market Shape (Q Bands + CI Thirds)",
                    "value": (
                        f"**Q1** ${q1:.2f} → "
                        f"**Median** ${median:.2f} → "
                        f"**Q3** ${q3:.2f}\n"
                        f"**Range:** ${summary.get('min_price_usd', 0):.2f} - ${summary.get('max_price_usd', 0):.2f}\n\n"
                        f"_Deal threshold (lower third):_ **${lower_third:.2f}**\n"
                        f"_Top third line:_ **${upper_third:.2f}**"
                    ),
                    "inline": False
                })

            # V3: Per-grade deals using deal_detector.py (Sept 16 beta feedback)
            # Founder's rule: deal = price < lower-third of CI band, where spread exists
            try:
                from deal_detector import detect_all_deals
                import re as re_mod

                # Build grade_breakdown from deals (group by grade parsed from title)
                grade_breakdown = {}
                for d in deals:
                    title = (d.get('title') or '').lower()
                    price = d.get('price_usd', 0)
                    if price <= 0:
                        continue

                    # Detect grade from title
                    if 'psa 10' in title or 'gem mint' in title:
                        tier = 'psa_10'
                        grade_label = 'PSA 10'
                    elif 'psa 9.5' in title:
                        tier = 'psa_9_5'
                        grade_label = 'PSA 9.5'
                    elif 'psa 9' in title:
                        tier = 'psa_9'
                        grade_label = 'PSA 9'
                    elif 'psa 8' in title:
                        tier = 'psa_8'
                        grade_label = 'PSA 8'
                    elif 'psa 7' in title:
                        tier = 'psa_7'
                        grade_label = 'PSA 7'
                    else:
                        tier = 'raw'
                        grade_label = 'Ungraded'

                    if tier not in grade_breakdown:
                        grade_breakdown[tier] = {'low': price, 'high': price, 'volume': 0, 'listings': []}
                    grade_breakdown[tier]['high'] = max(grade_breakdown[tier]['high'], price)
                    grade_breakdown[tier]['low'] = min(grade_breakdown[tier]['low'], price)
                    grade_breakdown[tier]['volume'] += 1
                    grade_breakdown[tier]['listings'].append(d)

                pricing_bands = {
                    tier: {
                        'low': data['low'],
                        'high': data['high'],
                        'volume': data['volume']
                    }
                    for tier, data in grade_breakdown.items()
                }
                listings_by_grade = {
                    tier: data['listings']
                    for tier, data in grade_breakdown.items()
                }

                if pricing_bands:
                    deals_results = detect_all_deals(pricing_bands, listings_by_grade)

                    # Show deals grouped by grade (only grades with spread)
                    deals_with_data = [d for d in deals_results if d['deals']]
                    if deals_with_data:
                        deals_text_lines = []
                        total_found = 0
                        for dr in deals_with_data:
                            total_found += dr.get('total_deals_found', len(dr['deals']))
                            deals_text_lines.append(
                                f"\n**{dr['grade']}** "
                                f"(spread ${dr['spread']:.0f}, {dr['spread_pct']:.0f}%, "
                                f"threshold ${dr['threshold']:.0f}):"
                            )
                            for d in dr['deals'][:3]:  # top 3 per grade
                                deals_text_lines.append(
                                    f"  • **${d['price']:.0f}** — "
                                    f"{d['discount_pct']:.0f}% below threshold — "
                                    f"[link]({d['url']})"
                                )
                        embed["fields"].append({
                            "name": f"🎯 Per-Grade Deals ({total_found} found)",
                            "value": "\n".join(deals_text_lines),
                            "inline": False
                        })
                    else:
                        # Show why no deals
                        no_deal_grades = [d for d in deals_results if d.get('no_deals_reason')]
                        if no_deal_grades:
                            reasons = "\n".join([
                                f"• **{d['grade']}:** {d['no_deals_reason']}"
                                for d in no_deal_grades[:3]
                            ])
                            embed["fields"].append({
                                "name": "🎯 Per-Grade Deals (none found)",
                                "value": (
                                    "_Per-grade deal detection (Sept 16 beta feedback)_\n\n"
                                    f"{reasons}\n\n"
                                    "_Where there's no spread, there's no deal._"
                                ),
                                "inline": False
                            })
            except Exception as e:
                print(f"  [DEAL] Error: {e}")
                pass  # Non-fatal: skip deal detection if errors
        except Exception as e:
            pass  # Non-fatal: skip per-grade ticker if data unavailable

    # Top listings — for thin markets, show raw listings (no "X% below" framing)
    if not market_thin:
        for i, deal in enumerate(deals[:3], 1):
            # Sept 18: handle below_fmv where each deal has its own _ch_fmv anchor
            if alert_type == 'below_fmv':
                deal_fmv = deal.get('_ch_fmv')
                deal_discount = deal.get('_discount_pct')
                classified = deal.get('_classified_grade', '?')
                if deal_discount is not None and deal_fmv:
                    deal_name = f"💰 ${deal.get('price_usd')} ({deal_discount:.0f}% below FMV ${deal_fmv:,.0f}) [{classified}]"
                elif deal_fmv:
                    deal_name = f"💰 ${deal.get('price_usd')} (FMV ${deal_fmv:,.0f}) [{classified}]"
                else:
                    deal_name = f"💰 ${deal.get('price_usd')} [{classified}]"
            elif threshold_value:
                savings = threshold_value - deal.get('price_usd', 0)
                savings_pct = (savings / threshold_value * 100)
                deal_name = f"💰 ${deal.get('price_usd')} ({savings_pct:.0f}% below {threshold_label})"
            else:
                deal_name = f"💰 ${deal.get('price_usd')}"

            if deal.get('sold_count'):
                demand_label = "🔥 HOT" if deal['sold_count'] > 50 else "📈 Active" if deal['sold_count'] > 20 else "Steady"
                deal_name += f"  {demand_label} ({deal['sold_count']} sold)"

            embed["fields"].append({
                "name": deal_name,
                "value": f"[{deal.get('title', 'N/A')[:80]}]({deal.get('url', '#')})",
                "inline": False
            })
    else:
        # Thin market: show top 3 raw listings (no % claim — we describe the market, trader decides)
        for i, deal in enumerate(deals[:3], 1):
            deal_name = f"📋 ${deal.get('price_usd')}"
            if deal.get('sold_count'):
                deal_name += f"  ({deal['sold_count']} sold)"

            embed["fields"].append({
                "name": deal_name,
                "value": f"[{deal.get('title', 'N/A')[:80]}]({deal.get('url', '#')})",
                "inline": False
            })

    # Recent Sold (if available) - shows the SELL side
    if sold_items and len(sold_items) > 0:
        # Sort by sold_date desc, take top 3
        sold_sorted = sorted(
            [s for s in sold_items if s.get('sold_date') or s.get('listing_type') == 'sold'],
            key=lambda x: x.get('sold_date') or '0000',
            reverse=True
        )[:3]

        if sold_sorted:
            sold_lines = []
            for s in sold_sorted:
                date_str = s.get('sold_date', 'recent')[:10] if s.get('sold_date') else 'recent'
                price = s.get('price_usd', 0)
                sold_lines.append(f"**${price}** {date_str}  [{s.get('title', '')[:50]}]({s.get('url', '#')})")

            embed["fields"].append({
                "name": f"💵 Recent Sold ({len(sold_sorted)})",
                "value": "\n".join(sold_lines),
                "inline": False
            })

            # Calculate buy/sell spread
            if deals and len(deals) > 0:
                cheapest_buy = min(d.get('price_usd', 0) for d in deals)
                highest_sold = max(s.get('price_usd', 0) for s in sold_sorted)
                if cheapest_buy > 0 and highest_sold > 0:
                    spread = highest_sold - cheapest_buy
                    spread_pct = (spread / highest_sold) * 100
                    embed["fields"].append({
                        "name": "💹 Buy/Sell Spread",
                        "value": f"Buy ${cheapest_buy} → Sold ${highest_sold} = **${spread} spread ({spread_pct:.0f}%)**",
                        "inline": False
                    })

    # Trend history — REMOVED (now shown at top in #1 field)
    # Old logic duplicated the trend field, removed in V3 alert layout (Sept 16)

    return {
        "embeds": [embed],
        "username": BOT_NAME,
        # Note: Don't override avatar_url - we set the avatar on the webhook itself
        # via PATCH /webhooks/{id}/{token} with base64 image data
    }


def send_discord_webhook(webhook_url, message_data):
    """POST message to Discord webhook."""
    if not webhook_url:
        return False

    try:
        resp = requests.post(webhook_url, json=message_data, timeout=10)
        if resp.status_code in [200, 204]:
            print(f"  [DISCORD] ✅ Alert sent successfully")
            return True
        else:
            print(f"  [DISCORD] ❌ Failed: {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  [DISCORD] ❌ Error: {e}")
        return False


# ============ MAIN LOGIC ============
def process_customer_from_db(customer, dry_run=False):
    """Process one customer from the DB."""
    print(f"\n{'='*70}")
    print(f"Processing: {customer.customer_id} ({customer.email or 'no email'})")
    print(f"{'='*70}")

    # Get customer's enabled cards
    session = get_session()
    cards = session.query(Card).filter_by(
        customer_id=customer.id,
        enabled=True
    ).all()
    session.close()

    # Tier enforcement
    max_cards = TIER_LIMITS.get(customer.tier, 6)
    if len(cards) > max_cards:
        print(f"  [LIMIT] {customer.tier} tier allows {max_cards} cards, has {len(cards)}")
        print(f"  Truncating to first {max_cards}")
        cards = cards[:max_cards]

    if not customer.discord_webhook and not dry_run:
        print(f"  [SKIP] No Discord webhook configured")
        return

    if customer.subscription_status not in ['active', 'trial']:
        print(f"  [SKIP] Subscription: {customer.subscription_status}")
        return

    if not cards:
        print(f"  [SKIP] No enabled cards")
        return

    alerts_sent = 0

    for card in cards:
        print(f"\n  Checking: {card.search_query}")

        # Run Apify search (active listings)
        # Use base search_query (not full_search_query with grade filter) —
        # grade filtering is applied at the MATCHING stage, not the SEARCH stage.
        # See run_apify_search() for why: eBay's parser doesn't handle long OR queries well.
        result = run_apify_search(
            card.search_query,
            preset=card.preset,
            max_listings=card.max_listings,
            include_sold=card.include_sold,
        )

        if not result:
            continue

        items = result['items']

        # NOTE: eBay sold scraping via includeSold=True is BROKEN — see actor log
        # "0 bytes" returned, hangs 200s. Per Sept 14 handoff
        # (For You/Plans/hugo-handoff-includesold-broken-2026-09-14.md), we use
        # Sportscardspro instead (already wired below via `sold_data`).
        # Sold section in alert renders from sportscardspro's per-grade prices.
        sold_items = []

        # Filter to matching items
        matching = filter_matching_items(items, card.search_query)

        if not matching:
            print(f"  [NO MATCHES] No items match '{card.search_query}'")
            continue

        # V2 grade-tiered listing quality filter (Sept 15)
        # Skip junk listings ($1 BIN, bulk lots, no watchers). Skip entirely
        # if market_thin (every listing is signal).
        try:
            from listing_quality import filter_listings_by_quality
            grade_tier = card.alert_type or 'raw'
            quality_result = filter_listings_by_quality(
                matching,
                grade_tier=grade_tier,
                thin_market=bool(getattr(card, 'market_thin', 0)),
            )
            dropped_count = len(quality_result['dropped'])
            if dropped_count > 0:
                print(f"  [V2 FILTER] Dropped {dropped_count}/{len(matching)} low-quality listings")
            matching = quality_result['kept']
        except Exception as e:
            print(f"  [V2 FILTER] Skipped (error: {e})")
            # Continue with all matching items if filter fails

        # Card Hedger dual-source fetch (Sept 17 evening)
        # Run Card Hedger in parallel with SCPro for data comparison.
        # Logs discrepancies to /data/card_hedger_vs_scpro.log.
        # Sept 18: extended to fetch per-grade FMVs (PSA 10, PSA 9, BGS 9.5, CGC 10)
        # ch_data is used downstream for per-grade alert logic.
        ch_data = None  # Initialize so it's accessible after try block
        try:
            from cardhedger_alert_integration import fetch_card_hedger_data, log_comparison
            ch_data = fetch_card_hedger_data(card)
            if ch_data and ch_data.get('median_price'):
                ch_price = ch_data['median_price']
                # Build SCPro stats for comparison
                from snapshot_system import compute_snapshot_stats
                scpro_stats = compute_snapshot_stats(matching)
                log_comparison(card, ch_data, scpro_stats)
                # Show per-grade FMV summary
                fmvs = ch_data.get('fmvs', {})
                grade_summary = ', '.join(
                    f'{g} ${f["price"]:,.0f}'
                    for g, f in fmvs.items()
                    if f.get('price')
                )
                print(f"  [CARD HEDGER] ${ch_price:,.2f} (overall grade {ch_data.get('card_hedger_grade', '?')})")
                if grade_summary:
                    print(f"  [CARD HEDGER FMVs] {grade_summary}")
            else:
                print(f"  [CARD HEDGER] No data (rate limit or no match)")
        except Exception as e:
            print(f"  [CARD HEDGER] Skipped (error: {type(e).__name__}: {e})")

        # Card Hedger comps (recent sold sales) - Sept 18
        # Until eBay Browse API is approved, this is our sold-data source.
        comps_data = None
        try:
            from cardhedger_comps import fetch_card_hedger_comps
            comps_data = fetch_card_hedger_comps(card, grade='PSA 10', count=10)
            if comps_data and comps_data.get('count_used'):
                print(f"  [CARD HEDGER COMPS] PSA 10 sales: ${comps_data['low']:,.0f}-${comps_data['high']:,.0f} (n={comps_data['count_used']}, median ${comps_data['comp_price']:,.0f})")
            else:
                print(f"  [CARD HEDGER COMPS] No sold data for PSA 10")
        except Exception as e:
            print(f"  [CARD HEDGER COMPS] Skipped (error: {type(e).__name__}: {e})")

        # Save snapshot (triggers trend detection)
        print(f"  [SNAPSHOT] Saving {len(matching)} matching items")
        trend = save_run_snapshot(card.id, matching)
        print(f"  [TREND] {trend} {get_trend_emoji(trend)}")

        # Compute summary + find deals
        summary = compute_summary(matching)
        # Sept 18: pass ch_data to enable per-grade FMV-based deal detection
        deals = find_deals(matching, summary, card.alert_type, ch_data=ch_data)

        if not deals:
            print(f"  [NO DEALS] No qualifying deals")
            continue

        # Get current snapshot for trend display
        session = get_session()
        current_snapshot = session.query(Snapshot).filter_by(
            card_id=card.id, window='current'
        ).first()
        session.close()

        # Optional: PSA population lookup (if include_pop flag set)
        pop_data = None
        if card.include_pop:
            psa_set_url = card.psa_set_url
            if not psa_set_url:
                print(f"  [POP] No psa_set_url set for card {card.id}, skipping pop lookup")
            else:
                print(f"  [POP] Looking up PSA population for {card.search_query[:30]}...")
                try:
                    items = lookup_psa_population(psa_set_url, max_results=500, max_wait_sec=300)
                    if items:
                        # Hugo's actor schema: each item has 'name', 'psa_10_pop', 'psa_9_pop' (in grade_breakdown), 'total_pop'
                        keywords = [k for k in card.search_query.split() if len(k) > 2][:3]
                        pop_data = None
                        for item in items:
                            name = (item.get('name') or '').lower()
                            # Skip the set-total row (it has 'is_set_total': true)
                            if item.get('is_set_total'):
                                continue
                            if all(kw.lower() in name for kw in keywords):
                                pop_data = {
                                    'subject': item.get('name'),
                                    'card_no': item.get('card_no'),
                                    'psa_10_pop': item.get('psa_10_pop', 0),
                                    'psa_9_pop': item.get('grade_breakdown', {}).get('9', 0),
                                    'total_pop': item.get('total_pop', 0),
                                }
                                break
                        if not pop_data and items:
                            # Fall back to first non-set-total row
                            for first in items:
                                if not first.get('is_set_total') and not first.get('_diagnostic') and not first.get('_error'):
                                    pop_data = {
                                        'subject': first.get('name'),
                                        'card_no': first.get('card_no'),
                                        'psa_10_pop': first.get('psa_10_pop', 0),
                                        'psa_9_pop': first.get('grade_breakdown', {}).get('9', 0),
                                        'total_pop': first.get('total_pop', 0),
                                    }
                                    break
                        if pop_data:
                            print(f"  [POP] ✓ Found: {pop_data.get('subject')} — PSA 10 = {pop_data['psa_10_pop']}, total = {pop_data['total_pop']}")
                        else:
                            print(f"  [POP] No matching card in set (got {len(items)} items)")
                except Exception as e:
                    print(f"  [POP] Lookup failed: {e}")

        # Optional: Sportscardspro sold data lookup (replaces unreliable eBay sold)
        sold_data = None
        sportscardspro_url = getattr(card, 'sportscardspro_url', None)
        if sportscardspro_url:
            print(f"  [SCPRO] Looking up sold data for {card.search_query[:30]}...")
            try:
                sc_data = lookup_sportscardspro(sportscardspro_url, max_sales=10, max_wait_sec=60)
                if sc_data:
                    sold_data = extract_sold_summary(sc_data)
                    # Stash raw data for ticker formatter (per-grade table needs prices[] + sales[])
                    if sold_data:
                        sold_data['_raw_data'] = sc_data
                    if sold_data and sold_data.get('psa_10_price'):
                        print(f"  [SCPRO] ✓ PSA 10 ref: ${sold_data['psa_10_price']:.2f} ({sold_data.get('psa_10_sold_30d', '?')} sold)")
                    else:
                        print(f"  [SCPRO] Got data but no PSA 10 price")

                    # Capture today's pricing band for 30-day history (ADR-001)
                    try:
                        pb_session = get_session()
                        capture_pricing_band_from_sc(pb_session, card.id, sc_data)
                        pb_session.close()
                        print(f"  [PBAND] Captured pricing band for card {card.id}")
                    except Exception as pb_err:
                        print(f"  [PBAND] Capture skipped: {pb_err}")

                else:
                    print(f"  [SCPRO] Lookup returned no data")
            except Exception as e:
                print(f"  [SCPRO] Lookup failed: {e}")

        # Format alert
        message = format_deal_alert(
            card.search_query,
            summary,
            deals,
            current_snapshot,
            card.alert_type,
            pop_data=pop_data,
            sold_items=sold_items if sold_items else None,
            sold_data=sold_data,
            market_thin=bool(getattr(card, 'market_thin', 0)),
            ch_data=ch_data,  # Sept 18: pass for per-grade FMV display
            comps_data=comps_data,  # Sept 18: pass for sold-data display
        )

        if not message:
            continue

        if dry_run:
            print(f"  [DRY RUN] Would send Discord alert with {len(deals)} deals")
            print(f"    Sample: ${deals[0].get('price_usd')} - {deals[0].get('title', '')[:60]}")
            continue

        # Send to Discord
        if send_discord_webhook(customer.discord_webhook, message):
            alerts_sent += 1

        # Log run
        session = get_session()
        run_record = RunHistory(
            customer_id=customer.id,
            card_id=card.id,
            run_at=datetime.utcnow(),
            apify_run_id=result.get('run_id'),
            duration_seconds=result.get('duration'),
            total_listings=len(items),
            matching_items=len(matching),
            deals_found=len(deals),
            alert_sent=True,
        )
        session.add(run_record)
        session.commit()
        session.close()

        # Rate limit protection
        time.sleep(2)

    print(f"\n  [DONE] {alerts_sent} alerts sent to {customer.customer_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-customer', help='Process specific customer_id only')
    parser.add_argument('--dry-run', action='store_true', help='Check for deals but do not send')
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"FUZZY BRACELET DISCORD ALERT BOT v3.0 (DB-backed) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # Initialize DB
    init_db()

    # Cleanup old pricing bands (ADR-001: TTL=30d)
    # Idempotent — safe to run every bot startup
    try:
        cleanup_session = get_session()
        deleted = cleanup_old_pricing_bands(cleanup_session, retention_days=30)
        if deleted > 0:
            print(f"[PBAND] Cleaned up {deleted} bands older than 30 days")
        cleanup_session.close()
    except Exception as e:
        print(f"[PBAND] Cleanup skipped: {e}")

    # Get customers from DB
    session = get_session()

    if args.test_customer:
        customers = session.query(Customer).filter_by(customer_id=args.test_customer).all()
    else:
        # Get all active customers
        customers = session.query(Customer).filter(
            Customer.subscription_status.in_(['active', 'trial'])
        ).all()

    session.close()

    if not customers:
        print(f"No customers found.")
        return

    for customer in customers:
        process_customer_from_db(customer, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
