import os
import logging
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
from bitlyshortener import Shortener
import telegram
from datetime import datetime

# 📂 Carica variabili da .env
load_dotenv()

# 🔧 Configurazione logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# 🔑 Leggi variabili ambiente
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

# 🛒 Amazon API
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

# 🔗 Bitly Shortener
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

# 🤖 Telegram Bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

# 🔍 Ciclo di ricerca
for kw in KEYWORDS:
    logging.info(f"🔍 Ricerca per: {kw}")

    try:
        results = amazon.search_items(keywords=kw, item_count=ITEM_COUNT)

        # Controllo risultati vuoti
        if not results.items:
            logging.warning(f"[NESSUN RISULTATO] per '{kw}'")
            continue

        for item in results.items:
            try:
                title = item.item_info.title.display_value if item.item_info and item.item_info.title else "Senza titolo"
                url = item.detail_page_url
                price = None
                save = 0

                if item.offers and item.offers.listings:
                    offer = item.offers.listings[0].price
                    price = f"{offer.amount} {offer.currency}"
                    if item.offers.listings[0].saving_basis:
                        saving = item.offers.listings[0].saving_basis
                        save = int(saving.amount)

                # Filtra per sconto minimo
                if save >= MIN_SAVE:
                    short_url = shortener.shorten_urls([url])[0]
                    message = f"📦 {title}\n💰 Prezzo: {price}\n🔗 {short_url}"
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

            except Exception as e:
                logging.error(f"[ERRORE ITEM] {e}")

    except Exception as e:
        logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")

logging.info("✅ Bot completato")
