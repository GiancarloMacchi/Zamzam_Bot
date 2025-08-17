import logging
import os
import random
from amazon_client import AmazonClient
from telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)

def main():
    try:
        logging.info("🔍 Recupero articoli da Amazon...")

        # Leggo variabili di ambiente
        access_key = os.getenv("AMAZON_ACCESS_KEY")
        secret_key = os.getenv("AMAZON_SECRET_KEY")
        associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        country = os.getenv("AMAZON_COUNTRY", "it")
        keywords = os.getenv("KEYWORDS", "regali bambino, regali mamma, regali papà").split(",")
        min_save = int(os.getenv("MIN_SAVE", 10))
        item_count = int(os.getenv("ITEM_COUNT", 5))
        dry_run = os.getenv("DRY_RUN", "False").lower() == "true"

        amazon_client = AmazonClient(
            access_key, secret_key, associate_tag, country,
            keywords, min_save, item_count
        )
        telegram_bot = TelegramBot(
            os.getenv("TELEGRAM_BOT_TOKEN"),
            os.getenv("TELEGRAM_CHAT_ID")
        )

        for keyword in keywords:
            keyword = keyword.strip()
            results = amazon_client.search_items(keyword)

            if not results:
                continue

            # 👇 prendo un prodotto casuale
            product = random.choice(results)

            msg = f"🎁 {product['title']}\n💰 {product['price']} ({product['discount']})\n👉 {product['url']}"

            if dry_run:
                logging.info(f"[DRY RUN] Messaggio pronto per Telegram:\n{msg}")
            else:
                telegram_bot.send_message(
                    msg,
                    image_url=product.get("image")
                )

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
