import os
import logging
import requests
from amazon_paapi import AmazonApi

# Lettura variabili ambiente (secrets GitHub)
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza Amazon API client
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    country=AMAZON_COUNTRY
)

def shorten_url(url):
    """Accorcia un URL usando Bitly"""
    if not BITLY_TOKEN:
        return url
    try:
        response = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={"Authorization": f"Bearer {BITLY_TOKEN}"},
            json={"long_url": url}
        )
        if response.status_code == 200:
            return response.json().get("link", url)
    except Exception as e:
        logging.error(f"Errore durante l'accorciamento URL: {e}")
    return url

def search_products():
    """Cerca prodotti su Amazon in base alle keywords"""
    try:
        results = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT,
            resources=[
                "ItemInfo.Title",
                "ItemInfo.ByLineInfo",
                "ItemInfo.ProductInfo",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "BrowseNodeInfo.BrowseNodes",
                "Images.Primary.Large"
            ]
        )
        return results.get("SearchResult", {}).get("Items", [])
    except Exception as e:
        logging.error(f"Errore ricerca prodotti Amazon: {e}")
        return []

def get_discount_percentage(product):
    """Calcola lo sconto in percentuale di un prodotto"""
    try:
        offers = product.get("Offers", {}).get("Listings", [])
        if not offers:
            return 0
        offer = offers[0]
        price = offer.get("Price", {}).get("Amount")
        base_price = offer.get("SavingBasis", {}).get("Amount")
        if not price or not base_price or base_price <= 0:
            return 0
        discount = round((base_price - price) / base_price * 100)
        return max(discount, 0)
    except Exception as e:
        logging.error(f"Errore calcolo sconto: {e}")
        return 0

def send_telegram_message(text):
    """Invia un messaggio a Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Token Telegram o Chat ID non impostati.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            logging.error(f"Errore invio messaggio Telegram: {r.text}")
    except Exception as e:
        logging.error(f"Errore connessione Telegram: {e}")
