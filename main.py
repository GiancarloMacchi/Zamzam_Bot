import os
import json
import random
import time
from amazon_paapi import AmazonAPI
from telegram_api import TelegramBot

# === CONFIGURAZIONE AMAZON API ===
amazon_api = AmazonAPI(
    os.getenv("AMAZON_ACCESS_KEY"),
    os.getenv("AMAZON_SECRET_KEY"),
    os.getenv("AMAZON_ASSOCIATE_TAG"),
    os.getenv("AMAZON_COUNTRY")
)

# === CONFIGURAZIONE TELEGRAM BOT ===
telegram_bot = TelegramBot(
    token=os.getenv("TELEGRAM_BOT_TOKEN"),
    chat_id=os.getenv("TELEGRAM_CHAT_ID")
)

# === LETTURA KEYWORDS DAI SECRETS ===
keywords = os.getenv("KEYWORDS", "").split(",")
keywords = [kw.strip() for kw in keywords if kw.strip()]

if not keywords:
    print("[ERRORE] ❌ Nessuna keyword trovata! Controlla il secret KEYWORDS nel repository.")
    exit(1)

print(f"[DEBUG] 📌 Keywords lette: {keywords}")

# === LETTURA FILE seen_items.json ===
seen_file = ".seen_items.json"
if os.path.exists(seen_file):
    with open(seen_file, "r") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

# === LETTURA PHRASES ===
phrases_file = "phrases.json"
if os.path.exists(phrases_file):
    with open(phrases_file, "r", encoding="utf-8") as f:
        phrases = json.load(f)
else:
    phrases = {}

# === FUNZIONE PER OTTENERE FRASE IRONICA ===
def get_phrase_for_keyword(keyword):
    if keyword in phrases and phrases[keyword]:
        return random.choice(phrases[keyword])
    return ""

# === PARAMETRI DA SECRETS ===
item_count = int(os.getenv("ITEM_COUNT", 10))
min_save = int(os.getenv("MIN_SAVE", 20))
run_once = os.getenv("RUN_ONCE", "false").lower() == "true"

print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {os.getenv('AMAZON_ASSOCIATE_TAG')}")

for kw in keywords:
    print(f"[INFO] 🔍 Ricerca per: {kw}")
    try:
        results = amazon_api.search_items(
            keywords=kw,
            item_count=item_count
        )
    except Exception as e:
        print(f"[ERRORE] ❌ Errore nella ricerca per '{kw}': {e}")
        continue

    for item in results:
        try:
            asin = item.asin
            if asin in seen_items:
                continue

            # Controlla lo sconto
            if item.list_price and item.offer_price:
                save_percent = 100 - (item.offer_price / item.list_price * 100)
                if save_percent < min_save:
                    continue
            else:
                continue

            phrase = get_phrase_for_keyword(kw)
            message = f"{phrase}\n\n{item.title}\n💰 Prezzo: {item.offer_price}€\n📉 Sconto: {int(save_percent)}%\n🔗 {item.detail_page_url}"
            telegram_bot.send_message(message, item.image_url)

            seen_items.append(asin)

            # Pausa random per sembrare più naturale
            time.sleep(random.randint(30, 90))

        except Exception as e:
            print(f"[ERRORE] ❌ Errore elaborando l'articolo: {e}")
            continue

# Salva gli ASIN visti
with open(seen_file, "w") as f:
    json.dump(seen_items, f)

print("[INFO] ✅ Bot completato")

if not run_once:
    while True:
        time.sleep(3600)
