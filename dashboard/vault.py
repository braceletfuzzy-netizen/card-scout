"""Vault / Portfolio Tracker routes (Sept 18, PL-007).

Routes:
- GET  /dashboard/<id>/vault         -> list owned cards + value + ROI
- POST /dashboard/<id>/vault/update   -> save cost_basis + notes per card
- POST /dashboard/<id>/vault/add      -> add a card from inventory to vault

Tier policy (Sept 18, founder):
- Casual ($15): max 25 vault cards
- Standard ($30): max 75 vault cards
- Dealer ($75): max 250 vault cards
- Pro ($150): unlimited + active sell-window alerts on Vault items
- Vault is FREE — differentiation is in alerts + max_cards

Path C: NO vendor names in customer copy. "Now: $X" with confidence
as hover text, not as inline brand mention.
"""
import sys
import os
import json
import sqlite3
from datetime import date
from flask import (
    Blueprint, render_template_string, request, redirect, url_for,
    flash, abort, session
)

sys.path.insert(0, os.path.dirname(__file__))
from app import db_session, get_current_customer, login_required

# Tier -> max Vault cards (Sept 18 founder decision)
TIER_MAX_VAULT = {
    'casual': 25,
    'standard': 75,
    'dealer': 250,
    'pro': None,  # unlimited
    'beta_power': 25,  # Jim's tier = treat like casual for now
    'trial': 25,
}


# ============================================================================
# Helpers
# ============================================================================

def get_ch_fmv_for_card(card, grade='PSA 10'):
    """Get the current FMV for a card from cached data or fall back to SCPro.

    Path C: returns a dict {value: float, confidence: str, source: str}
    The caller formats it WITHOUT showing source/grade in the main UI.
    """
    fmv = None
    confidence = None

    # Try Card Hedger first via the cached comparison log or live lookup
    try:
        from cardhedger_alert_integration import fetch_card_hedger_data
        ch_data = fetch_card_hedger_data(card)
        if ch_data:
            fmvs = ch_data.get('fmvs') or {}
            grade_fmv = fmvs.get(grade)
            if grade_fmv and grade_fmv.get('price'):
                fmv = grade_fmv['price']
                confidence = grade_fmv.get('confidence_grade', 'C')
    except Exception as e:
        if 'rate' not in str(e).lower() and '429' not in str(e):
            print(f'  [VAULT] CH lookup failed: {e}')
        pass

    # Fallback to SCPro sold data (psa_10_price from extract_sold_summary)
    if fmv is None and getattr(card, 'sportscardspro_url', None):
        try:
            from sportscardspro_lookup import lookup_sportscardspro, extract_sold_summary
            sc_data = lookup_sportscardspro(card.sportscardspro_url, max_sales=5, max_wait_sec=30)
            if sc_data:
                sd = extract_sold_summary(sc_data)
                if sd and sd.get('psa_10_price'):
                    fmv = sd['psa_10_price']
                    confidence = 'C'  # SCPro data is less reliable
        except Exception:
            pass

    return {'value': fmv, 'confidence': confidence}


# ============================================================================
# Routes
# ============================================================================

def vault_view(customer_id):
    """Display portfolio: per-card ROI + total."""
    customer = get_current_customer()
    if customer.customer_id != customer_id:
        abort(403)

    # Get all enabled cards
    cards = db_session.query(__import__('db_models').Card).filter_by(
        customer_id=customer.id, enabled=1
    ).order_by('id').all()

    # Compute per-card ROI
    rows = []
    total_cost = 0.0
    total_value = 0.0
    cards_with_value = 0
    cards_with_cost = 0
    for card in cards:
        fmv_data = get_ch_fmv_for_card(card, grade='PSA 10')
        current_value = fmv_data['value']
        cost = card.cost_basis_usd
        roi_pct = None
        gain_usd = None
        if cost and cost > 0 and current_value:
            gain_usd = current_value - cost
            roi_pct = (gain_usd / cost) * 100
            total_cost += cost
            total_value += current_value
            cards_with_cost += 1
            cards_with_value += 1
        elif cost and cost > 0:
            total_cost += cost
            cards_with_cost += 1
        elif current_value:
            total_value += current_value
            cards_with_value += 1

        rows.append({
            'card': card,
            'current_value': current_value,
            'confidence': fmv_data['confidence'],
            'cost': cost,
            'roi_pct': roi_pct,
            'gain_usd': gain_usd,
            'set_date': card.cost_basis_set_date or (card.added_date.date() if card.added_date else None),
            'vault_notes': card.vault_notes,
        })

    total_roi_pct = None
    if total_cost > 0:
        total_roi_pct = ((total_value - total_cost) / total_cost) * 100

    # Tier info
    tier_max = TIER_MAX_VAULT.get(customer.tier, 25)
    tier_max_str = '∞' if tier_max is None else str(tier_max)

    return render_template_string(VAULT_HTML,
        customer=customer,
        rows=rows,
        total_cost=total_cost,
        total_value=total_value,
        total_roi_pct=total_roi_pct,
        cards_with_cost=cards_with_cost,
        cards_with_value=cards_with_value,
        tier=customer.tier,
        tier_max=tier_max_str,
        today=date.today().isoformat(),
    )


