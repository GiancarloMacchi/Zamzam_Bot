import os
from amazon_paapi import AmazonApi

# Recupero credenziali da variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG]):
    raise EnvironmentError("Mancano una o più variabili d'ambiente Amazon.")

amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def cerca_prodotti(keywords, item_count=10):
    return amazon.search_items(keywords=keywords, item_count=item_count)
