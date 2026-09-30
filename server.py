"""Cringe Meter server: scores drafts with the fine-tuned Laya model and serves the demo page.

    python server.py                  # http://127.0.0.1:8780/   (uses out/cringe_v2)
    python server.py --model out/x --port 8781

    GET  /                    the "Cringe Lab" page (web/lab.html)
    GET  /health              {ok, model}
    POST /score {text}        -> {probs:{8 labels}, top, ms}
    POST /hot   {text}        -> {sentence, heat}   the single hottest sentence, for "delete this first"

Text never leaves the machine. Only the extension (chrome-extension://...) and this page's own origin may
call it from a browser. Nothing here touches LinkedIn or X.
"""
import argparse, json, os, re, sys, time, warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
warnings.filterwarnings("ignore")
import torch
import laya

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from schema import LABEL_ORDER, QUESTIONS

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=8780)
ap.add_argument("--model", default=os.path.join(HERE, "out", "cringe_v2"))
args = ap.parse_args()
torch.set_flush_denormal(True)   # 8x on this CPU class (measured earlier)
agent = laya.load(args.model, device="cpu")
lock = Lock()
MAX_CHARS = 1200        # the model was trained on the opening of a post (192 tokens); the hook matters most
WEB = os.path.join(HERE, "web")
SENT = re.compile(r"(?<=[.!?…])\s+|\n+")


last_used = [time.time()]


def score(texts):
    with lock:
        res = agent.predict_batch(texts, QUESTIONS, batch_size=8, sort_by_length=False)
    last_used[0] = time.time()
    return [r["answers"]["kind"]["probabilities"] for r in res]


def keep_warm(idle_s=25, every_s=15):
    """On a memory-starved machine Windows pages an idle model out to disk, and the next keystroke then waits 10+ s
    for it to come back. A tiny prediction whenever the server has been idle keeps the weights resident."""
    while True:
        time.sleep(every_s)
        if time.time() - last_used[0] > idle_s:
            try:
                score(["Keep-warm ping so the model stays in memory. It says very little on purpose."])
            except Exception:
                pass


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _origin(self):
        o = self.headers.get("Origin")
        own = f"http://127.0.0.1:{args.port}"
        return o if (o is None or o == own or o.startswith("chrome-extension://")) else False

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        o = self._origin()
        if o: self.send_header("Access-Control-Allow-Origin", o)
        self.end_headers(); self.wfile.write(b)

    def do_OPTIONS(self):
        o = self._origin(); self.send_response(204 if o else 403)
        if o:
            for k, v in (("Access-Control-Allow-Origin", o), ("Access-Control-Allow-Methods", "GET, POST"),
                         ("Access-Control-Allow-Headers", "Content-Type"), ("Access-Control-Allow-Private-Network", "true")):
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "model": os.path.relpath(args.model, HERE)})
        clean = self.path.split("?")[0]
        if clean.startswith("/ext/"):          # the extension's own files, so the stand-in page can load them unchanged
            f = os.path.join(HERE, "extension", os.path.basename(clean))
        else:
            f = os.path.join(WEB, "lab.html" if clean in ("/", "/index.html") else os.path.basename(clean))
        if os.path.isfile(f):
            ct = {".html": "text/html; charset=utf-8", ".js": "application/javascript", ".css": "text/css"}.get(os.path.splitext(f)[1], "application/octet-stream")
            return self._send(200, open(f, "rb").read(), ct)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self._origin() is False: return self._send(403, {"error": "origin not allowed"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            text = str(json.loads(self.rfile.read(min(n, 1 << 20)) or b"{}").get("text") or "")[:MAX_CHARS].strip()
        except ValueError:
            return self._send(400, {"error": "bad json"})
        if self.path == "/score":
            if len(text.split()) < 3: return self._send(200, {"probs": None, "top": None, "ms": 0})
            t0 = time.time(); p = score([text])[0]
            return self._send(200, {"probs": p, "top": max(p, key=p.get), "ms": round((time.time() - t0) * 1000)})
        if self.path == "/hot":
            sents = [s.strip() for s in SENT.split(text) if len(s.split()) >= 3][:8]
            if len(sents) < 2: return self._send(200, {"sentence": None, "heat": 0})
            t0 = time.time(); ps = score(sents)
            heats = [1 - p["genuine"] for p in ps]; i = max(range(len(sents)), key=heats.__getitem__)
            return self._send(200, {"sentence": sents[i], "heat": heats[i], "ms": round((time.time() - t0) * 1000)})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    # The first request after loading costs 10+ s (lazy init). Pay it now, before anyone is waiting on a keystroke.
    t0 = time.time()
    for _ in range(2):
        score(["Warm-up post so the first real request is fast. It says very little on purpose."])
    print(f"model warmed up in {time.time() - t0:.1f}s", flush=True)
    import threading
    threading.Thread(target=keep_warm, daemon=True).start()
    print(f"Cringe Meter on http://127.0.0.1:{args.port}/   model: {args.model}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), H).serve_forever()
