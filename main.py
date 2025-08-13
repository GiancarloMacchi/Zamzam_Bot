import logging
from amazon_client import get_items, KEYWORDS, BATCH_SIZE
from telegram_bot import send_to_telegram

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🔍 Recupero articoli da Amazon...")

    # Mostra batch di keyword usate in questo run
    if len(KEYWORDS) > BATCH_SIZE:
        logger.info(
            f"📦 Batch keyword attuale: {KEYWORDS[:BATCH_SIZE]} "
            f"(su {len(KEYWORDS)} totali)"
        )
    else:
        logger.info(f"📦 Keyword usate: {KEYWORDS}")

    items = get_items()

    if items:
        logger.info(f"✅ {len(items)} articoli trovati, invio a Telegram...")
        for item in items:
            send_to_telegram(item)
    else:
        logger.info("ℹ️ Nessun articolo trovato.")
