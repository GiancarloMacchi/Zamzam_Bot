import os
import random
import requests
from amazon_paapi import AmazonApi
from bs4 import BeautifulSoup
from bitlyshortener import Shortener

# Carica variabili ambiente dai GitHub Secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))

# Frasi simpatiche per categorie
CATEGORY_MESSAGES = {
    "infanzia": [
        "Perfetto per il tuo piccolo tesoro! 👶",
        "Un must-have per ogni genitore! 🍼",
        "La felicità di un bambino inizia da qui 💖"
    ],
    "giochi": [
        "Ore di divertimento garantite! 🎯",
        "Un gioco che non stanca mai! 🎲",
        "Pronti a giocare insieme? 🕹"
    ],
    "libri": [
        "Una storia che incanta grandi e piccini 📚",
        "Avventure fantastiche ti aspettano! ✨",
        "Un libro è un amico per sempre 📖"
    ],
    "vestiti": [
        "Stile e comfort per i più piccoli 👕",
        "Perfetti per ogni occasione 🎀",
        "Comodi e alla moda! 👗"
    ]
}

# Funzione per scegliere una frase in base alla categoria
def get_random_message(title):
    title_lower = title.lower()
    for category, messages in CATEGORY_MESSAGES.items():
        if category in title_lower:
            return random.choice(messages)
    return random.choice([
        "Un'offerta da non perdere! 🔥",
        "Solo per veri intenditori 💡",
        "Il momento giusto per comprare è adesso! ⏰"
    ])

# Inizializza API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=8192)

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False}
    requests.post(url, json=payload)

def main():
    for keyword in KEYWORDS:
        products = amazon.search_items(keywords=keyword.strip(), item_count=ITEM_COUNT)

        for p in products:
            if not hasattr(p, "offers") or not p.offers or not p.offers.listings:
                continue

            offer = p.offers.listings[0]
            if not hasattr(offer.price, "amount") or not hasattr(offer.saving_basis, "amount"):
                continue

            price = offer.price.amount
            original_price = offer.saving_basis.amount
            save_percent = int(((original_price - price) / original_price) * 100)

            if save_percent < MIN_SAVE:
                continue

            image_url = p.images.large if p.images and p.images.large else ""
            short_url = shortener.shorten_urls([p.detail_page_url])[0]
            message = get_random_message(p.item_info.title.display_value)

            telegram_text = (
                f"<b>{p.item_info.title.display_value}</b>\n"
                f"💰 <b>Prezzo:</b> {price}€ (Sconto {save_percent}%)\n"
                f"{message}\n\n"
                f"<a href='{short_url}'>🛒 Scopri l'offerta</a>"
            )

            if image_url:
                send_photo_to_telegram(image_url, telegram_text)
            else:
                send_to_telegram(telegram_text)

def send_photo_to_telegram(photo_url, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    main()
