"""Fine-tune Laya-multilingual's decision head on the 8-way post-archetype question (CPU only).

Recipe (measured earlier on this laptop): freeze the encoder and run it once per post (cached on
disk per item), train only Laya's 2-layer decision head on the cached states, flush denormals
(8x faster on this CPU class), select the epoch on the synthetic VALIDATION split (unseen phrasings),
fit a temperature, and save in Laya's own layout so laya.load(<dir>) just works. The hand-written
test set is only ever scored, never used to pick anything.

    python train.py out/cringe_v1
"""
import argparse, hashlib, json, os, random, shutil, sys, time, warnings
warnings.filterwarnings("ignore")
import torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file, save_file
from transformers import AutoTokenizer
from laya.agent import _fix_tokenizer_config
from laya.common import QTYPES, build_model, build_sequence

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from schema import INSTRUCTION, LABEL_ORDER
from test_handwritten import TEST

K, CHOICE = len(LABEL_ORDER), QTYPES["choice"]
CRIT = {k: "" for k in LABEL_ORDER}
torch.set_flush_denormal(True)


def collate(items, pad_id):
    n, L = len(items), max(len(it["ids"]) for it in items)
    ids = torch.full((n, L), pad_id, dtype=torch.long); att = torch.zeros((n, L), dtype=torch.long)
    for i, it in enumerate(items):
        ids[i, : len(it["ids"])] = torch.tensor(it["ids"]); att[i, : len(it["ids"])] = 1
    return ids, att, torch.tensor([it["markers"] for it in items])


def head_forward(model, h, att, mpos):
    h = h + model.type_emb(torch.full((h.size(0),), CHOICE, dtype=torch.long))[:, None, :]
    pad = ~att.bool()
    for layer in model.head.layers:
        h = layer(h, src_key_padding_mask=pad)
    m = torch.gather(h, 1, mpos[:, :, None].expand(-1, -1, h.size(-1)))
    return model.scorer(m).squeeze(-1).float()


@torch.no_grad()
def encode(model, items, pad_id, cache_path, bs=16):
    cache = torch.load(cache_path) if os.path.exists(cache_path) else {}
    key = lambda it: hashlib.sha1(json.dumps(it["ids"]).encode()).hexdigest()
    seen, todo = set(), []
    for it in items:
        k = key(it)
        if k not in cache and k not in seen:
            seen.add(k); todo.append(it)
    print(f"encoder states: {len(items) - len(todo)} cached, {len(todo)} to encode", flush=True)
    model.eval(); t0 = time.time()
    order = sorted(range(len(todo)), key=lambda i: len(todo[i]["ids"]))
    for n, j in enumerate(range(0, len(order), bs)):
        chunk = [todo[i] for i in order[j:j + bs]]
        ids, att, _ = collate(chunk, pad_id)
        h = model.encoder(input_ids=ids, attention_mask=att).last_hidden_state
        for r, it in enumerate(chunk):
            cache[key(it)] = h[r, : len(it["ids"])].to(torch.float16).clone()
        if n % 25 == 0:
            print(f"  encoded {j + len(chunk)}/{len(todo)} ({time.time() - t0:.0f}s)", flush=True)
    if todo:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True); torch.save(cache, cache_path)
    for it in items:
        it["h"] = cache[key(it)]


def batch(items, pad_id):
    ids, att, mp = collate(items, pad_id)
    h = torch.zeros((len(items), ids.size(1), items[0]["h"].size(-1)))
    for i, it in enumerate(items):
        h[i, : it["h"].size(0)] = it["h"].float()
    return h, att, mp, torch.tensor([it["y"] for it in items])


@torch.no_grad()
def predict(model, items, pad_id):
    model.eval(); out = []
    for i in range(0, len(items), 32):
        h, att, mp, _ = batch(items[i:i + 32], pad_id)
        out.append(head_forward(model, h, att, mp))
    model.train(); model.encoder.eval()
    return torch.cat(out)


