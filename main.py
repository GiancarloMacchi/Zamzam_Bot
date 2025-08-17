import logging
import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text, image_url=None):
        """Invia un messaggio su Telegram, con immagine opzionale."""
        try:
            if image_url:
                # Messaggio con immagine
                url = f"{self.base_url}/sendPhoto"
                payload = {
                    "chat_id": self.chat_id,
                    "caption": text,
                    "parse_mode": "HTML",
                }
                files = {"photo": requests.get(image_url, stream=True).raw}
                response = requests.post(url, data=payload, files=files)
            else:
                # Solo testo
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                }
                response = requests.post(url, data=payload)

            response.raise_for_status()
            logging.info("📨 Messaggio inviato con successo!")

        except Exception as e:
            logging.error(f"❌ Errore nell'invio del messaggio: {e}")
