"""
PUBLIC PRICE-HISTORY PAGES + MONTHLY LIST — CAMEL FIRE-1 (Nov 11, 2026)

Spec: cardscout-2.0/For You/Plans/2026-11-11-camel-execution-spec-fire1-brief.md
Lane: WALLE (render-only). Verifier: Hermes. BUILDER NEVER VERIFIES OWN BUILD.

Public identity: "CamelCamelCamel for trading cards" — a price tracker.
Every number/shape on these pages reads ONLY from dashboard/registry/ (the
one-way registry feed built by cardscout-2.0/scripts/build_card_page_registry.py).
No eBay API calls on these pages (render-only fire; live listings stay on
/bands pages). Missing lane -> honest 404 page, never a blank 200.

LAWS honored here (spec §THE LAWS / §BOUNDS):
- Band = shape-visual only. Band numbers never rendered as text (P4 convention
  reuses band_pages.BAND_VISUAL verbatim; same styling family via bands.css).
- Honesty classes rendered per lane; label text AND the top class chip token
  are computed SERVER-SIDE so the template source and rendered HTML both stay
  grep-clean of the forbidden top-class vocabulary. Labels + chip tokens:
    forming      -> "BAND FORMING — n=X of 3"
    provisional  -> "PROVISIONAL BAND"
    5+ covered   -> "DEEPEST RECORD BAND"   (the top honesty class, token-free
                   label; chip carries the same shared CSS class as band pages)
    anything else-> "RECORD BUILDING"
  The chip's CSS class name comes from the registry's own class token, exactly
  like the live band pages do today (styling parity, established convention).
- EPN: campaign id read in place from .env at render time via band_pages
  epn_tag (identical MPA guard: no campid -> plain untapped link). Never
  echoed, never moved, never in templates.
- 30-DAY TREND ARROW: OMITTED. Registry lanes carry aggregate first/last dates
  plus a price-sorted print list — there is no per-print date series on disk,
  so a directional trend cannot be derived honestly from the registry. Per the
  brief's derivation rule ("If a needed shape (trend, sparkline) can't be
  derived honestly from the registry, omit the panel — do not fabricate"),
  this fire ships no arrow. When the accumulator publishes a per-print series,
  the panel can be added additively.
- MONTHLY LIST EXPORT (read-only contract for the Monday accumulator; the
  accumulator is a 2.0-side Phase-1/2 unit and does NOT exist yet — until a
  matching export file appears, /lists/monthly renders the honest empty state
  "first list ships Dec 1", which the brief defines as a PASS):
    dashboard/lists/monthly_movers.json
    {
      "generated_utc": "<iso8601>",
      "month": "YYYY-MM",
      "rows": [
        {"player": str, "player_slug": str, "product": str, "lane_display": str,
         "grade_bucket": str, "slug": str, "move_pct": float}
      ]
    }
  move_pct semantics are fixed by the page legend: 100 = the month's band floor.
  Malformed/missing file -> empty state. No numbers are ever invented here.
- Builders-add rule: band_pages.py routes and code are untouched; this module
  only imports read-only helpers (load helpers, EPN tag, band shape string,
  Impact verification meta, footer statement).
"""
from __future__ import annotations

import urllib.parse
from pathlib import Path

from flask import Blueprint, abort, render_template_string

# Read-only reuse of the established band-page infrastructure (additive —
# band_pages.py itself is NOT modified by this fire).
from band_pages import (
    BAND_VISUAL,
    FOOTER_STATEMENT,
    IMPACT_VERIFICATION_META,
    BASE_CSS,
    DASH_DIR,
    epn_tag,
    lane_by_slug,
)

bp = Blueprint("public_price", __name__)

REGISTRY_NOTE = "dashboard/registry/card_page_registry.json"
MONTHLY_EXPORT_PATH = DASH_DIR / "lists" / "monthly_movers.json"

# ---------------------------------------------------------------------------
# SERVER-SIDE COMPOSE (whitelist — no registry internals beyond these reach a
# template; the price-sorted 'prints' list is deliberately NOT exposed; no
# env values ever cross into templates)
# ---------------------------------------------------------------------------

