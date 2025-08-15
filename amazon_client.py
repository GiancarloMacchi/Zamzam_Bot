# amazon_client.py
import logging
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self, access_key, secret_key, associate_tag, country, keywords):
        self.keywords = keywords
        self.api = AmazonAPI(access_key, secret_key, associate_tag, country)

    def get_products(self, keyword, item_count=10):
        logger.info(f"🔍 Cerco prodotti per: {keyword}")
        results = self.api.search_items(keyword, item_count=item_count)

        products = []
        for item in results:
            try:
                title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
                asin = item.get("ASIN", "")
                url = f"https://www.amazon.{self.api._get_tld()}/dp/{asin}"

                price_info = (
                    item.get("Offers", {})
                        .get("Listings", [{}])[0]
                        .get("Price", {})
                        .get("DisplayAmount", "N/D")
                )

                image_url = (
                    item.get("Images", {})
                        .get("Primary", {})
                        .get("Medium", {})
                        .get("URL", "")
                )

                products.append({
                    "title": title,
                    "asin": asin,
                    "url": url,
                    "price": price_info,
                    "image": image_url
                })
            except Exception as e:
                logger.error(f"Errore parsing prodotto: {e}")

        return products
