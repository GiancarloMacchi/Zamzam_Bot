import os
import logging
from dotenv import load_dotenv
from amazon_client import get_items
from telegram_bot import send_to_telegram

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    keywords = os.getenv("KEYWORDS", "")
    if not keywords:
        logger.error("❌ Nessuna keyword trovata. Imposta la variabile KEYWORDS.")
        return

    items = get_items(keywords)

    if not items:
        logger.info("ℹ️ Nessun articolo trovato.")
        return

    for item in items:
        # telegram_bot si aspetta 'title' e 'link'
        send_to_telegram(item)

if __name__ == "__main__":
    main()
