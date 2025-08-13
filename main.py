import logging
from amazon_client import get_items, KEYWORDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    all_items = []

    for keyword in KEYWORDS:
        try:
            items = get_items(keyword)
            all_items.extend(items)
        except Exception as e:
            logger.error(f"❌ Errore durante il recupero per '{keyword}': {e}")

    if all_items:
        logger.info(f"✅ Trovati {len(all_items)} articoli in totale.")
    else:
        logger.info("ℹ️ Nessun articolo trovato.")

if __name__ == "__main__":
    main()
