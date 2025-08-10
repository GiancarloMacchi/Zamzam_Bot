import os
import logging
import requests

def search_amazon_products():
    # Qui devi implementare la tua logica di ricerca Amazon PA-API
    # usando AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY
    # e KEYWORDS salvati nei secrets
    # Il risultato deve essere una lista di dict con:
    # Title, Url, ShortUrl, Image, Offers, Categories
    logging.info("Simulazione ricerca Amazon (da implementare con API reale)")
    return []

def shorten_url(long_url):
    bitly_token = os.getenv("BITLY_TOKEN")
    if not bitly_token:
        return long_url
    try:
        response = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={"Authorization": f"Bearer {bitly_token}"},
            json={"long_url": long_url}
        )
        if response.status_code == 200:
            return response.json().get("link", long_url)
    except Exception as e:
        logging.error(f"Errore Bitly: {e}")
    return long_url

def send_telegram_message(text, image_url=None):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.error("Token o chat_id Telegram mancanti")
        return

    try:
        if image_url:
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {"chat_id": chat_id, "caption": text}
            files = {"photo": requests.get(image_url).content}
            requests.post(url, data=payload, files=files)
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text}
            requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Errore Telegram: {e}")
