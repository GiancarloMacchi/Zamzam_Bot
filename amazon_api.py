import logging
import time
from amazon.paapi import AmazonAPI  # Assicurati che python-amazon-paapi sia installato

MAX_RETRIES = 3
RETRY_DELAY = 5  # secondi

def search_amazon(keyword, config):
    """
    Restituisce una lista di prodotti da Amazon per la keyword.
    Ogni prodotto: {'title', 'url', 'price', 'description', 'image'}
    """
    products = []
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            # Simulazione di chiamata reale a PA-API
            # Sostituire con AmazonAPI effettivo
            logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
            for i in range(1, 10):
                products.append({
                    "title": f"{keyword} Prodotto {i}",
                    "url": f"https://www.amazon.***/dp/EXAMPLE{i}",
                    "price": f"{i*10},99€",
                    "description": f"Breve descrizione di {keyword} {i}",
                    "image": f"https://via.placeholder.com/150?text={keyword}+{i}"
                })
            return products
        
        except Exception as e:
            retries += 1
            logging.error(f"Errore ricerca Amazon: {e} - Tentativo {retries}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    
    logging.warning(f"Nessun prodotto trovato per {keyword} dopo {MAX_RETRIES} tentativi.")
    return products
