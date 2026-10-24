"""
CardScout /bands — card pages: market band (upper) + live eBay listings (lower half).

Spec: cardscout-2.0/For You/Plans/2026-10-22-CARD-PAGE-BUILD-SPEC-v1.md  (v1)
Builder: WALL-E (Oct 23). Verifier: Hermes (P1-P8 battery).

BANKED DECISIONS honored here (see spec §2; no re-decisions):
- Band reads ONLY the published registry (corpus prints, one-way artifact from
  cardscout-2.0/scripts/build_card_page_registry.py). NEVER bands.json numbers.
- Honesty labels PROVISIONAL vs ENGINE-GRADE rendered distinctly; FORMING lanes
  show "band forming — n=X of 3" and no band visual.
- LOWER HALF = live listings (the main event); band = context.
- Default sort LOWEST-BIN-FIRST; auctions demoted below BINs (+OBO between).
- ALL sellers visible: score/feedback/shipping beside price. NO seller-filter
  logic exists in this module (user sorts are client-side only; zero API cost).
- EPN gate: campaign id from .env = arming switch. NO campid -> NO affiliate
  tagged link renders at all (plain links) — the MPA hard guard.
- Cache law: 1h per-lane cache; ceiling = lane-hours; stale-serve fallback; the
  page NEVER hard-fails on API error/timeout (degrades to cached/band-only).
- Deal ribbon highlights prices in-zone; it never leaks band numbers.
- Zero secrets/positions/band-numbers/z-scores/FMV in rendered HTML.
- Search = the seed: /bands?q=<query> logs exactly one deposit row; empty
  results render the gratitude page.
- No auth (Phase 1). Favorites = localStorage. No Discord push anywhere.

BRIEF 4 AMENDMENT (Oct 23 PM; extend, never rewrite): search-heatmap telemetry
(T5 instrument) — same search events also log to the 2.0 data lake
(search_heatmap.jsonl, raw query = the seed deposit; NO identity) and banded
lanes render a heatmap-lite strip (n>=5 per week + top 3 community phrases).
The watch-trigger LOOP (crossing detection -> queue -> email_alerts) lives in
contributor_bp.watch_trigger_tick (the same polling half-cycle via app.py).
"""
from __future__ import annotations

import base64
import json
import os
import re
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, abort, redirect, render_template_string, request, url_for

bp = Blueprint("bands", __name__)

# ---------------------------------------------------------------------------
# PATHS (read-only registry from the 2.0 corpus; caches local to this repo)
# ---------------------------------------------------------------------------
DASH_DIR = Path(__file__).resolve().parent
REPO_DIR = DASH_DIR.parent
REGISTRY_PATH = DASH_DIR / "registry" / "card_page_registry.json"
ENV_FILE = REPO_DIR / ".env"

try:  # cache/deposit home: repo-local unless env override (Render sets LISTING_CACHE_DIR)
    DATA_DIR = REPO_DIR / "data"
except OSError:
    DATA_DIR = REPO_DIR / "data"
LISTING_CACHE_DIR = Path(os.environ.get("LISTING_CACHE_DIR", DATA_DIR / "listing_cache"))
DEPOSITS_PATH = Path(os.environ.get("SEARCH_DEPOSITS_PATH", DATA_DIR / "search_deposits.jsonl"))
# Brief 4 T5: heatmap telemetry lives in the 2.0 data lake (append-only jsonl).
# Env override FIRST so the battery can redirect it; None (unset) = disabled —
# hosts without the 2.0 repo simply skip the telemetry write (degrade, not crash).
TWO_REPO_DATA = os.environ.get("CARDSCOUT2_HOME", r"C:/Users/J/Documents/LLM/cardscout-2.0")
HEATMAP_PATH = Path(os.environ["HEATMAP_PATH"]) if os.environ.get("HEATMAP_PATH") \
    else Path(TWO_REPO_DATA) / "data_lake" / "gold" / "search_heatmap.jsonl"

CACHE_TTL_SEC = 3600          # cache law: 1h per lane
EARN_TTL_SEC = 600            # .env re-read interval (arming switch)


def data_dir() -> Path:
    LISTING_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return LISTING_CACHE_DIR


# ---------------------------------------------------------------------------
# REGISTRY (band truth; server-side only)
# ---------------------------------------------------------------------------
_reg_lock = threading.Lock()
_reg_cache = {"mtime": None, "data": None}


