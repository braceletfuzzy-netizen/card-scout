"""
TRENDING SEARCHES — the homepage nav item fed by the search-deposit log.

Brief (Nov 12, 2026): '/trending' currently shows only Card-Hedger movers.
This pass feeds the SAME /trending page with the community's own search
activity aggregated from the heatmap ledger (search_heatmap.jsonl / the
search-deposit stream band_pages already appends to on every q= visit).

PRIVACY SHAPE (brief law):
- term + count aggregates ONLY — no identity, no per-user rows, no timestamps
  per term rendered, nothing per-person anywhere on the page.
- Raw queries are already the public seed (search-is-the-seed); this module
  aggregates + dedupes them case-insensitively into term groups.
- Probe/test rows ('probe', fixture markers, UUID-class digit strings) are
  filtered so fixture noise never reaches the public page.
- NEVER raises: unreadable/empty ledger = honest 'quiet' empty state
  (same degrade law as the movers half).

Data shape returned by top_search_terms():
  [{'term': str, 'count': int, 'slug': str|None, 'lane_display': str|None}]
  — count = total ledger hits within the window; slug = the registry lane
  the term resolves to (for the 'Open card page' link) or None.
"""
from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

# The heatmap ledger lives in the 2.0 data lake (env-redirectable for tests —
# the same env contract band_pages.heatmap_log writes under).
TWO_REPO_DATA = Path(r"C:/Users/J/Documents/LLM/cardscout-2.0")


def heatmap_path() -> Path:
    import os
    if os.environ.get("HEATMAP_PATH"):
        return Path(os.environ["HEATMAP_PATH"])
    return (TWO_REPO_DATA / "data_lake" / "gold" / "search_heatmap.jsonl"
            if TWO_REPO_DATA.exists()
            else Path("data_lake/gold/search_heatmap.jsonl"))

WINDOW_DAYS = 14          # rolling fortnight of community searches
MIN_COUNT = 2             # a term needs >1 hit to be 'trending' (no singletons)
TOP_N = 12                # terms rendered
MAX_LEN = 64              # per-term display truncation

# probe/fixture markers: anything matching these never renders publicly
_PROBE_RE = re.compile(r"probe|smoke|fixture|battery|_test|\d{6,}")

_lock = threading.Lock()
_cache: dict = {"ts": 0.0, "rows": []}


def _resolve_slug(term: str) -> dict | None:
    """Resolve a term to the registry lane it opens (best-effort; pure read).
    Reuses band_pages.find_lane_for_query's 2+-token overlap rule — if the
    term doesn't clearly name a real lane, no link renders (no near-misses)."""
    try:
        import sys
        dash = str(Path(__file__).resolve().parent.parent / "dashboard")
        if dash not in sys.path:
            sys.path.insert(0, dash)
        from band_pages import find_lane_for_query  # noqa: E402
        return find_lane_for_query(term)
    except Exception:
        return None


def top_search_terms(window_days: int = WINDOW_DAYS,
                     top_n: int = TOP_N,
                     min_count: int = MIN_COUNT) -> list[dict]:
    """Aggregate the search-deposit stream: term + count, identity-free.
    Cache 10 min (reads the whole append-only file; cheap + shared across
    requests). Any failure = [] = the honest quiet state."""
    now = __import__("time").time()
    with _lock:
        if now - _cache["ts"] < 600:
            return _cache["rows"]
    rows: list[dict] = []
    try:
        p = heatmap_path()
        if not p.exists():
            with _lock:
                _cache.update(ts=now, rows=[])
            return []
        cutoff = now - window_days * 86400
        counts: dict[str, int] = {}
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                try:
                    ts = datetime.fromisoformat(str(row.get("ts", ""))).timestamp()
                except (ValueError, OSError):
                    ts = 0.0
                if ts and ts < cutoff:
                    continue
                term = re.sub(r"[^a-z0-9 ]", " ", str(row.get("search_q") or "").lower())
                term = re.sub(r"\s+", " ", term).strip()
                if not term or _PROBE_RE.search(term):
                    continue
                counts[term] = counts.get(term, 0) + 1
        # keep only the honest threshold, sort by community weight
        hot = sorted(((t, c) for t, c in counts.items() if c >= min_count),
                     key=lambda kv: (-kv[1], kv[0]))[:top_n]
        for term, count in hot:
            lane = _resolve_slug(term)
            rows.append({
                "term": term[:MAX_LEN],
                "count": count,
                "slug": (lane or {}).get("slug"),
                "lane_display": (lane or {}).get("lane_display"),
            })
    except (OSError, ValueError):
        rows = []
    with _lock:
        _cache.update(ts=now, rows=rows)
    return rows


def render_searches_section(rows: list[dict]) -> str:
    """The HTML block the /trending page renders under the movers table.
    Pure string build (the movers renderer is a plain f-string builder too).
    Rows are term aggregates only — nothing per-person exists to leak."""
    if not rows:
        return (
            '<section class="search-heat-sec" style="margin-top:26px;">'
            "<h2>🔥 What collectors searched</h2>"
            '<p style="color:#888;font-size:14px;">Quiet right now — recent '
            "searches will appear here as the community types them.</p>"
            "</section>"
        )
    items = []
    for r in rows:
        label = r["term"]
        if r.get("lane_display"):
            label += " · " + r["lane_display"]
        if r.get("slug"):
            items.append(
                f'<li><a href="/bands/{r["slug"]}">{_esc(label)}</a>'
                f' <span class="heat-n">({r["count"]} this fortnight)</span></li>'
            )
        else:
            items.append(
                f'<li>{_esc(label)}'
                f' <span class="heat-n">({r["count"]} this fortnight)</span>'
                f' <a class="heat-cta" href="/bands?q={_esc_url(r["term"])}">'
                "Build its page</a></li>"
            )
    return (
        '<section class="search-heat-sec" style="margin-top:26px;">'
        "<h2>🔥 What collectors searched</h2>"
        '<p style="color:#888;font-size:13px;">Aggregated community searches '
        "(term + count only — never who). A term's card page is one click "
        "away.</p>"
        f'<ol class="search-heat-list" style="line-height:1.9;padding-left:20px;">'
        + "".join(items) +
        "</ol></section>"
    )


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _esc_url(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote_plus(s or "")
