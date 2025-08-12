import logging
import os
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def setup_logger():
    logging.basicConfig(
        format="***%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

def send_telegram_message(message):
    """Invia un messaggio su Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Token o Chat ID di Telegram mancanti.")
        return False

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
        return True
    except Exception as e:
        logging.error(f"Errore durante l'invio del messaggio Telegram: {e}")
        return False
