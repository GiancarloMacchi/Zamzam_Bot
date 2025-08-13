import logging
from amazon_client import get_items
from telegram_bot import send_to_telegram

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    items = get_items()

    if not items:
        logger.info("ℹ️ Nessun articolo trovato.")
        return

    logger.info(f"✅ Trovati {len(items)} articoli, invio a Telegram...")
    send_to_telegram(items)
    logger.info("✅ Invio completato.")

if __name__ == "__main__":
    main()
