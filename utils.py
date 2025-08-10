from amazon.paapi import AmazonAPI
import os

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")

def cerca_prodotti(keyword):
    amazon = AmazonAPI(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )
    products = amazon.search_items(keywords=keyword)
    return products
