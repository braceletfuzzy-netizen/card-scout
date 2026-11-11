"""
CAMEL FIRE-3 UNIT B — saved searches + deal-parsing (user-owned constraints).
The user defines players/lanes/price-levels; the parser runs over the one-way
registry feed (same source as the price pages) and returns matches. TOOLING
layer: the user's constraints, our execution. No engine vocabulary, no advice.
Storage = part of their own user file (saved_searches key) — same multi-tenant
pattern as watchlists (Fire-2). Sends: none (a digest email = future opt-in,
still behind the founder flag).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

DASH_DIR = Path(__file__).resolve().parent


def _registry() -> dict:
    try:
        return json.loads((DASH_DIR / "registry" / "card_page_registry.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"lanes": [], "slug_aliases": {}}


def normalize(v: str) -> str:
    return (v or "").strip().lower()


def add_saved(email: str, name: str, player_q: str = "", lane_q: str = "",
              grade_q: str = "", max_price: float | None = None,
              min_price: float | None = None) -> dict:
    """Add a saved search to the user's own file. Max 20 saved searches/user."""
    import user_state as US
    data = US.load_user(email)
    saved = data.setdefault("saved_searches", [])
    if len(saved) >= 20:
        return {"ok": False, "error": "saved-search limit reached (20)"}
    row = {
        "id": f"ss-{len(saved)+1}-{__import__('hashlib').sha1((name+player_q+lane_q+str(max_price)).encode()).hexdigest()[:8]}",
        "name": (name or "").strip()[:60] or "search",
        "player_q": player_q.strip().lower(),
        "lane_q": lane_q.strip().lower(),
        "grade_q": grade_q.strip().lower(),
        "max_price": max_price,
        "min_price": min_price,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    saved.append(row)
    US.save_user(email, data)
    return {"ok": True, "saved": row}


def remove_saved(email: str, sid: str) -> dict:
    import user_state as US
    data = US.load_user(email)
    before = len(data.get("saved_searches", []))
    data["saved_searches"] = [s for s in data.get("saved_searches", []) if s.get("id") != sid]
    removed = before - len(data["saved_searches"])
    US.save_user(email, data)
    return {"ok": removed > 0, "removed": removed}


def run_saved(email: str, sid: str) -> dict:
    """Execute one saved search against the registry. Returns matched lanes with
    their honest band class (FORMING rows report not-yet-priced — no fabrication)."""
    import user_state as US
    data = US.load_user(email)
    row = next((s for s in data.get("saved_searches", []) if s.get("id") == sid), None)
    if not row:
        return {"ok": False, "error": "unknown search", "matches": []}
    reg = _registry()
    matches = []
    for L in reg.get("lanes", []):
        band = L.get("band")
        if not (isinstance(band, dict) and isinstance(band.get("median"), (int, float))):
            continue  # forming/unpriced lanes skip numeric matching (honest class)
        if row["player_q"] and row["player_q"] not in normalize(L.get("player", "")):
            continue
        if row["lane_q"] and row["lane_q"] not in normalize(L.get("lane_display", "") + " " + normalize(L.get("lane", ""))):
            continue
        if row["grade_q"] and row["grade_q"] not in normalize(L.get("grade_bucket", "")):
            continue
        med = band["median"]
        if row["max_price"] is not None and med > row["max_price"]:
            continue
        if row["min_price"] is not None and med < row["min_price"]:
            continue
        matches.append({
            "player": L.get("player"), "player_slug": L.get("player_slug"),
            "slug": L["slug"], "lane_display": L.get("lane_display"),
            "grade": L.get("grade_bucket"), "class": L.get("band_class", ""),
            "median": med,
        })
    return {"ok": True, "search_id": sid, "matches": matches[:50]}
