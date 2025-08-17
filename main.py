import time
import logging
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message_scheduled

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Avvio bot Amazon…")
config = load_config()
KEYWORDS = config["KEYWORDS"]
ITEM_COUNT = int(config["ITEM_COUNT"])
DRY_RUN = config.get("DRY_RUN", True)

all_products = []

for kw in KEYWORDS:
    logging.info(f"Cercando prodotti per: {kw}")
    products = search_amazon(keyword=kw, item_count=ITEM_COUNT, dry_run=DRY_RUN)
    all_products.extend(products)

if all_products:
    logging.info("Invio prodotti su Telegram con intervallo programmato...")
    send_telegram_message_scheduled(all_products, dry_run=DRY_RUN)
else:
    logging.info("Nessun prodotto trovato.")
