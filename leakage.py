"""How much of a test set can be found, nearly word for word, inside the training templates?

    python leakage.py            # A, B and C
For each test post it finds the training template piece (hook / middle / closer, slots removed) whose
words are most contained in the post. A piece of >= 5 words with containment >= 0.8 counts as 'leaked'.
A post with a leaked piece is not a fair test of generalisation.
"""
import re
import gen_synthetic as g
from synth_extra import EXTRA
from test_handwritten import TEST as A
from test_blind import TEST_B as B
try:
    from test_fresh import TEST_C as C
except ImportError:
    C = []

W = lambda s: [w for w in re.findall(r"[a-z0-9']+", re.sub(r"\{[a-z0-9]+\}", " ", s.lower()))]
pieces = []
for pools in (g.P, {k: v for k, v in EXTRA.items()}):
    for cls, trip in pools.items():
        for part in trip:
            for p in part:
                w = W(p)
                if len(w) >= 5: pieces.append((cls, set(w), p))


def leaked(text):
    tw = set(W(text)); best = (0, None)
    for cls, pw, p in pieces:
        c = len(pw & tw) / len(pw)
        if c > best[0]: best = (c, p)
    return best


for name, data in (("A", A), ("B", B), ("C", C)):
    if not data: continue
    hits = [(t, leaked(t)) for t, _ in data]
    n = sum(1 for _, (c, _) in hits if c >= 0.8)
    print(f"Test {name}: {n}/{len(data)} posts contain a training template almost verbatim ({n / len(data):.0%})")
    if name == "B":
        for t, (c, p) in hits[:0]: pass
