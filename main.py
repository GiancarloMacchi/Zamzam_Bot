import logging
from amazon_client import AmazonClient
from telegram_client import TelegramClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    try:
        amazon_client = AmazonClient()
        telegram_client = TelegramClient()

        if not amazon_client.keywords:
            raise ValueError("⚠️ Nessuna keyword trovata nelle Secrets.")

        logger.info(f"📜 Keywords lette: {amazon_client.keywords}")

        for keyword in amazon_client.keywords:
            items = amazon_client.search_items(keyword)
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
