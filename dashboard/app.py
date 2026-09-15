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
import secrets
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, abort
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

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Random per-process, override in prod

# Session config — cookie-based for simplicity
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 1 day

# DB setup — share with bot
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
    """Decorator: require login, redirect to / if not logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_customer():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page — login form or link to dashboard."""
    customer = get_current_customer()
    if customer:
        return redirect(url_for('dashboard', customer_id=customer.customer_id))
    return render_template_string(INDEX_TEMPLATE)


@app.route('/login', methods=['POST'])
def login():
    """Login: customer enters Discord webhook URL → we look up their customer_id."""
    webhook = request.form.get('webhook', '').strip()

    if not webhook:
        flash('Please enter your Discord webhook URL.', 'error')
        return redirect(url_for('index'))

    # Basic validation: webhook URLs should start with https://discord.com/api/webhooks/
    if not webhook.startswith('https://discord.com/api/webhooks/'):
        flash('That doesn\'t look like a Discord webhook URL. Try again.', 'error')
        return redirect(url_for('index'))

    # Look up customer by webhook
    customer = db_session.query(Customer).filter_by(discord_webhook=webhook).first()
    if not customer:
        flash('Webhook not found. Contact support if you think this is wrong.', 'error')
        return redirect(url_for('index'))

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
    return redirect(url_for('index'))


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
        card.psa_set_url = psa_url if psa_url else None
        sc_url = request.form.get('sportscardspro_url', '').strip()
        card.sportscardspro_url = sc_url if sc_url else None

        db_session.commit()
        flash(f'Updated card #{card.id}.', 'success')
        return redirect(url_for('dashboard', customer_id=customer_id))

    elif action == 'add':
        new_card_text = request.form.get('new_card', '').strip()
        psa_url = request.form.get('psa_url', '').strip() or None
        sportscardspro_url = request.form.get('sportscardspro_url', '').strip() or None

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

  <form method="POST" action="{{ url_for('login') }}">
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
            {% if c.include_pop %}Pop ✓{% endif %} ·
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
            {% if c.include_pop %}Pop ✓{% endif %} ·
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
  <form method="POST" action="{{ url_for('update_dashboard', customer_id=customer.customer_id) }}" class="add-card">
    <input type="hidden" name="action" value="add">
    <div style="flex: 1;">
      <input type="text" name="new_card" placeholder="e.g. Mike Trout 2011 Topps Update Rookie #US1" required style="width: 100%;">
      <div style="display: flex; gap: 8px; margin-top: 8px;">
        <input type="text" name="psa_url" placeholder="PSA set URL (optional)" style="flex: 1; font-size: 12px;">
        <input type="text" name="sportscardspro_url" placeholder="Sportscardspro URL (optional)" style="flex: 1; font-size: 12px;">
      </div>
    </div>
    <button type="submit">Add</button>
  </form>
  <p style="font-size: 12px; color: #888; margin-top: 12px;">
    <strong>PSA URL:</strong> e.g. <code>https://www.psacard.com/pop/baseball-cards/1995/topps/49750</code><br>
    <strong>Sportscardspro URL:</strong> e.g. <code>https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14</code><br>
    Leave blank to use search-only mode (slower but works without URLs).
  </p>
</div>

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
