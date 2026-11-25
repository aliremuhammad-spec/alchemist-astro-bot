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
            "💡 تبعتلنا اقتراحاتك لتطوير البوت\n\n"
            "📸 وتابعنا على إنستغرام حتى توصلك كل الأخبار الفلكية أول بأول 👇"
        ),
        "open_app": "🔭 افتح التطبيق",
        "follow_main": "📸 تابع @{ig}",
        "follow_partner": "📜 تابع {label}",
        "add_channel": "📢 أضفني لقناتك",
        "add_group": "👥 أضفني لمجموعتك",
        "suggest_btn": "💡 اقتراح للتطوير",
        "suggest_prompt": "💡 اكتب اقتراحك أو ملاحظتك برسالة وحدة، وبتوصل مباشرة للمطوّر.\n(للإلغاء: /cancel)",
        "suggest_thanks": "🙏 شكراً! وصل اقتراحك للمطوّر.",
        "cancelled": "تم الإلغاء.",
        "channel_info": (
            "📢 <b>الأبراج اليومية لقناتك أو مجموعتك</b>\n\n"
            "1. اضغط الزر تحت واختار القناة أو المجموعة.\n"
            "2. بالقنوات لازم يكون البوت مشرف مع صلاحية نشر الرسائل.\n"
            "3. البوت بينشر أبراج اليوم كاملة كل يوم الساعة 09:00، وبتقدر تغيّر الوقت من التطبيق (تبويب «قنواتي»).\n\n"
            "مجاناً بالكامل 🤍"
        ),
        "chat_added_dm": "✅ تم ربط «{title}». رح ينشر البوت الأبراج اليومية فيها كل يوم الساعة {time} ({tz}). بتقدر تغيّر الوقت من التطبيق ← قنواتي.",
        "chat_added_post": "✨ تم تفعيل <b>الأبراج اليومية</b> هنا بواسطة @{bot}.\nرح تنشر كل يوم الساعة {time}.",
        "chat_need_admin": "⚠️ لازم تخلّي البوت مشرف بالقناة مع صلاحية «نشر الرسائل» حتى يقدر ينشر الأبراج.",
        "daily_title": "🌅 <b>برجك اليوم · {sign} {glyph}</b>\n<i>{date}</i>",
        "digest_title": "🔮 <b>أبراج اليوم</b> · {date}",
        "digest_footer": "🤖 من @{bot} · أضف الأبراج اليومية لقناتك مجاناً: {link}",
        "daily_footer": "📢 عندك قناة أو مجموعة؟ ضيف البوت لينشر الأبراج كل يوم تلقائياً.",
        "help": (
            "🔭 /app فتح التطبيق\n📢 /channel الأبراج لقناتك أو مجموعتك\n💡 /suggest اقتراح للتطوير\n"
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
            "💡 Send us your ideas to improve the bot\n\n"
            "📸 Follow us on Instagram for astro news 👇"
        ),
        "open_app": "🔭 Open the app",
        "follow_main": "📸 Follow @{ig}",
        "follow_partner": "📜 Follow {label}",
        "add_channel": "📢 Add me to your channel",
        "add_group": "👥 Add me to your group",
        "suggest_btn": "💡 Suggest an improvement",
        "suggest_prompt": "💡 Write your suggestion in one message and it goes straight to the developer.\n(/cancel to stop)",
        "suggest_thanks": "🙏 Thanks! Your suggestion reached the developer.",
        "cancelled": "Cancelled.",
        "channel_info": (
            "📢 <b>Daily horoscopes for your channel or group</b>\n\n"
            "1. Tap the button below and pick the channel or group.\n"
            "2. In channels the bot must be an admin allowed to post messages.\n"
            "3. The bot posts all 12 signs every day at 09:00; change the time in the app (My channels).\n\n"
            "Completely free 🤍"
        ),
        "chat_added_dm": "✅ “{title}” is connected. Daily horoscopes will be posted there every day at {time} ({tz}). Change it in the app → My channels.",
        "chat_added_post": "✨ <b>Daily horoscopes</b> are now enabled here by @{bot}.\nPosted every day at {time}.",
        "chat_need_admin": "⚠️ Make the bot an admin with “Post messages” permission so it can post horoscopes.",
        "daily_title": "🌅 <b>Your day · {sign} {glyph}</b>\n<i>{date}</i>",
        "digest_title": "🔮 <b>Today's horoscopes</b> · {date}",
        "digest_footer": "🤖 By @{bot} · Add free daily horoscopes to your channel: {link}",
        "daily_footer": "📢 Have a channel or group? Add the bot to post horoscopes there every day.",
        "help": "🔭 /app open the app\n📢 /channel horoscopes for your channel\n💡 /suggest suggest an improvement\nℹ️ /about about & source code",
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
