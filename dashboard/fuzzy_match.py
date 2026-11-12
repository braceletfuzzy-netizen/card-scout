"""fuzzy_match.py — accent-folded, tokenized fuzzy player-matching (BRIEF 2
ADDITIONAL: the KISS search-flow rewrite).

Founder repro: searching "brady turang" (typo) dead-ended on the gratitude
page even though Brice Turang has 38 live lanes. Fix: the search-miss page
first runs a fuzzy match against the lane store's player names.

Method (graded token overlap, tuned 2026-11-12 against the full 757-lane
registry + founder repros):
  1. accent-fold (unicodedata NFKD, drop combining marks) + lowercase —
     'Acuña' matches 'acuna' both ways.
  2. tokenize (>=2 chars; honorifics jr/sr/ii/iii dropped).
  3. token similarity = max(SequenceMatcher ratio, bigram overlap):
     'brady'/'brice' 0.4, 'turang'/'turang' 1.0, 'qwerty'/anything ~0.
  4. greedy best-pairing of query tokens -> player tokens; unpaired query
     tokens are 0 (they drag the mean down — one garbage token can't ride
     a match).
  5. score = mean(pair scores) * 1.2, capped 1.0, but ONLY when at least
     one pair is strong (>= 0.7, i.e. an exact or near-exact token).
     A query with zero strong tokens can never match — 'brice zzzzz' and
     'qwerty zzzz' stay rejected while 'brady turang' (turang=1.0, brady
     0.4 -> 0.84) matches Brice Turang.

Pure functions + a registry-facing helper; unit-testable without the app.
"""
from __future__ import annotations

import difflib
import unicodedata

STRONG_PAIR = 0.7   # exact-or-near token required for any match
PAIR_FLOOR = 0.3    # below this a pair is 'unpaired' (scores 0)
THRESHOLD = 0.62    # final score gate ('brady turang' -> 0.84; junk < 0.2)


def fold(text: str) -> str:
    """Accent-fold + lowercase: 'Ronald Acuña Jr.' -> 'ronald acuna jr.'"""
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def tokens(text: str) -> list[str]:
    return [t for t in fold(text).split() if len(t) >= 2]


# honorifics that never help a match
_DROP = {"jr", "sr", "ii", "iii", "iv"}


def name_tokens(name: str) -> list[str]:
    return [t for t in tokens(name) if t not in _DROP]


def _ratio(a: str, b: str) -> float:
    """max(SequenceMatcher, bigram-overlap). SequenceMatcher alone scores
    'brady'/'brice' 0.4; bigrams rescue near-miss spellings. 'qwerty'/X ~0."""
    seq = difflib.SequenceMatcher(None, a, b).ratio()
    if len(a) < 2 or len(b) < 2:
        return seq
    A = {a[i:i + 2] for i in range(len(a) - 1)}
    B = {b[i:i + 2] for i in range(len(b) - 1)}
    return max(seq, len(A & B) / len(A | B))


def name_match_score(query: str, candidate: str) -> tuple[float, list[float]]:
    """(0..1 similarity, per-query-token pair scores). Greedy best-pairing;
    zero-strong-token queries are structurally rejected."""
    qs = name_tokens(query)
    cs = name_tokens(candidate)
    if not qs or not cs:
        return 0.0, []
    used: set[int] = set()
    pairs: list[float] = []
    for qt in qs:
        best, best_i = 0.0, -1
        for i, ct in enumerate(cs):
            if i in used:
                continue
            r = _ratio(qt, ct)
            if r > best:
                best, best_i = r, i
        if best < PAIR_FLOOR:
            pairs.append(0.0)          # unpaired: drags the mean, no hijack
        else:
            pairs.append(best)
            used.add(best_i)
    if max(pairs) < STRONG_PAIR:
        return 0.0, pairs              # no near-exact token: never a match
    mean = sum(pairs) / len(pairs)
    return min(mean * 1.2, 1.0), pairs


def best_fuzzy_lane(q: str, lanes: list[dict], threshold: float = THRESHOLD) -> dict | None:
    """Best lane by fuzzy player-name match; None below threshold.

    Tiebreak (mirrors find_lane_for_query): banded lanes first, then most
    prints, then slug.
    """
    best, best_key = None, None
    for lane in lanes:
        s, _ = name_match_score(q, lane.get("player") or "")
        if s < threshold:
            continue
        key = (s, 1 if lane.get("band_class") != "forming" else 0, int(lane.get("n") or 0),
               lane.get("slug") or "")
        if best_key is None or key > best_key:
            best, best_key = lane, key
    return best


def fuzzy_player_hits(q: str, lanes: list[dict], threshold: float = THRESHOLD,
                      limit: int = 12) -> list[dict]:
    """ALL distinct players above threshold (the miss page lists their lanes),
    best first. Each item: {'player', 'score', 'lanes': [lane, ...]}."""
    agg: dict[str, dict] = {}
    for lane in lanes:
        s, _ = name_match_score(q, lane.get("player") or "")
        if s < threshold:
            continue
        entry = agg.setdefault(lane.get("player") or "", {"player": lane.get("player") or "",
                                                          "score": 0.0, "lanes": []})
        entry["score"] = max(entry["score"], s)
        entry["lanes"].append(lane)
    out = sorted(agg.values(), key=lambda e: (-e["score"], -len(e["lanes"])))
    for e in out:
        bs = 0 if e["score"] < 1 else 0   # keep insertion order determinism
        e["lanes"].sort(key=lambda l: (1 if l.get("band_class") == "forming" else 0,
                                       -int(l.get("n") or 0), l.get("slug") or ""))
    return out[:limit]
