import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_bot")

def send_telegram_message(bot_token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        logger.info("✅ Messaggio inviato con successo a Telegram.")
    except Exception as e:
        logger.error(f"❌ Errore inviando messaggio Telegram: {e}")
