import logging
from amazon_client import AmazonClient
from telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)

def main():
    try:
        amazon_client = AmazonClient(
            access_key="FAKE_KEY",
            secret_key="FAKE_SECRET",
            associate_tag="FAKE_TAG",
            country="it",
            keywords=[
                "regali bambino", "regali mamma", "regali papà",
                "bambina", "bambino", "lego", "gioco",
                "giocattolo", "scuola", "asilo"
            ],
            min_save=10,
            item_count=5
        )

        telegram_bot = TelegramBot()

        logging.info("🔍 Recupero articoli da Amazon (MOCK)...")
        logging.info(f"📜 Keywords lette: {amazon_client.keywords}")

        for keyword in amazon_client.keywords:
            products = amazon_client.search_items(keyword)
            telegram_bot.send_products(products)

        logging.info("✅ Processo completato con il MOCK.")

    except Exception as e:
        logging.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