def load_registry() -> dict:
    try:
        mtime = REGISTRY_PATH.stat().st_mtime
    except OSError:
        return {}
    with _reg_lock:
        if _reg_cache["mtime"] != mtime or _reg_cache["data"] is None:
            try:
                data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
                by_slug = {lane["slug"]: lane for lane in data.get("lanes", [])}
                _reg_cache["data"] = {"by_slug": by_slug, "raw": data}
                _reg_cache["mtime"] = mtime
            except (OSError, ValueError):
                _reg_cache["data"] = {"by_slug": {}, "raw": {}}
        return _reg_cache["data"]


def lane_by_slug(slug: str) -> dict | None:
    return load_registry()["by_slug"].get(slug)


# ---------------------------------------------------------------------------
# EPN ARMING SWITCH (campaign id read in place from .env; never rendered)
# ---------------------------------------------------------------------------
_epn_lock = threading.Lock()
_epn_cache = {"ts": 0.0, "campid": None, "read_at": -1e9}


def epn_campaign_id() -> str | None:
    now = time.time()
    with _epn_lock:
        if now - _epn_cache["read_at"] < EARN_TTL_SEC:
            return _epn_cache["campid"]
        campid = os.environ.get("EPN_CAMPAIGN_ID")
        if campid is None:
            # env UNSET -> file fallback (the .env arming switch)
            try:
                txt = ENV_FILE.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"^\s*EPN_CAMPAIGN_ID\s*=\s*['\"]?([A-Za-z0-9\-]+)", txt, re.M)
                campid = m.group(1) if m else None
            except OSError:
                campid = None
        # explicit EMPTY env var == disarmed (MPA guard must respect that)
        campid = (campid or "").strip() or None
        _epn_cache.update(campid=campid, read_at=now)
        return campid


def epn_tag(view_url: str, lane_slug: str) -> dict:
    """Return {'href': tagged-or-plain, 'tagged': bool}. MPA guard: with no
    campaign id the tagged link is NEVER rendered (plain link only)."""
    campid = epn_campaign_id()
    url = view_url or "https://www.ebay.com"
    if campid:
        params = {
            "mkcid": "1", "mkrid": "711-53200-19255-0", "siteid": "0",
            "campid": campid, "customid": lane_slug,
            "toolid": "10001", "mkevt": "1",
        }
        sep = "&" if "?" in url else "?"
        return {"href": url + sep + urllib.parse.urlencode(params), "tagged": True}
    return {"href": url, "tagged": False}


# ---------------------------------------------------------------------------
# EBAY BROWSE API (client credentials; token + listing caches)
# ---------------------------------------------------------------------------
# Prod keys live on the founder workstation in a runtime-referenced keys file
# (pattern proven in cardscout-2.0/scripts/ebay_left_tail.py). On Render the
# pair must be set as env vars EBAY_APP_ID / EBAY_CERT_ID instead.
KEYS_FILE = Path(r"C:/Users/J/Desktop/Working File/API/Ebay Live API.txt")
TOKEN_CACHE = Path(tempfile.gettempdir()) / "cardscout_browse_token.cache"


def _browse_creds() -> tuple[str, str] | None:
    appid = os.environ.get("EBAY_APP_ID")
    cert = os.environ.get("EBAY_CERT_ID")
    if not appid:
        try:
            raw = KEYS_FILE.read_text(encoding="utf-8", errors="ignore")

            def val(label: str) -> str | None:
                m = re.search(rf"{label}\s*[:=]\s*([^\s]+)", raw)
                return m.group(1).strip() if m else None

            appid, cert = val("APP ID"), val("CERT ID")
        except OSError:
            return None
    if appid and cert:
        return appid, cert
    return None


_tok_lock = threading.Lock()


