import json
import logging
import time
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Carica configurazione
with open("config.json", "r") as f:
    config = json.load(f)

DRY_RUN = config.get("DRY_RUN", True)
KEYWORDS = config.get("KEYWORDS", [])

logger = logging.getLogger(__name__)

def main():
    logger.info("Avvio bot Amazon…")

    for keyword in KEYWORDS:
        logger.info(f"Cercando prodotti per: {keyword}")
        products = search_amazon(keyword, config)

        if not products:
            continue

        for product in products:
            title = product.get("title", "Nessun titolo")
            url = product.get("url", "#")
            price = product.get("price", "N/A")
            image = product.get("image", "")
            description = product.get("description", "")

            message = (
                f"🔹 <b>{title}</b>\n"
                f"{url}\n"
                f"💰 Prezzo: {price}\n"
                f"{description}\n"
                f"Immagine: {image}"
            )

            if DRY_RUN:
                logger.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
            else:
                send_telegram_message(message)

            # Attesa di 30 minuti tra un prodotto e l'altro
            logger.info("Attendo 30 minuti prima della prossima offerta...")
            time.sleep(1800)  # 1800 secondi = 30 minuti

    logger.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
