import os
import logging
from datetime import datetime
from amazon_paapi import AmazonApi
import bitlyshortener

# Nome file log con data e ora
log_filename = f"bot_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_amazon_client():
    return AmazonApi(
        os.getenv("AMAZON_ACCESS_KEY"),
        os.getenv("AMAZON_SECRET_KEY"),
        os.getenv("AMAZON_ASSOCIATE_TAG"),
        country=os.getenv("AMAZON_COUNTRY", "IT")
    )

def shorten_url(url):
    try:
        tokens_pool = [os.getenv("BITLY_TOKEN")]
        shortener = bitlyshortener.Shortener(tokens=tokens_pool, max_cache_size=256)
        return shortener.shorten_urls([url])[0]
    except Exception as e:
        logging.error(f"Errore nel creare short link: {e}")
        return url

def filter_products(items, min_discount=20):
    filtered = []
    for item in items:
        try:
            if not hasattr(item, "offers") or not item.offers:
                logging.debug(f"Scartato (no offerte): {getattr(item, 'ASIN', 'N/A')}")
                continue
            
            price_info = item.offers.listings[0].price
            if not price_info.savings:
                logging.debug(f"Scartato (no sconto): {getattr(item, 'ASIN', 'N/A')}")
                continue
            
            discount = int(price_info.savings.percentage)
            if discount < min_discount:
                logging.debug(f"Scartato (sconto {discount}% < {min_discount}%): {getattr(item, 'ASIN', 'N/A')}")
                continue

            category = (item.product_info.get("Category", "") or "").lower()
            if not any(keyword in category for keyword in ["infanzia", "bambini", "scuola", "genitori"]):
                logging.debug(f"Scartato (categoria non valida): {getattr(item, 'ASIN', 'N/A')}")
                continue

            filtered.append(item)
        except Exception as e:
            logging.warning(f"Errore nel filtrare un prodotto: {e}")
            continue
    return filtered
