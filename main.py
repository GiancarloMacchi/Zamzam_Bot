import os
import logging
from amazon_client import get_items
from telegram_bot import send_to_telegram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    
    # Leggo le keyword dalle variabili d'ambiente
    keywords = os.getenv("KEYWORDS", "")
    if not keywords:
        logger.error("❌ Nessuna keyword trovata. Imposta la variabile KEYWORDS.")
        return

    # Chiamata API Amazon
    items = get_items(keywords)  # ✅ Passo le keyword qui

    if not items:
        logger.info("ℹ️ Nessun articolo trovato.")
        return

    # Invio articoli a Telegram
    for item in items:
        send_to_telegram(item)

if __name__ == "__main__":
    main()
