import os
from amazon_paapi import AmazonAPI
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def get_items(keywords, item_count=10, min_save=0):
    try:
        items = amazon.search_items(
            keywords=keywords,
            item_count=item_count,
            resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis"
            ]
        )

        results = []
        for item in items:
            title = item.item_info.title.display_value if item.item_info and item.item_info.title else "Titolo non disponibile"
            url = item.detail_page_url
            image = item.images.primary.medium.url if item.images and item.images.primary else None
            price = None
            save_percent = None

            if item.offers and item.offers.listings:
                listing = item.offers.listings[0]
                price = listing.price.display_amount if listing.price else None
                if listing.saving_basis:
                    save_percent = listing.saving_basis.amount

            if min_save and save_percent is not None and save_percent < min_save:
                continue

            results.append({
                "title": title,
                "url": url,
                "image": image,
                "price": price,
                "save_percent": save_percent
            })

        return results

    except Exception as e:
        print(f"[ERRORE] Impossibile ottenere prodotti: {e}")
        return []
