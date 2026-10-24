"""
CardScout CONTRIBUTOR WORKSPACE (paste → parse → reward) — Oct 23, 2026.

Brief: cardscout-2.0/For You/Plans/2026-10-23-walle-brief-contributor-workspace.md
Parent spec: 2026-10-22-CARD-PAGE-BUILD-SPEC-v1.md. Builder: WALL-E. Verifier: Hermes.

BANKED SHAPE (brief §AUTH revised Oct 23 AM — founder correction):
- Auth = Google OAuth2 (the /admin/login/google pattern in app.py), attribution to
  the PERSON (email), not a token. No account/passwords created.
- Roster gate: email must be in .env CONTRIBUTOR_EMAILS (founder-curated list,
  config-not-hardcode). Any other Google email -> clean redirect to /bands,
  zero interior render (P9).
- LOCAL-ONLY PHASE 1 (founder call at brief review): this surface is private;
  NEVER published, robots-disallowed, no public links.

THE LOOP (§ paste → reward):
  1 PASTE (textarea, ~200KB cap) -> 2 PARSE (standard funnel, lane-split,
  print/ask gate per Two-Class law — asks excluded with counted causes, never
  silent) -> 3 REWARD RENDER (their paste's distribution; the lane-refined
  before/after as a WIDTH-DELTA PERCENTAGE + credit line — band $ values never
  render per public law; BIN-sorted listings via the band_pages cache-law path;
  grade-state after contribution; ledger tick) -> 4 THANKS + ONE refinement tip.

BOUNDS honored here:
- NEVER publish anything from this workspace (one-way private; no index).
- NEVER leak positions/engine output/z-scores/band $ numbers in the reward render.
- NEVER send Discord/email push from this surface.
- NEVER break on parse failure: honest-200 error page with the counted cause (P10e).
- PII: ledger keys on GOOGLE EMAIL (person-attribution, founder-directed); name
  + email + counts + lanes only; deposit FILES keyed on anonymized contributor id.
- Google-info disclosure + the three no-advice/user-agency clauses render on the
  login view (expandable) and as the standing footer line (P12).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, redirect, render_template_string, request, session, url_for

# Band-pages machinery = the ONLY listings path (cache law + EPN gate inherited
# from the already-verified module — no duplicate implementation).
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import band_pages as BP  # noqa: E402

bp = Blueprint("contrib", __name__, url_prefix="/contributor")
# Prefix-less sibling for the PUBLIC CAN-SPAM endpoints (brief 3 Job 4: the
# email footer links to /unsubscribe — root, no auth, robots-disallowed)
unsub_bp = Blueprint("contrib_unsub", __name__)

DASH_DIR = Path(__file__).resolve().parent
REPO_DIR = DASH_DIR.parent
SITE_ENV = REPO_DIR / ".env"

# Contributor corpus lives in the 2.0 data lake (this is a same-machine Phase 1
# surface; on a future Render deploy this must move to the service's own disk —
# documented in the brief's STATUS note).
TWO_REPO = Path(os.environ.get(
    "CARDSCOUT2_HOME", r"C:/Users/J/Documents/LLM/cardscout-2.0"))
DEPOSITS_DIR = Path(os.environ.get(
    "CONTRIBUTOR_DEPOSITS_DIR", TWO_REPO / "data_lake" / "raw" / "contributor"))
LEDGER_PATH = Path(os.environ.get(
    "CONTRIBUTOR_LEDGER_PATH", TWO_REPO / "data_lake" / "contributor_ledger.json"))

# Brief 3 (§227): seller-watch LEDGER (append-only; the alert-side reversal is a
# LATER cycle — nothing reads this file yet besides its own append discipline)
SELLER_WATCH_PATH = Path(os.environ.get(
    "SELLER_WATCH_PATH", TWO_REPO / "data_lake" / "gold" / "seller_watch_registry.json"))

PASTE_MAX_CHARS = 200_000  # brief: ~200KB cap

# ---------------------------------------------------------------------------
# ENV (.env read-in-place; values never rendered or logged)
# ---------------------------------------------------------------------------
_env_lock = threading.Lock()
_env_cache: dict[str, str] = {}
_env_read_at = 0.0


def env_file_val(key: str, ttl: float = 600.0) -> str | None:
    """Read a key from the site .env (same pattern as band_pages.py)."""
    global _env_cache, _env_read_at
    now = time.time()
    with _env_lock:
        if now - _env_read_at > ttl:
            try:
                txt = SITE_ENV.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                txt = ""
            _env_cache = dict(re.findall(
                r"^\s*([A-Z_][A-Z0-9_]*)\s*=\s*['\"]?([^'\r\n]*)", txt, re.M))
            _env_read_at = now
        v = os.environ.get(key)
        if v not in (None, ""):
            return v.strip()
        v = (_env_cache.get(key) or "").strip()
        return v or None


def contributor_roster() -> list[str]:
    raw = env_file_val("CONTRIBUTOR_EMAILS") or ""
    return [e.strip().lower() for e in re.split(r"[,;\s]+", raw) if e.strip()]


def is_on_roster(email: str | None) -> bool:
    return bool(email) and email.strip().lower() in set(contributor_roster())


def google_client_id() -> str | None:
    return env_file_val("GOOGLE_CLIENT_ID")


# ---------------------------------------------------------------------------
# GOOGLE OAUTH2 (same flow as app.py's admin login, own namespace/keys)
# ---------------------------------------------------------------------------
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def _finish_login(user_info: dict) -> str:
    """Shared roster gate: on-roster -> interior; else redirect /bands (P9)."""
    email = (user_info.get("email") or "").strip().lower()
    if not email:
        return redirect(url_for("contrib.login"))
    if is_on_roster(email):
        session.clear()
        session["contributor_email"] = email
        session["contributor_name"] = (user_info.get("name") or email.split("@")[0])
        session.permanent = True
        _log_event("login-ok")
        return redirect(url_for("contrib.workspace"))
    # zero interior render: straight back to the public bands surface
    _log_event("login-denied")  # no email logged (PII rule)
    return redirect("/bands")


# ===========================================================================
# THE PARSE FUNNEL (local; standard lane-split + Two-Class print/ask law)
# ===========================================================================
# Lane vocabulary: 2.0 parser = source of truth; on hosts without the 2.0 repo
# (Render), degrade to the inline minimal taxonomy (honest-causes mode) instead
# of crashing the whole blueprint (the deploy-failure class caught Oct 23 PM).
LANE_TAXONOMY_FALLBACK = "inline-minimal"
try:  # primary: 2.0 repo (same machine)
    sys.path.insert(0, str(TWO_REPO / "src" / "mass_pipeline"))
    from stage_b_parse import LANE_TAXONOMY  # type: ignore  # noqa: E402
    LANE_TAXONOMY_FALLBACK = None  # full taxonomy live
except Exception:
    # degraded: build the taxonomy from the DEPLOYED registry (always present at
    # request time; offline-install = empty dict + honest "unclassified" causes)
    try:
        reg = json.loads((DASH_DIR / "registry" / "card_page_registry.json").read_text(encoding="utf-8"))
        _lanes = {}
        for l in reg.get("lanes", []):
            _lanes.setdefault(str(l.get("lane", "")).strip().lower(), str(l.get("lane", "")))
        LANE_TAXONOMY = _lanes  # name -> display (minimal vocabulary)
    except Exception:
        LANE_TAXONOMY = {}  # fully degraded: parser reports unclassified w/ cause

try:
    sys.path.insert(0, str(TWO_REPO / "scripts"))
    from build_card_page_registry import band_class_for  # type: ignore  # noqa: E402
except Exception:  # local fallback mirrors the builder's thresholds
    def band_class_for(n: int, player: str, lane: str) -> str:  # type: ignore
        if n < 3:
            return "forming"
        return "provisional"  # engine flag only via the builder's bands.json check

PRICE_RE = re.compile(r"\$\s?([1-9][\d,]*(?:\.\d{2})|[0-9](?:[\d,]*\.\d{2}))")
BIDS_RE = re.compile(r"(\d+)\s+bids?\b", re.IGNORECASE)
GRADE_RE = re.compile(r"\b(PSA|BGS|SGC|CGC)\s*(9\.5|10|9|8(\.5)?|7(\.5)?)\b", re.IGNORECASE)


def _norm_lane(title: str, has_grade: bool) -> str:
    is_auto = bool(re.search(r"auto|ink|signature", title, re.IGNORECASE))
    base = "mass"
    for lane_name, pattern in LANE_TAXONOMY.items():
        try:
            if re.search(pattern, title, re.IGNORECASE):
                base = lane_name
                break
        except re.error:
            continue
    parts = (["graded"] if has_grade else []) + (["auto"] if is_auto else [])
    if base != "mass":
        parts.append(base)
    return "-".join(parts) or "mass"


def parse_pull_dump(text: str, player_hint: str | None = None) -> dict:
    """The standard funnel on arbitrary pull-dump text. Honest accounting:
    every excluded line lands in `excluded` with its cause. Never raises."""
    excluded: dict[str, int] = {}
    rows: list[dict] = []
    seen: set[tuple] = set()
    text_l = text or ""
    is_html = bool(re.search(r"<\s*(!doctype|html|\bdiv\b)|s-item|s-card", text_l, re.IGNORECASE))
    blob = re.sub(r"\r", "\n", text_l[:PASTE_MAX_CHARS])

    records: list[dict] = []
    if is_html:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(blob, "html.parser")
            blocks = soup.find_all(lambda t: t.name in ["li", "div"] and t.get("class")
                                   and any(c in ["s-item", "s-card"] for c in t.get("class")))
            for el in blocks:
                title_el = el.find(class_=lambda c: c and "title" in c)
                title = (title_el.get_text(strip=True) if title_el else
                         el.get_text(separator=" ", strip=True)[:120])
                if title.lower().startswith("shop on ebay"):
                    excluded["nav-chrome"] = excluded.get("nav-chrome", 0) + 1
                    continue
                sp = el.find(string=lambda s: (s or "").strip().lower() == "sponsored")
                if sp is not None:
                    excluded["sponsored"] = excluded.get("sponsored", 0) + 1
                    continue
                records.append({"title": title, "line": el.get_text(separator=" ", strip=True)})
        except Exception:
            excluded["html-parse-error"] = excluded.get("html-parse-error", 0) + 1
            soup = None  # bs4 unavailable on this host — degrade to raw blob
        # SINGLE-PARSE INVARIANT (Brief 6, Oct 24): if bs4 extracted blocks, the
        # rows are complete — never re-parse page text through line mode (that
        # double-counted every row and let page chrome in as ghost prints).
        text_for_lines = blob if (soup is None or not records) else ""
    else:
        text_for_lines = blob

    last_context_title = ""  # typed pastes: title line, then Sold/price lines
    for line in (text_for_lines or "").splitlines():
        line = line.strip()
        if not line or len(line) < 4:
            continue
        records.append({"title": line[:160], "line": line})
        # carry title context for the price lines that follow (Oct 23 fix: the
        # founder's typed paste had titles and Sold-lines on separate lines;
        # without context-carry the Sold-rows had no player-name to resolve)
        if not PRICE_RE.search(line) and not line.lower().startswith("sold"):
            last_context_title = line[:160]

    carried_title = ""  # refreshed per row: context title for Sold-only lines
    for rec in records:
        line = rec["line"]
        low = line.lower()
        title = rec["title"]
        if not PRICE_RE.search(line) and not line.lower().startswith("sold"):
            carried_title = title  # a bare title line: becomes context for following rows
            excluded["title-line"] = excluded.get("title-line", 0) + 1
            continue
        if not title or title == line:
            title = carried_title or title  # Sold-only row inherits its context title
        m = PRICE_RE.search(line)
        if not m:
            excluded["no-price"] = excluded.get("no-price", 0) + 1
            continue
        try:
            price = float(m.group(1).replace(",", ""))
        except ValueError:
            excluded["bad-price"] = excluded.get("bad-price", 0) + 1
            continue
        if price <= 0:
            excluded["bad-price"] = excluded.get("bad-price", 0) + 1
            continue
        if "(ask)" in low or low.endswith("ask"):
            excluded["asks"] = excluded.get("asks", 0) + 1  # counted, never silent
            continue
        bid_m = BIDS_RE.search(line)
        bids = int(bid_m.group(1)) if bid_m else 0
        fmt = "OBO" if ("best offer" in low or "obo" in low) else (
            "AUCTION" if (bids > 0 or "auction" in low or " bid" in low) else "BIN")
        g = GRADE_RE.search(title)
        grade_bucket = f"{g.group(1).upper()}{g.group(2)}" if g else "raw"
        lane = _norm_lane(title, g is not None)
        date_m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", line)
        key = (title.lower()[:100], price)
        if key in seen:
            excluded["duplicates"] = excluded.get("duplicates", 0) + 1
            continue
        seen.add(key)
        rows.append({"title": title[:160], "price": price, "bids": bids,
                     "format": fmt, "grade_bucket": grade_bucket, "lane": lane,
                     "date": date_m.group(1) if date_m else ""})

    # player guess -- ROW-DOMINANCE law (Oct 23 mis-attribution catch: the
    # longest-first match hit eBay page CHROME, crediting Chourio for a Turang
    # paste). Rule: count registry-player mentions in the LISTING ROWS (not the
    # page blob: chrome and related-searches sit in the blob but not the rows);
    # the player named in the most rows wins; zero row-hits falls back to
    # player_hint; longest-name tiebreak only when row-counts tie.
    players = sorted({l["player"] for l in BP.load_registry()["raw"].get("lanes", [])},
                     key=len, reverse=True)
    hdr = re.search(
        r"([\d,.]+)\s*\+?\s*results\s*for\s*(?:<[^>]+>\s*)*([^\"<\n]{1,90})",
        blob, re.IGNORECASE)
    player = player_hint or None
    if not player:
        # SEARCH-TERM RESOLUTION (Oct 23, founder-directed): a page paste carries
        # its own declared query: "N results for <search typed in>" — eBay's SRP
        # heading, proven in our own deposits. The declared query beats inference:
        # if any registry player appears INSIDE the declared search text, that
        # player is the page's author-stated subject and outranks row-dominance.
        if hdr:
            declared = hdr.group(2).strip().lower()
            for pl in players:
                if pl.lower() in declared:
                    player = pl
                    break
    if not player:
        row_text = "\n".join((r.get("title", "") + " " + r.get("line", "")) for r in rows)
        counts = {}
        for p in players:
            c = row_text.lower().count(p.lower())
            if c:
                counts[p] = c
        if counts:
            player = max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))[0]
    # CARD-YEAR POOL (Brief 5 Job A): card years named in the LISTING TITLES
    # and the declared search header — what the paste itself declares about the
    # product. Sale dates are noise (2026-10-16 / "Sold Oct 15, 2026") and are
    # stripped first so they can never pretend to be card years.
    _title_text = " ".join(r.get("title", "") for r in rows)
    _title_text = re.sub(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b", " ", _title_text)
    _title_text = re.sub(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s*(20\d{2})\b",
        " ", _title_text, flags=re.IGNORECASE)
    paste_years: list[str] = sorted(set(re.findall(r"\b20\d{2}\b", _title_text))
                                    | (set(re.findall(r"\b20\d{2}\b", hdr.group(2)))
                                       if hdr else set()))
    lanes: dict[str, list[float]] = {}
    for r in rows:
        lanes.setdefault(r["lane"], []).append(r["price"])
    return {"rows": rows, "excluded": excluded, "player": player,
            "print_count": len(rows), "lanes": lanes, "paste_years": paste_years}


# ===========================================================================
# REFINEMENT MATH (before/after width delta; percents only — never band $)
# ===========================================================================
def _q(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = q * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _width(vals: list[float]) -> float | None:
    if len(vals) < 3:
        return None
    s = sorted(vals)
    return max(0.0, _q(s, .75) - _q(s, .25))


def refine_lanes(parse: dict) -> list[dict]:
    """Match paste lane-groups to registry lanes; compute the refine story."""
    out: list[dict] = []
    player = parse.get("player")
    if not player:
        return out
    reg = BP.load_registry()["raw"].get("lanes", [])
    registry_by_key: dict[tuple, dict] = {}
    for l in reg:
        if l["player"].lower() == player.lower():
            registry_by_key.setdefault((l["product"] or "", l["lane"], l["grade_bucket"]), l)
            # also allow product-less paste grouping against ANY product with same lane
            registry_by_key.setdefault(("*", l["lane"], l["grade_bucket"]), l)
    for lane_name, prices in sorted(parse.get("lanes", {}).items()):
        if len(prices) < 2:
            continue
        # grade bucket of the group: majority of the group's rows
        gbs: dict[str, int] = {}
        for r in parse["rows"]:
            if r["lane"] == lane_name:
                gbs[r["grade_bucket"]] = gbs.get(r["grade_bucket"], 0) + 1
        gb = max(gbs, key=lambda k: gbs[k]) if gbs else "raw"
        match = registry_by_key.get(("*", lane_name, gb)) or registry_by_key.get(("*", lane_name, "raw"))
        # Brief 5 JOB A — YEAR-MATCHED LANE RESOLVER (the queued founder fix):
        # a 2025 paste once resolved to a 2023 lane because the resolver matched
        # product/parallel tokens but ignored YEAR. Candidates for a paste
        # lane-group = every registry lane sharing (lane, grade_bucket) — the
        # exact set the wildcard lookup collapsed (last-insert-wins, which is
        # where the wrong year crept in). When the paste text names card years
        # (titles / declared search header; sale dates stripped as noise),
        # prefer the same-candidates whose slug year matches; pick ONLY when
        # that leaves exactly one distinct candidate year. No year, mixed
        # years, or no year-carrying lane -> current behavior (honest miss or
        # insertion-order match, never a guess).
        paste_years = set(parse.get("paste_years") or [])
        if match and paste_years:
            cands = [l for l in reg
                     if l["player"].lower() == player.lower()
                     and l["lane"] == lane_name and l["grade_bucket"] == gb]
            if not cands and gb != "raw":
                cands = [l for l in reg
                         if l["player"].lower() == player.lower()
                         and l["lane"] == lane_name and l["grade_bucket"] == "raw"]
            year_carrying = [l for l in cands
                             if re.search(r"-(20\d{2})-", f"-{l['slug']}-")]
            if not year_carrying:
                pass  # no candidate carries a year: nothing to verify against, keep legacy
            else:
                year_cands = [l for l in year_carrying
                              if (ym := re.search(r"-(20\d{2})-", f"-{l['slug']}-"))
                              and ym.group(1) in paste_years]
                if len(year_cands) == 1:
                    match = year_cands[0]  # unambiguous: the one year-matched lane
                else:
                    match = None  # declared year mismatches / ambiguous -> honest miss
        entry = {"lane": lane_name, "grade_bucket": gb, "n_paste": len(prices)}
        if match:
            old_prints = list(match.get("prints") or [])
            n_before = match["n"]
            merged = sorted(old_prints + [p for p in prices])
            w_old, w_new = _width(old_prints), _width(merged)
            entry.update({
                "slug": match["slug"], "lane_display": match["lane_display"],
                "n_before": n_before, "n_after": n_before + len(prices),
                "old_class": match["band_class"],
                "pct": (round((1 - w_new / w_old) * 100) if (w_old and w_new and w_new < w_old and n_before >= 3) else None),
                "widened": bool(w_old and w_new and w_new > w_old and n_before >= 3),
            })
            # the would-be class after the contribution (honest honest state)
            new_class = ("forming" if (n_before + len(prices)) < 3 else
                         "engine_grade" if match["band_class"] == "engine_grade" else
                         "provisional")
            if (n_before + len(prices)) >= 3 and match["band_class"] == "forming" and \
                    band_class_for(n_before + len(prices), match["player"], match["lane"]) == "engine_grade":
                new_class = "engine_grade"
            entry["new_class"] = new_class
            entry["upgrade"] = (entry["old_class"] != new_class)
        else:
            entry.update({"slug": None, "lane_display": lane_name.replace("-", " ").title(),
                          "starts_lane": True, "new_class": ("forming" if len(prices) < 3 else "provisional"),
                          "upgrade": False})
        out.append(entry)
    return out


# ===========================================================================
# LEDGER (append-only rows keyed by GOOGLE EMAIL; private file, never rendered
# beyond the session contributor's own rows — P11)
# ===========================================================================
_ledger_lock = threading.Lock()


def contributor_id(email: str) -> str:
    return "c" + hashlib.sha1(email.strip().lower().encode()).hexdigest()[:10]


def ledger_tick(email: str, display_name: str, parse: dict, refined: list[dict],
                paste_id: str, direction: str | None = None,
                target_price: float | None = None, seller_id: str | None = None) -> None:
    row = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "paste_id": paste_id,
        "prints": parse["print_count"],
        "asks_excluded": (parse.get("excluded") or {}).get("asks", 0),
        "lanes": [r.get("slug") or r.get("lane") for r in refined],
        "refined": [{"slug": r.get("slug"), "pct": r.get("pct")} for r in refined if r.get("slug")],
        "direction": direction,          # BUY | SELL | None (brief 3 §227.1)
        "target_price": target_price,    # user's own ceiling/floor; never site-suggested
        "seller_id": (seller_id or None),  # optional; seller-watch ledger only
    }
    with _ledger_lock:
        try:
            data = json.loads(LEDGER_PATH.read_text(encoding="utf-8")) if LEDGER_PATH.exists() else {}
        except (OSError, ValueError):
            data = {}
        contrib = data.setdefault("contributors", {}).setdefault(email, {
            "contributor_id": contributor_id(email),
            "display_name": display_name,
            "first_ts": row["ts"],
            "pastes": 0, "prints_total": 0, "rows": [],
        })
        contrib["display_name"] = display_name  # refreshed on login/analyze
        contrib["pastes"] = int(contrib.get("pastes", 0)) + 1
        contrib["prints_total"] = int(contrib.get("prints_total", 0)) + parse["print_count"]
        contrib.setdefault("rows", []).append(row)  # append-only
        tmp = LEDGER_PATH.with_suffix(".tmp")
        try:
            LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
            os.replace(tmp, LEDGER_PATH)
        except OSError:
            pass


def own_ledger_rows(email: str) -> dict | None:
    try:
        data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        return (data.get("contributors") or {}).get(email)
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# CAN-SPAM CLOSURE (Brief 3 Job 4): stateless HMAC unsubscribe tokens.
# Token = base64url(email|ts|"v1"|hmac). The email is INSIDE the token (it is
# a capability to opt that ONE address out; never rendered beyond the flow).
# ---------------------------------------------------------------------------
def _unsub_secret() -> bytes:
    """SECRET_KEY from env/.env; dev fallback derives from the ledger path so a
    missing env never silently produces cross-install-valid tokens."""
    s = os.environ.get("SECRET_KEY") or env_file_val("SECRET_KEY")
    if s:
        return s.encode()
    return ("cardscout-contrib-unsub|" + str(LEDGER_PATH)).encode()


def make_unsub_token(email: str) -> str:
    msg = f"{email.strip().lower()}|{int(time.time())}|v1".encode()
    sig = hmac.new(_unsub_secret(), msg, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(msg + b"|" + sig).decode().rstrip("=")


def verify_unsub_token(token: str) -> str | None:
    """Returns the email for a valid, well-formed, non-expired token; else None.
    (No expiry is enforced by default — the capability is an opt-out, not a
    session; a bogus HMAC is rejected, which is the honest security boundary.)"""
    try:
        pad = "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + pad)
        email_b, ts_b, ver_b, sig = raw.split(b"|", 3)
        msg = email_b + b"|" + ts_b + b"|" + ver_b
        good = hmac.new(_unsub_secret(), msg, hashlib.sha256).digest()
        if not hmac.compare_digest(good, sig):
            return None
        if ver_b != b"v1":
            return None
        email = email_b.decode("utf-8")
        return email or None
    except Exception:
        return None


def _opt_out_flag(email: str, value: bool) -> bool:
    """Flip opt_out on the contributor's ledger entry (append-only style: the
    entry's row history stays; the flag + a timestamped marker are set)."""
    with _ledger_lock:
        try:
            data = json.loads(LEDGER_PATH.read_text(encoding="utf-8")) if LEDGER_PATH.exists() else {}
        except (OSError, ValueError):
            data = {}
        contrib = (data.get("contributors") or {}).get(email)
        if contrib is None:
            return False  # unknown contributor: no data to flip (callers decide)
        contrib["opt_out"] = bool(value)
        contrib["opt_out_ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        tmp = LEDGER_PATH.with_suffix(".tmp")
        try:
            LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
            os.replace(tmp, LEDGER_PATH)
            return True
        except OSError:
            return False


def is_opted_out(email: str) -> bool:
    try:
        data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        c = (data.get("contributors") or {}).get(email)
        return bool(c and c.get("opt_out"))
    except (OSError, ValueError):
        return False


def seller_watch_tick(seller_id: str, email: str, lane_ids: list[str]) -> bool:
    """Append-only §227 ledger write: {ts, contributor_email_hash, seller_id,
    lanes}. NOTHING is sent (the alert-side reversal ships in a later cycle)."""
    row = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contributor_email_hash": contributor_id(email),  # hash, not the email
        "seller_id": seller_id.strip()[:80],
        "lanes": lane_ids[:20],
    }
    with _ledger_lock:
        try:
            data = json.loads(SELLER_WATCH_PATH.read_text(encoding="utf-8")) \
                if SELLER_WATCH_PATH.exists() else {"rows": []}
        except (OSError, ValueError):
            data = {"rows": []}
        data.setdefault("rows", []).append(row)  # append-only
        tmp = SELLER_WATCH_PATH.with_suffix(".tmp")
        try:
            SELLER_WATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
            os.replace(tmp, SELLER_WATCH_PATH)
            return True
        except OSError:
            return False


