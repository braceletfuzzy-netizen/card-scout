"""
Grade detector for trading card listings.

Parses grade markers from eBay listing titles.
Returns a structured dict with detected authority + numeric grade + tier bucket.

Per the ticker spec (card-scout-ticker-system-spec-2026-09-14.md):
- Show the per-grade market values, not "buy/sell spread" math
- Customer decides if it's a deal based on the grade the listing is actually sold at

Tier buckets (consistent with the spec's 6-bucket system):
- psa_10 (Gem Mint, $XXX+)
- psa_9 (Mint, $XX-XX)
- psa_8 (NM-MT, $XX)
- psa_lower (PSA 7 or below)
- raw (ungraded)
- other_graders (BGS/CGC/SGC)

Usage:
    from grade_detector import detect_grade
    result = detect_grade("1996 Topps Chrome #80 Derek Jeter BGS 9.5 GEM MINT")
    # => {'authority': 'BGS', 'grade': 9.5, 'tier': 'psa_9', 'is_graded': True}

    detect_grade("1995 Topps Derek Jeter Future Star #199 (raw)")
    # => {'authority': None, 'grade': None, 'tier': 'raw', 'is_graded': False}
"""

import re
from typing import Dict, Optional


# Grade regexes — order matters: BGS half-points (.5) before PSA full ints,
# so "BGS 9.5" doesn't get matched as "BGS 9" only.
GRADE_PATTERNS = [
    # BGS half-points (most specific)
    (r'\bBGS\s*(\d+\.5)\s*(GEM\s*MINT|BLACK\s*LABEL|BGS)?\b', 'BGS'),
    # BGS with prime variants
    (r'\bBGS\s*10\s*(PRIME|BGS\s*PRIME)?\b', 'BGS'),  # BGS 10 Prime
    # BGS / CGC / SGC whole numbers
    (r'\bBGS\s*(\d+)\b', 'BGS'),
    (r'\bCGC\s*(\d+(?:\.5)?)\b', 'CGC'),
    (r'\bSGC\s*(\d+(?:\.5)?)\b', 'SGC'),
    # PSA descriptors (special cases)
    (r'\bPSA\s*(?:GEM\s*MINT\s*10|GM\s*10|10\s*GEM\s*MINT|10\s*GM)\b', 'PSA'),
    (r'\bPSA\s*MT\s*(\d+)\b', 'PSA'),  # "PSA MT 9" = PSA 9 Mint
    # PSA standard (with optional OC qualifiers like "OC" / "AUTO")
    (r'\bPSA\s*(\d+)(?:\s*(?:OC|AUTO|MINT))?\b', 'PSA'),
]

# Words/phrases indicating UNGRADED (raw) condition
RAW_INDICATORS = [
    r'\b(?:ungraded|raw|unslabbed|no\s*grade|not\s*graded|ungraded\s*card)\b',
    r'\b(?:Near\s*Mint|NM|NM\s*\-?MT|EXMT|Excellent|Mint\s*condition)\b',  # raw condition descriptors
    r'\b(?:VG\s*\-?FINE|GD\s*\-?VG|GOOD|FAIR|POOR)\b',  # lower raw grades
]


def _parse_grade(match: re.Match, authority: str) -> Optional[float]:
    """Extract a numeric grade from a regex match. Returns None if can't parse."""
    if match.lastindex and match.group(1):
        try:
            return float(match.group(1))
        except ValueError:
            return None
    # Special cases like "BGS 10 Prime" or "PSA GEM MINT 10" — default to 10
    full_match = match.group(0).upper()
    if '10' in full_match or 'GEM MINT' in full_match or 'BLACK LABEL' in full_match:
        return 10.0
    return None


