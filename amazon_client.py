import os
import json
import logging
from amazon_paapi import AmazonAPI

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Legge keywords dai Secrets
keywords_str = os.getenv("KEYWORDS", "").strip()
if not keywords_str:
    logger.error("❌ Nessuna keyword trovata nei GitHub Secrets (KEYWORDS). Impostale in Actions -> Environment secrets.")
    exit(1)

KEYWORDS = [k.strip() for k in keywords_str.split(",") if k.strip()]
BATCH_SIZE = 1  # o il valore che avevi prima

# Configurazione Amazon API
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def get_items(keyword):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
    try:
        results = amazon.search_items(
            keywords=keyword,
            resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis"
            ]
        )
        items = []
        for item in results:
            try:
                data = item.to_dict()
                items.append(data)
            except AttributeError:
                logger.warning(f"⚠️ Risultato non valido per keyword '{keyword}': {item}")
        return items

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []


def save_debug(data):
    with open("amazon_debug.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("💾 amazon_debug.json salvato con le risposte grezze di Amazon")
