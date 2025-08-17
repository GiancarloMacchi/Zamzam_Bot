import logging
import time
from amazon.paapi import AmazonAPI  # richiede python-amazon-paapi

MAX_RETRIES = 3
RETRY_DELAY = 5  # secondi tra i tentativi

def search_amazon(keyword, config):
    AMAZON_ACCESS_KEY = config.get("AMAZON_ACCESS_KEY")
    AMAZON_SECRET_KEY = config.get("AMAZON_SECRET_KEY")
    AMAZON_ASSOCIATE_TAG = config.get("AMAZON_ASSOCIATE_TAG")
    AMAZON_COUNTRY = config.get("AMAZON_COUNTRY", "IT")

    amazon = AmazonAPI(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"[PA-API] Ricerca prodotto per keyword: {keyword} (tentativo {attempt})")
            products = amazon.search_items(keywords=keyword, search_index="All", item_count=10)
            results = []
            for item in products.items:
                results.append({
                    "title": item.title,
                    "url": item.detail_page_url,
                    "price": getattr(item, "price_and_currency", "N/A"),
                    "image": getattr(item, "images", {}).get("primary", {}).get("large", ""),
                    "description": getattr(item, "features", ["Breve descrizione non disponibile"])[0]
                })
            return results
        except Exception as e:
            logging.error(f"[PA-API] Errore durante ricerca Amazon: {e}")
            if attempt < MAX_RETRIES:
                logging.info(f"[PA-API] Ritento tra {RETRY_DELAY} secondi...")
                time.sleep(RETRY_DELAY)
            else:
                logging.error("[PA-API] Raggiunto numero massimo di tentativi, salto keyword.")
                return []
