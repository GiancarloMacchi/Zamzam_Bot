import os
import logging
from telegram import Bot
from telegram.error import TelegramError

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recupera le variabili d'ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza il bot
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN non impostato nelle variabili d'ambiente.")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(text: str) -> bool:
    """
    Invia un messaggio al canale/chat Telegram configurato.
    Ritorna True se inviato con successo, False in caso di errore.
    """
    if not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID non impostato.")
        return False

    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        logger.info(f"Messaggio inviato: {text}")
        return True
    except TelegramError as e:
        logger.error(f"Errore nell'invio del messaggio: {e}")
        return False
