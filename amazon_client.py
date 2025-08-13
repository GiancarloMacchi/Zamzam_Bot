import logging
import os
import time
from amazon_paapi import AmazonAPI
from urllib.error import HTTPError

# Configurazione logger
logger = logging.getLogger(__name__)

# Recupero variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 5))  # Quante keyword per esecuzione

# Funzione per recuperare articoli da Amazon
def get_items():
    api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
    all_items = []

    # Calcolo batch di keyword per run
    if len(KEYWORDS) > BATCH_SIZE:
        # Rotazione keyword in base all'ora
        batch_index = int(time.time() // (6 * 3600)) % (len(KEYWORDS) // BATCH_SIZE + 1)
        start = batch_index * BATCH_SIZE
        keywords_batch = KEYWORDS[start:start + BATCH_SIZE]
    else:
        keywords_batch = KEYWORDS

    for keyword in keywords_batch:
        keyword = keyword.strip()
        if not keyword:
            continue

        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
        try:
            items = api.search_items(keywords=keyword, item_count=ITEM_COUNT)
            if items:
                for item in items:
                    # Calcola percentuale di sconto se disponibile
                    try:
                        price = float(item.list_price.amount) if item.list_price else None
                        sale_price = float(item.offer_price.amount) if item.offer_price else None
                        if price and sale_price:
                            discount = ((price - sale_price) / price) * 100
                            if discount >= MIN_SAVE:
                                all_items.append(item)
                    except Exception:
                        pass
        except HTTPError as e:
            logger.error(f"❌ Errore durante il recupero degli articoli da Amazon API: {e}")
        except Exception as e:
            logger.error(f"❌ Errore imprevisto: {e}")

        # Pausa per non superare i limiti Amazon PA-API
        time.sleep(2)

    return all_items
