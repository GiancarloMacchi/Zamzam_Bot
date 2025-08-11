import os
from amazon_paapi import AmazonApi
from telegram import Bot
from utils import search_amazon_items

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))

def main():
    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    items = search_amazon_items(amazon, KEYWORDS, ITEM_COUNT, MIN_SAVE)
    if not items:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Nessun articolo trovato.")
        return

    for item in items:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"{item['title']}\n{item['url']}")

if __name__ == "__main__":
    main()
