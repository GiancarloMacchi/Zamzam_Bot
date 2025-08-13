import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = os.getenv("KEYWORDS", "")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def get_items():
    results = amazon.search_items(keywords=KEYWORDS, item_count=ITEM_COUNT)
    messages = []

    for item in results:
        title = item.title
        url = item.detail_page_url
        price = item.list_price and item.list_price.display_price or "N/D"
        offer_price = item.offer_price and item.offer_price.display_price or "N/D"
        save = 0

        if item.list_price and item.offer_price:
            try:
                list_val = float(item.list_price.amount)
                offer_val = float(item.offer_price.amount)
                save = int(((list_val - offer_val) / list_val) * 100)
            except:
                pass

        if save >= MIN_SAVE:
            messages.append(f"<b>{title}</b>\n💰 {offer_price} (Risparmio: {save}%)\n🔗 {url}")

    return messages
