import os
import logging
import requests
import telegram
from amazon_paapi import AmazonApi
from datetime import datetime

# Configura logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Recupero variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))

# Inizializza bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Inizializza API Amazon con timeout
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    country=AMAZON_COUNTRY
)

def search_amazon_products(keyword):
    """Cerca prodotti su Amazon usando la PA API"""
    try:
        return amazon.search_items(
            keywords=keyword.strip(),
            search_index="All",
            item_count=10,
            resources=[
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Images.Primary.Medium"
            ],
            timeout=10  # Timeout di sicurezza
        )
    except Exception as e:
        logging.error(f"Errore ricerca '{keyword}': {e}")
        return None

def post_to_telegram(product):
    """Invia il prodotto su Telegram"""
    try:
        title = product.item_info.title.display_value
        price = product.offers.listings[0].price.display_amount
        url = product.detail_page_url
        image_url = product.images.primary.medium.url

        message = f"📦 <b>{title}</b>\n💰 {price}\n🔗 <a href='{url}'>Acquista ora</a>"

        bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=image_url,
            caption=message,
            parse_mode=telegram.ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Errore invio Telegram: {e}")

def main():
    failed_keywords = 0

    for keyword in KEYWORDS:
        if not keyword.strip():
            continue

        logging.info(f"🔍 Cerco: {keyword}")
        products = search_amazon_products(keyword)

        if not products:
            failed_keywords += 1
            continue

        for product in products:
            try:
                price = product.offers.listings[0].price.amount
                saving_basis = getattr(product.offers.listings[0], "saving_basis", None)

                if saving_basis and saving_basis.amount > 0:
                    save_percent = ((saving_basis.amount - price) / saving_basis.amount) * 100
                    if save_percent >= MIN_SAVE:
                        post_to_telegram(product)
            except Exception as e:
                logging.error(f"Errore analisi prodotto: {e}")

    logging.info(f"🔴 Keyword fallite: {failed_keywords}")

if __name__ == "__main__":
    main()
