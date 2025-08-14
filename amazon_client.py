import logging
import json
import os
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

# Credenziali prese dalle GitHub Actions Secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Risorse di default se la secret non esiste o è malformata
DEFAULT_RESOURCES = [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "ItemInfo.Features",
    "ItemInfo.ByLineInfo",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis"
]

def load_resources_from_secret():
    resources_env = os.getenv("AMAZON_RESOURCES")
    if resources_env:
        try:
            resources = json.loads(resources_env)
            if isinstance(resources, list) and all(isinstance(r, str) for r in resources):
                logger.info("📦 Risorse Amazon caricate da Secret AMAZON_RESOURCES")
                return resources
            else:
                logger.warning("⚠️ Secret AMAZON_RESOURCES non valida. Uso default.")
        except Exception as e:
            logger.error(f"❌ Errore parsing AMAZON_RESOURCES: {e}")
    else:
        logger.info("ℹ️ Nessuna secret AMAZON_RESOURCES trovata. Uso default.")
    return DEFAULT_RESOURCES

RESOURCES = load_resources_from_secret()

amazon = AmazonAPI(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

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
