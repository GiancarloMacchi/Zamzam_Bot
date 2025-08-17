import logging
from config import load_config

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"

if not DRY_RUN:
    try:
        from amazon.paapi import AmazonAPI
        amazon = AmazonAPI(
            config["AMAZON_ACCESS_KEY"],
            config["AMAZON_SECRET_KEY"],
            config["AMAZON_ASSOCIATE_TAG"],
            config["AMAZON_COUNTRY"]
        )
    except ImportError:
        logging.error("Pacchetto python-amazon-paapi non installato. Passo in DRY_RUN.")
        DRY_RUN = True

def search_amazon(keyword):
    if DRY_RUN:
        logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
        products = []
        for i in range(1, 6):  # genera 5 prodotti fittizi
            products.append({
                "title": f"{keyword} Prodotto {i}",
                "url": f"https://www.amazon.***/dp/EXAMPLE{i}",
                "price": f"{i*10},99€",
                "image_url": f"https://via.placeholder.com/150?text={keyword}+{i}",
                "description": f"Breve descrizione di {keyword} {i}"
            })
        return products

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
                "description": getattr(item, 'features', [""])[0]  # prima caratteristica
            })
        return products

    except Exception as e:
        logging.error(f"Errore API Amazon: {e}")
        return []