def _log_event(event: str) -> None:
    try:
        DEPOSITS_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEPOSITS_DIR / "events.log", "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {event}\n")
    except OSError:
        pass


# ===========================================================================
# WATCH-TRIGGER LOOP (Brief 4 Job 1 — the §227.2 firing half). Runs on the SAME
# polling tick that refreshes lane caches (app.py's bands warm-up thread).
# LAW: user-owned triggers only — the machine computed NOTHING; it only reports
# that the market crossed the user's own number. Never advice, never band
# numbers (band thresholds render NOWHERE in mail), never unverified prints
# (registry prints = completed corpus prints; asks were excluded at parse),
# NEVER crashes the tick (every error = logged + skipped; bands still serve).
# One email per lane per cycle; a changed target = a new sent-marker key = re-arm.
# ===========================================================================
TRIGGER_SENT_PATH = Path(os.environ.get(
    "TRIGGER_SENT_PATH", TWO_REPO / "data_lake" / "gold" / "trigger_sent.json"))


def _load_trigger_markers() -> dict:
    try:
        return json.loads(TRIGGER_SENT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_trigger_markers(markers: dict) -> None:
    try:
        tmp = TRIGGER_SENT_PATH.with_suffix(".tmp")
        TRIGGER_SENT_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(markers), encoding="utf-8")
        os.replace(tmp, TRIGGER_SENT_PATH)
    except OSError:
        pass


