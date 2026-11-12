"""
CAMEL FIRE-5 UNIT A — the price-history time-series chart on price pages.
Data source: tp_pulls.jsonl (the Terapeak 5AM daily pulls — dated prints: price +
sold_date + lane). Builds per-(player,lane) monthly-median series, cached to
pricehistory/*.json at generation time, read-only by the /price pages. The CHART
renders the shape (sparkline SVG, no $ numbers on the y-axis label — the honesty
law: shape public, numbers on the page remain the band's honest chips).
"""
from __future__ import annotations

import json
import os
import math
import statistics
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DASH_DIR = Path(__file__).resolve().parent
DL = Path(r"C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold")
# Render: env var wins; shipped data/tp_pulls.jsonl = the deploy fallback; local DL last.
_SHIPPED = DASH_DIR.parent / "data" / "tp_pulls.jsonl"
if os.environ.get("TP_PULLS_DIR"):
    _DL = Path(os.environ["TP_PULLS_DIR"])
elif _SHIPPED.exists():
    _DL = _SHIPPED.parent
else:
    _DL = DL
TP_PULLS = _DL / "tp_pulls.jsonl"
CACHE_DIR = DASH_DIR / "pricehistory"
CACHE_DIR.mkdir(exist_ok=True)
_LOCK = threading.Lock()

KNOWN = ['turang','chourio','mcgonigle','ohtani','yamamoto','misiorowski','messick',
         'schlittler','tolle','sasaki','skubal','judge','witt','wood','caminero',
         'arroyo','rice','neto','detmers','harper','tatis','verlander','schwarber',
         'arraez','scherzer','harris','alonso','sale']

def _who(title: str) -> str | None:
    t = title.lower()
    for n in KNOWN:
        if n in t:
            return n
    return None


def _slug_for(player: str, lane: str) -> str:
    return f"{player}-{lane}-{(lane or '').lower()}"


def build_series(force: bool = False) -> dict:
    """One pass over tp_pulls.jsonl → per (player_slug, lane) monthly medians.
    Cached to pricehistory/<player>__<lane>.json. Returns the index."""
    with _LOCK:
        idx_path = CACHE_DIR / "_index.json"
        if idx_path.exists() and not force:
            try:
                return json.loads(idx_path.read_text(encoding="utf-8"))
            except ValueError:
                pass
        if not TP_PULLS.exists():
            idx_path.write_text("{}", encoding="utf-8")
            return {}
        series = defaultdict(lambda: defaultdict(list))  # (player,lane) -> month -> [prices]
        with open(TP_PULLS, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                pl = _who(j.get("title", ""))
                if not pl:
                    continue
                d, p = j.get("sold_date"), j.get("price")
                if not d or not isinstance(p, (int, float)):
                    continue
                try:
                    dt = datetime.strptime(d, "%b %d, %Y")
                except ValueError:
                    continue
                series[(pl, j.get("lane", "base"))][f"{dt.year}-{dt.month:02d}"].append(float(p))
        index = {}
        def _fname(player: str, lane: str) -> str:
            safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in lane.lower())
            return f"{player}__{safe}.json"
        for (pl, lane), months in series.items():
            pts = []
            for m, prices in sorted(months.items()):
                pts.append({"m": m, "med": round(statistics.median(prices), 2), "n": len(prices)})
            fname = _fname(pl, lane)
            (CACHE_DIR / fname).write_text(json.dumps(pts), encoding="utf-8")
            index[f"{pl}::{lane}"] = fname
        idx_path.write_text(json.dumps(index), encoding="utf-8")
        return index


def series_for_player_lane(player: str | None, lane_display: str | None,
                           player_slug: str | None = None) -> list[dict]:
    """Load the cached series for a page's (player, lane). Falls back to the
    player's ANY-lane series if the exact lane is absent (honest partial)."""
    idx = build_series()
    # exact match attempt: player+lane_display token match
    lane_key = (lane_display or "").lower().replace(" ", "-")
    p = (player or "").lower().split()[-1]  # surname
    for key, fname in idx.items():
        kp, kl = key.split("::")
        if kp == p and kl == lane_key:
            try:
                return json.loads((CACHE_DIR / fname).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
    # fallback: the player's median across lanes (monthly) — honest partial view
    per_month = defaultdict(list)
    for key, fname in idx.items():
        kp, _kl = key.split("::")
        if kp == p:
            try:
                for pt in json.loads((CACHE_DIR / fname).read_text(encoding="utf-8")):
                    per_month[pt["m"]].append(pt["med"])
            except (OSError, ValueError):
                pass
    if not per_month:
        return []
    return [{"m": m, "med": round(statistics.median(v), 2), "n": len(v)}
            for m, v in sorted(per_month.items())]


def sparkline_svg(pts: list[dict], width: int = 560, height: int = 120) -> str:
    """Render an honest sparkline of the monthly-median shape. NO dollar labels —
    the chart shows the SHAPE of the market's record; numbers stay off the axis
    to honor the tools-not-opinions / public-shape-only law."""
    if not pts or len(pts) < 2:
        return ""  # 1 point = no shape = no line (honest)
    meds = [p["med"] for p in pts]
    lo, hi = min(meds), max(meds)
    rng = (hi - lo) or 1.0
    step = (width - 20) / (len(pts) - 1)
    coords = []
    for i, p in enumerate(pts):
        x = 10 + i * step
        y = height - 10 - ((p["med"] - lo) / rng) * (height - 20)
        coords.append((round(x, 1), round(y, 1)))
    poly = " ".join(f"{x},{y}" for x, y in coords)
    first_month, last_month = pts[0]["m"], pts[-1]["m"]
    n_total = sum(p["n"] for p in pts)
    return (
        f'<svg viewBox="0 0 {width} {height}" class="ts-spark" role="img" '
        f'aria-label="price trend from {first_month} to {last_month}, {n_total} records">'
        f'<polyline fill="none" stroke="#e8a44c" stroke-width="1.6" points="{poly}"/>'
        f'<text x="10" y="{height - 1}" font-size="9" fill="#888">{first_month}</text>'
        f'<text x="{width - 62}" y="{height - 1}" font-size="9" fill="#888">{last_month} · {n_total} records</text>'
        f'</svg>'
    )
