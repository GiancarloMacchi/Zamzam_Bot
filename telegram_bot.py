import os
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise EnvironmentError("Mancano variabili d'ambiente Telegram.")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def invia_messaggio(testo):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=testo)
