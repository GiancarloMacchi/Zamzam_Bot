import os
import logging
from amazon_paapi import AmazonApi
from telegram import Bot

# Logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Leggi variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza API Amazon
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Inizializza Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Whitelist parole ammesse nei titoli
WHITELIST = [k.strip().lower() for k in KEYWORDS]

def is_whitelisted(title):
    return any(word in title.lower() for word in WHITELIST)

def shorten_url(url):
    import requests
    try:
        resp = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={"Authorization": f"Bearer {BITLY_TOKEN}"},
            json={"long_url": url}
        )
        if resp.status_code == 200:
            return resp.json()["link"]
    except Exception as e:
        logging.error(f"[ERRORE Bitly] {e}")
    return url

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        logging.error(f"[ERRORE Telegram] {e}")

def main():
    logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")
    for kw in KEYWORDS:
        kw = kw.strip()
        if not kw:
            continue
        logging.info(f"🔍 Ricerca per: {kw}")
        try:
            results = amazon.search_items(
                keywords=kw,
                item_count=ITEM_COUNT
            )
            if not results:
                logging.warning(f"[NESSUN RISULTATO] '{kw}'")
                continue

            for item in results.items:
                title = item.item_info.title.display_value
                if not is_whitelisted(title):
                    continue

                offers = item.offers.listings if item.offers else []
                if not offers:
                    continue

                price = offers[0].price.amount
                savings = offers[0].price.savings.amount if offers[0].price.savings else 0
                save_percent = offers[0].price.savings.percentage if offers[0].price.savings else 0

                if save_percent < MIN_SAVE:
                    continue

                url = shorten_url(item.detail_page_url)
                message = f"📦 <b>{title}</b>\n💰 {price}€ (-{save_percent}%)\n🔗 {url}"
                send_telegram_message(message)

        except Exception as e:
            logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")

    logging.info("✅ Bot completato")

if __name__ == "__main__":
    main()
