import time
import logging
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carica configurazione
config = load_config()
KEYWORDS = config["KEYWORDS"]
DRY_RUN = config.get("DRY_RUN", True)
RETRY_COUNT = config.get("RETRY_COUNT", 3)
RETRY_DELAY = config.get("RETRY_DELAY", 10)  # secondi
INTERVAL_MINUTES = config.get("INTERVAL_MINUTES", 30)

logging.info("Avvio bot Amazon…")

all_products = []

# Cerca prodotti per ogni keyword
for keyword in KEYWORDS:
    logging.info(f"Cercando prodotti per: {keyword}")
    retry_attempts = 0
    while retry_attempts < RETRY_COUNT:
        try:
            products = search_amazon(keyword)
            all_products.extend(products)
            break
        except Exception as e:
            retry_attempts += 1
            logging.warning(f"Errore API Amazon: {e} - Tentativo {retry_attempts}/{RETRY_COUNT}")
            time.sleep(RETRY_DELAY)
    else:
        logging.error(f"Falliti tutti i tentativi per keyword: {keyword}")

# Invio prodotti su Telegram dilazionato
if all_products:
    logging.info("Invio prodotti su Telegram con intervallo programmato...")
    for idx, product in enumerate(all_products, start=1):
        title = product.get("title", "N/A")
        url = product.get("url", "#")
        price = product.get("price", "N/A")
        image = product.get("image", "")
        description = product.get("description", "")

        message = f"🔹 <b>{title}</b>\n{url}\n💰 Prezzo: {price}\n{description}\nImmagine: {image}"

        if DRY_RUN:
            logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
        else:
            send_telegram_message(message)

        logging.info(f"Attendo {INTERVAL_MINUTES} minuti prima della prossima offerta...")
        time.sleep(INTERVAL_MINUTES * 60)

logging.info("Esecuzione completata.")
