import logging
from config import load_config
from amazon.paapi import AmazonAPI  # richiede pacchetto python-amazon-paapi

config = load_config()

# Inizializzazione PA-API
amazon = AmazonAPI(
    config["AMAZON_ACCESS_KEY"],
    config["AMAZON_SECRET_KEY"],
    config["AMAZON_ASSOCIATE_TAG"],
    config["AMAZON_COUNTRY"]
)

def search_amazon(keyword):
    try:
        logging.info(f"Cercando prodotti reali per keyword: {keyword}")
        items = amazon.search_products(keywords=keyword, item_count=int(config["ITEM_COUNT"]))
        products = []

        for item in items:
            products.append({
                "title": item.title,
                "url": item.detail_page_url,
                "price": getattr(item, 'price_and_currency', "N/A"),
                "image_url": item.images[0].url if item.images else None,
                "description": getattr(item, 'features', [""])[0]  # prima caratteristica come descrizione breve
            })
        return products
    except Exception as e:
        logging.error(f"Errore API Amazon: {e}")
        return []
