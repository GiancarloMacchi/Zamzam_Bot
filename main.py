import os
from dotenv import load_dotenv
from amazon_api import cerca_prodotti
from telegram_api import invia_messaggio

# Carica variabili da .env
load_dotenv()

KEYWORDS = os.getenv("KEYWORDS", "")
ITEM_COUNT = int(os.getenv("ITEM_COUNT") or 5)
MIN_SAVE = int(os.getenv("MIN_SAVE") or 20)  # Sconto minimo in %
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

def formatta_prodotto(prodotto):
    """Crea un testo formattato per Telegram."""
    titolo = prodotto.get("titolo", "Senza titolo")
    prezzo = prodotto.get("prezzo", "Prezzo non disponibile")
    url = prodotto.get("url", "")
    return f"<b>{titolo}</b>\n💰 {prezzo}\n🔗 {url}"

def main():
    if not KEYWORDS:
        print("❌ Nessuna parola chiave trovata in KEYWORDS. Controlla il file .env")
        return

    print(f"🔍 Ricerca prodotti per parole chiave: {KEYWORDS}")
    prodotti = cerca_prodotti(KEYWORDS, item_count=ITEM_COUNT)

    if not prodotti:
        print("⚠️ Nessun prodotto trovato.")
        return

    for prodotto in prodotti:
        messaggio = formatta_prodotto(prodotto)
        invia_messaggio(messaggio)

    print("✅ Ricerca completata.")

    if RUN_ONCE:
        print("🛑 Modalità RUN_ONCE attiva. Script terminato.")

if __name__ == "__main__":
    main()
