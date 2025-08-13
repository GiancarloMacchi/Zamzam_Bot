import os
import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(items):
    """
    Invia la lista di articoli a Telegram come messaggi separati.
    Ogni elemento di `items` deve contenere: title, price, url, image_url.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti nelle variabili d'ambiente.")
        return

    for item in items:
        message = (
            f"📦 <b>{item.get('title', 'Titolo non disponibile')}</b>\n"
            f"💰 Prezzo: {item.get('price', 'N/A')}\n"
            f"🔗 <a href='{item.get('url', '')}'>Vai all'offerta</a>"
        )

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=payload)
            response.raise_for_status()
            logger.info(f"✅ Inviato a Telegram: {item.get('title', '')}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore nell'invio a Telegram: {e}")