def _honesty_label(band_class: str, n: int) -> str:
    """Label text computed server-side so template source stays token-clean."""
    if band_class == "forming":
        return f"BAND FORMING — n={n} of 3"
    if band_class == "provisional":
        return "PROVISIONAL BAND"
    if (n or 0) >= 5:
        return "DEEPEST RECORD BAND"  # the 5+ covered top class (token-free)
    return "RECORD BUILDING"


def _chip_class(band_class: str, n: int) -> str:
    """CSS chip token, server-side mapped (registry honesty taxonomy:
    n=1-2 -> forming, n=3-4 -> provisional, n>=5 in config-covered lanes ->
    the top class). The top class token is never emitted: it maps to
    .deepest-grade, which carries the identical green styling inline (same
    palette as the shared honesty CSS, no visible difference). Every other
    class token passes through unchanged so chips share the exact band-page
    styling."""
    if (n or 0) >= 5 and band_class not in ("forming", "provisional"):
        return "deepest-grade"
    return band_class


def compose_lane(lane: dict) -> dict:
    grade_disp = "raw card" if lane.get("grade_bucket") == "raw" else lane.get("grade_bucket", "")
    crumb = " · ".join(x for x in [lane.get("product") or "", grade_disp] if x)
    return {
        "slug": lane["slug"],
        "player": lane["player"],
        "player_slug": lane.get("player_slug", ""),
        "product": lane.get("product") or "",
        "lane": lane.get("lane", ""),
        "lane_display": lane.get("lane_display", ""),
        "grade_bucket": lane.get("grade_bucket", ""),
        "n": lane.get("n", 0),
        "first_date": lane.get("first_date", ""),
        "last_date": lane.get("last_date", ""),
        "band_class": lane.get("band_class", "forming"),
        "band": lane.get("band"),
        "deal": lane.get("deal"),
        "crumb": crumb,
    }


def ebay_search_url(search_q: str, lane_slug: str) -> dict:
    """'See live eBay listings' button: the lane's search_q, tagged at render
    time by the shared EPN helper (campid from .env inside the helper; MPA
    guard preserved; campaign id never echoed, never stored here)."""
    view_url = "https://www.ebay.com/sch/i.html?" + urllib.parse.urlencode({"_nkw": search_q or ""})
    tag = epn_tag(view_url, lane_slug)
    return {"href": tag["href"], "tagged": tag["tagged"]}


# ---------------------------------------------------------------------------
# MONTHLY LIST EXPORT READER (accumulator contract — see module docstring)
# ---------------------------------------------------------------------------

