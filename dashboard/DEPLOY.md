# Deploy Card Scout Dashboard

Three options, ranked by cost + simplicity for your scale (1-10 customers).

---

## Option A: Render.com (RECOMMENDED for now)

**Cost:** $0/mo (free tier) or $7/mo (Starter)
**Time to deploy:** 30 minutes
**Best for:** MVP / 1-100 customers

### Steps

1. **Create Render account**: https://render.com (GitHub signup)

2. **Create new Web Service**:
   - Connect your GitHub repo (`card-scout`)
   - Root dir: `dashboard/`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app -b 0.0.0.0:$PORT`

3. **Create `dashboard/requirements.txt`**:
   ```
   flask==3.1.3
   gunicorn==23.0.0
   sqlalchemy==2.0.36
   ```

4. **Set environment variables** (in Render dashboard):
   - `SECRET_KEY` = random 64-char hex
   - `GOOGLE_SHEET_ID` = your sheet ID
   - `GOOGLE_APPLICATION_CREDENTIALS` = paste JSON content as a single env var

5. **Persistent disk** (Render add-on, $1/mo):
   - Mount path: `/data`
   - Set `DATABASE_URL=sqlite:////data/card_scout.db`
   - Run migration: copy card_scout.db to /data on first deploy

6. **Custom domain** (optional, $0):
   - Add `dashboard.cardscout.app` via CNAME

### Pros
- Zero config (auto-SSL, auto-deploy from git push)
- Free tier works for testing
- Easy to scale up

### Cons
- SQLite on Render's ephemeral disk is risky — needs persistent disk add-on
- Slower than bare metal at high scale (but fine for 1-100 customers)

---

## Option B: Hetzner VPS + nginx + gunicorn

**Cost:** €4.50/mo (~€54/year)
**Time to deploy:** 2-3 hours
**Best for:** When you have 50+ customers or want full control

### Steps

1. **Create Hetzner Cloud server**: CX22 (€4.50/mo) — 4 GB RAM, 40 GB SSD
   - OS: Ubuntu 24.04
   - Region: Falkenstein or Ashburn (closest to your customers)

2. **SSH in and install**:
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx certbot python3-certbot-nginx
   pip3 install flask gunicorn sqlalchemy gspread python-dotenv
   ```

3. **Deploy code**:
   ```bash
   git clone https://github.com/yourname/card-scout.git
   cd card-scout/dashboard
   # Create .env with SECRET_KEY, GOOGLE_SHEET_ID, GOOGLE_APPLICATION_CREDENTIALS
   # Copy card_scout.db to /var/lib/cardscout/card_scout.db
   ```

4. **Systemd service** (`/etc/systemd/system/cardscout-dashboard.service`):
   ```ini
   [Unit]
   Description=Card Scout Dashboard
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/home/cardscout/card-scout/dashboard
   Environment="PATH=/usr/bin:/usr/local/bin"
   EnvironmentFile=/home/cardscout/card-scout/dashboard/.env
   ExecStart=/usr/local/bin/gunicorn app:app -b 127.0.0.1:5000 --workers 2

   [Install]
   WantedBy=multi-user.target
   ```

5. **Nginx config** (`/etc/nginx/sites-available/cardscout`):
   ```
   server {
     listen 80;
     server_name dashboard.cardscout.app;
     location / {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
     }
   }
   ```

6. **SSL**:
   ```bash
   sudo certbot --nginx -d dashboard.cardscout.app
   ```

### Pros
- Full control
- Cheap
- Scales easily (just upgrade the VPS)

### Cons
- You manage the server (security updates, backups, etc.)
- More setup time
- Need to handle DB backups yourself (cron job to S3)

---

## Option C: Hugging Face Spaces (CHEAPEST)

**Cost:** $0/mo (free CPU tier)
**Time to deploy:** 1 hour
**Best for:** Public demos / hackathon-style launches

### Steps

1. Create HF account: https://huggingface.co
2. New Space → Gradio or Docker SDK
3. Add `app.py` + `requirements.txt`
4. Free tier has limited CPU (sleeps after 48h of inactivity)

### Pros
- Free

### Cons
- Slow (free CPU)
- Cold starts (sleeps)
- Not for production

---

## What to deploy for Card Scout right now

**Pick Option A (Render)** when you have 5+ paying customers.
**Pick Option B (Hetzner)** when you hit 50+ customers OR if Render free tier sleeps hurt you.

For now, run locally. The dashboard works on localhost for development.
