import json
import sqlite3
import os
import sys
import requests
import urllib.parse
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

DB_PATH = Path(__file__).parent.parent / 'card_scout.db'
REPORTS_DIR = Path(r"C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/reports")

# Disclaimer (B4)
DISCLAIMER = "Educational only — not financial advice — full text at cardscout.pro/disclaimer"

def generate_ebay_url(query):
    # Base URL
    base_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote_plus(query)}&_sop=16"
    
    # EPN Tagging (Job B2)
    epn_id = os.environ.get('EPN_CAMPAIGN_ID')
    if epn_id:
        return f"{base_url}&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={epn_id}&toolid=10001&mkevt=1"
    return base_url

def send_to_discord(webhook_url, content):
    if not webhook_url:
        return False
    try:
        resp = requests.post(webhook_url, json={"content": content}, timeout=10)
        if resp.status_code in [200, 204]:
            return True
        return False
    except:
        return False

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    customers = conn.execute("SELECT * FROM customers WHERE subscription_status != 'placeholder'").fetchall()
    
is_live = '--live' in sys.argv
    
    if is_live:
        try:
            r = requests.get('https://cardscout.pro/disclaimer', timeout=10)
            if r.status_code != 200:
                print(f"[FATAL] Live send blocked. /disclaimer returned {r.status_code}. Must be 200 to deploy live.")
                sys.exit(1)
        except Exception as e:
            print(f"[FATAL] Live send blocked. /disclaimer reachability error: {e}")
            sys.exit(1)
    test_webhook = os.environ.get('DISCORD_WEBHOOK_TEST')
    if not test_webhook:
        hook_path = Path(r"C:/Users/J/Documents/LLM/card-scout/config/discord-webhook.txt")
        if hook_path.exists():
            with open(hook_path, 'r') as f:
                test_webhook = f.read().strip()
                
    for cust in customers:
        cid = cust['customer_id']
        email = cust['email']
        webhook = cust['discord_webhook']
        tier = cust['tier']
        
        # B1: Exclude placeholders
        if cid.startswith('cs_CZYAKBA') or email.endswith('@placeholder.local'):
            continue
            
        alerts_path = REPORTS_DIR / f"customer_alerts_{cid}.json"
        if not alerts_path.exists():
            continue
            
        with open(alerts_path, 'r') as f:
            alerts = json.load(f)
            
        if not alerts:
            continue
            
        # Build message
        msg_lines = [f"**Card Scout Alerts for {email}**"]
        has_alert = False
        
        for a in alerts:
            # QUIET = no message
            if a['call'] in ['QUIET', 'NO-VALID-PRINT', 'UNMEASURED']:
                continue
                
            has_alert = True
            player = a.get('player', 'Unknown')
            lane = a.get('lane', 'Unknown')
            price = a.get('price', 0)
            call = a.get('call', '')
            evidence = a.get('evidence', '')
            
            search_query = f"{player} {lane}"
            link = generate_ebay_url(search_query)
            
            # Casual / Trial-Beta framing
            if tier in ['Casual']:
                msg_lines.append(f"• 📉 **DEAL SPOTTED:** A new market-floor deal for **{player} ({lane})** is available at **${price}**.\n  *Context:* {evidence}\n  *Link:* {link}")
            else:
                # Deal-Pro+ both directions framing
                if call == 'FLOOR-BREAK':
                    emoji = "📉"
                    framing = "market-floor deal"
                elif call in ['HEAT-TAP', 'HEAT-JOIN']:
                    emoji = "📈"
                    framing = "upward market breakout"
                elif call == 'INSIDE-BAND':
                    emoji = "⚖️"
                    framing = "stable market confirmation"
                else:
                    emoji = "🔔"
                    framing = "market signal"
                    
                msg_lines.append(f"• {emoji} **SIGNAL:** A new {framing} on **{player} ({lane})** at **${price}**.\n  *Context:* {evidence}\n  *Link:* {link}")
                
        if not has_alert:
            continue
            
        msg_lines.append("\n---\n" + DISCLAIMER)
        content = "\n\n".join(msg_lines)
        
        target_url = webhook if is_live else test_webhook
        
        import hashlib
        webhook_hash = hashlib.sha256((webhook or "").encode()).hexdigest()[:8]
        emitted_count = sum(1 for a in alerts if a['call'] not in ['QUIET', 'NO-VALID-PRINT', 'UNMEASURED'])
        
        print(f"[LOG] Attempting send for {cid} (hash {webhook_hash}) | alerts included: {emitted_count}")
        
        if target_url:
            success = send_to_discord(target_url, content)
            print(f"[LOG] Send to {cid} {'SUCCESS' if success else 'FAIL'}")
        else:
            print(f"[LOG] Send to {cid} SKIPPED (No target webhook available)")

if __name__ == '__main__':
    main()
