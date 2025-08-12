import os
import logging
from utils import search_amazon_products, send_telegram_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def esegui_bot():
    keywords = os.getenv("KEYWORDS", "").split(",")
    min_discount = int(os.getenv("MIN_SAVE", 20))
    for kw in keywords:
        for product in search_amazon_products(kw.strip(), min_discount):
            msg = f"🔥 {product['title']}\n💰 Prezzo: {product['price']}\n💸 Sconto: {product['discount']}%\n🔗 {product['url']}"
            send_telegram_message(msg)

if __name__ == "__main__":
    esegui_bot()
