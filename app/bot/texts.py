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
            "💡 تبعتلنا اقتراحاتك لتطوير البوت\n\n"
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
            "💳 <b>طرق دفع تانية للاشتراك المميز</b>\n"
            "اكتبلنا برسالة وحدة من وين إنت وشو طريقة الدفع اللي بتناسبك، والإدارة بترد عليك هون.\n(للإلغاء: /cancel)"
        ),
        "pay_thanks": "✅ وصلت رسالتك للإدارة، رح نرد عليك قريباً.",
        "help": (
            "🔭 /app فتح التطبيق\n🎁 /invite ادعُ أصحابك واربح أيام مميز\n📢 /channel الأبراج لقناتك أو مجموعتك\n💡 /suggest اقتراح للتطوير\n"
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
            "💡 Send us your ideas to improve the bot\n\n"
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
            "💳 <b>Other ways to pay for Premium</b>\n"
            "Tell us in one message where you are and which payment method suits you; the team will reply here.\n(/cancel to stop)"
        ),
        "pay_thanks": "✅ Your message reached the team; we'll reply soon.",
        "help": "🔭 /app open the app\n🎁 /invite invite friends, earn Premium days\n📢 /channel horoscopes for your channel\n💡 /suggest suggest an improvement\nℹ️ /about about & source code",
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
