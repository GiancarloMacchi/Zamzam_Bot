import logging
import time
from amazon.paapi import AmazonAPI

MAX_RETRIES = 3
RETRY_DELAY = 5  # secondi

def search_amazon(keyword, item_count):
    from config import load_config
    config = load_config()
    amazon = AmazonAPI(
        config["AMAZON_ACCESS_KEY"],
        config["AMAZON_SECRET_KEY"],
        config["AMAZON_ASSOCIATE_TAG"],
        country=config["AMAZON_COUNTRY"]
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            results = amazon.search_items(keywords=keyword, max_results=item_count)
            products = []
            for item in results:
                products.append({
                    "title": item.title,
                    "url": item.detail_page_url,
                    "price": getattr(item, "price_and_currency", {}).get("formatted", "N/A"),
                    "description": getattr(item, "features", ["Breve descrizione non disponibile"])[0],
                    "image": item.images[0].url if item.images else ""
                })
            return products
        except Exception as e:
            logging.error(f"Errore API Amazon (tentativo {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return []
