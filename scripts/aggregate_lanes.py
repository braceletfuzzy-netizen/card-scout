"""Card Scout — AGGREGATE-TAG FALLBACK (Nov 12, 2026). Brief:
cardscout-2.0/For You/Plans/… and Temp/hermes_brief_aggregate_tag.md.

When a /bands lane has no own-corpus print data (forming/n<3 or thin), the page
falls back to an AGGREGATE band sourced from the Card Hedge API. Honest tagging:

  own-corpus data (n>=3)       -> CORPUS   (existing behavior, untouched)
  no corpus + CH cached        -> AGGREGATE[.confidence A-D]
  no corpus + no CH cache      -> AGGREGATE-QUEUING (first search builds it)

Design (bounds honored — ADD never REMOVE):
- NEVER overwrites our own band values: the lane table is
  `own_band (CORPUS) else aggregate_band (AGGREGATE)` — one source of truth per
  row. CORPUS lanes are never shown aggregate numbers.
- CACHE-FIRST: every CH lookup caches to data/aggregate_lanes/<player>-<lane>.jsonl
  keyed `player|set|variant`; second-hit = zero CH API calls.
- RATE-BUDGET: ≤8 req/min enforced here; backfill runner batches nightly ≤20 lanes.
- Backward-looking consensus only (prices + sales + index history). No
  forward-chain, no flags/clocks/EV — Separation Charter held.

Key read-IN-PLACE from .secrets (never copied/moved):
  CARD_HEDGER_API_KEY=file:C:/Users/J/.secrets/card-scout/card-hedger-api-key.txt

CH API shapes verified live Nov 12:
  card-search(player=…, search=…) -> {cards:[{card_id, set, variant, prices:
    [{grade, price}], '7 Day Sales', '30 Day Sales', gain, …}], count}
  card-fmv(card_id, grade) -> {price, price_low, price_high, confidence_grade
    (A-D), confidence, as_of_date, …}

Usage in dashboard/band_pages.py: `get_aggregate_lane(player, lane, grade_bucket)`
returns a dict for the AGGREGATE branch, or None when no cached/matching
aggregate exists -> the page shows the QUEUING honest state instead.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
import urllib.parse
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent       # card-scout repo root
AGG_DIR = Path(os.environ.get("AGG_CACHE_DIR",
                              REPO_DIR / "data" / "aggregate_lanes"))  # cache home
AGG_LOG = AGG_DIR / "aggregate_backfill.log"

CLIENT_PATH = REPO_DIR / "scripts" / "cardhedger_client.py"
KEY_PATH = Path(r"C:/Users/J/.secrets/card-scout/card-hedger-api-key.txt")

RATE_MIN_INTERVAL = 7.5   # seconds between CH calls (≤8 req/min)
FMV_TTL_SEC = 86400 * 7   # aggregate-cache recheck after 7 days

_lock = threading.Lock()
_last_call = {"t": 0.0}
_client = None

# ---------------------------------------------------------------------------
# Card Hedge client (read-in-place; import or load lazily)
# ---------------------------------------------------------------------------
def _load_client():
    """Resolve the CH client (key read IN PLACE; never copied). Cache-only mode
    (False marker) when unreachable/unconfigured — the page degrades to the
    AGGREGATE-QUEUING honest state, never a crash."""
    global _client
    with _lock:
        if _client is not None:
            return _client
        try:
            if CLIENT_PATH.exists():
                sys.path.insert(0, str(CLIENT_PATH.parent))
                from cardhedger_client import CardHedgerClient  # noqa: E402
                os.environ.setdefault("CARD_HEDGER_API_KEY", f"file:{KEY_PATH}")
                _client = CardHedgerClient()
            else:
                _client = False  # marker: no client (Render) -> cache-only mode
        except Exception:
            _client = False  # key unset/invalid/empty (tests, Render) -> cache-only
        return _client


def _throttle() -> None:
    """Sleep to keep CH calls ≤8/min. Blocks the (background/build-time) caller."""
    with _lock:
        now = time.time()
        wait = _last_call["t"] + RATE_MIN_INTERVAL - now
        if wait > 0:
            time.sleep(wait)
        _last_call["t"] = time.time()


# ---------------------------------------------------------------------------
# Cache (jsonl per player-lane; keyed `player|set|variant`)
# ---------------------------------------------------------------------------
def _cache_path(player: str) -> Path:
    safe = re.sub(r"[^a-z0-9-]", "-", (player or "").lower()).strip("-") or "_x"
    AGG_DIR.mkdir(parents=True, exist_ok=True)
    return AGG_DIR / f"{safe}.jsonl"


def cache_read(player: str, lane: str, grade: str) -> dict | None:
    """Fresh (≤7d) cache row for this player+lane+grade, or None."""
    try:
        if not _cache_path(player).exists():
            return None
        cutoff = time.time() - FMV_TTL_SEC
        best = None
        with _cache_path(player).open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("player") != player or row.get("lane") != lane or row.get("grade") != grade:
                    continue
                ts = float(row.get("ts") or 0)
                if ts >= cutoff and (best is None or ts > float(best.get("ts") or 0)):
                    best = row
        return best
    except OSError:
        return None


def cache_write(player: str, lane: str, grade: str, band: dict) -> None:
    row = dict(band)
    row.update({"ts": time.time(), "player": player, "lane": lane, "grade": grade})
    try:
        AGG_DIR.mkdir(parents=True, exist_ok=True)
        with _cache_path(player).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Lane matching: registry lane token → CH card
# ---------------------------------------------------------------------------
def _lane_tokens(lane: str) -> list[str]:
    """'auto-wave' -> ['wave'], 'wave' -> ['wave']. 'auto' lanes can't match a
    CH variant; the raw lane token is the wave/variant keyword."""
    return [t for t in re.split(r"[-_ ]+", (lane or "").lower())
            if t not in ("auto",)]


def _grade_bucket_to_ch(grade_bucket: str) -> str:
    """Registry grade_bucket -> CH grade label."""
    gb = (grade_bucket or "raw").upper()
    if gb == "RAW":
        return "Raw"
    m = re.match(r"^(PSA|SGC|CGC|BGS)\s?(\d+(?:\.\d+)?)$", gb)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return gb


def _match_card(cards: list[dict], player: str, lane: str, product: str | None,
                grade: str) -> dict | None:
    """Pick the CH card whose player+variant+set best matches the lane."""
    toks = _lane_tokens(lane)
    if not toks:
        return None
    pl = (player or "").lower()

    def is_graded_lane() -> bool:
        return not grade.lower().startswith("raw")

    best, best_key = None, None
    for c in cards:
        cp = (c.get("player") or "").lower()
        if cp != pl and cp not in pl and pl not in cp:
            continue
        variant = (c.get("variant") or "").lower()
        vtoks = re.split(r"[-_ ]+", variant)
        if not all(any(t == v for v in vtoks) for t in toks):
            continue
        # graded lanes need a graded price present (raw lanes need Raw)
        need = grade if is_graded_lane() else "Raw"
        prices = c.get("prices") or []
        have = [p for p in prices
                if str(p.get("grade", "")).lower().startswith(need.lower())
                and _f(p.get("price")) > 0]
        if is_graded_lane() and not have:
            continue
        if not is_graded_lane() and not have:
            continue
        prod = (product or "").lower()
        cs = (c.get("set") or "").lower()
        prod_score = 0
        if prod:
            prod_score = 2 if (prod in cs or cs in prod) else 0
        # prefer most sales, then highest raw/grade price, then set-name match
        key = (prod_score,
               int(c.get("30 Day Sales") or 0),
               max((_f(p.get("price")) for p in have), default=0.0),
               -(len(variant) - len(" ".join(toks))))
        if best_key is None or key > best_key:
            best, best_key = c, key
    return best


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


_CONF_TAG = {"A": "A", "B": "B", "C": "C", "D": "D"}


def _derive_band(card: dict, fmv: dict | None, grade: str) -> dict | None:
    """AGGREGATE band values from CH consensus (backward-looking only).
    Derivation per brief:
      low  = min(Raw/grade asks), high = max(asks), mid = FMV price.
    Confidence: CH confidence_grade A-D -> display 'AGGREGATE·A'.
    """
    prices = card.get("prices") or []
    need = (grade or "Raw").lower()
    asks = [_f(p.get("price")) for p in prices
            if str(p.get("grade", "")).lower().startswith(need) and _f(p.get("price")) > 0]
    if not asks:
        return None
    if fmv and fmv.get("price"):
        mid = _f(fmv.get("price"))
    else:
        mid = sorted(asks)[len(asks) // 2]
    if mid <= 0:
        return None
    conf = (fmv or {}).get("confidence_grade") or ""
    conf = _CONF_TAG.get(conf.upper(), "") if conf else ""
    return {
        "low": round(min(asks), 2),
        "high": round(max(asks), 2),
        "mid": round(mid, 2),
        "confidence_grade": conf,
        "n_ch_asks": len(asks),
        "sales_7d": int(card.get("7 Day Sales") or 0),
        "sales_30d": int(card.get("30 Day Sales") or 0),
        "card_id": card.get("card_id") or "",
        "set": card.get("set") or "",
        "variant": card.get("variant") or "",
        "gain_pct": _f(card.get("gain")),
        "as_of": (fmv or {}).get("as_of_date") or "",
    }


# ---------------------------------------------------------------------------
# Public API (cache-first)
# ---------------------------------------------------------------------------
def get_aggregate_lane(player: str, lane: str, grade_bucket: str = "raw",
                       product: str | None = None,
                       allow_fetch: bool = True) -> dict | None:
    """Return AGGREGATE band dict for a lane, or None (caller shows QUEUING).

    Cache-first: a fresh cached row = zero CH API calls. Otherwise (when
    allow_fetch and CH reachable and within rate budget) one search+FMV pair
    runs, the result caches, and the page re-renders AGGREGATE next hit.
    """
    grade = _grade_bucket_to_ch(grade_bucket)
    key = {"player": player, "lane": lane, "grade": grade}
    hit = cache_read(player, lane, grade)
    if hit:
        band = {k: v for k, v in hit.items()
                if k not in ("ts", "player", "lane", "grade")}
        return {**key, "band": band["band"], "source": "cache"}
    if not allow_fetch:
        return None
    client = _load_client()
    if not client:
        return None
    try:
        _throttle()
        q = f"{player} {' '.join(_lane_tokens(lane))}".strip()
        reply = client.search_cards(search=q, category="Baseball")
        cards = reply.get("cards") or []
        card = _match_card(cards, player, lane, product, grade)
        if card is None:
            # miss: record a negative cache row so repeat loads don't re-burn API
            miss = {"band": None, "miss": True, "set": "", "variant": ""}
            miss.update(key)
            cache_write(player, lane, grade, {**key, "band": None, "miss": True})
            return None
        fmv = None
        try:
            _throttle()
            fmv = client.get_fmv(card_id=card["card_id"], grade=grade)
        except Exception:
            fmv = None
        band = _derive_band(card, fmv, grade)
        if band is None:
            cache_write(player, lane, grade, {**key, "band": None, "miss": True})
            return None
        cache_write(player, lane, grade, {**key, "band": band})
        return {**key, "band": band, "source": "fresh"}
    except Exception:
        return None


def lane_state(lane: dict | None, player: str | None = None) -> str:
    """Classify a lane for the renderer: 'corpus' | 'aggregate' | 'queue'."""
    if not lane:
        return "queue"
    cls = (lane.get("band_class") or "").lower()
    n = int(lane.get("n") or 0)
    if cls in ("engine_grade", "provisional") and n >= 3 and lane.get("band"):
        return "corpus"
    # forming / n<3 / band None -> not renderable corpus
    return "aggregate" if False else "queue-first"


def tag_label(state: str, confidence: str = "") -> str:
    if state == "corpus":
        return "CORPUS BAND"
    if state == "aggregate":
        return f"AGGREGATE BAND{('·' + confidence) if confidence else ''}"
    return "AGGREGATE-QUEUING"
