import os
import sys
from dotenv import load_dotenv
from amazon_client import get_items
import requests
import traceback

# Carica variabili da .env se presenti (utile in locale)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_ONCE = os.getenv("RUN_ONCE", "true").lower() == "true"

def send_telegram_message(message):
    """Invia un messaggio a Telegram e ritorna True/False in base al risultato."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("✅ Messaggio inviato con successo.")
            return True
        else:
            print(f"❌ Errore nell'invio del messaggio. Status code: {r.status_code}")
            print(r.text)
            return False
    except Exception as e:
        print(f"❌ Errore di rete nell'invio del messaggio: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Avvio Amazon Bot...")
    print(f"🌍 Paese Amazon: {os.getenv('AMAZON_COUNTRY')}")
    print(f"🔍 Parole chiave: {os.getenv('KEYWORDS')}")
    print(f"📉 Sconto minimo: {os.getenv('MIN_SAVE')}%")
    print(f"📦 Numero massimo risultati: {os.getenv('ITEM_COUNT')}")

    try:
        items = get_items()
    except Exception as e:
        print("❌ Errore durante il recupero degli articoli da Amazon API:")
        traceback.print_exc()
        sys.exit(1)

    if not items:
        print("⚠️ Nessun prodotto trovato con i criteri impostati.")
    else:
        print(f"📌 Trovati {len(items)} prodotti.")
        for msg in items:
            print(f"---\n{msg}\n---")
            send_telegram_message(msg)

    if RUN_ONCE:
        print("🏁 Esecuzione completata (RUN_ONCE=True).")
    else:
        print("♻️ Loop continuo disabilitato per ora.")
