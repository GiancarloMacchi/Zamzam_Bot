import os
from amazon_paapi import AmazonApi

# Prende le credenziali direttamente dalle repository secrets di GitHub Actions
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Inizializza il client Amazon API
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def cerca_prodotti(keywords, item_count=10, min_save=0):
    """
    Cerca prodotti su Amazon usando python-amazon-paapi.
    Filtra in base al risparmio minimo (min_save in percentuale).
    """
    try:
        results = amazon.search_items(
            keywords=keywords,
            item_count=item_count
        )

        prodotti = []
        for item in results.get("SearchResult", {}).get("Items", []):
            try:
                titolo = item["ItemInfo"]["Title"]["DisplayValue"]
                link = item["DetailPageURL"]
                prezzo = item.get("Offers", {}).get("Listings", [])[0]["Price"]["DisplayAmount"]
                prezzo_attuale = item.get("Offers", {}).get("Listings", [])[0]["Price"]["Amount"]
                prezzo_listino = item.get("Offers", {}).get("Listings", [])[0]["SavingBasis"]["Amount"] if "SavingBasis" in item.get("Offers", {}).get("Listings", [])[0] else prezzo_attuale
                risparmio = 0
                if prezzo_listino > prezzo_attuale:
                    risparmio = round(((prezzo_listino - prezzo_attuale) / prezzo_listino) * 100, 2)

                if risparmio >= min_save:
                    prodotti.append({
                        "titolo": titolo,
                        "link": link,
                        "prezzo": prezzo,
                        "risparmio": risparmio
                    })
            except Exception:
                continue

        return prodotti

    except Exception as e:
        print(f"❌ Errore durante la ricerca: {e}")
        return []
