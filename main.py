import os
import json
import time
import random
from amazon_api import AmazonApi
from telegram_api import TelegramBot

# Carica frasi da file
with open("phrases.json", "r", encoding="utf-8") as f:
    phrases_data = json.load(f)

# File per evitare duplicati
SEEN_ITEMS_FILE = ".seen_items.json"
if os.path.exists(SEEN_ITEMS_FILE):
    with open(SEEN_ITEMS_FILE, "r", encoding="utf-8") as f:
        seen_items = json.load(f)
else:
    seen_items = []

def save_seen_items():
    with open(SEEN_ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_items, f)

# Carica variabili ambiente da GitHub secrets
amazon_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
amazon_country = os.getenv("AMAZON_COUNTRY", "IT")
amazon_key = os.getenv("AMAZON_ACCESS_KEY")
amazon_secret = os.getenv("AMAZON_SECRET_KEY")
item_count = int(os.getenv("ITEM_COUNT", 10))
min_save = int(os.getenv("MIN_SAVE", 20))
keywords = os.getenv("KEYWORDS", "").split(",")

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza API
amazon_api = AmazonApi(amazon_key, amazon_secret, amazon_tag, amazon_country)
telegram_bot = TelegramBot(telegram_token, telegram_chat_id)

print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {amazon_tag}")

for keyword in keywords:
    keyword = keyword.strip()
    print(f"[INFO] 🔍 Ricerca per: {keyword}")

    results = amazon_api.search_items(
        keyword=keyword,
        item_count=item_count,
        min_save=min_save
    )

    if not results:
        print(f"[WARN] Nessun risultato per '{keyword}'")
        continue

    for item in results:
        if item['asin'] in seen_items:
            continue

        # Aggiunge frase casuale legata alla keyword
        phrase = random.choice(phrases_data.get(keyword, ["Ecco un affare che non puoi perdere!"]))
        
        caption = f"{phrase}\n\n{item['title']}\n💰 Prezzo: {item['price']}€\n💸 Sconto: {item['save_percent']}%\n🔗 {item['url']}"
        
        telegram_bot.send_photo(item['image'], caption)
        seen_items.append(item['asin'])
        save_seen_items()

        # Delay casuale tra post per sembrare più naturale
        delay = random.randint(30, 90)
        print(f"[INFO] ⏳ Attendo {delay} secondi prima del prossimo post...")
        time.sleep(delay)

print("[INFO] ✅ Bot completato")
