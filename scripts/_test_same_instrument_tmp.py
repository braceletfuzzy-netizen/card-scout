"""Check _same_instrument end-to-end with a fake session (no DB writes)."""
import sys
sys.path.insert(0, 'scripts')
from customer_onboarding_v2 import _same_instrument


class FakeCard:
    def __init__(self, q):
        self.search_query = q


class _R:
    def __init__(self, cards):
        self._cards = cards

    def all(self):
        return self._cards


class _Q:
    def __init__(self, cards):
        self._cards = cards

    def filter(self, *a, **k):
        return _R(self._cards)


class FakeSession:
    def __init__(self, cards):
        self._cards = cards

    def query(self, *a, **k):
        return _Q(self._cards)


alan_cards = [FakeCard("2018 Topps Upton, Ohtani & Trout US158 Parallel"),
              FakeCard("Mookie Betts Raw 10 Topps US26"),
              FakeCard("Portgas D. Ace Graded 10 One Piece OP13-119"),
              FakeCard("Imported 2026-09-17 18:06 Ken Griffey Jr. 1989 1 Autograph")]

cases = [
    ("Imported 2026-09-17 18:08 Upton, Ohtani & Trout 2018 US158 Parallel", True),
    ("One Piece Potgas D. Ace Wanted 2022-2026 OP13-119 Error", True),
    ("Topps 5 Star Bobby Witt Jr 2023 FSA-BW Autograph", False),
    ("Imported 2026-09-17 18:06 Ken Griffey Jr. 1989 1 Autograph", True),
]
ok = True
for q, expected in cases:
    got = _same_instrument(FakeSession(alan_cards), 3, q)
    status = 'OK' if got == expected else 'FAIL'
    if got != expected:
        ok = False
    print(f"{status}: same_instrument={got} expected={expected} | {q}")

# Empty customer: never matches
print("empty-customer ->", _same_instrument(FakeSession([]), 3, "Topps 5 Star Bobby Witt Jr 2023 FSA-BW Autograph"))
sys.exit(0 if ok else 1)