def lane_display_for(slug: str) -> str:
    """Honest display name from the registry lane (player + lane title)."""
    lane = BP.lane_by_slug(slug) or {}
    player = str(lane.get("player") or "").strip()
    disp = str(lane.get("lane_display") or "").strip()
    text = " — ".join(x for x in (player, disp) if x)
    return text[:90] or slug[:90]


def crossing_print(prints: list, direction: str | None, target_price: float) -> float | None:
    """The verified-prints crossing test: BUY + print <= target -> below-hit;
    SELL + print >= target -> above-hit. Returns the winning print or None.
    These are COMPLETED prints from the corpus registry (asks never entered it)."""
    if direction not in ("BUY", "SELL") or not isinstance(target_price, (int, float)):
        return None
    hit = None
    for p in prints:
        try:
            v = float(p)
        except (TypeError, ValueError):
            continue
        if direction == "BUY" and v <= target_price:
            hit = v if hit is None else max(hit, v)
        elif direction == "SELL" and v >= target_price:
            hit = v if hit is None else min(hit, v)
    return hit


def build_crossing_email(email: str, slug: str, direction: str | None,
                         target_price: float, hit: float) -> tuple[str, str] | None:
    """The four-part cross email: subject per brief + their trigger line + the
    hitting print's market state (counted from the corpus, no band numbers) +
    tagged lane link + the CAN-SPAM footer w/ their real token. None = skipped
    (any failure is a no-send, never a crash)."""
    try:
        sys.path.insert(0, str(REPO_DIR / "scripts"))
        from email_alerts import render_footer  # noqa: E402  (J3 token hardening)
        try:
            footer = render_footer(make_unsub_token(email))  # their real CAN-SPAM token
        except Exception:
            footer = render_footer(None)  # placeholder footer, never a crash
    except Exception:
        return None
    display = lane_display_for(slug)
    subject = f"Card Scout — your price crossed on {display}"
    # market state: counted from the corpus registry only — PUBLIC facts (how
    # many completed prints exist; where the hitting print landed in them).
    # Band thresholds/z-scores/engine output NEVER enter this string.
    lane = BP.lane_by_slug(slug) or {}
    prints = [p for p in (lane.get("prints") or []) if isinstance(p, (int, float))]
    n_prints = len(prints)
    rank_note = ""
    if prints:
        below = sum(1 for p in prints if p <= hit)
        rank_note = ("<p style='font-size:13px;color:#6b7280'>The market print of "
                     f"${hit:,.2f} sits at position {below} of {n_prints} completed "
                     "prints in this lane's record "
                     f"(corpus: {lane.get('first_date', '—')} → {lane.get('last_date', '—')}).</p>")
    import urllib.parse as _up
    sys.path.insert(0, str(DASH_DIR))
    import band_pages as _bp  # the verified tagging path (campid gate inherited)
    view_url = ("https://www.ebay.com/sch/i.html?_nkw=" + _up.quote_plus(lane.get("search_q") or display)
                + "&_sop=16")
    link_obj = _bp.epn_tag(view_url, slug)
    link_html = (f'<a href="{link_obj["href"]}">View live eBay listings</a>'
                 + (' <span style="font-size:12px;color:#6b7280">(affiliate link)</span>'
                    if link_obj["tagged"] else ""))
    dir_word = {"BUY": "ceiling", "SELL": "floor"}.get(direction or "", "line")
    body = (
        f'<p>The market crossed YOUR line on <strong>{display}</strong>.</p>'
        f'<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin:10px 0">'
        f'<div style="font-weight:600">Your {dir_word}: <strong>${target_price:,.2f}</strong></div>'
        f'<div>Completed sale print: <strong>${hit:,.2f}</strong></div>'
        f'{rank_note}'
        f'<div style="margin-top:8px">{link_html}</div>'
        f'</div>'
        f'<p style="font-size:13px;color:#374151">This is the market report you asked the '
        f'machine to watch — the market crossed your line, that is the whole story. '
        f'What to do about it is entirely your call.</p>'
        f'{footer}'
    )
    return subject, body


