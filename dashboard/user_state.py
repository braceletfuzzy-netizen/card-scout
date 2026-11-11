"""
PUBLIC USER STATE — CAMEL FIRE-2 (Nov 11, 2026) — the stateful unit (Hugo lane)

Spec: cardscout-2.0/For You/Plans/2026-11-11-camel-fire2-brief-hugo.md
Wires state into the Fire-1.5 render shells (user_bp.py templates unchanged):
- Google auth for public users (reuses the verified /admin/login/google OAuth
  pattern; separate session keys; separate storage under dashboard/users/)
- Multi-tenant watchlists: per-user JSON at users/<email-hash>/watchlist.json
  (email-hash folder; the user's own email inside their file; no cross-user reads)
- User-owned prices (SS227.2 pattern): trigger_low / trigger_high are THE USER'S
  levels — we execute, never advise
- Alert parametrization: watchlist → would-be alert JSON, SEND HARD-LOCKED
  (dry-run default; PUBLIC_USER_ALERTS_ENABLED founder-flag gates sends)

LAWS carried:
- User-owned data: stored in the user's own file; never rendered for another user.
- No engine vocabulary on user-visible surfaces; no band $ numbers as text.
- Honest-empty everywhere; no invented rows; malformed storage = fresh blank list.
- Secrets read-in-place from env; never echoed.
- Storage is dependency-free (JSON files; no new deps; sqlite reserved for the
  existing customer DB only — public users live OUTSIDE the customer database).
- Builders-add: user_bp.py/app.py additions are additive; nothing existing modified.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import threading
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint, redirect, render_template_string, request, session,
    url_for, jsonify,
)

DASH_DIR = Path(__file__).resolve().parent
USERS_DIR = DASH_DIR / "users"
USERS_DIR.mkdir(exist_ok=True)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# PUBLIC_USERS_MODE: open | allowlist (default allowlist = safe first)
PUBLIC_USERS_MODE = os.environ.get("PUBLIC_USERS_MODE", "allowlist").strip().lower()
if PUBLIC_USERS_MODE not in ("open", "allowlist"):
    PUBLIC_USERS_MODE = "allowlist"


def _email_hash(email: str) -> str:
    """Folder key: sha256(email)[:16]. Plain emails NEVER in folder names."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()[:16]


def _user_file(email: str) -> Path:
    return USERS_DIR / f"{_email_hash(email)}.json"


def _rostered(email: str) -> bool:
    """Allowlist mode: the founder-curated CONTRIBUTOR_EMAILS roster governs."""
    if PUBLIC_USERS_MODE != "allowlist":
        return True
    roster = (os.environ.get("CONTRIBUTOR_EMAILS") or "").strip()
    if not roster:
        return False
    return {e.strip().lower() for e in roster.split(",") if e.strip()}.__contains__(email.strip().lower())


_USER_LOCK = threading.Lock()


def load_user(email: str) -> dict:
    """Read the user's own storage file. Never raises; missing/corrupt = fresh."""
    f = _user_file(email)
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("email") != email.strip().lower():
            return {"email": email.strip().lower(), "watchlist": [], "created_utc": None}
        data.setdefault("watchlist", [])
        if not isinstance(data["watchlist"], list):
            data["watchlist"] = []
        return data
    except (OSError, ValueError):
        return {"email": email.strip().lower(), "watchlist": [], "created_utc": None}


def save_user(email: str, data: dict) -> None:
    """Atomic write of the user's own file (tmp + replace under the lock)."""
    email = email.strip().lower()
    data["email"] = email
    data.setdefault("created_utc", datetime.now(timezone.utc).isoformat())
    data["updated_utc"] = datetime.now(timezone.utc).isoformat()
    f = _user_file(email)
    with _USER_LOCK:
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
        tmp.replace(f)


def normalize_slug(v: str) -> str:
    return unicodedata.normalize("NFKC", v or "").strip()


# ---------------------------------------------------------------------------
# OAUTH (public-user variant of the admin google pattern — additive; own
# session keys; separate callback; never reuses admin's session state keys)
# ---------------------------------------------------------------------------

