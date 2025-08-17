import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message_with_interval

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    config = load_config()
    DRY_RUN = config["DRY_RUN"]
    KEYWORDS = config["KEYWORDS"]
    ITEM_COUNT = int(config.get("ITEM_COUNT", 5))

    logging.info("Avvio bot Amazon…")

    all_products = []

    # Ciclo su tutte le keyword
    for keyword in KEYWORDS:
        logging.info(f"Cercando prodotti per: {keyword}")
        try:
            if DRY_RUN:
                logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
                # Simulazione prodotti di test
                products = [
                    {
                        "title": f"{keyword} Prodotto {i+1}",
                        "url": f"https://www.amazon.***/dp/EXAMPLE{i+1}",
                        "price": f"{10*(i+1)},99€",
                        "description": f"Breve descrizione di {keyword} {i+1}",
                        "image": f"https://via.placeholder.com/150?text={keyword}+{i+1}"
                    }
                    for i in range(ITEM_COUNT)
                ]
            else:
                products = search_amazon(keyword, ITEM_COUNT)
            all_products.extend(products)
        except Exception as e:
            logging.error(f"Errore durante la ricerca di '{keyword}': {e}")

    # Invio prodotti su Telegram con intervallo
    send_telegram_message_with_interval(all_products, config)

    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
