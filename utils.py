import os
import requests
from amazon_paapi import AmazonApi

amazon = AmazonApi(
    os.getenv("AMAZON_ACCESS_KEY"),
    os.getenv("AMAZON_SECRET_KEY"),
    os.getenv("AMAZON_ASSOCIATE_TAG"),
    os.getenv("AMAZON_COUNTRY")
)

def search_amazon_products(keywords):
    try:
        result = amazon.search_items(
            keywords=keywords,
            search_index="All",
            item_count=int(os.getenv("ITEM_COUNT", 10))
        )

        # Restituiamo solo gli item
        items = getattr(result, "items", [])

        # Filtro lingua italiana se disponibile nei metadata
        filtered_items = []
        for item in items:
            lang_info = (
                item.get("ItemInfo", {})
                    .get("Languages", {})
                    .get("DisplayValues", [])
            )
            if not lang_info or any("Italian" in str(l) for l in lang_info):
                filtered_items.append(item)

        return filtered_items

    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Errore nell'invio Telegram: {e}")
