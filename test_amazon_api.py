import os
from dotenv import load_dotenv
from amazon_paapi import AmazonApi

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")

amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

print("🔍 Test connessione Amazon API...")
print(f"Marketplace: {COUNTRY}, Associate Tag: {ASSOCIATE_TAG}")

try:
    results = amazon.search_items(keywords="laptop", item_count=3)
    if results and results.items:
        print(f"✅ Trovati {len(results.items)} articoli!")
        for item in results.items:
            print("-", item.item_info.title.display_value)
    else:
        print("⚠️ Nessun articolo trovato.")
except Exception as e:
    print("❌ Errore Amazon API:")
    print(e)
