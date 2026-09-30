/* CringeMeter: a glass thermometer for how cringe a draft is. One file, no dependencies, works in the
 * demo page and (inside a shadow root) in the Chrome extension.
 *
 *   const m = new CringeMeter(hostElement, { compact: false });
 *   m.setScores({ genuine: .1, humblebrag: .7, ... }, 231);   // probabilities from Laya; heat = 1 - P(genuine)
 *   m.setHot("I'm humbled to announce...");                    // the sentence to delete first
 *   m.setIdle();  m.setBusy(true);  m.destroy();
 *
 * What it does with the heat value (0 = genuine, 1 = maximum cringe):
 *   0-.12  frost and snowflakes.   .12-.4 green-yellow, calm bubbles.   .4-.65 orange, sweat.
 *   .55+   the thermometer starts to shake.   .72+ smoke.   .9+ glass cracks, red flashing, "CRITICAL".
 *   Cooling is deliberately slower than heating, so cutting the cringe feels like it cools down.
 * The dominant archetype also rains its own emoji. Honours prefers-reduced-motion (colour + text only).
 */
(function (root) {
  "use strict";

  const LABELS = ["genuine", "humblebrag", "fake_parable", "engagement_bait", "hustle_guru", "buzzword_salad", "shameless_plug", "ai_thread_bro"];
  const META = {
    genuine: { name: "Genuine", emoji: "🧊" }, humblebrag: { name: "Humblebrag", emoji: "🙏" },
    fake_parable: { name: "Fake parable", emoji: "🧓" }, engagement_bait: { name: "Engagement bait", emoji: "👇" },
    hustle_guru: { name: "Hustle guru", emoji: "⏰" }, buzzword_salad: { name: "Buzzword salad", emoji: "🧩" },
    shameless_plug: { name: "Shameless plug", emoji: "💸" }, ai_thread_bro: { name: "AI thread bro", emoji: "🧵" },
  };
  // Laya cannot write text, so the meter's voice is canned lines picked by code (mirrors schema.py VERDICTS).
  const VERDICTS = {
    genuine: ["Suspiciously useful.", "Specific, honest, no fog machine. Post it.", "Alarmingly normal. Ship it."],
    humblebrag: ["You are 'humbled'. You are not humbled.", "Brag detected wearing a gratitude costume.", "Nobody is fooled by 'honoured'."],
    fake_parable: ["No janitor ever said that.", "This story has a moral and no witnesses.", "Ah, the wise Uber driver returns."],
    engagement_bait: ["You are asking for likes with a straight face.", "'Agree?' is not an idea.", "The algorithm is thrilled. Humans are not."],
    hustle_guru: ["Somewhere a 5AM alarm just screamed.", "Discipline speech: 100% delivered, 0% specifics.", "Nobody is coming to save you, but also this is a lot."],
    buzzword_salad: ["Synergy levels critical.", "Fluent in corporate, empty in meaning.", "You leveraged a paradigm. What did it do?"],
    shameless_plug: ["Ah, a commercial break.", "'Link in bio' energy.", "It's an ad. Own it."],
    ai_thread_bro: ["Thread bro alert: 'you're using AI wrong'.", "Save this post (you will not).", "Ten tools that will change your life by Tuesday."],
  };
  const IDLE = "Start typing. I'll judge after two sentences.";

  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const rand = (a, b) => a + Math.random() * (b - a);
  // green -> yellow -> orange -> red, as an hsl hue
  const hueAt = (h) => (h < 0.4 ? 145 - (145 - 52) * (h / 0.4) : h < 0.7 ? 52 - (52 - 28) * ((h - 0.4) / 0.3) : 28 - 26 * ((h - 0.7) / 0.3));
  const colourAt = (h, l = 52) => `hsl(${hueAt(clamp(h, 0, 1)).toFixed(0)} 82% ${l}%)`;

  const CSS = `
  :host { all: initial; }
  .card { position: relative; box-sizing: border-box; width: var(--w, 380px); padding: 16px; border-radius: 18px; overflow: hidden;
    background: radial-gradient(120% 90% at 20% 0%, #1d2330 0%, #12151c 60%); color: #e8ecf3; font: 500 13px/1.35 -apple-system, "Segoe UI", Roboto, sans-serif;
    border: 1px solid rgba(255,255,255,.10); box-shadow: 0 0 var(--glow, 20px) var(--glowc, rgba(60,220,140,.25)), 0 10px 30px rgba(0,0,0,.35); }
  .card.compact { --w: 300px; padding: 12px; font-size: 12px; }
  .row { display: grid; grid-template-columns: 112px 1fr; gap: 14px; align-items: stretch; position: relative; z-index: 1; padding-top: 34px; }
  .compact .row { grid-template-columns: 92px 1fr; gap: 10px; padding-top: 28px; }
  .thermo { width: 100%; height: auto; overflow: visible; will-change: transform; }
  canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }
  .vignette { position: absolute; inset: 0; pointer-events: none; z-index: 3; opacity: 0; background: radial-gradient(circle at 50% 40%, transparent 35%, rgba(255,40,30,.55) 100%); }
  .card.critical { animation: throb .5s ease-in-out infinite alternate; }
  .card.critical .vignette { opacity: 1; animation: flash .45s steps(2) infinite; }
  @keyframes throb { from { border-color: rgba(255,80,60,.35); } to { border-color: rgba(255,80,60,1); } }
  @keyframes flash { from { opacity: .25; } to { opacity: .9; } }
  .score { font: 800 40px/1 -apple-system, "Segoe UI", Roboto, sans-serif; letter-spacing: -1px; }
  .compact .score { font-size: 30px; }
  .score small { font-size: 16px; font-weight: 700; opacity: .7; margin-left: 2px; }
  .tag { display: inline-block; margin-top: 4px; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; background: rgba(255,255,255,.08); }
  .verdict { margin: 8px 0 8px; min-height: 2.7em; font-size: 14px; font-weight: 700; }
  .compact .verdict { font-size: 13px; min-height: 2.6em; }
  .bars { display: grid; gap: 4px; }
  .bar { display: grid; grid-template-columns: 88px 1fr 30px; gap: 6px; align-items: center; font-size: 11px; opacity: .78; }
  .compact .bar { grid-template-columns: 78px 1fr 28px; font-size: 10.5px; }
  .bar.top { opacity: 1; font-weight: 700; }
  .track { height: 6px; border-radius: 4px; background: rgba(255,255,255,.08); overflow: hidden; }
  .fill { height: 100%; width: 0; border-radius: 4px; background: #7dd3fc; transition: width .25s ease-out; }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .hot { margin-top: 10px; padding: 8px 10px; border-radius: 10px; background: rgba(255,120,60,.10); border: 1px solid rgba(255,120,60,.25); font-size: 12px; display: none; position: relative; z-index: 1; }
  .hot b { display: block; font-size: 10px; letter-spacing: .06em; text-transform: uppercase; opacity: .7; margin-bottom: 2px; }
  .hot span { display: block; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
  .foot { margin-top: 10px; display: flex; justify-content: space-between; font-size: 10.5px; opacity: .6; position: relative; z-index: 1; }
  .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #34d399; margin-right: 6px; vertical-align: 1px; }
  .dot.busy { background: #fbbf24; animation: pulse .6s ease-in-out infinite alternate; }
  @keyframes pulse { from { opacity: .3; } to { opacity: 1; } }
  .banner { display: none; margin-top: 6px; font-weight: 900; letter-spacing: .12em; color: #ff5a4a; font-size: 12px; }
  .card.critical .banner { display: block; animation: flash .3s steps(2) infinite; }
  @media (prefers-reduced-motion: reduce) { .card.critical, .card.critical .vignette, .card.critical .banner, .dot.busy { animation: none; } }
  `;

  const SVG = `
  <svg class="thermo" viewBox="0 0 120 340" aria-hidden="true">
    <defs>
      <clipPath id="tube"><rect x="42" y="20" width="36" height="240" rx="18"/><circle cx="60" cy="286" r="42"/></clipPath>
      <linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset=".25" stop-color="#fff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
    </defs>
    <g class="glass">
      <rect x="42" y="20" width="36" height="240" rx="18" fill="rgba(255,255,255,.05)" stroke="rgba(255,255,255,.35)" stroke-width="2.5"/>
      <circle cx="60" cy="286" r="42" fill="rgba(255,255,255,.05)" stroke="rgba(255,255,255,.35)" stroke-width="2.5"/>
    </g>
    <g clip-path="url(#tube)"><path class="liquid" d="" fill="#3ddc84"/><rect x="42" y="20" width="36" height="320" fill="url(#shine)"/></g>
    <g class="ticks" font-size="9" fill="rgba(255,255,255,.55)" font-weight="700">
      <line x1="80" x2="88" y1="207" y2="207" stroke="rgba(255,255,255,.4)"/><text x="92" y="210">mild</text>
      <line x1="80" x2="88" y1="152" y2="152" stroke="rgba(255,255,255,.4)"/><text x="92" y="155">cringe</text>
      <line x1="80" x2="88" y1="97" y2="97" stroke="rgba(255,255,255,.4)"/><text x="92" y="100">hot</text>
      <line x1="80" x2="88" y1="42" y2="42" stroke="rgba(255,255,255,.4)"/><text x="92" y="45">CRIT</text>
    </g>
    <g class="cracks" stroke="#fff" stroke-width="1.6" fill="none" opacity="0" stroke-linecap="round" stroke-linejoin="round">
      <path d="M62 24 L56 52 L66 74 L55 100 L64 122"/><path d="M56 52 L46 60"/><path d="M66 74 L76 84"/><path d="M55 100 L44 112"/>
      <path d="M50 270 L60 292 L72 276"/><path d="M60 292 L58 314"/>
    </g>
    <g class="face" data-mood="cool" stroke-linecap="round">
      <g class="eyes"><circle cx="46" cy="280" r="6.5" fill="#fff"/><circle cx="74" cy="280" r="6.5" fill="#fff"/>
        <circle class="pupil" cx="46" cy="281" r="3" fill="#1b1f2a"/><circle class="pupil" cx="74" cy="281" r="3" fill="#1b1f2a"/></g>
      <g class="closed" stroke="#1b1f2a" stroke-width="2.6" fill="none"><path d="M40 281 Q46 275 52 281"/><path d="M68 281 Q74 275 80 281"/></g>
      <g class="brows" stroke="#1b1f2a" stroke-width="2.6" fill="none"><path d="M39 271 L52 267"/><path d="M81 271 L68 267"/></g>
      <path class="mouth" d="M48 302 Q60 310 72 302" stroke="#1b1f2a" stroke-width="3" fill="none"/>
    </g>
  </svg>`;

  class CringeMeter {
    constructor(host, opts) {
      this.opts = opts || {};
      this.reduced = !!(root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches);
      this.root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
      this.root.innerHTML = `<style>${CSS}</style>
        <div class="card ${this.opts.compact ? "compact" : ""}">
          <div class="row">
            <div class="thermoWrap">${SVG}</div>
            <div class="info">
              <div class="score"><span class="pct">0</span><small>% cringe</small></div>
              <span class="tag">idle</span>
              <div class="banner">⚠ CRINGE CRITICAL</div>
              <div class="verdict"></div>
              <div class="bars"></div>
            </div>
          </div>
          <div class="hot"><b>Hottest line. Delete this first</b><span></span></div>
          <div class="foot"><span><i class="dot"></i><span class="status">local · Laya</span></span><span class="ms"></span></div>
          <canvas></canvas><div class="vignette"></div>
        </div>`;
      const $ = (s) => this.root.querySelector(s);
      this.el = { card: $(".card"), thermo: $(".thermo"), liquid: $(".liquid"), cracks: $(".cracks"), face: $(".face"), pct: $(".pct"), tag: $(".tag"),
        verdict: $(".verdict"), bars: $(".bars"), hot: $(".hot"), hotText: $(".hot span"), ms: $(".ms"), dot: $(".dot"), status: $(".status"), canvas: $("canvas") };
      this.ctx = this.el.canvas.getContext("2d");
      this.el.bars.innerHTML = LABELS.map((l) => `<div class="bar" data-l="${l}"><span>${META[l].emoji} ${META[l].name}</span><div class="track"><div class="fill"></div></div><span class="num">0</span></div>`).join("");
      this.barEls = Object.fromEntries(LABELS.map((l) => [l, this.root.querySelector(`.bar[data-l="${l}"]`)]));

      this.h = 0; this.v = 0; this.target = 0; this.probs = null; this.topLabel = null; this.parts = [];
      this.verdictFull = IDLE; this.verdictShown = 0; this.lastType = 0; this.phase = 0; this.t0 = 0; this.last = 0; this.emitAcc = {};
      this.busy = false; this.dead = false; this.size = { w: 0, h: 0 }; this.svgRect = null;
      this.el.verdict.textContent = "";
      this._ro = root.ResizeObserver ? new root.ResizeObserver(() => this.resize()) : null;
      if (this._ro) this._ro.observe(this.el.card);
      this.resize();
      this._raf = root.requestAnimationFrame((t) => this.frame(t));
    }

    /* ---- public API ------------------------------------------------------------------------- */
    setScores(probs, ms) {
      this.probs = probs;
      this.target = clamp(1 - (probs.genuine || 0), 0, 1);
      // The meter says "cringe" once P(genuine) < 50%, so the verdict must name the leading CRINGE archetype
      // then, even if "genuine" is still (narrowly) the single most likely label.
      const cringeOnly = LABELS.filter((l) => l !== "genuine");
      const topCringe = cringeOnly.reduce((a, b) => ((probs[b] || 0) > (probs[a] || 0) ? b : a));
      const top = this.target >= 0.5 ? topCringe : "genuine";
      if (top !== this.topLabel || this._bucket !== this.bucket(this.target)) this.newVerdict(top);
      this.topLabel = top; this._bucket = this.bucket(this.target);
      this.el.ms.textContent = ms != null ? `scored in ${Math.round(ms)} ms` : "";
      this.el.tag.textContent = META[top].name;
      for (const l of LABELS) {
        const p = probs[l] || 0, b = this.barEls[l];
        b.querySelector(".fill").style.width = (p * 100).toFixed(0) + "%";
        b.querySelector(".fill").style.background = l === "genuine" ? "#34d399" : colourAt(clamp(0.35 + p * 0.65, 0, 1), 58);
        b.querySelector(".num").textContent = Math.round(p * 100);
        b.classList.toggle("top", l === top);
      }
    }
    setIdle(message) {
      this.probs = null; this.target = 0; this.topLabel = null; this._bucket = null;
      this.verdictFull = message || IDLE; this.verdictShown = 0; this.el.tag.textContent = "idle"; this.el.ms.textContent = "";
      for (const l of LABELS) { const b = this.barEls[l]; b.querySelector(".fill").style.width = "0"; b.querySelector(".num").textContent = "0"; b.classList.remove("top"); }
      this.setHot(null);
    }
    setHot(sentence) {
      this.el.hot.style.display = sentence && this.target > 0.3 ? "block" : "none";
      this.el.hotText.textContent = sentence ? "“" + sentence.trim() + "”" : "";
      this._hotSentence = sentence;
    }
    setBusy(b) { this.busy = !!b; this.el.dot.classList.toggle("busy", this.busy); }
    setStatus(text) { this.el.status.textContent = text; }
    destroy() { this.dead = true; if (this._ro) this._ro.disconnect(); root.cancelAnimationFrame(this._raf); }
    // A hidden meter must not burn CPU on a busy page: stop the animation loop while it is not shown.
    pause() { if (this.paused || this.dead) return; this.paused = true; root.cancelAnimationFrame(this._raf); }
    resume() { if (!this.paused || this.dead) return; this.paused = false; this.last = 0; this.resize(); this._raf = root.requestAnimationFrame((t) => this.frame(t)); }

    /* ---- internals -------------------------------------------------------------------------- */
    bucket(h) { return h < 0.12 ? 0 : h < 0.4 ? 1 : h < 0.65 ? 2 : h < 0.9 ? 3 : 4; }
    newVerdict(top) {
      const list = VERDICTS[top];
      this.verdictFull = list[Math.floor(Math.random() * list.length)]; this.verdictShown = 0;
    }
    resize() {
      const r = this.el.card.getBoundingClientRect(), dpr = Math.min(2, root.devicePixelRatio || 1);
      this.size = { w: r.width, h: r.height };
      this.el.canvas.width = Math.max(1, r.width * dpr); this.el.canvas.height = Math.max(1, r.height * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const s = this.el.thermo.getBoundingClientRect();
      this.svgRect = { x: s.left - r.left, y: s.top - r.top, k: s.width / 120 };
    }
    // svg-space (x, y in the 120x340 box) -> canvas px
    pt(x, y) { const s = this.svgRect; return { x: s.x + x * s.k, y: s.y + y * s.k }; }

    spawn(kind, x, y, extra) {
      const p = Object.assign({ kind, x, y, vx: 0, vy: 0, life: 0, max: 1, r: 4, a: 1 }, extra);
      if (this.parts.length < 260) this.parts.push(p);
    }
    emit(kind, rate, dt, fn) {
      this.emitAcc[kind] = (this.emitAcc[kind] || 0) + rate * dt;
      while (this.emitAcc[kind] >= 1) { this.emitAcc[kind] -= 1; fn(); }
    }

    frame(t) {
      if (this.dead || this.paused) return;
      this._raf = root.requestAnimationFrame((tt) => this.frame(tt));
      const dt = this.last ? clamp((t - this.last) / 1000, 0.001, 0.05) : 0.016; this.last = t;
      this.phase += dt;
      // heating is snappy and a little bouncy; cooling is slow and smooth, so it visibly "cools down"
      const k = this.target > this.h ? 46 : 9, c = 2 * Math.sqrt(k) * (this.target > this.h ? 0.8 : 1.0);
      this.v += ((this.target - this.h) * k - this.v * c) * dt; this.h = clamp(this.h + this.v * dt, 0, 1);
      const h = this.h, calm = this.reduced;

      // -- thermometer -------------------------------------------------------------------------
      const level = 260 - 220 * clamp(h * 0.98 + 0.02, 0, 1);      // y of the liquid surface (260 = empty tube base, 40 = top)
      const amp = 1.2 + 3 * smooth(0.3, 1, h), wl = 0.16;
      let d = `M0 ${(level + Math.sin(this.phase * 3) * amp).toFixed(1)}`;
      for (let x = 4; x <= 120; x += 4) d += ` L${x} ${(level + Math.sin(this.phase * 3 + x * wl) * amp).toFixed(1)}`;
      this.el.liquid.setAttribute("d", d + " L120 340 L0 340 Z");
      this.el.liquid.setAttribute("fill", colourAt(h));
      const mood = h < 0.12 ? "cool" : h < 0.4 ? "ok" : h < 0.65 ? "warm" : h < 0.9 ? "hot" : "crit";
      if (this.el.face.dataset.mood !== mood) { this.el.face.dataset.mood = mood; this.setFace(mood); }
      this.el.cracks.setAttribute("opacity", (smooth(0.88, 0.97, h) * 0.9).toFixed(2));
      // shake: none below .55, violent near 1
      const sh = calm ? 0 : smooth(0.55, 1, h);
      const jx = sh * 5 * (Math.random() - 0.5) * 2, jy = sh * 3 * (Math.random() - 0.5) * 2, rot = sh * 2.4 * (Math.random() - 0.5) * 2;
      this.el.thermo.style.transform = sh > 0.01 ? `translate(${jx.toFixed(2)}px, ${jy.toFixed(2)}px) rotate(${rot.toFixed(2)}deg)` : "";
      if (h > 0.9) this.el.card.style.transform = calm ? "" : `translate(${((Math.random() - 0.5) * 2.2).toFixed(2)}px, ${((Math.random() - 0.5) * 2.2).toFixed(2)}px)`;
      else if (this.el.card.style.transform) this.el.card.style.transform = "";
      this.el.card.classList.toggle("critical", h > 0.9);
      this.el.card.style.setProperty("--glow", (14 + h * 34).toFixed(0) + "px");
      this.el.card.style.setProperty("--glowc", h < 0.12 ? "rgba(120,200,255,.35)" : colourAt(h, 50).replace("hsl(", "hsla(").replace(")", " / .42)"));
      // -- text ---------------------------------------------------------------------------------
      this.el.pct.textContent = Math.round(h * 100);
      if (t - this.lastType > 16 && this.verdictShown < this.verdictFull.length) { this.verdictShown++; this.lastType = t; this.el.verdict.textContent = this.verdictFull.slice(0, this.verdictShown); }
      // -- particles ---------------------------------------------------------------------------
      if (!calm) this.particles(dt, h);
    }

    setFace(mood) {
      const f = this.el.face, q = (s) => f.querySelector(s);
      const eyes = q(".eyes"), closed = q(".closed"), brows = q(".brows"), mouth = q(".mouth"), pupils = f.querySelectorAll(".pupil");
      eyes.style.display = mood === "cool" ? "none" : ""; closed.style.display = mood === "cool" ? "" : "none";
      brows.style.display = mood === "warm" || mood === "hot" || mood === "crit" ? "" : "none";
      pupils.forEach((p) => p.setAttribute("r", mood === "crit" ? "1.6" : mood === "hot" ? "2.2" : "3"));
      const M = { cool: "M48 302 Q60 311 72 302", ok: "M50 303 Q60 308 70 303", warm: "M50 305 Q55 301 60 305 Q65 309 70 305", hot: "M54 302 Q60 296 66 302 Q60 314 54 302 Z", crit: "M48 296 Q60 292 72 296 Q74 318 60 318 Q46 318 48 296 Z" };
      mouth.setAttribute("d", M[mood]); mouth.setAttribute("fill", mood === "hot" || mood === "crit" ? "#1b1f2a" : "none");
    }

    particles(dt, h) {
      const ctx = this.ctx, W = this.size.w, H = this.size.h, s = this.svgRect ? this.svgRect.k : 1;
      const top = this.pt(60, 18), lvl = 260 - 220 * clamp(h * 0.98 + 0.02, 0, 1);
      // bubbles rise inside the liquid
      this.emit("bubble", 1.5 + 14 * h, dt, () => this.spawn("bubble", this.pt(rand(48, 72), 300).x, this.pt(0, rand(240, 300)).y, { vx: rand(-4, 4), vy: -rand(20, 44) * s, r: rand(1.2, 3.2) * s, max: 1.5, top: this.pt(0, lvl).y }));
      // sweat drops (warm+)
      if (h > 0.45) this.emit("sweat", 5 * smooth(0.45, 0.9, h), dt, () => { const side = Math.random() < 0.5 ? 30 : 90; this.spawn("sweat", this.pt(side, 250).x, this.pt(0, rand(225, 262)).y, { vx: side < 60 ? -rand(2, 10) : rand(2, 10), vy: rand(12, 40), r: rand(2, 3.8) * s, max: 1.1 }); });
      // smoke (hot+)
      if (h > 0.7) this.emit("smoke", 4 + 46 * smooth(0.7, 1, h), dt, () => this.spawn("smoke", top.x + rand(-6, 6) * s, top.y + rand(-2, 4) * s, { vx: rand(-14, 14), vy: -rand(22, 55), r: rand(8, 15) * s, max: rand(1.6, 2.8), grow: rand(14, 30) * s, dark: smooth(0.85, 1, h) }));
      // sparks at critical
      if (h > 0.92) this.emit("spark", 22, dt, () => this.spawn("spark", top.x + rand(-10, 10), top.y, { vx: rand(-90, 90), vy: -rand(50, 150), r: rand(1, 2.2), max: rand(0.4, 0.8) }));
      // snow when it is genuinely cool
      if (h < 0.12) this.emit("snow", 5 * (1 - h / 0.12), dt, () => this.spawn("snow", rand(0, W), -6, { vx: rand(-8, 8), vy: rand(14, 30), r: rand(1.2, 2.8), max: (H + 20) / 20 }));
      // the dominant archetype rains its emoji
      if (this.probs && this.topLabel && this.topLabel !== "genuine" && h > 0.35) {
        const p = this.probs[this.topLabel] || 0;
        this.emit("emoji", 8 * p * smooth(0.35, 0.9, h), dt, () => this.spawn("emoji", rand(W * 0.05, W * 0.95), H + 10, { vx: rand(-14, 14), vy: -rand(40, 95), r: rand(14, 24), max: rand(2, 3.4), e: META[this.topLabel].emoji, rot: rand(-0.4, 0.4) }));
      }
      // ---- update + draw ----
      ctx.clearRect(0, 0, W, H);
      const live = [];
      for (const p of this.parts) {
        p.life += dt; if (p.life >= p.max) continue;
        const u = p.life / p.max;
        if (p.kind === "smoke") { p.r += p.grow * dt; p.vx += rand(-20, 20) * dt; }
        p.x += p.vx * dt; p.y += p.vy * dt;
        if (p.kind === "bubble" && p.y < p.top) continue;
        if (p.kind === "sweat") p.vy += 60 * dt;
        if (p.kind === "spark") p.vy += 200 * dt;
        if (p.x < -30 || p.x > W + 30 || p.y > H + 30 || p.y < -40) continue;
        this.draw(ctx, p, u); live.push(p);
      }
      this.parts = live;
    }

    draw(ctx, p, u) {
      ctx.save();
      switch (p.kind) {
        case "smoke": {
          const a = (1 - u) * 0.8 * (u < 0.1 ? u / 0.1 : 1), g = Math.round(185 - p.dark * 150);
          const gr = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
          gr.addColorStop(0, `rgba(${g},${g},${g + 6},${a})`); gr.addColorStop(1, `rgba(${g},${g},${g + 6},0)`);
          ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); break;
        }
        case "bubble": ctx.strokeStyle = `rgba(255,255,255,${0.6 * (1 - u)})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.stroke(); break;
        case "sweat": ctx.fillStyle = `rgba(120,200,255,${0.9 * (1 - u)})`; ctx.beginPath(); ctx.ellipse(p.x, p.y, p.r * 0.7, p.r * 1.1, 0, 0, 6.283); ctx.fill(); break;
        case "spark": ctx.fillStyle = `rgba(255,${Math.round(200 - 120 * u)},60,${1 - u})`; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); break;
        case "snow": ctx.fillStyle = `rgba(220,240,255,${0.85 * (1 - u * u)})`; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); break;
        case "emoji":
          ctx.globalAlpha = (1 - u) * (u < 0.1 ? u / 0.1 : 1) * 0.95; ctx.translate(p.x, p.y); ctx.rotate(p.rot + Math.sin(u * 9) * 0.15);
          ctx.font = `${p.r}px "Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(p.e, 0, 0); break;
      }
      ctx.restore();
    }
  }

  /* Is there enough text to judge fairly? Two sentences (each at least 3 words) and about 10 words in total, or a
   * long run-on of 25+ words. Judging the first few words of a perfectly normal post is what made the meter "lose it". */
  CringeMeter.assess = function (text) {
    const raw = text || "";
    const words = raw.trim() ? raw.trim().split(/\s+/).length : 0;
    const sentences = raw.split(/(?<=[.!?…])\s+|\n+/).map((x) => x.trim()).filter((x) => x.split(/\s+/).filter(Boolean).length >= 3).length;
    const ok = (sentences >= 2 && words >= 10) || words >= 25;
    const hint = words === 0 ? IDLE : ok ? "" : `Write two sentences and I'll judge. (${Math.min(sentences, 2)} of 2)`;
    return { ok, words, sentences, hint };
  };
  CringeMeter.LABELS = LABELS; CringeMeter.META = META; CringeMeter.VERDICTS = VERDICTS;
  root.CringeMeter = CringeMeter;
})(typeof window !== "undefined" ? window : globalThis);
