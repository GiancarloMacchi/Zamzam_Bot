import os
import logging
from dotenv import load_dotenv
from amazon_paapi import AmazonApi

# Configurazione logging
logger = logging.getLogger(__name__)

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Inizializza il client Amazon API
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

def get_items(keywords):
    try:
        logger.info(f"🔍 Chiamata Amazon API con keyword: {keywords}")
        items = amazon.search_items(keywords)
        return items
    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli da Amazon API:\n{e}")
        return []
