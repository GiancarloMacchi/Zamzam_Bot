import os
import logging
from dotenv import load_dotenv
from amazon_paapi import AmazonApi
from bitlyshortener import Shortener
from telegram import Bot
from bs4 import BeautifulSoup

# Carica variabili da .env
load_dotenv()

# Imposta logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Credenziali Amazon e Telegram
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = os.getenv("KEYWORDS", "")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

# Inizializza API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, country=AMAZON_COUNTRY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=8192)

def cerca_prodotti():
    logging.info("🔍 Avvio ricerca prodotti su Amazon...")
    logging.info(f"   Keywords: {KEYWORDS}")
    logging.info(f"   Numero massimo risultati: {ITEM_COUNT}")
    logging.info(f"   Sconto minimo: {MIN_SAVE}%\n")

    try:
        search_result = amazon.search_items(
            keywords=KEYWORDS,
            item_count=ITEM_COUNT
        )
    except Exception as e:
        logging.error(f"❌ Errore durante la ricerca: {e}")
        return []

    if not hasattr(search_result, "items") or not search_result.items:
        logging.warning("⚠ Nessun prodotto trovato.")
        return []

    prodotti = []
    logging.info("=== DEBUG: Prodotti restituiti da Amazon API ===")

    for item in search_result.items:
        try:
            asin = item.asin
            titolo = item.item_info.title.display_value if item.item_info and item.item_info.title else "Senza titolo"
            link = item.detail_page_url
            prezzo_offerta = item.offers.listings[0].price.amount if item.offers and item.offers.listings else None
            prezzo_vecchio = item.offers.listings[0].price.savings.amount if item.offers and item.offers.listings and item.offers.listings[0].price.savings else None
            percentuale_sconto = item.offers.listings[0].price.savings.percentage if item.offers and item.offers.listings and item.offers.listings[0].price.savings else 0

            logging.info(f"- {titolo} | ASIN: {asin} | Sconto: {percentuale_sconto}%")

            if percentuale_sconto >= MIN_SAVE:
                prodotti.append({
                    "asin": asin,
                    "titolo": titolo,
                    "link": link,
                    "prezzo_offerta": prezzo_offerta,
                    "prezzo_vecchio": prezzo_vecchio,
                    "sconto": percentuale_sconto
                })

        except Exception as e:
            logging.error(f"Errore nel parsing di un prodotto: {e}")

    logging.info("===============================================\n")
    return prodotti

def invia_telegram(prodotti):
    for p in prodotti:
        url_corto = shortener.shorten_urls([p["link"]])[0] if p["link"] else ""
        messaggio = (
            f"🔥 *{p['titolo']}*\n"
            f"💰 Prezzo: {p['prezzo_offerta']} €\n"
            f"💸 Sconto: {p['sconto']}%\n"
            f"🔗 [Acquista ora]({url_corto})"
        )
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode="Markdown")

if __name__ == "__main__":
    prodotti = cerca_prodotti()
    if prodotti:
        invia_telegram(prodotti)
    else:
        logging.info("Nessun prodotto da inviare.")
