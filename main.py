import os
import logging
from utils import get_amazon_client, search_amazon_products, send_telegram_message

logging.basicConfig(level=logging.INFO)

CATEGORIES = [
    "Neonati", "Giochi", "Bambini", "Scuola", "Maternità", "Genitorialità"
]

MIN_DISCOUNT = int(os.getenv("MIN_SAVE", 20))

def main():
    client = get_amazon_client()

    for category in CATEGORIES:
        try:
            logging.info(f"🔍 Cerco offerte nella categoria: {category}")
            products = search_amazon_products(client, category, MIN_DISCOUNT)

            if not products:
                logging.info(f"Nessun prodotto trovato per {category}")
                continue

            for p in products:
                try:
                    send_telegram_message(p)
                except Exception as e:
                    logging.error(f"Errore nell'invio prodotto: {e}")

        except Exception as e:
            logging.error(f"Errore nella categoria {category}: {e}")

if __name__ == "__main__":
    main()
