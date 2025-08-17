import logging
from paapi import AmazonAPI


def search_amazon(config, keyword):
    """Cerca prodotti su Amazon e restituisce lista di dict {title, url}"""
    amazon = AmazonAPI(
        config["AMAZON_ACCESS_KEY"],
        config["AMAZON_SECRET_KEY"],
        config["AMAZON_ASSOCIATE_TAG"],
        config["AMAZON_COUNTRY"]
    )

    try:
        items = amazon.search_items(keywords=keyword, item_count=int(config.get("ITEM_COUNT", 5)))
        results = []

        for item in items:
            try:
                title = item.title if hasattr(item, "title") else "Senza titolo"
                url = item.detail_page_url if hasattr(item, "detail_page_url") else "Nessun link"
                results.append({
                    "title": title,
                    "url": url
                })
            except Exception as e:
                logging.warning(f"Impossibile processare un item Amazon: {e}")

        return results

    except Exception as e:
        logging.error(f"Errore in search_amazon: {e}")
        raise
