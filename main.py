from utils import cerca_prodotti, KEYWORDS
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def main():
    for kw in KEYWORDS:
        risultati = cerca_prodotti(kw)
        for r in risultati:
            invia_telegram(r)

if __name__ == "__main__":
    main()