def _bucket_to_tier(authority: str, grade: Optional[float]) -> str:
    """
    Map (authority, grade) → tier bucket matching the bot's 6-bucket filter.

    The bot uses track_psa_10 / track_psa_9 / track_psa_8 / track_psa_lower /
    track_raw / track_other_graders. We map ALL grading companies into these
    tiers by numeric grade (PSA 10 and BGS 10 both → psa_10).
    """
    if grade is None:
        return 'raw'

    if grade >= 10:
        return 'psa_10'
    elif grade >= 9:
        return 'psa_9'
    elif grade >= 8:
        return 'psa_8'
    else:
        return 'psa_lower'


def detect_grade(title: str) -> Dict:
    """
    Parse grade information from a card listing title.

    Returns dict with:
      - authority: str | None (PSA, BGS, CGC, SGC, or None if raw)
      - grade: float | None (numeric grade, e.g. 9.5, 10.0)
      - tier: str (psa_10 / psa_9 / psa_8 / psa_lower / raw / other_graders)
      - is_graded: bool

    Edge cases:
      - Multiple grades in title (e.g. "PSA 9 BGS 9.5") → first one wins
      - "MINT" alone without authority → treated as raw (not a graded marker)
      - Numbers without grade context (card numbers, prices) → ignored
    """
    if not title:
        return {'authority': None, 'grade': None, 'tier': 'raw', 'is_graded': False}

    title_upper = title.upper()

    # Try each grade pattern
    for pattern, authority in GRADE_PATTERNS:
        match = re.search(pattern, title_upper, re.IGNORECASE)
        if match:
            grade = _parse_grade(match, authority)
            if grade is not None and 1.0 <= grade <= 10.0:
                tier = _bucket_to_tier(authority, grade)
                return {
                    'authority': authority,
                    'grade': grade,
                    'tier': tier,
                    'is_graded': True,
                }

    # No grade marker found — check for raw indicators (any match = probably raw)
    for raw_pat in RAW_INDICATORS:
        if re.search(raw_pat, title, re.IGNORECASE):
            return {'authority': None, 'grade': None, 'tier': 'raw', 'is_graded': False}

    # No grade marker AND no raw indicator = ambiguous, treat as raw
    return {'authority': None, 'grade': None, 'tier': 'raw', 'is_graded': False}


def bucket_listings(items: list) -> Dict[str, list]:
    """
    Bucket a list of eBay listing items by grade tier.

    Returns:
        {
          'psa_10': [item, ...],
          'psa_9':  [...],
          'psa_8':  [...],
          'psa_lower': [...],
          'raw':    [...],
          'other_graders': [...],  # not used for now, all graders → numeric tier
        }
    """
    buckets = {
        'psa_10': [],
        'psa_9': [],
        'psa_8': [],
        'psa_lower': [],
        'raw': [],
        'other_graders': [],
    }

    for item in items:
        result = detect_grade(item.get('title', ''))
        tier = result['tier']
        item_copy = dict(item)
        item_copy['_grade_info'] = result
        buckets[tier].append(item_copy)

    return buckets


# Self-test
if __name__ == '__main__':
    test_titles = [
        "1996 Topps Chrome #80 Derek Jeter Refractor PSA 7 Future Star",
        "PSA 10 GEM MINT -- 1996 Topps - Future Star Derek Jeter #219 HOF",
        "1996 Topps Chrome #80 Derek Jeter BGS 9.5 GEM MINT",
        "1995 Topps Derek Jeter Future Star #199 New York Yankees HOF",  # raw
        "1996 Topps - Future Star Derek Jeter PSA MT 9 #219",
        "🔥DEREK JETER🔥1996 TOPPS FUTURE STAR ROOKIE CARD VERY GOOD",  # raw (no authority)
        "1995 Topps FUTURE STAR Derek Jeter PSA 9 MINT",
        "BGS 10 Black Label Derek Jeter",
        "1995 Topps #199 - Graded Card - Will Send for Grading",
    ]

    print("="*70)
    for title in test_titles:
        result = detect_grade(title)
        print(f"\n{title}")
        print(f"  → {result}")
