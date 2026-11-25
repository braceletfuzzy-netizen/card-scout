"""NIGHTLY TRIFECTA-LANE FINDER (SS250.33 / SS250.33.1, founder GO Nov-13).

Cron no_agent, 6am CT daily. Silent-healthy, silent-quiet: posts ONLY criterion-met
finds to founder-direct Discord; empty nights produce no output, no posts.

THE LANE (SS250.33 The Find-Supply Law): repricing is fast, FINDING is the bottleneck.
Nightly BrightData (web_unlocker1) eBay live-ask queries on gate-passed watch-table
names (data_lake/gold/machine_watch_roster_50.json), 8 rung-shaped queries per name,
rotation + 60-call/day budget, ~8s spacing.

THE CRITERIA STACK (SS250.32 + SS250.23 + SS250.28):
  1. TRIFECTA = 1st-Bowman x auto x serialized rung   (SS250.23 confluence)
  2. BELOW-LEVERAGE = price / PP-rung-multiplier < $15/leverage (buy-band, SS250.23)
  3. GOLD-FLOOR ROW = gold-1st-auto on AA/AAA name priced <= $250 = below-floor entry
     (entries $50-250 under floor; $50-150 = the buy-band per SS250.28)
Parse law: s-card/s-item items, sponsored/shop-ad filtered, ask-only (no sold filter).

Delivery: raw Discord bot-API POST to 1567567851408072814, UA 'DiscordBot (https://cardscout.pro, 1.0)',
deduped by item id in seen_items.json (never re-alerts the same listing).
Smoke test: set env FIND_SMOKE=1 -> 1 name, 2 queries, Discord SUPPRESSED.

CONVENTION NOTE (fleet stall-exit pattern, adopted Nov-23 — agent-loop course item #3):
  This fleet's stand-exit rule = "2 rounds without fewer failures => structured stop".
  Module: For You/PolyScout/build/fleet_stall_exit.py (AppData hermes/scripts/ mirror
  per the two-place law) — import-ready NOW, call-site NOT yet wired (convention-first;
  do not rewire the finder loop without a FIND_SMOKE=1 test run):
      import sys as _sys
      _sys.path.insert(0, "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build")
      from fleet_stall_exit import check_stall, stall_exit_note
      # call-site (per query-round loop, after failures counted this round):
      #   _failure_history.append(failures_this_round)
      #   if len(_failure_history) >= 3:
      #       stop, reason = check_stall(_failure_history)
      #       if stop:
      #           print(stall_exit_note(what_tried="8-rung BrightData sweeps over roster",
      #                                 why_failing=reason,
      #                                 what_next="re-check ask-parse law (s-card/s-item) + budget rollover, then re-run FIND_SMOKE=1; escalate to founder if still flat"))
      #           _sys.exit(0)
"""
import os, sys, re, json, time, uuid, shutil
from pathlib import Path

# ---- self-heal interpreter: prefer the hermes venv (bs4 guaranteed) ----
try:
    import bs4  # noqa
except ImportError:
    VENV_PY = r"C:\Users\J\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
    if os.path.exists(VENV_PY) and os.path.abspath(sys.executable) != os.path.abspath(VENV_PY):
        os.execv(VENV_PY, [VENV_PY, __file__] + sys.argv[1:])
    raise

import requests
from bs4 import BeautifulSoup

ROOT = Path(r"C:\Users\J\Documents\LLM\cardscout-2.0")
ROSTER_PATH = ROOT / "data_lake" / "gold" / "machine_watch_roster_50.json"
PP_MULT_PATH = ROOT / "data_lake" / "gold" / "pp_checklists_2026-11-13.json"
TOKEN_PATH = Path(r"C:\Users\J\Documents\LLM\card-scout\config\bright-data-token.txt")
OUT_DIR = ROOT / "data_lake" / "gold" / "finder"
SEEN_PATH = OUT_DIR / "seen_items.json"
STATE_PATH = OUT_DIR / "rotation_state.json"
LOG_PATH = OUT_DIR / "finder_log.jsonl"
ENV_PATH = Path(r"C:\Users\J\AppData\Local\hermes\.env")
DISCORD_CHANNEL = "1567567851408072814"
DISCORD_UA = "DiscordBot (https://cardscout.pro, 1.0)"
BD_ZONE = "web_unlocker1"
BD_URL = "https://api.brightdata.com/request"
BD_CALL_CAP = 60          # calls/day ceiling (spec: 25-60)
NAMES_PER_NIGHT = 7       # ~56 calls at rung 8/name
QUERY_SLEEP = 8           # ~8s spacing between BrightData calls
PRICE_PER_LEV_CAP = 15.0  # SS250.23 buy-band
GOLD_FLOOR = 250.0        # SS250.28 AA/AAA gold-1st-auto floor
LIQ_MIN = 5               # SS250.51 liquidity-gate (founder law Nov-15): n>=5 CH
                          # sales/30d = REQUIRED input; below = dead-lane mirage
                          # (Thompson 13-pass ask-burst on 2-total-sales lane)
