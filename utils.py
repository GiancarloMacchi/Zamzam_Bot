import requests
import logging

def shorten_url(long_url, bitly_token):
    """Accorcia un URL usando l'API di Bitly."""
    try:
        headers = {
            "Authorization": f"Bearer {bitly_token}",
            "Content-Type": "application/json"
        }
        data = {"long_url": long_url}
        response = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("link", long_url)
    except Exception as e:
        logging.error(f"Errore Bitly: {e}")
        return long_url  # In caso di errore restituisce l'URL originale

def send_telegram_message(bot_token, chat_id, message):
    """Invia un messaggio a un canale o chat Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Messaggio inviato correttamente su Telegram.")
    except Exception as e:
        logging.error(f"Errore invio Telegram: {e}")
