import logging
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_products

import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = load_config()
KEYWORDS = config.get("KEYWORDS", [])

logging.info("Avvio bot Amazon…")

all_products = []
for kw in KEYWORDS:
    logging.info(f"Cercando prodotti per: {kw}")
    products = search_amazon(kw)
    all_products.extend(products)

if all_products:
    logging.info("Invio prodotti su Telegram con intervallo programmato...")
    send_products(all_products, interval_minutes=30)
else:
    logging.info("Nessun prodotto trovato.")

logging.info("Esecuzione completata.")
