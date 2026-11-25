"""FLEET-REJECTED (the rejected-list reader-hook, Nov-23).

THE FLEET-HARDENING ITEM-1 (agent-loop course adopt-item #2, founder GO Nov-23):
  stops cron workers / delegation children re-proposing founder- or verifier-vetoed
  ideas after restart. Vetoes die at PROPOSAL-TIME: any cron or worker imports this
  module and calls is_rejected() BEFORE proposing something new.

Ledger: fleet_rejected_list.json (same dir; this module auto-locates it via
  REJECTED_JSON env var -> CARASCOUT_ROOT env -> script-relative -> repo-relative).

Usage (one import + one call, in any cron/worker that proposes):
    from fleet_rejected import is_rejected
    rejected, entry = is_rejected(proposal_text)
    if rejected:
        print(f"[FLEET-REJECTED] Vetoed class '{entry['id']}' ({entry['cause'][:80]}...)")
        sys.exit(0)   # or skip-propose / log-and-halt per the caller's convention

  Batch mode:
    python fleet_rejected.py "proposal text one" "proposal text two" ...

Matching: keyword-fuzzy — each ledger entry carries a set of keyword stems;
an idea matches if >=MATCH_THRESHOLD stems hit (weighted: exact phrase hits count
double; single-hit-kill classes like customer-rebates veto on ONE stem hit).
Case-insensitive; matching runs both space-normalized and fully-squashed
(non-alphanumerics stripped) so "hardcoded customer IDs" hits "hard_coded_customer".
No LLM, no network, stdlib-only.
"""
# REPRODUCIBILITY-HEADER: claims tagged [Verified] were tool-checked this session; nothing here is fabricated — every seeded class cites its banked law name in fleet_rejected_list.json.

import json
import os
import re
import sys
from pathlib import Path

__all__ = ["is_rejected", "load_ledger", "MATCH_THRESHOLD"]

MATCH_THRESHOLD = 2  # distinct keyword stems required to call it a match

# Classes that veto on a SINGLE stem hit (the keyword is unambiguous alone).
SINGLE_HIT_CLASSES = {"customer-rebates", "apify-volume-scrapes"}

# module-level alias used by is_rejected (kept out of __all__ on purpose)
_SINGLE_HIT_CLASSES = SINGLE_HIT_CLASSES

_FALLBACK_ROOTS = [
    Path(r"C:\Users\J\Documents\LLM\cardscout-2.0"),
]

# Keyword stems per ledger class id. Phrase stems (with '_') must appear verbatim
# (normalized) and score 2x. Single tokens score 1x.
_CLASS_STEMS = {
    "process-all-enabled": (
        "hardcoded_ids", "hard_coded_customer", "hard_coded_id",
        "id_list", "customer_list", "iterate_over_ids",
    ),
    "customer-rebates": ("rebate", "rebates", "cash_back_to_customer"),
    "publish-engine-names": (
        "publish_engine_names", "forward_chain_names", "engine_name_public",
        "public_engine_label", "engine_grade_public", "fame_ladder", "fame_ladder_public",
    ),
    "falsify-word-civic-language": (
        "falsify_word", "civic_language_falsify", "falsify_label",
    ),
    "mixed-grade-medians": (
        "mixed_grade_median", "grade_mix_median", "ungraded_rows", "mixed_grades",
        "mixed_grade", "grade_mix", "mixing_graded",
    ),
    "ask-times-n-corner-math": (
        "ask_times_n", "ask* N", "multiply_ask_by_n", "ask_x_n", "asks_times_n",
    ),
    "memory-file-bypass-edits": (
        "bypass_memory_tool", "patch_memory_md", "shell_edit_memory",
        "memory_file_bypass", "sed_memory", "direct_write_memory_md",
    ),
    "reactive-bookings-classification": (
        "reactive_bookings", "reactive_booking_classification",
        "bookings_reactive_class",
    ),
    "apify-volume-scrapes": (
        "apify_actor", "apify_run", "apify_scrape", "apify_volume",
    ),
    "oversized-commit": (
        "commit_100mb", "commit_giant_pdf", "oversized_commit", "100mb_pdf_commit",
        "large_pdf_to_git", "commit_big_source_pdf",
    ),
}

_norm_re = re.compile(r"[\s\-_/]+")
_cache = {"mtime": None, "ledger": None}