def queue_crossing_email(to_email: str, subject: str, body_html: str) -> bool:
    """Queue into draft_outbox/ (the email_alerts dry-run stream). NOTHING is
    sent from the polling tick itself — a human (or the --send loop) sends.
    Returns queued True/False; never raises."""
    try:
        out_dir = Path(os.environ.get(
            "DRAFT_OUTBOX_DIR",
            Path(os.environ.get("CARDSCOUT2_HOME", TWO_REPO)) / "data_lake" / "gold" / "draft_outbox"))
        out_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-z0-9_-]+", "_", (to_email or "anon").strip().lower())[:80]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        # uuid suffix: seconds-resolution stamps collide when two triggers queue
        # in the same second (two lanes crossing in one tick) — never overwrite
        import uuid
        fname = f"trigger_{safe}_{stamp}_{uuid.uuid4().hex[:8]}.html"
        (out_dir / fname).write_text(
            json.dumps({"to": to_email, "subject": subject, "html": body_html,
                        "ts": stamp, "sent": False}, indent=0), encoding="utf-8")
        return True
    except OSError:
        return False


def mark_sent(markers: dict, key: str) -> None:
    markers[key] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _save_trigger_markers(markers)


def watch_trigger_tick() -> dict:
    """The §227.2 firing half, run on the bands cache polling half-cycle.
    NEVER raises — any failure is logged and skipped (bands still serve)."""
    summary = {"scanned": 0, "queued": 0, "skipped": 0, "errors": 0}
    try:
        data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        markers = _load_trigger_markers()
        reg = BP.load_registry()
        all_lanes = reg.get("raw", {}).get("lanes", [])
        for email, contrib in ((data.get("contributors") or {}).items()):
            try:
                if contrib.get("opt_out"):
                    summary["skipped"] += 1
                    continue
                fired_this_lane: set[str] = set()  # one email per lane per cycle
                for row in contrib.get("rows", []):
                    try:
                        target = row.get("target_price")
                        direction = row.get("direction")
                        if target is None or direction not in ("BUY", "SELL"):
                            continue
                        for slug in dedupe_lanes(row.get("lanes") or []):
                            try:
                                lane = next((l for l in all_lanes if l.get("slug") == slug), None)
                                prints = (lane or {}).get("prints") or []
                                if not prints:
                                    summary["skipped"] += 1
                                    continue
                                hit = crossing_print(prints, direction, float(target))
                                if hit is None:
                                    summary["scanned"] += 1
                                    continue
                                key = f"{email}|{slug}|{direction}|{target}"
                                if key in markers:
                                    summary["scanned"] += 1
                                    continue
                                if str(slug) in fired_this_lane:
                                    summary["skipped"] += 1
                                    continue
                                built = build_crossing_email(email, slug, direction, float(target), hit)
                                if built is None:
                                    summary["errors"] += 1
                                    continue
                                subj, body = built
                                if queue_crossing_email(email, subj, body):
                                    mark_sent(markers, key)
                                    fired_this_lane.add(str(slug))
                                    summary["queued"] += 1
                                    summary["scanned"] += 1
                                else:
                                    summary["errors"] += 1
                            except Exception:
                                summary["errors"] += 1
                                continue
                    except Exception:
                        summary["errors"] += 1
                        continue
            except Exception:
                summary["errors"] += 1
                continue
        _log_event("watch-tick " + json.dumps(summary))
        return summary
    except Exception as e:
        try:
            _log_event(f"watch-tick error {type(e).__name__}")
        except Exception:
            pass
        summary["errors"] += 1
        return summary


