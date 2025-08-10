import os
import requests
import bitlyshortener
from amazon.paapi import AmazonAPI

# Carico variabili d'ambiente
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.environ.get("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.environ.get("ITEM_COUNT", 5))
MIN_SAVE = float(os.environ.get("MIN_SAVE", 0.0))

# Lista parole chiave
KEYWORDS = [
    "offerte tecnologia",
    "cucina",
    "elettrodomestici",
    "giochi",
    "abbigliamento",
    "sport",
    "giardinaggio",
    "accessori auto",
]

# Config Amazon API
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Config Bitly
shortener = bitlyshortener.Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

def cerca_prodotti(keyword):
    try:
        items = amazon.search_items(keywords=keyword, item_count=ITEM_COUNT).items
    except Exception as e:
        print(f"❌ Errore ricerca '{keyword}': {e}")
        return

    if not items:
        print(f"⚠ Nessun prodotto trovato per '{keyword}'")
        return

    for item in items:
        try:
            title = getattr(item.item_info.title, "display_value", "Titolo non disponibile")
            price = getattr(item.offers.listings[0].price, "amount", None)
            currency = getattr(item.offers.listings[0].price, "currency", "")
            url = item.detail_page_url

            if not price:
                continue

            short_url = shortener.shorten_urls([url])[0]

            messaggio = f"📦 {title}\n💰 {price} {currency}\n🔗 {short_url}"
            invia_telegram(messaggio)
        except Exception as e:
            print(f"Errore elaborando un prodotto: {e}")

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Errore invio Telegram: {e}")
