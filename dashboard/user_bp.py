"""
PUBLIC USER SURFACES (render-side) — CAMEL FIRE-1.5 (Nov 11, 2026)

Spec: cardscout-2.0/For You/Plans/2026-11-11-camel-fire15-brief-walle.md
Identity: "CamelCamelCamel for trading cards" — a price tracker.
These are the /me shells: honest-empty watchlist page + the Google-login
explainer. Stubs by design: Fire-2 (Hugo lane) wires the stateful backend
into these exact templates.

LAWS carried (Fire-1 spec):
- Copy: NO forbidden tokens (fame/ladder/dislocation/trigger/engine/flag/opinion-
  words) in user-visible text. The pages say "your price" / "alert me at this
  price" — the USER sets their prices, we execute (user-agency law).
- Honest-empty: fresh visitor sees the real explainer — never a blank 200.
- Builders-add: no existing route modified; registration in app.py is additive
  (fire-tagged). Reused CSS vars only; no CDNs, no JS libs.
"""
from __future__ import annotations

from flask import Blueprint, render_template_string, request

bp = Blueprint("user", __name__)

# Fire-2 registry lookup (reuse the stateful module's read-only loader)
import user_state as US


EXTRA_CSS = '''
<style>
/* CAMEL FIRE-1.5 page-specific rules — tokens from style.css only */
.me-shell { max-width: 860px; }
.watch-empty { background: var(--color-card); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 40px 24px; text-align: center; }
.watch-empty h2 { margin-bottom: 10px; }
.watch-cta { display: inline-block; background: var(--color-accent); color: #fff; padding: 12px 20px; border-radius: var(--radius); font-weight: 700; text-decoration: none; margin-top: 12px; }
.watch-cta:hover { background: var(--color-accent-hover); }
/* GTG (5): the Google CTA is now a real link (Google sign-in is LIVE).
   /me/login renders as a static page; the CTA re-requests /me/login with
   the go=1 marker so Flask routes the click through the live OAuth handoff.
   (The href stays the same URL the OAuth blueprint owns.) */
.login-google-pad { margin-top: 10px; }
.step-list { margin: 14px auto 0; padding-left: 20px; color: var(--color-muted); font-size: 14px; line-height: 1.7; text-align: left; display: inline-block; }
</style>
'''

