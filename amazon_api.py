import os
from dotenv import load_dotenv
from amazon_paapi.amazon_api import AmazonAPI  # ✅ Import corretto
from amazon_paapi.models import Condition, SearchIndex

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def cerca_prodotti(keyword, item_count=5):
    try:
        items = amazon.search_items(
            keywords=keyword,
            search_index=SearchIndex.ALL,
            item_count=item_count,
            condition=Condition.NEW,
        )

        risultati = []
        for item in items:
            risultati.append({
                "titolo": item.item_info.title.display_value if item.item_info and item.item_info.title else "N/A",
                "prezzo": item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else "N/D",
                "url": item.detail_page_url,
            })
        return risultati
    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []
