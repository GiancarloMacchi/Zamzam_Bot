import os
from dotenv import load_dotenv
from amazon_paapi import AmazonAPI

# Carica le variabili d'ambiente
load_dotenv()

# Legge i valori dai secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def cerca_prodotti(keywords, item_count=10, min_save=None):
    """
    Cerca prodotti su Amazon in base a parole chiave.
    :param keywords: Stringa di ricerca.
    :param item_count: Numero massimo di risultati.
    :param min_save: Sconto minimo richiesto in percentuale.
    :return: Lista di dizionari con titolo, link e prezzo.
    """
    risultati = []
    try:
        items = amazon.search_items(keywords, item_count=item_count)
        for item in items:
            titolo = item.title
            link = item.detail_page_url
            prezzo = item.offers.listings[0].price.amount if item.offers else None
            risparmio = None
            if item.offers and item.offers.listings[0].price.savings:
                risparmio = item.offers.listings[0].price.savings.percentage

            if min_save is None or (risparmio and risparmio >= min_save):
                risultati.append({
                    "titolo": titolo,
                    "link": link,
                    "prezzo": prezzo,
                    "risparmio": risparmio
                })

    except Exception as e:
        print(f"Errore durante la ricerca prodotti: {e}")

    return risultati
