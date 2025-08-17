import time
import logging
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Avvio bot Amazon…")
    config = load_config()

    KEYWORDS = config["KEYWORDS"]
    ITEM_COUNT = int(config.get("ITEM_COUNT", 5))
    DRY_RUN = config.get("DRY_RUN", "True").lower() == "true"
    INTERVAL = int(config.get("INTERVAL_MINUTES", 30)) * 60  # intervallo in secondi

    all_products = []

    # ricerca prodotti per ogni keyword
    for keyword in KEYWORDS:
        logging.info(f"Cercando prodotti per: {keyword}")
        products = search_amazon(keyword, ITEM_COUNT)
        if not products:
            logging.warning(f"Nessun prodotto trovato per keyword: {keyword}")
        all_products.extend(products)

    if not all_products:
        logging.info("Nessun prodotto da inviare. Fine esecuzione.")
        return

    logging.info("Invio prodotti su Telegram con intervallo programmato...")
    for idx, product in enumerate(all_products, 1):
        message = f"🔹 <b>{product['title']}</b>\n"
        message += f"{product['url']}\n"
        message += f"💰 Prezzo: {product['price']}\n"
        message += f"{product['description']}\n"
        message += f"Immagine: {product['image']}"

        send_telegram_message(message, DRY_RUN)

        if idx < len(all_products):
            logging.info(f"Attendo {INTERVAL//60} minuti prima della prossima offerta...")
            time.sleep(INTERVAL)

    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
