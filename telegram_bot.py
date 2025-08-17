import logging
import time
import telegram
from config import load_config

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"

if not DRY_RUN:
    try:
        bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
    except ImportError:
        logging.warning("python-telegram-bot non installato, DRY_RUN abilitato")
        DRY_RUN = True

def send_message(product):
    message = f"🔹 <b>{product['title']}</b>\n"
    message += f"{product['url']}\n"
    message += f"💰 Prezzo: {product['price']}\n"
    message += f"{product['description']}"
    
    if DRY_RUN:
        logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}\nImmagine: {product['image_url']}")
        return

    if product.get("image_url"):
        bot.send_photo(
            chat_id=config["TELEGRAM_CHAT_ID"],
            photo=product["image_url"],
            caption=message,
            parse_mode="HTML"
        )
    else:
        bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=message, parse_mode="HTML")

def send_products(products, interval_minutes=30):
    for product in products:
        send_message(product)
        logging.info(f"Attendo {interval_minutes} minuti prima della prossima offerta...")
        time.sleep(interval_minutes * 60)
