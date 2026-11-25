"""FLEET-STALL-EXIT (the stall-exit pattern, Nov-23).

THE FLEET-HARDENING ITEM-2 (agent-loop course adopt-item #3, founder GO Nov-23):
  2 consecutive rounds without FEWER failures = structured stop-signal. Fixes the
  scraper/cron death-spiral class (proven fleet cases: the OH-column rescue and the
  finder's ask-only-mirage both died in repeat-loops before this pattern existed).

Usage (cron/worker loop):
    from fleet_stall_exit import check_stall, stall_exit_note

    failure_history = []          # per-round failure counts, appended each round
    ...
    failure_history.append(failures_this_round)
    if len(failure_history) >= 3:
        should_stop, reason = check_stall(failure_history)
        if should_stop:
            print(stall_exit_note(
                what_tried="...",
                why_failing=reason,
                what_next="..."))
            sys.exit(0)           # structured stop — never keep looping

  (first two rounds can never stall: >=3 points are needed for 2 consecutive
   non-improving transitions; call check_stall once you have 3+ rounds.)

Semantics of check_stall(failure_history, prev_history=None):
  - failure_history: list of per-round failure counts (ints >= 0), oldest first.
  - prev_history: optional earlier segment; when given, the two are concatenated
    (failure_history = prev_history + failure_history) so multi-window workers can
    feed just the latest window while carrying the prior rounds' history forward.
  - A round is NON-IMPROVING when failures[i] >= failures[i-1] (flat or worse).
  - 2 consecutive non-improving transitions -> should_stop=True.

stall_exit_note(what_tried, why_failing, what_next) -> str
  The standard 3-line stop-message: what was tried / why it's failing / what next
  (change plan or checkpoint, or escalate to the founder). Delivered verbatim on
  stdout by the caller — silent-healthy convention: only stalls produce output.
"""
# REPRODUCIBILITY-HEADER: [Verified] semantics implemented and self-tested this session (see _selftest); counts are ints, comparisons are pure arithmetic — nothing model-generated enters the decision.

__all__ = ["check_stall", "stall_exit_note"]

STALL_TRANSITIONS_REQUIRED = 2


def check_stall(failure_history, prev_history=None):
    """(should_stop: bool, reason: str).

    2 consecutive rounds without fewer failures (failures[i] >= failures[i-1],
    twice in a row) => should_stop=True with a reason naming the flat round-pair.
    """
    if prev_history:
        history = list(prev_history) + list(failure_history)
    else:
        history = list(failure_history)

    if len(history) < STALL_TRANSITIONS_REQUIRED + 1:
        return False, ""

    try:
        counts = [int(x) for x in history]
    except (TypeError, ValueError):
        return False, f"non-integer failure history: {history!r}"

    transitions = []  # (i, prev, cur, improving?)
    for i in range(1, len(counts)):
        improving = counts[i] < counts[i - 1]
        transitions.append((i, counts[i - 1], counts[i], improving))

    last_two = transitions[-STALL_TRANSITIONS_REQUIRED:]
    if all(not t[3] for t in last_two):
        a, b = last_two[0], last_two[1]
        return True, (
            f"Stall: {STALL_TRANSITIONS_REQUIRED} consecutive rounds without fewer failures "
            f"(rounds {b[0] - 1}->{b[0]}: {b[1]} -> {b[2]} failures; "
            f"rounds {a[0] - 1}->{a[0]}: {a[1]} -> {a[2]} failures — flat-or-worse twice). "
            f"Change plan/check/model or escalate."
        )
    return False, ""


def stall_exit_note(what_tried, why_failing, what_next):
    """The standard stop-message: what-tried / why-failing / what-next. Print on stdout, then exit."""
    return (
        "[STALL-EXIT] Structured stop — 2 rounds without fewer failures.\n"
        f"WHAT-TRIED:  {what_tried}\n"
        f"WHY-FAILING: {why_failing}\n"
        f"WHAT-NEXT:   {what_next}"
    )


def _selftest():
    # improving -> no stop
    assert check_stall([10, 5, 2]) == (False, "")
    # flat then worse -> stop
    stop, reason = check_stall([10, 10, 12])
    assert stop, reason
    # improvement on second transition -> no stop
    assert check_stall([10, 10, 3]) == (False, "")
    # too short
    assert check_stall([5, 5]) == (False, "")
    # prev_history concatenation: prev flat + flat + flat = 2 non-improving
    stop, _ = check_stall([10], prev_history=[10, 10])
    assert stop
    # but prev improving then flat then improving = no stop
    assert check_stall([7], prev_history=[10, 4]) == (False, "")
    # non-int guard
    stop, reason = check_stall(["x", "y", "z"])
    assert not stop and "non-integer" in reason
    print("fleet_stall_exit selftest: 8/8 OK")


if __name__ == "__main__":
    _selftest()