CH_KEY_PATH = Path(r"C:\Users\J\.secrets\card-scout\card-hedger-api-key.txt")
CH_SALES_URL = "https://api.cardhedger.com/v1/cards/total-sales-by-player"

# 8 rung-shaped query shapes (SS250.33: "<name> 1st auto <rung>")
RUNG_SHAPES = [
    ("gold",          "{n} 1st bowman auto gold"),
    ("gold_shimmer",  "{n} 1st bowman auto gold shimmer"),
    ("green",         "{n} 1st bowman auto green"),
    ("yellow",        "{n} 1st bowman auto yellow"),
    ("refractor",     "{n} 1st bowman auto refractor"),
    ("blue",          "{n} 1st bowman auto blue"),
    ("orange",        "{n} 1st bowman auto orange"),
    ("any_serial",    "{n} 1st bowman auto numbered"),
]

# Lane detection on listing titles: SPECIFIC-FIRST ordering (shimmer before gold, etc.)
LANE_PATTERNS = [
    ("gold_shimmer",   r"gold\s*shimmer"),
    ("gold",           r"\bgold\b"),
    ("orange_shimmer", r"orange\s*shimmer"),
    ("orange",         r"\borange\b"),
    ("yellow",         r"\byellow\b"),
    ("mini_diamond",   r"mini[- ]?diamond"),
    ("green_sapphire", r"green\s*sapphire"),
    ("green_lava",     r"green\s*lava"),
    ("green_reptilian", r"green\s*reptilian"),
    ("green",          r"\bgreen\b"),
    ("sapphire",       r"\bsapphire\b"),
    ("purple_mojo",    r"purple\s*mojo"),
    ("purple",         r"\bpurple\b"),
    ("speckle",        r"\bspeckle\b"),
    ("blue_raywave",   r"blue\s*raywave"),
    ("blue_reptilian", r"blue\s*reptilian"),
    ("blue",           r"\bblue\b"),
    ("aqua_mojo",      r"aqua\s*mojo"),
    ("mojo",           r"\bmojo\b"),
    ("packfractor",    r"packfractor"),
    ("wave",           r"\bwave\b"),
    ("black",          r"\bblack\b"),
    ("red",            r"\bred\b"),
    ("superfractor",   r"superfractor"),
    ("refractor",      r"refractor"),
    ("purple",         r"\bpurple\b"),   # catch-all repeats
    ("blue",           r"\bblue\b"),
    ("green",          r"\bgreen\b"),
]
_REFRACTOR_MULT = 1.8  # PP baseline for untagged chromes


def load_pp_multipliers():
    """PP print-odds rail (data provenance: pp_checklists_2026-11-13.json, PP TWMA multiples).
    Returns (mult_by_key, numbered_keys). mult_by_key maps normalized lane keys ->
    rung multiplier (2026 Bowman Chrome operating set, 2025 fallback)."""
    try:
        d = json.load(open(PP_MULT_PATH, encoding="utf-8"))
    except Exception:
        return {}, set()
    mult, numbered = {}, set()
    for sec in ("bowman_chrome_2026", "bowman_2025"):
        try:
            rows = d[sec]["multipliers"]
        except Exception:
            continue
        for row in rows:
            name, m = row[0], row[1]
            key = name.lower().split("/")[0].strip()
            if key not in mult:
                mult[key] = float(m)
            if "/" in name:
                numbered.add(key)
    mult.setdefault("refractor", _REFRACTOR_MULT)
    return mult, numbered


def detect_lane(title_l):
    for key, pat in LANE_PATTERNS:
        if re.search(pat, title_l):
            return key
    return "base"


def load_roster_names():
    d = json.load(open(ROSTER_PATH, encoding="utf-8"))
    names = []
    for sec in ("hitters", "pitchers"):
        for row in d.get(sec, []):
            names.append((row["name"], row.get("lvl", ""), float(row.get("age") or 0)))
    return names


