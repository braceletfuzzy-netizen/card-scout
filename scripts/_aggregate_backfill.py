"""
_aggregate_backfill.py — one-shot backfill runner for the AGGREGATE-TAG FALLBACK
(brief: Temp/hermes_brief_aggregate_tag.md; plan: cardscout-2.0/.hermes/plans/
2026-11-12-aggregate-tag-fallback-spec.md).

Pulls the 757-lane roster from dashboard/registry/card_page_registry.json,
dedups player names, and runs lane-level Card Hedge lookups for lanes that
have NO own-corpus band values (488 forming lanes) — building the
`player|set|variant`-keyed jsonl cache that /bands falls back to.

Rate-budget (bounds): ≤8 req/min enforced inside aggregate_lanes (7.5s spacing
between calls); this runner additionally caps each run at --max-lanes (default
20, the nightly batch). Idempotent + resumable: cached rows are skipped, so
re-runs only pay for missing lanes. All activity logged to
aggregate_backfill.log.

Run nightly (cron/Render cron or manual):
    python scripts/_aggregate_backfill.py            # ≤20 lanes this batch
    python scripts/_aggregate_backfill.py --max-lanes 40 --only-player "Jeremy Pena"
NEVER pushes, never deploys: cache lands in card-scout/data/aggregate_lanes/.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import logging
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from aggregate_lanes import (  # noqa: E402
    AGG_LOG, _load_client, cache_read, get_aggregate_lane,
    cache_write,
)

REGISTRY = REPO / "dashboard" / "registry" / "card_page_registry.json"


def setup_logger() -> logging.Logger:
    lg = logging.getLogger("aggregate_backfill")
    lg.setLevel(logging.INFO)
    lg.propagate = False
    if not lg.handlers:
        AGG_LOG.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(AGG_LOG, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        lg.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(message)s"))
        lg.addHandler(sh)
    return lg


def build_roster() -> list[dict]:
    """The 757-lane roster -> lanes needing aggregate (no own band values)."""
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    need = []
    for lane in data.get("lanes", []):
        if lane.get("band"):          # has CORPUS values -> never overwrites
            continue
        need.append({
            "player": lane["player"],
            "lane": lane["lane"],
            "grade_bucket": lane.get("grade_bucket", "raw"),
            "product": lane.get("product") or None,
            "slug": lane.get("slug", ""),
        })
    # dedup players for reporting; lanes processed individually (one search per
    # unique player+lane+grade key inside get_aggregate_lane)
    players = sorted({l["player"] for l in need})
    return need, players


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-lanes", type=int, default=20)
    ap.add_argument("--only-player", default=None)
    ap.add_argument("--only-slug", default=None)
    args = ap.parse_args()
    lg = setup_logger()

    client = _load_client()
    if not client:
        lg.error("Card Hedge client unavailable (key/read path missing) — aborting.")
        return 2

    need, players = build_roster()
    lg.info("roster: %d aggregate-needing lanes across %d players (757-lane registry)",
            len(need), len(players))
    if args.only_player:
        need = [l for l in need if l["player"].lower() == args.only_player.lower()]
        lg.info("player filter %r -> %d lanes", args.only_player, len(need))
    if args.only_slug:
        need = [l for l in need if l["slug"] == args.only_slug]
        lg.info("slug filter %r -> %d lanes", args.only_slug, len(need))

    built = missed = skipped = 0
    for lane in need[: args.max_lanes]:
        from aggregate_lanes import _grade_bucket_to_ch
        grade = _grade_bucket_to_ch(lane["grade_bucket"])
        if cache_read(lane["player"], lane["lane"], grade):
            skipped += 1
            continue
        res = get_aggregate_lane(
            lane["player"], lane["lane"], lane["grade_bucket"], lane["product"])
        if res and res.get("band"):
            built += 1
            b = res["band"]
            lg.info("OK  %s -> $%.2f–$%.2f mid $%.2f AGGREGATE·%s (asks=%d 30d=%d)",
                    res.get("lane", lane["lane"]), b["low"], b["high"], b["mid"],
                    b.get("confidence_grade") or "-", b.get("n_ch_asks", 0),
                    b.get("sales_30d", 0))
        else:
            missed += 1
            lg.warning("MISS %s (%s | lane=%s grade=%s)", lane["slug"],
                       lane["player"], lane["lane"], lane["grade_bucket"])
            cache_write(lane["player"], lane["lane"], grade,
                        {"band": None, "miss": True, "player": lane["player"],
                         "lane": lane["lane"], "grade": grade})
    lg.info("batch done: built=%d miss=%d cached-skip=%d (of %d in batch)",
            built, missed, skipped, min(len(need), args.max_lanes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
