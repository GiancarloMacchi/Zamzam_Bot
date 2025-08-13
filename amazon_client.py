import os
import logging
import time
from amazon_paapi import AmazonAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parametri
KEYWORDS = [kw.strip() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
BATCH_SIZE = 5
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

# Inizializza Amazon API
amazon = AmazonAPI(
    os.getenv("AMAZON_ACCESS_KEY"),
    os.getenv("AMAZON_SECRET_KEY"),
    os.getenv("AMAZON_ASSOCIATE_TAG"),
    os.getenv("AMAZON_COUNTRY", "it")
)

RESOURCES = [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "ItemInfo.Features",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis"
]

def get_items():
    all_items = []
    for i in range(0, len(KEYWORDS), BATCH_SIZE):
        batch = KEYWORDS[i:i + BATCH_SIZE]
        for keyword in batch:
            items = amazon.search_items(keyword, RESOURCES, ITEM_COUNT)
            if items:
                all_items.extend(items)
        # Delay per evitare limiti API
        time.sleep(1)
    return all_items
