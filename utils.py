import os
from amazon_paapi import AmazonApi
import bitlyshortener

# Carica variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 30))
KEYWORDS = os.getenv("KEYWORDS", "").split(",")

# Inizializza API Amazon
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Inizializza Bitly
shortener = bitlyshortener.Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

def cerca_prodotti(keyword):
    try:
        results = amazon.search_items(
            keywords=keyword.strip(),
            item_count=ITEM_COUNT,
            resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "ItemInfo.Features",
                "ItemInfo.ByLineInfo",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.Promotions",
                "ItemInfo.ContentInfo",
                "ItemInfo.ProductInfo",
                "ItemInfo.TechnicalInfo",
                "ItemInfo.Classifications",
                "ItemInfo.Languages"
            ],
            search_index="All"
        )

        prodotti_filtrati = []
        for item in results.items:
            try:
                # Filtro lingua italiana
                lingua = None
                if hasattr(item.item_info, "languages") and item.item_info.languages.display_values:
                    lingua = item.item_info.languages.display_values[0].value.lower()

                if lingua and "ital" not in lingua:
                    continue

                titolo = getattr(item.item_info.title, "display_value", "Senza titolo")
                url = shortener.shorten_urls([item.detail_page_url])[0] if item.detail_page_url else None

                prezzo = None
                risparmio = None
                if hasattr(item.offers, "listings") and item.offers.listings:
                    prezzo = item.offers.listings[0].price.display_amount
                    if hasattr(item.offers.listings[0], "saving_basis") and item.offers.listings[0].saving_basis:
                        risparmio = item.offers.listings[0].saving_basis.display_amount

                prodotti_filtrati.append({
                    "titolo": titolo,
                    "prezzo": prezzo,
                    "risparmio": risparmio,
                    "url": url
                })

            except Exception as e:
                print(f"Errore parsing prodotto: {e}")

        return prodotti_filtrati

    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []
