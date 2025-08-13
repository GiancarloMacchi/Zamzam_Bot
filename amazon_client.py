import os
import json
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = os.getenv("KEYWORDS", "")

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

    # Salva il risultato grezzo su file per analizzarlo
    try:
        raw_data = json.dumps(search_result.to_dict(), indent=2, ensure_ascii=False)
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            f.write(raw_data)
        print("✅ Dati grezzi salvati in amazon_debug.json")
    except Exception as e:
        print(f"⚠️ Impossibile salvare il JSON: {e}")

    return []
