import os
import requests

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "bambino,neonato,giocattolo,scuola,libro")

def cerca_prodotti():
    risultati = []

    for keyword in KEYWORDS.split(","):
        keyword = keyword.strip()
        url = f"https://api.rainforestapi.com/request"
        params = {
            "api_key": AMAZON_ACCESS_KEY,
            "type": "search",
            "amazon_domain": f"amazon.{AMAZON_COUNTRY.lower()}",
            "search_term": keyword,
            "sort_by": "featured",
            "page": 1
        }

        try:
            r = requests.get(url, params=params)
            data = r.json()

            for item in data.get("search_results", [])[:ITEM_COUNT]:
                titolo = item.get("title", "").strip()
                asin = item.get("asin", "")
                link = f"https://www.amazon.{AMAZON_COUNTRY.lower()}/dp/{asin}?tag={AMAZON_ASSOCIATE_TAG}"

                prezzo_attuale = None
                prezzo_listino = None

                # Prezzo attuale
                if "price" in item and isinstance(item["price"], dict):
                    prezzo_attuale = item["price"].get("value", None)

                # Prezzo di listino (se disponibile)
                if "list_price" in item and isinstance(item["list_price"], dict):
                    prezzo_listino = item["list_price"].get("value", None)

                risultati.append({
                    "title": titolo,
                    "url": link,
                    "price": prezzo_attuale,
                    "list_price": prezzo_listino
                })

        except Exception as e:
            print(f"Errore nella ricerca per {keyword}: {e}")

    return risultati
