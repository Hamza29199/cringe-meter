// Relays draft text from the page to the local Cringe Meter server. Content scripts on linkedin.com / x.com
// cannot reliably call http://127.0.0.1 themselves (the sites' security policies block it); this worker can,
// because host_permissions grants it. The text goes to 127.0.0.1 and nowhere else.
(() => {
  const SERVER = "http://127.0.0.1:8780";
  chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
    if (!msg || !["score", "hot", "health"].includes(msg.type)) return false;
    const init = msg.type === "health" ? { method: "GET" }
      : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: msg.text }) };
    fetch(`${SERVER}/${msg.type}`, init)
      .then(async (r) => reply({ ok: r.ok, data: await r.json().catch(() => null) }))
      .catch((e) => reply({ ok: false, error: String(e) }));
    return true; // async reply
  });
})();
