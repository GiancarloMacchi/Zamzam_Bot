import os
from amazon_paapi import AmazonApi

# Prende le variabili direttamente dalle Repository Secrets
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

# Inizializza l'oggetto Amazon API
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def cerca_prodotti(keywords, item_count=5, min_save=0):
    """
    Cerca prodotti su Amazon usando python-amazon-paapi.
    Mostra anche quelli senza list_price per debug.
    """
    try:
        print(f"🔍 Ricerca prodotti con keywords: '{keywords}', "
              f"item_count={item_count}, min_save={min_save}")
        results = amazon.search_products(
            keywords=keywords,
            item_count=item_count
        )
    except Exception as e:
        print(f"❌ Errore durante la ricerca: {e}")
        return []

    prodotti_filtrati = []

    if not results:
        print("⚠ Nessun prodotto restituito dall'API.")
        return prodotti_filtrati

    for prodotto in results:
        prezzo_listino = prodotto.list_price or 0
        prezzo_offerta = prodotto.price or 0

        # Calcolo sconto solo se c'è listino
        if prezzo_listino and prezzo_offerta:
            sconto = round((prezzo_listino - prezzo_offerta) / prezzo_listino * 100, 2)
        else:
            sconto = 0  # Nessun dato di sconto disponibile

        # Filtraggio
        if sconto >= min_save or min_save == 0:
            prodotti_filtrati.append({
                "titolo": prodotto.title,
                "prezzo": prezzo_offerta if prezzo_offerta else "N/D",
                "prezzo_listino": prezzo_listino if prezzo_listino else "N/D",
                "sconto": sconto,
                "link": prodotto.detail_page_url
            })

    print(f"✅ Prodotti trovati: {len(prodotti_filtrati)}")
    return prodotti_filtrati
