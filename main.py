import os
import logging
from amazon_paapi import AmazonApi

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s"
)

# Credenziali e configurazione Amazon PAAPI
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Lista keyword (puoi modificarla o caricarla da un file)
KEYWORDS = [
    "mamme", "genitori", "neonati", "prima infanzia",
    "bambini", "giochi educativi", "scuola", "zaini scuola",
    "libri scolastici", "adolescenti", "genitorialità"
]

# Inizializza client Amazon
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, country=COUNTRY)

# Contatore keyword fallite
failed_keywords = 0

# Esegui ricerca per ogni keyword
for kw in KEYWORDS:
    logging.info(f"🔍 Cerco: {kw}")
    try:
        results = amazon.search_products(keywords=kw, search_index="All")
        logging.info(f"✅ {len(results)} risultati trovati per '{kw}'")
    except Exception as e:
        failed_keywords += 1
        logging.error(f"❌ Errore ricerca '{kw}': {e}")

logging.info(f"📊 Keyword fallite: {failed_keywords}")
