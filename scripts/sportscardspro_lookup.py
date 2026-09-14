"""
Sportscardspro Sold Data Lookup - Bot Wrapper

Calls fuzzy_bracelet/sportscardspro-lookup actor and extracts:
- PSA 10 price + 30-day delta
- PSA 9 price
- PSA 10 sales volume ("1 sale per week")
- Total PSA 10 sales count
- Recent sales list (for spread analysis)

Cost: ~$0.001/run via BD free tier
"""
import json
import time
import urllib.request
from pathlib import Path

APIFY_TOKEN = Path(r"C:/Users/J/Documents/LLM/card-scout/config/apify-token.txt").read_text().strip()
BD_TOKEN = Path(r"C:/Users/J/Documents/LLM/card-scout/config/bright-data-token.txt").read_text().strip()
ACTOR_ID = "PGRtI1ZjuqUELHCGr"  # fuzzy_bracelet/sportscardspro-lookup
BASE_URL = "https://api.apify.com/v2"


def lookup_sportscardspro(card_url, max_sales=50, max_wait_sec=60):
    """Run the sportscardspro actor and return parsed result.

    Args:
        card_url: full sportscardspro URL for the card
        max_sales: how many individual sale rows to fetch (default 50)
        max_wait_sec: timeout for the Apify run

    Returns:
        dict with prices_by_tier, sold_counts_by_grade, sales list, title
        None on failure
    """
    run_input = {
        "brightDataToken": BD_TOKEN,
        "cardUrl": card_url,
        "maxSales": max_sales,
        "includeSalesList": True,
    }

    # Start run
    req = urllib.request.Request(
        f"{BASE_URL}/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}",
        data=json.dumps(run_input).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            run = json.loads(r.read()).get("data", {})
            run_id = run.get("id")
    except Exception as e:
        print(f"  [SCPRO] Failed to start actor: {e}")
        return None

    # Poll until done
    start = time.time()
    while time.time() - start < max_wait_sec:
        time.sleep(3)
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/acts/{ACTOR_ID}/runs/{run_id}?token={APIFY_TOKEN}"
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                run = json.loads(r.read()).get("data", {})
            status = run.get("status")
            if status in ("SUCCEEDED", "FAILED", "ABORTED"):
                break
        except Exception:
            continue

    if status != "SUCCEEDED":
        print(f"  [SCPRO] Actor run {status}")
        return None

    # Fetch dataset
    dataset_id = run.get("defaultDatasetId")
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            items = json.loads(r.read())
    except Exception as e:
        print(f"  [SCPRO] Failed to fetch dataset: {e}")
        return None

    if not items:
        return None

    return items[0]


def extract_sold_summary(data, card_name=None):
    """Extract a clean sold-data summary from the actor's output.

    Useful for bot alert format:
        - psa_10_price, psa_9_price, ungraded_price (all USD)
        - psa_10_volume ("1 sale per week")
        - psa_10_30d_delta (USD change)
        - psa_10_sold_count (how many sold in last 30)
        - recent_sales (list of {date, price_usd, title, ebay_url})
    """
    if not data:
        return None

    prices = data.get("prices_by_tier", {})
    sold_counts = data.get("sold_counts_by_grade", {})
    sales = data.get("sales", [])

    summary = {
        "title": data.get("title"),
        "source_url": data.get("url"),
        "psa_10_price": prices.get("psa_10", {}).get("price_usd"),
        "psa_10_delta_30d": prices.get("psa_10", {}).get("delta_30d_usd"),
        "psa_10_volume": prices.get("psa_10", {}).get("volume"),
        "psa_10_sold_30d": sold_counts.get("psa_10"),
        "psa_9_price": prices.get("psa_9", {}).get("price_usd"),
        "psa_9_volume": prices.get("psa_9", {}).get("volume"),
        "psa_9_sold_30d": sold_counts.get("psa_9"),
        "psa_8_price": prices.get("psa_8", {}).get("price_usd"),
        "ungraded_price": prices.get("ungraded", {}).get("price_usd"),
        "ungraded_sold_30d": sold_counts.get("ungraded"),
        "recent_sales": sales,
    }
    return summary


# ============ TEST ============
if __name__ == "__main__":
    test_url = "https://www.sportscardspro.com/game/baseball-cards-1995-topps/derek-jeter-199"
    print(f"Testing: {test_url}")
    data = lookup_sportscardspro(test_url, max_sales=10)
    if data:
        summary = extract_sold_summary(data)
        print(json.dumps(summary, indent=2))
    else:
        print("FAIL")
