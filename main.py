import os
import json
import random
from amazon_paapi import AmazonApi
from telegram_api import TelegramBot

# Caricamento variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

# Lista di keyword
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))

# File per tenere traccia degli ID già inviati
SEEN_ITEMS_FILE = ".seen_items.json"

# File frasi promozionali
PHRASES_FILE = "phrases.json"

# Carica frasi dal file
if os.path.exists(PHRASES_FILE):
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        phrases_data = json.load(f)
else:
    phrases_data = {"default": ["🔥 Offerta imperdibile!", "💥 Sconto speciale solo per oggi!"]}

# Funzione per scegliere una frase casuale
def get_random_phrase(keyword):
    phrases = phrases_data.get(keyword, phrases_data.get("default", []))
    if not phrases:
        phrases = ["🔥 Offerta imperdibile!", "💥 Sconto speciale solo per oggi!"]
    return random.choice(phrases)

# Carica gli ID già inviati
if os.path.exists(SEEN_ITEMS_FILE):
    with open(SEEN_ITEMS_FILE, "r", encoding="utf-8") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

# Inizializza Amazon API
amazon_api = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

# Inizializza Telegram Bot
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

# Loop per ogni keyword
for keyword in KEYWORDS:
    print(f"[INFO] 🔍 Ricerca per: {keyword}")
    try:
        results = amazon_api.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT
        )
    except Exception as e:
        print(f"[ERRORE] Ricerca fallita per '{keyword}': {e}")
        continue

    for item in results:
        asin = item.asin
        if asin in seen_items:
            continue  # Evita duplicati

        # Calcola percentuale di sconto
        if item.list_price and item.offer_price:
            try:
                discount = int(((item.list_price - item.offer_price) / item.list_price) * 100)
            except ZeroDivisionError:
                discount = 0
        else:
            discount = 0

        if discount >= MIN_SAVE:
            message = f"{get_random_phrase(keyword)}\n\n" \
                      f"📦 {item.title}\n" \
                      f"💰 {item.offer_price}€ (sconto {discount}%)\n" \
                      f"🔗 {item.detail_page_url}"

            telegram_bot.send_message(message)
            seen_items.append(asin)

# Salva ID inviati
with open(SEEN_ITEMS_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f)

print("[INFO] ✅ Bot completato.")

# Se RUN_ONCE è True, esce
if RUN_ONCE:
    exit()
