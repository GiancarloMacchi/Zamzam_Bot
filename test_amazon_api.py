import os
import json
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")
KEYWORDS = os.getenv("KEYWORDS", "laptop")

print("\n=== TEST AMAZON API ===")
print(f"ACCESS_KEY: {ACCESS_KEY[:4]}... (len {len(ACCESS_KEY)})")
print(f"SECRET_KEY: {SECRET_KEY[:4]}... (len {len(SECRET_KEY)})")
print(f"ASSOCIATE_TAG: {ASSOCIATE_TAG}")
print(f"COUNTRY: {COUNTRY}")
print(f"KEYWORDS: {KEYWORDS}")
print("=======================\n")

try:
    amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)
    results = amazon.search_items(keywords=KEYWORDS, item_count=3)

    # Salvo la risposta grezza
    with open("amazon_test_response.json", "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, ensure_ascii=False, indent=2)

    print("✅ Chiamata riuscita! Risposta salvata in amazon_test_response.json")
    print(f"Articoli trovati: {len(results.items)}")
    for item in results.items:
        print(f"- {item.item_info.title.display_value}")

except Exception as e:
    print("❌ ERRORE Amazon API:")
    print(e)
