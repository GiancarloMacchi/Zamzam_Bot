import os
from dotenv import load_dotenv
from amazon_api import cerca_prodotti
from telegram_bot import invia_messaggio

# Carica le variabili dal file .env
load_dotenv()

def esegui_bot():
    # Recupera e valida MIN_SAVE
    try:
        MIN_DISCOUNT = int(os.getenv("MIN_SAVE", "20").strip() or 20)
    except ValueError:
        MIN_DISCOUNT = 20

    KEYWORDS = os.getenv("KEYWORDS", "").split(",")
    ITEM_COUNT = int(os.getenv("ITEM_COUNT", "10").strip() or 10)
    RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

    if not KEYWORDS or all(k.strip() == "" for k in KEYWORDS):
        print("Nessuna keyword specificata. Controlla la variabile KEYWORDS.")
        return

    for keyword in KEYWORDS:
        keyword = keyword.strip()
        if not keyword:
            continue

        print(f"🔍 Ricerca per: {keyword}")
        prodotti = cerca_prodotti(keyword, ITEM_COUNT, MIN_DISCOUNT)

        if not prodotti:
            print(f"Nessun prodotto trovato per '{keyword}' con sconto minimo {MIN_DISCOUNT}%.")
            continue

        for prodotto in prodotti:
            invia_messaggio(prodotto)

    if RUN_ONCE:
        print("Esecuzione singola completata.")
    else:
        print("Modalità continua non implementata in questa versione.")

if __name__ == "__main__":
    esegui_bot()