def rotate_slice(names, n):
    state = {}
    try:
        state = json.load(open(STATE_PATH, encoding="utf-8"))
    except Exception:
        pass
    idx = int(state.get("next_index", 0))
    if idx >= len(names):
        idx = 0
    sl = names[idx: idx + n]
    nxt = idx + n
    if nxt >= len(names):
        nxt = 0
    try:
        json.dump({"next_index": nxt, "last_run": time.strftime("%Y-%m-%d %H:%M")},
                  open(STATE_PATH, "w", encoding="utf-8"))
    except Exception:
        pass
    return sl


def bd_fetch(query, token):
    """Live-ask eBay search (NO sold filters) via BrightData web_unlocker1. Returns HTML str or ''. """
    from urllib.parse import quote_plus
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}&_sop=10&_ipg=60"
    payload = json.dumps({"zone": BD_ZONE, "url": ebay_url, "format": "raw"}).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for attempt in (1, 2):
        try:
            req = requests.post(BD_URL, data=payload, headers=headers, timeout=120)
            if req.status_code == 200 and req.text.strip():
                html = req.text
                if "global adaptive rate limit" in html:
                    time.sleep(6)
                    continue
                return html
        except Exception:
            time.sleep(4)
    return ""


def extract_price(text):
    m = re.search(r"\$\s*([\d,]{1,7}(?:\.\d{1,2})?)", text or "")
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def parse_listings(html, name_l):
    """s-card law parse: s-item/s-card items, sponsored + shop-ad filtered. Ask rows only."""
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []
    items = soup.find_all(lambda tag: tag.name in ("li", "div") and tag.get("class")
                          and any(c in ("s-item", "s-card") for c in tag.get("class")))
    out = []
    seen_ids = set()
    for it in items:
        text = it.get_text(" | ", strip=True)
        low = text.lower()
        # shop-ad filter
        if "shop on ebay" in low or "sponsored" in low.split("|")[0:3].__str__():
            is_spon = False
            for sp in it.find_all(["span", "div"]):
                if sp.get_text(strip=True).lower() == "sponsored":
                    is_spon = True
                    break
            if "shop on ebay" in low or is_spon:
                continue
        title_el = it.find(class_=lambda c: c and "title" in c)
        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue
        if title.lower().startswith("new listing"):
            title = title[11:].strip()
        if title.lower().endswith("opens in a new window or tab"):
            title = title[:-28].strip()
        if title.lower().startswith("shop on ebay"):
            continue
        if name_l.split()[0].lower() not in title.lower():
            continue  # name pollution
        m = re.search(r"/itm/(\d+)", (it.find("a", href=True) or {}).get("href", "")
                      if it.find("a", href=True) else "")
        link = it.find("a", class_=lambda c: c and "link" in c)
        href = link.get("href", "") if link else ""
        mid = re.search(r"/itm/(\d+)", href) or re.search(r"/itm/(\d+)", text)
        item_id = (mid.group(1) if mid else f"{abs(hash(title)) % 10**12}")
        if item_id in seen_ids:
            continue
        price = extract_price(it.find(class_=lambda c: c and "price" in c).get_text(strip=True)
                              if it.find(class_=lambda c: c and "price" in c) else text)
        if not price or price <= 0:
            continue
        mb = re.search(r"(\d+)\s*bids?\b", low)
        out.append({"item_id": item_id, "title": title, "price": price,
                    "bids": int(mb.group(1)) if mb else 0,
                    "url": href or (f"https://www.ebay.com/itm/{item_id}" if mid else "")})
        seen_ids.add(item_id)
    return out


def load_liquidity(names):
    """SS250.51 liquidity-gate input: CH total-sales-by-player, 30d window.

    Returns {name_lower: n_sales_30d}; missing/failed entries = None
    (treated as unknown -> listed but NOT gated, honest-fail open side).
    A name with n < LIQ_MIN = the DEAD-LANE class: asks price nothing
    (Thompson-class mirage never again reaches the founder's phone).
    """
    out = {}
    try:
        key = open(CH_KEY_PATH, encoding="utf-8").read().strip()
    except Exception:
        return out  # empty = unknown for all -> gate degrades open, logged
    try:
        resp = requests.post(CH_SALES_URL, json={"players": list(names), "days": 30},
                             headers={"X-API-Key": key,
                                      "User-Agent": "CardScout/1.0 (+https://cardscout.pro)"},
                             timeout=30)
        data = resp.json()
        for entry in data.get("results", []):
            out[str(entry.get("player", "")).lower()] = entry.get("total_sales")
    except Exception as e:
        print(f"[FINDER] liquidity fetch failed ({e}) - gate open, honest-fail")
    return out


