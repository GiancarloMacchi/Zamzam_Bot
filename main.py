import logging
from amazon_client import get_items
from telegram_bot import send_telegram_message
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def main():
    logging.info("🔍 Recupero articoli da Amazon...")
    items = get_items()

    if not items:
        send_telegram_message(
            TELEGRAM_CHAT_ID,
            "❌ Nessuna offerta trovata o errore nelle API Amazon."
        )
        return

    for item in items:
        message = f"📦 {item['title']}\n💰 {item['price']} {item['currency']}\n💸 Sconto: {item['saving']}%\n🔗 {item['url']}"
        send_telegram_message(TELEGRAM_CHAT_ID, message)

if __name__ == "__main__":
    main()
