import logging

try:
    from telegram import Bot
except ImportError:
    logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")
    Bot = None

from config import load_config

def send_telegram_message(message, dry_run=True):
    if dry_run or Bot is None:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
    else:
        config = load_config()
        bot = Bot(token=config["TELEGRAM_BOT_TOKEN"])
        bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=message, parse_mode='HTML')