ME_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your cards — tracking &amp; alerts | Card Scout</title>
<meta name="description" content="Track the cards you care about and get an email when your price is hit. Free on Card Scout.">
<link rel="canonical" href="https://cardscout.pro/me">
''' + EXTRA_CSS + '''
</head>
<body class="bands-index">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/lists/monthly">Monthly list</a> <a href="/me">Your cards</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main me-shell">
  <h1>Your cards</h1>
{% if prefill %}
  <div class="watch-empty">
    <h2>Track: {{ prefill.player }}{% if prefill.lane_display %} · {{ prefill.lane_display }}{% endif %}{% if prefill.grade %} · {{ prefill.grade }}{% endif %}</h2>
    <form method="post" action="/me/watchlist">
      <input type="hidden" name="action" value="add">
      <input type="hidden" name="lane_slug" value="{{ prefill.slug }}">
      <input type="hidden" name="player_slug" value="{{ request.args.get('ps') or prefill.slug.rsplit('-',2)[0] }}">
      <p class="faq-line">Tell us your prices — the levels you want to hear about:</p>
      <p>
        <label>Email-me-if price falls to: <input type="number" step="0.01" min="0" name="trigger_low" style="width:110px;"></label>
        &nbsp; or &nbsp;
        <label>rises to: <input type="number" step="0.01" min="0" name="trigger_high" style="width:110px;"></label>
      </p>
      <button type="submit" class="watch-cta">Add to my watchlist</button>
    </form>
    <p class="faq-line">(New here? You'll sign in with Google first — one click, no new password.)</p>
  </div>
{% else %}
  <div class="watch-empty">
    <h2>Your watchlist is empty</h2>
    <p class="faq-line">Add cards from any Card Page — then tell us your prices.
    We watch the market and email you when your level is hit.</p>
    <a class="watch-cta" href="/bands">Find a card to track</a>
  </div>
{% endif %}
  {% if holdings %}
  <h2 style="margin-top:26px;">My holdings</h2>
  <table class="list-table">
    <thead><tr><th>Card</th><th>Basis (mine)</th><th>Qty</th><th>Record</th></tr></thead>
    <tbody>
    {% for h in holdings %}
      <tr>
        <td>{{ h.player }}{% if h.lane_display %} · {{ h.lane_display }}{% endif %}</td>
        <td class="num">{% if h.basis_cost is not none %}${{ '%.2f' % h.basis_cost }}{% else %}—{% endif %}</td>
        <td class="num">{{ h.qty }}</td>
        <td><span class="honesty honesty-{{ h.band_class or 'forming' }}">{{ {0:'BAND FORMING',1:'PROVISIONAL'}.get(h.band_class if h.band_class=='forming' else 1,'RECORD BUILDING') }}</span>
            <span class="faq-line" style="display:inline;">records {{ h.n }} · {{ h.first_date }} → {{ h.last_date }}</span>
            <a href="/price/{{ h.player_slug }}/{{ h.lane_slug }}">page →</a></td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <p class="faq-line">Basis figures are yours alone — private to you, never shown to anyone else. The record columns are the public record (print counts and dates), same as every Card Page.</p>
  {% endif %}
  <p class="faq-line"><strong>How it works:</strong></p>
  <ol class="step-list">
    <li>Open any Card Page and hit "Track this card."</li>
    <li>Set your prices — the level you'd want to hear about.</li>
    <li>We keep watch 24/7 and email you when the market reaches your level.</li>
  </ol>
  <p class="faq-line">Your prices are yours — we never suggest, never advise. We just watch.</p>
</main>
</body>
</html>'''


LOGIN_PREP_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in | Card Scout</title>
<meta name="description" content="Sign in with Google — no extra password to remember.">
<link rel="canonical" href="https://cardscout.pro/me/login">
''' + EXTRA_CSS + '''
</head>
<body class="bands-index">
<header>
  <nav>
    <div class="nav-brand"><a href="/">Card Scout</a></div>
    <div class="nav-links"><a href="/bands">Card Pages</a> <a href="/lists/monthly">Monthly list</a> <a href="/">Home</a></div>
  </nav>
</header>
<main class="band-main me-shell">
  <h1>Sign in</h1>
  <div class="watch-empty">
    <h2>One click — no new password</h2>
    <p class="faq-line">Browsing is anonymous — sign in only to save a watchlist.
    Sign in with Google, like the sites you already use.
    We never see your Google password, and you never make one up for us.</p>
    <div class="login-google-pad">
      <a class="watch-cta" href="/me/login?go=1" rel="nofollow">Sign in with Google</a>
      <p class="faq-line">(Not seeing the Google handoff? The sign-in service is
      warming up — this page retries it on click.)</p>
    </div>
    <div class="step-list">
      <p>We use your Google email only to attach your watchlist to you.
      It stays yours, is never shown to other users, and you can delete
      your list any time.</p>
    </div>
  </div>
</main>
</body>
</html>'''


@bp.route("/me")
def me_home():
    """Fire-3.1: honest watchlist page + prefill support. ?lane=<slug> renders
    a pre-filled add panel (the card's identity from the registry; the form
    posts to the Fire-2 watchlist API, which enforces auth + storage)."""
    lane_slug = (request.args.get("lane") or "").strip()
    prefill = None
    if lane_slug:
        L = US._registry_lane(lane_slug)
        if L:
            prefill = {
                "player": L.get("player", ""),
                "lane_display": L.get("lane_display", ""),
                "grade": ("" if L.get("grade_bucket") == "raw" else L.get("grade_bucket", "")),
                "slug": L["slug"],
            }
    # Fire-3.2: holdings render for logged-in users (their own data only)
    from flask import session as _sess
    holdings = None
    email = _sess.get("user_email")
    if email:
        try:
            from user_state import holdings_view
            holdings = US.holdings_view(email)  # user's own rows only
        except Exception:
            holdings = None  # honest degrade, never a blank 200
    return render_template_string(
        ME_TEMPLATE,
        prefill=prefill,
        logged_in=(email is not None),
        holdings=holdings,
    )


@bp.route("/me/login")
def me_login():
    """Fire-1.5 shell: the Google-login explainer (no auth logic — Fire-2)."""
    return render_template_string(LOGIN_PREP_TEMPLATE)


@bp.route("/me/home")
def user_home():
    """Fire-2 alias: the watchlist shell at /me/home for Fire-2 wiring."""
    return render_template_string(ME_TEMPLATE)
