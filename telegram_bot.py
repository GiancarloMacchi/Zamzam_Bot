import os
import requests
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def invia_messaggio(testo):
    """
    Invia un messaggio di testo al canale/chat Telegram.
    :param testo: Stringa del messaggio.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TOKEN o CHAT_ID mancanti. Controlla il file .env")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": testo,
        "disable_web_page_preview": False,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("📨 Messaggio inviato con successo")
            return True
        else:
            print(f"❌ Errore Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Errore nell'invio del messaggio Telegram: {e}")
        return False
