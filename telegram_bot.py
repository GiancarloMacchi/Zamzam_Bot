import logging
from config import load_config

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"

try:
    from telegram import Bot, ParseMode
    bot = Bot(token=config["TELEGRAM_BOT_TOKEN"])
except ImportError:
    bot = None
    logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")

def send_telegram_message(title, url, price, image_url, description=""):
    message = f"🔹 <b>{title}</b>\n{url}\n💰 Prezzo: {price}\n"
    if description:
        message += f"{description}\n"
    if image_url:
        message += f"Immagine: {image_url}"

    if DRY_RUN:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
    else:
        if bot:
            bot.send_photo(
                chat_id=config["TELEGRAM_CHAT_ID"],
                photo=image_url,
                caption=message,
                parse_mode=ParseMode.HTML
            )
        else:
            logging.error("Bot Telegram non inizializzato. Controlla il token.")
