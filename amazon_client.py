import logging
import json
import os
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonAPI(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

# Risorse che vogliamo ottenere dalla risposta Amazon API
RESOURCES = [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "ItemInfo.Features",
    "ItemInfo.ByLineInfo",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis"
]

def search_amazon_items(keyword, item_count=10):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

    try:
        results = amazon.search_items(
            keywords=keyword,
            item_count=item_count,
            resources=RESOURCES
        )

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

def get_items(keyword, item_count=10):
    return search_amazon_items(keyword, item_count)
