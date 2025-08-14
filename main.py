import logging
from amazon_client import AmazonClient

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("🔍 Recupero articoli da Amazon...")
    client = AmazonClient()

    # Solo 1 keyword di test
    keyword = "lego"
    items = client.search_items(keyword, item_count=5)

    logging.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")
    for item in items:
        logging.info(item)
