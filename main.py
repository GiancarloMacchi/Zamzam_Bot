import logging
from amazon_client import get_items, KEYWORDS, save_debug

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    all_items = []

    for keyword in KEYWORDS:
        items = get_items(keyword)
        if items:
            all_items.extend(items)
        else:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
        save_debug(items)

    if not all_items:
        logger.info("ℹ️ Nessun articolo trovato.")
    else:
        logger.info(f"✅ Trovati {len(all_items)} articoli totali.")

if __name__ == "__main__":
    main()
