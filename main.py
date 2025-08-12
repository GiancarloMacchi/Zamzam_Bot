import os
import random
import requests
from bs4 import BeautifulSoup
from bitlyshortener import Shortener
from dotenv import load_dotenv

# Carica variabili d'ambiente (funziona sia in locale che con GitHub Secrets)
load_dotenv()

# Legge le variabili d'ambiente dai Repository secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "")
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Frasi simpatiche per categoria
CATEGORY_MESSAGES = {
    "infanzia": [
        "Perfetto per il tuo piccolo tesoro! 👶",
        "Un must-have per ogni genitore! 🍼",
        "La felicità di un bambino inizia da qui 💖",
        "Piccoli momenti, grandi ricordi 🌟"
    ],
    "giochi": [
        "Ore di divertimento garantite! 🎯",
        "Un gioco che non stanca mai! 🎲",
        "Pronti a giocare insieme? 🕹",
        "Il sorriso di un bambino vale più di mille parole 😊"
    ],
    "giocattoli": [
        "Giocare è la miglior avventura! 🚀",
        "Creatività senza limiti! 🎨",
        "Perfetto per sognare ad occhi aperti ✨",
        "Il regalo giusto per mille risate 😂"
    ],
    "libri": [
        "Una storia che incanta grandi e piccini 📚",
        "Avventure fantastiche ti aspettano! ✨",
        "Un libro è un amico per sempre 📖",
        "Il potere della fantasia inizia qui 💫"
    ],
    "vestiti": [
        "Stile e comfort per i più piccoli 👕",
        "Perfetti per ogni occasione 🎀",
        "Comodi e alla moda! 👗",
        "Vestiti che raccontano una storia 🌈"
    ],
    "premaman": [
        "Comodità e stile per la futura mamma 🤰",
        "Per sentirti splendida in ogni momento ✨",
        "Coccolati mentre coccoli il tuo bimbo 🍼",
        "Perché la bellezza è anche nella dolce attesa 💖"
    ],
    "scuola": [
        "Pronti per un nuovo anno scolastico! 📚",
        "Il compagno perfetto per imparare 🎓",
        "Studiare non è mai stato così divertente ✏️",
        "Dal banco alla ricreazione, sempre al top! 🎒"
    ],
    "asilo": [
        "Perfetto per i primi giorni all'asilo 🏫",
        "Comodità e praticità per i più piccoli 👶",
        "Piccoli passi verso grandi avventure 🚀",
        "Tutto il necessario per iniziare alla grande 🌟"
    ],
    "piscina": [
        "Divertimento assicurato in acqua 🏊",
        "Pronti a fare splash? 💦",
        "Estate vuol dire anche piscina 🕶️",
        "L'accessorio perfetto per rinfrescarsi 😎"
    ],
    "scarpe": [
        "Per correre verso nuove avventure 🏃",
        "Comode e stilose 👟",
        "Passi leggeri, grandi sogni 🌈",
        "Il primo passo è sempre il più importante 💖"
    ],
    "videogiochi": [
        "Il gioco che stavi aspettando! 🎮",
        "Ore di divertimento garantite 🕹️",
        "Sfide epiche ti attendono 🚀",
        "Per veri gamer 💥"
    ]
}

# Frasi generiche se nessuna categoria è trovata
GENERIC_MESSAGES = [
    "Un'offerta da non perdere! 🔥",
    "Solo per veri intenditori 💡",
    "Il momento giusto per comprare è adesso! ⏰",
    "Affrettati, le scorte sono limitate! ⚡"
]

def get_category_message(title):
    """Trova un messaggio simpatico in base alla categoria nel titolo"""
    title_lower = title.lower()
    for category, messages in CATEGORY_MESSAGES.items():
        if category in title_lower:
            return random.choice(messages)
    return random.choice(GENERIC_MESSAGES)

def shorten_url(url):
    """Accorcia un link con Bitly"""
    if not BITLY_TOKEN:
        return url
    shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)
    return shortener.shorten_urls([url])[0]

def send_telegram_message(text):
    """Invia un messaggio su Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token Telegram o Chat ID mancanti.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def main():
    # Qui andrai a inserire il codice che recupera le offerte da Amazon
    # Esempio placeholder per test
    products = [
        {"title": "Giocattolo educativo per bambini", "url": "https://www.amazon.it/dp/example1"},
        {"title": "Libro illustrato per l'infanzia", "url": "https://www.amazon.it/dp/example2"}
    ]

    for product in products:
        short_url = shorten_url(product["url"])
        message = get_category_message(product["title"])
        text = f"<b>{product['title']}</b>\n{message}\n👉 {short_url}"
        send_telegram_message(text)

if __name__ == "__main__":
    main()
