"""
CAMEL FIRE-3 UNIT A — personalized alert delivery for public users (Nov 11).

Extends the verified Brevo send helper (scripts/email_alerts.py send_email_brevo)
to PUBLIC users with these hard rules:
1. SENDS DEFAULT OFF: PUBLIC_USER_ALERTS_ENABLED unset/false = build-only (dry run).
2. Recipient = the user's own Google email (from their storage file); we never
   send to any email the user didn't sign in with.
3. Content = TOOLING layer only: "AT YOUR PRICE" rows the user's own prices
   produced. No advice language, no engine output, no suggested levels.
4. The unsubscribe footer is REQUIRED on every public-user email (CAN-SPAM;
   the root /unsubscribe endpoint already exists from the contributor surface).
5. Cadence: max 1 email per user per UTC DAY (state per user in their own file).
6. Dry-run render = JSON printed; send = POST with per-email error log, never raises.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DASH_DIR = Path(__file__).resolve().parent
if str(DASH_DIR) not in sys.path:
    sys.path.insert(0, str(DASH_DIR))
sys.path.insert(0, str(DASH_DIR.parent / "scripts"))

import user_state as US  # noqa: E402 (flat import matching prod boot)


def env_val(name: str) -> str | None:
    v = os.environ.get(name)
    return v.strip() if v else None


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _sent_today(user: dict) -> bool:
    return user.get("last_alert_utc", "1970")[:10] >= _utc_today()


def _mark_sent(email: str) -> None:
    data = US.load_user(email)
    data["last_alert_utc"] = datetime.now(timezone.utc).isoformat()
    US.save_user(email, data)


_ALERT_TEMPLATE_HTML = """\
<html><body style="font-family:Segoe UI,Arial,sans-serif; color:#1a1a2e;">
<h2 style="margin:0 0 6px;">Your price watch</h2>
<p style="margin:0 0 14px;">Row(s) on your watchlist reached a level you set:</p>
{rows_html}
<p style="color:#666; font-size:12px; margin-top:18px;">
Your prices are yours — we never suggest, never advise. We just watch. Manage anytime:
<a href="{base}/me">{base}/me</a></p>
<p style="color:#888; font-size:11px;">
Don't want these? <a href="{unsub_url}">Unsubscribe</a>.</p>
</body></html>"""


def render_email(email: str) -> tuple[str | None, list[dict]]:
    """Build the personalized email HTML from the user's own watchlist.
    Returns (html_or_None, qualifying_rows). NO sending here."""
    payload = US.build_alert_payload(email)
    if not payload:
        return None, []
    rows_html = "".join(
        f"<p style='margin:4px 0;'><strong>{r['player']}</strong> "
        f"<span style='color:#555;'>· {r['lane']}</span> — reached your level "
        f"({r.get('your_price_low') or r.get('your_price_high')})</p>"
        for r in payload["rows"]
    )
    base = env_val("BASE_URL") or "https://cardscout.pro"
    unsub_url = env_val("UNSUB_URL") or f"{base}/unsubscribe"
    html = _ALERT_TEMPLATE_HTML.format(rows_html=rows_html, base=base, unsub_url=unsub_url)
    return html, payload["rows"]


def dispatch(email: str, send_enabled: bool | None = None) -> dict:
    """One user's full cycle: compute → dedupe-day → (maybe) render → (maybe) send.
    Never raises; every outcome returned in the report dict."""
    report = {"email": email, "stage": ""}
    data = US.load_user(email)
    if not data.get("watchlist"):
        report.update(stage="empty", ok=True)
        return report
    if _sent_today(data):
        report.update(stage="already_sent_today", ok=True)
        return report
    html, rows = render_email(email)
    if html is None:
        report.update(stage="nothing_qualifies", ok=True)
        return report
    if send_enabled is None:
        flag = (env_val("PUBLIC_USER_ALERTS_ENABLED") or "").strip().lower()
        send_enabled = flag in ("1", "true", "yes", "on")
        if not send_enabled:
            import camel_flags
            send_enabled = camel_flags.user_alerts_enabled()  # flags-file layer
    report.update(rows=rows, qualifies=True)
    if not send_enabled:
        report.update(stage="dry_run", ok=True, sent=False)
        report["preview_html_head"] = html[:200] + "..."
        return report
    from email_alerts import send_email_brevo  # the verified helper (read-in-place key)
    subject = f"Card Scout — your price watch ({len(rows)} row{'s' if len(rows)!=1 else ''})"
    ok, msg = send_email_brevo(email, subject, html)
    if ok:
        _mark_sent(email)
    report.update(stage=("sent" if ok else "send_failed"), ok=ok, sent=ok, send_detail=msg)
    return report


def run_all_public_users(send_enabled: bool | None = None) -> list[dict]:
    """Sweep every stored public user (their own file governs; no email is
    contacted unless their watchlist exists AND the dedupe-day passes)."""
    reports = []
    if not US.USERS_DIR.exists():
        return reports
    for f in sorted(US.USERS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            email = data.get("email")
            if email and "*" not in email:
                reports.append(dispatch(email, send_enabled))
        except (OSError, ValueError, KeyError):
            continue
    return reports


if __name__ == "__main__":
    # CLI: dry-run by default (prints the report JSON); --send = founder explicit
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="actually send (founder-only)")
    args = ap.parse_args()
    results = run_all_public_users(send_enabled=args.send)
    print(json.dumps(results, indent=1))
