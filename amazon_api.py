# amazon_api.py
from amazon_paapi import AmazonApi
import os

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")  # default Italia

def get_amazon_client():
    """Crea e restituisce un client Amazon API."""
    return AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

def get_amazon_products(keyword, item_count=10):
    """
    Cerca prodotti su Amazon in base alla keyword.
    Ritorna una lista di oggetti prodotto.
    """
    client = get_amazon_client()
    try:
        items = client.search_items(
            keywords=keyword,
            search_index="All",
            item_count=item_count
        )
        return items
    except Exception as e:
        print(f"Errore durante la ricerca di '{keyword}': {e}")
        return []