def _ledger_candidates():
    env = os.environ.get("REJECTED_JSON")
    if env:
        yield Path(env)
    script_dir = Path(__file__).resolve().parent
    yield script_dir / "fleet_rejected_list.json"
    if script_dir.name == "scripts":  # AppData mirror -> repo master via root env
        root = os.environ.get("CARASCOUT_ROOT")
        if root:
            yield Path(root) / "For You" / "PolyScout" / "build" / "fleet_rejected_list.json"
    for root in _FALLBACK_ROOTS:
        yield root / "For You" / "PolyScout" / "build" / "fleet_rejected_list.json"


def load_ledger():
    """Load (and cache) the rejected-list ledger. Returns the 'rejected' list."""
    for cand in _ledger_candidates():
        if cand.is_file():
            mtime = cand.stat().st_mtime
            if _cache["ledger"] is None or _cache["mtime"] != mtime:
                with open(cand, "r", encoding="utf-8") as f:
                    data = json.load(f)
                _cache["ledger"] = data
                _cache["mtime"] = mtime
            return _cache["ledger"].get("rejected", [])
    return []


def _normalize(text):
    return _norm_re.sub(" ", text.lower()).strip()


def _stems_hit(stems, entry_id, text, squashed):
    """Return (score, matched_display_stems). Phrase stems ('_') match verbatim.

    Matching runs against both the space-normalized text and a fully-squashed
    variant (non-alphanumerics stripped) so compound spellings like
    "hardcoded customer IDs" still hit the hard_coded_customer stem.
    """
    hits, score = [], 0
    for stem in stems:
        phrase = "_" in stem
        needle = _normalize(stem)
        if phrase:
            parts = stem.split("_")
            # verbatim squashed-phrase, OR all key words present in the text
            # (hyphenated/variant spellings caught: 'hard-code customer IDs' -> hard/customer/IDs)
            hit = "".join(parts) in squashed
            if not hit and len(parts) > 1:
                strong = [p for p in parts if len(p) >= 4 and p in text]
                hit = len(strong) >= 2
            if not hit and len(parts) > 1:
                # stem-variant bridge: inflected forms ('hard-code' vs 'hardcoded')
                # still carry the first-4 chars of the lead word + the tail word
                lead4 = parts[0][:4]
                tail = parts[-1]
                hit = lead4 in text and (tail in text or tail in squashed)
            if hit:
                score += 2
                hits.append(stem)
        else:
            tok = needle.replace(" ", "")
            if re.search(rf"(?<![a-z]){re.escape(tok)}(?![a-z])", text.replace(" ", "_")) \
               or tok in text or tok in squashed:
                score += 1
                hits.append(stem)
    return score, hits


def is_rejected(idea_text):
    """(bool, matched_entry|None) — keyword-fuzzy match of idea_text against the ledger.

    Returns (True, entry) when >= MATCH_THRESHOLD stems of one class hit
    (phrase stems score double). Returns (False, None) when clean.
    """
    if not idea_text or not str(idea_text).strip():
        return False, None
    text = _normalize(str(idea_text))
    squashed = re.sub(r"[^a-z0-9]", "", text)
    best = None  # (score, entry, hits)
    for entry in load_ledger():
        stems = _CLASS_STEMS.get(entry.get("id"), ())
        if not stems:
            continue
        threshold = 1 if entry.get("id") in _SINGLE_HIT_CLASSES else MATCH_THRESHOLD
        score, hits = _stems_hit(stems, entry.get("id"), text, squashed)
        if score >= threshold and (best is None or score > best[0]):
            best = (score, entry, hits)
    if best:
        score, entry, hits = best
        flagged = dict(entry)
        flagged["matched_keywords"] = hits
        flagged["match_score"] = score
        flagged["threshold"] = MATCH_THRESHOLD
        return True, flagged
    return False, None


def _cli(argv):
    if not argv:
        print(__doc__)
        return 0
    any_veto = False
    for idea in argv:
        rejected, entry = is_rejected(idea)
        if rejected:
            any_veto = True
            print(f"[FLEET-REJECTED] VETO '{entry['id']}' (vetoed_by={entry['vetoed_by']}, "
                  f"score={entry['match_score']}): {entry['idea_brief']}")
            print(f"    matched: {entry['matched_keywords']}")
            print(f"    cause:   {entry['cause']}")
        else:
            print(f"[FLEET-REJECTED] clean: {idea[:80]}")
    return 2 if any_veto else 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
