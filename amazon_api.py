from amazon.paapi import AmazonAPI
from config import load_config
import logging

config = load_config()
amazon = AmazonAPI(
    config["AMAZON_ACCESS_KEY"],
    config["AMAZON_SECRET_KEY"],
    config["AMAZON_ASSOCIATE_TAG"],
    config["AMAZON_COUNTRY"]
)

def search_amazon(keyword, item_count=5, dry_run=True):
    products = []
    if dry_run:
        logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
        for i in range(1, item_count + 1):
            products.append({
                "title": f"{keyword} Prodotto {i}",
                "url": f"https://www.amazon.***/dp/EXAMPLE{i}",
                "price": f"{i*10},99€",
                "description": f"Breve descrizione di {keyword} {i}",
                "image": f"https://via.placeholder.com/150?text={keyword}+{i}"
            })
        return products

    try:
        items = amazon.search_products(keywords=keyword, search_index="All", item_count=item_count)
        for item in items:
            products.append({
                "title": item.title,
                "url": item.detail_page_url,
                "price": item.price_and_currency[0] if item.price_and_currency else "N/A",
                "description": item.features[0] if item.features else "Descrizione non disponibile",
                "image": item.images[0].url if item.images else None
            })
    except Exception as e:
        logging.error(f"Errore API Amazon: {str(e)}")
    return products
