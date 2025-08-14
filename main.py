import os
import logging
from amazon_client import get_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    # Recupero le keywords dalle Secret
    keywords_env = os.getenv("KEYWORDS")
    if not keywords_env:
        logger.error("❌ Variabile KEYWORDS non trovata nelle Secret")
        return

    keywords = [k.strip() for k in keywords_env.split(",") if k.strip()]
    if not keywords:
        logger.error("❌ Nessuna keyword valida trovata")
        return

    totale_articoli = 0

    for keyword in keywords:
        items = get_items(keyword)
        if items:
            totale_articoli += len(items)
        else:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")

    logger.info(f"ℹ️ Trovati {totale_articoli} articoli in totale.")

if __name__ == "__main__":
    main()
