import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# --- Configurazione Logging ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lettura variabili da GitHub Secrets ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
KEYWORDS = os.getenv("KEYWORDS")
MIN_SAVE = os.getenv("MIN_SAVE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Controllo variabili mancanti ---
missing = [
    name for name, value in {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_TOKEN,
        "AMAZON_ACCESS_KEY": AMAZON_ACCESS_KEY,
        "AMAZON_SECRET_KEY": AMAZON_SECRET_KEY,
        "AMAZON_ASSOCIATE_TAG": AMAZON_ASSOCIATE_TAG,
        "AMAZON_COUNTRY": AMAZON_COUNTRY,
        "BITLY_TOKEN": BITLY_TOKEN,
        "KEYWORDS": KEYWORDS,
        "MIN_SAVE": MIN_SAVE,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID
    }.items() if not value
]

if missing:
    raise ValueError(f"⚠️ Manca una o più variabili d'ambiente nei Secrets: {', '.join(missing)}")

# --- Funzioni Bot ---
def start(update, context):
    update.message.reply_text("Ciao! Il bot è attivo ✅")

def help_command(update, context):
    update.message.reply_text("Comandi disponibili:\n/start - Avvia il bot\n/help - Mostra questo messaggio")

def echo(update, context):
    update.message.reply_text(update.message.text)

def main():
    """Avvio del bot"""
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
