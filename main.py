import os
import random
from bitlyshortener import Shortener
from amazon_paapi import AmazonApi
from datetime import datetime

# Credenziali
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")

# Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Bitly
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

# Lista di messaggi spiritosi
MESSAGGI_SPIRITOSI = [
    "🔥 Offerta imperdibile!",
    "💡 Trova l'affare prima degli altri!",
    "🎯 Colpo di fortuna per te!",
    "✨ Guarda cosa abbiamo scovato!",
    "🛒 Da non lasciarsi sfuggire!"
]

def accorcia_url(url):
    try:
        return shortener.shorten_urls([url])[0]
    except Exception as e:
        print(f"[WARN] Bitly fallito, uso URL originale: {e}")
        return url

def pubblica_offerta(keyword):
    try:
        risultati = amazon.search_items(keywords=keyword, item_count=1)
        for item in risultati.items:
            titolo = item.item_info.title.display_value
            prezzo = item.offers.listings[0].price.display_amount
            link = item.detail_page_url

            short_url = accorcia_url(link)
            messaggio = f"{random.choice(MESSAGGI_SPIRITOSI)}\n\n{titolo}\n💰 Prezzo: {prezzo}\n🔗 {short_url}"

            print(messaggio)  # Qui ci metti l'invio a Telegram
    except Exception as e:
        print(f"[ERRORE Amazon] ricerca '{keyword}': {e}")

def main():
    print(f"[INFO] 🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")
    keywords = ["infanzia", "mamma", "bimbo", "bambino", "bambina"]
    for kw in keywords:
        print(f"[INFO] 🔍 Ricerca per: {kw}")
        pubblica_offerta(kw)

if __name__ == "__main__":
    main()
