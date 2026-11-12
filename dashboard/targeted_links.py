"""
Targeted eBay link builder (BRIEF 2, Nov 12 2026) — the always-listings layer.

WANT honored here (Temp/hermes_brief2_targeted_links.md; builder Hugo):
- Every band page shows a "Search this lane on eBay" section underneath,
  in EVERY state (CORPUS / AGGREGATE / QUEUING) — "no live listings" is
  never a dead end; it falls through to a tagged eBay search.
- Targeted = the query is built from the lane's own structure (player +
  set + variant + grade-lane), NOT a generic player-only query.
- Pure functions + a tiny pure token-capsule the Jinja template renders;
  the only JS here is the client-side refine box (one input + one button
  that append user terms to the targeted query at CLICK TIME).

LAWS honored:
- EPN: campaign id is READ IN PLACE from .env via band_pages.epn_tag's
  arming switch — no campid -> plain link (the MPA guard is inherited,
  never bypassed, never duplicated here).
- URL pattern REUSED from the proven alert/digest path (digest_delivery.
  generate_ebay_url / public_price_bp See-live-listings):
  https://www.ebay.com/sch/i.html?_nkw=<quote_plus(q)>  -> epn_tag() appends
  mkcid/mkrid/siteid/campid/customid/toolid/mkevt. Nothing new invented.
- target=_blank + rel="sponsored nofollow" (matches the listing-row links).
- NO server round-trip, NO storage, NO cookies for user terms — the refine
  input is read only in the browser at click time (grep for its persistence
  shows: absent; there is no fetch, no localStorage write, no form submit).
- Add-only: this module is never imported at app boot except by band_pages
  (degrade, never crash); it touches nothing else on the page.
"""
from __future__ import annotations

import urllib.parse

MAX_TOKENS = 8  # founder cap: drop lowest-priority tokens on overflow


# ---------------------------------------------------------------------------
# LANED QUERY TOKENS (priority-ordered; pure, no IO — fully unit-testable)
# ---------------------------------------------------------------------------
def lane_tokens(player: str | None, product: str | None, lane_display: str | None,
                variant: str | None = None, raw_query: str | None = None) -> str:
    """Priority-ordered targeted query: player + set + variant + lane.

    Priority (high -> low); overflow drops from the BOTTOM of the join:
      1. player        (never dropped — brief: player-only fallback survives)
      2. set keywords  (product, e.g. "2026 Topps Chrome Update")
      3. variant       (the lane-exact name when the lane has one, e.g.
                       "Pink Wave Refractor"; else the lane display token)
      4. grade lane    (the lane's grade lane term)
    """
    player = (player or "").strip()
    product = (product or "").strip()
    variant = (variant or "").strip()
    lane_display = (lane_display or "").strip()
    raw_query = (raw_query or "").strip()

    if product and variant:
        # variant subsumes the lane display inside lane-exact queries
        # (e.g. "Pink Wave Refractor" already names the variant); the set
        # still rides along for targeted matching.
        base = [player, product, variant]
    elif raw_query:
        # registry search_q is already the curator-tuned targeted query
        # (e.g. "Jeremy Pena Blue PSA 9"); it IS the lane-exact intent.
        base = raw_query.split()
    else:
        base = [t for t in (player, product, lane_display or variant) if t]
    # 8-token cap, priority-ordered: lowest-priority tokens (the tail) drop
    # first; the player (head of the join) survives every overflow.
    return _enforce_token_cap(" ".join(t for t in base if t))


def lane_query(lane: dict) -> str:
    """Targeted query for a lane row (registry/composed-lane shape).

    Prefers the existing lane['search_q'] when it is already targeted
    (curator-tuned, e.g. player + set + variant + grade); this keeps the
    live-listings rail and the always-on search section on the SAME intent.
    Falls back to structural assembly when there is nothing better.
    """
    q = (lane.get("search_q") or "").strip()
    if q:
        # the cap applies to EVERY emitted query (including curator search_q:
        # priority order is preserved because search_q is already ordered
        # player-first — the tail grade terms drop, not the player)
        return _enforce_token_cap(q)
    return lane_tokens(
        lane.get("player"), lane.get("product") or lane.get("set"),
        lane.get("lane_display") or lane.get("variant"),
    )


