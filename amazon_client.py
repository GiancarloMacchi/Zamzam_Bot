import logging
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amazon_client")

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

def get_items(keywords):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keywords}")
    try:
        items = amazon.search_items(
            keywords=keywords,
            item_count=ITEM_COUNT,
            min_saving_percent=MIN_SAVE
        )
        return items
    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli da Amazon API:\n{e}")
        return []
