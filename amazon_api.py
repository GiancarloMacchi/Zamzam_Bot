from amazon_paapi import AmazonApi
import os

# Carica le credenziali da variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Crea e restituisce un client Amazon PA-API
def get_amazon_client():
    return AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Recupera i prodotti da Amazon PA-API
def get_amazon_products(keywords, item_count=10):
    client = get_amazon_client()
    try:
        products = client.search_items(
            keywords=keywords,
            item_count=item_count
        )
        return products
    except Exception as e:
        print(f"Errore durante la ricerca dei prodotti Amazon: {e}")
        return []
