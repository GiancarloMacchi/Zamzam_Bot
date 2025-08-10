import os
from amazon_paapi import AmazonApi

# Recupero variabili d'ambiente
access_key = os.environ.get("AMAZON_ACCESS_KEY")
secret_key = os.environ.get("AMAZON_SECRET_KEY")
partner_tag = os.environ.get("AMAZON_PARTNER_TAG")
region = os.environ.get("AMAZON_REGION", "IT")

# Controllo variabili
if not all([access_key, secret_key, partner_tag]):
    raise ValueError("⚠️ Manca una o più variabili AMAZON_* nei Secrets di GitHub!")

# Inizializzo l'API
amazon = AmazonApi(access_key, secret_key, partner_tag, region)

# Esempio ricerca
try:
    products = amazon.search_products(keywords="laptop", search_index="All")
    for product in products:
        print(f"{product.title} - {product.detail_page_url}")
except Exception as e:
    print(f"Errore durante la ricerca: {e}")
