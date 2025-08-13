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

amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

def get_items():
    search_result = amazon.search_items(
        keywords=KEYWORDS,
        item_count=ITEM_COUNT
    )

    if not hasattr(search_result, "items") or not search_result.items:
        print("⚠️ Nessun risultato restituito da Amazon API.")
        return []

    messages = []

    for item in search_result.items:
        try:
            title = item.item_info.title.display_value
        except AttributeError:
            title = "Titolo non disponibile"

        url = getattr(item, "detail_page_url", "URL non disponibile")

        try:
            # Prezzo di listino e offerta
            listing = item.offers.listings[0]
            list_price_amount = float(listing.price.amount)
            list_price_display = listing.price.display_amount
        except Exception:
            list_price_amount = None
            list_price_display = "N/D"

        try:
            offer_price_amount = float(listing.price.amount)
            offer_price_display = listing.price.display_amount
        except Exception:
            offer_price_amount = None
            offer_price_display = "N/D"

        save = 0
        if list_price_amount and offer_price_amount:
            try:
                save = int(((list_price_amount - offer_price_amount) / list_price_amount) * 100)
            except Exception:
                pass

        if save >= MIN_SAVE:
            messages.append(
                f"<b>{title}</b>\n💰 {offer_price_display} (Risparmio: {save}%)\n🔗 {url}"
            )

    return messages
