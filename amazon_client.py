import os
import logging
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amazon_client")

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")
KEYWORDS = os.getenv("KEYWORDS")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 3))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

def get_items():
    try:
        amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)
        logger.info(f"🔍 Chiamata Amazon API con keyword: {KEYWORDS}")

        response = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT,
            resources=[
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Images.Primary.Medium"
            ]
        )

        items = []
        for item in response.search_result.items:
            try:
                title = item.item_info.title.display_value
                price = item.offers.listings[0].price.amount
                currency = item.offers.listings[0].price.currency
                saving_basis = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else price
                saving = round(((saving_basis - price) / saving_basis) * 100, 2) if saving_basis else 0
                url = item.detail_page_url

                if saving >= MIN_SAVE:
                    items.append({
                        "title": title,
                        "price": price,
                        "currency": currency,
                        "saving": saving,
                        "url": url
                    })
            except Exception as e:
                logger.warning(f"Errore elaborando un articolo: {e}")

        return items

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli da Amazon API:\n{e}")
        return []
