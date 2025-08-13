import os
import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(item):
    """
    Invia un messaggio a Telegram con titolo e link dell'articolo.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ Token o Chat ID di Telegram mancanti.")
        return

    message = f"📌 {item.get('title', 'Senza titolo')}\n🔗 {item.get('link', '')}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": False}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("✅ Messaggio inviato con successo a Telegram.")
        else:
            logger.error(f"❌ Errore Telegram API: {response.text}")
    except Exception as e:
        logger.error(f"❌ Errore nell'invio a Telegram: {e}")
