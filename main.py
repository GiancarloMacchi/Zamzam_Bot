import os
import logging
from amazon_paapi import AmazonApi
from telegram import Bot

# === CONFIGURAZIONE LOG ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

# === LETTURA VARIABILI D'AMBIENTE ===
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

# === LISTA KEYWORDS ===
KEYWORDS = [
    "infanzia", "mamma", "bimbo", "bambino", "bambina", "papà",
    "libri bambini", "vestiti bambino", "premaman", "scuola",
    "asilo", "asilo nido", "colori", "pastelli", "regalo",
    "piscina", "costume", "ciabatte", "ragazzo", "ragazza", "adolescente"
]

# === WHITELIST IN ITALIANO ===
WHITELIST = [
    "bambino", "bambina", "bimbo", "bimba", "neonato", "neonata",
    "mamma", "papà", "famiglia", "scuola", "asilo", "infanzia",
    "giocattolo", "gioco", "colori", "pastelli", "premaman",
    "piscina", "costume", "ciabatte", "libro", "regalo", "adolescente"
]

# === AVVIO BOT ===
logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

for kw in KEYWORDS:
    logging.info(f"🔍 Ricerca per: {kw}")
    try:
        results = amazon.search_items(
            keywords=kw,
            SearchIndex="All",
            ItemCount=ITEM_COUNT
        )
        
        if not results:
            logging.warning(f"Nessun risultato per '{kw}'")
            continue
        
        for item in results:
            try:
                price, currency = item.price_and_currency if item.price_and_currency else (None, None)
                if not price:
                    logging.debug(f"⏭ Nessun prezzo per '{item.title}'")
                    continue

                title_lower = item.title.lower()

                # Controllo whitelist
                if not any(word in title_lower for word in WHITELIST):
                    logging.debug(f"⏭ Escluso per whitelist: {item.title}")
                    continue

                logging.info(f"📦 Prodotto trovato: {item.title}")
                logging.info(f"💰 Prezzo: {price} {currency}")
                logging.info(f"🔗 Link: {item.detail_page_url}")

                # Messaggio Telegram
                message = (
                    f"😎 Offerta Amazon!\n\n"
                    f"📦 {item.title}\n"
                    f"💰 {price} {currency}\n"
                    f"🔗 {item.detail_page_url}"
                )
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

            except Exception as e:
                logging.error(f"[ERRORE Invio Telegram] {e}")

    except Exception as e:
        logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")

logging.info("✅ Bot completato")