def macro_f1(pred, gold):
    f = []
    for c in range(K):
        tp = sum(p == c and g == c for p, g in zip(pred, gold)); pp = sum(p == c for p in pred); gg = sum(g == c for g in gold)
        if gg:
            pr, rc = (tp / pp if pp else 0), tp / gg
            f.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
    return sum(f) / len(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--epochs", type=int, default=12); ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--micro", type=int, default=16); ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--smooth", type=float, default=0.05); ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--synth", default="data/synth.jsonl")
    a = ap.parse_args()

    root = snapshot_download("convaiinnovations/laya"); mdir = os.path.join(root, "multilingual")
    _fix_tokenizer_config(mdir)
    cfg = json.load(open(os.path.join(mdir, "rl_agent_config.json")))
    tok = AutoTokenizer.from_pretrained(os.path.join(mdir, "tokenizer"))
    model = build_model(cfg, encoder_dir=os.path.join(mdir, "encoder"))
    model.load_state_dict(load_file(os.path.join(mdir, "model.safetensors")), strict=True)
    for p in model.encoder.parameters():
        p.requires_grad_(False)
    pad = tok.pad_token_id

    def mk(text, label):
        ids, mk_ = build_sequence(tok, text, {"t": "choice", "ins": INSTRUCTION, "crit": CRIT}, a.max_len, cfg.get("head_max_len", 192))
        assert len(mk_) == K
        return {"ids": ids, "markers": mk_, "y": LABEL_ORDER.index(label)}

    syn = [json.loads(l) for l in open(a.synth, encoding="utf-8")]
    train = [mk(r["text"], r["label"]) for r in syn if r["split"] == "train"]
    val = [mk(r["text"], r["label"]) for r in syn if r["split"] == "val"]
    test = [mk(t, l) for t, l in TEST]
    print(f"train {len(train)} | val {len(val)} (unseen phrasings) | hand-written test {len(test)}", flush=True)
    encode(model, train + val + test, pad, os.path.join(HERE, "out", "enc_cache.pt"))

    head = [p for n, p in model.named_parameters() if not n.startswith("encoder.")]
    opt = torch.optim.AdamW(head, lr=a.lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=(len(train) // a.micro + 1) * a.epochs, eta_min=1e-6)
    model.train(); model.encoder.eval()
    best, best_ep, best_state, t0 = -1, 0, None, time.time()
    acc = lambda p, y: sum(u == v for u, v in zip(p, y)) / len(y)
    for ep in range(a.epochs):
        random.Random(ep).shuffle(train); tot, nb = 0.0, 0
        for i in range(0, len(train), a.micro):
            h, att, mp, y = batch(train[i:i + a.micro], pad)
            lg = head_forward(model, h, att, mp)
            tgt = torch.full_like(lg, a.smooth / (K - 1)); tgt[torch.arange(len(y)), y] = 1 - a.smooth
            loss = -(tgt * torch.log_softmax(lg, -1)).sum(-1).mean()
            opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(head, 1.0); opt.step(); sched.step()
            tot += loss.item(); nb += 1
        pv, pt = (predict(model, x, pad).argmax(-1).tolist() for x in (val, test))
        yv, yt = [it["y"] for it in val], [it["y"] for it in test]
        f1v = macro_f1(pv, yv)
        print(f"=== epoch {ep + 1}/{a.epochs} loss {tot / nb:.4f} | val acc {acc(pv, yv):.3f} F1 {f1v:.3f} | hand-written test acc {acc(pt, yt):.3f} ({time.time() - t0:.0f}s)", flush=True)
        if f1v > best:
            best, best_ep = f1v, ep + 1
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items() if not k.startswith("encoder.")}
        elif ep + 1 - best_ep >= a.patience:
            print(f"early stop: best epoch {best_ep} (val F1 {best:.3f})", flush=True); break
        if os.path.exists(os.path.join(HERE, "STOP")):     # user asked to stop: keep the best epoch so far and save
            print(f"STOP file found: stopping after epoch {ep + 1}; best epoch {best_ep} (val F1 {best:.3f})", flush=True)
            os.remove(os.path.join(HERE, "STOP")); break
    model.load_state_dict(best_state, strict=False); print(f"restored epoch {best_ep}", flush=True)

    Z = predict(model, val, pad); T = torch.zeros((len(val), K))
    for i, it in enumerate(val): T[i, it["y"]] = 1.0
    log_t = torch.zeros(1, requires_grad=True); lb = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100)
    def closure():
        lb.zero_grad(); l = -(T * torch.log_softmax(Z / log_t.exp(), -1)).sum(-1).mean(); l.backward(); return l
    lb.step(closure); temp = float(torch.clamp(log_t.exp(), 0.1, 10.0)); print(f"temperature (choice): {temp:.3f}", flush=True)

    os.makedirs(a.out, exist_ok=True)
    save_file({k: v.contiguous().cpu() for k, v in model.state_dict().items()}, os.path.join(a.out, "model.safetensors"))
    model.encoder.config.save_pretrained(os.path.join(a.out, "encoder"))
    shutil.copytree(os.path.join(mdir, "tokenizer"), os.path.join(a.out, "tokenizer"), dirs_exist_ok=True)
    temps = list(cfg.get("temperature", [1.0, 1.0, 1.0])); temps[CHOICE] = temp
    cfg.update({"fine_tuned": True, "model_name": "cringe-meter", "temperature": temps, "max_len": a.max_len}); cfg.pop("temperature_by_options", None); cfg.pop("lang_temperatures", None)
    json.dump(cfg, open(os.path.join(a.out, "rl_agent_config.json"), "w"), indent=2)
    print("saved ->", a.out, flush=True)


if __name__ == "__main__":
    main()
