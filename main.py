import os
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from bitlyshortener import Shortener
from python_amazon_paapi import AmazonApi
from telegram import Bot

# Carica variabili d'ambiente dal file .env (utile per debug locale)
load_dotenv()

# 🔹 Lettura secrets da GitHub Actions (o .env locale)
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔹 Controllo secrets essenziali
required_vars = [
    "AMAZON_ACCESS_KEY",
    "AMAZON_SECRET_KEY",
    "AMAZON_ASSOCIATE_TAG",
    "BITLY_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "KEYWORDS"
]

for var in required_vars:
    if not globals()[var]:
        sys.exit(f"❌ ERRORE: La variabile '{var}' non è impostata nei Repository secrets!")

# 🔹 Inizializza API Amazon
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# 🔹 Inizializza Bitly
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=8192)

# 🔹 Inizializza Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

print(f"🔍 Avvio ricerca prodotti su Amazon...\n   Keywords: {KEYWORDS}\n   Numero massimo risultati: {ITEM_COUNT}\n   Sconto minimo: {MIN_SAVE}%\n")

try:
    results = amazon.search_items(keywords=KEYWORDS, item_count=ITEM_COUNT)
except Exception as e:
    sys.exit(f"❌ Errore durante la ricerca su Amazon: {e}")

if not results or not getattr(results, "items", []):
    sys.exit("❌ Nessun prodotto trovato dalla Amazon API.")

products = results.items
filtered_products = []

for item in products:
    try:
        title = item.item_info.title.display_value
        url = item.detail_page_url
        price = float(item.offers.listings[0].price.amount)
        savings = item.offers.listings[0].saving_amount
        discount = 0
        if savings:
            discount = (savings / (price + savings)) * 100

        if discount >= MIN_SAVE:
            short_url = shortener.shorten_urls([url])[0]
            filtered_products.append(f"{title} - {discount:.0f}% OFF - {short_url}")

    except Exception as e:
        print(f"⚠️ Errore su un prodotto: {e}")

if not filtered_products:
    sys.exit("❌ Nessun prodotto soddisfa i criteri di sconto.")

# 🔹 Invia messaggi su Telegram
for message in filtered_products:
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"⚠️ Errore invio Telegram: {e}")

print("✅ Offerte inviate con successo!")
