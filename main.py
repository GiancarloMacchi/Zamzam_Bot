import os
import json
import requests
from amazon_api import get_amazon_products
from utils import shorten_url

# Recupera variabili d'ambiente
REQUIRED_ENV_VARS = [
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

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Variabili mancanti: {', '.join(missing_vars)}")

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = os.getenv("KEYWORDS")
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))

# Funzione per inviare messaggio con immagine a Telegram
def send_telegram_message(photo_url, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print(f"Errore Telegram: {r.text}")

# Recupera i prodotti da Amazon
products = get_amazon_products(
    KEYWORDS,
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG
)

if not products:
    print("Nessun prodotto trovato.")
else:
    count = 0
    for item in products:
        try:
            title = item["ItemInfo"]["Title"]["DisplayValue"]
            image_url = item["Images"]["Primary"]["Medium"]["URL"]
            price_info = item["Offers"]["Listings"][0]["Price"]
            price = price_info.get("DisplayAmount", "N/A")
            amount = price_info.get("Amount", 0)

            # Calcolo sconto
            savings_info = item["Offers"]["Listings"][0].get("SavingBasis", {})
            if savings_info:
                original_price = savings_info.get("DisplayAmount", price)
                original_amount = savings_info.get("Amount", amount)
                discount_percent = round((original_amount - amount) / original_amount * 100, 2)
            else:
                original_price = price
                discount_percent = 0

            if discount_percent < MIN_SAVE:
                continue

            # Link Amazon con tag referral
            url_amazon = item["DetailPageURL"]
            short_url = shorten_url(url_amazon, BITLY_TOKEN)

            caption = (
                f"<b>{title}</b>\n"
                f"💰 Prezzo: <b>{price}</b>\n"
                f"💸 Sconto: <b>{discount_percent}%</b>\n"
                f"🔗 <a href='{short_url}'>Acquista qui</a>"
            )

            send_telegram_message(image_url, caption)
            count += 1

            if count >= ITEM_COUNT:
                break

        except Exception as e:
            print(f"Errore prodotto: {e}")

print("Invio completato ✅")
