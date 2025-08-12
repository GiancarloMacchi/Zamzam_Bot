from utils import setup_logger
from amazon_api import get_amazon_client
import logging

def esegui_bot():
    setup_logger()
    logging.info("Avvio bot...")

    try:
        client = get_amazon_client()
        logging.info("Connessione ad Amazon API avvenuta con successo.")

        # Esempio di chiamata di test
        results = client.search_items(keywords="laptop", item_count=1)
        logging.info(f"Risultato ricerca: {results}")

    except Exception as e:
        logging.error(f"Errore durante l'esecuzione del bot: {e}")

if __name__ == "__main__":
    esegui_bot()