def load_rung_liquidity(names):
    """SS250.56 V2 upgrade: PER-RUNG liquidity (the law names the liquidity on
    the TARGET RUNG, not the player). Player-level totals overcredit names
    whose liquidity lives in OTHER lanes (Hope 506-player vs 62-auto; the
    Thompson black-auto row can pass on other-lane sales).

    Uses POST /v1/cards/card-search per name (1 call/name; <=8/night in
    budget), sums 30d sales across the auto rows only (the finder's lane
    class). Missing rows = 0 = the honest dead-lane; fetch fail = None =
    honest-fail open. Returns {name_lower: auto_30d}.
    """
    out = {}
    try:
        key = open(CH_KEY_PATH, encoding="utf-8").read().strip()
    except Exception:
        return out
    headers = {"X-API-Key": key, "User-Agent": "CardScout/1.0 (+https://cardscout.pro)"}
    for name in names:
        try:
            resp = requests.post("https://api.cardhedger.com/v1/cards/card-search",
                                 json={"player": name, "page": 1},
                                 headers=headers, timeout=30)
            cards = (resp.json() or {}).get("cards") or []
            auto_30d = sum((c.get("30 Day Sales") or 0) for c in cards
                           if "auto" in (c.get("description") or "").lower())
            out[name.lower()] = auto_30d
        except Exception:
            out[name.lower()] = None  # unknown = honest-fail open
    return out


def evaluate(row, name, lvl, mult_by_key, numbered_keys, liq=None):
    """Returns (pass_dict or None). Criteria stack: trifecta + <$15/lev + gold-floor."""
    t = row["title"].lower()
    lane = detect_lane(t)
    mult = mult_by_key.get(lane) or mult_by_key.get(lane.replace("_", " ")) or mult_by_key.get(lane.replace("_", "-"))
    if mult is None:
        mult = _REFRACTOR_MULT
    has_first = ("1st" in t) or ("cpa" in t and "bowman" in t)
    has_auto = ("auto" in t) or ("signed" in t) or (" sig " in t)  # parse-law regex
    serial_in_title = bool(re.search(r"\b\d{1,3}\s*/\s*\d{1,3}\b", t))
    numbered_lane = lane in numbered_keys or lane.replace("_", " ") in numbered_keys
    trifecta = has_first and has_auto and (serial_in_title or numbered_lane)
    price = row["price"]
    per_lev = price / mult if mult else None
    tags = []
    # SS250.51 liquidity-gate (REQUIRED input): known n < 5/30d = dead lane.
    # Unknown (fetch failed / no CH row) = honest-fail open, never silent-block.
    if liq is not None and liq < LIQ_MIN:
        return None
    if trifecta and per_lev is not None and per_lev < PRICE_PER_LEV_CAP:
        tags.append({"tag": "BUY-BAND", "per_lev": round(per_lev, 2),
                     "note": f"trifecta 1st x auto x serial @ ${per_lev}/lev < $15 (SS250.23)"})
    if lane == "gold" and has_first and has_auto and str(lvl).upper() in ("AA", "AAA") and price <= GOLD_FLOOR:
        tags.append({"tag": "BELOW-FLOOR", "per_lev": round(per_lev, 2) if per_lev else None,
                     "note": f"gold-1st-auto @ ${price:.0f} vs $250 floor ({lvl}) (SS250.28)"})
    if not tags:
        return None
    return {"lane": lane, "mult": mult, "tags": tags, "player": name}


def smoketest_gate():
    return os.environ.get("FIND_SMOKE") == "1"


def post_discord(content):
    try:
        tok = [l for l in open(ENV_PATH, encoding="utf-8", errors="replace")
               if l.strip().startswith("DISCORD_BOT_TOKEN")][0].strip().split("=", 1)[1].strip().strip('"')
        H = {"Authorization": "Bot " + tok, "User-Agent": DISCORD_UA}
        r = requests.post(f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL}/messages",
                          headers=H, json={"content": content[:1900]}, timeout=20)
        return r.status_code in (200, 201)
    except Exception:
        return False


