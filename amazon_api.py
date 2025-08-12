import os
from dotenv import load_dotenv
from amazon_paapi import AmazonAPI

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

def cerca_prodotti(parole_chiave, item_count=5):
    try:
        amazon = AmazonAPI(
            AMAZON_ACCESS_KEY,
            AMAZON_SECRET_KEY,
            AMAZON_ASSOCIATE_TAG,
            AMAZON_COUNTRY
        )

        prodotti = amazon.search_items(
            keywords=parole_chiave,
            search_index="All",
            item_count=item_count
        )

        risultati = []
        for prodotto in prodotti.items:
            titolo = prodotto.item_info.title.display_value if prodotto.item_info and prodotto.item_info.title else "Titolo non disponibile"
            url = prodotto.detail_page_url or ""
            prezzo = None

            # Cerca il prezzo
            if prodotto.offers and prodotto.offers.listings:
                listing = prodotto.offers.listings[0]
                if listing.price and listing.price.display_amount:
                    prezzo = listing.price.display_amount

            risultati.append({
                "titolo": titolo,
                "url": url,
                "prezzo": prezzo or "Prezzo non disponibile"
            })

        return risultati

    except Exception as e:
        print(f"Errore durante la ricerca dei prodotti: {e}")
        return []
