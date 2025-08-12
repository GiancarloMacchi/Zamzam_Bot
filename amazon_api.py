import os
from amazon_paapi import AmazonAPI
from dotenv import load_dotenv

load_dotenv()

# ✅ Prende i dati dai secrets/env
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")  # Default Italia

# ✅ Inizializza API
amazon = AmazonAPI(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def cerca_prodotti(keywords, item_count=10):
    """Cerca prodotti su Amazon usando le API ufficiali."""
    try:
        results = amazon.search_items(
            keywords=keywords,
            item_count=item_count
        )
        prodotti = []
        for item in results.items:
            try:
                prodotti.append({
                    "asin": item.asin,
                    "titolo": item.item_info.title.display_value if item.item_info and item.item_info.title else "Senza titolo",
                    "prezzo": (
                        item.offers.listings[0].price.display_amount
                        if item.offers and item.offers.listings and item.offers.listings[0].price
                        else "N/A"
                    ),
                    "link": item.detail_page_url
                })
            except Exception as e:
                print(f"Errore parsing item: {e}")
        return prodotti
    except Exception as e:
        print(f"Errore ricerca prodotti: {e}")
        return []
