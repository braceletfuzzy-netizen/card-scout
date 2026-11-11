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

from flask import Blueprint, render_template_string

bp = Blueprint("user", __name__)

EXTRA_CSS = '''
<style>
/* CAMEL FIRE-1.5 page-specific rules — tokens from style.css only */
.me-shell { max-width: 860px; }
.watch-empty { background: var(--color-card); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 40px 24px; text-align: center; }
.watch-empty h2 { margin-bottom: 10px; }
.watch-cta { display: inline-block; background: var(--color-accent); color: #fff; padding: 12px 20px; border-radius: var(--radius); font-weight: 700; text-decoration: none; margin-top: 12px; }
.watch-cta:hover { background: var(--color-accent-hover); }
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
  <div class="watch-empty">
    <h2>Your watchlist is empty</h2>
    <p class="faq-line">Add cards from any Card Page — then tell us your prices.
    We watch the market and email you when your level is hit.</p>
    <a class="watch-cta" href="/bands">Find a card to track</a>
  </div>
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
    <p class="faq-line">Sign in with Google, like the sites you already use.
    We never see your Google password, and you never make one up for us.</p>
    <span class="watch-cta">Sign in with Google — opening soon</span>
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
    """Fire-1.5 shell: renders the honest-empty watchlist page. Fire-2 (Hugo
    lane) wires auth + storage into this exact template — render-only now."""
    return render_template_string(ME_TEMPLATE)


@bp.route("/me/login")
def me_login():
    """Fire-1.5 shell: the Google-login explainer (no auth logic — Fire-2)."""
    return render_template_string(LOGIN_PREP_TEMPLATE)


@bp.route("/me/home")
def user_home():
    """Fire-2 alias: the watchlist shell at /me/home for Fire-2 wiring."""
    return render_template_string(ME_TEMPLATE)
