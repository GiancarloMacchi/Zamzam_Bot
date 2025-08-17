import logging
import time
from amazon.paapi import AmazonAPI

logger = logging.getLogger(__name__)

def search_amazon(keyword, config):
    """
    Restituisce una lista di prodotti Amazon per la keyword.
    config: dizionario contenente chiavi AWS e PA-API
    """
    access_key = config['AMAZON_ACCESS_KEY']
    secret_key = config['AMAZON_SECRET_KEY']
    associate_tag = config['AMAZON_ASSOCIATE_TAG']
    country = config['AMAZON_COUNTRY']

    api = AmazonAPI(access_key, secret_key, associate_tag, country)

    for attempt in range(3):
        try:
            results = api.search_products(keywords=keyword, search_index='All', item_count=5)
            products = []
            for item in results.items:
                products.append({
                    'title': item.title,
                    'url': item.detail_page_url,
                    'price': getattr(item, 'price_and_currency', 'N/A'),
                    'image': getattr(item.images, 'primary', {}).get('medium', ''),
                    'description': getattr(item, 'feature_bullets', [''])[0]
                })
            return products
        except Exception as e:
            logger.warning(f"Errore API Amazon: {e} - Tentativo {attempt+1}/3")
            time.sleep(10)
    logger.error(f"Falliti tutti i tentativi per keyword: {keyword}")
    return []
