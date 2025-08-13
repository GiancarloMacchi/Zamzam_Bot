import os
import logging
from dotenv import load_dotenv
from telegram import Bot
from amazon_client import get_items

# Carica variabili d'ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_offer_to_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")

if __name__ == "__main__":
    # Esempio: prendi un prodotto specifico da Amazon
    asin_list = ["B09G9FPHY1"]  # esempio ASIN
    amazon_response = get_items(asin_list)

    if amazon_response and amazon_response.items_result:
        for item in amazon_response.items_result.items:
            title = item.item_info.title.display_value
            price = item.offers.listings[0].price.display_amount
            message = f"🔥 <b>{title}</b>\n💰 Prezzo: {price}"
            send_offer_to_telegram(message)
    else:
        logging.error("Nessun risultato trovato su Amazon.")
