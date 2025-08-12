import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

# Carica variabili da .env (non influisce se usi Repository Secrets su GitHub)
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

def cerca_prodotti(keywords, item_count=5, min_save=0):
    """Cerca prodotti su Amazon usando amazon-paapi."""
    try:
        results = amazon.search_products(
            keywords=keywords,
            item_count=item_count
        )
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return []

    prodotti_filtrati = []
    for prodotto in results:
        prezzo_listino = prodotto.list_price or 0
        prezzo_offerta = prodotto.price or 0

        if prezzo_listino and prezzo_offerta:
            sconto = round((prezzo_listino - prezzo_offerta) / prezzo_listino * 100, 2)
        else:
            sconto = 0

        if sconto >= min_save or min_save == 0:
            prodotti_filtrati.append({
                "titolo": prodotto.title,
                "prezzo": prezzo_offerta if prezzo_offerta else "N/D",
                "prezzo_listino": prezzo_listino if prezzo_listino else "N/D",
                "sconto": sconto,
                "link": prodotto.detail_page_url
            })

    return prodotti_filtrati
