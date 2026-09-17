"""
Card Scout Customer Dashboard

Self-serve web UI for customers to manage their card roster.

Auth: Customer enters Discord webhook URL → we look up their customer_id.
This is the simplest auth model — no separate passwords to manage.

Flow:
  1. GET / → landing page (asks for webhook)
  2. POST /login → checks webhook, redirects to /dashboard/<id>
  3. GET /dashboard/<id> → shows current cards pre-checked, can edit
  4. POST /dashboard/<id> → saves changes to DB

Deploy: See DEPLOY.md
"""

import hashlib
import os
import secrets
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, abort, jsonify
from flask.sessions import SecureCookieSessionInterface
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Add scripts/ to path so we can import db_models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from db_models import Customer, Card, init_db  # noqa: E402

# ============================================================================
# APP SETUP
# ============================================================================

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Random per-process, override in prod

# Session config — cookie-based for simplicity
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_COOKIE_SECURE', 'false').lower() == 'true'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 1 day

# Register public site blueprint (landing, deals, pricing, SEO)
from public_site import site_bp
app.register_blueprint(site_bp)

# DB setup — share with bot
# In production (Render), use DATABASE_URL env var pointing to persistent disk
DB_URL = os.environ.get('DATABASE_URL')
if DB_URL and DB_URL.startswith('sqlite:///'):
    DB_PATH = Path(DB_URL.replace('sqlite:////', '/').replace('sqlite:///', ''))
else:
    DB_PATH = Path(__file__).parent.parent / 'card_scout.db'
engine = create_engine(f'sqlite:///{DB_PATH}')
db_session = scoped_session(sessionmaker(bind=engine))

# ============================================================================
# HELPERS
# ============================================================================

def webhook_hash(webhook_url: str) -> str:
    """Hash webhook URL for secure comparison (don't store plaintext in cookies)."""
    return hashlib.sha256(webhook_url.encode()).hexdigest()[:16]


def get_current_customer():
    """Get customer from session, or None."""
    customer_id = session.get('customer_id')
    if not customer_id:
        return None
    return db_session.query(Customer).filter_by(customer_id=customer_id).first()


def login_required(f):
    """Decorator: require login, redirect to dashboard login if not logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_customer():
            return redirect(url_for('dashboard_login'))
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/dashboard/login', methods=['GET', 'POST'])
def dashboard_login():
    """Customer dashboard login — Discord webhook auth."""
    if request.method == 'GET':
        return render_template_string(INDEX_TEMPLATE)

    webhook = request.form.get('webhook', '').strip()

    if not webhook:
        flash('Please enter your Discord webhook URL.', 'error')
        return redirect(url_for('dashboard_login'))

    # Basic validation: webhook URLs should start with discord.com OR discordapp.com
    # (both are valid Discord domains — the old domain just redirects to the new one)
    valid_prefixes = (
        'https://discord.com/api/webhooks/',
        'https://discordapp.com/api/webhooks/',
    )
    if not webhook.startswith(valid_prefixes):
        flash('That doesn\'t look like a Discord webhook URL. Try again.', 'error')
        return redirect(url_for('dashboard_login'))

    # Look up customer by webhook
    customer = db_session.query(Customer).filter_by(discord_webhook=webhook).first()
    if not customer:
        flash('Webhook not found. Contact support if you think this is wrong.', 'error')
        return redirect(url_for('dashboard_login'))

    # Set session
    session.clear()
    session['customer_id'] = customer.customer_id
    session.permanent = True

    return redirect(url_for('dashboard', customer_id=customer.customer_id))


@app.route('/logout')
def logout():
    """Clear session and return to login."""
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('site.landing'))


@app.route('/dashboard/<customer_id>')
@login_required
def dashboard(customer_id):
    """Main dashboard — show customer's cards, allow edits."""
    customer = get_current_customer()
    if customer.customer_id != customer_id:
        # Try to prevent URL-tampering
        abort(403)

    cards = db_session.query(Card).filter_by(customer_id=customer.id).all()

    # Group cards by category for the UI
    sports_cards = [c for c in cards if c.search_query and not is_tcg_card(c.search_query)]
    tcg_cards = [c for c in cards if c.search_query and is_tcg_card(c.search_query)]

    return render_template_string(
        DASHBOARD_TEMPLATE,
        customer=customer,
        sports_cards=sports_cards,
        tcg_cards=tcg_cards,
    )


