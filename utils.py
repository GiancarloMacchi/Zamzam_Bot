import requests
import logging

def shorten_url(url, bitly_token):
    """Accorcia un URL usando Bitly"""
    if not bitly_token:
        return url
    try:
        headers = {"Authorization": f"Bearer {bitly_token}"}
        json_data = {"long_url": url}
        response = requests.post("https://api-ssl.bitly.com/v4/shorten", headers=headers, json=json_data)
        if response.status_code == 200:
            return response.json().get("link", url)
        else:
            logging.warning(f"Bitly errore {response.status_code}: {response.text}")
            return url
    except Exception as e:
        logging.error(f"Errore Bitly: {e}")
        return url


def send_telegram_message(bot_token, chat_id, text, image_url=None):
    """Invia un messaggio su Telegram, con o senza immagine"""
    try:
        if image_url:
            # Invia foto con didascalia
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {"chat_id": chat_id, "caption": text, "parse_mode": "Markdown"}
            files = {"photo": requests.get(image_url, stream=True).raw}
            r = requests.post(url, data=payload, files={"photo": requests.get(image_url, stream=True).raw})
        else:
            # Invia solo testo
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            r = requests.post(url, data=payload)

        if r.status_code != 200:
            logging.error(f"Errore Telegram {r.status_code}: {r.text}")
    except Exception as e:
        logging.error(f"Errore invio Telegram: {e}")
