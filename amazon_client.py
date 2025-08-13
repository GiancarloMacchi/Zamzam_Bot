import os
import json
import requests
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

        # Salva la risposta completa per debug
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(results.to_dict(), f, ensure_ascii=False, indent=2)

        items_list = []
        for item in results.items:
            try:
                title = item.item_info.title.display_value
                price_info = item.offers.listings[0].price
                price = price_info.amount
                currency = price_info.currency
                saving = 0
                if hasattr(price_info, "savings") and price_info.savings:
                    saving = price_info.savings.percentage

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
                print(f"⚠️ Errore nel parsing di un articolo: {e}")
                continue

        return items_list

    except Exception as e:
        print("❌ Errore durante il recupero degli articoli da Amazon API:")
        print(e)

        # Salvataggio risposta raw in caso di errore
        try:
            if hasattr(e, "response") and hasattr(e.response, "text"):
                with open("amazon_error.json", "w", encoding="utf-8") as f:
                    f.write(e.response.text)
                print("📄 Risposta di errore salvata in amazon_error.json")
        except Exception as save_err:
            print(f"⚠️ Impossibile salvare l'errore: {save_err}")

        return []
