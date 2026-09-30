"""Score checkpoints on the two hand-written test sets and time them.

    python evaluate.py base                       # zero-shot laya-multilingual (near chance)
    python evaluate.py out/cringe_v1 out/cringe_v2

  Test A (80): written before v1. It informed v2's templates (16% of its posts appear near-verbatim in them).
  Test B (64): meant to be blind, but v2's templates were then written from it: 80% overlap. NOT a valid test.
  Test C (64): written after v2 was trained and checked with leakage.py (3% overlap): the honest number.
All were written by the author of the generator, so all are only partly independent of it.
Reported per set: accuracy over 8 classes, per-class recall, and the 'cringe score' (1 - P(genuine)) AUC of
genuine vs cringe, which is what the thermometer actually shows. Also the genuine false-alarm rate: the share of
genuine posts the meter would call more than 50% cringe (the annoying failure).
"""
import collections, sys, time, warnings
warnings.filterwarnings("ignore")
import torch; torch.set_flush_denormal(True)
import laya
from schema import LABEL_ORDER, QUESTIONS
from test_handwritten import TEST as A
from test_blind import TEST_B as B
from test_fresh import TEST_C as C

SETS = {"A (80; 16% overlap with v2 templates)": A, "B (64; LEAKED: 80% overlap, do not trust)": B, "C (64; fresh, 3% overlap: the honest one)": C}


def auc(pos, neg):
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def main():
    models = sys.argv[1:] or ["out/cringe_v2"]
    show_errors = "--errors" in models
    models = [m for m in models if m != "--errors"]
    for path in models:
        agent = laya.load("convaiinnovations/laya", subfolder="multilingual", device="cpu") if path == "base" else laya.load(path, device="cpu")
        agent.predict("warmup", QUESTIONS)
        print(f"\n################ {path}")
        for name, data in SETS.items():
            texts, gold = [t for t, _ in data], [g for _, g in data]
            t0 = time.time(); res = agent.predict_batch(texts, QUESTIONS, batch_size=16, sort_by_length=True); ms = (time.time() - t0) / len(texts) * 1000
            prob = [r["answers"]["kind"]["probabilities"] for r in res]; pred = [max(p, key=p.get) for p in prob]
            acc = sum(p == g for p, g in zip(pred, gold)) / len(gold)
            cr = [1 - p["genuine"] for p in prob]
            pos = [c for c, g in zip(cr, gold) if g != "genuine"]; neg = [c for c, g in zip(cr, gold) if g == "genuine"]
            fa = sum(c > 0.5 for c in neg) / len(neg)
            print(f"\n== Test {name}: accuracy {acc:.3f} (chance {1 / len(LABEL_ORDER):.3f})   cringe-score AUC {auc(pos, neg):.3f}   "
                  f"genuine called >50% cringe: {fa:.0%}   ({ms:.0f} ms/post batched)")
            print("   recall: " + "  ".join(f"{c}={sum(p == c and g == c for p, g in zip(pred, gold))}/{gold.count(c)}" for c in LABEL_ORDER))
            print("   confusions:", dict(collections.Counter((g, p) for g, p in zip(gold, pred) if g != p).most_common(6)))
            if show_errors:
                for t, g, p, pr in zip(texts, gold, pred, prob):
                    if g != p: print(f"     gold={g:15s} pred={p:15s} {pr[p]:.2f} | {t[:80]!r}")


if __name__ == "__main__":
    main()