def dedupe_lanes(lanes: list) -> list[str]:
    out, seen = [], set()
    for x in lanes or []:
        s = str(x or "").strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _write_deposit(email: str, text: str, paste_id: str) -> None:
    dir_ = DEPOSITS_DIR / contributor_id(email)
    try:
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / f"{paste_id}_paste.txt").write_text(text[:PASTE_MAX_CHARS], encoding="utf-8")
    except OSError:
        pass


# ===========================================================================
# HISTOGRAM (their paste's own distribution — their data, honest bins)
# ===========================================================================
def histogram(prices: list[float], bins: int = 8) -> list[dict]:
    if not prices:
        return []
    lo, hi = min(prices), max(prices)
    if hi <= lo:
        return [{"x0": lo, "x1": hi, "n": len(prices), "w": 100.0}]
    step = (hi - lo) / bins
    counts = [0] * bins
    for p in prices:
        counts[min(int((p - lo) / step), bins - 1)] += 1
    return [{"x0": lo + b * step, "x1": lo + (b + 1) * step, "n": counts[b],
             "w": (counts[b] / len(prices) * 100.0)} for b in range(bins)]


# ===========================================================================
# TEMPLATES
# ===========================================================================
CSS = '<link rel="stylesheet" href="/static/style.css">\n<link rel="stylesheet" href="/static/contrib.css">'

# The founder-directed standing privacy + no-advice disclosure (P12: the login
# view carries the expandable full text; the workspace footer carries the
# one-liner; both contain the same clauses — never contradictory).
DISCLOSURE_FULL = """
<div class="contrib-disclosure">
  <p class="disc-lead"><strong>What we do with your Google information</strong></p>
  <p class="disc-take">WHAT WE TAKE: your Google email + display name — used SOLELY to
  attribute your contributions (ledger credit, your personal reward views).</p>
  <p class="disc-never">WHAT WE NEVER DO: sell, share, rent, advertise against, or export
  your information. Not in the business. Full stop.</p>
  <p class="disc-leaves">WHAT LEAVES: nothing. Data flows one-way INTO the machine; the
  ledger is private to you and the founder.</p>
  <p class="disc-disconnect">THE DISCONNECTION GUARANTEE: you can ask to be removed at any
  time (founder@cardscout.pro) — your ledger rows anonymize (email becomes a random
  contributor-id), the lanes stay (they're market data), and your attribution credit
  transfers into the anonymized form.</p>
  <div class="disc-agency">
    <p class="disc-agency-as-is">Listings are eBay content, shown as-is — we don't sell,
    hold, grade, or warrant any card, and we're not affiliated with eBay or any grader.</p>
    <p class="disc-agency-click">Clicking through to eBay or any seller is your decision
    and your transaction — we earn a small commission (disclosed) and take no part after
    the click.</p>
    <p class="disc-agency-bands">Bands are built from the community's own pulls — they
    show what has sold, not what to buy. Your judgment is the final layer.</p>
  </div>
</div>
"""

FOOTER_LINE = '''
<footer class="contrib-footer">
  <p>We show you the market with the data you provide — what you click and buy is your
  call. Your Google info is used only to credit your contributions; we never sell, share,
  or export it.</p>
</footer>
'''

LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Contributor workspace — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="contrib-main">
  <h1>Contributor workspace</h1>
  <p class="contrib-lede">Paste an eBay pull — the machine parses it and the page returns
  your reward: the paste's own distribution, the lane it refines, and your ledger credit.</p>
  {% if notice %}<p class="contrib-notice">{{ notice }}</p>{% endif %}
  <p class="google-btn-row">
    <a class="g-login" href="{{ auth_url or '/contributor/login/google' }}">Sign in with Google</a>
  </p>
  ''' + DISCLOSURE_FULL.replace('class="contrib-disclosure"', 'class="contrib-disclosure"') + '''
