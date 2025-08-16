import logging
import os
from amazon_client import AmazonClient
from telegram_bot import TelegramBot

# Configura logging
logging.basicConfig(level=logging.INFO)

def main():
    try:
        logging.info("🔍 Recupero articoli da Amazon...")

        # Leggo variabili di ambiente
        access_key = os.getenv("AMAZON_ACCESS_KEY", "fake_key")
        secret_key = os.getenv("AMAZON_SECRET_KEY", "fake_secret")
        associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG", "fake_tag")
        country = os.getenv("AMAZON_COUNTRY", "it")
        keywords = os.getenv("KEYWORDS", "giocattolo, regalo").split(",")
        min_save = int(os.getenv("MIN_SAVE", 10))
        item_count = int(os.getenv("ITEM_COUNT", 3))

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Client mock Amazon
        amazon_client = AmazonClient(
            access_key=access_key,
            secret_key=secret_key,
            associate_tag=associate_tag,
            country=country,
            keywords=keywords,
            min_save=min_save,
            item_count=item_count,
        )

        # Bot Telegram
        telegram_bot = TelegramBot(token=telegram_token, chat_id=telegram_chat_id)

        # Recupero prodotti
        for keyword in keywords:
            products = amazon_client.search_items(keyword.strip())

            for product in products:
                message = (
                    f"🎁 <b>{product['title']}</b>\n"
                    f"💰 Prezzo: {product['price']}\n"
                    f"🔻 Sconto: {product['discount']}\n"
                    f"🔗 <a href='{product['url']}'>Acquista su Amazon</a>"
                )
                telegram_bot.send_message(message, image_url=product["image"])

        logging.info("✅ Invio completato!")

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
