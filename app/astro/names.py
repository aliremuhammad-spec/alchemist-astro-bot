"""Display names for signs, planets, houses, aspects, nakshatras (Arabic + English)."""

SIGN_KEYS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
SIGN_ABBR = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
SIGN_GLYPH = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
SIGNS = {
    "ar": ["الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء",
           "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت"],
    "en": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
           "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
}

# key -> (glyph, ar, en)
PLANETS = {
    "sun": ("☉", "الشمس", "Sun"),
    "moon": ("☽", "القمر", "Moon"),
    "mercury": ("☿", "عطارد", "Mercury"),
    "venus": ("♀", "الزهرة", "Venus"),
    "mars": ("♂", "المريخ", "Mars"),
    "jupiter": ("♃", "المشتري", "Jupiter"),
    "saturn": ("♄", "زحل", "Saturn"),
    "uranus": ("♅", "أورانوس", "Uranus"),
    "neptune": ("♆", "نبتون", "Neptune"),
    "pluto": ("♇", "بلوتو", "Pluto"),
    "mean_north_lunar_node": ("☊", "العقدة الشمالية", "North Node"),
    "mean_south_lunar_node": ("☋", "العقدة الجنوبية", "South Node"),
    "chiron": ("⚷", "كايرون", "Chiron"),
}
VEDIC_NAMES = {  # Sanskrit-style names used in Vedic context
    "sun": ("Su", "سوريا (الشمس)", "Surya (Sun)"),
    "moon": ("Mo", "شاندرا (القمر)", "Chandra (Moon)"),
    "mars": ("Ma", "مانغالا (المريخ)", "Mangala (Mars)"),
    "mercury": ("Me", "بودها (عطارد)", "Budha (Mercury)"),
    "jupiter": ("Ju", "غورو (المشتري)", "Guru (Jupiter)"),
    "venus": ("Ve", "شوكرا (الزهرة)", "Shukra (Venus)"),
    "saturn": ("Sa", "شاني (زحل)", "Shani (Saturn)"),
    "mean_north_lunar_node": ("Ra", "راهو", "Rahu"),
    "mean_south_lunar_node": ("Ke", "كيتو", "Ketu"),
}
VEDIC_SHORT = {
    "ar": {"sun": "ش", "moon": "ق", "mars": "مر", "mercury": "عط", "jupiter": "مش",
           "venus": "زه", "saturn": "زح", "mean_north_lunar_node": "را", "mean_south_lunar_node": "كي"},
    "en": {"sun": "Su", "moon": "Mo", "mars": "Ma", "mercury": "Me", "jupiter": "Ju",
           "venus": "Ve", "saturn": "Sa", "mean_north_lunar_node": "Ra", "mean_south_lunar_node": "Ke"},
}

ASPECTS = {  # kerykeion name -> (glyph, ar, en)
    "conjunction": ("☌", "اقتران", "Conjunction"),
    "opposition": ("☍", "مقابلة", "Opposition"),
    "trine": ("△", "تثليث", "Trine"),
    "square": ("□", "تربيع", "Square"),
    "sextile": ("⚹", "تسديس", "Sextile"),
    "quincunx": ("⚻", "قينكونكس", "Quincunx"),
    "semi-sextile": ("⚺", "نصف تسديس", "Semi-sextile"),
    "semi-square": ("∠", "نصف تربيع", "Semi-square"),
    "sesquiquadrate": ("⚼", "تربيع ونصف", "Sesquiquadrate"),
    "quintile": ("Q", "خُمسي", "Quintile"),
    "biquintile": ("bQ", "خُمسي مزدوج", "Biquintile"),
}
MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

ELEMENTS = {"ar": {"fire": "نار", "earth": "تراب", "air": "هواء", "water": "ماء"},
            "en": {"fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water"}}
QUALITIES = {"ar": {"cardinal": "كاردينال", "fixed": "ثابت", "mutable": "متحول"},
             "en": {"cardinal": "Cardinal", "fixed": "Fixed", "mutable": "Mutable"}}

MOON_PHASES = {
    "New Moon": "محاق", "Waxing Crescent": "هلال متزايد", "First Quarter": "تربيع أول",
    "Waxing Gibbous": "أحدب متزايد", "Full Moon": "بدر", "Waning Gibbous": "أحدب متناقص",
    "Last Quarter": "تربيع أخير", "Third Quarter": "تربيع أخير", "Waning Crescent": "هلال متناقص",
}

NAKSHATRAS = [
    ("Ashwini", "أشويني"), ("Bharani", "بهاراني"), ("Krittika", "كريتيكا"), ("Rohini", "روهيني"),
    ("Mrigashira", "مريغاشيرا"), ("Ardra", "أردرا"), ("Punarvasu", "بونارفاسو"), ("Pushya", "بوشيا"),
    ("Ashlesha", "أشليشا"), ("Magha", "ماغا"), ("Purva Phalguni", "بورفا فالغوني"),
    ("Uttara Phalguni", "أوتارا فالغوني"), ("Hasta", "هاستا"), ("Chitra", "تشيترا"), ("Swati", "سواتي"),
    ("Vishakha", "فيشاكا"), ("Anuradha", "أنورادا"), ("Jyeshtha", "جييشتا"), ("Mula", "مولا"),
    ("Purva Ashadha", "بورفا أشادا"), ("Uttara Ashadha", "أوتارا أشادا"), ("Shravana", "شرافانا"),
    ("Dhanishta", "دانيشتا"), ("Shatabhisha", "شاتابيشا"), ("Purva Bhadrapada", "بورفا بادرابادا"),
    ("Uttara Bhadrapada", "أوتارا بادرابادا"), ("Revati", "ريفاتي"),
]
DASHA_LORDS = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
DASHA_YEARS = {"ketu": 7, "venus": 20, "sun": 6, "moon": 10, "mars": 7,
               "rahu": 18, "jupiter": 16, "saturn": 19, "mercury": 17}
DASHA_NAMES = {
    "ketu": ("كيتو", "Ketu"), "venus": ("الزهرة", "Venus"), "sun": ("الشمس", "Sun"),
    "moon": ("القمر", "Moon"), "mars": ("المريخ", "Mars"), "rahu": ("راهو", "Rahu"),
    "jupiter": ("المشتري", "Jupiter"), "saturn": ("زحل", "Saturn"), "mercury": ("عطارد", "Mercury"),
}

CONTINENTS = {
    "AS": ("آسيا", "Asia"), "AF": ("أفريقيا", "Africa"), "EU": ("أوروبا", "Europe"),
    "NA": ("أمريكا الشمالية", "North America"), "SA": ("أمريكا الجنوبية", "South America"),
    "OC": ("أوقيانوسيا", "Oceania"), "AN": ("القارة القطبية الجنوبية", "Antarctica"),
}


def sign_name(idx: int, lang: str) -> str:
    return SIGNS["ar" if lang == "ar" else "en"][idx % 12]


def planet_name(key: str, lang: str) -> str:
    g, ar, en = PLANETS[key]
    return ar if lang == "ar" else en
