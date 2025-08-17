import logging
import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text, image_url=None):
        """Invia un messaggio su Telegram. Se image_url è presente, manda una foto con didascalia."""
        try:
            if image_url:
                logging.info("🖼️ Invio messaggio con immagine a Telegram...")
                url = f"{self.api_url}/sendPhoto"
                payload = {
                    "chat_id": self.chat_id,
                    "caption": text,
                    "parse_mode": "HTML"
                }
                files = {
                    "photo": requests.get(image_url, stream=True).raw
                }
                response = requests.post(url, data=payload, files={"photo": (image_url, files["photo"])})
            else:
                logging.info("✉️ Invio messaggio testuale a Telegram...")
                url = f"{self.api_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, data=payload)

            response.raise_for_status()
            logging.info("✅ Messaggio inviato con successo a Telegram!")

        except Exception as e:
            logging.error(f"❌ Errore nell'invio del messaggio Telegram: {e}")
