import os
import logging
from amazon_paapi import AmazonAPI
from telegram import Bot

logging.basicConfig(level=logging.INFO)

# Credenziali da variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "10"))
MIN_SAVE = int(os.getenv("MIN_SAVE", "0"))

# Inizializza Amazon API
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Inizializza Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def search_and_send():
    logging.info(f"Cerco: {KEYWORDS}")
    products = amazon.search_items(keywords=KEYWORDS, item_count=ITEM_COUNT)
    for product in products:
        if product.savings and product.savings >= MIN_SAVE:
            message = f"{product.title}\n{product.detail_page_url}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

if __name__ == "__main__":
    search_and_send()