@app.route('/dashboard/<customer_id>/match_card', methods=['POST'])
@login_required
def match_card(customer_id):
    """Proxy Card Hedge /v1/cards/card-match for inline autocomplete on add-card form.

    POST body: { query: str, category?: str }
    Returns: { matched: bool, card: {card_id, description, player, set, number, image, category, prices}, confidence: float }
            or { matched: false, alternatives: [...], error?: str }

    Auth: requires valid Card Hedge API key in CARD_HEDGER_API_KEY env var.
    Rate limit: subject to Starter tier (10/min, 5000/day).
    """
    customer = get_current_customer()
    if customer.customer_id != customer_id:
        abort(403)

    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    category = (data.get('category') or '').strip() or None

    if len(query) < 3:
        return jsonify({'matched': False, 'error': 'Query too short (min 3 chars)', 'alternatives': []}), 400

    api_key = os.getenv('CARD_HEDGER_API_KEY')
    if not api_key:
        return jsonify({'matched': False, 'error': 'Card Hedger not configured', 'alternatives': []}), 503

    try:
        # Lazy import to avoid loading at module import time
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
        from cardhedger_client import CardHedgerClient

        client = CardHedgerClient()
        # Try AI match first (high confidence)
        match_payload = {'query': query}
        if category:
            match_payload['category'] = category
        match_result = client._post('/v1/cards/card-match', match_payload)

        # card-match response shape (verified Sept 17):
        #   {"match": {...card dict with card_id, confidence, description...}, "candidates_evaluated": N, "search_query_used": "..."}
        # The match can be null if no good match.
        match = match_result.get('match')
        if not match:
            # No match — return alternatives via search
            alternatives = []
            try:
                search_payload = {'search': query, 'page_size': 5}
                if category:
                    search_payload['category'] = category
                search_result = client._post('/v1/cards/card-search', search_payload)
                alternatives = search_result.get('cards', [])[:5]
            except Exception:
                pass
            return jsonify({
                'matched': False,
                'confidence': 0.0,
                'alternatives': alternatives[:5],
                'candidates_evaluated': match_result.get('candidates_evaluated'),
            })

        card = match
        confidence = card.get('confidence') or match_result.get('confidence') or 0.0

        # If confidence is too low, also fetch alternatives via search
        alternatives = []
        if confidence < 0.7:
            try:
                search_payload = {'search': query, 'page_size': 5}
                if category:
                    search_payload['category'] = category
                search_result = client._post('/v1/cards/card-search', search_payload)
                alternatives = search_result.get('cards', [])[:5]
            except Exception:
                pass  # Search fallback is best-effort

        # Extract clean card preview for the UI
        preview = {
            'card_id': card.get('card_id'),
            'description': card.get('description') or f"{card.get('player', '')} {card.get('set', '')}",
            'player': card.get('player'),
            'set': card.get('set'),
            'number': card.get('number'),
            'variant': card.get('variant'),
            'image': card.get('image'),
            'category': card.get('category'),
            'rookie': card.get('rookie', False),
            'seven_day_sales': card.get('7 Day Sales'),
            'thirty_day_sales': card.get('30 Day Sales'),
        }
        # Pull the first PSA 10 price for quick preview
        prices = card.get('prices', [])
        if isinstance(prices, list):
            for p in prices:
                if isinstance(p, dict) and p.get('grade') == 'PSA 10':
                    preview['psa_10_price'] = p.get('price')
                    break

        return jsonify({
            'matched': True,
            'card': preview,
            'confidence': confidence,
            'alternatives': alternatives[:5] if alternatives else [],
        })
    except Exception as e:
        # Log full error server-side, return minimal info to client
        app.logger.exception('Card Hedge match failed')
        return jsonify({'matched': False, 'error': str(e)[:200], 'alternatives': []}), 502


