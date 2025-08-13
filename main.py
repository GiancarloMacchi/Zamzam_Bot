import os
import json
from amazon_paapi import AmazonAPI
from telegram_api import TelegramBot

# Lettura variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 30))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

# 🔹 Nuova lettura KEYWORDS (virgole separate)
KEYWORDS = os.getenv("KEYWORDS", "infanzia").split(",")

# Inizializzazione API
amazon_api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BITLY_TOKEN)

# Carica lista oggetti già inviati
seen_items_file = ".seen_items.json"
if os.path.exists(seen_items_file):
    with open(seen_items_file, "r") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

# Loop principale
for keyword in KEYWORDS:
    keyword = keyword.strip()
    print(f"[INFO] 🔍 Ricerca per: {keyword}")

    try:
        results = amazon_api.search_items(keywords=keyword, item_count=ITEM_COUNT)
    except Exception as e:
        print(f"[ERRORE] Ricerca fallita per '{keyword}': {e}")
        continue

    for item in results:
        try:
            asin = item.asin
            title = item.item_info.title.display_value
            url = item.detail_page_url
            price = item.offers.listings[0].price.amount
            savings = item.offers.listings[0].savings.amount
            savings_percent = item.offers.listings[0].savings.percentage

            if asin in seen_items:
                continue

            if savings_percent >= MIN_SAVE:
                message = f"🔥 {title}\n💰 Prezzo: {price}€ (-{savings_percent}%)\n🔗 {url}"
                telegram_bot.send_message(message)
                seen_items.append(asin)

        except Exception as e:
            print(f"[ERRORE] Elaborazione item fallita: {e}")

# Salvataggio
with open(seen_items_file, "w") as f:
    json.dump(seen_items, f)

if RUN_ONCE:
    print("[INFO] Esecuzione singola completata.")
