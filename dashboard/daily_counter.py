# UNIQUE DAILY COUNTER — a privacy-clean tracker for the landing page.
# Built Oct 23 night, founder-directed. One file, no cookies, no identity.
#
# WHAT COUNTS AS "UNIQUE": a day-bucketed hash of (visitor-IP-salt + day). Not reversible,
# not cross-day trackable, no cookie stored on the visitor's machine. The salt lives in
# .env (DAILY_COUNTER_SALT). Same visitor same day = 1 unique; same visitor next day = a
# new unique for that day. That is the honest definition of a daily-unique counter.
#
# STORAGE: data_lake/gold/daily_counters.json (append-only events + daily rollups).
# RENDER: the landing page reads today's count + yesterday's for a live "X people
# searched the hobby today" style stat — no identity, one number, community frame.
#
# PRIVACY DOCTRINE (aligned with P12/Never-list): count, never track. No IP stored,
# no return-visit stitching possible, nothing to sell — the disclosure stays true.

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from flask import request

_DAILY_LOCK = threading.Lock()


def _counter_state() -> tuple[Path, str]:
    """Ledger path + the day-key for 'now', Render-safe (env override wins)."""
    data_home = os.environ.get(
        "CARDSCOUT2_HOME", r"C:/Users/J/Documents/LLM/cardscout-2.0")
    path = Path(os.environ.get(
        "DAILY_COUNTER_PATH",
        str(Path(data_home) / "data_lake" / "gold" / "daily_unique.json")))
    return path, datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _env_val(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    if val is None:
        try:
            txt = (Path(__file__).resolve().parent.parent / ".env").read_text(
                encoding="utf-8", errors="ignore")
            import re
            m = re.search(rf"^\s*{re.escape(key)}\s*=\s*['\"]?([^\r\n'\"]+)", txt, re.M)
            val = m.group(1).strip() if m else ""
        except OSError:
            val = ""
    return val.strip()


def _unique_fingerprint_for_day(day: str) -> str:
    """privacy: day-salted hash. No IP, no UA, no cookie stored anywhere."""
    salt = _env_val("DAILY_COUNTER_SALT") or "cardscout-daily-v1"
    raw = request.headers.get("X-Forwarded-For", "") or request.remote_addr or "anon"
    return hashlib.sha256(f"{salt}|{day}|{raw}".encode()).hexdigest()[:16]


def register_landing_visit() -> dict:
    """Count today's visit if this day-fingerprint is new for today.
    Returns {'today': n, 'yesterday': m} for the render. Never raises."""
    try:
        path, day = _counter_state()  # day = today's YYYY-MM-DD key
        data = {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        day_rec = data.setdefault("days", {}).setdefault(day, {"uniques": [], "hits": 0})
        day_rec["hits"] += 1
        # unique fingerprint (privacy: day-salted hash of the remote address —
        # no IP persisted, no cross-day stitching, no cookie)
        fp = _unique_fingerprint_for_day(day)
        uq = set(day_rec.get("fps", []))
        day_rec["fps"] = sorted(uq | {fp})
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        y_count = data.get("days", {}).get(yesterday, {}).get("uniques", 0)
        tmp = path.with_suffix(".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        os.replace(tmp, path)
        return {"today": len(day_rec.get("fps", [])), "hits": day_rec["hits"],
                "yesterday": y_count}
    except Exception:
        return {"today": 0, "hits": 0, "yesterday": 0}


def read_daily_uniques() -> dict:
    """Read-side: today + 7-day total (no exceptions — the landing never hard-fails)."""
    try:
        path, day = _counter_state()
        data = json.loads(path.read_text(encoding="utf-8"))
        days = data.get("days", {})
        today = days.get(day, {})
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        wk = 0
        for i in range(7):
            d = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            wk += len((days.get(d, {}) or {}).get("fps", []))
        return {"today_uniques": len((days.get(day, {}) or {}).get("fps", [])),
                "yesterday_uniques": len((days.get(yesterday, {}) or {}).get("fps", [])),
                "week_uniques": wk, "today_hits": (days.get(day, {}) or {}).get("hits", 0)}
    except Exception:
        return {"today_uniques": 0, "yesterday_uniques": 0, "week_uniques": 0,
                "today_hits": 0}