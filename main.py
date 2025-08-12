import os
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from bitlyshortener import Shortener
from amazon_paapi import AmazonApi
from telegram import Bot
from datetime import datetime

# Carica variabili ambiente
load_dotenv()
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 10))
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

# Frasi spiritose per categoria
MESSAGGI_CATEGORIA = {
    "baby": [
        "👶 Pronto a sciogliere cuori? Guarda qui...",
        "👶 Dolcezza a pacchi in arrivo...",
        "👶 Piccoli prezzi per piccoli tesori..."
    ],
    "school": [
        "📚 Pagina dopo pagina, la sorpresa è servita...",
        "📚 Preparati a colorare la giornata...",
        "📚 Un mondo di idee per crescere..."
    ],
    "gift": [
        "🎁 Attenzione: rischio di sorrisi immediati!",
        "🎁 La sorpresa perfetta ti aspetta...",
        "🎁 Chi ha detto che non si può comprare la felicità?"
    ],
    "pool": [
        "🏊 Tuffati in questa occasione...",
        "🏊 Preparati a fare splash nei saldi...",
        "🏊 L'estate è qui, e costa meno!"
    ],
    "other": [
        "🎯 Colpo d'occhio: ecco l'affare!",
        "🎯 Qui c'è da fare centro...",
        "🎯 Sconto mirato per te..."
    ]
}

# Parole chiave per categorie
CATEGORIE_KEYWORDS = {
    "baby": ["bimbo", "bambina", "infanzia", "premaman", "scuola", "asilo"],
    "school": ["libri", "lettura", "pastelli", "colori"],
    "gift": ["regalo", "giochi", "compleanno"],
    "pool": ["piscina", "costume", "ciabatte"]
}

# Blacklist parole
BLACKLIST = ["mutande uomo", "boxer uomo", "slip uomo"]

# Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Bitly
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

def categoria_prodotto(titolo):
    titolo_lower = titolo.lower()
    for cat, keywords in CATEGORIE_KEYWORDS.items():
        if any(k in titolo_lower for k in keywords):
            return cat
    return "other"

def messaggio_spiritoso(cat):
    return random.choice(MESSAGGI_CATEGORIA[cat])

def prodotto_valido(titolo):
    titolo_lower = titolo.lower()
    return not any(bad in titolo_lower for bad in BLACKLIST)

def cerca_prodotti(keyword):
    try:
        result = amazon.search_items(keywords=keyword, item_count=ITEM_COUNT)
        if not result.items:
            return []
        return result.items
    except Exception as e:
        print(f"[ERRORE Amazon] ricerca '{keyword}': {e}")
        return []

def invia_telegram(testo):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=testo, parse_mode="HTML")

def main():
    print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")
    for keyword in KEYWORDS:
        print(f"[INFO] 🔍 Ricerca per: {keyword}")
        prodotti = cerca_prodotti(keyword)
        for p in prodotti:
            titolo = p.item_info.title.display_value
            if not prodotto_valido(titolo):
                continue
            prezzo = p.offers.listings[0].price.amount if p.offers and p.offers.listings else None
            url = p.detail_page_url
            short_url = shortener.shorten_urls([url])[0]
            cat = categoria_prodotto(titolo)
            testo = f"{messaggio_spiritoso(cat)}\n<b>{titolo}</b>\n{short_url}"
            invia_telegram(testo)

    print("[INFO] ✅ Bot completato")

if __name__ == "__main__":
    main()
