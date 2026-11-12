"""Unit tests: targeted-links query builder (BRIEF 2; 5 lane shapes).

Run:  python scripts/test_targeted_links.py
Covers brief acceptance #4: player-only fallback (set unknown), variant-
included, grade-included, cap overflow, campid present. Pure functions only —
no network calls; the tagging function here is a FAKE replicating the shape
of band_pages.epn_tag so the suite runs without the .env arming state.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
import targeted_links as tl  # noqa: E402


FAKE_CAMPID = "1111111111"


def fake_epn_tag(view_url: str, lane_slug: str) -> dict:
    """Shape-identical to band_pages.epn_tag (armed branch) — proves links,
    through build_targeted_links, carry the campaign id into the URL."""
    params = {
        "mkcid": "1", "mkrid": "711-53200-19255-0", "siteid": "0",
        "campid": FAKE_CAMPID, "customid": lane_slug,
        "toolid": "10001", "mkevt": "1",
    }
    import urllib.parse
    sep = "&" if "?" in view_url else "?"
    return {"href": view_url + sep + urllib.parse.urlencode(params), "tagged": True}


def campid_links(lane: dict) -> list[dict]:
    return tl.build_targeted_links(lane, fake_epn_tag)


def test_player_only_fallback_when_set_unknown():
    # registry shape: a lane with NO product and NO set info at all
    lane = {"player": "Jeremy Pena", "product": "", "lane_display": "",
            "slug": "jeremy-pena-mass-raw", "search_q": "Jeremy Pena"}
    links = campid_links(lane)
    first = links[0]
    assert "Jeremy Pena" in first["tokens"]
    # player-only survives: first link's token list IS the player query when
    # the lane adds nothing else
    assert first["tokens"].split()[0] == "Jeremy"
    assert fake_epn_tag.__name__ == "fake_epn_tag"


def test_variant_included():
    # lane-exact: the variant name rides in the targeted query
    lane = {"player": "Brice Turang", "product": "2026 Topps Chrome",
            "lane_display": "Pink Wave Refractor", "variant": "Pink Wave Refractor",
            "slug": "brice-turang-pink-wave", "search_q": ""}
    links = campid_links(lane)
    q = links[0]["tokens"]
    q_l = q.lower()
    assert "pink wave refractor" in q_l, q
    assert "2026 topps chrome" in q_l, q
    assert "Brice" in q


def test_grade_included():
    # grade lane: the search_q (curator-tuned) carries "PSA 10"
    lane = {"player": "Jeremy Pena", "product": "",
            "grade_bucket": "PSA10", "lane_display": "Numbered",
            "slug": "jeremy-pena-graded-numbered-psa10",
            "search_q": "Jeremy Pena Numbered PSA 10"}
    links = campid_links(lane)
    q = links[0]["tokens"]
    assert q == "Jeremy Pena Numbered PSA 10", q
    assert "psa 10" in q.lower()


def test_cap_overflow():
    # 8-token cap: >8 tokens -> the query is word-truncated to <= 8
    long_q = "Jeremy Pena 2023 Topps Chrome Update Purple Wave Refractor PSA 10"
    lane = {"player": "Jeremy Pena", "product": "2023 Topps Chrome Update",
            "lane_display": "Purple Wave Refractor", "grade_bucket": "PSA10",
            "slug": "jeremy-pena-purple", "search_q": long_q}
    links = campid_links(lane)
    q = links[0]["tokens"]
    assert len(q.split()) <= tl.MAX_TOKENS, q
    # player survives truncation (priority-ordered: player is never the
    # dropped end)
    assert q.split()[0] == "Jeremy"


def test_campid_present_in_every_link():
    lane = {"player": "Brice Turang", "product": "2026 Topps", "grade_bucket": "raw",
            "lane_display": "Gold", "slug": "brice-turang-2026-topps-gold-raw",
            "search_q": "Brice Turang 2026 Topps Gold"}
    links = campid_links(lane)
    assert len(links) == 3, links           # lane-exact + wider + widest
    for l in links:
        assert "campid=%s" % FAKE_CAMPID in l["href"], l["href"]
        assert "customid=brice-turang-2026-topps-gold-raw" in l["href"]
        assert l["href"].startswith("https://www.ebay.com/sch/i.html?_nkw=")
        assert "_sop=16" in l["href"]


def test_refine_composition():
    # refine: base targeted query + user terms, one URL, still capped.
    url = tl.refine_href("Brice Turang Gold", "2026 chrome update pink")
    assert "_nkw=Brice+Turang+Gold+2026+chrome+update+pink" in url, url
    assert "_sop=16" in url
    # empty user terms degrade to the base query unchanged
    assert "_nkw=Brice+Turang+Gold" in tl.refine_href("Brice Turang Gold", "")


def test_refine_vars():
    v = tl.refine_template_vars()
    assert v["placeholder"] == "refine (e.g. 2022 chrome update pink wave)"
    assert v["button_label"]


def main() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
