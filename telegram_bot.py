import logging

try:
    from telegram import Bot
except ImportError:
    Bot = None
    logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")

from config import load_config

config = load_config()
TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message, dry_run=True):
    """
    Invia un messaggio su Telegram. Se dry_run=True, stampa solo su log.
    """
    if dry_run or Bot is None:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
        return
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
    logging.info("Messaggio inviato su Telegram.")
