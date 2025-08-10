import os
from amazon_paapi import AmazonAPI

# Carica le variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Lista di keyword
KEYWORDS = os.getenv("KEYWORDS", "scarpe,orologio").split(",")

def cerca_prodotti(keyword):
    amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
    prodotti = amazon.search_items(
        keywords=keyword,
        search_index="All",
        item_count=int(os.getenv("ITEM_COUNT", "10"))
    )
    results = []
    for item in prodotti:
        results.append({
            "titolo": item.item_info.title.display_value if item.item_info and item.item_info.title else None,
            "prezzo": item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else None,
            "url": item.detail_page_url
        })
    return results
