import logging
import time
from config import load_config
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Configurazione logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Caricamento configurazione
config = load_config()
KEYWORDS = config.get("KEYWORDS", [])
DRY_RUN = config.get("DRY_RUN", True)
INTERVAL = config.get("TELEGRAM_INTERVAL_MINUTES", 30) * 60  # secondi

def main():
    logging.info("Avvio bot Amazon…")
    
    for keyword in KEYWORDS:
        logging.info(f"Cercando prodotti per: {keyword}")
        products = search_amazon(keyword, config)
        if not products:
            logging.info(f"Nessun prodotto trovato per: {keyword}")
            continue
        
        logging.info("Invio prodotti su Telegram con intervallo programmato...")
        for product in products:
            message = f"🔹 <b>{product['title']}</b>\n"
            message += f"{product['url']}\n"
            message += f"💰 Prezzo: {product['price']}\n"
            message += f"{product['description']}\n"
            message += f"Immagine: {product['image']}"

            send_telegram_message(message, dry_run=DRY_RUN)
            
            logging.info(f"Attendo {INTERVAL // 60} minuti prima della prossima offerta...")
            time.sleep(INTERVAL)
    
    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