def browse_token(min_left: int = 60) -> str | None:
    """Mint/cache an OAuth client-credentials token. Returns None on failure."""
    with _tok_lock:
        try:
            if TOKEN_CACHE.exists():
                data = json.loads(TOKEN_CACHE.read_text())
                if data.get("exp", 0) - time.time() > min_left:
                    return data["access_token"]
        except (OSError, ValueError):
            pass
        creds = _browse_creds()
        if not creds:
            return None
        appid, cert = creds
        body = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }).encode()
        req = urllib.request.Request(
            "https://api.ebay.com/identity/v1/oauth2/token",
            data=body,
            headers={
                "Authorization": "Basic " + base64.b64encode(f"{appid}:{cert}".encode()).decode(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                tok = json.loads(r.read())["access_token"]
        except Exception:
            return None
        try:
            TOKEN_CACHE.write_text(json.dumps({
                "access_token": tok,
                "exp": time.time() + 7200,
            }))
        except OSError:
            pass
        return tok


def browse_search(q: str, limit: int = 40, graded: bool = False) -> dict:
    """One Browse API item_summary search. Raises nothing; returns reply dict."""
    token = browse_token()
    if not token:
        raise RuntimeError("no-token")
    url = (f"https://api.ebay.com/buy/browse/v1/item_summary/search?"
           f"q={urllib.parse.quote(q)}&limit={limit}&sort=price")
    if graded:
        url += "&filter=condition:{1500}"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def parse_listing(item: dict) -> dict:
    price = ""
    try:
        price = float(item["price"]["value"])
    except (KeyError, TypeError, ValueError):
        pass
    bo = item.get("buyingOptions") or []
    if isinstance(bo, str):
        bo = [bo]
    bo_set = {str(b).upper() for b in (bo or [])}
    if "FIXED_PRICE" in bo_set:
        cls = "bin"
    elif "BEST_OFFER" in bo_set:
        cls = "obo"
    else:
        cls = "auction"
    seller = item.get("seller") or {}
    ship = ""
    opts = item.get("shippingOptions") or []
    if opts and isinstance(opts, list):
        cost = (opts[0] or {}).get("shippingCost") or {}
        try:
            ship = float(cost.get("value"))
        except (TypeError, ValueError):
            ship = ""
    url = item.get("itemWebUrl") or f"https://www.ebay.com/itm/{item.get('itemId', '')}"
    return {
        "itemId": str(item.get("itemId", "")),
        "title": item.get("title", ""),
        "price": price,
        "cls": cls,                       # bin | obo | auction (founder type-classing)
        "score": seller.get("feedbackPercentage"),
        "fb": seller.get("feedbackScore"),
        "ship": ship,                     # float or '' (unknown, Browse summary limits)
        "end": (item.get("itemEndDate") or "")[:10],
        "url": url,
    }


# ---------------------------------------------------------------------------
# CACHE LAW LAYER (1h per lane; stale-serve; silent background refresh)
# ---------------------------------------------------------------------------
_cache_lock = threading.Lock()


def _cache_path(slug: str) -> Path:
    data_dir()
    return LISTING_CACHE_DIR / f"lane_{re.sub(r'[^a-z0-9-]', '_', slug)}.json"


def load_cache(slug: str) -> dict | None:
    try:
        return json.loads(_cache_path(slug).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_cache(slug: str, payload: dict) -> None:
    path = _cache_path(slug)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass


def _refresh_job(slug: str, search_q: str, graded: bool):
    def run():
        try:
            reply = browse_search(search_q, graded=graded)
            items = [parse_listing(it) for it in reply.get("itemSummaries", [])]
            items = [i for i in items if i["price"] != ""]
            dedup: dict[str, dict] = {}
            for it in items:
                dedup.setdefault(it["itemId"], it)
            write_cache(slug, {
                "ts": time.time(),
                "q": search_q,
                "items": sorted(dedup.values(), key=lambda x: (x["price"] if x["price"] != "" else 1e12)),
                "api_error": None,
            })
        except Exception:
            # silent refresh: on failure the previous (stale) cache survives; no log write
            return
    t = threading.Thread(target=run, daemon=True)
    t.start()


def get_listings(slug: str) -> tuple[list[dict], dict]:
    """Cache-law listings fetch. NEVER raises. Returns (items, meta).

    meta: {source: fresh|cached|stale|none|error, age: seconds, error: str|None}
    First-ever view of a lane (no cache at all) fetches synchronously with a
    hard 30s ceiling; every other path serves instantly.
    """
    lane = lane_by_slug(slug) or {}
    q = lane.get("search_q")
    if not q:
        return [], {"source": "none", "age": None, "error": None}
    graded = lane.get("grade_bucket", "raw") != "raw"
    cache = load_cache(slug)
    now = time.time()
    age = (now - cache["ts"]) if cache and cache.get("ts") else None
    if cache and age is not None and age <= CACHE_TTL_SEC:
        return cache.get("items", []), {"source": "cached", "age": age, "error": None}
    # expired or absent
    if cache:
        _refresh_job(slug, q, graded)  # silent background refresh; serve stale now
        items = cache.get("items", [])
        src = "stale" if items else "none"
        return items, {"source": src, "age": age, "error": None}
    # first view ever: synchronous, guarded — never hard-fails (P6)
    try:
        reply = browse_search(q, graded=graded)
        items = [parse_listing(it) for it in reply.get("itemSummaries", [])]
        items = [i for i in items if i["price"] != ""]
        dedup: dict[str, dict] = {}
        for it in items:
            dedup.setdefault(it["itemId"], it)
        item_list = sorted(dedup.values(), key=lambda x: (x["price"] if x["price"] != "" else 1e12))
        write_cache(slug, {"ts": now, "q": q, "items": item_list, "api_error": None})
        return item_list, {"source": "fresh", "age": 0, "error": None}
    except Exception as e:
        return [], {"source": "none", "age": None, "error": type(e).__name__}


# ---------------------------------------------------------------------------
# SEARCH DEPOSITS (search-is-the-seed; exactly one row per q= visit)
# ---------------------------------------------------------------------------
_dep_lock = threading.Lock()


def record_deposit(q: str, lane_slug: str | None, kind: str) -> None:
    row = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "q": (q or "")[:200],
        "lane_slug": lane_slug,
        "kind": kind,
    }
    line = json.dumps(row) + "\n"
    with _dep_lock:
        try:
            DEPOSITS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DEPOSITS_PATH, "a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# SEARCH-HEATMAP TELEMETRY (Brief 4 Job 2 — the T5 instrument). Same search
# events, second append-only ledger in the 2.0 data lake. heat != identity:
# the raw query IS stored (it's the corpus per search-is-the-seed), the sender
# is NOT. results_n rides along for observatory-depth stats.
# ---------------------------------------------------------------------------
_hm_lock = threading.Lock()


def heatmap_log(q: str, lane_slug: str | None, direction: str | None, results_n: int) -> None:
    """One append per logged search; NEVER raises (telemetry must not break
    the page; file absent/unwritable = skipped silently)."""
    if not q:
        return
    row = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "lane_slug": lane_slug,
        "search_q": (q or "")[:200],   # the raw query is the seed deposit itself
        "direction": direction,
        "results_n": int(results_n or 0),
    }
    try:
        line = json.dumps(row) + "\n"
    except (TypeError, ValueError):
        return
    with _hm_lock:
        try:
            HEATMAP_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(HEATMAP_PATH, "a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            pass  # telemetry loss is acceptable; the deposit itself is not lost


# ---------------------------------------------------------------------------
# LISTING PRESENTATION (lowest-BIN-first default, all sellers, no filtering)
# ---------------------------------------------------------------------------
def order_default(items: list[dict]) -> list[dict]:
    """Founder type-class order: plain BIN < OBO < Auction; price asc in class.

    This is the banked DEFAULT order only — the user's client-side sorts are
    the lens; nothing here filters or demotes by seller score.
    """
    cls_order = {"bin": 0, "obo": 1, "auction": 2}
    return sorted(
        items,
        key=lambda i: (cls_order.get(i["cls"], 3),
                       i["price"] if i["price"] != "" else 1e12),
    )


def deal_count(items: list[dict], lane: dict) -> int | None:
    """Count live asks inside this lane's deal window (prices only; no leak)."""
    deal = lane.get("deal")
    if not deal:
        return None
    lo, hi = float(deal["low"]), float(deal["high"])
    n = 0
    for it in items:
        p = it.get("price")
        if p == "":
            continue
        if lo <= float(p) <= hi:
            n += 1
    return n


# ---------------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------------
BASE_CSS = '<link rel="stylesheet" href="/static/style.css">\n<link rel="stylesheet" href="/static/bands.css">'

# Impact.com site-ownership verification — EXACT same tags as the homepage
# (public_site.py, EPN/affiliate path). Template-consistency (Brief 5 Job B):
# every public page carries the proof; values are public web metadata by design.
IMPACT_VERIFICATION_META = (
    '<!-- Impact.com site-ownership verification (same block as home, Oct 22) -->\n'
    '<meta name="impact-site-verification" content="0d54fa41-a1e1-48e7-854c-160e826f9210" value="0d54fa41-a1e1-48e7-854c-160e826f9210">\n'
    "<meta name='impact-site-verification' value='0d54fa41-a1e1-48e7-854c-160e826f9210'>\n"
    '<!-- end Impact verification block -->\n'
)

FOOTER_STATEMENT = '''
<footer class="bands-footer">
  <p>Bands on this site are built from our own record of completed sales — the
  more people search, the sharper every band gets. Your searches built these bands.</p>
</footer>
'''

BAND_VISUAL = '''
{% set _med = lane.band.median %}
{% set _lo = lane.band.low %}
{% set _hi = lane.band.high %}
{% set _span = _hi - _lo or 1 %}
{% set _medpct = ((_med - _lo) / _span * 100) | round(1) %}
{% set _deal_lo = lane.deal.low %}
{% set _deal_hi = lane.deal.high %}
{% set _dl = ((_deal_lo - _lo) / _span * 100) | round(1) %}
{% set _dw = ((_deal_hi - _deal_lo) / _span * 100) | round(1) %}
<div class="band-visual" role="img" aria-label="Market band for this card">
  <div class="band-track">
    <div class="band-box"></div>
    <div class="band-dealzone" style="left:{{ _dl }}%; width:{{ _dw }}%"></div>
    <div class="band-median" style="left:{{ _medpct }}%"></div>
  </div>
  <div class="band-scale"><span class="band-edge">low</span><span class="band-edge">high</span></div>
</div>
'''

CARD_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + IMPACT_VERIFICATION_META + '''<title>{{ lane.player }} {{ lane.lane_display }} price band &amp; live listings — Card Scout</title>
{% set _bw = 'engine-grade' if lane.band_class == 'engine_grade' else ('provisional' if lane.band_class == 'provisional' else 'forming') %}
<meta name="description" content="Live {{ lane.player }} {{ lane.lane_display }} listings with the {{ _bw }} market band built from real completed sales — free on Card Scout.">
<link rel="canonical" href="https://cardscout.pro/bands/{{ lane.slug }}">
<meta property="og:title" content="{{ lane.player }} {{ lane.lane_display }} price band &amp; live listings — Card Scout">
<meta property="og:description" content="Live {{ lane.player }} {{ lane.lane_display }} listings with the {{ _bw }} market band built from real completed sales — free on Card Scout.">
<meta property="og:url" content="https://cardscout.pro/bands/{{ lane.slug }}">
<meta property="og:type" content="website">
''' + BASE_CSS + '''
</head>
<body class="band-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/">Home</a></div>
  </nav>
</header>

<main class="band-main">
  <div class="band-head">
    <div class="band-head-left">
      <h1>{{ lane.player }} <span class="lane-title">{{ lane.lane_display }}</span></h1>
      <div class="band-crumb">
        {{ lane.crumb }}
        · <form class="band-search" action="/bands" method="get">
            <input type="search" name="q" placeholder="Search a card or player…" aria-label="Search cards">
          </form>
      </div>
    </div>
    <div class="band-head-right">
      <span class="honesty honesty-{{ lane.band_class }}">
        {%- if lane.band_class == 'engine_grade' -%}ENGINE-GRADE BAND
        {%- elif lane.band_class == 'provisional' -%}PROVISIONAL BAND
        {%- else -%}BAND FORMING — n={{ lane.n }} of 3
        {%- endif -%}
      </span>
      <button id="fav-btn" class="fav-btn" data-slug="{{ lane.slug }}" title="Favorite this card — kept on this device, no account">☆ Favorite</button>
    </div>
  </div>

  <p class="provenance">
    This band is assessed from {{ lane.n }} clean sale prints in our corpus
    {%- if lane.first_date %} ({{ lane.first_date }} → {{ lane.last_date }}){% endif %} —
    including searches like yours, which is how coverage grows.
  </p>

{% if lane.band_class != 'forming' %}
  ''' + BAND_VISUAL + '''
{% else %}
  <p class="band-forming-note">No band yet — {{ lane.n }} clean print{{ '' if lane.n == 1 else 's' }} so far
  (a band appears at 3). Live listings below are the market right now.</p>
{% endif %}

{% if deal_count is not none and deal_count > 0 %}
  <div class="deal-ribbon">◆ {{ deal_count }} live listing{{ '' if deal_count == 1 else 's' }} priced inside this lane's deal window</div>
{% endif %}

{% if heat_n is not none and heat_n >= 5 %}
  <div class="heat-strip" id="heat-strip">
    <div class="heat-line">🔥 Searched {{ heat_n }} times this week</div>
    {% if heat_phrases %}
    <div class="heat-phrases">Top community searches:
      {%- for ph in heat_phrases %} <span class="heat-phrase">“{{ ph }}”</span>{% if not loop.last %},{% endif %}{% endfor %}</div>
    {% endif %}
  </div>
{% endif %}

{% if listings_meta.source in ('stale', 'none', 'error') and items %}
  <div class="listings-note">Showing saved listings from the last hour — live refresh is running in the background.</div>
{% endif %}
{% if listings_meta.source in ('none', 'error') and not items %}
  <div class="listings-note">{{ 'No live listings right now — check back soon.' if band_only_ok else '' }}</div>
{% endif %}

  <section class="listings" id="listings">
    <h2>Live listings</h2>
{% if items %}
    <div class="sort-bar" role="toolbar" aria-label="Sort listings">
      <span class="sort-label">Sort:</span>
      <button class="sort-btn active" data-sort="default">Lowest BIN</button>
      <button class="sort-btn" data-sort="price">Price</button>
      <button class="sort-btn" data-sort="score">Score</button>
      <button class="sort-btn" data-sort="fb">Feedback</button>
      <button class="sort-btn" data-sort="ship">Free ship</button>
      <button class="sort-btn" data-sort="type">BIN/Auction</button>
      <button class="sort-btn" data-sort="date">Date</button>
    </div>
    <div class="listing-rows" id="listing-rows">
    {% for it in items %}
      <div class="listing-row"
           data-price="{{ it.price }}"
           data-class="{{ it.cls }}"
           data-score="{{ it.score if it.score is not none else -1 }}"
           data-fb="{{ it.fb if it.fb is not none else -1 }}"
           data-ship="{{ it.ship if it.ship != '' else 1e12 }}"
           data-date="{{ it.end or '' }}">
        <span class="row-rank">#{{ loop.index }}</span>
        <span class="row-price">{% if it.price != '' %}${{ '%.2f' % it.price }}{% else %}—{% endif %}</span>
        <span class="row-type">{% if it.cls == 'bin' %}BIN{% elif it.cls == 'obo' %}OBO{% else %}Auction{% endif %}</span>
        <span class="row-title"><a href="{{ it.href }}" {% if it.tagged %}rel="sponsored nofollow"{% endif %} target="_blank">{{ it.title[:96] }}</a></span>
        <span class="row-score">score {{ '—' if it.score is none else it.score | int }}%</span>
        <span class="row-fb">fb {{ '—' if it.fb is none else '{:,}'.format(it.fb | int) }}</span>
        <span class="row-ship">ship {{ '—' if it.ship == '' else ('Free' if it.ship == 0 else '$' ~ '%.2f' % it.ship) }}</span>
        <a class="row-buy" href="{{ it.href }}" {% if it.tagged %}rel="sponsored nofollow"{% endif %} target="_blank">View on eBay</a>
      </div>
    {% endfor %}
    </div>
    <p class="count-note">{{ items | length }} listings — every seller shown, lowest BIN first.</p>
{% else %}
    <p class="no-listings">No live listings right now — the band above is the market record for this lane.</p>
{% endif %}
  </section>

  <section class="disclosure">
    <p>This page is free because eBay pays us when you buy — nothing hidden.
    Your searches built these bands.</p>
  </section>
</main>
''' + FOOTER_STATEMENT + '''
<script src="/static/bands.js"></script>
</body>
</html>'''

INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + IMPACT_VERIFICATION_META + '''<title>Card Pages — Card Scout</title>
<meta name="description" content="Market bands and live listings, one free page per card lane. Search a card — every search grows the bands.">
<link rel="canonical" href="https://cardscout.pro/bands">
''' + BASE_CSS + '''
</head>
<body class="bands-index">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
        <div class="nav-links"><a href="/deals">Deals</a> <a href="/pricing">Pricing</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main">
  <h1>Card pages</h1>
  <p class="index-lede">One free page per card lane: the market band our records build,
  live listings below it. Search a card — if a page opens, that's your lane; if not,
  your search just started one.</p>
  <form class="index-search" action="/bands" method="get">
    <input type="search" name="q" placeholder="Search a card or player…" aria-label="Search cards" autofocus>
    <button type="submit">Search</button>
  </form>

  {% for player_name, player_lanes in grouped %}
  <details class="player-group" {% if loop.first %}open{% endif %}>
    <summary>{{ player_name }} <span class="lane-count">{{ player_lanes | length }} lanes</span></summary>
    <div class="lane-chips">
    {% for lane in player_lanes %}
      <a class="lane-chip chip-{{ lane.band_class }}" href="/bands/{{ lane.slug }}">
        <span class="chip-title">{{ lane.lane_display }}{% if lane.grade_bucket != 'raw' %} · {{ lane.grade_bucket }}{% endif %}</span>
        <span class="chip-meta">
          {%- if lane.band_class == 'engine_grade' -%}ENGINE-GRADE
          {%- elif lane.band_class == 'provisional' -%}PROVISIONAL
          {%- else -%}forming n={{ lane.n }}
          {%- endif -%}
        </span>
      </a>
    {% endfor %}
    </div>
  </details>
  {% endfor %}
</main>
''' + FOOTER_STATEMENT + '''
<script src="/static/bands.js"></script>
</body>
</html>'''

GRATITUDE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + IMPACT_VERIFICATION_META + '''<title>Thanks — your search taught the machine · Card Scout</title>
''' + BASE_CSS + '''
</head>
<body class="band-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main gratitude">
  <h1>Thank you — your search taught the machine.</h1>
  <p class="gratitude-lede">"<span class="gratitude-q">{{ q }}</span>" doesn't have a card page yet.
  That search is now a deposit in our record: when a few more like it arrive,
  a band starts to form and a page opens — built in part by you. No account, no fee.</p>
  <p class="gratitude-next">Try one of the live pages:</p>
  <div class="lane-chips">
    {% for lane in examples %}
    <a class="lane-chip chip-{{ lane.band_class }}" href="/bands/{{ lane.slug }}">
      <span class="chip-title">{{ lane.player }} · {{ lane.lane_display }}</span>
      <span class="chip-meta">
        {%- if lane.band_class == 'engine_grade' -%}ENGINE-GRADE
        {%- elif lane.band_class == 'provisional' -%}PROVISIONAL
        {%- else -%}forming n={{ lane.n }}
        {%- endif -%}
      </span>
    </a>
    {% endfor %}
  </div>
  <section class="disclosure">
    <p>This site is free because eBay pays us when you buy — nothing hidden.
    Your searches built these bands.</p>
  </section>
</main>
''' + FOOTER_STATEMENT + '''
<script src="/static/bands.js"></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@bp.route("/bands")
def bands_index() -> str:
    reg = load_registry()
    q = (request.args.get("q") or "").strip()
    if q:
        # SEARCH = THE SEED: one deposit per q= visit, then resolve or gratitude
        match = find_lane_for_query(q)
        if match:
            record_deposit(q, match["slug"], "search-hit")
            heatmap_log(q, match["slug"], None, 1)
            return redirect(url_for("bands.band_page", slug=match["slug"]))
        record_deposit(q, None, "search-expansion")
        heatmap_log(q, None, None, 0)
        example_lanes = sorted(
            [l for l in reg["raw"].get("lanes", []) if l["band_class"] != "forming"],
            key=lambda e: -e["n"])[:8]
        return render_template_string(
            GRATITUDE_TEMPLATE, q=q, example_lanes=example_lanes)

    lanes = reg["raw"].get("lanes", [])

    grouped = group_lanes_for_index(lanes)
    return render_template_string(INDEX_TEMPLATE, grouped=grouped)


def group_lanes_for_index(lanes: list) -> list:
    order = {"engine_grade": 0, "provisional": 1, "forming": 2}
    buckets: dict[str, list] = {}
    for lane in lanes:
        player = lane["player"]
        buckets.setdefault(player, []).append(lane)
    out = []
    for player, player_lanes in buckets.items():
        player_lanes = sorted(player_lanes, key=lambda e: (order[e["band_class"]], -e["n"], e["lane_display"]))
        out.append((player, player_lanes))
    out.sort(key=lambda x: (min(order[l["band_class"]] for l in x[1]), -sum(l["n"] for l in x[1]), x[0]))
    return out


def find_lane_for_query(q: str) -> dict | None:
    ql = re.sub(r"[^a-z0-9 ]", " ", q.lower())
    tokens = [t for t in ql.split() if t]
    if not tokens:
        return None
    best, best_key = None, None
    for lane in load_registry()["raw"].get("lanes", []):
        hay = lane["search_q"].lower() + " " + lane["player"].lower() + " " + lane["lane"].replace("-", " ")
        hay = re.sub(r"[^a-z0-9 ]", " ", hay)
        hits = sum(1 for t in tokens if t in hay)
        if hits < 2:
            continue
        # tiebreak: banded lanes before forming, then clean-print count, then slug
        key = (hits, 1 if lane["band_class"] != "forming" else 0, lane["n"], lane["slug"])
        if best_key is None or key > best_key:
            best, best_key = lane, key
    return best


def collect_search_heat(
    lane_slug: str,
    window_days: int = 7,
    min_n: int = 5,
    top_phrases: int = 3,
) -> tuple[int, list[str]]:
    """Aggregates feed NOTHING else yet (T5 lite): read this lane's raw search
    queries from the heatmap ledger within the window; return (n, top phrases).
    n>=min_n is the render gate; caller renders 'nothing' below it. NEVER
    raises; any read failure = (0, []) = honest quiet."""
    try:
        if not HEATMAP_PATH.exists():
            return 0, []
        cutoff = time.time() - window_days * 86400
        counts: dict[str, int] = {}
        n = 0
        with HEATMAP_PATH.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("lane_slug") != lane_slug:
                    continue
                try:
                    ts = datetime.fromisoformat(str(row.get("ts", ""))).timestamp()
                except (ValueError, OSError):
                    ts = 0.0
                if ts and ts < cutoff:
                    continue
                q = str(row.get("search_q") or "").strip().lower()
                if not q:
                    continue
                n += 1
                counts[q] = counts.get(q, 0) + 1
        top = [p for p, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top_phrases]]
        top = [p[:64] for p in top]
        return n, (top if n >= min_n else [])
    except OSError:
        return 0, []


def compose_lane(lane: dict) -> dict:
    """Whitelisted fields for templates (no env values, no engine internals)."""
    grade_disp = "raw card" if lane["grade_bucket"] == "raw" else lane["grade_bucket"]
    return {
        "slug": lane["slug"],
        "player": lane["player"],
        "product": lane.get("product") or "",
        "lane": lane["lane"],
        "lane_display": lane["lane_display"],
        "grade_bucket": lane["grade_bucket"],
        "n": lane["n"],
        "first_date": lane.get("first_date", ""),
        "last_date": lane.get("last_date", ""),
        "band_class": lane["band_class"],
        "band": lane.get("band"),
        "deal": lane.get("deal"),
        "search_q": lane.get("search_q", ""),
        "crumb": " · ".join(x for x in [lane.get("product") or "", grade_disp] if x),
    }


@bp.route("/bands/<slug>")
def band_page(slug: str):
    raw = lane_by_slug(slug)
    if not raw:
        abort(404)  # Brief-6-followup catch (Oct 24): 'abp.abort' NameError -> live 500 on every not-found lane slug
    lane = compose_lane(raw)
    items, meta = get_listings(slug)
    items = order_default(items)
    for it in items:
        tag = epn_tag(it["url"], slug)
        it["href"] = tag["href"]
        it["tagged"] = tag["tagged"]
    dc = deal_count(items, raw)
    heat_n, heat_phrases = collect_search_heat(slug)
    return render_template_string(
        CARD_PAGE_TEMPLATE, lane=lane, items=items,
        listings_meta=meta, deal_count=dc,
        heat_n=heat_n, heat_phrases=heat_phrases,
        band_only_ok=(lane["band_class"] != "forming"),
    )


@bp.route("/bands/health")
def bands_health():
    reg = load_registry()
    return {
        "ok": True,
        "lanes": reg.get("raw", {}).get("lane_count", 0),
        "epn_armed": epn_campaign_id() is not None,
        "cache_dir": str(LISTING_CACHE_DIR),
        "heatmap_path": str(HEATMAP_PATH),
        "heatmap_enabled": HEATMAP_PATH is not None,
    }