def vault_update(customer_id):
    """Save cost_basis + notes for cards (POST handler)."""
    customer = get_current_customer()
    if customer.customer_id != customer_id:
        abort(403)

    # Form fields are named cost_basis_<card_id> and vault_notes_<card_id>
    updated = 0
    for card in db_session.query(__import__('db_models').Card).filter_by(
        customer_id=customer.id, enabled=1
    ).all():
        cost_str = request.form.get(f'cost_basis_{card.id}', '').strip()
        date_str = request.form.get(f'cost_date_{card.id}', '').strip()
        notes = request.form.get(f'vault_notes_{card.id}', '').strip()

        changed = False
        if cost_str:
            try:
                new_cost = float(cost_str)
                if new_cost >= 0:
                    card.cost_basis_usd = new_cost
                    changed = True
            except ValueError:
                flash(f'Invalid cost for card #{card.id} (skipping).', 'error')
        elif cost_str == '':
            card.cost_basis_usd = None
            changed = True

        if date_str:
            try:
                from datetime import date as _date
                card.cost_basis_set_date = _date.fromisoformat(date_str)
                changed = True
            except ValueError:
                flash(f'Invalid date for card #{card.id} (skipping).', 'error')
        elif date_str == '':
            card.cost_basis_set_date = None
            changed = True

        if notes != (card.vault_notes or ''):
            card.vault_notes = notes or None
            changed = True

        if changed:
            updated += 1

    db_session.commit()
    if updated:
        flash(f'Updated {updated} card{"s" if updated != 1 else ""}.', 'success')
    return redirect(url_for('vault_view', customer_id=customer_id))


# ============================================================================
# HTML template (inline for simplicity, single-page app)
# ============================================================================

VAULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vault — {{ customer.customer_id }}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0d0e12; color: #e0e0e0; padding: 24px; max-width: 1100px; margin: 0 auto;
    }
    h1 { font-size: 28px; margin-bottom: 6px; color: #fff; }
    h2 { font-size: 18px; margin: 28px 0 12px; color: #fff; }
    .subtitle { color: #888; font-size: 14px; margin-bottom: 24px; }
    a { color: #4a9eff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .summary-grid {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: #16181f; padding: 18px; border-radius: 8px; border: 1px solid #2a2d36;
    }
    .stat-label { color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 24px; font-weight: 600; color: #fff; margin-top: 6px; }
    .stat-sub { color: #666; font-size: 12px; margin-top: 4px; }
    .gain-positive { color: #4ade80; }
    .gain-negative { color: #f87171; }
    .gain-neutral { color: #888; }
    table { width: 100%; border-collapse: collapse; background: #16181f; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px 14px; text-align: left; font-size: 14px; border-bottom: 1px solid #2a2d36; }
    th { background: #1c1e26; color: #aaa; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: #1c1e26; }
    input[type="text"], input[type="number"], input[type="date"] {
      width: 100%; padding: 6px 8px; background: #0d0e12; color: #fff;
      border: 1px solid #2a2d36; border-radius: 4px; font-size: 14px;
    }
    input:focus { outline: none; border-color: #4a9eff; }
    .btn {
      background: #4a9eff; color: #fff; padding: 8px 16px; border: none;
      border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 16px;
    }
    .btn:hover { background: #5ba8ff; }
    .btn-secondary {
      background: transparent; color: #aaa; border: 1px solid #2a2d36;
    }
    .btn-secondary:hover { background: #1c1e26; }
    .nav-links { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #2a2d36; }
    .nav-links a { margin-right: 20px; font-size: 14px; }
    .empty { padding: 60px 20px; text-align: center; color: #888; }
    .empty h3 { color: #fff; margin-bottom: 8px; }
    .flashes { list-style: none; padding: 0; margin-bottom: 16px; }
    .flashes li { padding: 10px 14px; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
    .flashes li.success { background: #14532d; color: #4ade80; border: 1px solid #166534; }
    .flashes li.error { background: #7f1d1d; color: #f87171; border: 1px solid #991b1b; }
    .tier-badge {
      display: inline-block; padding: 3px 10px; border-radius: 12px;
      background: #1e3a8a; color: #93c5fd; font-size: 11px; font-weight: 600;
      text-transform: uppercase; letter-spacing: 0.5px; vertical-align: middle; margin-left: 8px;
    }
    .help-text { font-size: 11px; color: #888; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="nav-links">
    <a href="/dashboard/{{ customer.customer_id }}">← Back to dashboard</a>
    <a href="/tracked">📈 Tracked</a>
    <a href="/trending">🔥 Trending</a>
  </div>

  <h1>📊 Vault <span class="tier-badge">{{ tier }}</span></h1>
  <p class="subtitle">Your portfolio — current value, cost basis, ROI</p>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <ul class="flashes">
        {% for cat, msg in messages %}<li class="{{ cat }}">{{ msg }}</li>{% endfor %}
      </ul>
    {% endif %}
  {% endwith %}

  <div class="summary-grid">
    <div class="stat-card">
      <div class="stat-label">Total cost</div>
      <div class="stat-value">${{ "{:,.2f}".format(total_cost) }}</div>
      <div class="stat-sub">{{ cards_with_cost }} of {{ rows|length }} cards with cost</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Current value</div>
      <div class="stat-value">${{ "{:,.2f}".format(total_value) }}</div>
      <div class="stat-sub">{{ cards_with_value }} of {{ rows|length }} cards with FMV</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">All-time gain</div>
      <div class="stat-value {% if total_value - total_cost > 0 %}gain-positive{% elif total_value - total_cost < 0 %}gain-negative{% else %}gain-neutral{% endif %}">
        {% if total_cost > 0 %}${{ "{:+,.2f}".format(total_value - total_cost) }}{% else %}—{% endif %}
      </div>
      <div class="stat-sub">
        {% if total_roi_pct is not none %}
          {% if total_roi_pct >= 0 %}+{{ "{:.1f}".format(total_roi_pct) }}%{% else %}{{ "{:.1f}".format(total_roi_pct) }}%{% endif %}
        {% else %}
          Set cost on cards to see ROI
        {% endif %}
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Tier capacity</div>
      <div class="stat-value">{{ rows|length }} / {{ tier_max }}</div>
      <div class="stat-sub">Cards in your Vault</div>
    </div>
  </div>

  <form method="POST" action="/dashboard/{{ customer.customer_id }}/vault/update">
    <h2>Your cards</h2>
    <table>
      <thead>
        <tr>
          <th>Card</th>
          <th style="width:120px;">Cost basis</th>
          <th style="width:140px;">Acquired</th>
          <th style="width:120px;">Current value</th>
          <th style="width:120px;">Gain / loss</th>
          <th style="width:100px;">ROI</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
          <tr>
            <td>
              <strong>{{ row.card.search_query[:60] }}</strong>
              {% if row.card.era %}<br><small style="color:#666;">{{ row.card.era }} · {{ row.card.category }}</small>{% endif %}
            </td>
            <td>
              <input type="number" name="cost_basis_{{ row.card.id }}" value="{{ row.cost if row.cost else '' }}" placeholder="—" min="0" step="0.01">
            </td>
            <td>
              <input type="date" name="cost_date_{{ row.card.id }}" value="{{ row.set_date.isoformat() if row.set_date else '' }}">
              <div class="help-text">{% if not row.set_date %}Defaults to added date{% endif %}</div>
            </td>
            <td>
              {% if row.current_value %}
                ${{ "{:,.0f}".format(row.current_value) }}
                {% if row.confidence %}<span class="help-text" title="Confidence: {{ row.confidence }}">· {{ row.confidence }}</span>{% endif %}
              {% else %}
                <span class="gain-neutral">—</span>
                <div class="help-text">No market data yet</div>
              {% endif %}
            </td>
            <td class="{% if row.gain_usd is none %}gain-neutral{% elif row.gain_usd > 0 %}gain-positive{% else %}gain-negative{% endif %}">
              {% if row.gain_usd is not none %}
                ${{ "{:+,.0f}".format(row.gain_usd) }}
              {% else %}—{% endif %}
            </td>
            <td class="{% if row.roi_pct is none %}gain-neutral{% elif row.roi_pct > 0 %}gain-positive{% else %}gain-negative{% endif %}">
              {% if row.roi_pct is not none %}
                {% if row.roi_pct >= 0 %}+{{ "{:.0f}".format(row.roi_pct) }}%{% else %}{{ "{:.0f}".format(row.roi_pct) }}%{% endif %}
              {% else %}—{% endif %}
            </td>
            <td>
              <input type="text" name="vault_notes_{{ row.card.id }}" value="{{ row.vault_notes or '' }}" placeholder="Optional">
            </td>
          </tr>
        {% endfor %}
        {% if not rows %}
          <tr><td colspan="7"><div class="empty">
            <h3>No cards in your Vault</h3>
            <p>Add cards from your <a href="/dashboard/{{ customer.customer_id }}">dashboard</a> to start tracking.</p>
          </div></td></tr>
        {% endif %}
      </tbody>
    </table>

    {% if rows %}
      <button type="submit" class="btn">Save cost basis + notes</button>
      <a href="/dashboard/{{ customer.customer_id }}" class="btn btn-secondary" style="margin-left: 8px;">Cancel</a>
    {% endif %}
  </form>

  <h2 style="margin-top: 40px;">How this works</h2>
  <p class="subtitle">
    <strong>Cost basis</strong> = what you paid. <strong>Current value</strong> = prevailing market range (PSA 10 default, switch to other grades below).
    <strong>ROI</strong> = (current value − cost basis) ÷ cost basis.
  </p>
  <p class="subtitle">
    Vault is free for all tiers — alert treatment on Vault items is the Pro-tier feature. {% if tier != 'pro' %}<br><a href="/upgrade">Upgrade to Pro</a> for active sell-window alerts on your Vault cards.{% endif %}
  </p>
</body>
</html>
"""
