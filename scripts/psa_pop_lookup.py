"""
PSA Population Lookup via lulzasaur's Apify actor.
Backup path while we build our own Puppeteer actor.

Cost: $15/1k results (cheap at Jim's scale = ~$1.44/mo).
Speed: 30-60 sec per lookup.

Usage:
    result = lookup_psa_population("https://www.psacard.com/pop/...")
    if result:
        for card in result:
            print(f"{card['subject']}: PSA 10 = {card['psaPop']['grade10']}")
"""

import requests
import time
import os

# Load Apify token from environment (NEVER commit tokens to code)
APIFY_TOKEN = os.environ['APIFY_TOKEN']

# Hugo's PSA Population Lookup actor (replaces lulzasaur).
# v1.0 — verified working 2026-09-13. Cost ~$0.005-0.013/run.
# ~20% login flake (auto-resolves on retry).
LULZASAUR_PSA_ACTOR = "DgLihiFRCa1Qf781s"  # fuzzy_bracelet/psa-population-lookup


def lookup_psa_population(set_url, max_results=10, max_wait_sec=180, bright_data_token=None):
    """Look up PSA population data for a set URL.

    Args:
        set_url: Direct PSA set URL
        max_results: Max cards to return
        max_wait_sec: Max time to wait for run
        bright_data_token: Required by actor's input schema (for compat only)

    Returns:
        list of cards with grade breakdown, or None on failure
    """
    if bright_data_token is None:
        from pathlib import Path
        bd_path = Path(r"C:/Users/J/Documents/LLM/card-scout/config/bright-data-token.txt")
        if bd_path.exists():
            bright_data_token = bd_path.read_text().strip()

    payload = {
        "brightDataToken": bright_data_token,
        "mode": "setUrl",
        "setUrl": set_url,
        "maxCards": max_results,
    }

    # Start run
    r = requests.post(
        f"https://api.apify.com/v2/acts/{LULZASAUR_PSA_ACTOR}/runs?token={APIFY_TOKEN}",
        json=payload,
        timeout=30
    )
    run_data = r.json().get("data", {})
    run_id = run_data.get("id")

    if not run_id:
        print(f"  [POP] Failed to start lulzasaur run: {r.text[:200]}")
        return None

    # Poll
    for i in range(max_wait_sec // 10):
        time.sleep(10)
        s = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}",
            timeout=15
        ).json().get("data", {})
        status = s.get("status")

        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            break

    if status != "SUCCEEDED":
        print(f"  [POP] Lulzasaur run failed: {status}")
        return None

    # Get results
    dataset_id = s.get("defaultDatasetId")
    items = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}",
        timeout=15
    ).json()

    # Check if all items are diagnostics or empty (login flake — pop page returned but no data)
    # Retry once if so (PSA brand-selection flake ~20% of runs)
    non_diag = [i for i in items if not i.get('_diagnostic') and not i.get('_error')] if items else []
    if not non_diag:  # Empty list, empty items, or all diagnostics
        print(f"  [POP] Run returned no usable data (login flake). Retrying...")
        time.sleep(2)
        # Re-run
        r = requests.post(
            f"https://api.apify.com/v2/acts/{LULZASAUR_PSA_ACTOR}/runs?token={APIFY_TOKEN}",
            json=payload,
            timeout=30
        )
        run_data = r.json().get("data", {})
        run_id = run_data.get("id")
        if run_id:
            for i in range(max_wait_sec // 10):
                time.sleep(10)
                s = requests.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}",
                    timeout=15
                ).json().get("data", {})
                status = s.get("status")
                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break
            if status == "SUCCEEDED":
                dataset_id = s.get("defaultDatasetId")
                items = requests.get(
                    f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}",
                    timeout=15
                ).json()
                non_diag = [i for i in items if not i.get('_diagnostic') and not i.get('_error')] if items else []
                if non_diag:
                    print(f"  [POP] ✓ Retry succeeded ({len(non_diag)} cards)")

    return items


def extract_pop_summary(items, subject_filter=None):
    """Extract a summary of pop data from Hugo's actor results.

    Hugo's actor returns 2 kinds of items:
    1. Data rows (card_no, name, total_pop, psa_10_pop, grade_breakdown)
    2. Diagnostics (_diagnostic: true) - filter these out

    Args:
        items: list of dicts from actor
        subject_filter: optional substring to filter by (e.g., 'jeter')

    Returns:
        dict with PSA pop data, or None if no data found
    """
    if not items:
        return None

    # Filter out diagnostics + errors
    data_rows = [i for i in items if not i.get('_diagnostic') and not i.get('_error')]
    if not data_rows:
        return None

    # Filter by subject if provided
    if subject_filter:
        data_rows = [r for r in data_rows if subject_filter.lower() in (r.get('name') or '').lower()]

    if not data_rows:
        return None

    # For a specific card, find best match (non-set-total)
    if subject_filter:
        # Prefer non-set-total rows
        candidates = [r for r in data_rows if not r.get('is_set_total')]
        if not candidates:
            candidates = data_rows  # fallback to anything
        # Prefer exact name match, then longest name, then first
        sf_lower = subject_filter.lower()
        match = None
        # 1. Exact match (name equals subject_filter)
        for c in candidates:
            if (c.get('name') or '').lower() == sf_lower:
                match = c
                break
        # 2. Starts-with match (name starts with subject_filter)
        if not match:
            for c in candidates:
                if (c.get('name') or '').lower().startswith(sf_lower):
                    match = c
                    break
        # 3. Longest name containing subject_filter
        if not match:
            containing = [c for c in candidates if sf_lower in (c.get('name') or '').lower()]
            if containing:
                match = max(containing, key=lambda c: len(c.get('name') or ''))
        # 4. First candidate
        if not match:
            match = candidates[0]
        return {
            'spec_id': match.get('card_no'),
            'subject': match.get('name'),
            'card_number': match.get('card_no'),
            'year': None,
            'psa_10_pop': match.get('psa_10_pop', 0),
            'psa_9_pop': match.get('grade_breakdown', {}).get('9', 0),
            'total_pop': match.get('total_pop', 0),
            'all_grades': match.get('grade_breakdown', {})
        }

    # Aggregate stats across set
    psa10_counts = [r.get('psa_10_pop', 0) for r in data_rows if r.get('psa_10_pop', 0) > 0]
    psa10_counts.sort()
    n = len(psa10_counts)
    if n == 0:
        return None
    return {
        'cards_found': n,
        'psa_10_median': psa10_counts[n // 2],
        'psa_10_min': psa10_counts[0],
        'psa_10_max': psa10_counts[-1],
        'cards_with_psa10': n
    }


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("Testing PSA pop lookup via lulzasaur...")
    test_url = "https://www.psacard.com/pop/tcg-cards/2024/pokemon-ssp-en-surging-sparks/285178"
    items = lookup_psa_population(test_url, max_results=5)
    print(f"\nGot {len(items) if items else 0} cards")
    if items:
        print(f"\nFirst card summary:")
        print(extract_pop_summary([items[0]]))
