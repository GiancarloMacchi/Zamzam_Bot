import logging
import json
import os
from amazon_paapi import AmazonAPI

# Logger
logger = logging.getLogger(__name__)

# Legge le variabili di ambiente (da GitHub Secrets)
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Inizializza client Amazon
amazon = AmazonAPI(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def search_amazon_items(keyword, item_count=10):
    """
    Cerca articoli su Amazon per una keyword.
    Salva un file di debug con la risposta grezza.
    """
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

    try:
        # Chiamata API senza search_index
        results = amazon.search_items(
            keywords=keyword,
            item_count=item_count
        )

        # Salvataggio file debug con risultati grezzi
        debug_filename = f"amazon_debug_{keyword.replace(' ', '_')}.json"
        with open(debug_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Risposta grezza salvata in {debug_filename}")

        if not results:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
            return []

        return results

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