</main>
''' + FOOTER_LINE + '''
</body>
</html>'''

WORKSPACE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Contributor workspace — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/contributor/ledger">My ledger</a>
      <a href="/contributor/logout">Sign out</a></div>
  </nav>
</header>
<main class="contrib-main">
  <h1>Paste an eBay pull</h1>
  {% if stats %}
  <div class="contrib-statstrip" id="stat-strip" aria-label="Your contribution totals">
    <span class="stat-num">{{ stats.pastes }}</span> paste{{ '' if stats.pastes == 1 else 's' }}
    <span class="stat-sep">·</span>
    <span class="stat-num">{{ stats.prints_total }}</span> print{{ '' if stats.prints_total == 1 else 's' }} contributed
    <span class="stat-sep">·</span>
    <span class="stat-num">{{ stats.lanes_touched }}</span> lane{{ '' if stats.lanes_touched == 1 else 's' }} touched
    <span class="stat-sep">·</span>
    credit since {{ stats.first_ts }}
  </div>
  <p class="contrib-credit-line">Every deposit sharpens the bands for the whole community — your searches built these.</p>
  {% endif %}
  <p class="contrib-lede">Multi-page pastes are fine. The parser counts everything it
  sets aside — nothing is dropped silently. You get the distribution, the refined lane,
  and the ledger credit.</p>
  <div class="depth-hint">
    <strong>How to make the perfect deposit (30 seconds):</strong>
    <ol style="margin:6px 0 0 18px; padding:0">
      <li>On your eBay results page, scroll to the bottom and set
          <strong>results-per-page to 240</strong> (the default is only 60 — a shallow pull).</li>
      <li><strong>Select everything on the page (Ctrl+A) and copy (Ctrl+C)</strong> —
          the whole page, chrome and all. It's our job to sort it, not yours.</li>
      <li>One page is the standard deposit — roughly 240 cards, a complete picture
          for most lanes. Feeling generous? Copy extra pages and stack them — every
          bonus page sharpens the band for everyone who searches this card after you.</li>
    </ol>
    Paste below — the page carries its own declaration ("N results for what you
    searched"), so we know exactly which instrument you brought us.
  </div>
  <form method="post" action="/contributor/analyze">
    <fieldset class="intake-fieldset">
      <legend class="intake-legend">Direction <span class="intake-optional">(optional — the analysis runs either way)</span></legend>
      <label class="intake-radio"><input type="radio" name="direction" value="BUY"> Buying</label>
      <label class="intake-radio"><input type="radio" name="direction" value="SELL"> Selling</label>
      <span class="intake-hint">Your watch alert branches on this: a ceiling when buying, a floor when selling.</span>
    </fieldset>
    <fieldset class="intake-fieldset">
      <legend class="intake-legend"><span data-dir-label data-buy="Your ceiling — alert me below this" data-sell="Your floor — alert me above this">Target price (optional)</span></legend>
      <input class="intake-target" type="number" step="0.01" min="0" name="target_price"
             placeholder="" aria-label="Target price (your own value; never suggested by the site)">
      <span class="intake-hint">Your own number — the site never suggests or pre-fills a price here.</span>
    </fieldset>
    <fieldset class="intake-fieldset">
      <legend class="intake-legend">Your eBay seller ID <span class="intake-optional">(optional — for the seller-watch ledger)</span></legend>
      <input class="intake-seller" type="text" name="seller_id" maxlength="80" autocomplete="off" placeholder="">
      <span class="intake-hint">Stored in the seller-watch ledger only; no seller features yet.</span>
    </fieldset>
    <textarea name="paste" rows="14" placeholder="Paste the pull dump here (text or page source)…"  maxlength="{{ paste_max }}"></textarea>
    <div class="paste-actions">
      <button type="submit">Analyze paste</button>
      <span class="paste-cap">up to ~{{ (paste_max // 1000) }}KB</span>
    </div>
  </form>
  %LEADER%
</main>
<script>
(function () {
  'use strict';
  // §227.1: direction-aware target label; NO default selection, NOTHING pre-filled.
  var radios = document.querySelectorAll('input[name="direction"]');
  var label = document.querySelector('[data-dir-label]');
  if (!radios.length || !label) return;
  radios.forEach(function (r) {
    r.addEventListener('change', function () {
      if (r.checked) label.textContent = r.value === 'SELL'
        ? label.getAttribute('data-sell')
        : label.getAttribute('data-buy');
    });
  });
})();
</script>
''' + FOOTER_LINE + '''
</body>
</html>'''

REWARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Your paste's reward — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/contributor">New paste</a>
      <a href="/contributor/ledger">My ledger</a> <a href="/contributor/logout">Sign out</a></div>
  </nav>
</header>
<main class="contrib-main reward">
  <h1>Analyzed — here's your reward</h1>

  <!-- 1: YOUR PASTE'S DISTRIBUTION (honest counts; junk counted by cause) -->
  <section class="reward-block">
    <h2>Your paste's distribution</h2>
    <p class="reward-note">{{ parse.print_count }} clean print{{ '' if parse.print_count == 1 else 's' }}
    {% if parse.player %} — {{ parse.player }}{% endif %}.
    {% set ex = parse.excluded %}
    {% if ex %}Set aside (counted, never silent):
      {% for cause, n in ex.items() %}{{ n }} {{ cause.replace('-', ' ') }}{{ '' if loop.last else ', ' }}{% endfor %}.
    {% else %}Nothing set aside.{% endif %}</p>
    {% for h in hists %}
      <div class="hist">
        <div class="hist-title">{{ h.label }}
          <span class="hist-summary">low ${{ '%.2f' % h.lo }} · median ${{ '%.2f' % h.med }} · high ${{ '%.2f' % h.hi }}</span>
        </div>
        <div class="hist-bars">
          {% for b in h.bins %}
          <div class="hist-bin"><div class="hist-bar" style="width:{{ b.w | round(1) }}%"></div>
            <span class="hist-count">{{ b.n }} <span class="hist-range">${{ '%.2f' % b.x0 }}–${{ '%.2f' % b.x1 }}</span></span></div>
          {% endfor %}
        </div>
      </div>
    {% endfor %}
  </section>

  <!-- 2: THE LANE REFINED (width-delta PERCENTAGE + credit; never band $) -->
  {% if refined %}
  <section class="reward-block">
    <h2>The lane refined</h2>
    {% for r in refined %}
      <div class="refine-row">
      {% if r.slug %}
        <p>{{ r.lane_display }} — {{ r.n_before }} prints → {{ r.n_after }} prints.
        {% if r.pct %}YOUR paste narrowed this lane's spread by {{ r.pct }}%. Credit: the freshest pull.{% endif %}
        {% if r.widened %}The lane's spread widened with this paste (real market movement, recorded honestly).{% endif %}
        {% if r.upgrade %}Lane state: {{ r.old_class | upper }} → <strong>{{ r.new_class | upper }}</strong>{% if r.new_class == 'provisional' and r.old_class == 'forming' %} — a band now forms on this page{% endif %}{% if r.new_class == 'engine_grade' and r.old_class != 'engine_grade' %} — engine-grade on the next registry rebuild{% endif %}.{% endif %}
        </p>
        <p class="refine-tip">Refinement tip: one refined query (name + set + the exact parallel) on your next pull tightens this lane further.</p>
      {% else %}
        <p>{{ r.lane_display }} — your paste starts data for a lane we don't have yet
        ({{ r.n_paste }} prints; the band appears at 3). Keep pulling.</p>
      {% endif %}
      </div>
    {% endfor %}
    {% if direction and target_price is not none %}
      {% if direction == 'BUY' %}
      <p class="watch-line">Entry watch: if this lane prints below YOUR ceiling (${{ '%.2f' % target_price }}), your next alert says so.</p>
      {% elif direction == 'SELL' %}
      <p class="watch-line">Repricing watch: if this lane prints above YOUR floor (${{ '%.2f' % target_price }}), your next alert says so.</p>
      {% endif %}
    {% elif seller_id %}
      <p class="watch-line watch-line-quiet">Seller watch: {{ seller_id }} is on the seller-watch ledger (no seller features yet).</p>
    {% endif %}
  </section>
  {% else %}
  <section class="reward-block">
    <h2>The lane refined</h2>
    <p>No known lane matched yet — your paste is deposited and the corpus grows.
    {% if not parse.player %}No player matched from the corpus yet; include the player name in your next search header for lane credit.{% endif %}</p>
    {% if direction and target_price is not none %}
      {% if direction == 'BUY' %}
      <p class="watch-line">Entry watch: if this lane prints below YOUR ceiling (${{ '%.2f' % target_price }}), your next alert says so.</p>
      {% elif direction == 'SELL' %}
      <p class="watch-line">Repricing watch: if this lane prints above YOUR floor (${{ '%.2f' % target_price }}), your next alert says so.</p>
      {% endif %}
    {% endif %}
  </section>
  {% endif %}

  <!-- 3: LISTINGS for the refined lane (standard lower-half, cache-law served) -->
  {% if lane_slug %}
  <section class="reward-block">
    <h2>Live listings — the refined lane</h2>
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
           data-price="{{ it.price }}" data-class="{{ it.cls }}"
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
    <p class="no-listings">No live listings right now — the refined band is the market record for this lane.</p>
    {% endif %}
  </section>
  {% endif %}

  <!-- 4: THANKS + ledger tick -->
  <section class="reward-block reward-thanks">
    <h2>Thank you</h2>
    <p>Your contribution is credited: this paste added {{ parse.print_count }} print{{ '' if parse.print_count == 1 else 's' }}
    to the corpus and +1 to your ledger.{% if ledger_total %} Ledger total: {{ ledger_total }} paste{{ '' if ledger_total == 1 else 's' }}.{% endif %}</p>
  </section>
