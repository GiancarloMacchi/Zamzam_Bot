import os
import logging
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.country = os.getenv("AMAZON_COUNTRY", "it")

        # Legge e prepara le keywords
        keywords_env = os.getenv("KEYWORDS", "")
        self.keywords = [kw.strip() for kw in keywords_env.split(",") if kw.strip()]

        # Parametri aggiuntivi
        self.item_count = int(os.getenv("ITEM_COUNT", 10))
        self.min_save = float(os.getenv("MIN_SAVE", 0))

        # Inizializza AmazonAPI
        self.api = AmazonAPI(
            access_key=self.access_key,
            secret_key=self.secret_key,
            associate_tag=self.associate_tag,
            country=self.country
        )

    def search_items(self, keyword):
        resources = [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
            "Offers.Listings.Promotions"
        ]
        return self.api.search_items(
            keywords=keyword,
            resources=resources,
            item_count=self.item_count
        )
