import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
from amazon_client import get_items

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "offerte").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))


def start(update, context):
    update.message.reply_text("Ciao! Ti invierò le migliori offerte Amazon 😉")


def send_offers(update, context):
    for keyword in KEYWORDS:
        products = get_items(keyword, ITEM_COUNT, MIN_SAVE)
        if not products:
            update.message.reply_text(f"Nessuna offerta trovata per '{keyword}'.")
            continue
        for product in products:
            message = f"**{product['title']}**\nPrezzo: {product['price']}\n{product['url']}"
            update.message.reply_text(message, parse_mode="Markdown")


if __name__ == "__main__":
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("offers", send_offers))

    logging.info("🤖 Bot avviato...")
    updater.start_polling()
    updater.idle()
