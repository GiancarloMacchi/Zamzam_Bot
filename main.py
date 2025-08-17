import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    config = load_config()
    keywords = config.get("KEYWORDS", ["regali bambino", "regali mamma", "regali papà", "lego", "scuola"])

    logging.info("Avvio bot Amazon…")

    for keyword in keywords:
        logging.info(f"Cercando prodotti per: {keyword}")

        # Chiamata API Amazon con retry
        success = False
        for attempt in range(3):
            try:
                results = search_amazon(config, keyword)
                if results:
                    logging.info(f"Trovati {len(results)} risultati per '{keyword}'")

                    for item in results:
                        message = f"🎁 {item['title']}\n{item['url']}"
                        send_telegram_message(config, message)

                    success = True
                    break
            except Exception as e:
                logging.warning(f"Errore API Amazon: {e} - Tentativo {attempt + 1}/3")
                time.sleep(10)

        if not success:
            logging.error(f"Falliti tutti i tentativi per keyword: {keyword}")

    logging.info("Esecuzione completata.")


if __name__ == "__main__":
    main()
