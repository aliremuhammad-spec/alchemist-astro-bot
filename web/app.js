/* The Alchemist Astro — Telegram Mini App (vanilla JS, no build step). */
(() => {
  const tg = window.Telegram && window.Telegram.WebApp;
  const qs = new URLSearchParams(location.search);
  const DEV = qs.get("dev"); // local preview only (server must run with DEV_AUTH=1)

  const I18N = {
    ar: {
      brand: "الخيميائي", beta: "<b>نسخة تجريبية</b> · من تطوير الخيميائي",
      tab_chart: "خارطتي", tab_syn: "التوافق", tab_daily: "برج اليوم", premium_btn: "✨ مميز",
      syn_title: "التوافق بين خارطتين", syn_sub: "اختار خارطتين من خرائطك المحفوظة. الحساب مجاني مقابل مشاهدة فيديو إعلاني قصير.",
      syn_need: "لازم يكون عندك خارطتين محفوظتين على الأقل. ضيف خارطة الشخص التاني من تبويب «خارطتي».",
      syn_a: "الشخص الأول", syn_b: "الشخص التاني", syn_go_ad: "شاهد إعلاناً واحسب التوافق", syn_go: "احسب التوافق",
      syn_same: "اختار شخصين مختلفين", ad_loading: "عم نحمّل الإعلان…", ad_closed: "انسكّر الإعلان قبل نهايته، جرّب مرة تانية.",
      ad_limit: "وصلت للحد اليومي، جرّب بكرا أو اشترك بالمميز.", score: "مؤشر التوافق", syn_details: "تفاصيل الاتصالات",
      varga: "الخريطة الفرعية", varga_lock: "الخرائط الفرعية من D2 لـ D60 للمشتركين المميزين (D9 مجانية).",
      prem_title: "الخيميائي المميز", prem_sub: "اشتراك شهري بالنجوم يفتح كل المزايا المتقدمة.",
      prem_active: "اشتراكك فعّال حتى ", prem_buy: "اشترك بـ {n} نجمة شهرياً", prem_paid: "تم الاشتراك، أهلاً بك بالمميز ✨",
      prem_perks: [["الخرائط الفرعية D2 لـ D60", "الهورا، الدريكانا، النافامشا، الداشامشا وكل الشودشافارغا"],
                   ["التوافق بلا إعلانات", "احسب توافق ما بدك مع أي خارطة محفوظة"],
                   ["ملفات غير محدودة", "احفظ خرائط العائلة والأصدقاء بدون حد"],
                   ["قريباً للمشتركين", "العبور اليومي الشخصي، تنبيهات العبور، الاختيارات الأسبوعية، التوافق الفيدي (36 نقطة)، تقرير PDF"]],
      prem_manual: "ما عندك نجوم تلغرام؟ راسلنا على إنستغرام لطرق دفع تانية.", tab_channels: "قنواتي", tab_about: "حول",
      hero_title: "خارطتك كما كانت السماء لحظة ولادتك",
      hero_sub: "بالنظامين الغربي والفيدي، مع الرسم الهندي الشمالي أو الجنوبي.",
      new_chart: "خارطة جديدة", name: "الاسم", name_ph: "اسمك أو اسم صاحب الخارطة",
      date: "تاريخ الولادة", day: "اليوم", month: "الشهر", year: "السنة",
      time: "وقت الولادة", hour: "الساعة", minute: "الدقيقة",
      unknown_time: "لا أعرف وقت الولادة",
      unknown_note: "بنحسب الخارطة على الظهر، وبدون طالع وبيوت لأنها بتعتمد على الوقت بالدقيقة.",
      place: "مكان الولادة", continent: "القارة", country: "الدولة", city: "المدينة",
      city_ph: "ابحث عن مدينتك", pick: "اختر…", indian_style: "شكل الخارطة الهندية",
      north: "شمالي", south: "جنوبي", calc: "احسب الخارطة", calculating: "عم نحسب…",
      western: "غربية", vedic: "فيدية", details_w: "مواقع الخارطة الغربية والاتصالات",
      details_v: "مواقع الخارطة الفيدية والنكشترا والدشا", send: "ابعتها عالمحادثة",
      sent: "بعتنا الخارطة عالمحادثة مع البوت", share: "شارك البوت",
      limit: "حفظنا لك {n} خرائط مجاناً. الخارطة انحسبت بس ما انحفظت.",
      del: "حذف", deleted: "انحذفت الخارطة", saved_charts: "خرائطك المحفوظة",
      need_city: "اختر المدينة من القائمة", need_date: "التاريخ غير صحيح",
      daily_title: "برجك كل يوم بوقتك", daily_sub: "رسالة يومية من البوت بالوقت اللي بتختاره، حسب برجك الشمسي.",
      daily_on: "ابعتلي برجي كل يوم", send_time: "وقت الإرسال", tz: "المنطقة الزمنية", sign: "البرج",
      sign_auto: "تلقائي من خارطتي", save: "احفظ", saved: "انحفظت الإعدادات",
      ch_title: "الأبراج اليومية لقناتك أو مجموعتك",
      ch_sub: "ضيف البوت، وكل يوم بينشر أبراج الـ12 برج كاملة بالوقت اللي بتختاره. مجاناً بالكامل.",
      add_channel: "أضف البوت لقناة", add_group: "أضف البوت لمجموعة",
      ch_steps: "بالقناة لازم يكون البوت مشرف مع صلاحية نشر الرسائل. بعد الإضافة بتظهر القناة هون وبتقدر تغيّر وقت النشر.",
      my_chats: "قنواتك ومجموعاتك", no_chats: "لسا ما ضفت البوت لأي قناة أو مجموعة.",
      lang: "لغة النشر", active: "النشر مفعّل",
      about_title: "عن الخيميائي",
      about_body: "هذه نسخة تجريبية (Beta) من بوت الخيميائي للفلك، من تطوير الخيميائي. الحسابات بمكتبة Swiss Ephemeris، والمحتوى للتأمل والترفيه.",
      follow: "تابعنا على إنستغرام", follow_main_sub: "الصفحة الرسمية للخيميائي", follow_partner_sub: "صفحة متعاونة",
      suggest_title: "اقتراح للتطوير", suggest_sub: "اكتب فكرتك أو ملاحظتك، وبتوصل مباشرة لحساب المطوّر.",
      suggest_ph: "شو الميزة اللي بتحب تشوفها؟ أو شو الشي اللي ما زبط معك؟", suggest_send: "ابعت الاقتراح",
      suggest_ok: "وصل اقتراحك للمطوّر، شكراً", source: "الكود المصدري",
      source_sub: "البوت مفتوح المصدر بترخيص AGPL-3.0", ui_lang: "لغة الواجهة",
      err: "صار خطأ: ", open_in_tg: "افتح التطبيق من داخل تلغرام عبر البوت.",
      months: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
      signs: ["الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء", "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت"],
    },
    en: {
      brand: "The Alchemist", beta: "<b>Beta</b> · developed by The Alchemist",
      tab_chart: "My chart", tab_syn: "Match", tab_daily: "Daily", premium_btn: "✨ Premium",
      syn_title: "Compatibility of two charts", syn_sub: "Pick two saved charts. It's free in exchange for a short video ad.",
      syn_need: "You need at least two saved charts. Add the other person's chart in My chart.",
      syn_a: "First person", syn_b: "Second person", syn_go_ad: "Watch an ad and compare", syn_go: "Compare charts",
      syn_same: "Pick two different people", ad_loading: "Loading the ad…", ad_closed: "The ad was closed early. Try again.",
      ad_limit: "Daily limit reached. Try tomorrow or go Premium.", score: "Compatibility score", syn_details: "Aspect details",
      varga: "Divisional chart", varga_lock: "Divisional charts D2–D60 are for Premium members (D9 is free).",
      prem_title: "Alchemist Premium", prem_sub: "A monthly Stars subscription that unlocks every advanced feature.",
      prem_active: "Your subscription is active until ", prem_buy: "Subscribe for {n} Stars a month", prem_paid: "You're Premium now ✨",
      prem_perks: [["Divisional charts D2–D60", "Hora, Drekkana, Navamsha, Dashamsha and the full Shodashavarga"],
                   ["Ad-free compatibility", "Compare any saved charts, as often as you like"],
                   ["Unlimited profiles", "Save family and friends without a limit"],
                   ["Coming for members", "Personal daily transits, transit alerts, weekly electional dates, Vedic 36-point matching, PDF report"]],
      prem_manual: "No Telegram Stars? Message us on Instagram for other payment options.", tab_channels: "Channels", tab_about: "About",
      hero_title: "Your chart: the sky at the moment you were born",
      hero_sub: "Western and Vedic, with a North or South Indian chart.",
      new_chart: "New chart", name: "Name", name_ph: "Your name or the chart owner's",
      date: "Birth date", day: "Day", month: "Month", year: "Year",
      time: "Birth time", hour: "Hour", minute: "Minute",
      unknown_time: "I don't know the birth time",
      unknown_note: "We'll cast it for noon, without Ascendant and houses, which need the exact time.",
      place: "Birthplace", continent: "Continent", country: "Country", city: "City",
      city_ph: "Search your city", pick: "Choose…", indian_style: "Indian chart style",
      north: "North", south: "South", calc: "Calculate chart", calculating: "Calculating…",
      western: "Western", vedic: "Vedic", details_w: "Western positions and aspects",
      details_v: "Vedic positions, nakshatras and dashas", send: "Send to chat",
      sent: "Chart sent to your chat with the bot", share: "Share the bot",
      limit: "Free plan keeps {n} charts. This one was calculated but not saved.",
      del: "Delete", deleted: "Chart deleted", saved_charts: "Saved charts",
      need_city: "Choose a city from the list", need_date: "Invalid date",
      daily_title: "Your horoscope, daily, on your time", daily_sub: "A daily message from the bot at the time you choose, by your sun sign.",
      daily_on: "Send me my horoscope every day", send_time: "Send at", tz: "Time zone", sign: "Sign",
      sign_auto: "From my chart", save: "Save", saved: "Settings saved",
      ch_title: "Daily horoscopes for your channel or group",
      ch_sub: "Add the bot and it posts all 12 signs every day at the time you choose. Completely free.",
      add_channel: "Add to a channel", add_group: "Add to a group",
      ch_steps: "In channels the bot must be an admin allowed to post. After adding, the chat appears here and you can set the time.",
      my_chats: "Your channels and groups", no_chats: "You haven't added the bot to a channel or group yet.",
      lang: "Post language", active: "Posting on",
      about_title: "About The Alchemist",
      about_body: "This is a beta of The Alchemist astrology bot, developed by The Alchemist. Calculations use the Swiss Ephemeris; content is for reflection and entertainment.",
      follow: "Follow us on Instagram", follow_main_sub: "The Alchemist's official page", follow_partner_sub: "Partner page",
      suggest_title: "Suggest an improvement", suggest_sub: "Your idea or note goes straight to the developer's account.",
      suggest_ph: "What would you like to see? What didn't work?", suggest_send: "Send suggestion",
      suggest_ok: "Your suggestion reached the developer. Thanks", source: "Source code",
      source_sub: "Open source under AGPL-3.0", ui_lang: "Interface language",
      err: "Error: ", open_in_tg: "Open the app from inside Telegram via the bot.",
      months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      signs: ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
    },
  };
  const GLYPHS = [..."♈♉♊♋♌♍♎♏♐♑♒♓"].map((g) => g + "\uFE0E");

  const S = { lang: "ar", theme: "dark", session: null, tab: "chart", chart: null, profileId: null,
              system: "western", style: "north", form: {}, editing: false };
  const $ = (sel, el = document) => el.querySelector(sel);
  const T = (k) => I18N[S.lang][k] ?? k;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const haptic = (t = "light") => { try { tg.HapticFeedback.impactOccurred(t); } catch (e) {} };

  function toast(msg) {
    const el = $("#toast"); el.textContent = msg; el.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(() => el.classList.remove("show"), 2600);
  }

  async function api(path, opts = {}) {
    const headers = { "Content-Type": "application/json" };
    if (DEV) headers.Authorization = "dev " + DEV;
    else if (tg && tg.initData) headers.Authorization = "tma " + tg.initData;
    const r = await fetch(path, { ...opts, headers: { ...headers, ...(opts.headers || {}) } });
    if (!r.ok) {
      let d = ""; try { d = (await r.json()).detail; } catch (e) {}
      throw new Error(typeof d === "string" ? d : r.status + "");
    }
    return r.json();
  }

  function openLink(url) { if (tg && tg.openLink) tg.openLink(url); else window.open(url, "_blank"); }
  function openTg(url) { if (tg && tg.openTelegramLink) tg.openTelegramLink(url); else window.open(url, "_blank"); }

  function countryName(iso) {
    try { return new Intl.DisplayNames([S.lang], { type: "region" }).of(iso); } catch (e) { return iso; }
  }

  function applyLang() {
    document.documentElement.lang = S.lang;
    document.documentElement.dir = S.lang === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-t]").forEach((el) => { el.innerHTML = T(el.dataset.t); });
  }

  /* ───────────── tabs ───────────── */
  function setTab(tab) {
    S.tab = tab;
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === tab));
    ({ chart: renderChart, synastry: renderSynastry, daily: renderDaily, channels: renderChannels,
       about: renderAbout, premium: renderPremium })[tab]();
    $("#prem-btn").classList.toggle("on", tab === "premium");
    window.scrollTo(0, 0);
  }

  /* ───────────── chart tab ───────────── */
  function zodiacRing() {
    const items = GLYPHS.map((g, i) => {
      const a = (i * 30 - 75) * Math.PI / 180, r = 96;
      return `<text x="${120 + r * Math.cos(a)}" y="${120 + r * Math.sin(a) + 5}" text-anchor="middle">${g}</text>`;
    }).join("");
    const ticks = Array.from({ length: 12 }, (_, i) => {
      const a = (i * 30 - 60) * Math.PI / 180;
      return `<line x1="${120 + 82 * Math.cos(a)}" y1="${120 + 82 * Math.sin(a)}" x2="${120 + 110 * Math.cos(a)}" y2="${120 + 110 * Math.sin(a)}"/>`;
    }).join("");
    return `<div class="hero-ring"><svg viewBox="0 0 240 240" aria-hidden="true" fill="none" stroke="var(--brass)" stroke-width="1">
      <circle cx="120" cy="120" r="110"/><circle cx="120" cy="120" r="82"/><circle cx="120" cy="120" r="40" stroke="var(--verdigris)"/>
      <g opacity=".5">${ticks}</g><g stroke="none">${items}</g></svg></div>`;
  }

  function profileChips() {
    const ps = S.session.profiles;
    if (!ps.length) return "";
    return `<h3>${T("saved_charts")}</h3><div class="chips">${ps.map((p) =>
      `<button class="chip" data-pid="${p.id}" aria-pressed="${p.id === S.profileId && !S.editing}">${esc(p.name)}</button>`).join("")}
      <button class="chip add" data-new aria-pressed="${S.editing}">+ ${T("new_chart")}</button></div>`;
  }

  function renderChart() {
    const v = $("#view");
    const showForm = S.editing || !S.chart;
    v.innerHTML = `${profileChips()}
      ${S.chart && !S.editing ? chartView() : ""}
      ${showForm ? (S.session.profiles.length ? "" : `${zodiacRing()}<h2>${T("hero_title")}</h2><p class="muted">${T("hero_sub")}</p>`) + formView() : ""}`;
    v.querySelectorAll("[data-pid]").forEach((b) => b.onclick = () => loadProfile(+b.dataset.pid));
    const nb = v.querySelector("[data-new]"); if (nb) nb.onclick = () => { S.editing = true; renderChart(); };
    if (showForm) bindForm(); else bindChart();
  }

  function formView() {
    const f = S.form; const y = new Date().getFullYear();
    const opts = (from, to, sel, labels) => Array.from({ length: to - from + 1 }, (_, i) => from + i)
      .map((n) => `<option value="${n}" ${n == sel ? "selected" : ""}>${labels ? labels[n - 1] : n}</option>`).join("");
    return `<form id="cf" novalidate>
      <label for="f-name">${T("name")}</label><input id="f-name" maxlength="60" placeholder="${T("name_ph")}" value="${esc(f.name || S.session.user.first_name || "")}">
      <label>${T("date")}</label>
      <div class="grid3">
        <select id="f-day" aria-label="${T("day")}">${opts(1, 31, f.day || 1)}</select>
        <select id="f-month" aria-label="${T("month")}">${opts(1, 12, f.month || 1, T("months"))}</select>
        <select id="f-year" aria-label="${T("year")}">${Array.from({ length: y - 1899 }, (_, i) => y - i).map((n) => `<option value="${n}" ${n == (f.year || 1995) ? "selected" : ""}>${n}</option>`).join("")}</select>
      </div>
      <label>${T("time")}</label>
      <div class="grid2" id="time-row" ${f.unknown ? "hidden" : ""}>
        <select id="f-hour" aria-label="${T("hour")}">${opts(0, 23, f.hour ?? 12).replace(/>(\d)</g, ">0$1<")}</select>
        <select id="f-min" aria-label="${T("minute")}">${opts(0, 59, f.minute ?? 0).replace(/>(\d)</g, ">0$1<")}</select>
      </div>
      <label class="switch"><input type="checkbox" id="f-unknown" ${f.unknown ? "checked" : ""}> ${T("unknown_time")}</label>
      <p class="muted" id="unknown-note" ${f.unknown ? "" : "hidden"}>${T("unknown_note")}</p>
      <label>${T("place")}</label>
      <div class="grid2">
        <select id="f-cont" aria-label="${T("continent")}"><option value="">${T("continent")}</option></select>
        <select id="f-country" aria-label="${T("country")}" disabled><option value="">${T("country")}</option></select>
      </div>
      <input id="f-city" placeholder="${T("city_ph")}" autocomplete="off" disabled style="margin-top:8px">
      <div class="cities" id="cities" role="listbox"></div>
      <label>${T("indian_style")}</label>
      <div class="seg" id="f-style"><button type="button" data-v="north" aria-pressed="${S.style === "north"}">${T("north")}</button><button type="button" data-v="south" aria-pressed="${S.style === "south"}">${T("south")}</button></div>
      <button class="btn block" id="f-go">${T("calc")}</button>
    </form>`;
  }

  async function bindForm() {
    const f = S.form;
    const unk = $("#f-unknown");
    unk.onchange = () => { $("#time-row").hidden = unk.checked; $("#unknown-note").hidden = !unk.checked; };
    $("#f-style").onclick = (e) => {
      const b = e.target.closest("button"); if (!b) return;
      S.style = b.dataset.v; $("#f-style").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
    };
    const cont = $("#f-cont"), country = $("#f-country"), city = $("#f-city"), list = $("#cities");
    const conts = await api(`/api/geo/continents?lang=${S.lang}`);
    cont.innerHTML += conts.map((c) => `<option value="${c.code}">${esc(c.name)}</option>`).join("");
    let cityTimer;
    const loadCities = async () => {
      if (!country.value) return;
      const rows = await api(`/api/geo/cities?country=${country.value}&q=${encodeURIComponent(city.value.trim())}`);
      list.innerHTML = rows.map((c) => `<button type="button" role="option" data-id="${c.id}" aria-selected="${c.id === f.city_id}">
        <span>${esc(S.lang === "ar" && c.ar ? c.ar : c.name)}</span><small>${S.lang === "ar" && c.ar ? esc(c.name) : ""}</small></button>`).join("");
    };
    cont.onchange = async () => {
      country.disabled = !cont.value; city.disabled = true; list.innerHTML = "";
      if (!cont.value) return;
      const cs = await api(`/api/geo/countries?continent=${cont.value}`);
      cs.forEach((c) => c.local = countryName(c.iso));
      cs.sort((a, b) => a.local.localeCompare(b.local, S.lang));
      country.innerHTML = `<option value="">${T("country")}</option>` + cs.map((c) => `<option value="${c.iso}">${esc(c.local)}</option>`).join("");
    };
    country.onchange = () => { f.city_id = null; city.value = ""; city.disabled = !country.value; loadCities(); };
    city.oninput = () => { f.city_id = null; clearTimeout(cityTimer); cityTimer = setTimeout(loadCities, 250); };
    list.onclick = (e) => {
      const b = e.target.closest("button[data-id]"); if (!b) return;
      f.city_id = +b.dataset.id; f.country = country.value;
      city.value = b.querySelector("span").textContent;
      list.querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", x === b));
      haptic();
    };
    $("#cf").onsubmit = async (e) => {
      e.preventDefault();
      Object.assign(f, {
        name: $("#f-name").value.trim(), day: +$("#f-day").value, month: +$("#f-month").value, year: +$("#f-year").value,
        hour: +$("#f-hour").value, minute: +$("#f-min").value, unknown: unk.checked,
      });
      const d = new Date(f.year, f.month - 1, f.day);
      if (d.getMonth() !== f.month - 1) return toast(T("need_date"));
      if (!f.city_id) return toast(T("need_city"));
      const go = $("#f-go"); go.disabled = true; go.innerHTML = `<span class="spinner"></span> ${T("calculating")}`;
      try {
        const res = await api("/api/chart", { method: "POST", body: JSON.stringify({
          name: f.name, day: f.day, month: f.month, year: f.year, hour: f.hour, minute: f.minute,
          time_known: !f.unknown, country: f.country, city_id: f.city_id, indian_style: S.style,
          theme: S.theme, lang: S.lang, save: true }) });
        // optional ad after a new chart (switched on server-side with CHART_AD=1; never for Premium)
        if (S.session.meta.chart_ad && !S.session.premium && window.Ads) {
          try { await window.Ads.watch("chart", S.session.meta.ads || {}, api); } catch (e) { /* the chart is free either way */ }
        }
        S.chart = res; S.profileId = res.profile_id; S.editing = false; S.system = "western"; S.varga = 1; S.vargaSvg = null;
        if (res.profile_limit_hit) toast(T("limit").replace("{n}", S.session.meta.free_profiles));
        await refreshSession();
        haptic("medium");
        renderChart();
      } catch (err) {
        toast(T("err") + err.message); go.disabled = false; go.textContent = T("calc");
      }
    };
  }

  function chartView() {
    const c = S.chart, m = c.meta;
    const place = [m.city, countryName(m.country)].filter(Boolean).join("، ");
    const warn = !m.time_known ? `<p class="warn">${T("unknown_note")}</p>` : "";
    return `<section class="stage">
      <p class="name">${esc(m.name)}</p><p class="when">${esc(m.local)} · ${esc(place)}</p>
      <div class="row between">
        <div class="seg" id="sys"><button data-v="western" aria-pressed="${S.system === "western"}">${T("western")}</button><button data-v="vedic" aria-pressed="${S.system === "vedic"}">${T("vedic")}</button></div>
        <div class="seg" id="sty" ${S.system === "vedic" ? "" : "hidden"}><button data-v="north" aria-pressed="${S.style === "north"}">${T("north")}</button><button data-v="south" aria-pressed="${S.style === "south"}">${T("south")}</button></div>
      </div>
      ${S.system === "vedic" && S.profileId ? `<label for="varga">${T("varga")}</label><select id="varga">${vargaOptions()}</select>` : ""}
      <div id="svg">${S.system === "western" ? c.svg.western : (S.vargaSvg || c.svg.indian)}</div>
    </section>
    ${warn}
    <details ${S.system === "western" ? "open" : ""}><summary>${T("details_w")}</summary><div class="report">${c.text.western}</div></details>
    <details ${S.system === "vedic" ? "open" : ""}><summary>${T("details_v")}</summary><div class="report">${c.text.vedic}</div></details>
    <div class="row">
      ${S.profileId ? `<button class="btn" id="send">${T("send")}</button>` : ""}
      <button class="btn ghost" id="share">${T("share")}</button>
      ${S.profileId ? `<button class="btn ghost small" id="del">${T("del")}</button>` : ""}
    </div>`;
  }

  function vargaOptions() {
    const prem = S.session.premium;
    return (S.vargas || [{ n: 1, name: "Rashi", ar: "الراشي" }]).map((v) =>
      `<option value="${v.n}" ${v.n === S.varga ? "selected" : ""}>${v.n === 1 || v.n === 9 || prem ? "" : "🔒 "}D${v.n} · ${esc(S.lang === "ar" ? v.ar : v.name)}</option>`).join("");
  }

  async function loadVarga(n) {
    if (n === 1) { S.varga = 1; S.vargaSvg = null; return renderChart(); }
    if (n !== 9 && !S.session.premium) { toast(T("varga_lock")); $("#varga").value = String(S.varga); return; }
    try {
      const r = await api(`/api/profiles/${S.profileId}/varga/${n}?style=${S.style}&theme=${S.theme}&lang=${S.lang}`);
      S.varga = n; S.vargaSvg = r.svg; renderChart();
    } catch (e) { toast(T("err") + e.message); }
  }

  function bindChart() {
    const vs = $("#varga"); if (vs) vs.onchange = () => loadVarga(+vs.value);
    $("#sys").onclick = (e) => {
      const b = e.target.closest("button"); if (!b) return;
      S.system = b.dataset.v; haptic(); renderChart();
    };
    $("#sty").onclick = async (e) => {
      const b = e.target.closest("button"); if (!b || b.dataset.v === S.style) return;
      S.style = b.dataset.v; haptic();
      if (S.profileId) { await loadProfile(S.profileId, true); }
    };
    const send = $("#send");
    if (send) send.onclick = async () => {
      send.disabled = true;
      try { await api(`/api/profiles/${S.profileId}/send`, { method: "POST", body: JSON.stringify({ lang: S.lang, style: S.style }) }); toast(T("sent")); haptic("medium"); }
      catch (e) { toast(T("err") + e.message); }
      send.disabled = false;
    };
    $("#share").onclick = () => {
      const url = `https://t.me/${S.session.meta.bot}`;
      const text = S.lang === "ar" ? "احسب خارطتك الفلكية الغربية والفيدية مجاناً مع بوت الخيميائي ✨" : "Cast your Western & Vedic birth chart for free ✨";
      openTg(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`);
    };
    const del = $("#del");
    if (del) del.onclick = async () => {
      await api(`/api/profiles/${S.profileId}`, { method: "DELETE" });
      S.chart = null; S.profileId = null; await refreshSession(); toast(T("deleted")); renderChart();
    };
  }

  async function loadProfile(pid, keepSystem) {
    try {
      const p = S.session.profiles.find((x) => x.id === pid);
      if (!keepSystem && p) S.style = p.indian_style;
      S.chart = await api(`/api/profiles/${pid}/chart?style=${S.style}&theme=${S.theme}&lang=${S.lang}`);
      S.profileId = pid; S.editing = false;
      if (!keepSystem) { S.system = "western"; S.varga = 1; S.vargaSvg = null; }
      else if (S.varga && S.varga !== 1) { const n = S.varga; S.varga = 1; S.vargaSvg = null; renderChart(); return loadVarga(n); }
      renderChart();
    } catch (e) { toast(T("err") + e.message); }
  }

  /* ───────────── daily tab ───────────── */
  async function renderDaily() {
    const d = S.session.daily || {};
    const tz = d.tz || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Damascus";
    const tzs = await api("/api/timezones");
    const hasProfile = S.session.profiles.length > 0;
    $("#view").innerHTML = `<h2>${T("daily_title")}</h2><p class="muted">${T("daily_sub")}</p>
      <label class="switch"><input type="checkbox" id="d-on" ${d.subscribed !== false ? "checked" : ""}> ${T("daily_on")}</label>
      <label for="d-time">${T("send_time")}</label><input type="time" id="d-time" value="${d.send_time || "08:00"}">
      <label for="d-tz">${T("tz")}</label><select id="d-tz">${tzs.map((z) => `<option ${z === tz ? "selected" : ""}>${z}</option>`).join("")}</select>
      <label for="d-sign">${T("sign")}</label>
      <select id="d-sign">${hasProfile ? `<option value="">${T("sign_auto")}</option>` : ""}
        ${T("signs").map((s, i) => `<option value="${i}" ${d.sign === i ? "selected" : ""}>${GLYPHS[i]} ${s}</option>`).join("")}</select>
      <button class="btn block" id="d-save">${T("save")}</button>`;
    $("#d-save").onclick = async () => {
      const sign = $("#d-sign").value;
      try {
        S.session.daily = await api("/api/daily", { method: "POST", body: JSON.stringify({
          subscribed: $("#d-on").checked, send_time: $("#d-time").value || "08:00", tz: $("#d-tz").value,
          sign: sign === "" ? null : +sign }) });
        toast(T("saved")); haptic("medium"); renderDaily();
      } catch (e) { toast(T("err") + e.message); }
    };
  }

  /* ───────────── channels tab ───────────── */
  async function renderChannels() {
    const m = S.session.meta;
    $("#view").innerHTML = `<h2>${T("ch_title")}</h2><p class="muted">${T("ch_sub")}</p>
      <div class="row"><button class="btn" id="c-add">${T("add_channel")}</button><button class="btn ghost" id="g-add">${T("add_group")}</button></div>
      <p class="muted">${T("ch_steps")}</p><h3>${T("my_chats")}</h3><div class="list" id="chats"><span class="spinner"></span></div>`;
    $("#c-add").onclick = () => openTg(m.add_channel);
    $("#g-add").onclick = () => openTg(m.add_group);
    const [chats, tzs] = await Promise.all([api("/api/channels"), api("/api/timezones")]);
    const box = $("#chats");
    if (!chats.length) { box.innerHTML = `<p class="muted">${T("no_chats")}</p>`; return; }
    box.innerHTML = chats.map((c) => `<div class="item" data-chat="${c.chat_id}"><h4>${esc(c.title || c.chat_id)}</h4>
      <div class="grid2"><input type="time" value="${c.send_time}" data-k="send_time" aria-label="${T("send_time")}">
      <select data-k="lang" aria-label="${T("lang")}"><option value="ar" ${c.lang === "ar" ? "selected" : ""}>العربية</option><option value="en" ${c.lang === "en" ? "selected" : ""}>English</option></select></div>
      <select data-k="tz" style="margin-top:8px" aria-label="${T("tz")}">${tzs.map((z) => `<option ${z === c.tz ? "selected" : ""}>${z}</option>`).join("")}</select>
      <label class="switch"><input type="checkbox" data-k="active" ${c.active ? "checked" : ""}> ${T("active")}</label>
      <button class="btn small" data-save style="margin-top:10px">${T("save")}</button></div>`).join("");
    box.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
      const it = b.closest(".item"), g = (k) => it.querySelector(`[data-k="${k}"]`);
      try {
        await api(`/api/channels/${it.dataset.chat}`, { method: "POST", body: JSON.stringify({
          send_time: g("send_time").value, tz: g("tz").value, lang: g("lang").value, active: g("active").checked }) });
        toast(T("saved"));
      } catch (e) { toast(T("err") + e.message); }
    });
  }

  /* ───────────── about tab ───────────── */
  function renderAbout() {
    const m = S.session.meta;
    const ig = `<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/></svg>`;
    const code = `<svg viewBox="0 0 24 24"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>`;
    $("#view").innerHTML = `<h2>${T("about_title")}</h2><p>${T("about_body")}</p>
      <h3>${T("follow")}</h3>
      <div class="follow">
        <a href="#" data-link="https://instagram.com/${m.instagram_main}">${ig}<span>@${esc(m.instagram_main)}<small>${T("follow_main_sub")}</small></span></a>
        ${m.instagram_partner ? `<a href="#" data-link="https://instagram.com/${m.instagram_partner}">${ig}<span>${esc(m.instagram_partner_label)} · @${esc(m.instagram_partner)}<small>${T("follow_partner_sub")}</small></span></a>` : ""}
      </div>
      <h3>${T("suggest_title")}</h3><p class="muted">${T("suggest_sub")}</p>
      <textarea id="fb" maxlength="3500" placeholder="${T("suggest_ph")}"></textarea>
      <button class="btn block" id="fb-send">${T("suggest_send")}</button>
      <h3>${T("source")}</h3>
      <div class="follow"><a href="#" data-link="${esc(m.source)}">${code}<span>GitHub<small>${T("source_sub")}</small></span></a></div>
      <h3>${T("ui_lang")}</h3>
      <div class="seg" id="lang"><button data-v="ar" aria-pressed="${S.lang === "ar"}">العربية</button><button data-v="en" aria-pressed="${S.lang === "en"}">English</button></div>`;
    $("#view").querySelectorAll("[data-link]").forEach((a) => a.onclick = (e) => { e.preventDefault(); openLink(a.dataset.link); });
    $("#fb-send").onclick = async () => {
      const text = $("#fb").value.trim(); if (text.length < 3) return;
      const b = $("#fb-send"); b.disabled = true;
      try { await api("/api/feedback", { method: "POST", body: JSON.stringify({ text }) }); $("#fb").value = ""; toast(T("suggest_ok")); haptic("medium"); }
      catch (e) { toast(T("err") + e.message); }
      b.disabled = false;
    };
    $("#lang").onclick = async (e) => {
      const b = e.target.closest("button"); if (!b) return;
      S.lang = b.dataset.v; applyLang(); renderAbout();
      api("/api/lang", { method: "POST", body: JSON.stringify({ lang: S.lang }) }).catch(() => {});
      if (S.profileId) loadProfile(S.profileId, true);
    };
  }

  /* ───────────── synastry tab ───────────── */
  function renderSynastry() {
    const ps = S.session.profiles;
    if (ps.length < 2) {
      $("#view").innerHTML = `<h2>${T("syn_title")}</h2><p class="muted">${T("syn_need")}</p><button class="btn" id="go-chart">${T("new_chart")}</button>`;
      $("#go-chart").onclick = () => { S.editing = true; setTab("chart"); };
      return;
    }
    const opt = (sel) => ps.map((p) => `<option value="${p.id}" ${p.id === sel ? "selected" : ""}>${esc(p.name)} · ${p.birth_date}</option>`).join("");
    const prem = S.session.premium;
    $("#view").innerHTML = `<h2>${T("syn_title")}</h2><p class="muted">${prem ? "" : T("syn_sub")}</p>
      <label for="sa">${T("syn_a")}</label><select id="sa">${opt(S.synA || ps[0].id)}</select>
      <label for="sb">${T("syn_b")}</label><select id="sb">${opt(S.synB || ps[1].id)}</select>
      <button class="btn block" id="syn-go">${prem ? T("syn_go") : T("syn_go_ad")}</button>
      <div id="syn-out">${S.synResult ? synView(S.synResult) : ""}</div>`;
    $("#syn-go").onclick = runSynastry;
  }

  function synView(r) {
    return `<section class="stage" style="margin-top:16px"><p class="name">${esc(r.names[0])} · ${esc(r.names[1])}</p>
      <div class="score"><b>${r.score.value}</b><span class="muted">${T("score")}</span></div>${r.svg}</section>
      <details open><summary>${T("syn_details")}</summary><div class="report">${r.text}</div></details>`;
  }

  async function runSynastry() {
    const a = +$("#sa").value, b = +$("#sb").value;
    if (a === b) return toast(T("syn_same"));
    S.synA = a; S.synB = b;
    const btn = $("#syn-go"); btn.disabled = true;
    let ticket = null;
    try {
      if (!S.session.premium) {
        btn.innerHTML = `<span class="spinner"></span> ${T("ad_loading")}`;
        const r = await window.Ads.watch("synastry", S.session.meta.ads || {}, api);
        if (!r.granted) throw new Error("ad");
        ticket = r.ticket;
      }
      btn.innerHTML = `<span class="spinner"></span> ${T("calculating")}`;
      S.synResult = await api("/api/synastry", { method: "POST", body: JSON.stringify({ a, b, ticket, theme: S.theme, lang: S.lang }) });
      haptic("medium"); renderSynastry();
    } catch (e) {
      const msg = e instanceof window.Ads.AdSkipped ? T("ad_closed") : /limit/.test(e.message) ? T("ad_limit") : T("err") + e.message;
      toast(msg); btn.disabled = false; btn.textContent = S.session.premium ? T("syn_go") : T("syn_go_ad");
    }
  }

  /* ───────────── premium ───────────── */
  async function renderPremium() {
    const info = await api("/api/premium");
    const perks = T("prem_perks").map(([b, s]) => `<li><b>${b}</b><span>${s}</span></li>`).join("");
    $("#view").innerHTML = `<h2>${T("prem_title")}</h2><p class="muted">${T("prem_sub")}</p><ul class="perks">${perks}</ul>
      ${info.active ? `<p class="warn">${T("prem_active")}${info.until.slice(0, 10)}</p>`
                    : `<button class="btn block" id="buy">⭐ ${T("prem_buy").replace("{n}", info.stars)}</button>`}
      <p class="muted" style="margin-top:14px">${T("prem_manual")}</p>`;
    const buy = $("#buy");
    if (buy) buy.onclick = async () => {
      buy.disabled = true;
      try {
        const { link } = await api("/api/premium/invoice", { method: "POST" });
        const done = async (status) => {
          buy.disabled = false;
          if (status === "paid") {
            toast(T("prem_paid")); haptic("heavy");
            setTimeout(async () => { await refreshSession(); renderPremium(); }, 1500);
          }
        };
        if (tg && tg.openInvoice) tg.openInvoice(link, done); else { openTg(link); buy.disabled = false; }
      } catch (e) { toast(T("err") + e.message); buy.disabled = false; }
    };
  }

  async function refreshSession() { S.session = await api("/api/session", { method: "POST" }); }

  /* ───────────── boot ───────────── */
  async function boot() {
    if (tg) {
      tg.ready(); tg.expand();
      S.theme = tg.colorScheme === "light" ? "light" : "dark";
      try { tg.setHeaderColor(S.theme === "light" ? "#eef1ec" : "#141a33"); tg.setBackgroundColor(S.theme === "light" ? "#eef1ec" : "#141a33"); } catch (e) {}
    }
    if (qs.get("theme") === "light") S.theme = "light";
    document.documentElement.classList.toggle("light", S.theme === "light");
    const code = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) || navigator.language || "ar";
    S.lang = code.startsWith("ar") ? "ar" : "en";
    applyLang();
    document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => { haptic(); setTab(b.dataset.tab); });
    $("#prem-btn").onclick = () => { haptic(); setTab("premium"); };
    if (!DEV && !(tg && tg.initData)) { $("#view").innerHTML = `<p class="warn">${T("open_in_tg")}</p>`; return; }
    try {
      await refreshSession();
      S.lang = S.session.user.lang || S.lang; applyLang();
      api("/api/vargas").then((v) => { S.vargas = v; }).catch(() => {});
      // Telegram puts tgWebAppData in the hash; only plain words are our own tab links (#daily, #channels…)
      const h = location.hash.replace("#", "");
      const start = (/^[a-z]+$/.test(h) && h) || (tg && tg.initDataUnsafe && tg.initDataUnsafe.start_param) || "chart";
      const main = S.session.profiles[0];
      if (main && start === "chart") { S.style = main.indian_style; await loadProfile(main.id); setTab("chart"); }
      else setTab(["chart", "synastry", "daily", "channels", "about", "premium"].includes(start) ? start : "chart");
    } catch (e) {
      $("#view").innerHTML = `<p class="warn">${T("err")}${esc(e.message)}</p>`;
    }
  }
  boot();
})();
