"""band_graph.py — BRIEF 2 ADDITIONAL: price-history graph with
search-granularity-selected default window (Nov 12, 2026).

Founder contract:
- Every band page gets a price-history graph; the DEFAULT window is selected
  by lane granularity:
    coarse lane (player+product, e.g. 'brice turang topps')  -> 30d
    deep lane (player+product+variant+grade)                 -> 7d
  A 7d / 30d / 90d toggle overrides the default (?w= query param).
- DATA SOURCES in priority order:
    1. our own tp_pulls time-series (price_timeseries.py; ~716 dated prints,
       monthly medians -> used for 90d view when it covers the window)
    2. Card Hedge player-index-history (1830 days at cardhedger.com/v1/
       cards/player-index-history; per-point {date, value}) -> 7d/30d points
    3. hidden honest ("not enough history yet") — never a fake axis.
- Rendered server-side as lightweight INLINE SVG (no third-party JS, no
  <script src> trackers — the privacy law holds). $ labels stay OFF the axis
  (shape public; the honesty law from the sparkline lives).

Cache law: CH history cached per player (jsonl, 24h TTL, same style as
aggregate_lanes) so page renders never re-burn API. Every failure degrades
to source 2 then 3, never a crash.
"""
from __future__ import annotations

import json
import re
import threading
import time
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
AGG_DIR = Path(r"C:/Users/J/Documents/LLM/card-scout/data/aggregate_lanes")

WINDOWS = (7, 30, 90)

# granularity: a lane is DEEP when it carries a variant/grade token beyond
# player+product (grade_bucket != raw OR the lane slug has a variant token
# like chrome/wave/refractor). Registry grade buckets are authoritative.
def deep_lane(grade_bucket: str | None, lane_display: str | None) -> bool:
    gb = (grade_bucket or "raw").strip().lower()
    if gb not in ("raw", "", "none"):
        return True                        # graded lane = deepest granularity
    # raw lane with a variant-ish display token (wave, refractor, numbered…)
    toks = [t for t in re.split(r"[-_ ]+", (lane_display or "").lower()) if t]
    return any(t in ("wave", "refractor", "numbered", "sapphire", "black", "orange",
                     "purple", "gold", "blue", "green", "red", "case-hit", "iv")
               for t in toks)


def default_window(grade_bucket: str | None, lane_display: str | None) -> int:
    return 7 if deep_lane(grade_bucket, lane_display) else 30


# ---------------------------------------------------------------------------
# Source 2 cache: CH player-index-history per player (24h TTL)
# ---------------------------------------------------------------------------
_HIST_TTL_SEC = 86400
_hist_lock = threading.Lock()


def _hist_path(player: str) -> Path:
    safe = re.sub(r"[^a-z0-9-]", "-", (player or "").lower()).strip("-") or "_x"
    AGG_DIR.mkdir(parents=True, exist_ok=True)
    return AGG_DIR / f"indexhist_{safe}.json"


def _load_client():
    try:                                   # reuse the deployed CH client
        import sys
        sys_path = str(REPO_DIR / "scripts")
        if sys_path not in __import__("sys").path:
            __import__("sys").path.insert(0, sys_path)
        from cardhedger_client import CardHedgerClient  # noqa: E402
        import os
        os.environ.setdefault(
            "CARD_HEDGER_API_KEY",
            "file:C:/Users/J/.secrets/card-scout/card-hedger-api-key.txt")
        return CardHedgerClient()
    except Exception:
        return None


def index_history(player: str, days: int = 90) -> list[dict]:
    """[{date, value}] for the window, CH index-history, cache-first. NEVER
    raises; [] = no series (source 3 honest-hide)."""
    days = max(1, min(int(days), 366))     # API clamps at 366; we show <=90
    cache = _hist_path(player)
    now = time.time()
    with _hist_lock:
        try:
            if cache.exists():
                row = json.loads(cache.read_text(encoding="utf-8"))
                if now - float(row.get("ts") or 0) < _HIST_TTL_SEC:
                    pts = row.get("points") or []
                    if pts:
                        # window-reslice from the cached 366
                        return pts[-days:]
        except (OSError, ValueError):
            pass
        client = _load_client()
        if not client:
            return []
        try:
            resp = client.session.post(
                "https://api.cardhedger.com/v1/cards/player-index-history",
                json={"name": player}, timeout=20)
            if resp.status_code != 200:
                return []
            data = resp.json()
            pts = [{"date": p.get("date"), "value": float(p.get("value") or 0)}
                   for p in (data.get("points") or [])
                   if p.get("date") and p.get("value") and float(p.get("value")) > 0]
            pts = [p for p in pts if p["value"] > 0]
            if not pts:
                return []
            try:
                cache.write_text(json.dumps({"ts": now, "points": pts}), encoding="utf-8")
            except OSError:
                pass
            return pts[-days:]
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Source 1: own tp_pulls via the existing price_timeseries module
# ---------------------------------------------------------------------------
def own_series(player: str | None, lane_display: str | None,
               player_slug: str | None = None) -> list[dict]:
    """Monthly medians [{m, med, n}] from tp_pulls (or []). Never raises."""
    try:
        import price_timeseries as ts  # the deployed module
        return ts.series_for_player_lane(player, lane_display, player_slug)
    except Exception:
        return []


