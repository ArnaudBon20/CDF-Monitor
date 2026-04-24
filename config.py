"""Configuration du monitoring CDF/EFK."""

# Mots-clés à rechercher (insensible à la casse)
# Les mots courts (≤4 car.) sont recherchés avec word boundary pour éviter les faux positifs
KEYWORDS = [
    "CDF",
    "EFK",
    "Contrôle fédéral des finances",
    "Eidgenössische Finanzkontrolle",
    "Controllo federale delle finanze",
    "Federal Audit Office",
    "Finanzkontrolle",
]

# Channels Telegram publics à surveiller (sans @)
# Seuls les channels avec preview web publique (t.me/s/...) fonctionnent
TELEGRAM_CHANNELS = [
    "swissinfofrench",       # SWI swissinfo.ch — news suisses (FR)
    "swissinfoenglish",      # SWI swissinfo.ch — news suisses (EN)
    "nebelspalterOnline",    # Nebelspalter — politique suisse (DE)
    "insideparadeplatz",     # Inside Paradeplatz — finance suisse (DE)
    "schweizermonat",        # Schweizer Monat — analyse politique (DE)
]

# Subreddits Reddit à surveiller
REDDIT_SUBREDDITS = [
    "Switzerland",
    "suisse",
    "schweiz",
    "SwissPolitics",
]

# Flux RSS des médias suisses {nom: url}
# Seuls les flux testés et fonctionnels sont inclus
RSS_FEEDS = {
    # Deutsch
    "SRF News Schweiz": "https://www.srf.ch/news/bnf/rss/1890",
    "SRF Wirtschaft": "https://www.srf.ch/news/bnf/rss/1926",
    "NZZ Schweiz": "https://www.nzz.ch/schweiz.rss",
    "NZZ Wirtschaft": "https://www.nzz.ch/wirtschaft.rss",
    "NZZ Finanzen": "https://www.nzz.ch/finanzen.rss",
    "Blick Politik": "https://www.blick.ch/politik/rss.xml",
    "Blick News": "https://www.blick.ch/news/rss",
    # Français
    "Le Temps": "https://www.letemps.ch/feed",
}
