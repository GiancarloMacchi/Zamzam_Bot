import os
import json
import random
from datetime import datetime
from amazon_paapi import AmazonAPI
from telegram_api import TelegramBot

# ===== CONFIGURAZIONE =====
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))

# ===== FILE LOCALI =====
SEEN_ITEMS_FILE = ".seen_items.json"
PHRASES_FILE = "phrases.json"

# ===== INIZIALIZZAZIONE =====
bot = TelegramBot()
amazon_api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# ===== FUNZIONI =====
def load_seen_items():
    if os.path.exists(SEEN_ITEMS_FILE):
        try:
            with open(SEEN_ITEMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_seen_items(seen_items):
    with open(SEEN_ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_items, f)

def load_phrases():
    if os.path.exists(PHRASES_FILE):
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def choose_phrase(phrases, keyword):
    if keyword in phrases:
        return random.choice(phrases[keyword])
    elif "default" in phrases:
        return random.choice(phrases["default"])
    return ""

# ===== MAIN =====
if __name__ == "__main__":
    print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

    seen_items = load_seen_items()
    phrases = load_phrases()

    for keyword in KEYWORDS:
        print(f"[INFO] 🔍 Ricerca per: {keyword}")
        results = amazon_api.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT
        )

        for item in results:
            asin = item.asin
            if asin in seen_items:
                continue

            if hasattr(item, "offers") and item.offers and item.list_price and item.offer_price:
                discount = round((1 - (item.offer_price / item.list_price)) * 100, 2)
            else:
                discount = 0

            if discount < MIN_SAVE:
                continue

            phrase = choose_phrase(phrases, keyword)

            message = (
                f"{phrase}\n\n"
                f"<b>{item.title}</b>\n"
                f"💰 <b>Prezzo:</b> {item.offer_price}€\n"
                f"📉 <b>Sconto:</b> {discount}%\n"
                f"🔗 <a href='{item.detail_page_url}'>Vedi su Amazon</a>"
            )

            bot.send_message(message)
            seen_items.append(asin)

    save_seen_items(seen_items)
    print("[INFO] ✅ Completato.")
