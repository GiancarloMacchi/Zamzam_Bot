import os
import json
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")
KEYWORDS = os.getenv("KEYWORDS")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 30))

print("\n=== DEBUG AMAZON CONFIG ===")
print(f"ACCESS_KEY: {ACCESS_KEY[:4]}... (lunghezza {len(ACCESS_KEY)})")
print(f"SECRET_KEY: {SECRET_KEY[:4]}... (lunghezza {len(SECRET_KEY)})")
print(f"ASSOCIATE_TAG: {ASSOCIATE_TAG}")
print(f"COUNTRY: {COUNTRY}")
print(f"KEYWORDS: {KEYWORDS}")
print(f"ITEM_COUNT: {ITEM_COUNT}")
print(f"MIN_SAVE: {MIN_SAVE}")
print("===========================\n")

amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def get_items():
    try:
        print(f"🔍 Chiamata Amazon API con keyword: {KEYWORDS}")
        results = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT
        )

        # Salva la risposta completa per debug
        raw_response = results.to_dict()
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(raw_response, f, ensure_ascii=False, indent=2)

        print("📄 Risposta grezza Amazon salvata in amazon_debug.json")

        items_list = []
        for item in results.items:
            try:
                title = item.item_info.title.display_value
                price_info = item.offers.listings[0].price
                price = price_info.amount
                currency = price_info.currency
                saving = 0
                if item.offers.listings[0].price.savings:
                    saving = item.offers.listings[0].price.savings.percentage

                url = item.detail_page_url

                if saving >= MIN_SAVE:
                    items_list.append({
                        "title": title,
                        "price": price,
                        "currency": currency,
                        "saving": saving,
                        "url": url
                    })
            except Exception as e:
                print(f"Errore nel parsing di un articolo: {e}")
                continue

        return items_list

    except Exception as e:
        print("❌ Errore durante il recupero degli articoli da Amazon API:")
        print(e)
        return []
