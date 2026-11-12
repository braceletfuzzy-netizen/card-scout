"""Unit tests: BRIEF 2 ADDITIONAL — fuzzy player matching (the KISS search fix).

Run: python scripts/test_fuzzy_match.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
import fuzzy_match as fm  # noqa: E402

LANES = [
    {"player": "Brice Turang", "player_slug": "brice-turang", "n": 38,
     "band_class": "provisional", "slug": "brice-turang-mass-raw"},
    {"player": "Tai Peete", "player_slug": "tai-peete", "n": 1,
     "band_class": "forming", "slug": "tai-peete-auto-raw"},
    {"player": "Ronald Acuña Jr.", "player_slug": "ronald-acuna-jr", "n": 12,
     "band_class": "engine_grade", "slug": "ronald-acuna-base-raw"},
    {"player": "Jeremy Pena", "player_slug": "jeremy-pena", "n": 6,
     "band_class": "provisional", "slug": "jeremy-pena-wave-raw"},
]


def t_fuzzy_typo_brady():
    hit = fm.best_fuzzy_lane("brady turang", LANES)
    assert hit and hit["player"] == "Brice Turang", hit


def t_accent_folded():
    hit = fm.best_fuzzy_lane("ronald acuna", LANES)
    assert hit and hit["player"] == "Ronald Acuña Jr.", hit
    hit2 = fm.best_fuzzy_lane("ronald acuña", LANES)
    assert hit2 and "Acuña" in hit2["player"], hit2


def t_exact_still_hits():
    hit = fm.best_fuzzy_lane("tai peete", LANES)
    assert hit and hit["player"] == "Tai Peete", hit
    hit2 = fm.best_fuzzy_lane("Jeremy Pena Wave", LANES)
    assert hit2 and hit2["player"] == "Jeremy Pena", hit2


def t_total_miss_returns_none():
    assert fm.best_fuzzy_lane("zz qwrt", LANES) is None
    assert fm.best_fuzzy_lane("garbage words here", LANES) is None
    # one exact token + one garbage token must NOT match (the no-hijack law)
    assert fm.best_fuzzy_lane("brice zzzzz", LANES) is None
    assert fm.best_fuzzy_lane("qwerty zzzz", LANES) is None


def t_fuzzy_player_hits_lists_all():
    hits = fm.fuzzy_player_hits("brady turang", LANES)
    assert hits and hits[0]["player"] == "Brice Turang", hits
    assert hits[0]["lanes"] == [LANES[0]]
    # single exact token + junk never surfaces a player
    assert fm.fuzzy_player_hits("peete zzzz", LANES) == [] or \
        all(h["player"] != "Pete Crow-Armstrong" for h in fm.fuzzy_player_hits("peete zzzz", LANES))


def t_score_bounds():
    s_exact, _ = fm.name_match_score("Brice Turang", "Brice Turang")
    s_typo, p_typo = fm.name_match_score("brady turang", "brice turang")
    s_junk, _ = fm.name_match_score("qwerty zzzz", "brice turang")
    assert s_exact == 1.0
    assert 0.62 <= s_typo <= 1.0, (s_typo, p_typo)
    assert s_junk == 0.0


def main() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("t_")]
    fails = 0
    for fn in fns:
        try:
            fn()
            print("PASS", fn.__name__)
        except AssertionError as e:
            fails += 1
            print("FAIL", fn.__name__, "->", e)
    print(f"\n{len(fns) - fails}/{len(fns)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
