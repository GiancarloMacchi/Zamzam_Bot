import logging
from amazon_paapi import AmazonApi

class AmazonClient:
    def __init__(self, access_key, secret_key, associate_tag, country, item_count):
        self.api = AmazonApi(
            access_key=access_key,
            secret_key=secret_key,
            associate_tag=associate_tag,
            country=country
        )
        self.item_count = item_count
        self.logger = logging.getLogger("amazon_client")

    def search_items(self, keywords):
        self.logger.info(f"🔍 DEBUG — Parametri di ricerca:")
        self.logger.info(f"  Keywords: {keywords}")
        self.logger.info(f"  Country: ***")
        self.logger.info(f"  Resources: ['Images.Primary.Medium', 'ItemInfo.Title', 'Offers.Listings.Price', 'Offers.Listings.SavingBasis', 'Offers.Listings.Promotions']")
        self.logger.info(f"  Item Count: ***")

        try:
            response = self.api.search_items(
                keywords=keywords,
                search_index="All",  # test su tutti i reparti
                item_count=self.item_count,
                resources=[
                    "Images.Primary.Medium",
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis",
                    "Offers.Listings.Promotions"
                ]
            )
            items = response.get("SearchResult", {}).get("Items", [])
            if not items:
                self.logger.warning(f"⚠️ Nessun articolo trovato per '{keywords}'")
            return items
        except Exception as e:
            self.logger.error(f"❌ Errore Amazon API per '{keywords}': {e}")
            return []

    def test_connection(self):
        self.logger.info("🛠 Test connessione API Amazon con 'lego'")
        items = self.search_items("lego")
        self.logger.info(f"📦 Risultati trovati per 'lego': {len(items)}")
        return len(items) > 0
