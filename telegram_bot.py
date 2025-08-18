import logging
import requests


def send_telegram_message(config, message, photo_url=None):
    """
    Invia un messaggio al canale Telegram.
    Se viene passata una foto, invia la foto con didascalia.
    """
    bot_token = config['TELEGRAM_BOT_TOKEN']
    chat_id = config['TELEGRAM_CHAT_ID']

    if not bot_token or not chat_id:
        logging.error("Token Telegram o Chat ID mancanti.")
        return

    try:
        if photo_url:
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "caption": message,
                "parse_mode": "Markdown"
            }
            files = {
                "photo": requests.get(photo_url, stream=True).raw
            }
            response = requests.post(url, data=payload, files={"photo": (photo_url, files["photo"])})
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)

        if response.status_code != 200:
            logging.error(f"Errore nell'invio a Telegram: {response.text}")
        else:
            logging.info("Messaggio inviato correttamente su Telegram.")

    except Exception as e:
        logging.error(f"Errore durante l'invio al bot Telegram: {e}")
