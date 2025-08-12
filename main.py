import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
import bitlyshortener
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Carica variabili ambiente
load_dotenv()

amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
amazon_associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
amazon_country = os.getenv("AMAZON_COUNTRY")
bitly_token = os.getenv("BITLY_TOKEN")
item_count = os.getenv("ITEM_COUNT")
keywords = os.getenv("KEYWORDS").split(",")
min_save = int(os.getenv("MIN_SAVE"))
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Amazon API
amazon = AmazonApi(
    amazon_access_key,
    amazon_secret_key,
    amazon_associate_tag,
    amazon_country
)

# Risorse da recuperare
resources = [
    "ItemInfo.Title",
    "ItemInfo.Features",
    "Offers.Listings.Price",
    "Offers.Listings.SavingBasis",
    "Offers.Listings.SavingBasis.Price",
    "Offers.Listings.SavingBasis.Percentage",
    "Offers.Summaries.LowestPrice",
    "Images.Primary.Large"
]

# Bitly
shortener = bitlyshortener.Shortener(tokens=[bitly_token], max_cache_size=256)

# Telegram
bot = Bot(token=telegram_bot_token)


def cerca_offerte(keyword):
    try:
        items = amazon.search_items(
            keywords=keyword,
            search_index="All",
            item_count=int(item_count),
            Resources=resources  # ✅ solo qui, R maiuscola
        )
        print(f"[INFO] '{keyword}': Amazon ha restituito {len(items)} risultati.")
        return items
    except Exception as e:
        print(f"[ERRORE] ricerca '{keyword}': {e}")
        return []


def estrai_sconto(item):
    try:
        prezzo_listino = item.offers.listings[0].saving_basis.price.value
        prezzo_attuale = item.offers.listings[0].price.value
        sconto = round((prezzo_listino - prezzo_attuale) / prezzo_listino * 100)
        return sconto
    except:
        return 0


def invia_telegram(messaggio):
    bot.send_message(chat_id=telegram_chat_id, text=messaggio, parse_mode="HTML")


def main():
    for keyword in keywords:
        items = cerca_offerte(keyword)
        for item in items:
            sconto = estrai_sconto(item)
            if sconto >= min_save:
                titolo = item.item_info.title.display_value
                link = shortener.shorten_urls([item.detail_page_url])[0]
                prezzo = item.offers.listings[0].price.display_amount
                messaggio = f"<b>{titolo}</b>\nPrezzo: {prezzo}\nSconto: {sconto}%\n{link}"
                invia_telegram(messaggio)


if __name__ == "__main__":
    main()
