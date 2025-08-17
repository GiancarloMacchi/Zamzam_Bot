import logging
from amazon_client import AmazonClient
from telegram_bot import TelegramBot
from config import load_config

logging.basicConfig(level=logging.INFO)

def main():
    try:
        logging.info("🔍 Recupero articoli da Amazon...")

        config = load_config()
        mock_mode = config.get("MOCK", True)

        amazon_client = AmazonClient(
            config["AMAZON_ACCESS_KEY"],
            config["AMAZON_SECRET_KEY"],
            config["AMAZON_ASSOCIATE_TAG"],
            config["AMAZON_COUNTRY"],
            config["KEYWORDS"],
            config["MIN_SAVE"],
            config["ITEM_COUNT"],
        )

        telegram_bot = TelegramBot(config["TELEGRAM_BOT_TOKEN"], config["TELEGRAM_CHAT_ID"])

        for keyword in config["KEYWORDS"]:
            products = amazon_client.search_items(keyword)

            for product in products:
                message = (
                    f"<b>{product['title']}</b>\n"
                    f"💰 Prezzo: {product['price']}\n"
                    f"🔻 Sconto: {product['discount']}\n"
                    f"🔗 <a href='{product['url']}'>Vedi su Amazon</a>"
                )
                image_url = None if mock_mode else product.get("image")
                try:
                    telegram_bot.send_message(message, image_url=image_url)
                except Exception as e:
                    logging.error(f"❌ Errore nell'invio del messaggio: {e}. Riprovo senza immagine.")
                    telegram_bot.send_message(message, image_url=None)

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
