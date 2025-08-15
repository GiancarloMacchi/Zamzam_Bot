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

    def get_items(self):
        all_items = []
        for kw in self.keywords:
            kw = kw.strip()
            if not kw:
                continue
            items = self.api.search_items(kw, self.item_count)
            logger.info(f"📦 Risultati trovati per '{kw}': {len(items)}")
            all_items.extend(items)
        return all_items
