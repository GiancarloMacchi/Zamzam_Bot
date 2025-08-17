import logging
import time
from amazon_paapi import AmazonAPI


def search_amazon(keyword, config, max_retries=3, delay=10):
    """
    Cerca prodotti su Amazon usando le API PAAPI.
    Ritorna una lista di prodotti (dizionari con 'title' e 'url').
    """
    amazon = AmazonAPI(
        config["AMAZON_ACCESS_KEY"],
        config["AMAZON_SECRET_KEY"],
        config["AMAZON_ASSOCIATE_TAG"],
        config["AMAZON_COUNTRY"],
    )

    for attempt in range(1, max_retries + 1):
        try:
            products = amazon.search_items(
                keywords=keyword,
                item_count=int(config.get("ITEM_COUNT", 3))
            )

            results = []
            for item in products.items:
                try:
                    results.append({
                        "title": item.item_info.title.display_value,
                        "url": item.detail_page_url,
                    })
                except AttributeError:
                    continue  # se manca qualche campo, saltiamo l'item

            if results:
                return results

        except Exception as e:
            logging.warning(
                f"Errore API Amazon: {e} - Tentativo {attempt}/{max_retries}"
            )
            time.sleep(delay)

    return []
