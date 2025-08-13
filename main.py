import os
import json
import random
import time
import logging
from amazon_paapi import AmazonApi
from telegram_api import TelegramBot

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Credenziali da secrets
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Parametri di ricerca
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "10"))
MIN_SAVE = int(os.getenv("MIN_SAVE", "20"))
KEYWORDS = os.getenv("KEYWORDS", "infanzia,giochi,giocattoli").split(",")

# File di controllo duplicati
SEEN_FILE = ".seen_items.json"
seen_items = []
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_items = json.load(f) or []
    except json.JSONDecodeError:
        seen_items = []

# Carica frasi
phrases = {}
if os.path.exists("phrases.json"):
    with open("phrases.json", "r", encoding="utf-8") as f:
        phrases = json.load(f)

# Inizializza bot e client
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, TAG, COUNTRY)
telegram = TelegramBot(BOT_TOKEN, CHAT_ID)

logging.info(f"🚀 Bot avviato con tag: {TAG}")
logging.info(f"📌 Keyword in uso: {KEYWORDS}")

for kw in KEYWORDS:
    kw = kw.strip()
    if not kw:
        continue
    logging.info(f"🔍 Cerco: {kw}")

    try:
        result = amazon.search_items(keywords=kw, item_count=ITEM_COUNT)
    except Exception as e:
        logging.error(f"Errore ricerca '{kw}': {e}")
        continue

    for item in result.items:
        try:
            asin = item.asin
            if asin in seen_items:
                continue

            listing = item.offers.listings[0]
            price = listing.price.amount
            pct = getattr(listing.price.savings, "percentage", 0)

            if pct < MIN_SAVE:
                continue

            title = item.item_info.title.display_value
            url = item.detail_page_url
            image = item.images.primary.large.url

            phrase_list = phrases.get(kw, phrases.get("default", []))
            phrase = random.choice(phrase_list) if phrase_list else ""

            caption = f"{phrase}\n\n📦 <b>{title}</b>\n💰 {price}€ (-{pct}%)\n🔗 {url}"
            telegram.send_photo(image, caption)

            seen_items.append(asin)
            with open(SEEN_FILE, "w", encoding="utf-8") as f:
                json.dump(seen_items, f, ensure_ascii=False)

            wait = random.randint(30, 90)
            logging.info(f"⏳ Attendo {wait} secondi...")
            time.sleep(wait)

        except Exception as e:
            logging.error(f"Errore invio item: {e}")

logging.info("✅ Bot completato")
