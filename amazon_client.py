import logging
import json
from amazon_paapi import AmazonAPI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

KEYWORDS = ["BAMBINI", "GIOCATTOLI"]
BATCH_SIZE = 10

amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

def get_items(keyword):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
    try:
        # resources richiesti da Amazon PAAPI
        resources = [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ]
        results = amazon.search_items(keyword, resources=resources)

        # Salva risposta grezza per debug
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in results], f, ensure_ascii=False, indent=4)

        return [item.to_dict() for item in results]

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
