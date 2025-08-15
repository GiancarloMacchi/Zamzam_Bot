# amazon_client.py
import os
import logging
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self):
        self.keywords = os.getenv("KEYWORDS", "").split(",")
        self.item_count = int(os.getenv("ITEM_COUNT", 10))
        self.api = AmazonAPI()

        if not self.keywords or self.keywords == ['']:
            logger.error("❌ Nessuna keyword trovata nelle secrets KEYWORDS.")
            self.keywords = []

    def search_items(self, keyword, item_count=None):
        """Manteniamo il nome usato nel main.py"""
        keyword = keyword.strip()
        if not keyword:
            return []

        count = item_count or self.item_count
        items = self.api.search_items(keyword, count)

        # Log dettagliato per ogni articolo
        for item in items:
            try:
                title = item["ItemInfo"]["Title"]["DisplayValue"]
                price_info = item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {})
                price = price_info.get("DisplayAmount", "N/A")
                logger.info(f"🛒 {title} | 💰 {price}")
            except Exception as e:
                logger.error(f"Errore leggendo un articolo: {e}")

        logger.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")
        return items
