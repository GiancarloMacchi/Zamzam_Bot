import os
import requests
from bs4 import BeautifulSoup
from amazon_paapi import AmazonApi, SearchItemsRequest
from bitlyshortener import Shortener
from telegram import Bot

# Caricamento variabili d'ambiente
amazon_access_key = os.environ["AMAZON_ACCESS_KEY"]
amazon_secret_key = os.environ["AMAZON_SECRET_KEY"]
amazon_tag = os.environ["AMAZON_ASSOCIATE_TAG"]
amazon_country = os.environ["AMAZON_COUNTRY"]
bitly_token = os.environ["BITLY_TOKEN"]
item_count = os.environ.get("ITEM_COUNT", 5)
keywords = os.environ.get("KEYWORDS", "").split(",")
min_save = int(os.environ.get("MIN_SAVE", 0))
telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]

# Lista resources corretta
resources = [
    "Images.Primary.Large",
    "ItemInfo.Title",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Listings.Promotions",
    "Offers.Listings.SavingAmount"
]

# Inizializzazione API
amazon = AmazonApi(amazon_access_key, amazon_secret_key, amazon_tag, amazon_country)
shortener = Shortener(tokens=[bitly_token], max_cache_size=256)
bot = Bot(token=telegram_token)

def cerca_offerte(keyword):
    try:
        request = SearchItemsRequest(
            Keywords=keyword,
            SearchIndex="All",
            ItemCount=int(item_count),
            Resources=resources
        )
        response = amazon.search_items(request)
        return response["SearchResult"]["Items"]
    except Exception as e:
        print(f"Errore ricerca '{keyword}': {e}")
        return []

def filtra_offerte(items):
    risultati = []
    for item in items:
        try:
            titolo = item["ItemInfo"]["Title"]["DisplayValue"]
            prezzo = item["Offers"]["Listings"][0]["Price"]["Amount"]
            prezzo_vecchio = item["Offers"]["Listings"][0].get("SavingBasis", {}).get("Amount", prezzo)
            sconto = round((prezzo_vecchio - prezzo) / prezzo_vecchio * 100) if prezzo_vecchio > prezzo else 0

            if sconto >= min_save:
                url = item["DetailPageURL"]
                short_url = shortener.shorten_urls([url])[0]
                risultati.append(f"{titolo}\n💰 {prezzo}€ (-{sconto}%)\n🔗 {short_url}")
        except Exception:
            continue
    return risultati

def invia_telegram(messaggi):
    for msg in messaggi:
        bot.send_message(chat_id=telegram_chat_id, text=msg)

if __name__ == "__main__":
    for kw in keywords:
        items = cerca_offerte(kw.strip())
        offerte = filtra_offerte(items)
        if offerte:
            invia_telegram(offerte)
