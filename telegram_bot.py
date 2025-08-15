import os
import logging
import requests

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.token or not self.chat_id:
            raise ValueError("❌ Mancano le variabili TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")

        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text):
        """Invia un messaggio di testo su Telegram."""
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            r = requests.post(self.api_url, data=payload)
            if r.status_code != 200:
                logging.error(f"❌ Errore nell'invio messaggio Telegram: {r.text}")
        except Exception as e:
            logging.error(f"❌ Errore di connessione a Telegram: {e}")

    def send_products(self, products):
        """Invia una lista di prodotti su Telegram."""
        for p in products:
            message = f"<b>{p['title']}</b>\n{p['url']}\n💰 Prezzo: {p['price']}"
            self.send_message(message)