def wider_query(lane: dict) -> str:
    """Player + product (the wider net; variant dropped)."""
    return " ".join(t for t in
                    ((lane.get("player") or "").strip(),
                     (lane.get("product") or "").strip()) if t) \
        or (lane.get("player") or "").strip()


def widest_query(lane: dict) -> str:
    """Player-only (widest)."""
    return (lane.get("player") or "").strip()


# ---------------------------------------------------------------------------
# TOKEN CAP CAPSULE (the ~8-token budget; drop lowest-priority on overflow)
# ---------------------------------------------------------------------------
def _enforce_token_cap(q: str) -> str:
    """Keep the first MAX_TOKENS words only (word-level priority by order)."""
    toks = [t for t in q.split() if t]
    return " ".join(toks[:MAX_TOKENS])


# ---------------------------------------------------------------------------
# SEARCH URL (the reused proven shape; epn_tag appends the campaign id)
# ---------------------------------------------------------------------------
SEARCH_BASE = "https://www.ebay.com/sch/i.html"


def build_targeted_links(lane: dict, epn_tag_fn) -> list[dict]:
    """2-3 link variants for the template. epn_tag_fn = band_pages.epn_tag
    (the shared MPA-gate tagging; campid read-in-place from .env inside it).
    Returns ordered dicts: {'href', 'tagged', 'label', 'sub', 'tokens',
    'full', 'raw'}.
    """
    raw_q = lane_query(lane)
    wider_q = _enforce_token_cap(wider_query(lane)) or raw_q
    widest_q = widest_query(lane) or wider_q

    def mk(q: str, label: str, sub: str, raw: str | None = None):
        view_url = SEARCH_BASE + "?_nkw=" + urllib.parse.quote_plus(q) + "&_sop=16"
        tag = epn_tag_fn(view_url, lane.get("slug", ""))
        return {
            "href": tag["href"], "tagged": tag["tagged"],
            "label": label, "sub": sub,
            "tokens": q,
            # full/raw = what the refine box composes against (rendered ONLY
            # into the JS data- attribute; never persisted anywhere)
            "full": q,
            "raw": raw,
        }

    out = [mk(raw_q, "Lane-exact search", _display(lane), raw_q)]
    if wider_q and wider_q != raw_q:
        out.append(mk(wider_q, "Wider: player + product", None))
    if widest_q and widest_q not in {raw_q, wider_q}:
        out.append(mk(widest_q, "Widest: player only", None))
    return out


def _display(lane: dict) -> str | None:
    """The lane-exact query itself is the sub-caption (nothing to hide)."""
    q = lane_query(lane)
    return q or None


# ---------------------------------------------------------------------------
# REFINE-BOX HELPERS (used by the renderer + its unit tests)
# ---------------------------------------------------------------------------
def refine_template_vars() -> dict:
    """Values the template needs to render the refine box (pure constants)."""
    return {"placeholder": "refine (e.g. 2022 chrome update pink wave)",
            "button_label": "Search refined"}


def refine_href(base_q: str, user_terms: str) -> str:
    """The URL the refine click composes in the BROWSER (client-side only:
    no fetch, no storage — this helper exists for the unit test of the
    composition + for the degrade path when JS is off, where the form does
    a plain GET to /bands/refined which 302s to the same URL)."""
    q = " ".join(t for t in ((base_q or "").strip(), (user_terms or "").strip()) if t)
    q = _enforce_token_cap(q)
    # cap after appending user terms too (combined <= cap; drop from the end)
    return SEARCH_BASE + "?_nkw=" + urllib.parse.quote_plus(q) + "&_sop=16"
