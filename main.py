import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG")
REGION = os.getenv("AMAZON_REGION", "IT")  # Default Italia

# Inizializza il client API
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, PARTNER_TAG, REGION)

def search_items(keywords, search_index="All", item_count=5):
    """
    Cerca prodotti su Amazon usando le API PA-API 5.0
    """
    try:
        results = amazon.search_items(
            keywords=keywords,
            search_index=search_index,
            item_count=item_count
        )
        for item in results.items:
            print(f"Titolo: {item.item_info.title.display_value}")
            print(f"ASIN: {item.asin}")
            if item.detail_page_url:
                print(f"URL: {item.detail_page_url}")
            print("-" * 40)
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")

if __name__ == "__main__":
    search_items("laptop")
