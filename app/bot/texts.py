"""Bot message texts (Arabic default, English)."""
from ..config import settings

T = {
    "ar": {
        "welcome": (
            "✨ أهلاً {name}، أنا <b>بوت الخيميائي للفلك</b>.\n"
            "🧪 <i>هذه نسخة تجريبية (Beta) من تطوير الخيميائي.</i>\n\n"
            "مع البوت بتقدر:\n"
            "🔭 تطلع خارطتك الفلكية بالنظامين الغربي والفيدي، بالشكل الهندي الشمالي أو الجنوبي\n"
            "🌅 تشترك بالأبراج اليومية بالوقت اللي بيناسبك\n"
            "📢 تضيف البوت لقناتك أو مجموعتك لينشر الأبراج كل يوم تلقائياً\n"
            "🎁 تدعي أصحابك: كل صديق بيوصله تقرير فلكي مجاني، وإنت بتاخد 3 أيام مميز عن كل صديق نشط (/invite)\n"
            "💡 تبعتلنا اقتراحاتك لتطوير البوت\n"
            "✍️ تكتب @{bot} بأي محادثة: برجك، أو «القمر في الأسد»، أو «الاختيارات الأسبوعية»\n\n"
            "📸 وتابعنا على إنستغرام حتى توصلك كل الأخبار الفلكية أول بأول 👇"
        ),
        "open_app": "🔭 افتح التطبيق",
        "follow_main": "📸 تابع الخيميائي",
        "follow_partner": "📜 تابع {label}",
        "add_channel": "📢 أضفني لقناتك",
        "add_group": "👥 أضفني لمجموعتك",
        "suggest_btn": "💡 اقتراح للتطوير",
        "suggest_prompt": "💡 اكتب اقتراحك أو ملاحظتك برسالة وحدة، وبتوصل مباشرة للمطوّر.\n(للإلغاء: /cancel)",
        "suggest_thanks": "🙏 شكراً! وصل اقتراحك للمطوّر.",
        "cancelled": "تم الإلغاء.",
        "channel_info": (
            "📢 <b>الأبراج اليومية لقناتك أو مجموعتك</b>\n\n"
            "<b>شو بتستفيد إنت؟</b>\n"
            "• محتوى يومي جاهز ومجاني: البوت بينشر أبراج الـ12 برج كل يوم لحاله، بالساعة واللغة اللي بتختارها.\n"
            "• الأوقات بالمنشور بتنحوّل لتوقيت جمهورك، فما في داعي تعدّل شي.\n"
            "• منشور ثابت كل يوم بيخلي قناتك حيّة وبيرفع التفاعل.\n"
            "• 💰 <b>عمولة 20% بالنجوم</b>: انضم لبرنامج الإحالة تبع البوت، وكل متابع بيفوت من رابطك بتاخد 20% من النجوم "
            "اللي بيدفعها لمدة 3 شهور. تلغرام بيحوّلها لرصيدك مباشرة.\n"
            "• بتوقف النشر أو بتغيّر الإعدادات بأي وقت من التطبيق (تبويب «قنواتي»).\n\n"
            "<b>كيف بتربطها؟</b>\n"
            "1. اضغط الزر تحت واختار القناة أو المجموعة.\n"
            "2. بالقنوات لازم يكون البوت مشرف مع صلاحية «نشر الرسائل» بس.\n"
            "3. للعمولة: من تلغرام افتح بروفايل البوت ← «برنامج الإحالة» (أو الإعدادات ← نجومي ← اربح نجوم) ← انضم، وانسخ رابطك وحطه بالتطبيق ← قنواتي. "
            "هيك كل منشور يومي بيحمل رابطك.\n\n"
            "مجاني بالكامل 🤍"
        ),
        "chat_added_dm": "✅ تم ربط «{title}». رح ينشر البوت الأبراج اليومية فيها كل يوم الساعة {time} ({tz}). بتقدر تغيّر الوقت من التطبيق ← قنواتي.",
        "chat_added_post": "✨ تم تفعيل <b>الأبراج اليومية</b> هنا بواسطة @{bot}.\nرح تنشر كل يوم الساعة {time}.",
        "chat_need_admin": "⚠️ لازم تخلّي البوت مشرف بالقناة مع صلاحية «نشر الرسائل» حتى يقدر ينشر الأبراج.",
        "daily_title": "🌅 <b>برجك اليوم · {sign} {glyph}</b>\n<i>{date}</i>",
        "digest_title": "🔮 <b>أبراج اليوم</b> · {date}",
        "inline_daily": "أهلاً {name} 👋 وصلت من رسالة برج اليوم.\nبالتطبيق بتطلع خارطتك الكاملة مجاناً، وبتشترك ببرجك اليومي ليوصلك كل يوم بالساعة اللي بتناسبك وبتوقيتك 👇",
        "inline_weekly": "أهلاً {name} 👋 الاختيارات الفلكية الأسبوعية مجانية بالتطبيق: أفضل الأوقات للبدايات والعقود والسفر، والأوقات اللي يُفضّل تتجنبها، كلها بتوقيتك 👇",
        "inline_place": "أهلاً {name} 👋 هالتفسير جزء صغير من خارطتك. احسب خارطتك الكاملة مجاناً بالتطبيق وشوف وين كواكبك كلها وشو بتعني 👇",
        "start_daily": "🌅 فعّل برجك اليومي من التطبيق: اختار برجك والساعة اللي بتناسبك، والأوقات بتوصلك بتوقيتك المحلي.",
        "start_weekly": "🗓 الاختيارات الفلكية الأسبوعية: أفضل الأوقات للبدايات والعقود والسفر، محوّلة لتوقيتك.",
        "digest_more": "📖 التوقعات الكاملة لبرجك (عاطفية، مالية، مهنية) بتوصلك كل يوم عالخاص: {link}",
        "digest_footer": "🤖 من @{bot} · أضف الأبراج اليومية لقناتك مجاناً: {link}",
        "daily_footer": "📢 عندك قناة أو مجموعة؟ ضيف البوت لينشر الأبراج كل يوم تلقائياً.",
        "invite_info": (
            "🎁 <b>ادعُ أصحابك للخيميائي</b>\n\n"
            "• صديقك بياخد <b>تقرير فلكي مجاني</b> لخارطته (غربي + فيدي، PDF).\n"
            "• وإنت بتاخد <b>3 أيام مميز</b> عن كل صديق بيصير نشط: بيحفظ خارطته وبيرجع للبوت بيوم تاني.\n\n"
            "رابطك الخاص:\n{link}\n\n"
            "لحد هلأ: دعيت {invited}، النشطين {active}، وربحت {days} يوم."
        ),
        "invite_share": "📤 شارك الرابط",
        "invite_share_text": "طلعت خارطتي الفلكية بالخيميائي 🔭 جرّب إنت كمان، وبيوصلك تقرير فلكي مجاني لخارطتك 🎁",
        "ref_gift": (
            "🎁 <b>وصلتك هدية من صديقك:</b> تقرير فلكي مجاني لخارطتك!\n"
            "افتح التطبيق، احسب خارطتك، واضغط «📄 تقرير فلكي PDF»."
        ),
        "pay_prompt": (
            "💳 <b>طرق دفع تانية</b>\n"
            "تلغرام بيسمح ندفع للخدمات الرقمية بالبوت <b>بنجوم تلغرام ⭐ بس</b>. إذا ما فيك تشتري نجوم مباشرة، "
            "فيك تشتريها من <b>وسيط</b> بالطريقة اللي بتناسبك، وبتوصل النجوم لحسابك، وبعدها بتدفع فيها هون عادي.\n\n"
            "{list}\n"
            "⚠️ الوسطاء جهات مستقلة ومنن تابعين إلنا، فما منضمنن. ابدأ بكمية صغيرة، ولا تعطي حدا كلمة سرك أو كود الدخول؛ "
            "الوسيط بيحتاج اسم المستخدم (@username) بس.\n\n"
            "ما زبطت معك ولا طريقة؟ اضغط «تواصل مع الإدارة» واكتبلنا من وين إنت."
        ),
        "pay_contact": "💬 تواصل مع الإدارة",
        "pay_write": "اكتبلنا برسالة وحدة من وين إنت وشو طريقة الدفع اللي بتناسبك، والإدارة بترد عليك هون.\n(للإلغاء: /cancel)",
        "ps_intro": (
            "🧾 <b>دعم الدفعات</b>\n{list}\n\n"
            "اكتب مشكلتك برسالة وحدة (مثلاً: دفعت وما تفعّل الاشتراك، أو بدك استرداد ولّيش)، وبتوصل مباشرة للإدارة "
            "مع تفاصيل دفعاتك. منرد عليك هون خلال 48 ساعة.\n(للإلغاء: /cancel)"
        ),
        "ps_none": "ما لقينا أي دفعة بنجوم تلغرام على حسابك.",
        "ps_row": "• {date} · {stars}⭐ · {what}{ref}",
        "ps_refunded": " · ↩️ مسترَدة",
        "ps_thanks": "✅ وصل طلبك لإدارة الدفعات، رح نرد عليك هون قريباً.",
        "ps_refund_done": "↩️ تم استرداد {stars} نجمة لحسابك. رح تشوفها برصيد نجومك بتلغرام.",
        "what_premium": "اشتراك مميز",
        "what_natrep": "تقرير فلكي",
        "what_synrep": "تقرير توافق",
        "del_confirm": (
            "🗑 <b>مسح بياناتي</b>\n"
            "رح ينمسح فوراً ونهائياً: حسابك، {n} خارطة، إعدادات الأبراج اليومية، الدعوات، رسائلك وسجل استخدامك.{prem}\n"
            "بيضل بس سجل الدفعات (للاسترداد) وبصمة مشفّرة بتمنع تكرار الهدايا. التفاصيل: {url}\n\n"
            "متأكد؟"
        ),
        "del_prem": "\n⚠️ <b>اشتراكك المميز الحالي رح ينتهي وما بيرجع.</b>",
        "del_yes": "🗑 إي، امسح كل شي",
        "del_no": "↩️ لا، تراجع",
        "del_done": "✅ انمسحت بياناتك. إذا رجعت استخدمت البوت بيبدأ حساب جديد فاضي. منتمنالك الخير ✨",
        "del_admin": "حسابات الإدارة ما بتنمسح من هون.",
        "privacy": "🔐 <b>سياسة الخصوصية</b>\nشو منجمع وليش وكيف تمسحه:\n{url}\n\nلمسح كل بياناتك: /deletemydata",
        "pay_thanks": "✅ وصلت رسالتك للإدارة، رح نرد عليك قريباً.",
        "help": (
            "✍️ اكتب @{bot} بأي محادثة: برجك، أو «القمر في الأسد»، أو «الاختيارات الأسبوعية»\n"
            "🔭 /app فتح التطبيق\n🎁 /invite ادعُ أصحابك واربح أيام مميز\n📢 /channel الأبراج لقناتك أو مجموعتك\n💡 /suggest اقتراح للتطوير\n"
            "🧾 /paysupport دعم الدفعات والاسترداد\n🔐 /privacy سياسة الخصوصية · /deletemydata مسح بياناتي\n"
            "ℹ️ /about عن البوت والكود المصدري"
        ),
        "about": (
            "🧪 <b>بوت الخيميائي للفلك</b> · نسخة تجريبية (Beta) من تطوير الخيميائي.\n\n"
            "الحسابات بمكتبة Swiss Ephemeris عبر kerykeion. الكود مفتوح المصدر بترخيص AGPL-3.0:\n{source}\n\n"
            "المحتوى للتأمل والترفيه، ولا يغني عن استشارة مختص بالقرارات المهمة."
        ),
        "chart_caption": "🔭 خارطة {name}",
    },
    "en": {
        "welcome": (
            "✨ Hi {name}, I'm <b>The Alchemist Astro bot</b>.\n"
            "🧪 <i>This is a beta version developed by The Alchemist.</i>\n\n"
            "Here you can:\n"
            "🔭 Cast your birth chart in Western and Vedic systems (North or South Indian style)\n"
            "🌅 Get your daily horoscope at a time you choose\n"
            "📢 Add the bot to your channel or group to post daily horoscopes automatically\n"
            "🎁 Invite friends: each friend gets a free astrological report, you get 3 Premium days per active friend (/invite)\n"
            "💡 Send us your ideas to improve the bot\n"
            "✍️ Type @{bot} in any chat: your sign, “Moon in Leo”, or “weekly picks”\n\n"
            "📸 Follow us on Instagram for astro news 👇"
        ),
        "open_app": "🔭 Open the app",
        "follow_main": "📸 Follow The Alchemist",
        "follow_partner": "📜 Follow {label}",
        "add_channel": "📢 Add me to your channel",
        "add_group": "👥 Add me to your group",
        "suggest_btn": "💡 Suggest an improvement",
        "suggest_prompt": "💡 Write your suggestion in one message and it goes straight to the developer.\n(/cancel to stop)",
        "suggest_thanks": "🙏 Thanks! Your suggestion reached the developer.",
        "cancelled": "Cancelled.",
        "channel_info": (
            "📢 <b>Daily horoscopes for your channel or group</b>\n\n"
            "<b>What you get</b>\n"
            "• Free daily content: the bot posts all 12 signs every day on its own, at the time and language you choose.\n"
            "• Times in the post are converted to your audience's time zone.\n"
            "• A steady daily post keeps the channel alive and lifts engagement.\n"
            "• 💰 <b>20% commission in Stars</b>: join the bot's affiliate program and earn 20% of the Stars spent by "
            "everyone who arrives through your link, for 3 months. Telegram pays it straight to your balance.\n"
            "• Pause or change it any time in the app (My channels).\n\n"
            "<b>How to connect</b>\n"
            "1. Tap the button below and pick the channel or group.\n"
            "2. In channels the bot only needs admin rights to “Post messages”.\n"
            "3. For the commission: open the bot's profile in Telegram → Affiliate program (or Settings → My Stars → Earn Stars) → Join, copy your link and paste it "
            "in the app → My channels, so every daily post carries it.\n\n"
            "Completely free 🤍"
        ),
        "chat_added_dm": "✅ “{title}” is connected. Daily horoscopes will be posted there every day at {time} ({tz}). Change it in the app → My channels.",
        "chat_added_post": "✨ <b>Daily horoscopes</b> are now enabled here by @{bot}.\nPosted every day at {time}.",
        "chat_need_admin": "⚠️ Make the bot an admin with “Post messages” permission so it can post horoscopes.",
        "daily_title": "🌅 <b>Your day · {sign} {glyph}</b>\n<i>{date}</i>",
        "digest_title": "🔮 <b>Today's horoscopes</b> · {date}",
        "inline_daily": "Hi {name} 👋 you came from a daily horoscope message.\nIn the app you get your full chart for free, and can subscribe to your daily horoscope at the hour you like, in your time zone 👇",
        "inline_weekly": "Hi {name} 👋 the weekly electional picks are free in the app: the best windows for beginnings, contracts and travel, plus times to avoid, all in your time zone 👇",
        "inline_place": "Hi {name} 👋 that reading is one small piece of a chart. Cast your full chart for free in the app and see where all your planets are and what they mean 👇",
        "start_daily": "🌅 Turn on your daily horoscope in the app: pick your sign and time; times arrive in your local zone.",
        "start_weekly": "🗓 Weekly electional picks: the best windows for beginnings, contracts and travel, in your time zone.",
        "digest_more": "📖 Your sign's full reading (love, money, career) in private, every day: {link}",
        "digest_footer": "🤖 By @{bot} · Add free daily horoscopes to your channel: {link}",
        "daily_footer": "📢 Have a channel or group? Add the bot to post horoscopes there every day.",
        "invite_info": (
            "🎁 <b>Invite friends to The Alchemist</b>\n\n"
            "• Your friend gets a <b>free astrological report</b> of their chart (Western + Vedic, PDF).\n"
            "• You get <b>3 Premium days</b> for every friend who becomes active: saves a chart and comes back another day.\n\n"
            "Your link:\n{link}\n\n"
            "So far: {invited} invited, {active} active, {days} days earned."
        ),
        "invite_share": "📤 Share the link",
        "invite_share_text": "I cast my birth chart with The Alchemist 🔭 Try it and get a free astrological report of yours 🎁",
        "ref_gift": (
            "🎁 <b>A gift from your friend:</b> a free astrological report of your chart!\n"
            "Open the app, cast your chart and tap “📄 Astrological report PDF”."
        ),
        "pay_prompt": (
            "💳 <b>Other payment methods</b>\n"
            "Telegram only allows digital services in bots to be paid with <b>Telegram Stars ⭐</b>. If you can't buy Stars "
            "directly, buy them from a <b>reseller</b> with a method that suits you; the Stars land in your account and you "
            "pay here as usual.\n\n{list}\n"
            "⚠️ Resellers are independent and not affiliated with us, so we can't guarantee them. Start small and never "
            "share your password or login code; a reseller only needs your @username.\n\n"
            "None of these work for you? Tap “Contact the team” and tell us where you are."
        ),
        "pay_contact": "💬 Contact the team",
        "pay_write": "Tell us in one message where you are and which payment method suits you; the team will reply here.\n(/cancel to stop)",
        "ps_intro": (
            "🧾 <b>Payment support</b>\n{list}\n\n"
            "Describe the problem in one message (e.g. you paid and Premium didn't activate, or you want a refund and why). "
            "It goes straight to the team with your payment details. We reply here within 48 hours.\n(/cancel to stop)"
        ),
        "ps_none": "We found no Telegram Stars payments on your account.",
        "ps_row": "• {date} · {stars}⭐ · {what}{ref}",
        "ps_refunded": " · ↩️ refunded",
        "ps_thanks": "✅ Your request reached the payments team; we'll reply here soon.",
        "ps_refund_done": "↩️ {stars} Stars were refunded to your account. You'll see them in your Telegram Stars balance.",
        "what_premium": "Premium",
        "what_natrep": "Astrological report",
        "what_synrep": "Compatibility report",
        "del_confirm": (
            "🗑 <b>Delete my data</b>\n"
            "This immediately and permanently deletes your account, {n} chart(s), daily horoscope settings, invites, "
            "messages and usage history.{prem}\n"
            "Only payment records (for refunds) and an encrypted fingerprint that blocks repeat gifts remain. Details: {url}\n\n"
            "Are you sure?"
        ),
        "del_prem": "\n⚠️ <b>Your active Premium will end and is not refunded.</b>",
        "del_yes": "🗑 Yes, delete everything",
        "del_no": "↩️ No, keep it",
        "del_done": "✅ Your data has been deleted. If you use the bot again it starts a fresh, empty account. All the best ✨",
        "del_admin": "Admin accounts can't be erased from here.",
        "privacy": "🔐 <b>Privacy policy</b>\nWhat we collect, why, and how to delete it:\n{url}\n\nTo delete all your data: /deletemydata",
        "pay_thanks": "✅ Your message reached the team; we'll reply soon.",
        "help": "✍️ Type @{bot} in any chat: your sign, “Moon in Leo”, or “weekly picks”\n🔭 /app open the app\n🎁 /invite invite friends, earn Premium days\n📢 /channel horoscopes for your channel\n💡 /suggest suggest an improvement\n🧾 /paysupport payment support & refunds\n🔐 /privacy privacy policy · /deletemydata delete my data\nℹ️ /about about & source code",
        "about": (
            "🧪 <b>The Alchemist Astro</b> · beta, developed by The Alchemist.\n\n"
            "Calculations use the Swiss Ephemeris via kerykeion. Open source under AGPL-3.0:\n{source}\n\n"
            "Content is for reflection and entertainment, not a substitute for professional advice."
        ),
        "chart_caption": "🔭 {name}'s chart",
    },
}


def t(lang: str, key: str, **kw) -> str:
    lang = "en" if lang == "en" else "ar"
    return T[lang][key].format(bot=settings.bot_username, **kw)


def add_channel_link() -> str:
    return f"https://t.me/{settings.bot_username}?startchannel=true&admin=post_messages"


def add_group_link() -> str:
    return f"https://t.me/{settings.bot_username}?startgroup=true"
