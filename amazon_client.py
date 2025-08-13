import os
import json
import logging
from amazon_paapi import AmazonAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazioni da variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "10"))
MIN_SAVE = int(os.getenv("MIN_SAVE", "0"))
KEYWORDS = os.getenv("KEYWORDS", "").split(",")

api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def get_items():
    all_items = []
    debug_data = {}

    for keyword in KEYWORDS:
        keyword = keyword.strip()
        if not keyword:
            continue

        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
        try:
            items = api.search_items(keywords=keyword, item_count=ITEM_COUNT)
            debug_data[keyword] = items  # Salvo risposta completa in debug

            logger.info(f"📦 Risultati grezzi ricevuti: {len(items)}")
            # Applica filtro sconto minimo
            filtered = [
                item for item in items
                if item.get("Offers", {}).get("Listings", [{}])[0]
                .get("Price", {}).get("Savings", {}).get("Percentage", 0) >= MIN_SAVE
            ]

            logger.info(f"✅ Risultati dopo filtri: {len(filtered)}")
            all_items.extend(filtered)

        except Exception as e:
            logger.error(f"❌ Errore durante il recupero degli articoli: {e}")

    # Salvo il debug JSON
    try:
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        logger.info("💾 amazon_debug.json salvato con le risposte grezze di Amazon")
    except Exception as e:
        logger.error(f"❌ Errore salvataggio amazon_debug.json: {e}")

    return all_items
