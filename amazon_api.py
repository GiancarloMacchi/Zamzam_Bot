import os
import requests

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Parole chiave per categorie ammesse
CATEGORIE_AMMESSE = [
    "bambini", "infanti", "genitori", "scuola",
    "libri per ragazzi", "giocattoli", "videogiochi"
]

def prodotto_valido(prodotto):
    """
    Ritorna True se il prodotto ha sconto >= 20% e appartiene a una categoria ammessa.
    """
    try:
        prezzo_originale = float(prodotto.get("price", 0))
        prezzo_scontato = float(prodotto.get("discounted_price", prezzo_originale))
        sconto = 0
        if prezzo_originale > 0:
            sconto = ((prezzo_originale - prezzo_scontato) / prezzo_originale) * 100

        categoria = prodotto.get("category", "").lower()

        return sconto >= 20 or any(cat in categoria for cat in CATEGORIE_AMMESSE)
    except Exception:
        return False

def cerca_prodotti(parola_chiave):
    """
    Simula la chiamata all'API di Amazon e filtra i prodotti validi.
    """
    # Qui va implementata la chiamata reale all'API di Amazon PA-API
    # Per esempio fittizio:
    prodotti = [
        {"title": "Giocattolo educativo", "price": 50, "discounted_price": 35, "category": "giocattoli"},
        {"title": "Libro per ragazzi", "price": 20, "discounted_price": 18, "category": "libri"},
        {"title": "Mouse da gaming", "price": 40, "discounted_price": 25, "category": "videogiochi"}
    ]

    return [p for p in prodotti if prodotto_valido(p)]
