import os
import json
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

# Variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = os.getenv("KEYWORDS", "")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

# Inizializza Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

def get_items():
    # Chiamata API
    results = amazon.search_items(keywords=KEYWORDS, item_count=ITEM_COUNT)

    # Salva la risposta raw in JSON
    try:
        with open("amazon_raw_response.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DEBUG] Errore salvataggio amazon_raw_response.json: {e}")

    messages = []
    debug_data = []

    # Itera sugli articoli
    for item in results.items:
        try:
            title = getattr(item, "title", "N/D")
            url = getattr(item, "detail_page_url", "N/D")
            price = getattr(item, "list_price", None)
            offer_price = getattr(item, "offer_price", None)

            price_display = price.display_price if price else "N/D"
            offer_display = offer_price.display_price if offer_price else "N/D"

            save = 0
            if price and offer_price:
                try:
                    list_val = float(price.amount)
                    offer_val = float(offer_price.amount)
                    save = int(((list_val - offer_val) / list_val) * 100)
                except Exception:
                    pass

            debug_data.append({
                "title": title,
                "url": url,
                "list_price": price_display,
                "offer_price": offer_display,
                "save_percent": save
            })

            if save >= MIN_SAVE:
                messages.append(f"<b>{title}</b>\n💰 {offer_display} (Risparmio: {save}%)\n🔗 {url}")

        except Exception as e:
            print(f"[DEBUG] Errore elaborando un articolo: {e}")

    # Salva file debug
    try:
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(debug_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DEBUG] Errore salvataggio amazon_debug.json: {e}")

    return messages
