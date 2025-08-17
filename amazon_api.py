# amazon_api.py
import time
import logging
from amazon.paapi import AmazonAPI, AmazonException

AMAZON_ACCESS_KEY = "INSERISCI_LA_TUA_CHIAVE"
AMAZON_SECRET_KEY = "INSERISCI_LA_TUA_CHIAVE"
AMAZON_ASSOCIATE_TAG = "iltuotag-21"
AMAZON_COUNTRY = "it"

MAX_RETRIES = 3      # numero massimo di tentativi
RETRY_DELAY = 5      # secondi tra i retry

def search_amazon(keyword, item_count=5):
    """
    Cerca prodotti su Amazon usando PA-API 5.0 con retry automatici.
    Restituisce una lista di dizionari: [{'title':..., 'url':..., 'price':..., 'image':..., 'description':...}, ...]
    """
    api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
    attempts = 0

    while attempts < MAX_RETRIES:
        try:
            logging.info(f"[PA-API] Tentativo {attempts+1} per keyword: {keyword}")
            products = api.search_items(keywords=keyword, item_count=item_count)
            results = []
            for p in products:
                results.append({
                    "title": p.title,
                    "url": p.detail_page_url,
                    "price": getattr(p, 'price_and_currency', "N/A"),
                    "image": getattr(p, 'images', [{}])[0].get('url', ''),
                    "description": getattr(p, 'feature_bullets', ["Breve descrizione non disponibile"])[0]
                })
            return results

        except AmazonException as e:
            attempts += 1
            logging.warning(f"[PA-API] Errore Amazon: {e}. Retry in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            attempts += 1
            logging.warning(f"[PA-API] Errore generico: {e}. Retry in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

    logging.error(f"[PA-API] Falliti tutti i {MAX_RETRIES} tentativi per keyword: {keyword}")
    return []  # ritorna lista vuota se tutti i tentativi falliscono
