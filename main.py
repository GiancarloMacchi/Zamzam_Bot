import logging
from config import load_config
from telegram_bot import send_telegram_message
import requests
from urllib.parse import quote

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AMAZON_ACCESS_KEY = config["AMAZON_ACCESS_KEY"]
AMAZON_SECRET_KEY = config["AMAZON_SECRET_KEY"]
AMAZON_ASSOCIATE_TAG = config["AMAZON_ASSOCIATE_TAG"]
AMAZON_COUNTRY = config["AMAZON_COUNTRY"]
KEYWORDS = [kw.strip() for kw in config["KEYWORDS"].split(",")]
ITEM_COUNT = int(config["ITEM_COUNT"])

def search_amazon(keyword):
    """
    Semplice simulazione ricerca Amazon tramite URL.
    Restituisce lista di prodotti come dizionari: title, url, price, image_url
    """
    # Questo è un esempio. Qui dovrai sostituire con una vera chiamata API Amazon PA-API
    products = []
    for i in range(1, ITEM_COUNT+1):
        products.append({
            "title": f"{keyword} Prodotto {i}",
            "url": f"https://www.amazon.{AMAZON_COUNTRY}/dp/EXAMPLE{i}",
            "price": f"{10*i},99€",
            "image_url": f"https://via.placeholder.com/150?text={quote(keyword)}+{i}"
        })
    return products

def main():
    logging.info("Avvio bot Amazon…")

    for keyword in KEYWORDS:
        logging.info(f"Cercando prodotti per: {keyword}")
        products = search_amazon(keyword)
        for product in products:
            send_telegram_message(
                title=product.get("title"),
                url=product.get("url"),
                price=product.get("price"),
                image_url=product.get("image_url")
            )

    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
