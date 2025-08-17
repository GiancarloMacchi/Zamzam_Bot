import logging
import time
from amazon_paapi import AmazonAPI  # <--- correggiamo l'import
from config import load_config

def search_amazon(keyword, config):
    client = AmazonAPI(
        access_key=config['AMAZON_ACCESS_KEY'],
        secret_key=config['AMAZON_SECRET_KEY'],
        associate_tag=config['AMAZON_ASSOCIATE_TAG'],
        country=config['AMAZON_COUNTRY']
    )

    try:
        products = client.search_products(keywords=keyword, item_count=int(config['ITEM_COUNT']))
        results = []
        for p in products:
            results.append({
                "title": p.title,
                "url": p.detail_page_url,
                "price": p.price_and_currency[0] if p.price_and_currency else "N/A",
                "image": p.large_image_url,
                "description": p.title  # placeholder, puoi personalizzare
            })
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
