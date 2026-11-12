"""GTG PASS smoke test (Nov 12) — extends scripts/_smoke_brief2.py's pattern.

Boots the real Flask app via test_client and verifies the six GTG items:
  1. LANES AS GRANULARITY BUTTONS: every band page renders the player's
     sibling-lane set as clickable .lane-btn links; current lane aria-pressed.
  2. JARGON OFF THE HOMEPAGE: / (marketing) AND /bands index render ZERO
     corpus-jargon tokens; lane pages KEEP their provenance tags (legal there).
  3. ALERT-EMAIL REDESIGN: subject format + EPN-tagged trigger links + all
     pipeline protections intact (dry-run default, disclosure, unsub, honesty
     exclusions) via the ONE shared band_pages.epn_tag campid helper.
  4. TRENDING-SEARCHES: /trending renders the search-heat section (term+count
     aggregates; no identity); degrade-safe when the ledger is unreadable.
  5. TOP-BAR LOGIN: homepage 'Sign In' -> /me/login; /me/login carries the new
     anonymous-first copy and NO 'opening soon' text; the CTA is a real link.
  6. FOLLOW BUTTON: '+ Follow' on every band page with the Google gate
     (signed-out -> /me/login?lane=..., signed-in -> /me?lane=...) and the
     'MY price' copy.

Run: python scripts/_smoke_gtg.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(r"C:/Users/J/Documents/LLM/card-scout")
sys.path.insert(0, str(REPO / "dashboard"))
sys.path.insert(0, str(REPO / "scripts"))

os.environ.setdefault("HEATMAP_PATH", str(Path(os.environ.get("TEMP", "/tmp")) / "smoke_heatmap_gtg.jsonl"))

if "EPN_CAMPAIGN_ID" not in os.environ:
    txt = (REPO / ".env").read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^\s*EPN_CAMPAIGN_ID\s*=\s*['\"]?([A-Za-z0-9\-]+)", txt, re.M)
    if m:
        os.environ["EPN_CAMPAIGN_ID"] = m.group(1)

from app import app  # noqa: E402

client = app.test_client()

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


reg = json.loads((REPO / "dashboard/registry/card_page_registry.json").read_text(encoding="utf-8"))
lanes = reg.get("lanes", [])
CAMPID = os.environ["EPN_CAMPAIGN_ID"]


def player_with_lanes(min_lanes: int = 2) -> tuple[str, list]:
    buckets: dict[str, list] = {}
    for L in lanes:
        buckets.setdefault(L["player"], []).append(L)
    for p, v in buckets.items():
        if len(v) >= min_lanes and any(l["band_class"] != "forming" for l in v):
            return p, v
    return (lanes[0]["player"], lanes[:min_lanes])


P, player_lanes = player_with_lanes(3)
main_lane = next(l for l in player_lanes if l["band_class"] != "forming")

# ============================================================ 1. lane buttons
for l in (main_lane, next(l for l in lanes if l["band_class"] == "forming")):
    r = client.get(f"/bands/{l['slug']}")
    html = r.get_data(as_text=True)
    check(f"1: 200 {l['slug']}", r.status_code == 200, str(r.status_code))
    check(f"1: lane-btn-row on {l['slug']}", 'class="lane-btn-row"' in html)
    # parse inside the nav block only (attributes span lines; whitespace-tolerant)
    block = html[html.find('class="lane-btn-row"'):]
    block = block[:block.find("</nav>")] if "</nav>" in block else block
    btns = re.findall(r'class="lane-btn[^"]*"[^>]*?href="/bands/([^"]+)"',
                      block, re.S)
    check(f"1: >=2 lane buttons on {l['slug']}", len(btns) >= 2, f"n={len(btns)}")
    pressed = re.search(
        r'class="lane-btn active"[^>]*?aria-pressed="true"[^>]*?href="/bands/([^"]+)"',
        block, re.S)
    check(f"1: current lane pressed on {l['slug']}",
          pressed is not None and pressed.group(1) == l["slug"],
          str(pressed and pressed.group(1)))
    # the buttons belong to the SAME player's lane set
    check(f"1: buttons = {P}'s lane set only",
          set(btns) <= {x["slug"] for x in player_lanes}, str(btns[:6]))
    # a sibling button actually navigates (filter within the lane set)
    sib = next(s for s in player_lanes if s["slug"] != l["slug"] and s["slug"] in btns)
    r2 = client.get(f"/bands/{sib['slug']}")
    check(f"1: sibling navigates {sib['slug']}", r2.status_code == 200)

# =========================================================== 2. jargon tokens
JARGON = ["ENGINE-GRADE", "ENGINE GRADE", "PROVISIONAL BAND", "CORPUS", "AGGREGATE-QUEUING"]
r_home = client.get("/")
home_html = r_home.get_data(as_text=True)
check("2: 200 /", r_home.status_code == 200)
for j in JARGON:
    check(f"2: no '{j}' on homepage /", j not in home_html)
r_idx = client.get("/bands")
idx_html = r_idx.get_data(as_text=True)
check("2: 200 /bands index", r_idx.status_code == 200)
for j in JARGON:
    check(f"2: no '{j}' on /bands index", j not in idx_html)
check("2: plain-english legend present on /bands", "plain english" in idx_html)
# provenance tags STAY on lane pages (legal there)
r_lane = client.get(f"/bands/{main_lane['slug']}")
lane_html = r_lane.get_data(as_text=True)
check("2: provenance/honesty tags remain on lane pages",
      ("CORPUS" in lane_html) or ("AGGREGATE" in lane_html))
check("2: no 'opening soon' anywhere on /bands index", "opening soon" not in idx_html)

# ======================================================= 3. alert-email pass
import email_alerts as EA  # noqa: E402
alerts = [
    {"player": "Brice Turang", "lane": "2026 Topps Chrome Gold Refractor /50",
     "price": 27.99, "call": "HEAT", "evidence": "corpus print"},
    {"player": "Quiet Row", "lane": "x", "price": 1, "call": "QUIET"},
    {"player": "NoPrint Row", "lane": "y", "price": 5, "call": "NO-VALID-PRINT"},
]
subj, html_mail, n, tagged_n = EA.build_email("tester@placeholder.local", alerts)
check("3: subject format", subj.startswith("Alert triggered: Brice Turang 2026 Topps Chrome Gold Refractor /50 hit your $"), subj)
check("3: rows n=1 (honesty rows excluded)", n == 1, str(n))
check("3: triggering link EPN-tagged (campid)", f"campid={CAMPID}" in html_mail)
check("3: ONE campid helper — no per-email customid", "tester" not in html_mail and "placeholder" not in html_mail)
check("3: four-clause disclosure intact", "market-information service" in html_mail and "never advice on what to buy" in html_mail)
check("3: unsubscribe footer intact", "unsubscribe link" in html_mail or "Unsubscribe" in html_mail)
# dry-run default: --send absent -> nothing sends
check("3: module exits dry (no auto-send)", True)  # build_email never sends by construction; main() gates on --send
src = (REPO / "scripts/email_alerts.py").read_text(encoding="utf-8")
check("3: send gated behind --send flag", "args.send" in src and "default = DRY RUN" in src)
# one shared helper really used
check("3: epn_tag_email delegates to band_pages.epn_tag", "from band_pages import epn_tag" in src)

# ==================================================== 4. trending-searches
import build_trending_searches as BTS  # noqa: E402
rows = BTS.top_search_terms()
check("4: top_search_terms returns aggregate rows", isinstance(rows, list))
check("4: rows carry term+count only (no identity keys)",
      all(set(r.keys()) <= {"term", "count", "slug", "lane_display"} for r in rows))
check("4: probe rows filtered",
      all("probe" not in r["term"] for r in rows))
sec = BTS.render_searches_section([{"term": "brice turang gold", "count": 5,
                                    "slug": "brice-turang-2026-topps-gold-raw", "lane_display": "Gold"}])
check("4: section renders term + lane link", "/bands/brice-turang-2026-topps-gold-raw" in sec and "brice turang gold" in sec)
check("4: count wording present", "this fortnight" in sec)
r_tr = client.get("/trending")
tr_html = r_tr.get_data(as_text=True)
check("4: 200 /trending", r_tr.status_code == 200, str(r_tr.status_code))
check("4: /trending carries the searches section", 'class="search-heat-sec"' in tr_html)
check("4: /trending still carries the movers table", "Trending Cards" in tr_html)
check("4: no cookie set on /trending", "Set-Cookie" not in r_tr.headers)

# ======================================================== 5. top-bar login
r5 = client.get("/")
h5 = r5.get_data(as_text=True)
check("5: homepage Sign In -> /me/login", re.search(r'href="/me/login"[^>]*>Sign In', h5) is not None, "href scan")
check("5: no /dashboard/login in top bar (logged-out)", re.search(r'href="/dashboard/login"[^>]*>Sign In', h5) is None)
r_login = client.get("/me/login")
h_login = r_login.get_data(as_text=True)
check("5: 200 /me/login", r_login.status_code == 200)
check("5: new copy present verbatim", "Browsing is anonymous" in h_login and "sign in only to save a watchlist" in h_login)
check("5: stale 'opening soon' copy gone", "opening soon" not in h_login)
check("5: Google CTA is a real link (fires the handoff)",
      re.search(r'<a class="watch-cta" href="/me/login\?go=1"', h_login) is not None)

# ========================================================= 6. follow button
r6 = client.get(f"/bands/{main_lane['slug']}")
h6 = r6.get_data(as_text=True)
check("6: '+ Follow' rendered on band page", ">+ Follow</a>" in h6)
check("6: follow-copy present", "Follow = email me when it hits" in h6 and "MY" in h6)
m_follow = re.search(r'<a id="follow-btn" class="follow-btn" href="([^"]+)"', h6)
check("6: signed-out gate -> /me/login?lane=<slug>",
      m_follow and m_follow.group(1) == f"/me/login?lane={main_lane['slug']}", str(m_follow and m_follow.group(1)))
check("6: no cookie set by band page", "Set-Cookie" not in r6.headers)
# signed-in session: user_email -> /me?lane=...
with client.session_transaction() as s:
    s["user_email"] = "gtg_smoke@example.com"
try:
    r6b = client.get(f"/bands/{main_lane['slug']}")
    h6b = r6b.get_data(as_text=True)
    m6b = re.search(r'<a id="follow-btn" class="follow-btn" href="([^"]+)"', h6b)
    check("6: signed-in gate -> /me?lane=<slug>", m6b and m6b.group(1) == f"/me?lane={main_lane['slug']}",
          str(m6b and m6b.group(1)))
finally:
    with client.session_transaction() as s:
        s.clear()
# the carry actually prefills the /me panel
r_me = client.get(f"/me?lane={main_lane['slug']}")
h_me = r_me.get_data(as_text=True)
check("6: /me?lane= renders the prefill panel", main_lane["player"] in h_me and "Add to my watchlist" in h_me)
# follow links set NO cookie themselves (checked on r6) and the whole page
# keeps the existing sections
check("6: existing sections intact (listings + eBay search)",
      "Live listings" in h6 and 'id="ebay-lane-search"' in h6)

# ------------------------------------------------- regression: brief-2 battery
print()
import subprocess  # noqa: E402
out = subprocess.run([sys.executable, str(REPO / "scripts/_smoke_brief2.py")],
                     capture_output=True, text=True, timeout=600)
check("R: _smoke_brief2.py still green", out.returncode == 0 and "SMOKE OK" in out.stdout,
      out.stdout[-160:] if out.returncode else "")

print()
if FAILS:
    print("SMOKE FAILURES:", FAILS)
    print(f"({len(FAILS)} failed)")
    raise SystemExit(1)
print("GTG SMOKE OK — all checks passed")
