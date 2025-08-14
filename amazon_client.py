import os
import json
import logging
from amazon_paapi import AmazonAPI

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config da environment variables
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Keywords di test - puoi cambiarle
KEYWORDS = ["giocattoli lego", "zainetto scuola bimbi"]
BATCH_SIZE = 2  # quante keyword per esecuzione

# Lista completa di resources
RESOURCES = [
    "Images.Primary.Large",
    "Images.Variants.Large",
    "ItemInfo.Title",
    "ItemInfo.Features",
    "ItemInfo.ProductInfo",
    "ItemInfo.ByLineInfo",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Summaries.LowestPrice"
]

# Inizializza Amazon API
amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def get_items(keyword):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
    try:
        items = amazon.search_items(
            keywords=keyword,
            resources=RESOURCES
        )

        # Salviamo la risposta grezza per debug
        raw_data = [item.__dict__ for item in items] if items else []
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False)
            logger.info("💾 amazon_debug.json salvato con le risposte grezze di Amazon")

        if not items:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
            return []

        results = []
        for item in items:
            try:
                results.append({
                    "title": getattr(item.item_info.title, "display_value", None),
                    "url": getattr(item, "detail_page_url", None),
                    "price": getattr(item.offers.listings[0].price, "amount", None) if item.offers and item.offers.listings else None,
                    "currency": getattr(item.offers.listings[0].price, "currency", None) if item.offers and item.offers.listings else None,
                })
            except Exception as e:
                logger.error(f"Errore parsing item: {e}")

        return results

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