def own_series_recent(pts: list[dict], days: int) -> list[dict]:
    """Approximate a d-window from monthly medians: keep the trailing ~
    (days/30 ceil) months, minimum 2 points to have a shape."""
    if not pts:
        return []
    keep = max(2, (days + 29) // 30)
    return pts[-keep:]


# ---------------------------------------------------------------------------
# SVG (inline; no dollar labels; no external JS)
# ---------------------------------------------------------------------------
def line_svg(pts: list[dict], width: int = 640, height: int = 150,
             label_left: str = "", label_right: str = "") -> str:
    """Honest line chart of a [{x: date-or-month, y: value}] series."""
    if len(pts) < 2:
        return ""
    ys = [p["y"] for p in pts]
    lo, hi = min(ys), max(ys)
    rng = (hi - lo) or 1.0
    step = (width - 24) / (len(pts) - 1)
    coords = []
    for i, p in enumerate(pts):
        x = 12 + i * step
        y = height - 18 - ((p["y"] - lo) / rng) * (height - 30)
        coords.append((round(x, 1), round(y, 1)))
    poly = " ".join(f"{x},{y}" for x, y in coords)
    last = pts[-1]
    dot_x, dot_y = coords[-1]
    return (
        f'<svg viewBox="0 0 {width} {height}" class="band-graph" role="img" '
        f'aria-label="price history shape, {len(pts)} points">'
        f'<polyline fill="none" stroke="#2563eb" stroke-width="1.8" points="{poly}"/>'
        f'<circle cx="{dot_x}" cy="{dot_y}" r="3" fill="#2563eb"/>'
        f'<text x="12" y="{height - 3}" font-size="10" fill="#9ca3af">{label_left}</text>'
        f'<text x="{width - 12}" y="{height - 3}" font-size="10" fill="#9ca3af" '
        f'text-anchor="end">{label_right}</text>'
        f"</svg>"
    )


def build_graph(lane: dict, window: int | None = None) -> dict:
    """The renderer's bundle: {'svg', 'window', 'windows', 'source', 'points'}.

    Priority: own tp_pulls series -> CH index-history -> {'svg': ''} honest
    hide. window=None = granularity default. NEVER raises.
    """
    gb = lane.get("grade_bucket")
    ld = lane.get("lane_display") or lane.get("lane")
    w = int(window) if window in WINDOWS else default_window(gb, ld)
    out = {"window": w, "windows": WINDOWS, "svg": "", "source": "", "points": []}
    try:
        # 1) our own prints (only meaningful with enough of them in window)
        pts = own_series_recent(
            own_series(lane.get("player"), ld, lane.get("player_slug")), w)
        if len(pts) >= 2:
            out["svg"] = line_svg(
                [{"x": p["m"], "y": p["med"]} for p in pts],
                label_left=pts[0]["m"],
                label_right=f"{pts[-1]['m']} · {sum(p['n'] for p in pts)} prints",
            )
            out["source"] = "tp_pulls"
            out["points"] = [{"x": p["m"], "y": p["med"]} for p in pts]
            return out
        # 2) CH player index history
        ch = index_history(lane.get("player") or "", days=w)
        if len(ch) >= 2:
            out["svg"] = line_svg(
                [{"x": p["date"], "y": p["value"]} for p in ch],
                label_left=ch[0]["date"],
                label_right=ch[-1]["date"] + " · CH player index",
            )
            out["source"] = "ch_index"
            out["points"] = [{"x": p["date"], "y": p["value"]} for p in ch]
            return out
    except Exception:
        pass
    return out  # 3) honest hide
