import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_messages_with_interval

logging.basicConfig(level=logging.INFO)

config = load_config()
KEYWORDS = config["KEYWORDS"]
ITEM_COUNT = int(config["ITEM_COUNT"])
DRY_RUN = config.get("DRY_RUN", True) in [True, "True", "true"]

logging.info("Avvio bot Amazon…")
products = search_amazon(KEYWORDS, ITEM_COUNT)
send_messages_with_interval(products, DRY_RUN=DRY_RUN)
logging.info("Esecuzione completata.")
