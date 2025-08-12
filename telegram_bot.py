import telegram
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_telegram_client():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("Token o Chat ID di Telegram non impostati.")
    return telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(bot, message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)

def send_telegram_photo(bot, photo_url, caption):
    bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo_url, caption=caption, parse_mode=telegram.ParseMode.HTML)
