// Attaches the Cringe Meter to the post box on LinkedIn / X. It looks at whatever large text field you are
// typing in (so it survives the sites changing their markup), scores it on every pause via the local server,
// and shows the thermometer as a floating card. It only ever reads the field you are typing in.
//
// Design notes (each one fixes something that went wrong in real use):
//  * The card is BUILT ONCE at page load, hidden, and just revealed when you focus a post box: opening a box shows
//    the meter instantly instead of constructing it then.
//  * It judges nothing until there are two sentences (CringeMeter.assess), so a normal post is not "lost" after 3 words.
//  * It heals itself: if the site removes the card, or swaps the editor for a new node, it re-attaches by itself.
//  * A dismissed (x) box comes back the next time you click into it, not never.
(() => {
  if (window.__cringeMeterContent) return;
  window.__cringeMeterContent = true;

  const VERSION = "0.4.0";        // shown on the badge and in errors, so you can tell which build Chrome is really running
  const DEBOUNCE_MS = 220, HOT_DELAY_MS = 650, RETRY_MS = 8000, POLL_MS = 200, WATCHDOG_MS = 500, LOST_GRACE_TICKS = 6;

  // If anything throws on the real page, say so on screen (a red note, bottom-left) instead of failing silently.
  function report(e, where) {
    try {
      console.error("[Cringe Meter " + VERSION + "] error in " + where, e);
      let b = document.getElementById("cringe-meter-error");
      if (!b) {
        b = document.createElement("div"); b.id = "cringe-meter-error"; b.setAttribute("popover", "manual");
        b.style.cssText = "position:fixed;inset:auto;left:18px;bottom:18px;margin:0;border:0;width:auto;height:auto;max-width:440px;z-index:2147483647;padding:8px 14px;border-radius:10px;background:#b3261e;color:#fff;font:600 12px -apple-system,Segoe UI,sans-serif;";
        document.documentElement.append(b);
        try { b.showPopover(); } catch (_) {}
      }
      b.textContent = "Cringe Meter " + VERSION + " error (" + where + "): " + String((e && e.message) || e).slice(0, 180);
    } catch (_) { /* nothing more we can do */ }
  }
  const safe = (where, fn) => (...a) => {
    try { const r = fn(...a); if (r && typeof r.catch === "function") r.catch((e) => report(e, where)); return r; }
    catch (e) { report(e, where); }
  };
  const EDITABLE = 'textarea, [contenteditable="true"], [contenteditable=""], [role="textbox"]';
  const KNOWN = '.ql-editor, [data-testid^="tweetTextarea"], .share-creation-state__text-editor [contenteditable]';

  let target = null, wrap = null, meter = null, seq = 0, mo = null, lostTicks = 0, lastHint = null;
  let tDebounce = null, tHot = null, tRetry = null;
  let dismissed = null, dismissedBlurred = false;

  const bg = (msg) => new Promise((res) => {
    try { chrome.runtime.sendMessage(msg, (r) => res(r || { ok: false, error: chrome.runtime.lastError?.message })); }
    catch (e) { res({ ok: false, error: String(e) }); }      // extension reloaded under us
  });

  const textOf = (el) => (el.value !== undefined ? el.value : el.innerText || "").replace(/ /g, " ");

  // A composer is a big editable box (not a search field or a one-line input).
  function composerFor(node) {
    const el = node && node.closest ? node.closest(EDITABLE) : null;
    if (!el || el.tagName === "INPUT") return null;
    if (el.matches(KNOWN)) return el;
    const r = el.getBoundingClientRect();
    return r.height >= 56 && r.width >= 200 ? el : null;
  }

  // The open modal <dialog> that holds the post box, looking through shadow roots. Everything OUTSIDE a modal dialog is
  // inert (a click would hit its backdrop and could close the post box), so the meter is parented INSIDE it. As a
  // popover it is still drawn in the top layer, above the dialog and its dark backdrop.
  function modalAncestor(el) {
    let n = el;
    while (n) { if (n.nodeType === 1 && n.tagName === "DIALOG" && n.open) return n; n = n.parentNode || n.host || null; }
    return null;
  }

  function place() {
    if (!wrap) return;
    const parent = (target && modalAncestor(target)) || document.documentElement;
    if (wrap.parentNode !== parent) { try { wrap.hidePopover(); } catch (_) {} parent.append(wrap); }
    try { if (!wrap.matches(":popover-open")) wrap.showPopover(); } catch (_) { /* older browser: plain z-index */ }
  }

  // ---- the card: built once, shown and hidden --------------------------------------------------------------------
  function build() {
    wrap = document.createElement("div");
    wrap.id = "cringe-meter-root";
    wrap.setAttribute("popover", "manual");
    wrap.style.cssText = "position:fixed;inset:auto;right:18px;bottom:18px;margin:0;padding:0;border:0;background:transparent;overflow:visible;width:auto;height:auto;color:inherit;z-index:2147483647;display:none;";
    const host = document.createElement("div");
    const x = document.createElement("button");
    x.textContent = "×"; x.title = "Hide the Cringe Meter for this box (click into the box again to bring it back)";
    x.style.cssText = "position:absolute;top:6px;right:8px;z-index:5;width:22px;height:22px;border:0;border-radius:50%;background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font:700 15px/22px sans-serif;padding:0;";
    x.onclick = () => { dismissed = target; dismissedBlurred = false; detach(); };
    wrap.append(host, x);
    // draggable: grab the card anywhere except the close button (it may cover a button on the host page)
    let drag = null;
    wrap.addEventListener("pointerdown", (e) => {
      if (e.target === x) return;
      const r = wrap.getBoundingClientRect(); drag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
      wrap.setPointerCapture(e.pointerId); wrap.style.cursor = "grabbing"; e.preventDefault();
    });
    wrap.addEventListener("pointermove", (e) => {
      if (!drag) return;
      const w = wrap.offsetWidth, h = wrap.offsetHeight;
      const left = Math.max(0, Math.min(innerWidth - w, e.clientX - drag.dx)), top = Math.max(0, Math.min(innerHeight - h, e.clientY - drag.dy));
      wrap.style.left = left + "px"; wrap.style.top = top + "px"; wrap.style.right = "auto"; wrap.style.bottom = "auto";
    });
    wrap.addEventListener("pointerup", () => { drag = null; wrap.style.cursor = ""; });
    document.documentElement.append(wrap);
    meter = new CringeMeter(host, { compact: true });
    meter.pause();                                       // hidden: no animation loop until it is shown
  }

  function show() {
    if (!wrap || !meter) build();
    if (!wrap) return;
    wrap.style.display = "";
    place();
    meter.resume();
  }

  function hide() {
    if (!wrap) return;
    try { wrap.hidePopover(); } catch (_) {}
    wrap.style.display = "none";
    meter.pause();
  }

  // ---- attach / detach -------------------------------------------------------------------------------------------
  function setHint(hint) {                               // only retype the message when it actually changes
    if (hint === lastHint) return;
    lastHint = hint; meter.setIdle(hint || undefined);
  }

  function attach(el) {
    if (el === dismissed) { if (!dismissedBlurred) return; dismissed = null; }   // hidden for this box until you click into it again
    if (el === target) return;
    if (!wrap || !meter) build();                        // never got built, or the page took it away
    const first = !target;
    target = el; lostTicks = 0;
    if (mo) mo.disconnect();
    mo = new MutationObserver(() => schedule());         // contenteditable editors (Quill, DraftJS) change the DOM, not .value
    mo.observe(el, { childList: true, characterData: true, subtree: true });
    if (first) { lastHint = null; meter.setIdle(); }
    show();
    schedule();
  }

  function detach() {
    if (mo) mo.disconnect(); mo = null; target = null;
    clearTimeout(tDebounce); clearTimeout(tHot); clearTimeout(tRetry); seq++; lastHint = null;
    if (meter) meter.setIdle();
    hide();
  }

  function schedule() { clearTimeout(tDebounce); tDebounce = setTimeout(safe("run", run), DEBOUNCE_MS); }

  async function run() {
    if (!target || !meter) return;
    const text = textOf(target), my = ++seq;
    clearTimeout(tHot);
    const a = CringeMeter.assess(text);
    if (!a.ok) { meter.setBusy(false); meter.setHot(null); setHint(a.hint); return; }   // not enough written to judge fairly
    lastHint = null;
    meter.setBusy(true);
    const r = await bg({ type: "score", text });
    if (my !== seq || !meter) return;                    // a newer keystroke superseded this one
    meter.setBusy(false);
    if (!r.ok || !r.data) { offline(); return; }
    clearTimeout(tRetry);
    meter.setStatus("local · Laya");
    if (!r.data.probs) { setHint(a.hint || CringeMeter.assess("").hint); return; }
    meter.setScores(r.data.probs, r.data.ms);
    meter.setHot(null);
    if (1 - r.data.probs.genuine > 0.3) tHot = setTimeout(() => hot(text, my), HOT_DELAY_MS);
  }

  async function hot(text, my) {
    const r = await bg({ type: "hot", text });
    if (!meter || my !== seq || !r.ok || !r.data) return;
    meter.setHot(r.data.sentence && r.data.heat > 0.4 ? r.data.sentence : null);
  }

  // The server may start after the page loads (or be stopped): keep trying quietly.
  function offline() {
    if (!meter) return;
    lastHint = null;
    meter.setIdle("Server not running. Start it with start-server.cmd");
    meter.setStatus("waiting for local server…");
    clearTimeout(tRetry);
    tRetry = setTimeout(async () => { const h = await bg({ type: "health" }); if (h.ok) schedule(); else offline(); }, RETRY_MS);
  }

  // ---- finding the post box --------------------------------------------------------------------------------------
  // LinkedIn's post box lives inside an open shadow root, so event.target at the document is the shadow HOST.
  // composedPath()[0] is the element that was really focused / typed in.
  const realTarget = (e) => (e.composedPath && e.composedPath()[0]) || e.target;
  const deepActive = () => { let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement; return a; };

  document.addEventListener("focusin", safe("focusin", (e) => { const el = composerFor(realTarget(e)); if (el) attach(el); }), true);
  document.addEventListener("focusout", safe("focusout", (e) => { if (dismissed && realTarget(e) === dismissed) dismissedBlurred = true; }), true);
  document.addEventListener("input", safe("input", (e) => {
    const t = realTarget(e);
    if (!target) { const el = composerFor(t); if (el) attach(el); return; }   // focusin missed: attach on the first keystroke
    if (t === target || target.contains(t)) schedule();
  }), true);

  // Focus events can be swallowed by shadow roots, so also look at what actually has focus. Cheap: runs 5x a second.
  setInterval(safe("poll", () => { const a = deepActive(); if (!a) return; const el = composerFor(a); if (el && el !== target) attach(el); }), POLL_MS);

  // Watchdog: heals the two things the host page does to us.
  setInterval(safe("watchdog", () => {
    if (!target) return;
    if (!target.isConnected) {                           // the editor was swapped for a new node (Quill re-init, route change)
      const a = deepActive(), el = a && composerFor(a);
      if (el) { target = null; attach(el); return; }
      if (++lostTicks >= LOST_GRACE_TICKS) detach();     // ~3 s with no replacement: the box is really gone
      return;
    }
    lostTicks = 0;
    // The box can stay in the page but be hidden (a closed dialog): hide the card with it, and bring it back when the box shows again.
    if (target.getClientRects().length === 0) { if (wrap && wrap.style.display !== "none") hide(); return; }
    if (wrap && (!wrap.isConnected || wrap.style.display === "none")) show();   // the page removed our card, or the box is back: show it
    else if (wrap && !wrap.matches(":popover-open")) place();
  }), WATCHDOG_MS);

  safe("build", build)();

  // A small badge for a few seconds so you can tell the extension loaded on this page.
  try {
    console.log("[Cringe Meter " + VERSION + "] loaded on", location.hostname);
    const b = document.createElement("div");
    b.textContent = "🌡 Cringe Meter v" + VERSION + " is on. Click into a post box.";
    b.setAttribute("popover", "manual");
    b.style.cssText = "position:fixed;inset:auto;right:18px;bottom:18px;margin:0;border:0;overflow:visible;width:auto;height:auto;z-index:2147483646;padding:8px 14px;border-radius:999px;background:#12151c;color:#e8ecf3;font:600 12px -apple-system,Segoe UI,sans-serif;box-shadow:0 4px 18px rgba(0,0,0,.35);transition:opacity .6s;pointer-events:none;";
    document.documentElement.append(b);
    try { b.showPopover(); } catch (_) {}
    setTimeout(() => { b.style.opacity = "0"; }, 6000);
    setTimeout(() => b.remove(), 6800);
  } catch (_) {}
})();
