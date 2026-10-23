"""
CardScout EMAIL ALERTS — the CCC loop closer (band on web, alert by email, click back).
Built Oct 23, 2026. Builder: Hermes-lane. Verify: Hermes.

Brief context: CARD-PAGE-BUILD-SPEC-v1.md §EMAIL-ALERTS ASSESSMENT (2ec6351):
- Provider: Brevo-class SMTP/API (free tier 300/day ≈ 750 alert-subscribers)
- Sender: alerts@cardscout.pro (domain-auth SPF/DKIM/DMARC done at setup)
- Trigger: reuses the MWF cadence outputs (customer_alerts_{cid}.json) — same
  alert stream that feeds Discord for beta users, now also email for everyone.
- EPN tagging: the SAME generate_ebay_url path (campid from .env) — the MPA
  guard inherits: no campaign ID = plain links everywhere.
- CAN-SPAM: every email carries the one-click unsubscribe token + the
  four-clause disclosure footer (privacy + no-advice + user-agency).
- NEVER: advice in the body ("what has sold, not what to buy"), never band
  threshold numbers, never positions, never engine output. Market-state only.

CONFIG (.env or env):
  BREVO_API_KEY      = the Brevo API key (never committed)
  ALERT_EMAIL_FROM   = alerts@cardscout.pro
  ALERT_EMAIL_FROM_NAME = Card Scout
  BASE_URL           = https://cardscout.pro
  UNSUB_URL          = https://cardscout.pro/unsubscribe (one-click GET token)

USAGE:
  python email_alerts.py --customer <customer_id>   (one customer dry-run/build)
  python email_alerts.py --all [--send]             (all enabled; --send actually sends;
                                                     default = DRY RUN, builds + prints)
Exit codes: 0 ok, 1 config error, 2 send error (per-email logged, never raises to top).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from email.utils import parseaddr
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# CONFIG (env-first; .env file fallback read-in-place, never moved/printed)
# ---------------------------------------------------------------------------
_ENV_CACHE: dict = {}


def env_val(key: str, ttl: float = 600.0) -> str | None:
    now = __import__("time").time()
    if key in _ENV_CACHE and now - _ENV_CACHE[key]["read_at"] < ttl:
        return _ENV_CACHE[key]["value"]
    val = os.environ.get(key)
    if val is None:
        try:
            txt = (REPO_DIR / ".env").read_text(encoding="utf-8", errors="ignore")
            m = re.search(rf"^\s*{re.escape(key)}\s*=\s*['\"]?([^\n\r'\"]+)", txt, re.M)
            val = m.group(1).strip() if m else None
        except OSError:
            val = None
    val = (val or "").strip() or None
    _ENV_CACHE[key] = {"value": val, "read_at": now}
    return val


def _fmt_dollars(x: float | int | None) -> str:
    try:
        f = float(x)
        return f"${f:,.2f}" if f >= 100 else f"${f:.2f}"
    except (TypeError, ValueError):
        return "$0.00"


# ---------------------------------------------------------------------------
# CAN-SPAM + disclosure footer (P12-aligned: same clauses as the web surface)
# ---------------------------------------------------------------------------
DISCLOSURE_HTML = (
    '<hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">'
    '<p style="font-size:12px;color:#6b7280">'
    'This alert is a market-information service: it shows what the community\'s own '
    'pulls say has sold — never advice on what to buy. eBay listings and content are '
    'shown as-is; clicking through and any purchase is your decision and your '
    'transaction. We earn a small commission (disclosed) from eBay qualifying '
    'purchases and take no part after the click. '
    'We are not affiliated with eBay or any grading service.</p>'
    '<p style="font-size:12px;color:#6b7280">Your Google/subscription information is '
    'used solely for delivering your alerts — never sold, shared, or exported. '
    '<a href="{unsub}">Unsubscribe</a> (one click, immediate).</p>'
)


def render_footer(unsub_token: str | None) -> str:
    if unsub_token:
        unsub = env_val("UNSUB_URL") or "https://cardscout.pro/unsubscribe"
        return DISCLOSURE_HTML.format(unsub=f"{unsub}?t={urllib.parse.quote(unsub_token)}")
    # dry-run without token: still render a placeholder-marked footer
    return DISCLOSURE_HTML.format(unsub="(unsubscribe link: requires token)")


# ---------------------------------------------------------------------------
# EPN tagging (same rule as band_pages: no campid = plain link)
# ---------------------------------------------------------------------------
def epn_tag(view_url: str, email: str) -> tuple[str, bool]:
    campid = env_val("EPN_CAMPAIGN_ID")
    if not campid:
        return view_url, False
    params = {
        "mkcid": "1", "mkrid": "711-53200-19255-0", "siteid": "0",
        "campid": campid, "customid": re.sub(r"[^a-z0-9]+", "-", (email or "anon").lower())[:40],
        "toolid": "10001", "mkevt": "1",
    }
    sep = "&" if "?" in view_url else "?"
    return view_url + sep + urllib.parse.urlencode(params), True


# ---------------------------------------------------------------------------
# EMAIL CONTENT (from the standard alert JSON — no new data path)
# ---------------------------------------------------------------------------
def alert_row_html(a: dict, email: str) -> tuple[str, bool]:
    player = str(a.get("player", "Unknown"))
    lane = str(a.get("lane", ""))
    price = a.get("price")
    call = str(a.get("call", ""))
    evidence = str(a.get("evidence", ""))
    query = f"{player} {lane}".strip()

    url, tagged = epn_tag(
        f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote_plus(query)}&_sop=16",
        email,
    )
    band_note = ""
    # market-state only: show the OBSERVED last verified print context, never thresholds
    ctx = a.get("context") or a.get("baseline")
    if ctx:
        band_note = f'<div style="color:#6b7280;font-size:12px">Market context: {str(ctx)[:120]}</div>'

    link_txt = "View live eBay listings" + (" (affiliate link)" if tagged else "")
    row = (
        f'<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin:10px 0">'
        f'<div style="font-weight:600">{player} — {lane}</div>'
        f'<div>Last print: <strong>{_fmt_dollars(price)}</strong> · {call}</div>'
        f'{band_note}'
        f'<div style="margin-top:6px"><a href="{url}">{link_txt}</a></div>'
        f'</div>'
    )
    return row, tagged


def build_email(email: str, alerts: list[dict]) -> tuple[str, str, int, int]:  # subj, html, sent_rows, tagged_n
    lines = []
    tagged_n = 0
    for a in alerts:
        if str(a.get("call", "")) in ("QUIET", "NO-VALID-PRINT", "UNMEASURED"):
            continue  # honesty states never render as deals
        row, tagged = alert_row_html(a, email)
        lines.append(row)
        tagged_n += 1 if tagged else 0
    n = len(lines)
    subj = f"Card Scout — {n} new market signal{'s' if n != 1 else ''}" if n else "Card Scout — quiet markets this cycle"
    if n == 0:
        body = ("<p>No market signals this cycle. The bands are holding — "
                "which is itself the market talking.</p>")
    else:
        body = (
            f'<p>Market signals from the community corpus (what has sold, '
            f'never advice on what to buy):</p>' + "".join(lines)
        )
    token = None  # Phase-2: per-user unsub token from ledger; dry runs use placeholder
    # Brief 3 Job 4: generate the REAL CAN-SPAM token when the caller is a real
    # address (dry runs with placeholder addresses keep the placeholder footer).
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
        from contributor_bp import make_unsub_token  # noqa: E402
        if email and "@placeholder.local" not in email:
            token = make_unsub_token(email)
    except Exception:
        token = None  # honest fallback: placeholder footer, never a crash
    return subj, f"<html><body>{body}{render_footer(token)}</body></html>", n, tagged_n


# ---------------------------------------------------------------------------
# SENDER (Brevo HTTP API by default; SMTP2GO/SES would swap only this function)
# ---------------------------------------------------------------------------
def send_email_brevo(to_email: str, subject: str, html: str) -> tuple[bool, str]:
    api_key = env_val("BREVO_API_KEY")
    sender = env_val("ALERT_EMAIL_FROM") or "alerts@cardscout.pro"
    from_name = env_val("ALERT_EMAIL_FROM_NAME") or "Card Scout"
    if not api_key:
        return False, "BREVO_API_KEY not configured"
    # address sanity (CAN-SPAM basics: valid To header)
    _, addr = parseaddr(to_email)
    if "@" not in addr:
        return False, f"invalid recipient: {addr!r}"
    payload = json.dumps({
        "sender": {"name": from_name, "email": sender},
        "to": [{"email": addr}],
        "subject": subj_fix(subject),
        "htmlContent": html,
        **({"replyTo": {"email": rt}} if (rt := env_val("REPLY_TO_EMAIL")) else {}),
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return (resp.status == 201), f"HTTP {resp.status}"
    except Exception as e:  # per-email log, never raise to top
        return False, f"send error: {e}"


def subj_fix(subject: str) -> str:
    return subject


def send_unsubscribe_confirmation(to_email: str, resub_token: str | None = None) -> bool:
    """Brief 5 Job C — ONE short transactional confirmation email when the
    opt-out FLIPS (the /unsubscribe route calls this only on a fresh flip).
    Body: 3 lines (alerts stopped · bands stay public · one-click resubscribe
    with their token) + the one-liner; NO full footer on a transactional note.
    Discipline: never raises; BREVO_API_KEY missing = skip silently (log-only),
    like the send path; send errors logged, never raised."""
    try:
        if not to_email or "@placeholder.local" in to_email:
            return False
        if not env_val("BREVO_API_KEY"):
            print("[unsub-confirm] skip (log-only): BREVO_API_KEY not configured")
            return False
        # fresh capability token preferred (helper read from contributor_bp);
        # the URL's token is a valid fallback; no token at all = drop the link
        tok = resub_token
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
            from contributor_bp import make_unsub_token  # noqa: E402
            tok = make_unsub_token(to_email)
        except Exception:
            pass
        base = env_val("UNSUB_URL") or "https://cardscout.pro/unsubscribe"
        resub = base.replace("/unsubscribe", "/resubscribe")
        link = (f'{resub}?t={urllib.parse.quote(tok)}') if tok else None
        lines = [
            "<p>Your alerts have stopped immediately.</p>",
            "<p>The bands stay public at cardscout.pro — free, no account needed.</p>",
        ]
        if link:
            lines.append(f'<p>Changed your mind? <a href="{link}">Re-subscribe</a>'
                         " — one click, immediate.</p>")
        oneliner = ('<p style="font-size:12px;color:#6b7280">A market-information '
                    "service: what has sold, never advice on what to buy.</p>")
        html = "<html><body>" + "".join(lines) + oneliner + "</body></html>"
        ok, msg = send_email_brevo(to_email, "Card Scout — you're unsubscribed", html)
        print(f"[unsub-confirm] {to_email}: {'sent' if ok else f'not sent ({msg})'}")
        return ok
    except Exception as e:  # transactional nicety: logged, never raised
        print(f"[unsub-confirm] error (never raised): {type(e).__name__}: {e}")
        return False


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def load_alerts_for(customer_id: str, reports_dir: Path | None = None) -> list[dict]:
    # 1.0's reports live in the 2.0 data_lake (same-machine pattern banked):
    rd = Path(reports_dir or "C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/reports")
    p = rd / f"customer_alerts_{customer_id}.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Card Scout email alerts (CCC loop closer)")
    ap.add_argument("--customer", help="single customer_id build/send")
    ap.add_argument("--all", action="store_true", help="all enabled customers")
    ap.add_argument("--send", action="store_true", help="actually send (default = DRY RUN)")
    ap.add_argument("--reports-dir", default=str(REPO_DIR / "reports"))
    args = ap.parse_args()

    if args.customer:
        alerts = load_alerts_for(args.customer)
        subj, html, n, tagged_n = build_email("jim@example.com", alerts)
        print(f"[DRY] {args.customer}: {n} alert rows, {tagged_n} tagged links; subject: {subj}")
        out = Path("C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/reports") / f"email_draft_{args.customer}.html"
        out.write_text(html, encoding="utf-8")
        print(f"[DRY] email built -> {out}")
        if args.send:
            ok, msg = send_email_brevo(env_val("ALERT_EMAIL_FROM") or "", subject := subj, html)
            print("send:", "OK" if ok else f"FAIL ({msg})")
            return 0 if ok else 2
        return 0

    if args.all:
        # iterate the enabled customers (the 1.0 DB pattern; placeholders excluded
        # by the same rule digest_delivery uses)
        import sqlite3
        # opt-out filter (CAN-SPAM closure): contributor ledger flags, if present.
        # Brief 4 J3: path env-redirectable so the battery can prove the skip
        # end-to-end without touching the live ledger.
        optouts: set[str] = set()
        try:
            _ledger = Path(os.environ.get(
                "CONTRIBUTOR_LEDGER_PATH",
                r"C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/contributor_ledger.json"))
            _led = json.loads(_ledger.read_text(encoding="utf-8"))
            optouts = {e for e, c in (_led.get("contributors") or {}).items() if c.get("opt_out")}
        except (OSError, ValueError):
            pass
        db = REPO_DIR / "card_scout.db"
        if not db.exists():
            print("card_scout.db not found; nothing to do", file=sys.stderr)
            return 1
        import sqlite3
        con = sqlite3.connect(str(db))
        rows = con.execute(
            "SELECT customer_id, email, tier FROM customers WHERE email NOT LIKE '%@placeholder.local'"
        ).fetchall()
        rc = 0
        for cid, email, tier in rows:
            if email in optouts:
                print(f"  skip (opted-out): {cid} ({email})")
                continue
            alerts = load_alerts_for(cid, Path(args.reports_dir))
            subj, html, n, tagged_n = build_email(email, alerts)
            print(f"[DRY] {cid} ({email}): {n} rows, {tagged_n} tagged; subject: {subj}")
            if args.send:
                # Brief 4 J3 hardening: ONE send path (send_email_brevo handles
                # config errors per-address; the loop never aborts wholesale).
                ok, msg = send_email_brevo(email, subj, html)
                print(f"  send: {'OK' if ok else f'FAIL ({msg})'}")
                if not ok:
                    rc = 2
        return rc

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())