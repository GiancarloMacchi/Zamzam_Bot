import time
import logging
from config import load_config

config = load_config()
DRY_RUN = config.get("DRY_RUN", True)

try:
    from telegram import Bot
except ImportError:
    logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")
    Bot = None

def send_telegram_message(product, dry_run=True):
    msg = f"🔹 <b>{product['title']}</b>\n{product['url']}\n💰 Prezzo: {product['price']}\n{product['description']}\nImmagine: {product['image']}"
    if dry_run or Bot is None:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{msg}")
        return
    bot = Bot(token=config["TELEGRAM_BOT_TOKEN"])
    bot.send_photo(chat_id=config["TELEGRAM_CHAT_ID"], photo=product['image'], caption=msg, parse_mode="HTML")

def send_telegram_message_scheduled(products, interval_minutes=30, dry_run=True):
    for product in products:
        send_telegram_message(product, dry_run=dry_run)
        logging.info(f"Attendo {interval_minutes} minuti prima della prossima offerta...")
        time.sleep(interval_minutes * 60)
