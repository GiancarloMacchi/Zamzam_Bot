import os
from dotenv import load_dotenv
from amazon_client import get_items
from telegram import Bot

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

def send_message(message):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    keywords = os.getenv("KEYWORDS").split(",")
    item_count = int(os.getenv("ITEM_COUNT"))

    for keyword in keywords:
        products = get_items(keyword.strip(), item_count)
        for p in products:
            send_message(f"{p.title} - {p.detail_page_url}")
