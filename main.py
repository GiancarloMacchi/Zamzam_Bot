import logging
import os

# Tentativo di import con fallback
try:
    from telegram_bot import TelegramBot
except ModuleNotFoundError:
    from telegram_client import TelegramBot

from amazon_client import AmazonClient

logging.basicConfig(level=logging.INFO)

def main():
    try:
        amazon_client = AmazonClient()
        telegram_bot = TelegramBot()

        logging.info("🔍 Recupero articoli da Amazon...")
        keywords = amazon_client.keywords
        logging.info(f"📜 Keywords lette: {keywords}")

        for keyword in keywords:
            logging.info(f"🔍 Cerco prodotti per: {keyword}")
            items = amazon_client.search_items(keyword)
            logging.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")

            if items:
                telegram_bot.send_products(items)

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
