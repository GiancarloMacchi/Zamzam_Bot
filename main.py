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
        logger.info(f"📜 Keywords lette dalle secrets: {keywords}")

        min_save = float(os.getenv("MIN_SAVE", 0))
        item_count = int(os.getenv("ITEM_COUNT", 10))

        amazon_client = AmazonClient()
        telegram_client = TelegramClient()

        for keyword in keywords:
            items = amazon_client.search_items(keyword, item_count=item_count)
            logger.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")

            for item in items:
                try:
                    title = item["ItemInfo"]["Title"]["DisplayValue"]
                    price_info = item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {})
                    price = price_info.get("DisplayAmount", "N/A")
                    url = item["DetailPageURL"]

                    msg = f"🔥 {title}\n💰 {price}\n🔗 {url}"
                    telegram_client.send_message(msg)
                except Exception as e:
                    logger.error(f"Errore elaborando un articolo: {e}")

    except Exception as e:
        logger.error(f"❌ Errore nel main: {e}")

if __name__ == "__main__":
    main()