oauth_bp = Blueprint("user_oauth", __name__, url_prefix="/me")


@oauth_bp.route("/login")
def me_login_redirect():
    """Replaces the Fire-1.5 static explainer with the real Google handoff
    (render-only shells stay as the fallback when Google isn't configured)."""
    if not GOOGLE_CLIENT_ID:
        from public_price_bp import BASE_CSS  # same styling family
        return render_template_string(_LOGIN_FALLBACK), 200
    try:
        from requests_oauthlib import OAuth2Session
        provider_cfg = __import__("requests").get(GOOGLE_DISCOVERY_URL, timeout=15).json()
        oauth = OAuth2Session(
            GOOGLE_CLIENT_ID,
            redirect_uri=request.url_root + "me/login/callback",
            scope=["openid", "email", "profile"],
        )
        authorization_url, state = oauth.authorization_url(provider_cfg["authorization_endpoint"])
        session["user_oauth_state"] = state
        return redirect(authorization_url)
    except Exception:
        return redirect(url_for("user.user_home"))


@oauth_bp.route("/login/callback")
def me_login_callback():
    if "user_oauth_state" not in session:
        return redirect(url_for("user.user_home"))
    import requests as _requests
    from requests_oauthlib import OAuth2Session
    try:
        provider_cfg = _requests.get(GOOGLE_DISCOVERY_URL, timeout=15).json()
        oauth = OAuth2Session(GOOGLE_CLIENT_ID, state=session["user_oauth_state"],
                              redirect_uri=request.url_root + "me/login/callback")
        oauth.fetch_token(provider_cfg["token_endpoint"],
                          authorization_response=request.url,
                          client_secret=GOOGLE_CLIENT_SECRET)
        user_info = oauth.get(provider_cfg["userinfo_endpoint"]).json()
        email = (user_info.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return redirect(url_for("user.user_home"))
        if not _rostered(email):
            # allowlist mode: not rostered -> redirect to bands, zero interior render
            return redirect("/bands")
        session.clear()
        # SEPARATE session keys from the admin/customer surface (user_email only)
        session["user_email"] = email
        session.permanent = True
        return redirect(url_for("user.user_home"))
    except Exception:
        return redirect(url_for("user.user_home"))


@oauth_bp.route("/logout")
def me_logout():
    session.pop("user_email", None)
    return redirect(url_for("user.user_home"))


def _current_user():
    email = session.get("user_email")
    if not email:
        return None
    return email


# ---------------------------------------------------------------------------
# WATCHLIST API (multi-tenant; the user's own file only)
# ---------------------------------------------------------------------------

def _registry_lane(lane_slug: str):
    """Look a lane up in the one-way registry feed (same source as /price pages).
    Read-only; aliases resolved via the registry's slug_aliases if present."""
    try:
        data = json.loads((DASH_DIR / "registry" / "card_page_registry.json").read_text(encoding="utf-8"))
        for L in data.get("lanes", []):
            if L.get("slug") == lane_slug:
                return L
        # alias pass
        alias = data.get("slug_aliases", {})
        target = alias.get(lane_slug)
        if target:
            for L in data.get("lanes", []):
                if L.get("slug") == target:
                    return L
    except (OSError, ValueError):
        pass
    return None


def _price_float(v):
    try:
        f = float(v)
        if f > 0:
            return round(f, 2)
    except (TypeError, ValueError):
        pass
    return None


@oauth_bp.route("/watchlist", methods=["GET", "POST"])
def user_watchlist():
    email = _current_user()
    if not email:
        return redirect(url_for("user.me_home"))

    if request.method == "POST":
        action = normalize_slug(request.form.get("action") or request.json.get("action") if request.is_json else request.form.get("action")) if True else ""
        # support both form and JSON
        payload = request.get_json(silent=True) or request.form
        data = load_user(email)
        wl = data["watchlist"]

        if payload.get("action") == "add":
            lane_slug = normalize_slug(payload.get("lane_slug") or "")
            lane = _registry_lane(lane_slug)
            if not lane:
                return jsonify({"ok": False, "error": "unknown card"}), 404
            low = _price_float(payload.get("trigger_low"))
            high = _price_float(payload.get("trigger_high"))
            if low is None and high is None:
                return jsonify({"ok": False, "error": "set at least one of your prices"}), 400
            if any(r.get("lane_slug") == lane_slug for r in wl):
                for r in wl:
                    if r["lane_slug"] == lane_slug:
                        r["trigger_low"] = low
                        r["trigger_high"] = high
            else:
                wl.append({
                    "player_slug": normalize_slug(payload.get("player_slug") or lane.get("player_slug", "")),
                    "lane_slug": lane["slug"],
                    "player": lane.get("player", ""),
                    "lane_display": lane.get("lane_display", ""),
                    "product": lane.get("product", ""),
                    "trigger_low": low,
                    "trigger_high": high,
                    "added_utc": datetime.now(timezone.utc).isoformat(),
                })
            save_user(email, data)
            return jsonify({"ok": True, "count": len(wl)})

        if payload.get("action") == "update":
            lane_slug = normalize_slug(payload.get("lane_slug") or "")
            low = _price_float(payload.get("trigger_low"))
            high = _price_float(payload.get("trigger_high"))
            for r in wl:
                if r.get("lane_slug") == lane_slug:
                    r["trigger_low"] = low
                    r["trigger_high"] = high
                    r["updated_utc"] = datetime.now(timezone.utc).isoformat()
            save_user(email, data)
            return jsonify({"ok": True, "count": len(wl)})

        if payload.get("action") == "remove":
            lane_slug = normalize_slug(payload.get("lane_slug") or "")
            data["watchlist"] = [r for r in wl if r.get("lane_slug") != lane_slug]
            save_user(email, data)
            return jsonify({"ok": True, "count": len(data["watchlist"])})

        return jsonify({"ok": False, "error": "unknown action"}), 400

    # GET: the user's own list, joined with display info from their file
    data = load_user(email)
    return jsonify({
        "ok": True,
        "email_domain": email.split("@")[-1],
        "rows": data["watchlist"],
    })


# ---------------------------------------------------------------------------
# WOULD-BE ALERT RENDER (dry-run HARD-LOCKED; sends require the founder flag)
# ---------------------------------------------------------------------------

def compute_alerts(email: str) -> list[dict]:
    """Pure computation: the user's rows vs the registry feed's band/deal data.
    Returns the would-be alert rows (the TOOLING layer, user-owned prices).
    NEVER sends. Public surface renders these as 'watching' status only."""
    data = load_user(email)
    try:
        reg = json.loads((DASH_DIR / "registry" / "card_page_registry.json").read_text(encoding="utf-8"))
        by_slug = {L.get("slug"): L for L in reg.get("lanes", [])}
        alias = reg.get("slug_aliases", {})
    except (OSError, ValueError):
        by_slug, alias = {}, {}
    out = []
    for r in data.get("watchlist", []):
        slug = r.get("lane_slug")
        lane = by_slug.get(slug) or by_slug.get(alias.get(slug, ""))
        if not lane:
            out.append({**r, "status": "watching", "hit_now": False})
            continue
        band = lane.get("band") or {}
        low = band.get("low")
        rows = []
        hit = False
        if r.get("trigger_low") is not None and isinstance(low, (int, float)) and low <= r["trigger_low"]:
            hit = True
        if r.get("trigger_high") is not None:
            high = band.get("high")
            if isinstance(high, (int, float)) and high >= r["trigger_high"]:
                hit = True
        out.append({**r, "status": ("AT YOUR PRICE" if hit else "watching"), "hit_now": hit})
    return out


def build_alert_payload(email: str) -> dict | None:
    """The parametrized alert the email engine would render/send for this user.
    Return None when nothing qualifies (honest-empty contract)."""
    rows = [r for r in compute_alerts(email) if r.get("hit_now")]
    if not rows:
        return None
    return {
        "email_domain": email.split("@")[-1],
        "rows": [{"player": r.get("player", ""), "lane": r.get("lane_display", ""),
                  "your_price_low": r.get("trigger_low"), "your_price_high": r.get("trigger_high")}
                 for r in rows],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
