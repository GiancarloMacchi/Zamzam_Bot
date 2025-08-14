import logging
import os
import json
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

def get_items(keyword):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

    amazon = AmazonAPI(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )

    try:
        # Richiesta a Amazon API
        response = amazon.search_items(
            keywords=keyword,
            search_index="All",
            resources=[
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.Promotions"
            ]
        )

        # Salva risposta grezza in un file per debug
        debug_filename = f"amazon_debug_{keyword.replace(' ', '_')}.json"
        with open(debug_filename, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        logger.info(f"💾 Dati grezzi salvati in {debug_filename}")

        # Estrazione dati utili
        items = []
        for item in response.get("SearchResult", {}).get("Items", []):
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue")
            offers = item.get("Offers", {}).get("Listings", [])
            price = None
            savings_percent = 0

            if offers:
                price_info = offers[0].get("Price", {})
                price = price_info.get("DisplayAmount")
                saving_basis = offers[0].get("SavingBasis", {})
                if saving_basis:
                    orig_price = saving_basis.get("DisplayAmount")
                    # Qui potremmo calcolare lo sconto se necessario
                    savings_percent = saving_basis.get("Percentage", 0)

            items.append({
                "title": title,
                "price": price,
                "savings_percent": savings_percent
            })

        return items

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
