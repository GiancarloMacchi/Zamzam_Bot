import os
from amazon.paapi import AmazonAPI
import bitlyshortener

AMAZON_ACCESS_KEY = os.environ['AMAZON_ACCESS_KEY']
AMAZON_SECRET_KEY = os.environ['AMAZON_SECRET_KEY']
AMAZON_ASSOCIATE_TAG = os.environ['AMAZON_ASSOCIATE_TAG']
AMAZON_COUNTRY = os.environ['AMAZON_COUNTRY']
KEYWORDS = os.environ['KEYWORDS'].split(',')
ITEM_COUNT = int(os.environ['ITEM_COUNT'])
MIN_SAVE = int(os.environ['MIN_SAVE'])
BITLY_TOKEN = os.environ['BITLY_TOKEN']

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
bitly = bitlyshortener.Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

def cerca_prodotti(keyword):
    try:
        products = amazon.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT
        )
        risultati = []
        for item in products.items:
            item_info = item.item_info
            title = item_info.title.display_value if item_info and item_info.title else "Senza titolo"
            price = None
            if item_info and item_info.product_info and item_info.product_info.list_price:
                price = item_info.product_info.list_price.amount
            if item_info and item_info.product_info and item_info.product_info.savings:
                savings = item_info.product_info.savings.percentage
            else:
                savings = 0
            if savings >= MIN_SAVE:
                url_corto = bitly.shorten_urls([item.detail_page_url])[0]
                risultati.append(f"{title} - Sconto: {savings}% - {url_corto}")
        return risultati
    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []
