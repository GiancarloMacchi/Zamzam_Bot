import logging
import os
from amazon_client import AmazonClient
from telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)

def main():
    try:
        logging.info("🔍 Recupero articoli da Amazon...")

        # Configurazioni (prese da variabili d’ambiente)
        access_key = os.getenv("AMAZON_ACCESS_KEY")
        secret_key = os.getenv("AMAZON_SECRET_KEY")
        associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        country = os.getenv("AMAZON_COUNTRY", "it")
        keywords = os.getenv("KEYWORDS", "regali bambino,regali mamma").split(",")
        min_save = int(os.getenv("MIN_SAVE", 20))
        item_count = int(os.getenv("ITEM_COUNT", 3))
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Client Amazon mock
        amazon_client = AmazonClient(
            access_key, secret_key, associate_tag, country,
            keywords, min_save, item_count
        )

        # Bot Telegram
        telegram_bot = TelegramBot(telegram_token, telegram_chat_id)

        # Recupera prodotti per ogni keyword
        for kw in keywords:
            products = amazon_client.search_items(kw)
            logging.info(f"📦 Risultati trovati per '{kw}': {len(products)}")

            for p in products:
                message = f"<b>{p['title']}</b>\n{p['price']} ({p['discount']})\n<a href='{p['url']}'>Acquista su Amazon</a>"
                telegram_bot.send_message(message, image_url=p.get("image"))

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
