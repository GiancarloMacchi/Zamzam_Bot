from amazon_api import cerca_prodotti
from telegram_bot import invia_messaggio
import os

# Parole chiave per la macro-categoria
CATEGORIE_BAMBINI = [
    "bambino", "bambini", "infanzia", "genitore", "genitori",
    "scuola", "libro", "libri", "ragazzi", "ragazzo",
    "giocattolo", "giocattoli", "videogiochi", "videogioco", "neonato", "neonati"
]

def prodotto_in_categoria(titolo: str) -> bool:
    titolo_lower = titolo.lower()
    return any(keyword in titolo_lower for keyword in CATEGORIE_BAMBINI)

def calcola_sconto(prezzo_attuale: float, prezzo_originale: float) -> float:
    try:
        if prezzo_originale and prezzo_originale > 0:
            return round((prezzo_originale - prezzo_attuale) / prezzo_originale * 100, 2)
    except Exception:
        pass
    return 0.0

def main():
    risultati = cerca_prodotti()

    for prodotto in risultati:
        titolo = prodotto.get("title", "").strip()
        prezzo_attuale = prodotto.get("price", None)
        prezzo_originale = prodotto.get("list_price", None)
        url = prodotto.get("url", "")

        # Calcola lo sconto
        sconto = calcola_sconto(prezzo_attuale, prezzo_originale)

        # Filtro 1: sconto >= 20%
        if sconto < 20:
            continue

        # Filtro 2: categoria bambini/genitori/scuola
        if not prodotto_in_categoria(titolo):
            continue

        # Messaggio finale
        messaggio = f"{titolo} - {prezzo_attuale}€ ({sconto}% di sconto) - {url}"
        invia_messaggio(messaggio)

if __name__ == "__main__":
    main()
