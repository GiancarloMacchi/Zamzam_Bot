import logging
import time
from config import load_config
from telegram_bot import send_telegram_message
from amazon_api import search_amazon

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"
KEYWORDS = config["KEYWORDS"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DELAY_SECONDS = 1800  # 30 minuti tra un invio e l'altro

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
                image_url=product.get("image_url"),
                description=product.get("description")
            )

            logging.info(f"Attendo {DELAY_SECONDS} secondi prima del prossimo invio…")
            time.sleep(DELAY_SECONDS)

    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
