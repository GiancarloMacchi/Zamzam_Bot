import os
import sys
import logging
from amazon_paapi import AmazonApi
from utils import shorten_url, send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

REQUIRED_ENV_VARS = [
    "AMAZON_ACCESS_KEY", "AMAZON_SECRET_KEY", "AMAZON_ASSOCIATE_TAG",
    "AMAZON_COUNTRY", "BITLY_TOKEN", "ITEM_COUNT", "KEYWORDS", "MIN_SAVE",
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
]

# Controllo variabili mancanti
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logging.error(f"❌ Variabili mancanti: {', '.join(missing_vars)}")
    sys.exit(1)

# Config
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS")
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CATEGORY_KEYWORDS = [
    "bambino", "bambina", "neonato", "neonata", "infanzia",
    "scuola", "giocattolo", "pannolino", "pappa", "maternità",
    "genitore", "studente", "zaino", "cartoleria"
]

def product_matches_category(product_title, product_category):
    text = f"{product_title} {product_category}".lower()
    return any(keyword in text for keyword in CATEGORY_KEYWORDS)

def main():
    logging.info("🔍 Avvio ricerca offerte Amazon...")

    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

    try:
        results = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT
        )
    except Exception as e:
        logging.error(f"Errore ricerca Amazon: {e}")
        sys.exit(1)

    for item in results.items:
        try:
            title = item.item_info.title.display_value if item.item_info and item.item_info.title else None
            category = item.item_info.product_info.product_group.display_value if item.item_info and item.item_info.product_info and item.item_info.product_info.product_group else ""
            offers = item.offers.listings if item.offers and item.offers.listings else None

            if not title or not offers:
                continue

            offer = offers[0].price
            if not offer or not offer.savings or not offer.savings.percentage:
                continue

            discount = offer.savings.percentage
            if discount < MIN_SAVE:
                continue

            if not product_matches_category(title, category):
                continue

            price = offer.display_amount
            url = item.detail_page_url
            short_url = shorten_url(url, BITLY_TOKEN)
            message = f"🎯 {title}\n💰 {price} (-{discount}%)\n🔗 {short_url}"

            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

        except Exception as e:
            logging.error(f"Errore elaborazione prodotto: {e}")
            continue

if __name__ == "__main__":
    main()