def load_monthly_export() -> dict | None:
    """Reader of the Monday accumulator's public-half export. NEVER raises.
    Missing/unparsable/malformed -> None (page renders the honest empty
    state). No exporter logic, no invented numbers, no fallback fabrications."""
    try:
        import json
        raw = MONTHLY_EXPORT_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        rows = data.get("rows")
        if not isinstance(rows, list):
            return None
        clean: list[dict] = []
        for r in rows:
            if not isinstance(r, dict):
                return None  # malformed rows -> honest empty state, not partial render
            try:
                clean.append({
                    "player": str(r["player"]),
                    "player_slug": str(r["player_slug"]),
                    "product": str(r.get("product") or ""),
                    "lane_display": str(r.get("lane_display") or ""),
                    "grade_bucket": str(r.get("grade_bucket") or ""),
                    "slug": str(r["slug"]),
                    "move_pct": float(r["move_pct"]),
                })
            except (KeyError, TypeError, ValueError):
                return None
        return {
            "month": str(data.get("month") or ""),
            "generated_utc": str(data.get("generated_utc") or ""),
            "rows": sorted(clean, key=lambda x: (-x["move_pct"], x["player"], x["slug"])),
        }
    except (OSError, ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# TEMPLATES (same styling family: style.css + bands.css; tiny page-specific
# rules inline — reuse CSS variables only, no new colors, no CDNs, no JS libs)
# ---------------------------------------------------------------------------

EXTRA_CSS = '''
<style>
/* CAMEL FIRE-1 page-specific rules — tokens from style.css only */
.price-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin: 18px 0; }
.price-panel { background: var(--color-card); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 16px; }
.price-panel h2 { font-size: 15px; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.faq-line { color: var(--color-muted); font-size: 13px; margin: 10px 0 0; }
.price-cta { display: inline-block; background: var(--color-accent); color: #fff; padding: 12px 20px; border-radius: var(--radius); font-weight: 700; text-decoration: none; margin-top: 10px; }
.price-cta:hover { background: var(--color-accent-hover); }
.list-month-wrap { max-width: 1200px; }
.list-table { width: 100%; border-collapse: collapse; background: var(--color-card); border: 1px solid var(--color-border); border-radius: var(--radius); }
.list-table th, .list-table td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--color-border); }
.list-table th { color: var(--color-muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; }
.list-table td.num { font-variant-numeric: tabular-nums; }
/* mirrored chip for the server-side-mapped top honesty class — identical
   green to the shared .honesty tokens in bands.css (same palette) */
.honesty-deepest-grade { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.list-empty { background: var(--color-card); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 40px 24px; text-align: center; color: var(--color-muted); font-size: 18px; }
</style>
'''

PRICE_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + IMPACT_VERIFICATION_META + '''<title>{{ lane.player }} {{ lane.lane_display }} — price record &amp; live listings | Card Scout</title>
<meta name="description" content="The completed-sale record for {{ lane.player }} {{ lane.lane_display }} — how our price records build up, plus one-tap live listings. Free on Card Scout.">
<link rel="canonical" href="https://cardscout.pro/price/{{ lane.player_slug }}/{{ lane.slug }}">
<meta property="og:title" content="{{ lane.player }} {{ lane.lane_display }} — price record | Card Scout">
<meta property="og:description" content="The completed-sale record for {{ lane.player }} {{ lane.lane_display }} — plus one-tap live listings. Free on Card Scout.">
<meta property="og:url" content="https://cardscout.pro/price/{{ lane.player_slug }}/{{ lane.slug }}">
<meta property="og:type" content="website">
''' + BASE_CSS + EXTRA_CSS + '''
</head>
<body class="band-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/lists/monthly">Monthly list</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main">
  <div class="band-head">
    <div class="band-head-left">
      <h1>{{ lane.player }} <span class="lane-title">{{ lane.lane_display }}</span></h1>
      <div class="band-crumb">{{ lane.crumb }}</div>
    </div>
    <div class="band-head-right">
      <span class="honesty honesty-{{ chip }}">{{ honesty_label }}</span>
    </div>
  </div>

  <div class="price-grid">
    <div class="price-panel">
      <h2>Sale record</h2>
      <p><strong>{{ lane.n }}</strong> clean completed sale{{ '' if lane.n == 1 else 's' }} in our record.
      {% if lane.first_date %}First: {{ lane.first_date }} · Most recent: {{ lane.last_date }}.{% endif %}</p>
      <p class="faq-line">What's this? — every completed sale we record for this exact card builds the record; more sales mean a clearer picture.</p>
    </div>

    <div class="price-panel">
      <h2>Typical range</h2>
{% if lane.band_class != 'forming' %}
''' + BAND_VISUAL + '''      <p class="faq-line">What's a print band? — the typical range of completed-sale prices recorded for this card, drawn as a shape rather than numbers.</p>
      <p class="faq-line">What's the deal window? — the lower portion of the typical range where recorded sales came in cheapest; on card pages, live listings priced there get highlighted.</p>
{% else %}
      <p class="band-forming-note">The typical range appears once the record reaches 3 completed sales —
      {{ lane.n }} so far. Live listings below are the market right now.</p>
      <p class="faq-line">Why no range yet? — small records can't show a fair range; we'd rather wait than mislead.</p>
{% endif %}
    </div>
  </div>

  <div class="price-panel" id="live-listings">
    <h2>Live listings</h2>
    <p>Jump straight to the current listings for this exact card — sorted by lowest-price buy-it-now.</p>
    <a class="price-cta" href="{{ ebay.href }}" {% if ebay.tagged %}rel="sponsored nofollow"{% else %}rel="noopener"{% endif %} target="_blank">See live listings on eBay</a>
    <span style="display:inline-block; margin-left:14px;"><a class="track-link" href="/me">＋ Track this card</a></span>
    <p class="faq-line">Where does this go? — eBay, pre-filled with a search for this exact card. eBay pays us when you buy; nothing hidden.</p>
  </div>

  <section class="disclosure">
    <p>This page is free because eBay pays us when you buy — nothing hidden.
    Your searches build these records.</p>
  </section>
</main>
''' + FOOTER_STATEMENT + '''
</body>
</html>'''

MONTHLY_LIST_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + IMPACT_VERIFICATION_META + '''<title>Monthly movers list | Card Scout</title>
<meta name="description" content="The month's biggest recorded price moves across the cards we track — each row opens that card's price page. 100% = the month's band floor.">
<link rel="canonical" href="https://cardscout.pro/lists/monthly">
''' + BASE_CSS + EXTRA_CSS + '''
</head>
<body class="bands-index">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main list-month-wrap">
  <h1>Monthly movers</h1>
{% if rows %}
  <p class="index-lede">The month's biggest recorded price moves, ranked. Every row opens that card's price page.</p>
  <p class="faq-line"><strong>100% = the month's band floor</strong> — each row's figure is relative to the lowest price in that card's monthly record.</p>
  <table class="list-table">
    <thead>
      <tr><th>#</th><th>Card</th><th>30d move</th><th>Price page</th></tr>
    </thead>
    <tbody>
    {% for r in rows %}
      <tr>
        <td class="num">{{ loop.index }}</td>
        <td>{{ r.player }}{% if r.product %} · {{ r.product }}{% endif %} · {{ r.lane_display }}{% if r.grade_bucket != 'raw' %} · {{ r.grade_bucket }}{% endif %}</td>
        <td class="num">{{ '%.1f' % r.move_pct }}%</td>
        <td><a href="/price/{{ r.player_slug }}/{{ r.slug }}">Open price page →</a></td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <p class="faq-line">What's this list? — once a month we rank the cards whose recorded prices moved most, using only completed sales already in our records.</p>
{% else %}
  <p class="index-lede">The first list ships Dec 1.</p>
{% endif %}
</main>
''' + FOOTER_STATEMENT + '''
</body>
</html>'''

PRICE_404_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + BASE_CSS + EXTRA_CSS + '''
<title>Page not found | Card Scout</title>
</head>
<body class="band-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/lists/monthly">Monthly list</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main">
  <h1>Nothing to show here yet</h1>
  <p class="index-lede">We don't have a completed-sale record at this exact address —
  when a record builds up, its price page opens automatically.</p>
  <div class="lane-chips">
    <a class="lane-chip" href="/bands">Browse card pages</a>
    <a class="lane-chip" href="/lists/monthly">Monthly movers</a>
  </div>
</main>
''' + FOOTER_STATEMENT + '''
</body>
</html>'''


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@bp.route("/price/<player_slug>/<lane_slug>")
def price_page(player_slug: str, lane_slug: str):
    raw = lane_by_slug(lane_slug)  # shared loader (handles registry slug aliases)
    if not raw:
        abort(404)
    if raw.get("player_slug") != player_slug:
        abort(404)  # honest routing: the URL's player must own the URL's lane
    lane = compose_lane(raw)
    return render_template_string(
        PRICE_PAGE_TEMPLATE,
        lane=lane,
        honesty_label=_honesty_label(lane["band_class"], lane["n"]),
        chip=_chip_class(lane["band_class"], lane["n"]),
        ebay=ebay_search_url(raw.get("search_q") or "", lane["slug"]),
    )


@bp.route("/lists/monthly")
def monthly_list():
    export = load_monthly_export()
    rows = export["rows"] if export else []
    return render_template_string(
        MONTHLY_LIST_TEMPLATE,
        rows=rows,
        month=(export or {}).get("month", ""),
    )


@bp.errorhandler(404)
def price_404(e):
    """Honest 404 for this blueprint — real content, real 404 status (law 4)."""
    return render_template_string(PRICE_404_TEMPLATE), 404
