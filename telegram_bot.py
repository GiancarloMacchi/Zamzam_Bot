import requests
import logging
from config import load_config

config = load_config()

TELEGRAM_BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = config["TELEGRAM_CHAT_ID"]
DRY_RUN = config.get("DRY_RUN", "True") == "True"

def send_telegram_message(title, url, price=None, image_url=None):
    """
    Invia un messaggio su Telegram. Se DRY_RUN è True, stampa solo il messaggio.
    
    title: titolo del prodotto
    url: link al prodotto
    price: prezzo (opzionale)
    image_url: URL immagine prodotto (opzionale)
    """
    message = f"🔹 <b>{title}</b>\n{url}"
    if price:
        message += f"\n💰 Prezzo: {price}"

    if DRY_RUN:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}\nImmagine: {image_url}")
        return

    if image_url:
        telegram_url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload_photo = {
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": image_url,
            "caption": message,
            "parse_mode": "HTML"
        }
        response = requests.post(telegram_url_photo, data=payload_photo)
    else:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(telegram_url, data=payload)

    if response.status_code != 200:
        logging.error(f"Errore invio Telegram: {response.text}")
    else:
        logging.info(f"Messaggio inviato correttamente: {title}")
