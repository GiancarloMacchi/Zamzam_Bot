import os
import logging
from dotenv import load_dotenv
from amazon_client import get_items
from telegram_bot import send_telegram_message

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carica variabili dal .env
load_dotenv()

KEYWORDS = os.getenv("KEYWORDS")

def main():
    logger.info("🔍 Recupero articoli da Amazon...")
    
    try:
        items = get_items(KEYWORDS)
    except Exception as e:
        logger.error(f"Errore durante il recupero degli articoli: {e}")
        send_telegram_message("❌ Errore nelle API Amazon.")
        return

    if not items:
        send_telegram_message("❌ Nessuna offerta trovata o errore nelle API Amazon.")
        return

    for item in items:
        title = item.get("title", "Senza titolo")
        url = item.get("url", "")
        send_telegram_message(f"{title}\n{url}")

if __name__ == "__main__":
    main()
