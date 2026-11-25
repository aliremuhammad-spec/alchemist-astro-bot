/* The Alchemist Astro — Telegram Mini App (vanilla JS, no build step). */
(() => {
  const tg = window.Telegram && window.Telegram.WebApp;
  const qs = new URLSearchParams(location.search);
  const DEV = qs.get("dev"); // local preview only (server must run with DEV_AUTH=1)

  /* ───────────── text ───────────── */
  const I18N = {
    ar: {
      brand: "الخيميائي", beta: "<b>نسخة تجريبية</b> · من تطوير الخيميائي", premium_btn: "✨ مميز",
      tab_chart: "خارطتي", tab_syn: "التوافق", tab_daily: "اليوم", tab_channels: "قنواتي", tab_about: "حول", tab_admin: "الإدارة",
      hero_title: "خارطتك كما كانت السماء لحظة ولادتك",
      hero_sub: "بالنظامين الغربي والفيدي، مع الرسم الهندي الشمالي أو الجنوبي.",
      new_chart: "خارطة جديدة", name: "الاسم", name_ph: "اسمك أو اسم صاحب الخارطة",
      date: "تاريخ الولادة", day: "اليوم", month: "الشهر", year: "السنة",
      time: "وقت الولادة", hour: "الساعة", minute: "الدقيقة", unknown_time: "لا أعرف وقت الولادة",
      unknown_note: "بنحسب الخارطة على الظهر، وبدون طالع وبيوت لأنها بتعتمد على الوقت بالدقيقة.",
      place: "مكان الولادة", continent: "القارة", country: "الدولة", city_ph: "ابحث عن مدينتك…",
      indian_style: "شكل الخارطة الهندية", north: "شمالي", south: "جنوبي", calc: "احسب الخارطة", calculating: "عم نحسب…",
      western: "غربية", vedic: "فيدية", send: "ابعتها عالمحادثة", sent: "بعتنا الخارطة عالمحادثة مع البوت",
      share: "شارك", del: "حذف", deleted: "انحذفت الخارطة", saved_charts: "خرائطك",
      limit: "الخطة المجانية بتحفظ {n} خرائط. الخارطة انحسبت بس ما انحفظت.",
      need_city: "اختار المدينة من القائمة", need_date: "التاريخ غير صحيح",
      big_sun: "الشمس", big_moon: "القمر", big_asc: "الطالع",
      planets: "الكواكب", sign: "البرج", house: "البيت", aspects: "الاتصالات", elements: "العناصر", modes: "الصفات",
      nak: "النكشترا", lagna: "اللغنا", moon_nak: "نكشترا القمر", dasha: "الدشا الحالية (فمشوتاري)",
      maha: "مها دشا", antar: "أنتار دشا", until: "حتى", timeline: "خط الدشا", full_text: "النص الكامل",
      applying: "يقترب", separating: "يبتعد", retro: "متراجع",
      varga: "الخريطة الفرعية", varga_lock: "الخرائط الفرعية من D2 لـ D60 للمشتركين المميزين (D9 مجانية).",
      syn_title: "التوافق بين خارطتين", syn_sub: "اختار خارطتين من خرائطك. الحساب مجاني مقابل فيديو إعلاني قصير.",
      syn_need: "لازم يكون عندك خارطتين محفوظتين. ضيف خارطة الشخص التاني من «خارطتي».",
      syn_a: "الشخص الأول", syn_b: "الشخص التاني", syn_go_ad: "شاهد إعلاناً واحسب التوافق", syn_go: "احسب التوافق",
      syn_same: "اختار شخصين مختلفين", ad_loading: "عم نحمّل الإعلان…", ad_closed: "انسكّر الإعلان قبل نهايته، جرّب مرة تانية.",
      ad_limit: "وصلت للحد اليومي، جرّب بكرا أو اشترك بالمميز.", score: "مؤشر التوافق",
      levels: { Minimal: "ضعيف", Medium: "متوسط", Important: "مهم", "Very Important": "مهم جداً", Exceptional: "استثنائي", "Rare Exceptional": "نادر" },
      sky_title: "سماء اليوم", sky_moon: "القمر في", sky_retro: "متراجعة الآن", sky_none: "ولا كوكب متراجع",
      daily_title: "برجك كل يوم بوقتك", daily_sub: "رسالة يومية من البوت بالوقت اللي بتختاره.",
      daily_on: "ابعتلي برجي كل يوم", send_time: "وقت الإرسال", tz: "المنطقة الزمنية", sign_pick: "البرج",
      sign_auto: "تلقائي من خارطتي", save: "احفظ", saved: "انحفظت الإعدادات",
      ch_title: "الأبراج اليومية لقناتك أو مجموعتك",
      ch_sub: "ضيف البوت، وكل يوم بينشر أبراج الـ12 برج كاملة بالوقت اللي بتختاره. مجاناً بالكامل.",
      add_channel: "أضف لقناة", add_group: "أضف لمجموعة",
      ch_steps: "بالقناة لازم يكون البوت مشرف مع صلاحية نشر الرسائل. بعد الإضافة بتظهر هون وبتقدر تغيّر وقت النشر.",
      my_chats: "قنواتك ومجموعاتك", no_chats: "لسا ما ضفت البوت لأي قناة أو مجموعة.", post_lang: "لغة النشر", active: "النشر مفعّل",
      about_title: "عن الخيميائي",
      about_body: "نسخة تجريبية (Beta) من بوت الخيميائي للفلك، من تطوير الخيميائي. الحسابات بمكتبة Swiss Ephemeris، والمحتوى للتأمل والترفيه.",
      follow: "تابعنا على إنستغرام", follow_main_sub: "الصفحة الرسمية للخيميائي", follow_partner_sub: "صفحة متعاونة",
      suggest_title: "اقتراح للتطوير", suggest_sub: "فكرتك أو ملاحظتك بتوصل مباشرة لحساب المطوّر.",
      suggest_ph: "شو الميزة اللي بتحب تشوفها؟ أو شو الشي اللي ما زبط معك؟", suggest_send: "ابعت الاقتراح",
      suggest_ok: "وصل اقتراحك للمطوّر، شكراً", source: "الكود المصدري", source_sub: "مفتوح المصدر بترخيص AGPL-3.0", ui_lang: "لغة الواجهة",
      prem_title: "الخيميائي المميز", prem_sub: "اشتراك شهري بالنجوم يفتح كل المزايا المتقدمة.",
      prem_active: "اشتراكك فعّال حتى ", prem_buy: "اشترك بـ {n} نجمة شهرياً", prem_paid: "تم الاشتراك، أهلاً بك بالمميز ✨",
      prem_perks: [["الخرائط الفرعية D2 لـ D60", "الهورا، الدريكانا، النافامشا، الداشامشا وكل الشودشافارغا"],
        ["التوافق بلا إعلانات", "احسب توافق ما بدك مع أي خارطة محفوظة"],
        ["ملفات غير محدودة", "احفظ خرائط العائلة والأصدقاء بدون حد"],
        ["قريباً للمشتركين", "العبور اليومي الشخصي، تنبيهات العبور، الاختيارات الأسبوعية، التوافق الفيدي (36 نقطة)، تقرير PDF"]],
      prem_manual: "ما عندك نجوم تلغرام؟ راسلنا على إنستغرام لطرق دفع تانية.",
      err: "صار خطأ: ", open_in_tg: "افتح التطبيق من داخل تلغرام عبر البوت.",
      months: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
      signs: ["الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء", "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت"],
      el: { fire: "نار", earth: "تراب", air: "هواء", water: "ماء" }, md: { cardinal: "كاردينال", fixed: "ثابت", mutable: "متحول" },
      ad_overview: "نظرة عامة", ad_users: "المستخدمين", ad_msg: "الرسائل", ad_content: "المحتوى", ad_fb: "الاقتراحات", ad_chats: "القنوات",
      k_users: "المستخدمين", k_new: "جدد اليوم", k_active: "نشطين 7 أيام", k_daily: "مشتركين بالأبراج", k_chats: "قنوات ومجموعات",
      k_charts: "خرائط محسوبة", k_syn: "توافقات", k_prem: "مميزين الآن", k_stars: "نجوم مدفوعة", k_blocked: "حظروا البوت",
      k_series: "آخر 14 يوم", k_newusers: "مستخدمين جدد", k_ads: "الإعلانات (30 يوم)", k_req: "طلبات", k_geo: "دول الولادة",
      k_tz: "المناطق الزمنية", k_lang: "اللغات", k_src: "مصادر الدخول", geo_note: "الموقع الحالي غير معروف؛ هاي دولة الولادة بالخارطة الرئيسية.",
      st: { completed: "مكتمل", nofill: "بدون إعلان متاح", skipped: "تخطّى", rejected_fast: "مرفوض (سريع)" },
      search_user: "ابحث بالرقم أو الاسم أو @username", premium_until: "مميز حتى", upgrade: "ترقية", days: "يوم", revoke: "إلغاء المميز",
      note: "ملاحظة (مثلاً: دفع بطريقة أخرى)", granted: "تمت الترقية", revoked: "تم إلغاء المميز", message_user: "راسله",
      msg_to: "إلى", msg_one: "مستخدم واحد (رقم)", msg_text: "نص الرسالة (يدعم <b> و <i> و <a>)", msg_send: "ارسل", msg_queued: "انضافت للإرسال: {n}",
      segs: { all: "الكل", ar: "العربية", en: "الإنجليزية", daily: "مشتركين بالأبراج", premium: "المميزين", free: "المجانيين", inactive7: "غير نشطين 7 أيام" },
      daily_url: "رابط ملف الأبراج اليومية (raw)", weekly_url: "رابط ملف الاختيارات الأسبوعية (raw)", price: "سعر الاشتراك (نجوم)",
      fetch_now: "اسحب الآن", today_ok: "أبراج اليوم موجودة", today_missing: "أبراج اليوم ناقصة", fetched_days: "آخر الأيام المسحوبة",
      reply: "رد", no_items: "لا يوجد شيء بعد", confirm_send: "رح تنبعت لـ «{n}». تأكيد؟",
    },
    en: {
      brand: "The Alchemist", beta: "<b>Beta</b> · developed by The Alchemist", premium_btn: "✨ Premium",
      tab_chart: "My chart", tab_syn: "Match", tab_daily: "Today", tab_channels: "Channels", tab_about: "About", tab_admin: "Admin",
      hero_title: "Your chart: the sky at the moment you were born", hero_sub: "Western and Vedic, with a North or South Indian chart.",
      new_chart: "New chart", name: "Name", name_ph: "Your name or the chart owner's",
      date: "Birth date", day: "Day", month: "Month", year: "Year",
      time: "Birth time", hour: "Hour", minute: "Minute", unknown_time: "I don't know the birth time",
      unknown_note: "We'll cast it for noon, without Ascendant and houses, which need the exact time.",
      place: "Birthplace", continent: "Continent", country: "Country", city_ph: "Search your city…",
      indian_style: "Indian chart style", north: "North", south: "South", calc: "Calculate chart", calculating: "Calculating…",
      western: "Western", vedic: "Vedic", send: "Send to chat", sent: "Chart sent to your chat with the bot",
      share: "Share", del: "Delete", deleted: "Chart deleted", saved_charts: "Your charts",
      limit: "Free plan keeps {n} charts. This one was calculated but not saved.",
      need_city: "Choose a city from the list", need_date: "Invalid date",
      big_sun: "Sun", big_moon: "Moon", big_asc: "Rising",
      planets: "Planets", sign: "Sign", house: "House", aspects: "Aspects", elements: "Elements", modes: "Modalities",
      nak: "Nakshatra", lagna: "Lagna", moon_nak: "Moon nakshatra", dasha: "Current dasha (Vimshottari)",
      maha: "Mahadasha", antar: "Antardasha", until: "until", timeline: "Dasha timeline", full_text: "Full text",
      applying: "applying", separating: "separating", retro: "retrograde",
      varga: "Divisional chart", varga_lock: "Divisional charts D2–D60 are for Premium members (D9 is free).",
      syn_title: "Compatibility of two charts", syn_sub: "Pick two saved charts. Free in exchange for a short video ad.",
      syn_need: "You need two saved charts. Add the other person's chart in My chart.",
      syn_a: "First person", syn_b: "Second person", syn_go_ad: "Watch an ad and compare", syn_go: "Compare charts",
      syn_same: "Pick two different people", ad_loading: "Loading the ad…", ad_closed: "The ad was closed early. Try again.",
      ad_limit: "Daily limit reached. Try tomorrow or go Premium.", score: "Compatibility score",
      levels: {},
      sky_title: "Today's sky", sky_moon: "Moon in", sky_retro: "Retrograde now", sky_none: "No planet retrograde",
      daily_title: "Your horoscope, daily, on your time", daily_sub: "A daily message from the bot at the time you choose.",
      daily_on: "Send me my horoscope every day", send_time: "Send at", tz: "Time zone", sign_pick: "Sign",
      sign_auto: "From my chart", save: "Save", saved: "Settings saved",
      ch_title: "Daily horoscopes for your channel or group",
      ch_sub: "Add the bot and it posts all 12 signs every day at the time you choose. Completely free.",
      add_channel: "Add to a channel", add_group: "Add to a group",
      ch_steps: "In channels the bot must be an admin allowed to post. After adding, it appears here and you can set the time.",
      my_chats: "Your channels and groups", no_chats: "You haven't added the bot anywhere yet.", post_lang: "Post language", active: "Posting on",
      about_title: "About The Alchemist",
      about_body: "A beta of The Alchemist astrology bot, developed by The Alchemist. Calculations use the Swiss Ephemeris; content is for reflection and entertainment.",
      follow: "Follow us on Instagram", follow_main_sub: "The Alchemist's official page", follow_partner_sub: "Partner page",
      suggest_title: "Suggest an improvement", suggest_sub: "Your idea goes straight to the developer's account.",
      suggest_ph: "What would you like to see? What didn't work?", suggest_send: "Send suggestion",
      suggest_ok: "Your suggestion reached the developer. Thanks", source: "Source code", source_sub: "Open source under AGPL-3.0", ui_lang: "Interface language",
      prem_title: "Alchemist Premium", prem_sub: "A monthly Stars subscription that unlocks every advanced feature.",
      prem_active: "Your subscription is active until ", prem_buy: "Subscribe for {n} Stars a month", prem_paid: "You're Premium now ✨",
      prem_perks: [["Divisional charts D2–D60", "Hora, Drekkana, Navamsha, Dashamsha and the full Shodashavarga"],
        ["Ad-free compatibility", "Compare any saved charts, as often as you like"],
        ["Unlimited profiles", "Save family and friends without a limit"],
        ["Coming for members", "Personal daily transits, transit alerts, weekly electional dates, Vedic 36-point matching, PDF report"]],
      prem_manual: "No Telegram Stars? Message us on Instagram for other payment options.",
      err: "Error: ", open_in_tg: "Open the app from inside Telegram via the bot.",
      months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      signs: ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
      el: { fire: "Fire", earth: "Earth", air: "Air", water: "Water" }, md: { cardinal: "Cardinal", fixed: "Fixed", mutable: "Mutable" },
      ad_overview: "Overview", ad_users: "Users", ad_msg: "Messages", ad_content: "Content", ad_fb: "Feedback", ad_chats: "Channels",
      k_users: "Users", k_new: "New today", k_active: "Active 7 days", k_daily: "Daily subscribers", k_chats: "Channels & groups",
      k_charts: "Charts cast", k_syn: "Synastries", k_prem: "Premium now", k_stars: "Stars paid", k_blocked: "Blocked the bot",
      k_series: "Last 14 days", k_newusers: "New users", k_ads: "Ads (30 days)", k_req: "requests", k_geo: "Birth countries",
      k_tz: "Time zones", k_lang: "Languages", k_src: "Sources", geo_note: "Current location is unknown; this is the birth country of the main chart.",
      st: { completed: "completed", nofill: "no fill", skipped: "skipped", rejected_fast: "rejected (too fast)" },
      search_user: "Search by id, name or @username", premium_until: "Premium until", upgrade: "Upgrade", days: "days", revoke: "Revoke premium",
      note: "Note (e.g. paid another way)", granted: "Upgraded", revoked: "Premium revoked", message_user: "Message",
      msg_to: "To", msg_one: "One user (id)", msg_text: "Message (supports <b>, <i>, <a>)", msg_send: "Send", msg_queued: "Queued: {n}",
      segs: { all: "Everyone", ar: "Arabic", en: "English", daily: "Daily subscribers", premium: "Premium", free: "Free", inactive7: "Inactive 7 days" },
      daily_url: "Daily horoscope file URL (raw)", weekly_url: "Weekly electional file URL (raw)", price: "Subscription price (Stars)",
      fetch_now: "Fetch now", today_ok: "Today's horoscopes are in", today_missing: "Today's horoscopes are missing", fetched_days: "Latest fetched days",
      reply: "Reply", no_items: "Nothing yet", confirm_send: "Send to “{n}”? Confirm?",
    },
  };
  const GLYPHS = [..."♈♉♊♋♌♍♎♏♐♑♒♓"].map((g) => g + "︎");
  const PL = {
    sun: ["☉", "الشمس", "Sun"], moon: ["☽", "القمر", "Moon"], mercury: ["☿", "عطارد", "Mercury"], venus: ["♀", "الزهرة", "Venus"],
    mars: ["♂", "المريخ", "Mars"], jupiter: ["♃", "المشتري", "Jupiter"], saturn: ["♄", "زحل", "Saturn"], uranus: ["♅", "أورانوس", "Uranus"],
    neptune: ["♆", "نبتون", "Neptune"], pluto: ["♇", "بلوتو", "Pluto"], mean_north_lunar_node: ["☊", "العقدة الشمالية", "N. Node"],
    mean_south_lunar_node: ["☋", "كيتو", "Ketu"], chiron: ["⚷", "كايرون", "Chiron"], ascendant: ["AC", "الطالع", "Asc"], medium_coeli: ["MC", "وسط السماء", "MC"],
  };
  const VNAME = { mean_north_lunar_node: ["راهو", "Rahu"], mean_south_lunar_node: ["كيتو", "Ketu"] };
  const ASP = { conjunction: ["☌", "اقتران", "Conjunction"], opposition: ["☍", "مقابلة", "Opposition"], trine: ["△", "تثليث", "Trine"],
    square: ["□", "تربيع", "Square"], sextile: ["⚹", "تسديس", "Sextile"] };
  const DASHA = { ketu: ["كيتو", "Ketu"], venus: ["الزهرة", "Venus"], sun: ["الشمس", "Sun"], moon: ["القمر", "Moon"], mars: ["المريخ", "Mars"],
    rahu: ["راهو", "Rahu"], jupiter: ["المشتري", "Jupiter"], saturn: ["زحل", "Saturn"], mercury: ["عطارد", "Mercury"] };
  const PHASES = { "New Moon": "محاق", "Waxing Crescent": "هلال متزايد", "First Quarter": "تربيع أول", "Waxing Gibbous": "أحدب متزايد",
    "Full Moon": "بدر", "Waning Gibbous": "أحدب متناقص", "Last Quarter": "تربيع أخير", "Third Quarter": "تربيع أخير", "Waning Crescent": "هلال متناقص" };

  const S = { lang: "ar", theme: "dark", session: null, tab: "chart", chart: null, profileId: null, system: "western", style: "north",
              form: {}, editing: false, varga: 1, vargaSvg: null, vargas: null, adminTab: "overview" };
  const $ = (sel, el = document) => el.querySelector(sel);
  const T = (k) => I18N[S.lang][k] ?? I18N.ar[k] ?? k;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const haptic = (t = "light") => { try { tg.HapticFeedback.impactOccurred(t); } catch (e) {} };
  const pn = (k) => (PL[k] ? PL[k][S.lang === "ar" ? 1 : 2] : k);
  const vn = (k) => (VNAME[k] ? VNAME[k][S.lang === "ar" ? 0 : 1] : pn(k));
  const sn = (i) => T("signs")[i];
  const deg = (d) => { let a = Math.floor(d), m = Math.round((d - a) * 60); if (m === 60) { a += 1; m = 0; } return `<span class="num">${a}°${String(m).padStart(2, "0")}′</span>`; };
  const fmtNum = (n) => Number(n || 0).toLocaleString("en-US");

  function toast(msg) {
    const el = $("#toast"); el.textContent = msg; el.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(() => el.classList.remove("show"), 2800);
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
  const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body || {}) });

  function openLink(url) { if (tg && tg.openLink) tg.openLink(url); else window.open(url, "_blank"); }
  function openTg(url) { if (tg && tg.openTelegramLink) tg.openTelegramLink(url); else window.open(url, "_blank"); }
  function countryName(iso) { try { return new Intl.DisplayNames([S.lang], { type: "region" }).of(iso); } catch (e) { return iso; } }
  const skeleton = (n = 3) => `<div class="skel" aria-hidden="true">${"<div></div>".repeat(n)}</div>`;

  function applyLang() {
    document.documentElement.lang = S.lang;
    document.documentElement.dir = S.lang === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-t]").forEach((el) => { el.innerHTML = T(el.dataset.t); });
  }

  /* ───────────── tabs ───────────── */
  const VIEWS = {};
  function setTab(tab) {
    if (!VIEWS[tab]) tab = "chart";
    S.tab = tab;
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === tab));
    $("#prem-btn").classList.toggle("on", tab === "premium");
    const v = $("#view"); v.classList.remove("enter"); void v.offsetWidth; v.classList.add("enter");
    VIEWS[tab]();
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
    return `<div class="chips">${ps.map((p) =>
      `<button class="chip" data-pid="${p.id}" aria-pressed="${p.id === S.profileId && !S.editing}">${esc(p.name)}</button>`).join("")}
      <button class="chip add" data-new aria-pressed="${S.editing}">+ ${T("new_chart")}</button></div>`;
  }

  VIEWS.chart = function renderChart() {
    const v = $("#view");
    const showForm = S.editing || !S.chart;
    const first = !S.session.profiles.length;
    v.innerHTML = `${profileChips()}
      ${S.chart && !S.editing ? chartView() : ""}
      ${showForm ? (first ? `${zodiacRing()}<h2 class="hero-title">${T("hero_title")}</h2><p class="muted center">${T("hero_sub")}</p>` : "") + formView() : ""}`;
    v.querySelectorAll("[data-pid]").forEach((b) => b.onclick = () => loadProfile(+b.dataset.pid));
    const nb = v.querySelector("[data-new]"); if (nb) nb.onclick = () => { S.editing = true; VIEWS.chart(); };
    if (showForm) bindForm(); else bindChart();
  };

  function formView() {
    const f = S.form; const y = new Date().getFullYear();
    const opts = (from, to, sel, labels, pad) => Array.from({ length: to - from + 1 }, (_, i) => from + i)
      .map((n) => `<option value="${n}" ${n == sel ? "selected" : ""}>${labels ? labels[n - 1] : pad ? String(n).padStart(2, "0") : n}</option>`).join("");
    return `<form id="cf" class="card form" novalidate>
      <label for="f-name">${T("name")}</label><input id="f-name" maxlength="60" placeholder="${T("name_ph")}" value="${esc(f.name || (S.session.profiles.length ? "" : S.session.user.first_name) || "")}">
      <label>${T("date")}</label>
      <div class="grid3">
        <select id="f-day" aria-label="${T("day")}">${opts(1, 31, f.day || 1)}</select>
        <select id="f-month" aria-label="${T("month")}">${opts(1, 12, f.month || 1, T("months"))}</select>
        <select id="f-year" aria-label="${T("year")}">${Array.from({ length: y - 1899 }, (_, i) => y - i).map((n) => `<option value="${n}" ${n == (f.year || 1995) ? "selected" : ""}>${n}</option>`).join("")}</select>
      </div>
      <label>${T("time")}</label>
      <div class="grid2" id="time-row" ${f.unknown ? "hidden" : ""}>
        <select id="f-hour" aria-label="${T("hour")}">${opts(0, 23, f.hour ?? 12, null, true)}</select>
        <select id="f-min" aria-label="${T("minute")}">${opts(0, 59, f.minute ?? 0, null, true)}</select>
      </div>
      <label class="switch"><input type="checkbox" id="f-unknown" ${f.unknown ? "checked" : ""}> ${T("unknown_time")}</label>
      <p class="muted small" id="unknown-note" ${f.unknown ? "" : "hidden"}>${T("unknown_note")}</p>
      <label>${T("place")}</label>
      <div class="grid2">
        <select id="f-cont" aria-label="${T("continent")}"><option value="">${T("continent")}</option></select>
        <select id="f-country" aria-label="${T("country")}" disabled><option value="">${T("country")}</option></select>
      </div>
      <input id="f-city" placeholder="${T("city_ph")}" autocomplete="off" disabled class="mt8">
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
      list.classList.toggle("open", rows.length > 0);
    };
    cont.onchange = async () => {
      country.disabled = !cont.value; city.disabled = true; list.innerHTML = ""; list.classList.remove("open");
      if (!cont.value) return;
      const cs = await api(`/api/geo/countries?continent=${cont.value}`);
      cs.forEach((c) => c.local = countryName(c.iso));
      cs.sort((a, b) => a.local.localeCompare(b.local, S.lang));
      country.innerHTML = `<option value="">${T("country")}</option>` + cs.map((c) => `<option value="${c.iso}">${esc(c.local)}</option>`).join("");
    };
    country.onchange = () => { f.city_id = null; city.value = ""; city.disabled = !country.value; loadCities(); };
    city.oninput = () => { f.city_id = null; clearTimeout(cityTimer); cityTimer = setTimeout(loadCities, 250); };
    city.onfocus = () => { if (country.value && !f.city_id) loadCities(); };
    list.onclick = (e) => {
      const b = e.target.closest("button[data-id]"); if (!b) return;
      f.city_id = +b.dataset.id; f.country = country.value;
      city.value = b.querySelector("span").textContent;
      list.querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", x === b));
      list.classList.remove("open"); haptic();
    };
    $("#cf").onsubmit = async (e) => {
      e.preventDefault();
      Object.assign(f, { name: $("#f-name").value.trim(), day: +$("#f-day").value, month: +$("#f-month").value, year: +$("#f-year").value,
        hour: +$("#f-hour").value, minute: +$("#f-min").value, unknown: unk.checked });
      const d = new Date(f.year, f.month - 1, f.day);
      if (d.getMonth() !== f.month - 1) return toast(T("need_date"));
      if (!f.city_id) return toast(T("need_city"));
      const go = $("#f-go"); go.disabled = true; go.innerHTML = `<span class="spinner"></span> ${T("calculating")}`;
      try {
        const res = await post("/api/chart", { name: f.name, day: f.day, month: f.month, year: f.year, hour: f.hour, minute: f.minute,
          time_known: !f.unknown, country: f.country, city_id: f.city_id, indian_style: S.style, theme: S.theme, lang: S.lang, save: true });
        if (S.session.meta.chart_ad && !S.session.premium && window.Ads) {
          try { await window.Ads.watch("chart", S.session.meta.ads || {}, api); } catch (e) { /* the chart is free either way */ }
        }
        S.chart = res; S.profileId = res.profile_id; S.editing = false; S.system = "western"; S.varga = 1; S.vargaSvg = null; S.form = {};
        if (res.profile_limit_hit) toast(T("limit").replace("{n}", S.session.meta.free_profiles));
        await refreshSession(); haptic("medium"); VIEWS.chart();
      } catch (err) { toast(T("err") + err.message); go.disabled = false; go.textContent = T("calc"); }
    };
  }

  function bigThree(c) {
    const w = c.western.points, items = [["big_sun", w.sun], ["big_moon", w.moon]];
    if (c.western.asc) items.push(["big_asc", c.western.asc]);
    return `<div class="big3">${items.map(([k, p]) => `<div><span class="g">${GLYPHS[p.sign]}</span><b>${sn(p.sign)}</b><small>${T(k)}</small></div>`).join("")}</div>`;
  }

  function bars(obj, labels) {
    return `<div class="bars">${Object.entries(obj).map(([k, v]) => `<div class="bar"><span>${labels[k]}</span><i style="--v:${v}%"></i><b class="num">${v}%</b></div>`).join("")}</div>`;
  }

  function westernDetails(c) {
    const w = c.western;
    const rows = Object.entries(w.points).map(([k, p]) => `<tr><td><span class="pg">${PL[k][0]}</span>${pn(k)}</td>
      <td>${GLYPHS[p.sign]} ${sn(p.sign)} ${deg(p.deg)}</td><td class="num">${p.house || "—"}</td><td>${p.retro && !k.includes("node") ? `<span class="rx" title="${T("retro")}">℞</span>` : ""}</td></tr>`).join("");
    const angles = w.asc ? `<tr class="angle"><td><span class="pg">AC</span>${pn("ascendant")}</td><td>${GLYPHS[w.asc.sign]} ${sn(w.asc.sign)} ${deg(w.asc.deg)}</td><td></td><td></td></tr>
      <tr class="angle"><td><span class="pg">MC</span>${pn("medium_coeli")}</td><td>${GLYPHS[w.mc.sign]} ${sn(w.mc.sign)} ${deg(w.mc.deg)}</td><td></td><td></td></tr>` : "";
    const asp = w.aspects.filter((a) => a.major).slice(0, 18).map((a) => `<li><span>${pn(a.p1)}</span><b class="ag ag-${a.type}">${ASP[a.type][0]}</b><span>${pn(a.p2)}</span>
      <small>${ASP[a.type][S.lang === "ar" ? 1 : 2]} · <span class="num">${a.orb.toFixed(1)}°</span> · ${a.applying ? T("applying") : T("separating")}</small></li>`).join("");
    const ph = w.moon_phase;
    return `<section class="card"><h3>${T("planets")}</h3><table class="tbl"><thead><tr><th></th><th>${T("sign")}</th><th>${T("house")}</th><th></th></tr></thead><tbody>${angles}${rows}</tbody></table></section>
      <section class="card"><h3>${T("aspects")}</h3><ul class="asp">${asp}</ul></section>
      <section class="card two"><div><h3>${T("elements")}</h3>${bars(w.elements, T("el"))}</div><div><h3>${T("modes")}</h3>${bars(w.qualities, T("md"))}</div></section>
      <p class="phase">${ph.emoji} ${S.lang === "ar" ? PHASES[ph.name] || ph.name : ph.name}</p>`;
  }

  function vedicDetails(c) {
    const v = c.vedic;
    const dn = (l) => DASHA[l][S.lang === "ar" ? 0 : 1];
    const nk = (n) => `${S.lang === "ar" ? n.name_ar : n.name} <small class="muted">· ${S.lang === "ar" ? "بادا" : "pada"} ${n.pada}</small>`;
    const rows = Object.entries(v.points).map(([k, p]) => `<tr><td>${vn(k)}</td><td>${GLYPHS[p.sign]} ${sn(p.sign)} ${deg(p.deg)}${p.retro && !k.includes("node") ? ' <span class="rx">℞</span>' : ""}</td>
      <td class="num">${p.house || "—"}</td><td>${nk(p.nakshatra)}</td></tr>`).join("");
    const lag = v.lagna ? `<tr class="angle"><td>${T("lagna")}</td><td>${GLYPHS[v.lagna.sign]} ${sn(v.lagna.sign)} ${deg(v.lagna.deg)}</td><td></td><td>${nk(v.lagna.nakshatra)}</td></tr>` : "";
    const d = v.dasha, now = new Date().toISOString().slice(0, 10);
    const tl = d.timeline.slice(0, 9).map((p) => `<li class="${p.start <= now && now < p.end ? "now" : ""}"><b>${dn(p.lord)}</b><span class="num">${p.start.slice(0, 4)}–${p.end.slice(0, 4)}</span></li>`).join("");
    return `<section class="card"><h3>${T("planets")}</h3><div class="scrollx"><table class="tbl"><thead><tr><th></th><th>${T("sign")}</th><th>${T("house")}</th><th>${T("nak")}</th></tr></thead><tbody>${lag}${rows}</tbody></table></div></section>
      <section class="card dasha"><h3>${T("dasha")}</h3>
        <div class="dnow"><div><small>${T("maha")}</small><b>${dn(d.maha.lord)}</b><span class="muted small">${T("until")} <span class="num">${d.maha.end}</span></span></div>
        ${d.antar ? `<div><small>${T("antar")}</small><b>${dn(d.antar.lord)}</b><span class="muted small">${T("until")} <span class="num">${d.antar.end}</span></span></div>` : ""}</div>
        <h4>${T("timeline")}</h4><ol class="tl">${tl}</ol>
        <p class="muted small">${T("moon_nak")}: ${nk(v.moon_nakshatra)}</p></section>`;
  }

  function chartView() {
    const c = S.chart, m = c.meta;
    const place = [m.city, countryName(m.country)].filter(Boolean).join("، ");
    const warn = !m.time_known ? `<p class="warn">${T("unknown_note")}</p>` : "";
    const ved = S.system === "vedic";
    return `<section class="stage">
      <p class="name">${esc(m.name)}</p><p class="when"><span class="num">${esc(m.local)}</span> · ${esc(place)}</p>
      ${bigThree(c)}
      <div class="row between">
        <div class="seg" id="sys"><button data-v="western" aria-pressed="${!ved}">${T("western")}</button><button data-v="vedic" aria-pressed="${ved}">${T("vedic")}</button></div>
        <div class="seg" id="sty" ${ved ? "" : "hidden"}><button data-v="north" aria-pressed="${S.style === "north"}">${T("north")}</button><button data-v="south" aria-pressed="${S.style === "south"}">${T("south")}</button></div>
      </div>
      ${ved && S.profileId ? `<select id="varga" class="mt8" aria-label="${T("varga")}">${vargaOptions()}</select>` : ""}
      <div id="svg" class="wheel">${ved ? (S.vargaSvg || c.svg.indian) : c.svg.western}</div>
    </section>
    ${warn}
    ${ved ? vedicDetails(c) : westernDetails(c)}
    <details class="card"><summary>${T("full_text")}</summary><div class="report">${ved ? c.text.vedic : c.text.western}</div></details>
    <div class="actions">
      ${S.profileId ? `<button class="btn" id="send">${T("send")}</button>` : ""}
      <button class="btn ghost" id="share">${T("share")}</button>
      ${S.profileId ? `<button class="btn ghost danger" id="del">${T("del")}</button>` : ""}
    </div>`;
  }

  function vargaOptions() {
    const prem = S.session.premium;
    return (S.vargas || [{ n: 1, name: "Rashi", ar: "الراشي" }]).map((v) =>
      `<option value="${v.n}" ${v.n === S.varga ? "selected" : ""}>${v.n === 1 || v.n === 9 || prem ? "" : "🔒 "}D${v.n} · ${esc(S.lang === "ar" ? v.ar : v.name)}</option>`).join("");
  }

  async function loadVarga(n) {
    if (n === 1) { S.varga = 1; S.vargaSvg = null; return VIEWS.chart(); }
    if (n !== 9 && !S.session.premium) { toast(T("varga_lock")); $("#varga").value = String(S.varga); return; }
    try {
      const r = await api(`/api/profiles/${S.profileId}/varga/${n}?style=${S.style}&theme=${S.theme}&lang=${S.lang}`);
      S.varga = n; S.vargaSvg = r.svg; VIEWS.chart();
    } catch (e) { toast(T("err") + e.message); }
  }

  function bindChart() {
    const vs = $("#varga"); if (vs) vs.onchange = () => loadVarga(+vs.value);
    $("#sys").onclick = (e) => { const b = e.target.closest("button"); if (!b) return; S.system = b.dataset.v; haptic(); VIEWS.chart(); };
    $("#sty").onclick = async (e) => {
      const b = e.target.closest("button"); if (!b || b.dataset.v === S.style) return;
      S.style = b.dataset.v; haptic(); if (S.profileId) await loadProfile(S.profileId, true);
    };
    const send = $("#send");
    if (send) send.onclick = async () => {
      send.disabled = true; send.innerHTML = `<span class="spinner"></span>`;
      try { await post(`/api/profiles/${S.profileId}/send`, { lang: S.lang, style: S.style }); toast(T("sent")); haptic("medium"); }
      catch (e) { toast(T("err") + e.message); }
      send.disabled = false; send.textContent = T("send");
    };
    $("#share").onclick = () => {
      const url = `https://t.me/${S.session.meta.bot}`;
      const text = S.lang === "ar" ? "احسب خارطتك الفلكية الغربية والفيدية مجاناً مع بوت الخيميائي ✨" : "Cast your Western & Vedic birth chart for free ✨";
      openTg(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`);
    };
    const del = $("#del");
    if (del) del.onclick = async () => {
      if (del.dataset.armed !== "1") { del.dataset.armed = "1"; del.textContent = T("del") + " ؟"; setTimeout(() => { del.dataset.armed = ""; del.textContent = T("del"); }, 3000); return; }
      await api(`/api/profiles/${S.profileId}`, { method: "DELETE" });
      S.chart = null; S.profileId = null; await refreshSession(); toast(T("deleted")); VIEWS.chart();
    };
  }

  async function loadProfile(pid, keepSystem) {
    try {
      if (!keepSystem) { S.profileId = pid; $("#view").innerHTML = profileChips() + skeleton(4); }
      const p = S.session.profiles.find((x) => x.id === pid);
      if (!keepSystem && p) S.style = p.indian_style;
      S.chart = await api(`/api/profiles/${pid}/chart?style=${S.style}&theme=${S.theme}&lang=${S.lang}`);
      S.profileId = pid; S.editing = false;
      if (!keepSystem) { S.system = "western"; S.varga = 1; S.vargaSvg = null; }
      else if (S.varga && S.varga !== 1) { const n = S.varga; S.varga = 1; S.vargaSvg = null; VIEWS.chart(); return loadVarga(n); }
      if (S.tab === "chart") VIEWS.chart();
    } catch (e) { toast(T("err") + e.message); }
  }

  /* ───────────── synastry tab ───────────── */
  VIEWS.synastry = function renderSynastry() {
    const ps = S.session.profiles;
    if (ps.length < 2) {
      $("#view").innerHTML = `<h2>${T("syn_title")}</h2><p class="muted">${T("syn_need")}</p><button class="btn" id="go-chart">+ ${T("new_chart")}</button>`;
      $("#go-chart").onclick = () => { S.editing = true; setTab("chart"); };
      return;
    }
    const opt = (sel) => ps.map((p) => `<option value="${p.id}" ${p.id === sel ? "selected" : ""}>${esc(p.name)} · ${p.birth_date}</option>`).join("");
    const prem = S.session.premium;
    $("#view").innerHTML = `<h2>${T("syn_title")}</h2>${prem ? "" : `<p class="muted">${T("syn_sub")}</p>`}
      <div class="card form"><label for="sa">${T("syn_a")}</label><select id="sa">${opt(S.synA || ps[0].id)}</select>
      <label for="sb">${T("syn_b")}</label><select id="sb">${opt(S.synB || ps[1].id)}</select>
      <button class="btn block" id="syn-go">${prem ? T("syn_go") : T("syn_go_ad")}</button></div>
      <div id="syn-out">${S.synResult ? synView(S.synResult) : ""}</div>`;
    $("#syn-go").onclick = runSynastry;
  };

  function synView(r) {
    const pct = Math.min(100, Math.round((r.score.value / 20) * 100));
    const lvl = (T("levels") || {})[r.score.level] || r.score.level;
    const asp = r.aspects.slice(0, 16).map((a) => `<li><span>${pn(a.a)}</span><b class="ag ag-${a.type}">${ASP[a.type][0]}</b><span>${pn(a.b)}</span>
      <small>${ASP[a.type][S.lang === "ar" ? 1 : 2]} · <span class="num">${a.orb.toFixed(1)}°</span></small></li>`).join("");
    return `<section class="stage mt16"><p class="name">${esc(r.names[0])} · ${esc(r.names[1])}</p>
      <div class="scorebox"><div class="ring" style="--p:${pct}"><b class="num">${r.score.value}</b></div><div><b>${esc(lvl)}</b><small class="muted">${T("score")}</small></div></div>
      <div class="wheel">${r.svg}</div></section>
      <section class="card"><h3>${T("aspects")}</h3><ul class="asp">${asp}</ul></section>
      <details class="card"><summary>${T("full_text")}</summary><div class="report">${r.text}</div></details>`;
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
      S.synResult = await post("/api/synastry", { a, b, ticket, theme: S.theme, lang: S.lang });
      haptic("medium"); VIEWS.synastry();
      setTimeout(() => { const o = $("#syn-out"); if (o) o.scrollIntoView({ behavior: "smooth" }); }, 50);
    } catch (e) {
      const msg = window.Ads && e instanceof window.Ads.AdSkipped ? T("ad_closed") : /limit/.test(e.message) ? T("ad_limit") : T("err") + e.message;
      toast(msg); btn.disabled = false; btn.textContent = S.session.premium ? T("syn_go") : T("syn_go_ad");
    }
  }

  /* ───────────── today tab ───────────── */
  async function skyCard() {
    try {
      const s = await api("/api/sky");
      const m = s.points.moon, nk = s.moon_nakshatra;
      const retro = s.retrograde.length ? s.retrograde.map((k) => `<span class="pill">${PL[k][0]} ${pn(k)}</span>`).join("") : `<span class="muted small">${T("sky_none")}</span>`;
      return `<section class="card sky"><h3>${T("sky_title")}</h3>
        <div class="skyrow"><div class="moonbig" aria-hidden="true">${s.moon_phase.emoji}</div><div><small class="muted">${T("sky_moon")}</small>
        <b>${GLYPHS[m.sign]} ${sn(m.sign)} ${deg(m.deg)}</b><span class="muted small">${S.lang === "ar" ? PHASES[s.moon_phase.name] || "" : s.moon_phase.name} · ${S.lang === "ar" ? nk.name_ar : nk.name}</span></div></div>
        <small class="muted">${T("sky_retro")}</small><div class="pills">${retro}</div></section>`;
    } catch (e) { return ""; }
  }

  VIEWS.daily = async function renderDaily() {
    const d = S.session.daily || {};
    const tz = d.tz || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Damascus";
    $("#view").innerHTML = skeleton(3);
    const [sky, tzs] = await Promise.all([skyCard(), api("/api/timezones")]);
    if (S.tab !== "daily") return;
    const tzOk = tzs.includes(tz) ? tz : "Asia/Damascus";
    const hasProfile = S.session.profiles.length > 0;
    $("#view").innerHTML = `${sky}<h2>${T("daily_title")}</h2><p class="muted">${T("daily_sub")}</p>
      <div class="card form"><label class="switch"><input type="checkbox" id="d-on" ${d.subscribed !== false ? "checked" : ""}> ${T("daily_on")}</label>
      <div class="grid2"><div><label for="d-time">${T("send_time")}</label><input type="time" id="d-time" value="${d.send_time || "08:00"}"></div>
      <div><label for="d-sign">${T("sign_pick")}</label><select id="d-sign">${hasProfile ? `<option value="">${T("sign_auto")}</option>` : ""}
        ${T("signs").map((s, i) => `<option value="${i}" ${d.sign === i ? "selected" : ""}>${GLYPHS[i]} ${s}</option>`).join("")}</select></div></div>
      <label for="d-tz">${T("tz")}</label><select id="d-tz">${tzs.map((z) => `<option ${z === tzOk ? "selected" : ""}>${z}</option>`).join("")}</select>
      <button class="btn block" id="d-save">${T("save")}</button></div>`;
    $("#d-save").onclick = async () => {
      const sign = $("#d-sign").value;
      try {
        S.session.daily = await post("/api/daily", { subscribed: $("#d-on").checked, send_time: $("#d-time").value || "08:00",
          tz: $("#d-tz").value, sign: sign === "" ? null : +sign });
        toast(T("saved")); haptic("medium");
      } catch (e) { toast(T("err") + e.message); }
    };
  };

  /* ───────────── channels tab ───────────── */
  VIEWS.channels = async function renderChannels() {
    const m = S.session.meta;
    $("#view").innerHTML = `<section class="card promo"><h2>${T("ch_title")}</h2><p class="muted">${T("ch_sub")}</p>
      <div class="row"><button class="btn" id="c-add">📢 ${T("add_channel")}</button><button class="btn ghost" id="g-add">👥 ${T("add_group")}</button></div>
      <p class="muted small">${T("ch_steps")}</p></section><h3>${T("my_chats")}</h3><div class="list" id="chats">${skeleton(2)}</div>`;
    $("#c-add").onclick = () => openTg(m.add_channel);
    $("#g-add").onclick = () => openTg(m.add_group);
    const [chats, tzs] = await Promise.all([api("/api/channels"), api("/api/timezones")]);
    const box = $("#chats"); if (!box) return;
    if (!chats.length) { box.innerHTML = `<p class="muted">${T("no_chats")}</p>`; return; }
    box.innerHTML = chats.map((c) => `<div class="card" data-chat="${c.chat_id}"><h4>${esc(c.title || c.chat_id)}</h4>
      <div class="grid2"><input type="time" value="${c.send_time}" data-k="send_time" aria-label="${T("send_time")}">
      <select data-k="lang" aria-label="${T("post_lang")}"><option value="ar" ${c.lang === "ar" ? "selected" : ""}>العربية</option><option value="en" ${c.lang === "en" ? "selected" : ""}>English</option></select></div>
      <select data-k="tz" class="mt8" aria-label="${T("tz")}">${tzs.map((z) => `<option ${z === c.tz ? "selected" : ""}>${z}</option>`).join("")}</select>
      <label class="switch"><input type="checkbox" data-k="active" ${c.active ? "checked" : ""}> ${T("active")}</label>
      <button class="btn small mt8" data-save>${T("save")}</button></div>`).join("");
    box.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
      const it = b.closest("[data-chat]"), g = (k) => it.querySelector(`[data-k="${k}"]`);
      try { await post(`/api/channels/${it.dataset.chat}`, { send_time: g("send_time").value, tz: g("tz").value, lang: g("lang").value, active: g("active").checked }); toast(T("saved")); }
      catch (e) { toast(T("err") + e.message); }
    });
  };

  /* ───────────── about tab ───────────── */
  VIEWS.about = function renderAbout() {
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
      try { await post("/api/feedback", { text }); $("#fb").value = ""; toast(T("suggest_ok")); haptic("medium"); }
      catch (e) { toast(T("err") + e.message); }
      b.disabled = false;
    };
    $("#lang").onclick = async (e) => {
      const b = e.target.closest("button"); if (!b) return;
      S.lang = b.dataset.v; applyLang(); VIEWS.about();
      post("/api/lang", { lang: S.lang }).catch(() => {});
      if (S.profileId) api(`/api/profiles/${S.profileId}/chart?style=${S.style}&theme=${S.theme}&lang=${S.lang}`).then((c) => { S.chart = c; }).catch(() => {});
    };
  };

  /* ───────────── premium ───────────── */
  VIEWS.premium = async function renderPremium() {
    $("#view").innerHTML = skeleton(4);
    const info = await api("/api/premium");
    if (S.tab !== "premium") return;
    const perks = T("prem_perks").map(([b, s], i) => `<li class="${i === 3 ? "soon" : ""}"><b>${b}</b><span>${s}</span></li>`).join("");
    $("#view").innerHTML = `<section class="prem-hero"><div class="star" aria-hidden="true">✦</div><h2>${T("prem_title")}</h2><p class="muted">${T("prem_sub")}</p></section>
      <ul class="perks">${perks}</ul>
      ${info.active ? `<p class="warn ok">${T("prem_active")}<span class="num">${info.until.slice(0, 10)}</span></p>`
                    : `<button class="btn block big" id="buy">⭐ ${T("prem_buy").replace("{n}", info.stars)}</button>`}
      <p class="muted small mt16">${T("prem_manual")}</p>`;
    const buy = $("#buy");
    if (buy) buy.onclick = async () => {
      buy.disabled = true;
      try {
        const { link } = await post("/api/premium/invoice");
        const done = (status) => {
          buy.disabled = false;
          if (status === "paid") { toast(T("prem_paid")); haptic("heavy"); setTimeout(async () => { await refreshSession(); VIEWS.premium(); }, 1500); }
        };
        if (tg && tg.openInvoice) tg.openInvoice(link, done); else { openTg(link); buy.disabled = false; }
      } catch (e) { toast(T("err") + e.message); buy.disabled = false; }
    };
  };

  /* ───────────── admin dashboard ───────────── */
  const ADMIN_TABS = ["overview", "users", "msg", "content", "fb", "chats"];
  VIEWS.admin = function renderAdmin() {
    if (!S.session.is_admin) return setTab("chart");
    $("#view").innerHTML = `<div class="subnav">${ADMIN_TABS.map((t) => `<button data-a="${t}" aria-pressed="${S.adminTab === t}">${T("ad_" + t)}</button>`).join("")}</div><div id="admin">${skeleton(4)}</div>`;
    $("#view").querySelectorAll("[data-a]").forEach((b) => b.onclick = () => { S.adminTab = b.dataset.a; haptic(); VIEWS.admin(); });
    ({ overview: adOverview, users: adUsers, msg: adMsg, content: adContent, fb: adFeedback, chats: adChats })[S.adminTab]()
      .catch((e) => { const a = $("#admin"); if (a) a.innerHTML = `<p class="warn">${T("err")}${esc(e.message)}</p>`; });
  };

  const kpi = (n, label) => `<div class="kpi"><b class="num">${fmtNum(n)}</b><small>${label}</small></div>`;
  function listBars(rows, key, labelFn) {
    const max = Math.max(1, ...rows.map((r) => r.n));
    return rows.length ? `<div class="bars">${rows.map((r) => `<div class="bar"><span>${esc(labelFn ? labelFn(r[key]) : r[key])}</span><i style="--v:${(r.n / max) * 100}%"></i><b class="num">${r.n}</b></div>`).join("")}</div>`
      : `<p class="muted small">${T("no_items")}</p>`;
  }
  function seriesChart(series) {
    const W = 320, H = 122, max = Math.max(1, ...series.map((d) => d.users)), bw = W / series.length;
    const rects = series.map((d, i) => { const h = (d.users / max) * (H - 38);
      return `<rect x="${i * bw + 3}" y="${H - 18 - h}" width="${bw - 6}" height="${Math.max(h, 1.5)}" rx="3"><title>${d.day}: ${d.users}</title></rect>
        ${d.users ? `<text x="${i * bw + bw / 2}" y="${H - 22 - h}" text-anchor="middle" class="v">${d.users}</text>` : ""}`; }).join("");
    const labels = [0, series.length - 1].map((i) => `<text x="${i * bw + bw / 2}" y="${H - 3}" text-anchor="middle">${series[i].day.slice(5)}</text>`).join("");
    return `<svg viewBox="0 0 ${W} ${H}" class="spark" role="img" aria-label="${T("k_newusers")}">${rects}<g class="axis">${labels}</g></svg>`;
  }

  async function adOverview() {
    const o = await api("/api/admin/overview");
    const adRows = {}; o.ads.forEach((r) => { (adRows[r.provider] = adRows[r.provider] || {})[r.status] = r.n; });
    const sts = ["completed", "nofill", "skipped"];
    const adTable = Object.keys(adRows).length ? `<table class="tbl"><thead><tr><th></th>${sts.map((s) => `<th>${T("st")[s]}</th>`).join("")}</tr></thead><tbody>
      ${Object.entries(adRows).map(([p, v]) => `<tr><td>${esc(p === "none" ? "—" : p)}</td>${sts.map((s) => `<td class="num">${v[s] || 0}</td>`).join("")}</tr>`).join("")}</tbody></table>`
      : `<p class="muted small">${T("no_items")}</p>`;
    $("#admin").innerHTML = `<div class="kpis">${kpi(o.users, T("k_users"))}${kpi(o.new_today, T("k_new"))}${kpi(o.active7, T("k_active"))}
      ${kpi(o.daily_subs, T("k_daily"))}${kpi(o.chats, T("k_chats"))}${kpi(o.charts, T("k_charts"))}${kpi(o.synastry, T("k_syn"))}
      ${kpi(o.premium, T("k_prem"))}${kpi(o.stars, "⭐ " + T("k_stars"))}${kpi(o.blocked, T("k_blocked"))}</div>
      <section class="card"><h3>${T("k_newusers")} · ${T("k_series")}</h3>${seriesChart(o.series)}</section>
      <section class="card"><h3>${T("k_ads")}</h3><p class="muted small">${T("k_req")}: <span class="num">${o.ads_requested}</span></p>${adTable}</section>
      <section class="card"><h3>${T("k_geo")}</h3><p class="muted small">${T("geo_note")}</p>${listBars(o.countries, "country", countryName)}</section>
      <section class="card two"><div><h3>${T("k_lang")}</h3>${listBars(o.langs, "lang")}</div><div><h3>${T("k_src")}</h3>${listBars(o.sources, "src")}</div></section>
      <section class="card"><h3>${T("k_tz")}</h3>${listBars(o.timezones, "tz")}</section>`;
  }

  async function adUsers(q = "") {
    const rows = await api(`/api/admin/users?q=${encodeURIComponent(q)}`);
    const a = $("#admin"); if (!a) return;
    a.innerHTML = `<input id="uq" placeholder="${T("search_user")}" value="${esc(q)}">
      <div class="list mt8">${rows.map((u) => `<div class="card user" data-uid="${u.id}">
        <div class="row between"><div><b>${esc(u.first_name || "—")}</b> ${u.username ? `<span class="muted" dir="ltr">@${esc(u.username)}</span>` : ""}
          <div class="muted small num">${u.id} · ${u.lang} · ${u.last_seen.slice(0, 10)}${u.blocked ? " · ⛔" : ""}</div></div>
          ${u.premium_until ? `<span class="pill gold">✨ ${T("premium_until")} <span class="num">${u.premium_until.slice(0, 10)}</span></span>` : ""}</div>
        <div class="row"><select data-days class="w-auto"><option value="30">30 ${T("days")}</option><option value="90">90 ${T("days")}</option><option value="180">180 ${T("days")}</option><option value="365">365 ${T("days")}</option></select>
          <button class="btn small" data-grant>${T("upgrade")}</button>
          ${u.premium_until ? `<button class="btn small ghost" data-revoke>${T("revoke")}</button>` : ""}
          <button class="btn small ghost" data-msg>${T("message_user")}</button></div>
        <input data-note placeholder="${T("note")}" class="mt8"></div>`).join("") || `<p class="muted">${T("no_items")}</p>`}</div>`;
    let t; $("#uq").oninput = (e) => { clearTimeout(t); t = setTimeout(() => adUsers(e.target.value).then(() => { const i = $("#uq"); if (i) { i.focus(); i.setSelectionRange(i.value.length, i.value.length); } }), 350); };
    a.querySelectorAll("[data-uid]").forEach((card) => {
      const uid = +card.dataset.uid;
      card.querySelector("[data-grant]").onclick = async () => {
        try { await post("/api/admin/grant", { user_id: uid, days: +card.querySelector("[data-days]").value, note: card.querySelector("[data-note]").value }); toast(T("granted")); adUsers($("#uq").value); }
        catch (e) { toast(T("err") + e.message); }
      };
      const rv = card.querySelector("[data-revoke]");
      if (rv) rv.onclick = async () => { await post("/api/admin/revoke", { user_id: uid }); toast(T("revoked")); adUsers($("#uq").value); };
      card.querySelector("[data-msg]").onclick = () => { S.adminTab = "msg"; S.msgTo = uid; VIEWS.admin(); };
    });
  }

  async function adMsg() {
    const segs = T("segs");
    $("#admin").innerHTML = `<div class="card form"><label for="mt">${T("msg_to")}</label>
      <select id="mt"><option value="user" ${S.msgTo ? "selected" : ""}>${T("msg_one")}</option>${Object.entries(segs).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
      <input id="mu" class="mt8" inputmode="numeric" dir="ltr" placeholder="user id" value="${S.msgTo || ""}">
      <label for="mx">${T("msg_text")}</label><textarea id="mx" maxlength="4000"></textarea>
      <button class="btn block" id="ms">${T("msg_send")}</button></div>`;
    const mt = $("#mt"), mu = $("#mu"); mu.hidden = mt.value !== "user";
    mt.onchange = () => { mu.hidden = mt.value !== "user"; };
    const ms = $("#ms");
    ms.onclick = async () => {
      const text = $("#mx").value.trim(); if (!text) return;
      const body = mt.value === "user" ? { text, user_id: +mu.value } : { text, segment: mt.value };
      if (mt.value !== "user" && ms.dataset.armed !== "1") {
        ms.dataset.armed = "1"; ms.textContent = T("confirm_send").replace("{n}", segs[mt.value]);
        setTimeout(() => { ms.dataset.armed = ""; ms.textContent = T("msg_send"); }, 4000); return;
      }
      ms.dataset.armed = ""; ms.disabled = true;
      try { const r = await post("/api/admin/message", body); toast(T("msg_queued").replace("{n}", r.queued)); $("#mx").value = ""; S.msgTo = null; }
      catch (e) { toast(T("err") + e.message); }
      ms.disabled = false; ms.textContent = T("msg_send");
    };
  }

  async function adContent() {
    const c = await api("/api/admin/content");
    $("#admin").innerHTML = `<p class="warn ${c.has_today ? "ok" : ""}">${c.has_today ? "✅ " + T("today_ok") : "⚠️ " + T("today_missing")}</p>
      <div class="card form"><label for="du">${T("daily_url")}</label><input id="du" dir="ltr" value="${esc(c.daily_url)}">
      <label for="wu">${T("weekly_url")}</label><input id="wu" dir="ltr" value="${esc(c.weekly_url)}">
      <label for="pr">${T("price")}</label><input id="pr" type="number" min="1" max="10000" value="${c.premium_stars}">
      <div class="row mt8"><button class="btn" id="cs">${T("save")}</button><button class="btn ghost" id="cf2">${T("fetch_now")}</button></div></div>
      <section class="card"><h3>${T("fetched_days")}</h3>${c.days.length ? `<ul class="plain">${c.days.map((d) => `<li class="num">${d.day} <small class="muted">· ${d.fetched_at.slice(0, 16).replace("T", " ")}</small></li>`).join("")}</ul>` : `<p class="muted small">${T("no_items")}</p>`}</section>`;
    $("#cs").onclick = async () => {
      try { await post("/api/admin/settings", { daily_url: $("#du").value, weekly_url: $("#wu").value, premium_stars: +$("#pr").value }); toast(T("saved")); }
      catch (e) { toast(T("err") + e.message); }
    };
    $("#cf2").onclick = async () => { const r = await post("/api/admin/fetch"); toast(`daily: ${r.daily} · weekly: ${r.weekly}`); adContent(); };
  }

  async function adFeedback() {
    const rows = await api("/api/admin/feedback");
    $("#admin").innerHTML = `<div class="list">${rows.map((f) => `<div class="card"><div class="row between"><b>${esc(f.first_name || "—")} ${f.username ? `<span class="muted" dir="ltr">@${esc(f.username)}</span>` : ""}</b>
      <small class="muted num">${f.created_at.slice(0, 16).replace("T", " ")}</small></div><p class="pre">${esc(f.text)}</p>
      <button class="btn small ghost" data-reply="${f.user_id}">${T("reply")}</button></div>`).join("") || `<p class="muted">${T("no_items")}</p>`}</div>`;
    $("#admin").querySelectorAll("[data-reply]").forEach((b) => b.onclick = () => { S.adminTab = "msg"; S.msgTo = +b.dataset.reply; VIEWS.admin(); });
  }

  async function adChats() {
    const rows = await api("/api/admin/chats");
    $("#admin").innerHTML = `<div class="list">${rows.map((c) => `<div class="card"><div class="row between"><b>${esc(c.title || c.chat_id)}</b>
      <span class="pill ${c.active ? "" : "off"}">${c.kind} · ${c.active ? "✓" : "✕"}</span></div>
      <p class="muted small num">${c.send_time} ${esc(c.tz)} · ${c.lang} · ${c.last_sent || "—"} · ${esc(c.owner || "")} ${c.owner_username ? "@" + esc(c.owner_username) : ""}</p></div>`).join("") || `<p class="muted">${T("no_items")}</p>`}</div>`;
  }

  async function refreshSession() { S.session = await api("/api/session", { method: "POST" }); }

  /* ───────────── boot ───────────── */
  async function boot() {
    if (tg) {
      tg.ready(); tg.expand();
      S.theme = tg.colorScheme === "light" ? "light" : "dark";
      try { const c = S.theme === "light" ? "#eef1ec" : "#141a33"; tg.setHeaderColor(c); tg.setBackgroundColor(c); } catch (e) {}
    }
    if (qs.get("theme") === "light") S.theme = "light";
    document.documentElement.classList.toggle("light", S.theme === "light");
    const code = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) || navigator.language || "ar";
    S.lang = code.startsWith("ar") ? "ar" : "en";
    applyLang();
    document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => { haptic(); setTab(b.dataset.tab); });
    $("#prem-btn").onclick = () => { haptic(); setTab("premium"); };
    if (!DEV && !(tg && tg.initData)) { $("#view").innerHTML = `<p class="warn">${T("open_in_tg")}</p>`; return; }
    $("#view").innerHTML = skeleton(5);
    try {
      await refreshSession();
      S.lang = S.session.user.lang || S.lang; applyLang();
      if (S.session.is_admin) { $("#tab-admin").hidden = false; document.querySelector(".tabs").classList.add("six"); }
      api("/api/vargas").then((v) => { S.vargas = v; }).catch(() => {});
      // Telegram puts tgWebAppData in the hash; only plain words are our own tab links (#daily, #channels…)
      const h = location.hash.replace("#", "");
      const start = (/^[a-z]+$/.test(h) && h) || (tg && tg.initDataUnsafe && tg.initDataUnsafe.start_param) || "chart";
      const main = S.session.profiles[0];
      if (main && start === "chart") { S.style = main.indian_style; setTab("chart"); await loadProfile(main.id); }
      else setTab(VIEWS[start] ? start : "chart");
    } catch (e) {
      $("#view").innerHTML = `<p class="warn">${T("err")}${esc(e.message)}</p>`;
    }
  }
  boot();
})();
