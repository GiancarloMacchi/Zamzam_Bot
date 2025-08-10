import logging
from amazon_paapi import AmazonApi

# --- CONFIGURAZIONE ---
ACCESS_KEY = "TUO_ACCESS_KEY"
SECRET_KEY = "TUO_SECRET_KEY"
TAG = "TUO_ASSOCIATE_TAG"
REGION = "IT"

# Inizializza logger
logging.basicConfig(level=logging.INFO, format="***%(asctime)s - %(levelname)s - %(message)s")

# Inizializza API Amazon
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, TAG, REGION)

# Lista keyword da cercare
keywords = [
    "mamme",
    "prima infanzia",
    "bambini",
    "scuola",
    "libri scuola",
    "genitorialità"
]

fallite = 0

for kw in keywords:
    logging.info(f"🔍 Cerco: {kw}")
    try:
        results = amazon.search_products(
            keywords=kw,
            search_index="All",
            item_count=5
        )

        if not results:
            logging.warning(f"Nessun risultato per '{kw}'")
            fallite += 1
        else:
            for item in results:
                logging.info(f"- {item.title} | {item.detail_page_url}")

    except Exception as e:
        logging.error(f"Errore ricerca '{kw}': {e}")
        fallite += 1

logging.info(f"❌ Keyword fallite: {fallite}")
