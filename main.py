import os
import json
import random
import time
import logging
from amazon_paapi import AmazonApi
from telegram import Bot

# ===================== CONFIGURAZIONE LOG =====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

# ===================== LETTURA VARIABILI AMBIENTE =====================
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
KEYWORDS = os.getenv("KEYWORDS", "infanzia,mamma,bimbo").split(",")

# ===================== FILE PER GESTIONE DOPPIONI =====================
SEEN_FILE = ".seen_items.json"

if not os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "w") as f:
        json.dump([], f)

with open(SEEN_FILE, "r") as f:
    seen_items = set(json.load(f))

# ===================== FRASE IRONICA PER KEYWORD =====================
PHRASES = {
    "infanzia": [
        "Per i piccoli di casa... o per i grandi con un cuore bambino 💖",
        "Se l'infanzia fosse uno sconto, sarebbe questo 😍",
        "Piccoli prezzi per piccoli grandi sorrisi 👶"
    ],
    "mamma": [
        "Per tutte le mamme multitasking 🦸‍♀️",
        "Perché le mamme meritano sempre il meglio ❤️",
        "Coccole e risparmio: combo perfetta per le mamme!"
    ],
    "bimbo": [
        "Il sorriso di un bimbo non ha prezzo... ma questo sconto aiuta 😁",
        "Regala ai bimbi momenti speciali 🎁",
        "Perché ogni bimbo merita qualcosa di bello 🍼"
    ]
}

# ===================== FUNZIONI =====================
def get_amazon_client():
    return AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

def shorten_url(url):
    if not BITLY_TOKEN:
        return url
    import requests
    try:
        headers = {"Authorization": f"Bearer {BITLY_TOKEN}", "Content-Type": "application/json"}
        data = {"long_url": url}
        r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers=headers, json=data)
        return r.json().get("link", url)
    except Exception as e:
        logging.error(f"[ERRORE Bitly] {e}")
        return url

def save_seen():
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_items), f)

def get_random_phrase(keyword):
    if keyword in PHRASES:
        return random.choice(PHRASES[keyword])
    return "Ecco un'offerta imperdibile 🤩"

def post_to_telegram(bot, title, url, image, phrase):
    text = f"{phrase}\n\n<b>{title}</b>\n{url}"
    bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image, caption=text, parse_mode="HTML")

# ===================== MAIN =====================
def main():
    logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

    amazon = get_amazon_client()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for keyword in KEYWORDS:
        logging.info(f"🔍 Ricerca per: {keyword}")
        try:
            results = amazon.search_items(
                keywords=keyword,
                item_count=ITEM_COUNT
            )

            for item in results:
                asin = item.asin
                if asin in seen_items:
                    continue

                if not item.list_price or not item.offer_price:
                    continue

                save_percent = ((item.list_price - item.offer_price) / item.list_price) * 100
                if save_percent < MIN_SAVE:
                    continue

                url = shorten_url(item.detail_page_url)
                phrase = get_random_phrase(keyword)
                post_to_telegram(bot, item.title, url, item.image, phrase)

                seen_items.add(asin)
                save_seen()

                delay = random.randint(30, 90)
                logging.info(f"⏳ Attendo {delay} sec prima del prossimo post...")
                time.sleep(delay)

        except Exception as e:
            logging.error(f"[ERRORE Amazon] ricerca '{keyword}': {e}")

    logging.info("✅ Bot completato")

if __name__ == "__main__":
    main()
