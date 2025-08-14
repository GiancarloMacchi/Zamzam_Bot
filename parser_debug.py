import json
import glob
import os

# Legge MIN_SAVE dai secrets/env
MIN_SAVE = int(os.getenv("MIN_SAVE", 5))

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
            save_percent = None

            if offers:
                price_info = offers[0].get("Price", {})
                price = price_info.get("DisplayAmount", "N/A")
                savings = price_info.get("Savings", {})
                save_percent = savings.get("Percentage")

            # Mostra con indicazione se supera MIN_SAVE
            if save_percent is not None:
                status = "✅" if save_percent >= MIN_SAVE else "❌"
                print(f"{idx}. {title} - {price} | Sconto: {save_percent}% {status}")
            else:
                print(f"{idx}. {title} - {price} | Sconto: N/D ❌")

if __name__ == "__main__":
    print(f"📊 MIN_SAVE richiesto: {MIN_SAVE}%")
    parse_debug_files()
