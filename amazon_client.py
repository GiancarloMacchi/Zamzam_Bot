import logging
import json
import os
from amazon_paapi import AmazonAPI
from datetime import datetime

logger = logging.getLogger(__name__)

def get_items(keyword):
    amazon = AmazonAPI(
        os.environ["AMAZON_ACCESS_KEY"],
        os.environ["AMAZON_SECRET_KEY"],
        os.environ["AMAZON_ASSOCIATE_TAG"],
        country=os.environ["AMAZON_COUNTRY"]
    )

    logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

    try:
        items = amazon.search_items(
            keywords=keyword,
            search_index="All",
            resources=[
                "Images.Primary.Large",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.SavingsPercentage",
                "Offers.Listings.MerchantInfo"
            ]
        )

        # items può essere lista di oggetti o dict, normalizziamo
        raw_list = []
        for item in items:
            try:
                raw_list.append(item.to_dict())
            except AttributeError:
                raw_list.append(item)

        # Salvataggio debug grezzo
        debug_file = f"amazon_debug_{keyword.replace(' ', '_')}.json"
        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(raw_list, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Salvati {len(raw_list)} risultati grezzi per '{keyword}' in {debug_file}")

        # Filtro sugli sconti
        min_save = int(os.environ.get("MIN_SAVE", 0))
        filtered = []
        for item in raw_list:
            try:
                offers = item["Offers"]["Listings"]
                for offer in offers:
                    save_perc = offer.get("SavingsPercentage")
                    if save_perc is not None and save_perc >= min_save:
                        filtered.append(item)
                        break
            except (KeyError, TypeError):
                continue

        logger.info(f"✅ Articoli dopo filtro MIN_SAVE={min_save}: {len(filtered)} per '{keyword}'")
        return filtered

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
