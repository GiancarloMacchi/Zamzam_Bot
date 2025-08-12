import os
import logging
from amazon_paapi import AmazonApi
from amazon_paapi.sdk.models.search_items_request import SearchItemsRequest
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import bitlyshortener
from telegram import Bot
from datetime import datetime

# Carica variabili d'ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "infanzia,mamma,bimbo").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 4))
MIN_SAVE = float(os.getenv("MIN_SAVE", 10))

# Inizializza API Amazon
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Bitly
shortener = bitlyshortener.Shortener(tokens=[BITLY_TOKEN])

# Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Lista risorse Amazon
RESOURCES = [
    "ItemInfo.Title",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Listings.PercentageSavings",
    "Images.Primary.Medium",
    "DetailPageURL"
]

logging.info(f"🚀 Avvio bot Amazon alle {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

for kw in KEYWORDS:
    logging.info(f"🔍 Ricerca per: {kw}")
    try:
        # Creo la request senza duplicare resources
        request = SearchItemsRequest(
            keywords=kw,
            resources=RESOURCES,
            item_count=ITEM_COUNT
        )

        response = amazon.search_items(request)

        if not hasattr(response, "search_result") or not response.search_result.items:
            logging.info(f"Nessuna offerta valida per '{kw}'.")
            continue

        for item in response.search_result.items:
            try:
                price = item.offers.listings[0].price.amount
                saving_basis = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else None
                percentage = item.offers.listings[0].percentage_savings if hasattr(item.offers.listings[0], "percentage_savings") else None

                if percentage is None or percentage < MIN_SAVE:
                    continue

                url = shortener.shorten_urls([item.detail_page_url])[0]
                title = item.item_info.title.display_value
                image = item.images.primary.medium.url

                message = f"🎯 <b>{title}</b>\n💰 {price}€\n💸 Sconto: {percentage}%\n🔗 {url}"

                bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image, caption=message, parse_mode="HTML")

            except Exception as e:
                logging.error(f"Errore elaborando offerta: {e}")

    except Exception as e:
        logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")

logging.info("✅ Bot completato")
