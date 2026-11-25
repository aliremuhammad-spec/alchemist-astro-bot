/* Rewarded ads, tried network by network until one serves a full view.
   IDs come from the server (/api/session → meta.ads); an empty ID turns that network off.
   Ported from the Gem Arcade integration (Adexium, TADS, OnClickA, Monetag, AdsGram). */
(() => {
  class AdUnavailable extends Error {}
  class AdSkipped extends Error {}
  const loaded = {};
  const load = (src, attrs = {}) => loaded[src] ??= new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = src; s.async = true; Object.assign(s.dataset, attrs);
    s.onload = res; s.onerror = () => { delete loaded[src]; rej(new AdUnavailable("sdk")); };
    document.head.appendChild(s);
  });

  async function adexium(wid) {
    await load("https://cdn.tgads.space/assets/js/adexium-widget.min.js");
    if (!window.AdexiumWidget) throw new AdUnavailable("sdk");
    let ad;
    try { ad = new window.AdexiumWidget({ wid, adFormat: "interstitial" }); } catch (e) { throw new AdUnavailable("init"); }
    await new Promise((resolve, reject) => {
      let shown = false, done = false;
      const t = setTimeout(() => !shown && finish(new AdUnavailable("timeout")), 12000);
      const hs = [
        ["adReceived", (ads) => { shown = true; ad.displayAd(ads); }],
        ["noAdFound", () => finish(new AdUnavailable("no_ad"))],
        ["requestAdError", () => finish(new AdUnavailable("error"))],
        ["adPlaybackCompleted", () => finish()],
        ["adClosed", () => setTimeout(() => finish(new AdSkipped("closed")), 150)],
      ];
      function finish(err) {
        if (done) return; done = true; clearTimeout(t);
        hs.forEach(([e, h]) => ad.off && ad.off(e, h));
        err ? reject(err) : resolve();
      }
      hs.forEach(([e, h]) => ad.on(e, h));
      ad.requestRewardedAd("interstitial").catch(() => finish(new AdUnavailable("error")));
    });
  }

  async function tads(widgetId) {
    if (!window.tads) await load("https://w.tads.me/widget.js");
    if (!window.tads) throw new AdUnavailable("sdk");
    await new Promise((resolve, reject) => {
      let done = false, rewarded = false, mo = null;
      const hard = setTimeout(() => finish(rewarded ? undefined : new AdUnavailable("timeout")), 90000);
      function finish(err) { if (done) return; done = true; clearTimeout(hard); mo && mo.disconnect(); err ? reject(err) : resolve(); }
      const before = new Set(Array.from(document.body.children));
      let ctl;
      try {
        ctl = window.tads.init({ widgetId, type: "fullscreen",
          onShowReward: () => { rewarded = true; finish(); },
          onAdsNotFound: () => finish(new AdUnavailable("no_ad")) });
      } catch (e) { return finish(new AdUnavailable("init")); }
      ctl.showAd().then(() => {
        const overlay = Array.from(document.body.children).filter((el) => !before.has(el));
        if (!overlay.length) return;
        mo = new MutationObserver(() => {
          if (overlay.every((el) => !el.isConnected)) setTimeout(() => finish(rewarded ? undefined : new AdSkipped("closed")), 800);
        });
        mo.observe(document.body, { childList: true, subtree: true });
      }).catch(() => finish(new AdUnavailable("no_ad")));
    });
  }

  async function onclicka(id) {
    if (!document.getElementById("onclicka-ad")) { const d = document.createElement("div"); d.id = "onclicka-ad"; document.body.appendChild(d); }
    if (!window.initCdTma) await load("https://js.onclckvd.com/in-stream-ad-admanager/tma.js");
    if (!window.initCdTma) throw new AdUnavailable("sdk");
    const show = await window.initCdTma({ id }).catch(() => { throw new AdUnavailable("init"); });
    const t0 = Date.now();
    try { await show(); } catch (e) { throw Date.now() - t0 > 3000 ? new AdSkipped("closed") : new AdUnavailable("no_ad"); }
  }

  async function monetag(zone, ticket) {
    const fn = "show_" + zone;
    if (!window[fn]) await load("https://libtl.com/sdk.js", { zone, sdk: fn });
    if (!window[fn]) throw new AdUnavailable("sdk");
    let r;
    try { r = await window[fn]({ ymid: ticket }); } catch (e) { throw new AdUnavailable("no_ad"); }
    if (!r || r.reward_event_type !== "valued") throw new AdSkipped("closed");
  }

  let gram = null;
  async function adsgram(blockId) {
    await load("https://sad.adsgram.ai/js/sad.min.js");
    if (!window.Adsgram) throw new AdUnavailable("sdk");
    gram = gram || window.Adsgram.init({ blockId });
    try { const r = await gram.show(); if (!r.done) throw new AdSkipped(r.description); }
    catch (e) { if (e instanceof AdSkipped) throw e; throw e && e.error ? new AdUnavailable("no_ad") : new AdSkipped("closed"); }
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  /** Returns {ticket, granted}. Throws AdSkipped if the user closed a real ad early. */
  async function watch(placement, cfg, api) {
    const { ticket, min_seconds } = await api("/api/ads/start", { method: "POST", body: JSON.stringify({ placement }) });
    const started = Date.now();
    const order = [
      ["adexium", cfg.adexium && (() => adexium(cfg.adexium))],
      ["tads", cfg.tads && (() => tads(cfg.tads))],
      ["onclicka", cfg.onclicka && (() => onclicka(cfg.onclicka))],
      ["monetag", cfg.monetag && (() => monetag(cfg.monetag, ticket))],
      ["adsgram", cfg.adsgram && (() => adsgram(cfg.adsgram))],
    ].filter(([, f]) => f);
    let served = null;
    for (const [name, show] of order) {
      const t0 = Date.now();
      try { await show(); served = name; break; }
      catch (e) {
        console.warn("[ads]", name, e && e.message);
        if (e instanceof AdSkipped && Date.now() - t0 > 3000) {
          await api("/api/ads/complete", { method: "POST", body: JSON.stringify({ ticket, provider: name, status: "skipped" }) }).catch(() => {});
          throw e;
        }
      }
    }
    if (served) {
      const wait = min_seconds * 1000 + 300 - (Date.now() - started);
      if (wait > 0) await sleep(wait);
    }
    const r = await api("/api/ads/complete", { method: "POST", body: JSON.stringify({
      ticket, provider: served || "none", status: served ? "completed" : "nofill" }) });
    return { ticket, granted: r.granted, served };
  }

  window.Ads = { watch, AdSkipped, AdUnavailable };
})();
