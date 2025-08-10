import requests
import logging

def shorten_url(long_url, bitly_token):
    """Accorcia un URL usando l'API di Bitly."""
    try:
        headers = {"Authorization": f"Bearer {bitly_token}"}
        data = {"long_url": long_url}
        response = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("link")
    except Exception as e:
        logging.error(f"Errore nel creare il link Bitly: {e}")
        return long_url  # In caso di errore restituisce il link originale


def send_telegram_message(bot_token, chat_id, text, image_url=None):
    """Invia un messaggio su Telegram (con immagine opzionale)."""
    try:
        if image_url:
            # Invia come foto con didascalia
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": image_url,
                "caption": text,
                "parse_mode": "Markdown"
            }
        else:
            # Invia solo testo
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }

        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("✅ Messaggio inviato su Telegram")
    except Exception as e:
        logging.error(f"Errore nell'invio del messaggio Telegram: {e}")
