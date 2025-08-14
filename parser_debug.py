import json
import glob
import os

def parse_debug_files():
    debug_files = glob.glob("amazon_debug_*.json")

    if not debug_files:
        print("⚠️ Nessun file di debug trovato.")
        return

    for file_path in debug_files:
        keyword = os.path.basename(file_path).replace("amazon_debug_", "").replace(".json", "").replace("_", " ")
        print(f"\n===== Risultati per keyword: {keyword.upper()} =====")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("SearchResult", {}).get("Items", [])
        if not items:
            print("❌ Nessun articolo trovato.")
            continue

        for idx, item in enumerate(items, start=1):
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "N/A")
            offers = item.get("Offers", {}).get("Listings", [])
            price = "N/A"
            if offers:
                price = offers[0].get("Price", {}).get("DisplayAmount", "N/A")

            print(f"{idx}. {title} - {price}")

if __name__ == "__main__":
    parse_debug_files()
