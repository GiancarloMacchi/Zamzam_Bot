import os
import logging
import requests
from amazon_paapi import AmazonApi

def get_amazon_client():
    return AmazonApi(
        os.getenv("AMAZON_ACCESS_KEY"),
        os.getenv("AMAZON_SECRET_KEY"),
        os.getenv("AMAZON_ASSOCIATE_TAG"),
        os.getenv("AMAZON_COUNTRY", "IT")
    )

def search_amazon_products(client, keyword, min_discount):
    try:
        result = client.search_items(keywords=keyword, item_count=int(os.getenv("ITEM_COUNT", 10)))

        items = getattr(result, "items", None)
        if items is None and hasattr(result, "search_result"):
            items = getattr(result.search_result, "items", [])

        if not items:
            return []

        filtered = []
        for item in items:
            try:
                if not hasattr(item, "offers") or not item.offers:
                    continue

                offer = item.offers.listings[0]
                price = offer.price.amount
                savings = offer.price.savings.amount if offer.price.savings else 0
                discount = (savings / (price + savings) * 100) if price + savings > 0 else 0

                if discount >= min_discount:
                    filtered.append(format_product_message(item, discount))
            except Exception as e:
                logging.error(f"Errore nel parsing di un prodotto: {e}")
        return filtered
    except Exception as e:
        logging.error(f"Errore nella ricerca Amazon: {e}")
        return []

def format_product_message(item, discount):
    title = getattr(item, "item_info", {}).get("title", {}).get("display_value", "Prodotto senza titolo")
    url = getattr(item, "detail_page_url", "")
    return f"🔥 {title}\nSconto: {discount:.0f}%\n{url}"

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)
