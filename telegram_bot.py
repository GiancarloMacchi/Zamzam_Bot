import logging
import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text, parse_mode="HTML"):
        """Invia un messaggio di testo su Telegram."""
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logging.info("✅ Messaggio inviato con successo a Telegram")
        except Exception as e:
            logging.error(f"❌ Errore invio messaggio Telegram: {e}")

    def send_photo(self, photo_url, caption="", parse_mode="HTML"):
        """Invia una foto con didascalia su Telegram."""
        url = f"{self.api_url}/sendPhoto"
        payload = {
            "chat_id": self.chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logging.info("✅ Foto inviata con successo a Telegram")
        except Exception as e:
            logging.error(f"❌ Errore invio foto Telegram: {e}")
