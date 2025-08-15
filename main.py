import os
import logging
from amazon_client import AmazonClient
from telegram_client import TelegramClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    try:
        keywords_env = os.getenv("KEYWORDS")
        if not keywords_env:
            raise ValueError("⚠️ La variabile KEYWORDS non è impostata nelle Secrets.")

        keywords = [kw.strip() for kw in keywords_env.split(",") if kw.strip()]
        logger.info(f"📜 Keywords lette: {keywords}")

        min_save = float(os.getenv("MIN_SAVE", 0))
        item_count = int(os.getenv("ITEM_COUNT", 10))

        amazon_client = AmazonClient(
            access_key=os.getenv("AMAZON_ACCESS_KEY"),
            secret_key=os.getenv("AMAZON_SECRET_KEY"),
            associate_tag=os.getenv("AMAZON_ASSOCIATE_TAG"),
            country=os.getenv("AMAZON_COUNTRY"),
            keywords=keywords
        )

        telegram_client = TelegramClient()

        for keyword in amazon_client.keywords:
            items = amazon_client.get_products(keyword, item_count=item_count)
            logger.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")

            for item in items:
                try:
                    msg = f"🔥 {item['title']}\n💰 {item['price']}\n🔗 {item['url']}"
                    telegram_client.send_message(msg)
                except Exception as e:
                    logger.error(f"Errore inviando un articolo a Telegram: {e}")

    except Exception as e:
        logger.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
