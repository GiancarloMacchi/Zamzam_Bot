import logging
import time
import os

try:
    from telegram import Bot, ParseMode
except ImportError:
    logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")
    Bot = None

def send_telegram_message(product, config):
    DRY_RUN = config.get("DRY_RUN", True)
    TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = config.get("TELEGRAM_CHAT_ID")

    message = (
        f"🔹 <b>{product['title']}</b>\n"
        f"{product['url']}\n"
        f"💰 Prezzo: {product['price']}\n"
        f"{product['description']}\n"
        f"Immagine: {product['image']}"
    )

    if DRY_RUN or Bot is None:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
    else:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=product['image'],
            caption=message,
            parse_mode=ParseMode.HTML
        )

def send_telegram_message_with_interval(products, config, interval_minutes=30):
    logging.info("Invio prodotti su Telegram con intervallo programmato...")
    for i, product in enumerate(products):
        send_telegram_message(product, config)
        if i < len(products) - 1:
            logging.info(f"Attendo {interval_minutes} minuti prima della prossima offerta...")
            time.sleep(interval_minutes * 60)
