import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = load_config()
keywords = config['KEYWORDS']

logging.info("Avvio bot Amazon…")

for keyword in keywords:
    logging.info(f"Cercando prodotti per: {keyword}")
    attempts = 3
    for attempt in range(attempts):
        try:
            products = search_amazon(keyword, config)
            if products:
                send_telegram_message(products, config)
            break
        except Exception as e:
            logging.warning(f"Errore API Amazon: {e} - Tentativo {attempt+1}/{attempts}")
            time.sleep(10)
    else:
        logging.error(f"Falliti tutti i tentativi per keyword: {keyword}")
    time.sleep(1800)  # 30 minuti tra un invio e l'altro

logging.info("Esecuzione completata.")
