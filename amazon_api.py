import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def cerca_prodotti(keywords, item_count=5, min_save=0):
    """
    Cerca prodotti su Amazon usando la libreria python-amazon-paapi.
    Ritorna solo quelli che hanno almeno la percentuale di sconto indicata.
    """
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

        if sconto >= min_save:
            prodotti_filtrati.append({
                "titolo": prodotto.title,
                "prezzo": prezzo_offerta,
                "prezzo_listino": prezzo_listino,
                "sconto": sconto,
                "link": prodotto.detail_page_url
            })

    return prodotti_filtrati
