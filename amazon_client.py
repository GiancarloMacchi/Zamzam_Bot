import os
import logging
from amazon_paapi import AmazonAPI
import json

# Configurazione logging
logger = logging.getLogger(__name__)

# Carica variabili ambiente
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

# Lista di risorse richieste all'API
RESOURCES = [
    "Images.Primary.Large",
    "ItemInfo.Title",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Listings.Savings"
]

# Inizializza API client
api = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def get_items():
    all_items = []
    raw_responses = []

    for keyword in KEYWORDS:
        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

        try:
            items = api.search_items(
                keywords=keyword,
                item_count=ITEM_COUNT,
                resources=RESOURCES
            )
            raw_responses.append({keyword: items.to_dict()})

            if not items.items:
                continue

            for item in items.items:
                try:
                    title = item.item_info.title.display_value
                    price = item.offers.listings[0].price.amount
                    saving_basis = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else None
                    savings = item.offers.listings[0].savings.amount if item.offers.listings[0].savings else None
                    url = item.detail_page_url
                    image = item.images.primary.large.url if item.images and item.images.primary and item.images.primary.large else None

                    if saving_basis and savings:
                        discount_percent = round((savings / saving_basis) * 100, 2)
                        if discount_percent < MIN_SAVE:
                            continue
                    else:
                        discount_percent = 0

                    all_items.append({
                        "title": title,
                        "price": price,
                        "url": url,
                        "image": image,
                        "discount_percent": discount_percent
                    })
                except Exception as e:
                    logger.error(f"❌ Errore parsing articolo: {e}")

        except Exception as e:
            logger.error(f"❌ Errore durante il recupero degli articoli: {e}")

    # Salvataggio risposta grezza per debug
    with open("amazon_debug.json", "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, indent=2, ensure_ascii=False)
    logger.info("💾 amazon_debug.json salvato con le risposte grezze di Amazon")

    return all_items
