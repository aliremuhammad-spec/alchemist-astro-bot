/* The Alchemist Astro — Telegram Mini App (vanilla JS, no build step). */
(() => {
  const tg = window.Telegram && window.Telegram.WebApp;
  const qs = new URLSearchParams(location.search);
  const DEV = qs.get("dev"); // local preview only (server must run with DEV_AUTH=1)

  /* ───────────── text ───────────── */
  const I18N = {
    ar: {
      brand: "الخيميائي", beta: "<b>نسخة تجريبية</b> · من تطوير الخيميائي", premium_btn: "✨ مميز",
      tab_chart: "الخرائط", my_chart: "خارطتي", make_main: "هاي خارطتي أنا",
      is_mine: "هاي خارطتي أنا", is_mine_note: "«خارطتي» هي الخارطة اللي بتنبعتلك على أساسها الأبراج اليومية والعبورات والتوقعات الشخصية. باقي الخرائط للعيلة والأصدقاء والتوافق.",
      main_set: "⭐ صارت هاي «خارطتي»: الأبراج اليومية والمزايا الشخصية بتتبعها", tab_syn: "التوافق", tab_daily: "اليوم", tab_channels: "قنواتي", tab_about: "حول", tab_admin: "الإدارة",
      hero_title: "خارطتك كما كانت السماء لحظة ولادتك",
      hero_sub: "بالنظامين الغربي والفيدي، مع الرسم الهندي الشمالي أو الجنوبي.",
      new_chart: "خارطة جديدة", name: "الاسم", name_ph: "اسمك أو اسم صاحب الخارطة",
      date: "تاريخ الولادة", day: "اليوم", month: "الشهر", year: "السنة",
      time: "وقت الولادة", hour: "الساعة", minute: "الدقيقة", unknown_time: "لا أعرف وقت الولادة",
      unknown_note: "بنحسب الخارطة على الظهر، وبدون طالع وبيوت لأنها بتعتمد على الوقت بالدقيقة.",
      place: "مكان الولادة", continent: "القارة", country: "الدولة", city_ph: "ابحث عن مدينتك…",
      indian_style: "شكل الخارطة الهندية", north: "شمالي", south: "جنوبي", calc: "احسب الخارطة", calculating: "عم نحسب…",
      western: "غربية", vedic: "فيدية", fd_title: "العضوية المؤسسة", fd_sub: "شهر مميز مجاني لأول {n} عضو: {d} يوم بكل المزايا المميزة.", fd_left: "باقي {n} من {t}",
      fd_soon: "بتبلش {d}: شهر مميز مجاني لأول {n} عضو. حضّر خارطتك من هلأ.", fd_claim: "🌟 احجز مقعدك المجاني", fd_claim_chart: "احسب خارطتك واحجز مقعدك",
      fd_need_chart: "احسب خارطتك واحفظها أول، بعدين احجز مقعدك.", fd_done: "🌟 مبروك! صرت العضو المؤسس رقم {n}", fd_full: "خلصت المقاعد المؤسسة",
      fd_already: "إنت عضو مؤسس من قبل", fd_not_started: "العضوية المؤسسة لسا ما بلّشت", fd_badge: "عضو مؤسس رقم {n}",
      q_natal: "باقيلك {n} من {m} تقارير فلكية هالشهر", q_syn: "باقيلك {n} من {m} تقارير توافق هالشهر",
      queued: "دخل تقريرك الطابور (دورك رقم {n})، ورح يوصلك عالمحادثة مع البوت.", in_progress: "في تقرير إلك عم يتجهّز، استنى يوصل وبعدين اطلب التاني.",
      extra_h: "خلصت تقارير هالشهر", extra_natal: "استخدمت كل التقارير الفلكية المشمولة باشتراكك ({m}). فيك تطلب تقرير إضافي بالنجوم.",
      extra_syn: "استخدمت كل تقارير التوافق المشمولة ({m}). فيك تطلب تقرير إضافي بالنجوم.", extra_buy: "⭐ تقرير إضافي بـ {n} نجمة", extra_paid: "تم الدفع، اطلب التقرير مرة تانية",
      cancel: "إلغاء", rl_title: "بأي لغة بدك التقرير؟", rl_sub: "اختار لغة التقرير قبل ما نجهّزه.", report: "📄 تقرير فلكي PDF", report_gift: "🎁 تقرير فلكي مجاني", report_wait: "عم نجهّز التقرير الفلكي… بياخد شي دقيقة", report_sent: "وصلك التقرير الفلكي عالمحادثة مع البوت", report_lock: "التقرير الفلكي المفصّل للمشتركين المميزين، أو هدية لما حدا يدعيك",
      inv_title: "ادعُ أصحابك", inv_sub: "صديقك بياخد تقرير فلكي مجاني لخارطته، وإنت بتاخد 3 أيام مميز عن كل صديق بيصير نشط.",
      inv_how: "النشط = حفظ خارطته ورجع للبوت بيوم تاني.", inv_link: "رابطك الخاص", inv_copy: "انسخ", inv_copied: "انتسخ الرابط", inv_share: "📤 شارك مع صديق",
      inv_invited: "دعوات", inv_active: "نشطين", inv_days: "يوم مميز ربحته", inv_cta: "🎁 ادعُ صديق: هو بياخد تقرير فلكي مجاني، وإنت 3 أيام مميز",
      inv_share_text: "طلعت خارطتي الفلكية بالخيميائي 🔭 جرّب إنت كمان، وبيوصلك تقرير فلكي مجاني لخارطتك 🎁",
      syn_partner: "💞 ادعُ الشخص التاني: بيحسب خارطته لحاله وبياخد تقرير فلكي هدية.",
      syn_locked_h: "التوافق المفصّل للمميزين", syn_locked: "المشتركين المميزين بيشوفوا التوافق على مستويين مع تقرير PDF:",
      syn_locked_list: ["تفسير كامل لأبعاد العلاقة: الانجذاب، التواصل، القيم، الاستقرار، الاحتكاك", "أقوى الاتصالات بين الخارطتين، والبيوت اللي بيفعّلها كل طرف، والخارطة المركّبة", "الأشتاكوتا الفيدية (36 نقطة) مع الدوشا والمانغاليك", "تقرير توافق PDF مفصّل (30 تقرير بالشهر)"],
      syn_tab_s: "الخلاصة", syn_dims: "أبعاد العلاقة", syn_signs: "الشمس والقمر والزهرة والمريخ", syn_contacts: "أقوى الاتصالات بين الخارطتين",
      syn_balance: "توازن العناصر والطبائع", syn_composite: "الخارطة المركّبة", syn_policy: "حساب محايد: الكوتات الاتجاهية بتنحسب بالاتجاهين وبيأخذ المتوسط.",
      syn_dosha_h: "الدوشا وحالات التخفيف (حسب المدارس)", syn_moon_h: "علاقة برجي القمر والتارا",
      syn_tab_w: "غربي", syn_tab_v: "فيدي", syn_themes: "محاور العلاقة", syn_soft: "متناغم", syn_hard: "متوتر", syn_intense: "مكثّف",
      syn_overlays: "البيوت اللي بيفعّلها كل طرف", syn_ov_line: "كواكب {b} ببيوت {a}", syn_ov_none: "بحاجة لوقت ميلاد دقيق",
      syn_ak: "الأشتاكوتا", syn_ak_note: "الحساب التقليدي بيعتبر الشخص الأول طرف الرجل والتاني طرف المرأة.",
      syn_verdict: { excellent: "ممتاز", good: "جيد", average: "مقبول", low: "ضعيف" }, syn_manglik: "المانغاليك", syn_manglik_yes: "مانغاليك", syn_manglik_no: "غير مانغاليك",
      syn_mbal: "متوازن بين الطرفين", syn_munbal: "غير متوازن بين الطرفين",
      syn_doshas: { nadi: "نادي دوشا", bhakoot: "بهاكوت دوشا", gana: "تباين الغانا" },
      syn_report: "📄 تقرير التوافق PDF", syn_report_left: "باقيلك {n} من {m} هالشهر", syn_report_sent: "وصلك تقرير التوافق عالمحادثة",
      syn_report_buy: "⭐ تقرير إضافي بـ {n} نجمة", syn_report_quota: "خلصت تقارير هالشهر. فيك تشتري تقرير إضافي.", syn_report_paid: "تم الدفع، اضغط على زر التقرير مرة تانية",
      ch_why_h: "شو بتستفيد؟", ch_why: ["محتوى يومي جاهز ومجاني بينشر لحاله بالوقت واللغة اللي بتختارها", "الأوقات بالمنشور محوّلة لتوقيت جمهورك", "منشور ثابت كل يوم بيحافظ على تفاعل قناتك", "💰 عمولة 20% من النجوم اللي بيدفعها كل متابع بيدخل من رابطك، لمدة 3 شهور، وتلغرام بيحوّلها لرصيدك مباشرة"],
      ch_aff_h: "كيف تاخد عمولة 20%؟", ch_aff_steps: ["افتح بروفايل البوت بتلغرام ← «برنامج الإحالة» (أو الإعدادات ← نجومي ← اربح نجوم)", "انضم بقناتك وانسخ رابط الإحالة", "الصقه هون بإعدادات القناة، وكل منشور يومي بيحمل رابطك"],
      ch_ref: "رابط الإحالة تبعك (t.me/…?start=_tgr_…)", ch_ref_bad: "الرابط لازم يكون رابط إحالة البوت من تلغرام",
      prem_contact: "💬 تواصل مع الإدارة", prem_or_invite: "أو اربح أيام مميز مجاناً: كل صديق نشط = 3 أيام", interp_h: "قاعدة التفسيرات", interp_n: "مدخلات محمّلة", interp_up: "رفع ملف قاعدة (تفسيرات أو توافق: .sqlite أو .json أو .json.gz)، البوت بيتعرّف عليها لحاله", compat_db: "قاعدة التوافق", interp_ok: "تم الاستيراد: {n} مدخل", send: "ابعتها عالمحادثة", sent: "بعتنا الخارطة عالمحادثة مع البوت",
      share: "شارك", del: "حذف", deleted: "انحذفت الخارطة", saved_charts: "خرائطك",
      limit: "الخطة المجانية بتحفظ {n} خرائط. الخارطة انحسبت بس ما انحفظت.",
      need_city: "اختار المدينة من القائمة", need_date: "التاريخ غير صحيح",
      big_sun: "الشمس", big_moon: "القمر", big_asc: "الطالع",
      planets: "الكواكب", sign: "البرج", house: "البيت", aspects: "الاتصالات", elements: "العناصر", modes: "الصفات",
      nak: "النكشترا", lagna: "اللغنا", moon_nak: "نكشترا القمر", dasha: "الدشا الحالية (فمشوتاري)",
      maha: "مها دشا", antar: "أنتار دشا", until: "حتى", timeline: "خط الدشا", full_text: "النص الكامل",
      applying: "يقترب", separating: "يبتعد", retro: "متراجع",
      varga: "الخريطة الفرعية", varga_lock: "الخرائط الفرعية من D2 لـ D60 للمشتركين المميزين (D9 مجانية).",
      syn_title: "التوافق بين خارطتين", syn_sub: "اختار خارطتين من خرائطك. الحساب الأساسي مجاني مقابل فيديو إعلاني قصير، والمفصّل (غربي + فيدي) للمميزين.",
      syn_need: "لازم يكون عندك خارطتين محفوظتين. ضيف خارطة الشخص التاني من «خارطتي».",
      syn_a: "الشخص الأول", syn_b: "الشخص التاني", syn_go_ad: "شاهد إعلاناً واحسب التوافق", syn_go: "احسب التوافق",
      syn_same: "اختار شخصين مختلفين", ad_loading: "عم نحمّل الإعلان…", ad_closed: "انسكّر الإعلان قبل نهايته، جرّب مرة تانية.",
      ad_limit: "وصلت للحد اليومي، جرّب بكرا أو اشترك بالمميز.", score: "مؤشر التوافق",
      levels: { Minimal: "ضعيف", Medium: "متوسط", Important: "مهم", "Very Important": "مهم جداً", Exceptional: "استثنائي", "Rare Exceptional": "نادر" },
      sky_title: "سماء اليوم", sky_moon: "القمر في", sky_retro: "متراجعة الآن", sky_none: "ولا كوكب متراجع",
      daily_title: "برجك كل يوم بوقتك", daily_sub: "رسالة يومية من البوت بالوقت اللي بتختاره.",
      daily_on: "ابعتلي برجي كل يوم", today_h: "توقعات اليوم", today_none: "توقعات اليوم لسا ما نزلت، جرّب بعد شوي.", tz_note: "الأوقات محوّلة لتوقيت:",
      week_title: "الاختيارات الفلكية الأسبوعية", week_sub: "أفضل الأوقات للبدايات والعقود والسفر، بتوقيتك", week_none: "ما في اختيارات منشورة لهالأسبوع لسا.",
      week_locked: "الاختيارات الأسبوعية للمشتركين المميزين: أفضل نوافذ الأسبوع للبدايات والعقود والسفر، وأوقات يُفضّل تجنّبها، محوّلة لتوقيتك.",
      week_tz: "الأوقات محوّلة لتوقيت: ", go_premium: "اشترك بالمميز", send_time: "وقت الإرسال", tz: "المنطقة الزمنية", sign_pick: "البرج",
      sign_auto: "حسب «خارطتي»", save: "احفظ", saved: "انحفظت الإعدادات",
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
        ["توافق مفصّل بلا إعلانات", "غربي وفيدي (الأشتاكوتا 36 نقطة) مع 30 تقرير توافق PDF بالشهر (5 بالشهر المجاني للمؤسسين)"],
        ["ملفات غير محدودة", "احفظ خرائط العائلة والأصدقاء بدون حد"],
        ["تقرير فلكي PDF مفصّل", "10 تقارير بالشهر (3 بالشهر المجاني للمؤسسين): تفسير كامل للخارطة الغربية والفيدية مع اليوغات والدشا"],
        ["الاختيارات الفلكية الأسبوعية", "أفضل أوقات الأسبوع للبدايات والعقود والسفر، محوّلة لتوقيتك"],
        ["قريباً للمشتركين", "العبور اليومي الشخصي، تنبيهات العبور، الحسابات الفيدية المتقدمة (شادبالا وأشتاكافارغا)"]],
      prem_manual: "ما عندك نجوم تلغرام؟ تواصل مع الإدارة لطرق دفع تانية.",
      err: "صار خطأ: ", open_in_tg: "افتح التطبيق من داخل تلغرام عبر البوت.",
      months: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
      signs: ["الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء", "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت"],
      el: { fire: "نار", earth: "تراب", air: "هواء", water: "ماء" }, md: { cardinal: "كاردينال", fixed: "ثابت", mutable: "متحول" },
      ad_overview: "نظرة عامة", ad_users: "المستخدمين", ad_msg: "الرسائل", ad_content: "المحتوى", ad_fb: "الاقتراحات", ad_chats: "القنوات",
      k_users: "المستخدمين", k_new: "جدد اليوم", k_active: "نشطين 7 أيام", k_daily: "مشتركين بالأبراج", k_chats: "قنوات ومجموعات",
      k_charts: "خرائط محسوبة", k_syn: "توافقات", k_prem: "مميزين الآن", k_stars: "نجوم مدفوعة", k_blocked: "حظروا البوت",
      k_series: "آخر 14 يوم", k_newusers: "مستخدمين جدد", k_ads: "الإعلانات (30 يوم)", k_req: "طلبات", k_geo: "دول الولادة",
      k_tz: "المناطق الزمنية", k_founders: "مؤسسين", k_inv: "دعوات", k_inv_act: "دعوات نشطة", k_reports: "تقارير فلكية", k_syn_reports: "تقارير توافق", syn_price: "سعر تقرير التوافق الإضافي (نجوم)", k_lang: "اللغات", k_src: "مصادر الدخول", geo_note: "الموقع الحالي غير معروف؛ هاي دولة الولادة بالخارطة الرئيسية.",
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
      tab_chart: "Charts", my_chart: "My chart", make_main: "This is my chart",
      is_mine: "This is my own chart", is_mine_note: "“My chart” is the one your daily horoscope, transits and personal forecasts follow. Other charts are for family, friends and compatibility.",
      main_set: "⭐ This is now “My chart”: your daily horoscope and personal features follow it", tab_syn: "Match", tab_daily: "Today", tab_channels: "Channels", tab_about: "About", tab_admin: "Admin",
      hero_title: "Your chart: the sky at the moment you were born", hero_sub: "Western and Vedic, with a North or South Indian chart.",
      new_chart: "New chart", name: "Name", name_ph: "Your name or the chart owner's",
      date: "Birth date", day: "Day", month: "Month", year: "Year",
      time: "Birth time", hour: "Hour", minute: "Minute", unknown_time: "I don't know the birth time",
      unknown_note: "We'll cast it for noon, without Ascendant and houses, which need the exact time.",
      place: "Birthplace", continent: "Continent", country: "Country", city_ph: "Search your city…",
      indian_style: "Indian chart style", north: "North", south: "South", calc: "Calculate chart", calculating: "Calculating…",
      western: "Western", vedic: "Vedic", fd_title: "Founding membership", fd_sub: "A free Premium month for the first {n} members: {d} days of every Premium feature.", fd_left: "{n} of {t} left",
      fd_soon: "Opens {d}: a free Premium month for the first {n} members. Get your chart ready now.", fd_claim: "🌟 Claim your free seat", fd_claim_chart: "Cast your chart and claim a seat",
      fd_need_chart: "Cast and save your chart first, then claim your seat.", fd_done: "🌟 Welcome, founding member #{n}!", fd_full: "All founding seats are taken",
      fd_already: "You're already a founding member", fd_not_started: "Founding membership hasn't opened yet", fd_badge: "Founding member #{n}",
      q_natal: "{n} of {m} astrological reports left this month", q_syn: "{n} of {m} compatibility reports left this month",
      queued: "Your report is in the queue (position {n}); it will arrive in your chat with the bot.", in_progress: "One of your reports is being prepared; wait for it before requesting another.",
      extra_h: "This month's reports are used", extra_natal: "You've used the astrological reports included in your plan ({m}). You can order an extra one with Stars.",
      extra_syn: "You've used the compatibility reports included ({m}). You can order an extra one with Stars.", extra_buy: "⭐ Extra report for {n} Stars", extra_paid: "Paid. Request the report again",
      cancel: "Cancel", rl_title: "Which language for the report?", rl_sub: "Choose the report language before we prepare it.", report: "📄 Astrological report PDF", report_gift: "🎁 Free astrological report", report_wait: "Preparing your astrological report… about a minute", report_sent: "Astrological report sent to your chat with the bot", report_lock: "The detailed astrological report is for Premium members, or a gift when someone invites you",
      inv_title: "Invite friends", inv_sub: "Your friend gets a free astrological report; you get 3 Premium days for every friend who becomes active.",
      inv_how: "Active = saved a chart and came back another day.", inv_link: "Your link", inv_copy: "Copy", inv_copied: "Link copied", inv_share: "📤 Share with a friend",
      inv_invited: "Invited", inv_active: "Active", inv_days: "Premium days earned", inv_cta: "🎁 Invite a friend: they get a free astrological report, you get 3 Premium days",
      inv_share_text: "I cast my birth chart with The Alchemist 🔭 Try it and get a free astrological report of yours 🎁",
      syn_partner: "💞 Invite the other person: they cast their own chart and get an astrological report as a gift.",
      syn_locked_h: "Detailed compatibility is Premium", syn_locked: "Premium members see compatibility on two levels, plus a PDF report:",
      syn_locked_list: ["Full reading of each dimension: attraction, communication, values, stability, friction", "Strongest contacts, the houses each person activates, and the composite chart", "Vedic Ashtakoota (36 points) with doshas and Manglik", "Detailed compatibility PDF report (30 a month)"],
      syn_tab_s: "Summary", syn_dims: "Relationship dimensions", syn_signs: "Sun, Moon, Venus and Mars", syn_contacts: "Strongest contacts",
      syn_balance: "Elements and modalities", syn_composite: "Composite chart", syn_policy: "Gender-neutral: directional kootas are computed both ways and averaged.",
      syn_dosha_h: "Doshas and mitigations (school-dependent)", syn_moon_h: "Moon-sign relation and Tara",
      syn_tab_w: "Western", syn_tab_v: "Vedic", syn_themes: "Relationship themes", syn_soft: "Harmonious", syn_hard: "Tense", syn_intense: "Intense",
      syn_overlays: "Houses each person activates", syn_ov_line: "{b}'s planets in {a}'s houses", syn_ov_none: "Needs an exact birth time",
      syn_ak: "Ashtakoota", syn_ak_note: "Classically the first person is read as the groom and the second as the bride.",
      syn_verdict: { excellent: "Excellent", good: "Good", average: "Acceptable", low: "Low" }, syn_manglik: "Manglik", syn_manglik_yes: "Manglik", syn_manglik_no: "Not Manglik",
      syn_mbal: "Balanced between both", syn_munbal: "Not balanced between both",
      syn_doshas: { nadi: "Nadi dosha", bhakoot: "Bhakoot dosha", gana: "Gana contrast" },
      syn_report: "📄 Compatibility report PDF", syn_report_left: "{n} of {m} left this month", syn_report_sent: "Compatibility report sent to your chat",
      syn_report_buy: "⭐ Extra report for {n} Stars", syn_report_quota: "This month's reports are used up. You can buy an extra one.", syn_report_paid: "Paid. Tap the report button again",
      ch_why_h: "What you get", ch_why: ["Free daily content posted automatically at your time and language", "Times in posts are converted to your audience's zone", "A steady daily post keeps your channel engaged", "💰 20% of the Stars spent by everyone who joins through your link, for 3 months, paid by Telegram to your balance"],
      ch_aff_h: "How to earn the 20%", ch_aff_steps: ["Open the bot's profile in Telegram → Affiliate program (or Settings → My Stars → Earn Stars)", "Join with your channel and copy the referral link", "Paste it here in the channel settings so every daily post carries it"],
      ch_ref: "Your referral link (t.me/…?start=_tgr_…)", ch_ref_bad: "Use the bot's Telegram referral link",
      prem_contact: "💬 Contact the team", prem_or_invite: "Or earn Premium days for free: each active friend = 3 days", interp_h: "Interpretation database", interp_n: "entries loaded", interp_up: "Upload a database (interpretations or compatibility: .sqlite, .json or .json.gz); detected automatically", compat_db: "Compatibility database", interp_ok: "Imported: {n} entries", send: "Send to chat", sent: "Chart sent to your chat with the bot",
      share: "Share", del: "Delete", deleted: "Chart deleted", saved_charts: "Your charts",
      limit: "Free plan keeps {n} charts. This one was calculated but not saved.",
      need_city: "Choose a city from the list", need_date: "Invalid date",
      big_sun: "Sun", big_moon: "Moon", big_asc: "Rising",
      planets: "Planets", sign: "Sign", house: "House", aspects: "Aspects", elements: "Elements", modes: "Modalities",
      nak: "Nakshatra", lagna: "Lagna", moon_nak: "Moon nakshatra", dasha: "Current dasha (Vimshottari)",
      maha: "Mahadasha", antar: "Antardasha", until: "until", timeline: "Dasha timeline", full_text: "Full text",
      applying: "applying", separating: "separating", retro: "retrograde",
      varga: "Divisional chart", varga_lock: "Divisional charts D2–D60 are for Premium members (D9 is free).",
      syn_title: "Compatibility of two charts", syn_sub: "Pick two saved charts. The basic reading is free for a short video ad; the detailed one (Western + Vedic) is Premium.",
      syn_need: "You need two saved charts. Add the other person's chart in My chart.",
      syn_a: "First person", syn_b: "Second person", syn_go_ad: "Watch an ad and compare", syn_go: "Compare charts",
      syn_same: "Pick two different people", ad_loading: "Loading the ad…", ad_closed: "The ad was closed early. Try again.",
      ad_limit: "Daily limit reached. Try tomorrow or go Premium.", score: "Compatibility score",
      levels: {},
      sky_title: "Today's sky", sky_moon: "Moon in", sky_retro: "Retrograde now", sky_none: "No planet retrograde",
      daily_title: "Your horoscope, daily, on your time", daily_sub: "A daily message from the bot at the time you choose.",
      daily_on: "Send me my horoscope every day", today_h: "Today's reading", today_none: "Today's reading isn't out yet; try again shortly.", tz_note: "Times shown in:",
      week_title: "Weekly electional picks", week_sub: "Best windows for beginnings, contracts and travel, in your time", week_none: "No picks published for this week yet.",
      week_locked: "Weekly picks are for Premium members: the week's best windows for beginnings, contracts and travel, plus times to avoid, in your time zone.",
      week_tz: "Times shown in: ", go_premium: "Go Premium", send_time: "Send at", tz: "Time zone", sign_pick: "Sign",
      sign_auto: "From “My chart”", save: "Save", saved: "Settings saved",
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
        ["Detailed compatibility, no ads", "Western and Vedic (36-point Ashtakoota) with 30 compatibility PDF reports a month (5 in the founders' free month)"],
        ["Unlimited profiles", "Save family and friends without a limit"],
        ["Detailed astrological report PDF", "10 a month (3 in the founders' free month): full Western and Vedic interpretation with yogas and dashas"],
        ["Weekly electional picks", "The week's best windows for beginnings, contracts and travel, in your time zone"],
        ["Coming for members", "Personal daily transits, transit alerts, advanced Vedic strength (Shadbala, Ashtakavarga)"]],
      prem_manual: "No Telegram Stars? Contact the team for other payment options.",
      err: "Error: ", open_in_tg: "Open the app from inside Telegram via the bot.",
      months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      signs: ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
      el: { fire: "Fire", earth: "Earth", air: "Air", water: "Water" }, md: { cardinal: "Cardinal", fixed: "Fixed", mutable: "Mutable" },
      ad_overview: "Overview", ad_users: "Users", ad_msg: "Messages", ad_content: "Content", ad_fb: "Feedback", ad_chats: "Channels",
      k_users: "Users", k_new: "New today", k_active: "Active 7 days", k_daily: "Daily subscribers", k_chats: "Channels & groups",
      k_charts: "Charts cast", k_syn: "Synastries", k_prem: "Premium now", k_stars: "Stars paid", k_blocked: "Blocked the bot",
      k_series: "Last 14 days", k_newusers: "New users", k_ads: "Ads (30 days)", k_req: "requests", k_geo: "Birth countries",
      k_tz: "Time zones", k_founders: "Founders", k_inv: "Invites", k_inv_act: "Active invites", k_reports: "Astrological reports", k_syn_reports: "Compatibility reports", syn_price: "Extra compatibility report price (Stars)", k_lang: "Languages", k_src: "Sources", geo_note: "Current location is unknown; this is the birth country of the main chart.",
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
  const isPrem = () => !!(S.session && (S.session.premium || S.session.is_admin));
  function setTab(tab) {
    if (!VIEWS[tab]) tab = "chart";
    S.tab = tab;
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === tab));
    $("#prem-btn").classList.toggle("on", tab === "premium");
    const v = $("#view"); v.classList.remove("enter"); void v.offsetWidth; v.classList.add("enter");
    VIEWS[tab]();
    window.scrollTo(0, 0);
    if (tab === "synastry" || tab === "premium" || tab === "chart") refreshSession().then(() => {
      const was = S._prem; S._prem = isPrem(); if (was !== undefined && was !== S._prem && S.tab === tab) VIEWS[tab]();
    }).catch(() => {});
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
      `<button class="chip ${p.is_main ? "mine" : ""}" data-pid="${p.id}" aria-pressed="${p.id === S.profileId && !S.editing}">${p.is_main ? `<span aria-label="${T("my_chart")}">⭐</span> ` : ""}${esc(p.name)}</button>`).join("")}
      <button class="chip add" data-new aria-pressed="${S.editing}">+ ${T("new_chart")}</button></div>`;
  }

  VIEWS.chart = function renderChart() {
    const v = $("#view");
    const showForm = S.editing || !S.chart;
    const first = !S.session.profiles.length;
    v.innerHTML = `${profileChips()}${foundersBanner()}
      ${S.chart && !S.editing ? chartView() : ""}
      ${showForm ? (first ? `${zodiacRing()}<h2 class="hero-title">${T("hero_title")}</h2><p class="muted center">${T("hero_sub")}</p>` : "") + formView() : ""}`;
    v.querySelectorAll("[data-pid]").forEach((b) => b.onclick = () => loadProfile(+b.dataset.pid));
    const nb = v.querySelector("[data-new]"); if (nb) nb.onclick = () => { S.editing = true; VIEWS.chart(); };
    if (showForm) bindForm(); else bindChart();
    bindFounders();
  };

  function mainName() { const p = S.session.profiles.find((x) => x.is_main); return p ? p.name : ""; }

  /* ───────────── founding members ───────────── */
  function foundersBanner() {
    const f = S.session.founders;
    if (!f || f.claimed || S.session.is_admin) return "";
    if (!f.started) {
      const d = new Date(f.start).toLocaleDateString(S.lang === "ar" ? "ar-SY" : "en-GB", { day: "numeric", month: "long" });
      return `<section class="card founders soon"><b>🌟 ${T("fd_title")}</b><p class="small">${T("fd_soon").replace("{n}", f.total).replace("{d}", d)}</p></section>`;
    }
    if (!f.open) return "";
    const pct = Math.round((f.taken / f.total) * 100);
    return `<section class="card founders"><div class="row between"><b>🌟 ${T("fd_title")}</b><span class="num fd-left">${T("fd_left").replace("{n}", f.left).replace("{t}", f.total)}</span></div>
      <p class="small">${T("fd_sub").replace("{n}", f.total).replace("{d}", f.days)}</p>
      <div class="tbar"><span style="width:${Math.max(3, pct)}%"></span></div>
      <button class="btn block" data-founder>${f.has_chart ? T("fd_claim") : T("fd_claim_chart")}</button></section>`;
  }

  function bindFounders() {
    document.querySelectorAll("[data-founder]").forEach((b) => b.onclick = async () => {
      const f = S.session.founders;
      if (!f.has_chart) { S.editing = true; setTab("chart"); toast(T("fd_need_chart")); return; }
      b.disabled = true; b.innerHTML = `<span class="spinner"></span>`;
      try {
        const r = await post("/api/founders/claim");
        await refreshSession(); S._prem = isPrem(); haptic("heavy");
        toast(T("fd_done").replace("{n}", r.number)); VIEWS[S.tab]();
      } catch (e) {
        const m = { full: T("fd_full"), already: T("fd_already"), need_chart: T("fd_need_chart"), not_started: T("fd_not_started") }[e.message];
        toast(m || T("err") + e.message); await refreshSession(); VIEWS[S.tab]();
      }
    });
  }

  function quotaLine(kind) {
    const q = (S.session.quota || {})[kind];
    if (!q || !q.tier || q.tier === "admin") return "";
    return `<p class="muted small center">${T(kind === "natal" ? "q_natal" : "q_syn").replace("{n}", q.left + q.credits).replace("{m}", q.limit)}</p>`;
  }

  async function buyExtra(kind) {
    const url = kind === "natal" ? "/api/report/invoice" : "/api/synastry/report/invoice";
    try {
      const { link } = await post(url);
      const done = async (status) => { if (status === "paid") { toast(T("extra_paid")); await refreshSession(); VIEWS[S.tab](); } };
      if (tg && tg.openInvoice) tg.openInvoice(link, done); else openTg(link);
    } catch (e) { toast(T("err") + e.message); }
  }

  function askBuyExtra(kind) {
    const q = (S.session.quota || {})[kind] || {};
    const box = document.createElement("div");
    box.className = "sheet-back";
    box.innerHTML = `<div class="sheet" role="dialog" aria-modal="true"><h3>${T("extra_h")}</h3>
      <p class="muted small">${T(kind === "natal" ? "extra_natal" : "extra_syn").replace("{m}", q.limit || "")}</p>
      <button class="btn block" data-b="1">${T("extra_buy").replace("{n}", q.price || 50)}</button>
      <button class="btn ghost block" data-b="">${T("cancel")}</button></div>`;
    box.addEventListener("click", (e) => { const b = e.target.closest("[data-b]"); if (b || e.target === box) { box.remove(); if (b && b.dataset.b) buyExtra(kind); } });
    document.body.appendChild(box);
  }

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
      <label class="switch mt8"><input type="checkbox" id="f-mine" ${S.session.profiles.some((p) => p.is_main) ? "" : "checked"}> ${T("is_mine")}</label>
      <p class="muted small">${T("is_mine_note")}</p>
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
          time_known: !f.unknown, country: f.country, city_id: f.city_id, indian_style: S.style, theme: S.theme, lang: S.lang, save: true,
          is_mine: $("#f-mine").checked });
        if (S.session.meta.chart_ad && !isPrem() && window.Ads) {
          try { await window.Ads.watch("chart", S.session.meta.ads || {}, api); } catch (e) { /* the chart is free either way */ }
        }
        S.chart = res; S.profileId = res.profile_id; S.editing = false; S.system = "western"; S.varga = 1; S.vargaSvg = null; S.form = {};
        if (res.profile_limit_hit) toast(T("limit").replace("{n}", S.session.meta.free_profiles));
        await refreshSession(); haptic("medium"); VIEWS.chart();
        if (res.profile_id && (S.session.profiles.find((p) => p.id === res.profile_id) || {}).is_main) toast(T("main_set"));
      } catch (err) { toast(T("err") + err.message); go.disabled = false; go.textContent = T("calc"); }
    };
  }

  function mainBadge() {
    if (!S.profileId) return "";
    const p = S.session.profiles.find((x) => x.id === S.profileId);
    if (!p) return "";
    return p.is_main ? `<p class="mine-badge">⭐ ${T("my_chart")}</p>`
      : `<button class="btn small ghost mine-set" id="set-main">⭐ ${T("make_main")}</button>`;
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
      ${mainBadge()}
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
      ${S.profileId ? (isPrem() ? `<button class="btn" id="report">${T("report")}</button>`
        : S.session.report_credits > 0 ? `<button class="btn gift" id="report">${T("report_gift")}</button>`
        : `<button class="btn ghost" id="report">🔒 ${T("report")}</button>`) : ""}
      <button class="btn ghost" id="share">${T("share")}</button>
      ${S.profileId ? `<button class="btn ghost danger" id="del">${T("del")}</button>` : ""}
    </div>
    ${S.profileId ? quotaLine("natal") : ""}
    ${S.profileId ? `<button class="card invite-cta" data-invite>${T("inv_cta")}</button>` : ""}`;
  }

  function vargaOptions() {
    const prem = isPrem();
    return (S.vargas || [{ n: 1, name: "Rashi", ar: "الراشي" }]).map((v) =>
      `<option value="${v.n}" ${v.n === S.varga ? "selected" : ""}>${v.n === 1 || v.n === 9 || prem ? "" : "🔒 "}D${v.n} · ${esc(S.lang === "ar" ? v.ar : v.name)}</option>`).join("");
  }

  async function loadVarga(n) {
    if (n === 1) { S.varga = 1; S.vargaSvg = null; return VIEWS.chart(); }
    if (n !== 9 && !isPrem()) { toast(T("varga_lock")); $("#varga").value = String(S.varga); return; }
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
    const rep = $("#report");
    if (rep) rep.onclick = async () => {
      if (!isPrem() && !(S.session.report_credits > 0)) { toast(T("report_lock")); return setTab("premium"); }
      const lang = await pickReportLang(); if (!lang) return;
      rep.disabled = true; rep.innerHTML = `<span class="spinner"></span>`; toast(T("report_wait"));
      try {
        const pr = S.session.profiles.find((x) => x.id === S.profileId) || {};
        let country_name = null; try { country_name = new Intl.DisplayNames([lang], { type: "region" }).of(pr.country); } catch (e) {}
        const r = await post(`/api/profiles/${S.profileId}/report`, { lang, style: S.style, country_name });
        toast(T("queued").replace("{n}", r.position)); haptic("heavy");
        await refreshSession(); VIEWS.chart(); return;
      }
      catch (e) {
        if (e.message === "report_quota") askBuyExtra("natal");
        else toast(e.message === "premium_required" ? T("report_lock") : e.message === "report_in_progress" ? T("in_progress") : T("err") + e.message);
      }
      rep.disabled = false; rep.textContent = T("report");
    };
    document.querySelectorAll("[data-invite]").forEach((b) => b.onclick = () => setTab("invite"));
    const sm = $("#set-main");
    if (sm) sm.onclick = async () => {
      sm.disabled = true;
      try { await post(`/api/profiles/${S.profileId}/main`); await refreshSession(); haptic("medium"); toast(T("main_set")); VIEWS.chart(); }
      catch (e) { toast(T("err") + e.message); sm.disabled = false; }
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
      $("#view").innerHTML = `<h2>${T("syn_title")}</h2><p class="muted">${T("syn_need")}</p><button class="btn" id="go-chart">+ ${T("new_chart")}</button>
        <button class="card invite-cta mt16" data-invite>${T("syn_partner")}</button>`;
      $("#go-chart").onclick = () => { S.editing = true; setTab("chart"); };
      document.querySelector("[data-invite]").onclick = () => setTab("invite");
      return;
    }
    const opt = (sel) => ps.map((p) => `<option value="${p.id}" ${p.id === sel ? "selected" : ""}>${esc(p.name)} · ${p.birth_date}</option>`).join("");
    const prem = isPrem();
    $("#view").innerHTML = `<h2>${T("syn_title")}</h2>${prem ? "" : `<p class="muted">${T("syn_sub")}</p>`}
      <div class="card form"><label for="sa">${T("syn_a")}</label><select id="sa">${opt(S.synA || ps[0].id)}</select>
      <label for="sb">${T("syn_b")}</label><select id="sb">${opt(S.synB || ps[1].id)}</select>
      <button class="btn block" id="syn-go">${prem ? T("syn_go") : T("syn_go_ad")}</button></div>
      <div id="syn-out">${S.synResult ? synView(S.synResult) : ""}</div>`;
    $("#syn-go").onclick = runSynastry;
    bindSynDetail();
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
      ${r.compat ? compatView(r) : r.detail ? synDetail(r) : ""}${r.locked ? (r.compat_teaser ? compatTeaser(r.compat_teaser) : "") + synLocked() : ""}
      <details class="card"><summary>${T("full_text")}</summary><div class="report">${r.text}</div></details>`;
  }

  const DIMS = { ar: { attraction: "الانجذاب", communication: "التواصل", values: "القيم", stability: "الاستقرار", friction: "الاحتكاك" },
                 en: { attraction: "Attraction", communication: "Communication", values: "Values", stability: "Stability", friction: "Friction" } };
  const LVL = { ar: { high: "مرتفع", mid: "متوسط", low: "منخفض" }, en: { high: "High", mid: "Medium", low: "Low" } };
  const ent = (d, open) => d ? `<details class="ent" ${open ? "open" : ""}><summary><b>${esc(d.title)}</b>${d.summary && d.summary !== d.title ? `<small>${esc(d.summary)}</small>` : ""}</summary>
      ${d.text ? `<div class="pre">${esc(d.text)}</div>` : ""}${d.advice ? `<p class="adv">${esc(d.advice)}</p>` : ""}</details>` : "";

  function compatTeaser(t) {
    const L = S.lang === "ar" ? "ar" : "en";
    return `<section class="card compat"><div class="akbox"><div class="ring" style="--p:${t.overall}"><b class="num">${t.overall}%</b></div>
      <div><b>${esc(t.band || "")}</b><small class="muted">${esc(t.summary || "")}</small></div></div>
      <div class="pills">${t.dimensions.map((d) => `<span class="pill">🔒 ${DIMS[L][d.key]}</span>`).join("")}</div></section>`;
  }

  function compatView(r) {
    const c = r.compat, L = S.lang === "ar" ? "ar" : "en", tab = S.synTab || "s", [A, B] = c.names.map(esc);
    const dims = c.dimensions.map((d) => `<div class="theme"><div class="row between"><b>${DIMS[L][d.key]}</b><small class="muted">${LVL[L][d.level]} · <span class="num">${Math.round(d.score)}</span></small></div>
        <div class="tbar ${d.key === "friction" ? "warm" : ""}"><span style="width:${Math.max(3, d.score)}%"></span></div>${d.entry ? `<small class="muted">${esc(d.entry.summary || "")}</small>` : ""}</div>`).join("");
    const ov = (list, a, b) => `<h3>${T("syn_ov_line").replace("{a}", a).replace("{b}", b)}</h3>${list ? list.map((o) => ent(o.entry)).join("") : `<p class="muted small">${T("syn_ov_none")}</p>`}`;
    let body;
    if (tab === "s") {
      body = `<div class="akbox"><div class="ring" style="--p:${c.overall}"><b class="num">${c.overall}%</b></div><div><b>${esc((c.overall_entry || {}).title || "")}</b>
          <small class="muted">${T("syn_tab_w")} <span class="num">${Math.round(c.western_score)}%</span> · ${T("syn_ak")} <span class="num">${c.ashtakoota_total}/36</span></small></div></div>
        ${ent(c.overall_entry, true)}<h3>${T("syn_dims")}</h3>${dims}`;
    } else if (tab === "w") {
      body = `<h3>${T("syn_signs")}</h3>${c.sign_pairs.map((p) => ent(p.entry)).join("")}
        <h3>${T("syn_contacts")}</h3>${c.aspects.slice(0, 12).map((x) => ent(x.entry)).join("")}
        ${ov(c.overlays.ab, A, B)}${ov(c.overlays.ba, B, A)}
        <h3>${T("syn_balance")}</h3>${c.balance.map((x) => ent(x.entry)).join("")}
        <h3>${T("syn_composite")}</h3>${c.composite.asc ? ent(c.composite.asc) : ""}${c.composite.planets.slice(0, 7).map((p) => ent(p.sign_entry)).join("")}`;
    } else {
      const v = c.vedic;
      body = `<div class="akbox"><div class="ring" style="--p:${Math.round(v.total / 36 * 100)}"><b class="num">${v.total}</b></div><div><b>${T("syn_ak")} · ${esc((v.score_band || {}).title || "")}</b><small class="muted">/ 36</small></div></div>
        ${ent(v.score_band)}
        <table class="ak">${v.kootas.map((k) => `<tr class="${k.points >= k.max ? "full" : k.points === 0 ? "zero" : ""}"><td><b>${esc((k.entry || {}).title || k.key)}</b><small class="muted">${esc((k.entry || {}).summary || "")}</small></td><td class="num">${k.points}/${k.max}</td></tr>`).join("")}</table>
        <p class="muted small">${T("syn_policy")}</p>
        ${v.doshas.length || v.yoni_pair ? `<h3>${T("syn_dosha_h")}</h3>${v.doshas.map((d) => ent(d)).join("")}${ent(v.yoni_pair)}${v.cancels.map((x) => ent(x)).join("")}` : ""}
        <h3>${T("syn_moon_h")}</h3>${ent(v.moon_relation)}${v.tara.map((x) => ent(x)).join("")}
        <h3>${T("syn_manglik")}</h3>${ent(v.manglik.entry)}${v.manglik.people.map((p, i) => p.is && p.entry ? ent({ ...p.entry, title: `${[A, B][i]}: ${p.entry.title}` }) : "").join("")}`;
    }
    const q = r.report_quota, left = q ? (q.left ?? Math.max(0, q.limit - q.used)) : 0;
    const repBtn = q ? (left > 0 || q.credits > 0 || S.session.is_admin
      ? `<button class="btn block" id="syn-rep">${T("syn_report")}</button><p class="muted small center">${T("syn_report_left").replace("{n}", left + q.credits).replace("{m}", q.limit)}</p>`
      : `<p class="muted small">${T("syn_report_quota")}</p><button class="btn block" id="syn-buy">${T("syn_report_buy").replace("{n}", q.price)}</button>`) : "";
    return `<section class="card syn-detail compat"><div class="seg three" id="syn-tabs">
        <button data-v="s" aria-pressed="${tab === "s"}">${T("syn_tab_s")}</button><button data-v="w" aria-pressed="${tab === "w"}">${T("syn_tab_w")}</button><button data-v="v" aria-pressed="${tab === "v"}">${T("syn_tab_v")}</button></div>
      ${body}<div class="mt16">${repBtn}</div>${c.footer ? `<p class="footer-note">${esc(c.footer)}</p>` : ""}</section>`;
  }

  /* Report language is always the reader's explicit choice, never inferred. */
  function pickReportLang() {
    return new Promise((resolve) => {
      const box = document.createElement("div");
      box.className = "sheet-back";
      box.innerHTML = `<div class="sheet" role="dialog" aria-modal="true" aria-labelledby="rl-h">
        <h3 id="rl-h">${T("rl_title")}</h3><p class="muted small">${T("rl_sub")}</p>
        <div class="grid2"><button class="btn" data-l="ar" lang="ar">العربية</button><button class="btn" data-l="en" lang="en">English</button></div>
        <button class="btn ghost block" data-l="">${T("cancel")}</button></div>`;
      const done = (v) => { box.remove(); resolve(v || null); };
      box.addEventListener("click", (e) => { const b = e.target.closest("[data-l]"); if (b) { haptic(); done(b.dataset.l); } else if (e.target === box) done(null); });
      document.addEventListener("keydown", function esc(e) { if (e.key === "Escape") { document.removeEventListener("keydown", esc); done(null); } });
      document.body.appendChild(box);
      box.querySelector("[data-l]").focus();
    });
  }

  function synLocked() {
    return `<section class="card locked"><h3>✨ ${T("syn_locked_h")}</h3><p class="muted">${T("syn_locked")}</p>
      <ul class="plain checks">${T("syn_locked_list").map((x) => `<li>${x}</li>`).join("")}</ul>
      <button class="btn block" data-go-prem>${T("go_premium")}</button></section>`;
  }

  function synDetail(r) {
    const d = r.detail, w = d.western, v = d.vedic, ak = v.ashtakoota, ar = S.lang === "ar";
    const tab = S.synTab || "w", [A, B] = r.names.map(esc);
    const themes = w.themes.map((t) => `<div class="theme"><div class="row between"><b>${esc(ar ? t.ar : t.en)}</b>
        <small class="muted">${T("syn_soft")} ${t.soft} · ${T("syn_hard")} ${t.hard}${t.intense ? ` · ${T("syn_intense")} ${t.intense}` : ""}</small></div>
        ${t.score === null ? "" : `<div class="tbar"><span style="width:${Math.max(3, t.score)}%"></span></div>`}
        <small class="muted">${esc(ar ? t.about_ar : t.about_en)}</small></div>`).join("");
    const ov = (list, a, b) => `<div><h4>${T("syn_ov_line").replace("{a}", a).replace("{b}", b)}</h4>${list ? `<ul class="plain">${list.map((o) => `<li>${PL[o.planet][0]} ${pn(o.planet)} → ${S.lang === "ar" ? "البيت" : "House"} <span class="num">${o.house}</span></li>`).join("")}</ul>` : `<p class="muted small">${T("syn_ov_none")}</p>`}</div>`;
    const kootas = ak.kootas.map((k) => `<tr class="${k.points >= k.max ? "full" : k.points === 0 ? "zero" : ""}"><td><b>${esc(ar ? k.ar : k.en)}</b><small class="muted">${esc(ar ? k.about_ar : k.about_en)}</small></td><td class="num">${k.points}/${k.max}</td></tr>`).join("");
    const mg = v.manglik.map((m, i) => `<span class="pill ${m.is ? "warnp" : ""}">${[A, B][i]}: ${m.is ? T("syn_manglik_yes") : T("syn_manglik_no")}</span>`).join("");
    const q = r.report_quota;
    const left = q ? (q.left ?? Math.max(0, q.limit - q.used)) : 0;
    const repBtn = q ? (left > 0 || q.credits > 0 || S.session.is_admin
      ? `<button class="btn block" id="syn-rep">${T("syn_report")}</button><p class="muted small center">${T("syn_report_left").replace("{n}", left + q.credits).replace("{m}", q.limit)}</p>`
      : `<p class="muted small">${T("syn_report_quota")}</p><button class="btn block" id="syn-buy">${T("syn_report_buy").replace("{n}", q.price)}</button>`) : "";
    return `<section class="card syn-detail"><div class="seg" id="syn-tabs"><button data-v="w" aria-pressed="${tab === "w"}">${T("syn_tab_w")}</button><button data-v="v" aria-pressed="${tab === "v"}">${T("syn_tab_v")}</button></div>
      ${tab === "w" ? `<h3>${T("syn_themes")}</h3>${themes}<h3>${T("syn_overlays")}</h3><div class="grid2">${ov(w.overlays_ab, A, B)}${ov(w.overlays_ba, B, A)}</div>`
        : `<div class="akbox"><div class="ring" style="--p:${Math.round(ak.total / 36 * 100)}"><b class="num">${ak.total}</b></div><div><b>${T("syn_ak")} · ${(T("syn_verdict") || {})[ak.verdict] || ak.verdict}</b><small class="muted">/ 36</small></div></div>
           <table class="ak">${kootas}</table><p class="muted small">${T("syn_ak_note")}</p>
           ${ak.doshas.length ? `<div class="pills">${ak.doshas.map((x) => `<span class="pill warnp">${T("syn_doshas")[x]}</span>`).join("")}</div>` : ""}
           <h3>${T("syn_manglik")}</h3><div class="pills">${mg}</div><p class="muted small">${v.manglik_balanced ? T("syn_mbal") : T("syn_munbal")}</p>`}
      <div class="mt16">${repBtn}</div></section>`;
  }

  function bindSynDetail() {
    const tabs = $("#syn-tabs");
    if (tabs) tabs.onclick = (e) => { const b = e.target.closest("button"); if (!b) return; S.synTab = b.dataset.v; haptic(); VIEWS.synastry(); };
    document.querySelectorAll("[data-go-prem]").forEach((b) => b.onclick = () => setTab("premium"));
    const rep = $("#syn-rep");
    if (rep) rep.onclick = async () => {
      const lang = await pickReportLang(); if (!lang) return;
      rep.disabled = true; rep.innerHTML = `<span class="spinner"></span>`; toast(T("report_wait"));
      try {
        const r = await post("/api/synastry/report", { a: S.synResult.a, b: S.synResult.b, lang });
        S.synResult.report_quota = r.quota; toast(T("queued").replace("{n}", r.position)); haptic("heavy"); VIEWS.synastry();
      } catch (e) {
        if (e.message === "report_quota") { S.synResult.report_quota.left = 0; S.synResult.report_quota.credits = 0; VIEWS.synastry(); toast(T("syn_report_quota")); }
        else { toast(e.message === "report_in_progress" ? T("in_progress") : T("err") + e.message); rep.disabled = false; rep.textContent = T("syn_report"); }
      }
    };
    const buy = $("#syn-buy");
    if (buy) buy.onclick = async () => {
      buy.disabled = true;
      try {
        const { link } = await post("/api/synastry/report/invoice");
        const done = (status) => { buy.disabled = false; if (status === "paid") { S.synResult.report_quota.credits = (S.synResult.report_quota.credits || 0) + 1; toast(T("syn_report_paid")); VIEWS.synastry(); } };
        if (tg && tg.openInvoice) tg.openInvoice(link, done); else { openTg(link); buy.disabled = false; }
      } catch (e) { toast(T("err") + e.message); buy.disabled = false; }
    };
  }

  async function runSynastry() {
    const a = +$("#sa").value, b = +$("#sb").value;
    if (a === b) return toast(T("syn_same"));
    S.synA = a; S.synB = b;
    const btn = $("#syn-go"); btn.disabled = true;
    let ticket = null;
    try {
      await refreshSession().catch(() => {});
      if (!isPrem()) {
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
      toast(msg); btn.disabled = false; btn.textContent = isPrem() ? T("syn_go") : T("syn_go_ad");
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
      <div><label for="d-sign">${T("sign_pick")}</label><select id="d-sign">${hasProfile ? `<option value="" ${d.follow_main ? "selected" : ""}>${T("sign_auto")}${mainName() ? ` (⭐ ${esc(mainName())})` : ""}</option>` : ""}
        ${T("signs").map((s, i) => `<option value="${i}" ${d.sign === i && !d.follow_main ? "selected" : ""}>${GLYPHS[i]} ${s}</option>`).join("")}</select></div></div>
      <label for="d-tz">${T("tz")}</label><select id="d-tz">${tzs.map((z) => `<option ${z === tzOk ? "selected" : ""}>${z}</option>`).join("")}</select>
      <button class="btn block" id="d-save">${T("save")}</button></div>
      <button class="card week-link" id="go-week"><span class="wl-ic" aria-hidden="true">🗓</span><span><b>${T("week_title")}</b><small class="muted">${T("week_sub")}</small></span><span aria-hidden="true">‹</span></button>
      <section class="card" id="today"><div class="row between"><h3>${T("today_h")}</h3>
        <select id="t-sign" aria-label="${T("sign_pick")}">${T("signs").map((s, i) => `<option value="${i}" ${(d.sign ?? 0) === i ? "selected" : ""}>${GLYPHS[i]} ${s}</option>`).join("")}</select></div>
        <div id="t-body" class="reading">${skeleton(2)}</div></section>`;
    const loadToday = async () => {
      try {
        const r = await api(`/api/daily/today?tz=${encodeURIComponent($("#d-tz").value)}&sign=${$("#t-sign").value}&lang=${S.lang}`);
        $("#t-body").innerHTML = r.available ? `${r.overview ? `<p class="muted small">${r.overview}</p>` : ""}<div>${r.html}</div><p class="muted small">${T("tz_note")} <span dir="ltr">${esc(r.tz)}</span></p>`
          : `<p class="muted">${T("today_none")}</p>`;
      } catch (e) { $("#t-body").innerHTML = `<p class="muted">${T("err")}${esc(e.message)}</p>`; }
    };
    $("#t-sign").onchange = loadToday; $("#d-tz").onchange = loadToday; loadToday();
    $("#go-week").onclick = () => setTab("weekly");
    $("#d-save").onclick = async () => {
      const sign = $("#d-sign").value;
      try {
        S.session.daily = await post("/api/daily", { subscribed: $("#d-on").checked, send_time: $("#d-time").value || "08:00",
          tz: $("#d-tz").value, sign: sign === "" ? null : +sign });
        toast(T("saved")); haptic("medium");
      } catch (e) { toast(T("err") + e.message); }
    };
  };

  /* ───────────── invite friends ───────────── */
  VIEWS.invite = async function renderInvite() {
    $("#view").innerHTML = skeleton(3);
    const st = await api("/api/invite");
    if (S.tab !== "invite") return;
    $("#view").innerHTML = `<section class="prem-hero"><div class="star" aria-hidden="true">🎁</div><h2>${T("inv_title")}</h2><p class="muted">${T("inv_sub")}</p></section>
      <div class="kpis three"><div class="kpi"><b class="num">${st.invited}</b><span>${T("inv_invited")}</span></div><div class="kpi"><b class="num">${st.active}</b><span>${T("inv_active")}</span></div><div class="kpi"><b class="num">${st.days}</b><span>${T("inv_days")}</span></div></div>
      <div class="card form"><label>${T("inv_link")}</label><div class="row"><input id="inv-link" dir="ltr" readonly value="${esc(st.link)}"><button class="btn small ghost" id="inv-copy">${T("inv_copy")}</button></div>
      <button class="btn block big mt8" id="inv-share">${T("inv_share")}</button><p class="muted small">${T("inv_how")}</p></div>`;
    $("#inv-share").onclick = () => { haptic(); openTg(`https://t.me/share/url?url=${encodeURIComponent(st.link)}&text=${encodeURIComponent(T("inv_share_text"))}`); };
    $("#inv-copy").onclick = async () => { try { await navigator.clipboard.writeText(st.link); } catch (e) { $("#inv-link").select(); document.execCommand("copy"); } toast(T("inv_copied")); };
  };

  /* ───────────── weekly electional picks (premium, protected view) ───────────── */
  VIEWS.weekly = async function renderWeekly() {
    const tz = (S.session.daily && S.session.daily.tz) || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Damascus";
    $("#view").innerHTML = skeleton(4);
    let w;
    try { w = await api(`/api/weekly?tz=${encodeURIComponent(tz)}&lang=${S.lang}`); } catch (e) { $("#view").innerHTML = `<p class="muted">${T("err")}${esc(e.message)}</p>`; return; }
    if (S.tab !== "weekly") return;
    const head = `<button class="link back" id="wk-back">› ${T("daily_title")}</button><h2>${T("week_title")}</h2>`;
    if (!w.available) { $("#view").innerHTML = `${head}<p class="muted">${T("week_none")}</p>`; bindBack(); return; }
    const range = `<p class="muted num">${w.week_start}${w.week_end ? " → " + w.week_end : ""}</p>`;
    if (w.locked) {
      $("#view").innerHTML = `${head}${range}<section class="card locked"><p>🔒 ${T("week_locked")}</p><button class="btn block" id="wk-prem">${T("go_premium")}</button></section>`;
      $("#wk-prem").onclick = () => setTab("premium"); bindBack(); return;
    }
    const sec = (s) => s.days
      ? `<h3 class="wk-h">${esc(s.title)}</h3>${s.days.map((d, i) => `<details class="card wk-day" ${i === 0 ? "open" : ""}><summary>${esc(d.title)}</summary>${d.html}</details>`).join("")}`
      : `<section class="card"><h3>${esc(s.title)}</h3>${s.html}</section>`;
    const order = (s) => (/أهم|Top/.test(s.title) ? 0 : /تجنب|Avoid/.test(s.title) ? 1 : /أبرز|Highlights/.test(s.title) ? 2 : /تفصيل|Day/.test(s.title) ? 3 : 4);
    $("#view").innerHTML = `${head}${range}<p class="muted small">${T("week_tz")} <span dir="ltr">${esc(w.tz)}</span></p>
      <div class="protected" id="wk">${[...w.sections].sort((a, b) => order(a) - order(b)).map(sec).join("")}
      ${w.intro ? `<p class="muted small">${w.intro}</p>` : ""}</div>`;
    const box = $("#wk");
    ["copy", "cut", "contextmenu", "selectstart", "dragstart"].forEach((ev) => box.addEventListener(ev, (e) => e.preventDefault()));
    bindBack();
    function bindBack() { $("#wk-back").onclick = () => setTab("daily"); }
  };

  /* ───────────── channels tab ───────────── */
  VIEWS.channels = async function renderChannels() {
    const m = S.session.meta;
    $("#view").innerHTML = `<section class="card promo"><h2>${T("ch_title")}</h2><p class="muted">${T("ch_sub")}</p>
      <div class="row"><button class="btn" id="c-add">📢 ${T("add_channel")}</button><button class="btn ghost" id="g-add">👥 ${T("add_group")}</button></div>
      <p class="muted small">${T("ch_steps")}</p></section>
      <section class="card"><h3>${T("ch_why_h")}</h3><ul class="plain checks">${T("ch_why").map((x) => `<li>${x}</li>`).join("")}</ul>
      <h3>${T("ch_aff_h")}</h3><ol class="steps">${T("ch_aff_steps").map((x) => `<li>${x}</li>`).join("")}</ol></section>
      <h3>${T("my_chats")}</h3><div class="list" id="chats">${skeleton(2)}</div>`;
    $("#c-add").onclick = () => openTg(m.add_channel);
    $("#g-add").onclick = () => openTg(m.add_group);
    const [chats, tzs] = await Promise.all([api("/api/channels"), api("/api/timezones")]);
    const box = $("#chats"); if (!box) return;
    if (!chats.length) { box.innerHTML = `<p class="muted">${T("no_chats")}</p>`; return; }
    box.innerHTML = chats.map((c) => `<div class="card" data-chat="${c.chat_id}"><h4>${esc(c.title || c.chat_id)}</h4>
      <div class="grid2"><input type="time" value="${c.send_time}" data-k="send_time" aria-label="${T("send_time")}">
      <select data-k="lang" aria-label="${T("post_lang")}"><option value="ar" ${c.lang === "ar" ? "selected" : ""}>العربية</option><option value="en" ${c.lang === "en" ? "selected" : ""}>English</option></select></div>
      <select data-k="tz" class="mt8" aria-label="${T("tz")}">${tzs.map((z) => `<option ${z === c.tz ? "selected" : ""}>${z}</option>`).join("")}</select>
      <label class="mt8 small">${T("ch_ref")}</label><input data-k="ref_link" dir="ltr" placeholder="https://t.me/${esc(m.bot)}?start=_tgr_…" value="${esc(c.ref_link || "")}">
      <label class="switch"><input type="checkbox" data-k="active" ${c.active ? "checked" : ""}> ${T("active")}</label>
      <button class="btn small mt8" data-save>${T("save")}</button></div>`).join("");
    box.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
      const it = b.closest("[data-chat]"), g = (k) => it.querySelector(`[data-k="${k}"]`);
      try { await post(`/api/channels/${it.dataset.chat}`, { send_time: g("send_time").value, tz: g("tz").value, lang: g("lang").value, active: g("active").checked, ref_link: g("ref_link").value.trim() || null }); toast(T("saved")); }
      catch (e) { toast(e.message === "bad_ref_link" ? T("ch_ref_bad") : T("err") + e.message); }
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
    const perks = T("prem_perks").map(([b, s], i) => `<li class="${i === 5 ? "soon" : ""}"><b>${b}</b><span>${s}</span></li>`).join("");
    const fd = S.session.founders || {};
    $("#view").innerHTML = `<section class="prem-hero"><div class="star" aria-hidden="true">✦</div><h2>${T("prem_title")}</h2><p class="muted">${T("prem_sub")}</p>
      ${fd.claimed ? `<p class="pill gold">🌟 ${T("fd_badge").replace("{n}", fd.number)}</p>` : ""}</section>${foundersBanner()}
      <ul class="perks">${perks}</ul>
      ${info.active ? `<p class="warn ok">${T("prem_active")}<span class="num">${info.until.slice(0, 10)}</span></p>`
                    : `<button class="btn block big" id="buy">⭐ ${T("prem_buy").replace("{n}", info.stars)}</button>`}
      <div class="card manual mt16"><p class="small">${T("prem_manual")}</p><button class="btn ghost block" id="contact-admin">${T("prem_contact")}</button></div>
      <button class="card invite-cta" data-invite>${T("prem_or_invite")}</button>`;
    $("#contact-admin").onclick = () => { haptic(); openTg(`https://t.me/${S.session.meta.bot}?start=pay`); if (tg && tg.close) setTimeout(() => tg.close(), 300); };
    document.querySelector("[data-invite]").onclick = () => setTab("invite");
    bindFounders();
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
      ${kpi(o.premium, T("k_prem"))}${kpi(o.stars, "⭐ " + T("k_stars"))}${kpi(o.blocked, T("k_blocked"))}
      ${kpi(o.founders, "🌟 " + T("k_founders"))}${kpi(o.invited, T("k_inv"))}${kpi(o.invited_active, T("k_inv_act"))}${kpi(o.reports, T("k_reports"))}${kpi(o.syn_reports, T("k_syn_reports"))}</div>
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
    const ip = await api("/api/admin/interp").catch(() => ({ entries: 0 }));
    $("#admin").innerHTML = `<section class="card form"><h3>${T("interp_h")}</h3>
      <p class="${ip.entries ? "" : "warn"}"><b class="num">${ip.entries}</b> ${T("interp_n")}${ip.version ? ` · <span class="num">v${esc(ip.version)}</span>` : ""}</p>
      <p class="${ip.compat && ip.compat.entries ? "" : "warn"}">${T("compat_db")}: <b class="num">${(ip.compat || {}).entries || 0}</b> ${T("interp_n")}${ip.compat && ip.compat.version ? ` · <span class="num">v${esc(ip.compat.version)}</span>` : ""}</p>
      <label for="ipf">${T("interp_up")}</label><input id="ipf" type="file" accept=".sqlite,.db,.json,.gz">
      <button class="btn mt8" id="ipu">${T("save")}</button></section>
      <p class="warn ${c.has_today ? "ok" : ""}">${c.has_today ? "✅ " + T("today_ok") : "⚠️ " + T("today_missing")}</p>
      <div class="card form"><label for="du">${T("daily_url")}</label><input id="du" dir="ltr" value="${esc(c.daily_url)}">
      <label for="wu">${T("weekly_url")}</label><input id="wu" dir="ltr" value="${esc(c.weekly_url)}">
      <label for="pr">${T("price")}</label><input id="pr" type="number" min="1" max="10000" value="${c.premium_stars}">
      <label for="spr">${T("syn_price")}</label><input id="spr" type="number" min="1" max="10000" value="${c.syn_report_stars}">
      <div class="row mt8"><button class="btn" id="cs">${T("save")}</button><button class="btn ghost" id="cf2">${T("fetch_now")}</button></div></div>
      <section class="card"><h3>${T("fetched_days")}</h3>${c.days.length ? `<ul class="plain">${c.days.map((d) => `<li class="num">${d.day} <small class="muted">· ${d.fetched_at.slice(0, 16).replace("T", " ")}</small></li>`).join("")}</ul>` : `<p class="muted small">${T("no_items")}</p>`}</section>`;
    $("#cs").onclick = async () => {
      try { await post("/api/admin/settings", { daily_url: $("#du").value, weekly_url: $("#wu").value, premium_stars: +$("#pr").value, syn_report_stars: +$("#spr").value }); toast(T("saved")); }
      catch (e) { toast(T("err") + e.message); }
    };
    $("#ipu").onclick = async () => {
      const f = $("#ipf").files[0]; if (!f) return;
      const b = $("#ipu"); b.disabled = true; b.innerHTML = `<span class="spinner"></span>`;
      const fd = new FormData(); fd.append("file", f, f.name);
      const headers = {}; if (DEV) headers.Authorization = "dev " + DEV; else if (tg && tg.initData) headers.Authorization = "tma " + tg.initData;
      try {
        const r = await fetch("/api/admin/interp/upload", { method: "POST", body: fd, headers });
        const d = await r.json(); if (!r.ok) throw new Error(d.detail || r.status);
        toast(T("interp_ok").replace("{n}", d.imported) + (d.kind === "compat" ? " · " + T("compat_db") : "")); adContent();
      } catch (e) { toast(T("err") + e.message); b.disabled = false; b.textContent = T("save"); }
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
      await refreshSession(); S._prem = isPrem();
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
