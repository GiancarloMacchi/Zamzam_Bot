import logging
import os
import requests

from amazon_api import get_amazon_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

RELEVANT_CATS = [
    "bambini", "infanzi", "genitori", "scuola",
    "libro", "ragazzi", "giocattoli", "videogiochi", "puericultura"
]

def category_or_title_matches(prod):
    title = prod.item_info.title.display_value.lower()
    category = getattr(prod.item_info.classifications.binding, 'display_value', '').lower() if prod.item_info.classifications else ""
    return any(kw in title for kw in RELEVANT_CATS) or any(kw in category for kw in RELEVANT_CATS)

def search_amazon_products(keyword, min_discount):
    amazon = get_amazon_client()
    logging.info(f"Searching '{keyword}' on Amazon.it")
    try:
        items = amazon.search_items(keywords=keyword, item_count=int(os.getenv("ITEM_COUNT", 10)))
    except Exception as e:
        logging.error("Amazon API error: %s", e)
        return []

    results = []
    for it in items:
        try:
            title = it.item_info.title.display_value
            url = it.detail_page_url
            price = it.offers.listings[0].price.display_amount if it.offers.listings else "N/A"
            discount = it.offers.listings[0].price.savings.percentage if it.offers.listings and it.offers.listings[0].price.savings else 0
            if discount >= min_discount and category_or_title_matches(it):
                results.append({"title": title, "price": price, "discount": discount, "url": url})
        except Exception:
            continue
    return results

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
    if resp.status_code != 200:
        logging.error(f"Telegram error: {resp.text}")
