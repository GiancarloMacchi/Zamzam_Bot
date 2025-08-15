import os
import logging
from amazon_paapi import AmazonAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amazon_client")

class AmazonClient:
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.country = os.getenv("AMAZON_COUNTRY")

        if not all([self.access_key, self.secret_key, self.associate_tag, self.country]):
            raise ValueError("⚠️ Manca una o più variabili AMAZON_* nelle secrets.")

        self.api = AmazonAPI(
            self.access_key,
            self.secret_key,
            self.associate_tag,
            self.country
        )

    def search_items(self, keyword, item_count=10):
        logger.info("🔍 DEBUG — Parametri di ricerca:")
        logger.info(f"  Keywords: {keyword}")
        logger.info(f"  Country: {self.country}")
        logger.info(f"  Resources: ['Images.Primary.Medium', 'ItemInfo.Title', 'Offers.Listings.Price', 'Offers.Listings.SavingBasis', 'Offers.Listings.Promotions']")
        logger.info(f"  Item Count: {item_count}")

        try:
            response = self.api.search_items(
                keywords=keyword,
                item_count=item_count,
                resources=[
                    "Images.Primary.Medium",
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis",
                    "Offers.Listings.Promotions"
                ]
            )

            if hasattr(response, "items") and response.items:
                return response.items
            else:
                logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
                return []

        except Exception as e:
            logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
            return []
