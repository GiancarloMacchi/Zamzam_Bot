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

    def send(self, items):
        """Invia la lista di articoli a Telegram come messaggi separati."""
        for item in items:
            message = (
                f"🛒 <b>{item.get('title', 'Titolo non disponibile')}</b>\n"
                f"💶 Prezzo: {item.get('price', 'N/A')}\n"
                f"<a href='{item.get('url', '')}'>Vai all'offerta</a>"
            )
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }
            requests.post(f"https://api.telegram.org/bot{self.bot_token}/sendMessage", data=payload)
