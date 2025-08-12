import os
from telegram import Bot
from telegram.constants import ParseMode

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_telegram_client():
    """
    Restituisce il client Telegram Bot.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("Token o Chat ID di Telegram mancanti nei secrets.")
    return Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(bot, message):
    """
    Invia un messaggio di testo su Telegram.
    """
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        parse_mode=ParseMode.HTML
    )

def send_telegram_photo(bot, photo_url, caption):
    """
    Invia una foto con didascalia su Telegram.
    """
    bot.send_photo(
        chat_id=TELEGRAM_CHAT_ID,
        photo=photo_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