@app.route('/dashboard/<customer_id>/update', methods=['POST'])
@login_required
def update_dashboard(customer_id):
    """Save changes to the customer's card roster."""
    customer = get_current_customer()
    if customer.customer_id != customer_id:
        abort(403)

    # Get form data
    action = request.form.get('action', '')

    if action == 'remove':
        card_id = request.form.get('card_id', type=int)
        if card_id:
            card = db_session.query(Card).filter_by(id=card_id, customer_id=customer.id).first()
            if card:
                db_session.delete(card)
                db_session.commit()
                flash(f'Removed card #{card_id}.', 'success')
            else:
                flash('Card not found.', 'error')
        return redirect(url_for('dashboard', customer_id=customer_id))

    elif action == 'edit':
        card_id = request.form.get('card_id', type=int)
        if not card_id:
            flash('Card not found.', 'error')
            return redirect(url_for('dashboard', customer_id=customer_id))

        card = db_session.query(Card).filter_by(id=card_id, customer_id=customer.id).first()
        if not card:
            flash('Card not found.', 'error')
            return redirect(url_for('dashboard', customer_id=customer_id))

        # Update only fields provided (allow blank = clear)
        new_query = request.form.get('new_card', '').strip()
        if new_query:
            card.search_query = new_query
        psa_url = request.form.get('psa_url', '').strip()
        old_psa_url = card.psa_set_url
        card.psa_set_url = psa_url if psa_url else None
        sc_url = request.form.get('sportscardspro_url', '').strip()
        card.sportscardspro_url = sc_url if sc_url else None

        # V3 AUTO-FETCH POP (Sept 16): when PSA URL changes, fetch pop data
        if psa_url and psa_url != old_psa_url:
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
                from psa_pop_persister import fetch_and_persist_pop
                pop_data = fetch_and_persist_pop(db_session, card)
                if pop_data and pop_data.get('psa_total_pop'):
                    flash(
                        f"Updated card #{card.id}. Pop fetched: "
                        f"{pop_data['psa_total_pop']} graded, "
                        f"{pop_data['psa_10_pop']} PSA 10.",
                        'success'
                    )
                else:
                    flash(f'Updated card #{card.id} (pop data could not be fetched — try refresh).', 'warning')
            except Exception as e:
                flash(f'Updated card #{card.id} but pop fetch failed: {e}', 'warning')
        elif not psa_url:
            # Cleared URL → clear pop data
            card.psa_total_pop = None
            card.psa_10_pop = None
            card.psa_9_pop = None
            card.psa_pop_fetched_at = None
            flash(f'Updated card #{card.id}.', 'success')
        else:
            flash(f'Updated card #{card.id}.', 'success')

        db_session.commit()
        return redirect(url_for('dashboard', customer_id=customer_id))

    elif action == 'add':
        new_card_text = request.form.get('new_card', '').strip()
        psa_url = request.form.get('psa_url', '').strip() or None
        sportscardspro_url = request.form.get('sportscardspro_url', '').strip() or None
        # Optional: Card Hedge match fields (sent by inline autocomplete JS)
        card_id = request.form.get('card_id', '').strip() or None
        card_match_confidence = request.form.get('card_match_confidence', '').strip()
        card_match_confidence = float(card_match_confidence) if card_match_confidence else None

        if new_card_text:
            # Check max cards
            max_cards = customer.max_cards or 3
            current_count = db_session.query(Card).filter_by(customer_id=customer.id).count()
            if current_count >= max_cards:
                flash(f'You\'re at your limit ({max_cards} cards). Upgrade tier to add more.', 'error')
                return redirect(url_for('dashboard', customer_id=customer_id))

            new_card = Card(
                customer_id=customer.id,
                search_query=new_card_text,
                psa_set_url=psa_url,
                sportscardspro_url=sportscardspro_url,
                card_id=card_id,
                card_match_confidence=card_match_confidence,
                include_pop=1,
                include_sold=1,
                market_thin=0,
                added_date=datetime.utcnow(),
            )
            db_session.add(new_card)
            db_session.commit()
            flash(f'Added: {new_card_text}', 'success')
        else:
            flash('Please enter a card description.', 'error')
        return redirect(url_for('dashboard', customer_id=customer_id))

    flash('Unknown action.', 'error')
    return redirect(url_for('dashboard', customer_id=customer_id))
# ============================================================================
# HELPERS
# ============================================================================

TCG_KEYWORDS = [
    'charizard', 'mewtwo', 'pokemon', 'mtg', 'magic:', 'black lotus',
    'yu-gi-oh', 'pikachu', 'blastoise', 'venusaur',
]


def is_tcg_card(search_query: str) -> bool:
    """Detect if a card is a TCG card based on search query."""
    if not search_query:
        return False
    q = search_query.lower()
    return any(kw in q for kw in TCG_KEYWORDS)


