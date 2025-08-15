import logging
import os
from amazon_client import AmazonClient
from telegram_client import TelegramClient

logging.basicConfig(level=logging.INFO)

def main():
    # 🔑 Leggi secrets
    AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
    AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
    AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
    AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
    ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
    KEYWORDS = os.getenv("KEYWORDS", "").split(",")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    amazon_client = AmazonClient(
        access_key=AMAZON_ACCESS_KEY,
        secret_key=AMAZON_SECRET_KEY,
        associate_tag=AMAZON_ASSOCIATE_TAG,
        country=AMAZON_COUNTRY,
        item_count=ITEM_COUNT
    )

    telegram_client = TelegramClient(
        token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )

    # 🛠 Test connessione API Amazon
    if not amazon_client.test_connection():
        logging.error("❌ La connessione alla PA-API non sta restituendo risultati. Controlla credenziali o stato account.")
        return

    logging.info("🔍 Recupero articoli da Amazon...")
    logging.info(f"📜 Keywords lette dalle secrets: {KEYWORDS}")

    for keyword in KEYWORDS:
        items = amazon_client.search_items(keyword.strip())
        logging.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")

        for item in items:
            telegram_client.send_item(item)

if __name__ == "__main__":
    main()
