import logging
from amazon_client import get_items
from telegram_bot import send_telegram_message
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    items = get_items()

    if not items:
        send_telegram_message(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
            "❌ Nessuna offerta trovata o errore nelle API Amazon."
        )
        return

    for item in items:
        message = (
            f"📦 <b>{item['title']}</b>\n"
            f"💰 Prezzo: {item['price']} {item['currency']}\n"
            f"💸 Sconto: {item['saving']}%\n"
            f"🔗 <a href='{item['url']}'>Vedi su Amazon</a>"
        )
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

if __name__ == "__main__":
    main()
