import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def cerca_prodotti(keyword, item_count=5, min_save=0):
    risultati = []
    try:
        prodotti = amazon.search_items(
            keywords=keyword,
            search_index="All",
            item_count=item_count
        )

        for item in prodotti.items:
            titolo = getattr(item.item_info.title, 'display_value', None)
            prezzo = getattr(item.offers.listings[0].price, 'amount', None) if item.offers else None
            sconto = None
            descrizione = getattr(item.item_info.by_line_info, 'manufacturer', None)

            if item.offers and hasattr(item.offers.listings[0], 'saving_basis'):
                base = getattr(item.offers.listings[0].saving_basis.price, 'amount', None)
                if base and prezzo:
                    sconto = round((base - prezzo) / base * 100)

            if sconto is not None and sconto < min_save:
                continue

            if titolo and prezzo:
                risultati.append({
                    "titolo": titolo,
                    "prezzo": prezzo,
                    "sconto": sconto if sconto is not None else 0,
                    "link": item.detail_page_url,
                    "descrizione": descrizione if descrizione else ""
                })

    except Exception as e:
        print(f"Errore nella ricerca prodotti: {e}")

    return risultati
