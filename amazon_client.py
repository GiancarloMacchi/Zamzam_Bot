import os
from amazon_paapi import AmazonAPI
from dotenv import load_dotenv

load_dotenv()

def get_items(keywords, item_count):
    amazon = AmazonAPI(
        os.getenv("AMAZON_ACCESS_KEY"),
        os.getenv("AMAZON_SECRET_KEY"),
        os.getenv("AMAZON_ASSOCIATE_TAG"),
        os.getenv("AMAZON_COUNTRY")
    )

    products = amazon.search_items(keywords=keywords, item_count=item_count)
    return products