# ============================================================================
# TEMPLATES
# ============================================================================

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Card Scout - Login</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #f5f5f5; color: #222; max-width: 480px; margin: 80px auto; padding: 0 20px; }
  .card { background: white; padding: 32px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  h1 { margin-top: 0; color: #1a1a1a; }
  .subtitle { color: #666; margin-bottom: 24px; font-size: 14px; }
  label { display: block; font-weight: 600; margin-bottom: 8px; font-size: 14px; }
  input[type=text] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;
                      font-size: 14px; box-sizing: border-box; }
  button { background: #5865f2; color: white; border: none; padding: 10px 20px; border-radius: 4px;
           font-size: 14px; font-weight: 600; cursor: pointer; margin-top: 16px; }
  button:hover { background: #4752c4; }
  .alert { padding: 10px 14px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
  .alert.error { background: #fee; color: #c33; border: 1px solid #fcc; }
  .alert.success { background: #efe; color: #3a3; border: 1px solid #cfc; }
  .alert.info { background: #eef; color: #33c; border: 1px solid #ccf; }
  .help { font-size: 12px; color: #888; margin-top: 8px; }
</style>
</head>
<body>
<div class="card">
  <h1>Card Scout</h1>
  <p class="subtitle">Graded card ticker for collectors.</p>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="alert {{ category }}">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <form method="POST" action="{{ url_for('dashboard_login') }}">
    <label for="webhook">Discord Webhook URL</label>
    <input type="text" id="webhook" name="webhook" placeholder="https://discord.com/api/webhooks/..." required>
    <div class="help">This is how we identify you. Each customer has a unique webhook.</div>
    <button type="submit">Sign In</button>
  </form>
</div>
</body>
</html>
'''


DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Card Scout - {{ customer.customer_id }}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #f5f5f5; color: #222; max-width: 720px; margin: 40px auto; padding: 0 20px; }
  .card { background: white; padding: 32px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px; }
  h1 { margin-top: 0; color: #1a1a1a; }
  h2 { color: #1a1a1a; border-bottom: 1px solid #eee; padding-bottom: 8px; }
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
  .logout { color: #888; font-size: 14px; text-decoration: none; }
  .logout:hover { color: #555; }
  .meta { background: #f9f9f9; padding: 12px 16px; border-radius: 4px; margin-bottom: 16px;
          font-size: 14px; color: #555; }
  .meta strong { color: #222; }
  ul { list-style: none; padding: 0; margin: 0; }
  li.card-item { display: flex; justify-content: space-between; align-items: center;
                  padding: 12px 16px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 8px;
                  background: #fafafa; }
  li.card-item .info { flex: 1; }
  li.card-item .info .query { font-weight: 600; color: #1a1a1a; }
  li.card-item .info .meta-row { font-size: 12px; color: #888; margin-top: 4px; }
  li.card-item button { background: #fee; color: #c33; border: 1px solid #fcc; padding: 6px 12px;
                         border-radius: 4px; cursor: pointer; font-size: 13px; }
  li.card-item button:hover { background: #fdd; }
  form.add-card { display: flex; gap: 8px; margin-top: 16px; }
  form.add-card input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
  form.add-card button { background: #5865f2; color: white; border: none; padding: 10px 20px;
                          border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; }
  form.add-card button:hover { background: #4752c4; }
  .empty { color: #888; font-style: italic; padding: 16px; text-align: center; }
  .alert { padding: 10px 14px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
  .alert.error { background: #fee; color: #c33; border: 1px solid #fcc; }
  .alert.success { background: #efe; color: #3a3; border: 1px solid #cfc; }
  .alert.info { background: #eef; color: #33c; border: 1px solid #ccf; }
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>Your Card Scout</h1>
    <a class="logout" href="{{ url_for('logout') }}">Logout</a>
  </div>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="alert {{ category }}">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <div class="meta">
    <strong>{{ customer.customer_id }}</strong> ·
    Tier: <strong>{{ customer.tier }}</strong> ·
    Cards: <strong>{{ (sports_cards|length + tcg_cards|length) }} / {{ customer.max_cards or 3 }}</strong>
  </div>
</div>

{% if sports_cards %}
<div class="card">
  <h2>Sports Cards</h2>
  <ul>
    {% for c in sports_cards %}
      <li class="card-item">
        <div class="info">
          <div class="query">{{ c.search_query }}</div>
          <div class="meta-row">
            Card #{{ c.id }} ·
            {% if c.psa_set_url %}<a href="{{ c.psa_set_url }}" target="_blank">PSA</a>{% else %}<span style="color:#c33;">no PSA URL</span>{% endif %} ·
            {% if c.sportscardspro_url %}<a href="{{ c.sportscardspro_url }}" target="_blank">SC</a>{% else %}<span style="color:#c33;">no SC URL</span>{% endif %} ·
            {% if c.psa_total_pop %}<span style="color:#3a3;">Pop: {{ c.psa_total_pop }} graded, {{ c.psa_10_pop }} PSA 10</span>{% elif c.include_pop %}<span style="color:#c93;">Pop: pending</span>{% endif %} ·
            {% if c.market_thin %}Thin market{% endif %}
          </div>
        </div>
        <div style="display: flex; gap: 6px;">
          <button type="button" onclick="document.getElementById('edit-{{ c.id }}').style.display = document.getElementById('edit-{{ c.id }}').style.display === 'none' ? 'block' : 'none'; this.textContent = this.textContent === 'Edit' ? 'Cancel' : 'Edit';" style="background: #eef; color: #33c; border: 1px solid #ccf; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 13px;">Edit</button>
          <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}" style="margin:0;">
            <input type="hidden" name="action" value="remove">
            <input type="hidden" name="card_id" value="{{ c.id }}">
            <button type="submit" onclick="return confirm('Remove {{ c.search_query }}?');">Remove</button>
          </form>
        </div>
      </li>
      <li id="edit-{{ c.id }}" style="display: none; background: #f9f9f9; padding: 12px; margin-bottom: 8px; border-radius: 4px;">
        <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}">
          <input type="hidden" name="action" value="edit">
          <input type="hidden" name="card_id" value="{{ c.id }}">
          <input type="text" name="new_card" value="{{ c.search_query }}" placeholder="Card description" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; margin-bottom: 6px;">
          <input type="text" name="psa_url" value="{{ c.psa_set_url or '' }}" placeholder="PSA URL" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 12px; margin-bottom: 6px;">
          <input type="text" name="sportscardspro_url" value="{{ c.sportscardspro_url or '' }}" placeholder="Sportscardspro URL" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 12px; margin-bottom: 6px;">
          <button type="submit" style="background: #5865f2; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;">Save Changes</button>
        </form>
      </li>
    {% endfor %}
  </ul>
</div>
{% endif %}

{% if tcg_cards %}
<div class="card">
  <h2>TCG Cards</h2>
  <ul>
    {% for c in tcg_cards %}
      <li class="card-item">
        <div class="info">
          <div class="query">{{ c.search_query }}</div>
          <div class="meta-row">
            Card #{{ c.id }} ·
            {% if c.psa_set_url %}<a href="{{ c.psa_set_url }}" target="_blank">PSA</a>{% else %}<span style="color:#c33;">no PSA URL</span>{% endif %} ·
            {% if c.sportscardspro_url %}<a href="{{ c.sportscardspro_url }}" target="_blank">SC</a>{% else %}<span style="color:#c33;">no SC URL</span>{% endif %} ·
            {% if c.psa_total_pop %}<span style="color:#3a3;">Pop: {{ c.psa_total_pop }} graded, {{ c.psa_10_pop }} PSA 10</span>{% elif c.include_pop %}<span style="color:#c93;">Pop: pending</span>{% endif %} ·
            {% if c.market_thin %}Thin market{% endif %}
          </div>
        </div>
        <div style="display: flex; gap: 6px;">
          <button type="button" onclick="document.getElementById('edit-{{ c.id }}').style.display = document.getElementById('edit-{{ c.id }}').style.display === 'none' ? 'block' : 'none'; this.textContent = this.textContent === 'Edit' ? 'Cancel' : 'Edit';" style="background: #eef; color: #33c; border: 1px solid #ccf; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 13px;">Edit</button>
          <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}" style="margin:0;">
            <input type="hidden" name="action" value="remove">
            <input type="hidden" name="card_id" value="{{ c.id }}">
            <button type="submit" onclick="return confirm('Remove {{ c.search_query }}?');">Remove</button>
          </form>
        </div>
      </li>
      <li id="edit-{{ c.id }}" style="display: none; background: #f9f9f9; padding: 12px; margin-bottom: 8px; border-radius: 4px;">
        <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}">
          <input type="hidden" name="action" value="edit">
          <input type="hidden" name="card_id" value="{{ c.id }}">
          <input type="text" name="new_card" value="{{ c.search_query }}" placeholder="Card description" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; margin-bottom: 6px;">
          <input type="text" name="psa_url" value="{{ c.psa_set_url or '' }}" placeholder="PSA URL" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 12px; margin-bottom: 6px;">
          <input type="text" name="sportscardspro_url" value="{{ c.sportscardspro_url or '' }}" placeholder="Sportscardspro URL" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 12px; margin-bottom: 6px;">
          <button type="submit" style="background: #5865f2; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;">Save Changes</button>
        </form>
      </li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<div class="card">
  <h2>Add a Card</h2>
  <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}" class="add-card" id="add-card-form">
    <input type="hidden" name="action" value="add">
    <div style="flex: 1; position: relative;">
      <input type="text" name="new_card" id="new-card-input" placeholder="e.g. Mike Trout 2011 Topps Update Rookie #US1" required style="width: 100%;" autocomplete="off">
      <!-- Hidden fields populated by inline matcher -->
      <input type="hidden" name="card_id" id="matched-card-id">
      <input type="hidden" name="card_match_confidence" id="matched-confidence">
      <!-- Inline preview shown when user types something Card Hedge recognizes -->
      <div id="card-match-preview" style="display: none; margin-top: 10px; padding: 12px; border: 1px solid #ddd; border-radius: 6px; background: #fafafa;">
        <div style="display: flex; gap: 12px; align-items: center;">
          <img id="preview-image" src="" alt="" style="width: 60px; height: 84px; object-fit: cover; border-radius: 4px; background: #eee;">
          <div style="flex: 1; font-size: 13px;">
            <div id="preview-description" style="font-weight: 600; color: #333;"></div>
            <div id="preview-meta" style="color: #666; margin-top: 2px;"></div>
            <div id="preview-price" style="color: #2e7d32; margin-top: 4px;"></div>
          </div>
          <div id="preview-confidence" style="font-size: 11px; padding: 3px 8px; border-radius: 10px; background: #e8f5e9; color: #2e7d32;"></div>
        </div>
        <div id="preview-alternatives" style="display: none; margin-top: 10px; font-size: 12px; color: #888;">
          <div>Other options:</div>
          <ul id="alternatives-list" style="margin: 4px 0 0 0; padding-left: 16px;"></ul>
        </div>
      </div>
      <!-- Status indicator while matching -->
      <div id="match-status" style="display: none; margin-top: 6px; font-size: 12px; color: #888;"></div>
      <div style="display: flex; gap: 8px; margin-top: 8px;">
        <input type="text" name="psa_url" placeholder="PSA set URL (optional)" style="flex: 1; font-size: 12px;">
        <input type="text" name="sportscardspro_url" placeholder="Sportscardspro URL (optional)" style="flex: 1; font-size: 12px;">
      </div>
    </div>
    <button type="submit" id="add-card-btn">Add</button>
  </form>
  <p style="font-size: 12px; color: #888; margin-top: 12px;">
    <strong>Tip:</strong> Start typing a card name and we'll look it up live. You'll see a preview with image and recent price before adding.
    <br><strong>PSA URL:</strong> e.g. <code>https://www.psacard.com/pop/baseball-cards/1995/topps/49750</code><br>
    <strong>Sportscardspro URL:</strong> e.g. <code>https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14</code><br>
    Leave blank to use search-only mode (slower but works without URLs).
  </p>
</div>

<script>
(function() {
  // Inline card matcher — debounced autocomplete via Card Hedge /card-match
  const input = document.getElementById('new-card-input');
  const preview = document.getElementById('card-match-preview');
  const previewImage = document.getElementById('preview-image');
  const previewDescription = document.getElementById('preview-description');
  const previewMeta = document.getElementById('preview-meta');
  const previewPrice = document.getElementById('preview-price');
  const previewConfidence = document.getElementById('preview-confidence');
  const previewAlternatives = document.getElementById('preview-alternatives');
  const alternativesList = document.getElementById('alternatives-list');
  const matchStatus = document.getElementById('match-status');
  const matchedCardId = document.getElementById('matched-card-id');
  const matchedConfidence = document.getElementById('matched-confidence');
  const addBtn = document.getElementById('add-card-btn');

  let debounceTimer = null;
  let lastQuery = '';
  let inflight = null;

  function hidePreview() {
    preview.style.display = 'none';
    previewAlternatives.style.display = 'none';
    matchedCardId.value = '';
    matchedConfidence.value = '';
  }

  function showStatus(msg) {
    matchStatus.textContent = msg;
    matchStatus.style.display = msg ? 'block' : 'none';
  }

  function showPreview(data) {
    if (!data.matched) {
      hidePreview();
      showStatus(data.error || 'No match found. Try a different name or paste a PSA/SCPro URL.');
      return;
    }
    const c = data.card || {};
    previewImage.src = c.image || '';
    previewImage.alt = c.description || '';
    previewDescription.textContent = c.description || '(unknown card)';
    const parts = [];
    if (c.player) parts.push(c.player);
    if (c.set) parts.push(c.set);
    if (c.number) parts.push('#' + c.number);
    if (c.variant) parts.push(c.variant);
    previewMeta.textContent = parts.join(' · ');
    if (c.psa_10_price) {
      previewPrice.textContent = 'PSA 10 last sale: $' + c.psa_10_price;
    } else {
      previewPrice.textContent = '';
    }
    const conf = data.confidence || 0;
    const pct = (conf * 100).toFixed(0) + '%';
    previewConfidence.textContent = pct + ' match';
    previewConfidence.style.background = conf >= 0.7 ? '#e8f5e9' : conf >= 0.5 ? '#fff8e1' : '#ffebee';
    previewConfidence.style.color = conf >= 0.7 ? '#2e7d32' : conf >= 0.5 ? '#f57f17' : '#c62828';

    matchedCardId.value = c.card_id || '';
    matchedConfidence.value = conf;

    // Show alternatives if confidence is low OR if there are popular alternates
    if (data.alternatives && data.alternatives.length > 0) {
      alternativesList.innerHTML = '';
      data.alternatives.forEach(function(alt) {
        const li = document.createElement('li');
        li.style.cursor = 'pointer';
        li.style.padding = '4px 8px';
        li.style.borderRadius = '4px';
        li.style.marginBottom = '2px';
        li.style.transition = 'background 0.15s';
        li.textContent = (alt.description || alt.player || '?') + ' — click to use';
        li.onmouseenter = function() { li.style.background = '#eee'; };
        li.onmouseleave = function() { li.style.background = ''; };
        li.onclick = function(e) {
          e.preventDefault();
          // Select this alternative directly — populate hidden fields + update preview
          const preview2 = {
            card_id: alt.card_id,
            description: alt.description,
            player: alt.player,
            set: alt.set,
            number: alt.number,
            variant: alt.variant,
            image: alt.image,
            category: alt.category,
            rookie: alt.rookie,
            seven_day_sales: alt['7 Day Sales'],
            thirty_day_sales: alt['30 Day Sales'],
            psa_10_price: null,
          };
          // Look for PSA 10 price in the alt's prices list
          if (Array.isArray(alt.prices)) {
            for (let p of alt.prices) {
              if (p && p.grade === 'PSA 10') {
                preview2.psa_10_price = p.price;
                break;
              }
            }
          }
          // Update the preview UI in place with this alternative
          previewImage.src = preview2.image || '';
          previewImage.alt = preview2.description || '';
          previewDescription.textContent = preview2.description || '(unknown card)';
          const parts = [];
          if (preview2.player) parts.push(preview2.player);
          if (preview2.set) parts.push(preview2.set);
          if (preview2.number) parts.push('#' + preview2.number);
          if (preview2.variant) parts.push(preview2.variant);
          previewMeta.textContent = parts.join(' · ');
          previewPrice.textContent = preview2.psa_10_price ? 'PSA 10 last sale: $' + preview2.psa_10_price : '';
          previewConfidence.textContent = 'Selected';
          previewConfidence.style.background = '#e3f2fd';
          previewConfidence.style.color = '#1565c0';
          // Update text input to show the chosen card name (so customer sees what they'll save)
          input.value = preview2.description || preview2.player || '';
          // Set the hidden fields
          matchedCardId.value = preview2.card_id || '';
          matchedConfidence.value = '1.0';  // user-selected = full confidence
          // Hide alternatives (already chosen)
          previewAlternatives.style.display = 'none';
          // Update lastQuery to prevent re-matching
          lastQuery = preview2.description || preview2.player || '';
        };
        alternativesList.appendChild(li);
      });
      // Always show alternatives section so customers can see other options
      previewAlternatives.style.display = 'block';
    } else {
      previewAlternatives.style.display = 'none';
    }

    preview.style.display = 'block';
    showStatus('');
  }

  function debouncedMatch() {
    clearTimeout(debounceTimer);
    const query = input.value.trim();
    if (query.length < 3) {
      hidePreview();
      showStatus('');
      return;
    }
    if (query === lastQuery) return;  // already matched this
    lastQuery = query;
    showStatus('Looking up...');
    debounceTimer = setTimeout(function() {
      // Cancel any in-flight request
      if (inflight) inflight.abort();
      inflight = new AbortController();
      fetch('{{ url_for("match_card", customer_id=customer.customer_id) }}', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query}),
        signal: inflight.signal,
      })
      .then(function(r) { return r.json().then(function(j) { return {ok: r.ok, json: j}; }); })
      .then(function(res) {
        showPreview(res.json);
      })
      .catch(function(err) {
        if (err.name === 'AbortError') return;
        showStatus('Lookup failed: ' + err.message);
      });
    }, 400);  // 400ms debounce
  }

  input.addEventListener('input', debouncedMatch);
  input.addEventListener('focus', function() {
    if (input.value.trim().length >= 3 && !preview.style.display !== 'none') {
      debouncedMatch();
    }
  });
})();
</script>

{% if not sports_cards and not tcg_cards %}
<div class="card">
  <p class="empty">No cards yet. Add one above to get started.</p>
</div>
{% endif %}

</body>
</html>
'''


# ============================================================================
# TEARDOWN
# ============================================================================

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Clean up DB session at end of request."""
    db_session.remove()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    init_db()  # Make sure tables exist
    print("\n" + "=" * 70)
    print("CARD SCOUT DASHBOARD")
    print("=" * 70)
    print(f"\n  Open in browser: http://localhost:5000")
    print(f"  DB path: {DB_PATH}")
    print(f"  Press Ctrl+C to stop\n")
    app.run(host='127.0.0.1', port=5000, debug=False)


# ============================================================================
# ADMIN: One-time DB sync endpoint (Sept 17)
# ============================================================================
# Used to upload local card_scout.db to Render's persistent disk.
# Auth: requires SYNC_DB_SECRET env var matching the request header.
# Remove or keep disabled after sync is done.

@app.route('/admin/sync_db', methods=['POST'])
def admin_sync_db():
    """One-time DB sync endpoint.

    POST body: raw SQLite DB file bytes (Content-Type: application/octet-stream)
    Required header: X-Sync-Secret: <SYNC_DB_SECRET env var value>

    Backs up existing /data/card_scout.db to /data/card_scout.db.backup-<ts>
    before writing the new content.

    Returns: { ok: bool, message: str, backup_path?: str, customers_in_db: int }
    """
    expected = os.environ.get('SYNC_DB_SECRET')
    if not expected:
        return jsonify({'ok': False, 'message': 'SYNC_DB_SECRET not configured on server'}), 503

    provided = request.headers.get('X-Sync-Secret', '')
    if not provided or provided != expected:
        return jsonify({'ok': False, 'message': 'Invalid or missing X-Sync-Secret header'}), 403

    body = request.get_data()
    if not body or len(body) < 100:
        return jsonify({'ok': False, 'message': f'Body too small ({len(body)} bytes) — expected SQLite DB'}), 400

    # Sanity check: SQLite files start with 'SQLite format 3\x00'
    if not body.startswith(b'SQLite format 3\x00'):
        return jsonify({'ok': False, 'message': 'Body is not a SQLite DB file (missing magic bytes)'}), 400

    # Determine target path (Render uses /data, local uses project root)
    target_dir = os.environ.get('RENDER_DATA_PATH', '/data') if os.environ.get('RENDER') else '.'
    target_path = os.path.join(target_dir, 'card_scout.db')

    # Backup existing if present
    backup_path = None
    if os.path.exists(target_path):
        from datetime import datetime
        ts = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        backup_path = f'{target_path}.backup-{ts}'
        try:
            import shutil
            shutil.copy2(target_path, backup_path)
        except Exception as e:
            return jsonify({'ok': False, 'message': f'Failed to backup existing DB: {e}'}), 500

    # Write new DB
    try:
        os.makedirs(target_dir, exist_ok=True)
        with open(target_path, 'wb') as f:
            f.write(body)
    except Exception as e:
        return jsonify({'ok': False, 'message': f'Failed to write DB: {e}'}), 500

    # Verify by counting customers
    customers_in_db = 0
    try:
        import sqlite3 as _sqlite
        conn = _sqlite.connect(target_path)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM customers')
        customers_in_db = cur.fetchone()[0]
        conn.close()
    except Exception:
        pass

    return jsonify({
        'ok': True,
        'message': f'Wrote {len(body)} bytes to {target_path}',
        'backup_path': backup_path,
        'customers_in_db': customers_in_db,
    })
