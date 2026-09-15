# Card Scout Customer Dashboard (Option A)

## What it is
Self-serve web app for Card Scout customers. Replaces Google Forms for V2 onboarding.

## Features
- Customer enters Discord webhook URL → logs in (no separate password)
- Sees their current card roster, pre-checked
- Can add/remove cards
- Tier shown (trial, beta_power, etc.)
- Max cards shown (3 for trial, more for paid)
- Submits → updates DB directly
- Bot picks up changes on next cycle

## Run locally
```
cd "C:\Users\J\Documents\LLM\card-scout"
python dashboard/app.py
```
Then open http://localhost:5000 in browser.

## Architecture
- Flask (single-file app, no DB migrations needed)
- Reads/writes card_scout.db directly via SQLAlchemy (same DB as bot)
- Auth = Discord webhook URL lookup (simple, no separate auth system)
- Pure HTML + tiny vanilla JS (no React/Vue)

## Deploy
See `dashboard/DEPLOY.md` for Hetzner setup.
