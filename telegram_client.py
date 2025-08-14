import os
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not self.bot_token or not self.chat_id:
            logger.error("❌ TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti nelle variabili d'ambiente.")

    def send_message(self, text):
        """Invia un singolo messaggio a Telegram."""
        if not self.bot_token or not self.chat_id:
            logger.error("❌ Impossibile inviare messaggi: token o chat_id mancanti.")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                data=payload
            )
            if response.status_code != 200:
                logger.error(f"❌ Errore Telegram API: {response.text}")
        except Exception as e:
            logger.error(f"❌ Errore durante l'invio a Telegram: {e}")
