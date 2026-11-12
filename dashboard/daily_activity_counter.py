"""Card Scout — McDonalds-style DAILY COUNTER (ADDENDUM 2, Nov 12 2026).

Brief: Temp/hermes_brief_aggregate_tag.md §ADDENDUM-2.
One honest integer per day. Nothing else. No cookies, no fingerprints, no IPs,
no third parties — the stored payload contains ONLY {date: count} pairs.

DIFFERENCE vs daily_counter.py (the Oct-23 landing counter): that module keeps
per-day fingerprint lists (fps) + hit counters — still anonymous, but it stores
more than {date:count}. The addendum's acceptance law is stricter:
  "the stored data contains ONLY {date: count} pairs; zero cookies set."
So this module is a separate store (data/daily_activity.json) holding exactly:
  {"2026-11-12": 47, "2026-11-11": 123, ...}   # rolling 90 days, nothing more

WHAT COUNTS: +1 per qualifying server-side request — homepage or /bands index
or /bands/<slug> band view. Reset at midnight CT (America/Chicago) because the
founder's day is CT; the day key is today's CT date string, so the counter
rolls over at CT midnight naturally.

DISPLAY: 'TODAY: N SEARCHES BUILT BANDS' — shown in the /bands footer + landing
stat. Optional cumulative line ('N BANDS-BUILT TOTAL' = sum over the window +
the pre-counter baseline constant, kept private — see BASELINE below).

No customer path to per-day history: the JSON is never rendered; only today's
scalar (and the cumulative total) ever reaches HTML.

Zero cookies: this module reads nothing from request.cookies and sets nothing.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

_CT = ZoneInfo("America/Chicago")
_LOCK = threading.Lock()
ROLLING_DAYS = 90

# Founder's private baseline (bands built before this counter existed, for the
# optional 'total' line). Lives here, server-side only, never rendered raw.
_BASELINE_BANDS_BUILT = 757  # the lane catalog, the honest floor

try:
    _DATA_DIR = Path(os.environ.get("LISTING_CACHE_DIR", "")).parent if os.environ.get("LISTING_CACHE_DIR") else None
except Exception:
    _DATA_DIR = None


def store_path() -> Path:
    """Counter home: repo-local data/ (Render: LISTING_CACHE_DIR's parent)."""
    if os.environ.get("DAILY_ACTIVITY_PATH"):
        return Path(os.environ["DAILY_ACTIVITY_PATH"])
    base = _DATA_DIR
    if base is None:
        base = Path(__file__).resolve().parent.parent / "data"
    return Path(base) / "daily_activity.json"


def today_key_ct() -> str:
    """Today's date string in CT — the day key. Resets midnight CT."""
    return datetime.now(_CT).strftime("%Y-%m-%d")


def _load() -> dict:
    """Read {date: count}; drop anything older than the 90-day window."""
    try:
        data = json.loads(store_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    clean = {}
    cutoff = (datetime.now(_CT) - timedelta(days=ROLLING_DAYS)).strftime("%Y-%m-%d")
    for k, v in data.items():
        # strict acceptance law: ONLY {date: count} pairs survive
        if isinstance(k, str) and len(k) == 10 and k[4] == "-" and k[7] == "-" and isinstance(v, int):
            if k >= cutoff:
                clean[k] = v
    return clean


def _save(data: dict) -> None:
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, sort_keys=True)
    os.replace(tmp, path)


def bump() -> dict:
    """+1 for today (CT). Returns {'today': n, 'total': sum}. Never raises."""
    try:
        day = today_key_ct()
        with _LOCK:
            data = _load()
            data[day] = int(data.get(day, 0)) + 1
            _save(data)
            return {"today": data[day], "total": sum(data.values())}
    except Exception:
        return {"today": 0, "total": 0}


def read_today() -> dict:
    """Read-side for footers: today + optional cumulative line. Never raises."""
    try:
        with _LOCK:
            data = _load()
        day = today_key_ct()
        today = int(data.get(day, 0))
        total = sum(data.values()) + _BASELINE_BANDS_BUILT
        return {"today": today, "total": total}
    except Exception:
        return {"today": 0, "total": _BASELINE_BANDS_BUILT}


def acceptance_snapshot() -> dict:
    """Verifier hook: returns the stored payload (must be ONLY {date: count})."""
    try:
        return _load()
    except Exception:
        return {}