def main():
    smoke = smoketest_gate()
    if not smoke:
        try:
            import bs4  # noqa  (ensures the reexec above resolved)
        except ImportError:
            raise
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mult_by_key, numbered_keys = load_pp_multipliers()
    if not mult_by_key:
        print("[FINDER] PP multipliers MISSING - aborting honest-fail")
        sys.exit(1)
    try:
        token = open(TOKEN_PATH, encoding="utf-8").read().strip()
    except Exception:
        print("[FINDER] BD token MISSING at", TOKEN_PATH, "- aborting honest-fail")
        sys.exit(1)

    all_names = load_roster_names()
    n_names = 1 if smoke else NAMES_PER_NIGHT
    roster_slice = rotate_slice(all_names, n_names)

    seen = {}
    try:
        seen = json.load(open(SEEN_PATH, encoding="utf-8"))
    except Exception:
        pass

    calls = 0
    findings = []
    log_rows = []

    # SS250.51 + SS250.56: liquidity-gate input — PER-RUNG (V2) preferred
    # (the auto-lane 30d on the actual instrument class), player-level
    # fallback if the V2 fetch comes back empty. 1 CH call/name, before
    # any BrightData spend (the gate must gate the SPEND).
    slice_names = [n for n, _, _ in roster_slice]
    liq_map = load_rung_liquidity(slice_names)
    if not any(v is not None and v > 0 for v in liq_map.values()):
        liq_map = load_liquidity(slice_names)  # fallback: player-level
    log_rows.append({"run_ts": time.strftime("%Y-%m-%d %H:%M"),
                     "event": "liquidity-slice", "mode": "rung-v2", "liq": liq_map})
    for name, lvl, age in roster_slice:
        if calls >= BD_CALL_CAP:
            log_rows.append({"player": name, "skipped": "call budget exhausted", "calls": calls})
            break
        name_l = name.lower()
        shapes = RUNG_SHAPES[:2] if smoke else RUNG_SHAPES
        per_player_passes = []
        for lane_key, qtpl in shapes:
            if calls >= BD_CALL_CAP:
                break
            q = qtpl.format(n=name)
            html = bd_fetch(q, token)
            calls += 1
            if not html:
                log_rows.append({"query": q, "status": "fetch-failed"})
            else:
                for row in parse_listings(html, name_l):
                    ev = evaluate(row, name, lvl, mult_by_key, numbered_keys,
                                  liq_map.get(name.lower()))
                    if ev and row["item_id"] not in seen:
                        rec = {**row, **{k: ev[k] for k in ("lane", "mult", "tags")}, "player": name, "lvl": lvl}
                        findings.append(rec)
                        seen[row["item_id"]] = {"ts": time.time(), "player": name}
                        per_player_passes.append(rec)
            time.sleep(QUERY_SLEEP)
        if per_player_passes and not smoke:
            lines = [f"[FINDER {time.strftime('%m-%d %H:%M')}] {name} ({lvl}) - {len(per_player_passes)} pass(es):"]
            for r in per_player_passes[:6]:
                tags = "; ".join(t["tag"] for t in r["tags"])
                lev = next((t["per_lev"] for t in r["tags"] if t["per_lev"] is not None), "-")
                lines.append(f"- ${r['price']:.2f} {r['lane']} auto {tags} ${lev}/lev {r['bids']}b")
                lines.append(f"  {r['url']}")
                lines.append(f"  {r['title'][:140]}")
            ok = post_discord("\n".join(lines)[:1900])
            log_rows.append({"player": name, "posted": len(per_player_passes[:6]), "discord": ok})

    # persist
    try:
        with open(OUT_DIR / ("smoke_findings.json" if smoke else "finder_results.jsonl"),
                  ("w" if smoke else "a"), encoding="utf-8") as f:
            if smoke:
                json.dump(findings, f, indent=1)
            else:
                for r in findings:
                    f.write(json.dumps(r) + "\n")
    except Exception:
        pass
    if len(seen) > 6000:
        for k in sorted(seen, key=lambda k: seen[k].get("ts", 0))[: len(seen) - 5000]:
            seen.pop(k, None)
    try:
        json.dump(seen, open(SEEN_PATH, "w", encoding="utf-8"))
    except Exception:
        pass
    try:
        log_rows.append({"run": time.strftime("%Y-%m-%d %H:%M"), "calls": calls, "players": len(roster_slice),
                         "findings": len(findings), "smoke": smoke})
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            for r in log_rows:
                f.write(json.dumps(r) + "\n")
    except Exception:
        pass
    # silent-healthy: stdout ONLY when smoke test or findings exist
    if smoke or findings:
        print(json.dumps({"smoke": smoke, "calls": calls, "players_processed": len(roster_slice),
                          "findings": len(findings),
                          "posted_to_discord": smoke is False}, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
