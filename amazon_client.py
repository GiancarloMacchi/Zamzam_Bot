import os
import json
import logging
from amazon_paapi import AmazonAPI
from datetime import datetime

# Configurazione logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Credenziali Amazon dal repository secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Parametri bot
KEYWORDS = [kw.strip() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))
BATCH_SIZE = 10  # batch di keyword per evitare throttling

# Risorse da richiedere alle API Amazon
RESOURCES = [
    "Images.Primary.Large",
    "ItemInfo.Title",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Listings.Promotions",
]

amazon_api = AmazonAPI(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)


def get_items(keyword):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword.upper()}")
    try:
        # Chiamata API Amazon
        results = amazon_api.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT,
            resources=RESOURCES
        )

        items_data = []
        for item in results:
            # Se è già un dict, lo usiamo direttamente
            if isinstance(item, dict):
                items_data.append(item)
            else:
                # Altrimenti proviamo a convertirlo
                if hasattr(item, "to_dict"):
                    items_data.append(item.to_dict())
                else:
                    logger.warning(f"Elemento senza to_dict(): {item}")

        # Salvataggio debug locale
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(items_data, f, ensure_ascii=False, indent=2)

        return items_data

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []


if __name__ == "__main__":
    all_items = []
    for kw in KEYWORDS:
        all_items.extend(get_items(kw))
    logger.info(f"Totale articoli trovati: {len(all_items)}")
