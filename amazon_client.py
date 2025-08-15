import logging
import os
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AmazonClient:
    def __init__(self):
        self.api = AmazonAPI(
            access_key=os.getenv("AMAZON_ACCESS_KEY"),
            secret_key=os.getenv("AMAZON_SECRET_KEY"),
            associate_tag=os.getenv("AMAZON_ASSOCIATE_TAG"),
            country=os.getenv("AMAZON_COUNTRY")
        )
        self.resources = [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
            "Offers.Listings.Promotions"
        ]
        self.item_count = int(os.getenv("ITEM_COUNT", 10))

    def search_by_keyword(self, keyword):
        logger.info("🔍 DEBUG — Parametri di ricerca:")
        logger.info(f"  Keywords: {keyword}")
        logger.info(f"  Country: {os.getenv('AMAZON_COUNTRY')}")
        logger.info(f"  Resources: {self.resources}")
        logger.info(f"  Item Count: {self.item_count}")

        items = self.api.search_items(
            keywords=keyword,
            resources=self.resources,
            item_count=self.item_count
        )

        if not items:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
        else:
            logger.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")
        return items
