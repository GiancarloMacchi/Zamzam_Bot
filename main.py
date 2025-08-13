import os
import json
import random
import time
from amazon_paapi import AmazonApi
from telegram_api import TelegramBot

# === CONFIG ===
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "5"))
MIN_SAVE = int(os.getenv("MIN_SAVE", "30"))

# === FILE TRACKING ===
SEEN_FILE = ".seen_items.json"
PHRASES_FILE = "phrases.json"

# Carica articoli già pubblicati
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

# Carica frasi
if os.path.exists(PHRASES_FILE):
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        phrases_data = json.load(f)
else:
    phrases_data = {}

# === INIT API ===
amazon_api = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)
bot = TelegramBot(BOT_TOKEN, CHAT_ID)

print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {ASSOCIATE_TAG}")

for keyword in KEYWORDS:
    print(f"[INFO] 🔍 Ricerca per: {keyword}")
    try:
        results = amazon_api.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT
        )
    except Exception as e:
        print(f"[ERRORE] Impossibile cercare {keyword}: {e}")
        continue

    for item in results:
        asin = item.asin
        if asin in seen_items:
            continue

        if not hasattr(item, "offers") or not item.offers.listings:
            continue

        price = item.offers.listings[0].price.amount
        savings = item.offers.listings[0].savings
        if not savings or savings.percentage < MIN_SAVE:
            continue

        # Scegli una frase casuale
        phrase_list = phrases_data.get(keyword, ["Offerta imperdibile!"])
        chosen_phrase = random.choice(phrase_list)

        message = (
            f"{chosen_phrase}\n\n"
            f"💰 Prezzo: {price}€\n"
            f"🔗 {item.detail_page_url}"
        )

        bot.send_message(message)
        seen_items.append(asin)

        # Attesa casuale per sembrare naturale
        time.sleep(random.randint(30, 90))

# Salva articoli già pubblicati
with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f, ensure_ascii=False, indent=2)

print("[INFO] ✅ Esecuzione completata")