</main>
''' + FOOTER_LINE + '''
<script src="/static/bands.js"></script>
</body>
</html>'''

ERROR_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Paste not parseable — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/contributor">Try again</a></div>
  </nav>
</header>
<main class="contrib-main">
  <h1>Analysis failed — paste was not parseable</h1>
  <p class="contrib-lede">Nothing was lost and nothing broke: here is exactly what the
  parser saw.</p>
  <ul class="cause-list">
    {% for k, v in causes.items() %}
      <li>{{ v }} {{ k.replace('_', ' ') }}</li>
    {% endfor %}
  </ul>
  <p class="refine-tip">Refinement tip: paste the listing text that includes prices
  ($ amounts per line), or the full results-page source — one refined query per pull
  gives a tighter lane next time.</p>
</main>
''' + FOOTER_LINE + '''
<script src="/static/bands.js"></script>
</body>
</html>'''

LEDGER_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>My ledger — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/contributor">New paste</a> <a href="/contributor/logout">Sign out</a></div>
  </nav>
</header>
<main class="contrib-main">
  <h1>My ledger</h1>
  {% if me %}
  <p class="ledger-summary">{{ me.pastes }} paste{{ '' if me.pastes == 1 else 's' }},
  {{ me.prints_total }} prints contributed.</p>
  <table class="ledger-table">
    <thead><tr><th>When</th><th>Prints</th><th>Set aside (asks)</th><th>Lanes credited</th><th>Refinement</th></tr></thead>
    <tbody>
    {% for row in me.rows %}
      <tr>
        <td>{{ row.ts }}</td>
        <td>{{ row.prints }}</td>
        <td>{{ row.asks_excluded }}</td>
        <td>{{ row.lanes | length }}</td>
        <td>{% for r in row.refined %}{{ r.slug[:28] }}{% if r.pct %} −{{ r.pct }}%{% endif %}{{ '' if loop.last else '; ' }}{% else %}—{% endfor %}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="contrib-lede">No contributions yet — paste your first pull.</p>
  {% endif %}
