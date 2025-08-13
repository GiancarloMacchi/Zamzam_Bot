import os
import json
import random
from datetime import datetime
from amazon_paapi import AmazonAPI
import requests

# ======== CONFIG ========
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ======== FILES ========
PHRASES_FILE = "phrases.json"
SEEN_FILE = ".seen_items.json"

# ======== LOAD PHRASES ========
with open(PHRASES_FILE, "r", encoding="utf-8") as f:
    PHRASES = json.load(f)

# ======== AMAZON API ========
amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

# ======== SEEN ITEMS ========
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

def shorten_url(url):
    if not BITLY_TOKEN:
        return url
    try:
        r = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={"Authorization": f"Bearer {BITLY_TOKEN}", "Content-Type": "application/json"},
            json={"long_url": url}
        )
        if r.status_code == 200:
            return r.json().get("link", url)
    except Exception:
        pass
    return url

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                  data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})

# ======== MAIN LOOP ========
for keyword in KEYWORDS:
    print(f"[INFO] 🔍 Ricerca per: {keyword}")
    try:
        products = amazon.search_items(keywords=keyword, item_count=ITEM_COUNT)
    except Exception as e:
        print(f"[ERROR] Amazon API error: {e}")
        continue

    for p in products:
        asin = p.asin
        if asin in seen_items:
            continue

        try:
            title = p.item_info.title.display_value
            url = shorten_url(p.detail_page_url)
            price = p.offers.listings[0].price.amount
            saving = p.offers.listings[0].saving.amount if p.offers.listings[0].saving else 0
        except Exception:
            continue

        if saving < MIN_SAVE:
            continue

        phrase = random.choice(PHRASES.get(keyword.lower(), PHRASES["default"]))
        message = f"{phrase}\n\n<b>{title}</b>\n💶 {price}€\n🔗 {url}"

        send_telegram_message(message)
        seen_items.append(asin)

# ======== SAVE SEEN ITEMS ========
with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_items, f)

if RUN_ONCE:
    print("[INFO] ✅ Esecuzione singola completata.")
