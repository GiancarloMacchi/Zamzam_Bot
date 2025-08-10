import os
import logging
import requests
from urllib.parse import urlencode

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))

# ==========================
# 🔍 Funzione ricerca Amazon
# ==========================
def search_products():
    """
    Effettua una ricerca prodotti usando l'API di Amazon PA-API.
    """
    from amazon.paapi import AmazonAPI  # Richiede libreria paapi5-python-sdk o simile
    
    amazon = AmazonAPI(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )

    logging.info(f"🔎 Ricerca primi {ITEM_COUNT} prodotti da Amazon...")
    products = amazon.search_items(
        keywords="",
        item_count=ITEM_COUNT,
        resources=[
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.Price.Savings",
            "BrowseNodeInfo.BrowseNodes",
            "DetailPageURL"
        ]
    )
    return products

# ==========================
# 🔗 Short URL con Bitly
# ==========================
def shorten_url(url):
    if not BITLY_TOKEN:
        return url
    try:
        headers = {"Authorization": f"Bearer {BITLY_TOKEN}"}
        data = {"long_url": url}
        resp = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("link", url)
    except Exception as e:
        logging.error(f"Errore Bitly: {e}")
    return url

# ==========================
# 📢 Invia messaggio Telegram
# ==========================
def send_telegram_message(text):
    """
    Invia un messaggio su Telegram (supporta Markdown).
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram BOT_TOKEN o CHAT_ID mancanti!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            logging.error(f"Errore invio Telegram: {resp.text}")
    except Exception as e:
        logging.error(f"Errore connessione Telegram: {e}")