</main>
''' + FOOTER_LINE + '''
</body>
</html>'''


# ===========================================================================
# ROUTES
# ===========================================================================
def _require_contributor() -> str | None:
    if not is_on_roster(session.get("contributor_email")):
        # clean single redirect to the public surface, zero interior (P9)
        return redirect("/bands")
    return None


@bp.route("/")
def workspace():
    email = session.get("contributor_email")
    if is_on_roster(email):
        # Brief 5 Job D: the credit made visible — a compact strip from THIS
        # contributor's own ledger rows (pastes / prints / lanes / first_ts).
        # Own-data only (P11); no band numbers (P4); no new computation.
        me = own_ledger_rows(email) or {}
        lanes_touched = len({slug for row in me.get("rows", [])
                             for slug in (row.get("lanes") or []) if slug})
        stats = None
        if me.get("pastes"):
            stats = {
                "pastes": me.get("pastes", 0),
                "prints_total": me.get("prints_total", 0),
                "lanes_touched": lanes_touched,
                "first_ts": str(me.get("first_ts") or "")[:10] or "your first paste",
            }
        tpl = WORKSPACE_TEMPLATE.replace("%LEADER%", "")
        return render_template_string(tpl, paste_max=PASTE_MAX_CHARS,
                                      display_name=session.get("contributor_name"),
                                      stats=stats)
    # logged-out or non-roster direct access -> interior never renders (P9's letter):
    # clean redirect to the public bands surface. The login view lives at
    # /contributor/login for the explicit "log in to contribute" entry point.
    return redirect("/bands")


@bp.route("/login")
def login():
    notice = None
    if not google_client_id():
        notice = "Google login is not configured on this host — set GOOGLE_CLIENT_ID."
    auth_url = url_for("contrib.login_google")  # the route performs the redirect dance
    email = session.get("contributor_email")
    if is_on_roster(email):
        return redirect(url_for("contrib.workspace"))
    body = LOGIN_TEMPLATE
    return render_template_string(body, notice=notice, auth_url=auth_url)


@bp.route("/login/google")
def login_google():
    if not google_client_id():
        return redirect(url_for("contrib.login"))
    from requests_oauthlib import OAuth2Session
    import requests as _rq
    try:
        cfg = _rq.get(GOOGLE_DISCOVERY_URL, timeout=15).json()
        oa = OAuth2Session(google_client_id(), scope=["openid", "email", "profile"],
                           redirect_uri=request.url_root.rstrip("/") + "/contributor/login/google/callback")
        auth_url, state = oa.authorization_url(cfg["authorization_endpoint"])
        session["contrib_oauth_state"] = state
        return redirect(auth_url)
    except Exception:
        return redirect(url_for("contrib.login"))


@bp.route("/login/google/callback")
def login_google_callback():
    from requests_oauthlib import OAuth2Session
    import requests as _rq
    if "contrib_oauth_state" not in session:
        return redirect(url_for("contrib.login"))
    try:
        cfg = _rq.get(GOOGLE_DISCOVERY_URL, timeout=15).json()
        oa = OAuth2Session(google_client_id(), state=session["contrib_oauth_state"],
                           redirect_uri=request.url_root.rstrip("/") + "/contributor/login/google/callback")
        oa.fetch_token(cfg["token_endpoint"], authorization_response=request.url,
                       client_secret=env_file_val("GOOGLE_CLIENT_SECRET"))
        user_info = oa.get(cfg["userinfo_endpoint"]).json()
        session.pop("contrib_oauth_state", None)
        return _finish_login(user_info)
    except Exception:
        return redirect(url_for("contrib.login"))


@bp.route("/logout")
def logout():
    session.pop("contributor_email", None)
    session.pop("contributor_name", None)
    return redirect(url_for("contrib.workspace"))


@bp.route("/analyze", methods=["POST"])
def analyze():
    gate = _require_contributor()
    if gate is not None:
        return gate
    email = session["contributor_email"]
    name = session.get("contributor_name") or email.split("@")[0]
    text = (request.form.get("paste") or "")
    # --- Brief 3 intake (all three null-safe; §227.1/§227.2) ---
    direction = (request.form.get("direction") or "").strip().upper() or None
    if direction not in ("BUY", "SELL"):
        direction = None
    target_raw = (request.form.get("target_price") or "").strip()
    target_price: float | None = None
    if target_raw:
        try:
            v = float(target_raw)
            if v > 0:
                target_price = round(v, 2)  # the USER'S own number; never site-suggested
        except ValueError:
            target_price = None
    seller_id = (request.form.get("seller_id") or "").strip()[:80] or None
    if len(text) > PASTE_MAX_CHARS:
        return render_template_string(
            ERROR_TEMPLATE,
            causes={"paste-too-large": f"paste exceeded the {PASTE_MAX_CHARS // 1000}KB cap —"
                    " split it into two pastes"},
        )
    if not text.strip():
        return render_template_string(ERROR_TEMPLATE, causes={"empty-paste": "1"})
    parse = parse_pull_dump(text)
    refined = refine_lanes(parse)
    if parse["print_count"] == 0:
        # honest 200 with the counted causes (P10e: never a 500)
        causes = parse.get("excluded") or {"no-price": 1}
        _log_event(f"parse-failed prints=0 causes={json.dumps(causes)}"
                   .replace(email or "NOEMAIL", "[contributor]"))  # no PII in logs
        return render_template_string(ERROR_TEMPLATE, causes=causes)
    paste_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _write_deposit(email, text, paste_id)
    # Brief 3: the deposit's sidecar carries the intake trio (null-safe)
    try:
        sidecar = {
            "paste_id": paste_id, "direction": direction,
            "target_price": target_price, "seller_id": seller_id,
        }
        (DEPOSITS_DIR / contributor_id(email) / f"{paste_id}_intake.json").write_text(
            json.dumps(sidecar), encoding="utf-8")
    except OSError:
        pass
    if seller_id:  # §227 ledger-only write; nothing is ever sent
        seller_watch_tick(seller_id, email, [r.get("slug") or r.get("lane") for r in refined])
    ledger_tick(email, name, parse, refined, paste_id,
                direction=direction, target_price=target_price, seller_id=seller_id)
    # the refined lane's listings: the FIRST matched known lane with a slug
    lane_slug = next((r["slug"] for r in refined if r.get("slug")), None)
    # Brief 4 T5: the analyze path logs its search heat too — the refined lane's
    # community query, the user's direction, and the prints this paste added.
    # NO identity in the heat row (heat != identity).
    if lane_slug:
        try:
            _heat_lane = BP.lane_by_slug(lane_slug) or {}
            BP.heatmap_log(_heat_lane.get("search_q") or lane_slug, lane_slug,
                           direction, parse["print_count"])
        except Exception:
            pass  # telemetry never breaks the reward render
    items, meta = [], {"source": "none", "age": None, "error": None}
    if lane_slug:
        items, meta = BP.get_listings(lane_slug)
        items = BP.order_default(items)
        for it in items:
            tag = BP.epn_tag(it["url"], lane_slug)
            it["href"] = tag["href"]
            it["tagged"] = tag["tagged"]
    # histograms: per refined lane with a slug; else one overall distribution
    hists = []
    if refined:
        for r in refined:
            prices = parse["lanes"].get(r["lane"], [])
            if prices and r.get("slug"):
                hs = sorted(prices)
                hists.append({"label": r["lane_display"] + f" (n={len(prices)})",
                              "bins": histogram(prices),
                              "lo": min(hs), "med": _q(hs, .5), "hi": max(hs)})
    if not hists:
        hs = sorted(r["price"] for r in parse["rows"])
        hists.append({"label": f"All prints (n={parse['print_count']})",
                      "bins": histogram(hs),
                      "lo": min(hs), "med": _q(hs, .5), "hi": max(hs)})
    me = own_ledger_rows(email)
    return render_template_string(
        REWARD_TEMPLATE, parse={**parse}, hists=hists, refined=refined,
        lane_slug=lane_slug, items=items, listings_meta=meta,
        direction=direction, target_price=target_price, seller_id=seller_id,
        ledger_total=(me or {}).get("pastes"))


@bp.route("/ledger")
def ledger_view():
    gate = _require_contributor()
    if gate is not None:
        return gate
    me = own_ledger_rows(session["contributor_email"])
    return render_template_string(LEDGER_TEMPLATE, me=me)


@bp.route("/health")
def health():
    return {"ok": True, "roster_size": len(contributor_roster()),
            "auth_configured": bool(google_client_id())}


# ---------------------------------------------------------------------------
# CAN-SPAM endpoints (Brief 3 Job 4): public, token-gated, robots-disallowed.
# They ONLY flip ledger flags — ZERO email is ever sent from this module.
# ---------------------------------------------------------------------------
UNSUB_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{{ headline }} — Card Scout</title>
''' + CSS + '''
</head>
<body class="contrib-page">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a></div>
  </nav>
</header>
<main class="contrib-main">
  <h1>{{ headline }}</h1>
  <p class="contrib-lede">{{ lede }}</p>
  {% if show_resub %}
  <p><a class="g-login resub-btn" href="/resubscribe?t={{ token }}">Re-subscribe</a></p>
  {% endif %}
</main>
''' + FOOTER_LINE + '''
</body>
</html>'''


@unsub_bp.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    token = (request.args.get("t") or "").strip()
    email = verify_unsub_token(token) if token else None
    ok = False
    if email:
        was_out = is_opted_out(email)
        ok = _opt_out_flag(email, True)
        _log_event("unsubscribe-ok" if ok else "unsubscribe-unknown")
        if ok and not was_out:
            # Brief 5 Job C: ONE transactional confirmation on the FLIP only —
            # already-out users get nothing; send errors never touch this page.
            try:
                sys.path.insert(0, str(REPO_DIR / "scripts"))
                from email_alerts import send_unsubscribe_confirmation  # noqa: E402
                sent = send_unsubscribe_confirmation(email, token)
                _log_event("unsub-confirmation sent" if sent
                           else "unsub-confirmation skipped-or-failed")
            except Exception:
                _log_event("unsub-confirmation error-suppressed")
    else:
        _log_event("unsubscribe-bad-token")
    return render_template_string(
        UNSUB_TEMPLATE,
        ok=ok,
        headline=("You're unsubscribed." if ok else "Link expired."),
        lede=("The bands stay public at cardscout.pro — your alerts stop immediately. "
              "Changed your mind? One click, right here."
              if ok else
              "This unsubscribe link isn't valid anymore — contact "
              "jonathan@cardscout.pro and we'll sort it out immediately. "
              "The bands stay public at cardscout.pro."),
        token=token if ok else "",
        show_resub=ok)


@unsub_bp.route("/resubscribe", methods=["GET"])
def resubscribe():
    token = (request.args.get("t") or "").strip()
    email = verify_unsub_token(token) if token else None
    ok = False
    if email:
        ok = _opt_out_flag(email, False)
        _log_event("resubscribe-ok" if ok else "resubscribe-unknown")
    return render_template_string(
        UNSUB_TEMPLATE,
        ok=ok,
        headline=("You're re-subscribed." if ok else "Link expired."),
        lede=("Your alerts resume immediately. The bands stay public at cardscout.pro."
              if ok else
              "This re-subscribe link isn't valid anymore — contact "
              "jonathan@cardscout.pro and we'll fix it immediately."),
        token="",
        show_resub=False)

# ===========================================================================
# THE CAR-DEALER ANALOGY (Oct 23 night, founder crystallization — capture verbatim-
# intent): "We should TELL them how to do it. 1) It's the easiest way and makes
# THEM more efficient. 2) It gives us THE VEHICLE THEY ARE SEARCHING UNDER —
# make and model." = the teaching layer and the telemetry layer are THE SAME
# ACT. Instructing the exact search (year + set + parallel + /nn) does double
# duty: contributors get sharper bands faster, and the machine receives each
# paste pre-declared (the URL/state carries the instrument's make/model).
# The depth hint + refined-query tips + SRP-declaration resolution = one unified
# TEACH-AND-TRACK system: every lesson we teach is also a sensor we install.
# ===========================================================================
