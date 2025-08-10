import os
import logging
from amazon_api import get_amazon_products
from utils import shorten_url, send_telegram_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Legge le variabili d'ambiente
required_vars = [
    "AMAZON_ACCESS_KEY",
    "AMAZON_SECRET_KEY",
    "AMAZON_ASSOCIATE_TAG",
    "AMAZON_COUNTRY",
    "BITLY_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "ITEM_COUNT",
    "KEYWORDS",
    "MIN_SAVE"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logging.error(f"❌ Variabili mancanti: {', '.join(missing_vars)}")
    exit(1)

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.getenv("ITEM_COUNT"))
KEYWORDS = os.getenv("KEYWORDS")
MIN_SAVE = int(os.getenv("MIN_SAVE"))

try:
    products = get_amazon_products(
        KEYWORDS,
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG
    )
except Exception as e:
    logging.error(f"Errore durante la richiesta ad Amazon API: {e}")
    exit(1)

if not products:
    logging.info("Nessun prodotto trovato.")
    exit(0)

for product in products:
    try:
        title = product.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
        image_url = product.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL")
        offers = product.get("Offers", {}).get("Listings", [])

        if not offers:
            logging.info(f"⏩ Nessuna offerta per '{title}', salto...")
            continue

        price_info = offers[0].get("Price", {})
        amount = price_info.get("Amount")
        currency = price_info.get("Currency")

        saving_info = offers[0].get("SavingBasis", {})
        saving_amount = saving_info.get("Amount", 0)
        saving_percentage = 0
        if amount and saving_amount:
            saving_percentage = int((saving_amount - amount) / saving_amount * 100)

        if saving_percentage < MIN_SAVE:
            logging.info(f"⏩ Sconto {saving_percentage}% inferiore al minimo per '{title}', salto...")
            continue

        url = product.get("DetailPageURL")
        short_url = shorten_url(url, BITLY_TOKEN)

        message = f"🎯 *{title}*\n💰 Prezzo: {amount} {currency}\n📉 Sconto: {saving_percentage}%\n🔗 [Acquista qui]({short_url})"

        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, image_url)

    except Exception as e:
        logging.error(f"Errore nel processare un prodotto: {e}")
        continue
