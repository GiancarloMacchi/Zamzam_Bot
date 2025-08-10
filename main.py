import logging
from amazon_paapi import AmazonApi
from amazon_paapi.models import SearchItemsRequest, SearchItemsResource
import os

# Configura logging
logging.basicConfig(level=logging.INFO, format="***%(asctime)s - %(levelname)s - %(message)s")

# Variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Inizializza Amazon API
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    country=AMAZON_COUNTRY
)

# Lista keywords
keywords = ["mamme", "neonati", "prima infanzia"]

# Risorse da richiedere
resources = [
    SearchItemsResource.ITEMINFO_TITLE,
    SearchItemsResource.OFFERS_LISTINGS_PRICE,
    SearchItemsResource.IMAGES_PRIMARY_LARGE
]

# Esegui ricerca per ogni keyword
failed_keywords = 0
for kw in keywords:
    logging.info(f"🔍 Cerco: {kw}")
    try:
        request = SearchItemsRequest(
            keywords=kw,
            search_index="All",
            resources=resources
        )
        response = amazon.search_items(request)
        logging.info(f"Trovati {len(response.items)} risultati per '{kw}'")
    except Exception as e:
        failed_keywords += 1
        logging.error(f"Errore ricerca '{kw}': {e}")

logging.info(f"❌ Keyword fallite: {failed_keywords}")
