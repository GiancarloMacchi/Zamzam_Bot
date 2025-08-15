import os
import json
import logging
from amazon_client import AmazonClient
from telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)

def main():
    try:
        logging.info("🔍 Recupero articoli da Amazon...")

        # Inizializza AmazonClient con valori dalle variabili d'ambiente
        amazon_client = AmazonClient(
            access_key=os.getenv("AMAZON_ACCESS_KEY"),
            secret_key=os.getenv("AMAZON_SECRET_KEY"),
            associate_tag=os.getenv("AMAZON_ASSOCIATE_TAG"),
            country=os.getenv("AMAZON_COUNTRY", "it"),
            keywords=json.loads(os.getenv("KEYWORDS", '[]')),
            min_save=int(os.getenv("MIN_SAVE", "20")),
            item_count=int(os.getenv("ITEM_COUNT", "5"))
        )

        # Inizializza TelegramBot
        telegram_bot = TelegramBot(
            token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )

        logging.info(f"📜 Keywords lette: {amazon_client.keywords}")

        # Cerca e invia articoli per ogni keyword
        for keyword in amazon_client.keywords:
            items = amazon_client.search_items(keyword)
            for item in items:
                message = (
                    f"📦 {item['title']}\n"
                    f"💰 Prezzo: {item['price']}\n"
                    f"💸 Sconto: {item['discount']}\n"
                    f"🔗 Link: {item['url']}"
                )
                telegram_bot.send_message(message)

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
