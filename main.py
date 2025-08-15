import os
import json
import logging
from amazon_client import AmazonClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, text):
        # Simulazione invio messaggio
        logging.info(f"📤 [MOCK] Messaggio inviato a Telegram: {text[:50]}...")

def main():
    try:
        logger.info("🔍 Recupero articoli da Amazon...")

        # Lettura variabili ambiente
        access_key = os.getenv("AMAZON_ACCESS_KEY", "fake_key")
        secret_key = os.getenv("AMAZON_SECRET_KEY", "fake_secret")
        associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG", "fake_tag")
        country = os.getenv("AMAZON_COUNTRY", "it")
        min_save = int(os.getenv("MIN_SAVE", 10))
        item_count = int(os.getenv("ITEM_COUNT", 5))

        keywords_env = os.getenv("KEYWORDS", '["lego","giocattolo","scuola"]')
        try:
            keywords = json.loads(keywords_env)
        except json.JSONDecodeError:
            keywords = [k.strip() for k in keywords_env.split(",") if k.strip()]

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "fake_token")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "fake_chat_id")

        # Creazione client Amazon (MOCK)
        amazon_client = AmazonClient(
            access_key, secret_key, associate_tag,
            country, keywords, min_save, item_count
        )

        telegram_bot = TelegramBot(telegram_token, telegram_chat_id)

        for keyword in keywords:
            results = amazon_client.search_items(keyword)
            for product in results:
                message = (
                    f"{product['title']}\n"
                    f"{product['price']} ({product['discount']})\n"
                    f"{product['url']}"
                )
                telegram_bot.send_message(message)

    except Exception as e:
        logger.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
