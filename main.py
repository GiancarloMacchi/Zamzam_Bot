import os
from dotenv import load_dotenv
from amazon_api import cerca_prodotti
from telegram_api import invia_messaggio

# Carica le variabili d'ambiente
load_dotenv()

KEYWORDS = os.getenv("KEYWORDS")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

def main():
    print("🔍 Avvio ricerca prodotti Amazon...")
    prodotti = cerca_prodotti(KEYWORDS, item_count=ITEM_COUNT, min_save=MIN_SAVE)

    if not prodotti:
        print("❌ Nessun prodotto trovato.")
        return

    print(f"✅ Trovati {len(prodotti)} prodotti. Invio su Telegram...")
    for p in prodotti:
        messaggio = f"{p['titolo']}\n💰 Prezzo: {p['prezzo']}€"
        if p["risparmio"]:
            messaggio += f" (-{p['risparmio']}%)"
        messaggio += f"\n🔗 {p['link']}"
        invia_messaggio(messaggio)

    print("📤 Invio completato.")

if __name__ == "__main__":
    main()
