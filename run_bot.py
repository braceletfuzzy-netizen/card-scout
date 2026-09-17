#!/usr/bin/env python3
"""Wrapper to run discord_alert_bot_v3.py with .env loaded."""
import os
import sys
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# Inject APIFY_TOKEN explicitly (script reads it at module load)
if not os.getenv('APIFY_TOKEN'):
    print('[FAIL] APIFY_TOKEN not in .env')
    sys.exit(1)

# Run the bot script via runpy
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
import runpy
sys.argv = ['discord_alert_bot_v3.py'] + sys.argv[1:]
runpy.run_path('scripts/discord_alert_bot_v3.py', run_name='__main__')
