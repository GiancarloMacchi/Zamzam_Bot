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

amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def get_items():
    try:
        results = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT
        )

        # Salva sempre la risposta, anche se è un errore
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(results.to_dict(), f, ensure_ascii=False, indent=2)

        items_list = []
        for item in results.items:
            try:
                title = item["ItemInfo"]["Title"]["DisplayValue"]
                price_info = item["Offers"]["Listings"][0]["Price"]
                price = price_info["Amount"]
                currency = price_info["Currency"]
                saving = 0
                if "Savings" in price_info:
                    saving = price_info["Savings"].get("Percentage", 0)

                url = item["DetailPageURL"]

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

        # Log anche l'errore in JSON
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump({"error": str(e)}, f, ensure_ascii=False, indent=2)

        return []
