import os
import logging
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
from bitlyshortener import Shortener
import telegram
from datetime import datetime

# Carica variabili d'ambiente
load_dotenv()

# Configura logging
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO
)

# Parametri dal file .env / GitHub Secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Inizializza Bitly
bitly = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

# Inizializza Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def shorten_url(url):
    try:
        return bitly.shorten_urls([url])[0]
    except Exception as e:
        logging.error(f"Errore Bitly: {e}")
        return url

def get_deals(keyword):
    try:
        logging.info(f"🔍 Ricerca per: {keyword}")
        items = amazon.search_items(
            keywords=keyword,
            item_count=ITEM_COUNT,
            resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.PercentageSaved"
            ]
        )

        total_found = len(items)
        filtered_items = []
        scartati = 0

        for item in items:
            try:
                price = item.offers.listings[0].price.amount
                saving_basis = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else None
                percentage_saved = item.offers.listings[0].percentage_saved if item.offers.listings[0].percentage_saved else 0

                if percentage_saved >= MIN_SAVE:
                    filtered_items.append({
                        "title": item.item_info.title.display_value,
                        "url": shorten_url(item.detail_page_url),
                        "price": price,
                        "save": percentage_saved,
                        "image": item.images.primary.medium.url
                    })
                else:
                    scartati += 1
            except Exception as e:
                logging.warning(f"Prodotto non valido: {e}")

        logging.info(f"  → Totali: {total_found} | Validi: {len(filtered_items)} | Scartati: {scartati}")
        return filtered_items

    except Exception as e:
        logging.error(f"[ERRORE Amazon] ricerca '{keyword}': {e}")
        return []

def send_to_telegram(deals):
    for deal in deals:
        message = (
            f"**{deal['title']}**\n"
            f"💰 Prezzo: {deal['price']} €\n"
            f"💸 Sconto: {deal['save']}%\n"
            f"🔗 {deal['url']}"
        )
        try:
            bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=deal['image'], caption=message, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    logging.info(f"🚀 Avvio bot Amazon alle {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for keyword in KEYWORDS:
        deals = get_deals(keyword)
        if deals:
            send_to_telegram(deals)
        else:
            logging.info(f"Nessuna offerta valida per '{keyword}'.")
    logging.info("✅ Bot completato")
