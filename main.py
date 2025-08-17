import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main():
    logging.info("Avvio bot Amazon…")
    config = load_config()

    for keyword in config["KEYWORDS"]:
        logging.info(f"Cercando prodotti per: {keyword}")

        # ✅ Passiamo config alla funzione
        products = search_amazon(keyword, config)

        if not products:
            logging.error(f"Falliti tutti i tentativi per keyword: {keyword}")
            continue

        for product in products:
            message = f"{product['title']}\n{product['url']}"
            send_telegram_message(message, config)
            time.sleep(2)  # per non spammare troppo

    logging.info("Esecuzione completata.")


if __name__ == "__main__":
    main()
